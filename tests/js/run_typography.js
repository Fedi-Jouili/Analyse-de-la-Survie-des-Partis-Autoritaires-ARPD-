// Prints, as JSON, the French texts of the site that still have an ordinary space before ? ! ; : » or after «:
// every key of the dictionary through I18n.t (with sample parameters) and every generated French text of
// frontend/data/stats.js through I18n.frenchTypography, the way core.js prepares them.
// Usage: node tests/js/run_typography.js
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..");
const ctx = {
  location: { search: "?lang=fr", hash: "", href: "http://localhost/" },
  navigator: { languages: ["fr"] },
  localStorage: { getItem: () => null, setItem() {} },
  document: { documentElement: {}, addEventListener() {} },
  console, URLSearchParams, Intl, history: {},
};
ctx.window = ctx;
vm.createContext(ctx);
for (const file of ["frontend/assets/i18n/fr.js", "frontend/assets/js/i18n.js", "frontend/data/stats.js"]) {
  vm.runInContext(fs.readFileSync(path.join(root, file), "utf8"), ctx, { filename: file });
}
const I18n = ctx.I18n;
const BAD = / [?!;:»]|« /;
const found = [];

// Dictionary: leaves of the key tree (plural objects are one key)
const PLURAL = ["zero", "one", "two", "few", "many", "other"];
const isPlural = (v) => v && typeof v === "object" && !Array.isArray(v) && "other" in v
  && Object.keys(v).every((k) => PLURAL.includes(k));
function walk(node, prefix) {
  for (const [k, v] of Object.entries(node)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v) && !isPlural(v)) { walk(v, key); continue; }
    const params = { count: 2 };
    for (const m of JSON.stringify(v).matchAll(/\{(\w+)\}/g)) if (m[1] !== "count") params[m[1]] = "x";
    const out = Array.isArray(v) ? I18n.tList(key, params) : [I18n.t(key, params), I18n.tHtml(key, params)];
    out.flat().forEach((s) => { if (typeof s === "string" && BAD.test(s)) found.push({ key, text: s.slice(0, 120) }); });
  }
}
walk(ctx.I18N_DICT.fr, "");

// Generated texts
const stats = ctx.SITE.stats;
function strings(v, where) {
  if (typeof v === "string") { if (BAD.test(v)) found.push({ key: where, text: v.slice(0, 120) }); return; }
  if (Array.isArray(v)) v.forEach((x, i) => strings(x, `${where}[${i}]`));
  else if (v && typeof v === "object") Object.entries(v).forEach(([k, x]) => strings(x, `${where}.${k}`));
}
let checked = 0;
for (const [name, block] of Object.entries(stats)) {
  if (block && block.texts && block.texts.fr) { strings(I18n.frenchTypography(block.texts.fr), `${name}.texts.fr`); checked++; }
}
console.log(JSON.stringify({ found, generatedBlocks: checked }));
