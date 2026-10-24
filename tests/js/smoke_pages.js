// Smoke test of the website: every page, in every language, at 1600 px and 390 px wide, in a headless browser.
// Usage: node tests/js/smoke_pages.js <base url> <browser executable>     (run by tests/test_frontend_smoke.py)
// Prints one JSON record per page load: console errors, lang/dir, horizontal overflow, untranslated keys, number of
// charts; on the Atlas at 1600 px, the globe and the chart button; at 390 px, the position of the "world situation"
// card; then two Atlas loads in a browser without WebGL (records with variant "no-webgl").
// Requests outside the local server (Google Fonts) are blocked, so the test does not depend on the network.
const puppeteer = require("puppeteer-core");

const [base, executablePath] = process.argv.slice(2);
const PAGES = ["index", "atlas", "analyse", "simulation", "about"];
const LANGS = ["fr", "en", "ar"];
const SIZES = [[1600, 960, false], [390, 844, true]];
// A request answered after its tab has closed rejects: log it instead of letting Node exit
process.on("unhandledRejection", (e) => console.error("ignored:", e && e.message));

/** Atlas on a phone: the world card, closed then open, must not cover the timeline, the controls or a country card. */
function worldCard() {
  const box = (sel) => {
    const n = document.querySelector(sel);
    const r = n && n.getBoundingClientRect();
    return !n || getComputedStyle(n).display === "none" || n.hidden || !r.width ? null
      : { top: r.top, bottom: r.bottom, left: r.left, right: r.right };
  };
  const overlap = (a, b) => Boolean(a && b && a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom);
  const toggle = document.getElementById("world-toggle");
  const snap = () => {
    const w = box("#world");
    return { visible: Boolean(w), expanded: toggle.getAttribute("aria-expanded"), summary: toggle.textContent.trim(),
             covers: ["timeline", "hud-controls", "dossier"].filter((c) => overlap(w, box("." + c))) };
  };
  const out = { closed: snap() };
  toggle.click();
  out.open = snap();
  window.Atlas.select("CHN");
  out.withCard = snap();
  window.Atlas.select(null);
  toggle.click();
  return out;
}

/** Atlas on a computer: the globe ends above the timeline, whose chart a button hides and shows again. */
function chartToggle() {
  const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
  const button = document.getElementById("graph-toggle");
  const snap = () => ({
    globeBottom: rect("#globe").bottom, timelineTop: rect(".timeline").top, timelineHeight: rect(".timeline").height,
    chart: getComputedStyle(document.getElementById("history")).display !== "none",
    expanded: button.getAttribute("aria-expanded"), label: button.textContent.trim() });
  const out = { shown: snap() };
  button.click();
  out.hidden = snap();
  button.click();                      // back to the default for the next loads (the choice is remembered)
  out.again = snap();
  return out;
}

async function open(browser, url, width, height, mobile) {
  const tab = await browser.newPage();
  await tab.setViewport({ width, height, deviceScaleFactor: 1, isMobile: mobile, hasTouch: mobile });
  await tab.setRequestInterception(true);
  tab.on("request", (r) => {
    const done = r.url().startsWith(base) || r.url().startsWith("data:") ? r.continue() : r.abort();
    if (done && done.catch) done.catch(() => {});
  });
  const errors = [];
  tab.on("console", (m) => {
    const url = (m.location() && m.location().url) || "";
    if (m.type() === "error" && (!url || url.startsWith(base))) errors.push(m.text());
  });
  tab.on("pageerror", (e) => errors.push(e.message));
  let ready = true;
  try {
    await tab.goto(url, { waitUntil: "domcontentloaded", timeout: 120000 });
    // The Atlas sets __ready once the globe is created; the globe's first frame, drawn on the CPU in software
    // rendering, can then hold the page for minutes. Polling on DOM mutations (not on animation frames) sees
    // __ready before that frame; the long protocol timeout of the launch lets later evaluations wait for it.
    await tab.waitForFunction("window.__ready === true", { timeout: 300000, polling: "mutation" });
  } catch (e) {
    ready = false;
    errors.push(String(e.message || e));
  }
  await new Promise((r) => setTimeout(r, 600));
  return { tab, errors, ready };
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath, headless: "new", protocolTimeout: 900000,
    args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"],
  });
  const results = [];
  for (const page of PAGES) {
    for (const lang of LANGS) {
      for (const [width, height, mobile] of SIZES) {
        const { tab, errors, ready } = await open(browser, `${base}/${page}.html?lang=${lang}`, width, height, mobile);
        const info = await tab.evaluate(() => {
          const text = document.body.innerText;
          return {
            htmlLang: document.documentElement.lang,
            dir: document.documentElement.dir,
            title: document.title,
            overflow: document.documentElement.scrollWidth - window.innerWidth,
            keys: (text.match(/\b(?:home|atlas|analyse|dash|sim|about|labels|common|units|nav|status|brand)\.[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*\b/g) || []).slice(0, 10),
            braces: (text.match(/\{[a-zA-Z]+\}/g) || []).slice(0, 10),
            empty: [...document.querySelectorAll("[data-i18n]")].filter((n) => !n.textContent.trim()).map((n) => n.dataset.i18n),
            charts: document.querySelectorAll("main svg.chart, main .cchart").length,
            // French typography: no ordinary space before ? ! ; : » or after « in the visible text
            typo: document.documentElement.lang === "fr" ? (text.match(/.{0,30}(?: [?!;:»]|« ).{0,10}/g) || []).slice(0, 5) : [],
          };
        }).catch((e) => ({ evalError: String(e) }));
        if (page === "atlas" && !mobile && ready) info.chartToggle = await tab.evaluate(chartToggle).catch((e) => ({ evalError: String(e) }));
        if (page === "atlas" && mobile && ready) info.worldCard = await tab.evaluate(worldCard).catch((e) => ({ evalError: String(e) }));
        results.push({ page, lang, width, ready, errors, ...info });
        await tab.close();
      }
    }
  }
  await browser.close();

  // Atlas without WebGL: the List view opens by itself, with a message, and nothing else breaks
  const noGl = await puppeteer.launch({ executablePath, headless: "new", protocolTimeout: 900000,
                                        args: ["--disable-3d-apis", "--disable-webgl"] });
  for (const [lang, width, height, mobile] of [["fr", 1600, 960, false], ["ar", 390, 844, true]]) {
    const { tab, errors, ready } = await open(noGl, `${base}/atlas.html?lang=${lang}`, width, height, mobile);
    const info = await tab.evaluate(() => ({
      webgl: window.Atlas.state.render.webgl, view: window.Atlas.state.view,
      listVisible: !document.getElementById("list-panel").hidden,
      rows: document.querySelectorAll("#list-body tbody tr").length,
      message: document.getElementById("list-note").hidden ? "" : document.getElementById("list-note").textContent,
      globeButtonDisabled: document.querySelector('#view-seg button[data-view="globe"]').disabled,
      overflow: document.documentElement.scrollWidth - window.innerWidth,
    })).catch((e) => ({ evalError: String(e) }));
    results.push({ page: "atlas", lang, width, variant: "no-webgl", ready, errors, ...info });
    await tab.close();
  }
  await noGl.close();
  process.stdout.write(JSON.stringify(results));
})().catch((e) => { console.error(e); process.exit(1); });
