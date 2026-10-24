/* Page 01 : Accueil. Introduction, chiffres clés, résumé des résultats en cinq graphiques, accès aux outils, sources.
   Les chiffres viennent des exports des notebooks (frontend/data/stats.js), comme sur la page Analyse. */
(function () {
  "use strict";

  const { el } = Core;
  const t = I18n.t;
  const S = window.SITE.stats;
  const E = S.eda, P = S.panel, M = S.ml, DM = S.demo;
  const fmt = (v, d = 0) => I18n.n(v, d);
  const years = (v) => t("units.years", { count: v });

  /** Sources des données : noms propres (les mêmes dans les trois langues) ; leur rôle vient du dictionnaire. */
  const SOURCES = [
    ["arpd", "ARPD — Miller (2020)"], ["vdem", "V-Dem v16"], ["polity", "Polity5"], ["archigos", "Archigos"],
    ["reign", "REIGN"], ["ucdp", "UCDP/PRIO"], ["maddison", "Maddison Project 2023"],
    ["wpp", "UN World Population Prospects 2024"], ["wdi", "World Bank WDI · ILO"], ["epr", "Ethnic Power Relations (EPR)"],
    ["qog", "QoG · Alesina et al. (2003)"], ["clio", "Clio-Infra"], ["afi", "Academic Freedom Index"],
    ["emdat", "EM-DAT (CRED, UCLouvain)"], ["noaa", "NOAA NCEI"], ["prio", "PRIO Battle Deaths"],
    ["famine", "World Peace Foundation"], ["faostat", "FAOSTAT"], ["lead", "LEAD — Ellis et al. (2015)"],
    ["naturalearth", "Natural Earth"],
  ];

  // ------------------------------------------------------------------ chiffres clés
  function renderKpis() {
    const box = document.getElementById("kpis");
    box.innerHTML = "";
    const s = E.sample, km = E.km_overall;
    box.appendChild(el("div", { class: "kpi hero" }, [
      el("span", { class: "label", text: t("home.kpi.median") }),
      el("div", { class: "v" }, [el("span", { text: fmt(km.median) }), el("small", { text: t("units.yearsWord", { count: km.median }) })]),
      el("div", { class: "s", text: t("home.kpi.medianSub") }),
    ]));
    [["parties", fmt(s.spells), t("analyse.s00.kpiPartiesSub", { from: s.first_accession, to: s.last_accession, end: s.last_year })],
     ["countries", fmt(s.countries), t("home.kpi.countriesSub")],
     ["fallen", Core.pct((100 * s.events) / s.spells), t("units.falls", { count: s.events })],
     ["inPower", fmt(s.censored), t("home.kpi.inPowerSub", { year: s.last_year })],
    ].forEach(([key, value, sub]) => box.appendChild(el("div", { class: "kpi" }, [
      el("span", { class: "label", text: t(`home.kpi.${key}`) }), el("div", { class: "v", text: value }),
      el("div", { class: "s", text: sub })])));
  }

  // ------------------------------------------------------------------ résumé des résultats
  let drawers = [];
  function finding(box, id, title, text, link, note) {
    const chart = el("div", { class: "finding-chart" });
    box.appendChild(el("article", { class: "finding panel bracket", "aria-labelledby": `f-${id}` }, [
      el("h3", { id: `f-${id}`, text: title }),
      el("p", { class: "finding-text", text }),
      chart,
      note ? el("p", { class: "note finding-note", text: note }) : null,
      el("a", { class: "more-link", href: I18n.href(`analyse.html#${link}`), text: t("home.seeAnalysis") }),
    ]));
    return chart;
  }
  function renderFindings() {
    const box = document.getElementById("findings");
    box.innerHTML = "";
    drawers = [];
    // 1. Combien de temps ?
    const km = E.km_overall;
    const c1 = finding(box, "survival", t("home.f.survival.title"), t("home.f.survival.text", { median: years(km.median) }), "survie");
    drawers.push(() => Charts.km(c1, [{ key: "all", label: "", curve: km.curve, hl: true }], { median: km.median, height: 180 }));
    // 2. Ce qui protège, ce qui fragilise
    const best = Findings.protective(P), worst = Findings.harmful(P);
    const c2 = finding(box, "factors", t("home.f.factors.title"), best && worst
      ? t("home.f.factors.text", { best: I18n.cap(Findings.factorName(best.key)), k1: fmt(1 / best.hr, 1),
                                    worst: Findings.factorName(worst.key), k2: fmt(worst.hr, 1) })
      : t("home.f.factors.none"), "facteurs");
    drawers.push(() => Charts.effects(c2, Findings.significant(P), { legendLabels: {
      protect: t("dash.factors.protect"), harm: t("dash.factors.harm"), none: t("dash.factors.none") } }));
    // 3. Peut-on prédire la chute ?
    const groups = Findings.predictionGroups(M);
    const cox = groups.A.find((r) => r.ref);
    const c3 = finding(box, "prediction", t("home.f.prediction.title"),
      t(Findings.mlBetter(M).length ? "home.f.prediction.textBetter" : "home.f.prediction.text", { c: fmt(cox.mean, 2) }), "prediction");
    drawers.push(() => Charts.scores(c3, [{ title: t("dash.prediction.groupA"), rows: groups.A }],
                                     { chanceLabel: t("dash.prediction.chance"), perfectLabel: t("dash.prediction.perfect") }));
    // 4. Le pays compte-t-il ?
    const rowsC = Findings.countryRows(DM);
    const T = DM.texts[I18n.lang] || DM.texts.fr;
    const order = Findings.rows(DM.candidates).map((r) => r.variable);
    const c4 = finding(box, "country", t("home.f.country.title"), DM.kept.length
      ? t("home.f.country.textKept", { list: I18n.list(DM.kept.map((v) => T.labels[order.indexOf(v)])) })
      : t("home.f.country.text", { tested: fmt(DM.decision.data.length) }), "pays",
      rowsC.every((r) => r.p >= 0.05) ? t("dash.country.noteNone") : null);
    drawers.push(() => Charts.dumbbell(c4, rowsC.map((r) => ({ label: r.name, a: r.a, b: r.b,
      tip: () => `<div class="t-head">${Core.escape(r.name)}</div>` + Core.escape(t("dash.country.tip",
        { variable: r.variable, pair: I18n.iso(`${I18n.raw(r.a, 3)} → ${I18n.raw(r.b, 3)}`), p: I18n.pval(r.p) })) })),
      { legendLabels: { a: t("dash.country.m0"), b: t("dash.country.best") } }));
    // 5. Les chocs comptent-ils ? (catastrophes, guerres, famines, récessions)
    const SH = S.shocks;
    if (SH) {
      const TS = SH.texts[I18n.lang] || SH.texts.fr;
      const orderS = Findings.rows(SH.candidates).map((r) => r.variable);
      const c5 = finding(box, "shocks", t("home.f.shocks.title"), SH.kept.length
        ? t("home.f.shocks.textKept", { list: I18n.list(SH.kept.map((v) => TS.labels[orderS.indexOf(v)])) })
        : t("home.f.shocks.text", { tested: fmt(SH.decision.data.length) }), "chocs");
      drawers.push(() => Charts.effects(c5, Findings.shockEffects(SH), { legendLabels: {
        protect: t("dash.factors.protect"), harm: t("dash.factors.harm"), none: t("dash.factors.none") } }));
    }
    requestAnimationFrame(() => drawers.forEach((d) => d()));
  }

  // ------------------------------------------------------------------ sources
  function renderSources() {
    const ul = document.getElementById("source-grid");
    ul.innerHTML = "";
    SOURCES.forEach(([key, name]) => ul.appendChild(el("li", {}, [
      el("bdi", { class: "src-name", dir: "ltr", text: name }), el("span", { class: "src-role", text: t(`about.sources.${key}`) })])));
    document.getElementById("built").textContent = t("about.built", { date: S.built });
  }

  function render() {
    Core.tooltip.hide();
    renderKpis();
    renderFindings();
    renderSources();
  }
  render();
  I18n.onChange(render);
  let timer;
  window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(() => drawers.forEach((d) => d()), 150); });
  // Page prête (pour les tests) une fois les graphiques dessinés, au même rafraîchissement de l'écran
  requestAnimationFrame(() => { window.__ready = true; document.documentElement.dataset.ready = "1"; });
})();
