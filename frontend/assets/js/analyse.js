/* Page 03 : Analyse, en tableau de bord.
   En haut, les chiffres clés ; puis une carte par question (durée, facteurs, prédiction, pays, chocs, parti et
   dirigeant, données) : une phrase de réponse et un graphique. Le détail
   (tableaux, méthodes, textes générés en trois langues par src/site_text.py) est replié sous « Voir le détail » ;
   en bas, « Pour aller plus loin » regroupe la conclusion, les questions de recherche, les limites, les sources et
   le glossaire. Changer de langue reconstruit la page en gardant la carte affichée. */
(function () {
  "use strict";

  const { el, svg, escape, markdown } = Core;
  const t = I18n.t;
  const S = window.SITE.stats;
  const E = S.eda, P = S.panel, M = S.ml, MOD = S.model, DM = S.demo, SH = S.shocks, LD = S.leaders;
  const report = document.getElementById("report-body");
  const fmt = (v, d = 0) => I18n.n(v, d);
  const pval = (p) => I18n.pval(p);
  /** Textes générés dans la langue du site (repli : français). */
  const TX = (block) => block.texts[I18n.lang] || block.texts.fr;
  const rows = Findings.rows;
  const cov = (name) => Labels.covariate(name);
  const years = (v) => t("units.years", { count: v });
  const hrFormula = (hr) => I18n.iso(`HR = ${I18n.raw(hr, 2)}`);
  const factorName = Findings.factorName;
  const kmAt = Charts.kmAt;
  /** Durée (années) citée dans la phrase sur la survie : un paramètre du texte, pas un résultat. */
  const PLAIN_YEARS = 20;
  const protective = () => Findings.protective(P);
  const harmful = () => Findings.harmful(P);

  /** Effets robustes : même règle que src/site_text.py (PanelResults) — significatifs dans les trois modèles de Cox
      (statique, corrigé, time-varying), dans le même sens. Dans le modèle corrigé, une covariable dont l'effet change
      avec le temps compte comme significative si l'un de ses deux intervalles (avant ou après le seuil) exclut 1. */
  const EQUIV = { polity2: { static: "polity2_entry", corrected: "polity2_entry", timevarying: "polity2_lag1" },
                  conflict: { static: "conflict_entry", corrected: "conflict_entry", timevarying: "conflict_active_lag1" },
                  gdp: { timevarying: "log_gdppc_lag1" } };
  function across(concept) {
    const ph = P.proportional_hazards;
    const periods = rows(ph.early_late);
    const names = EQUIV[concept] || { static: concept, corrected: concept, timevarying: concept };
    const out = [];
    for (const [model, name] of Object.entries(names)) {
      const r = P.models[model].hazard_ratios.find((h) => h.covariate === name);
      if (!r) continue;
      if (model === "corrected" && ph.corrected_covariates.includes(name)) {
        out.push({ hr: null, sig: periods.some((x) => x.covariate === name && (x["lower 95%"] > 1 || x["upper 95%"] < 1)) });
      } else {
        out.push({ hr: r.hr, sig: r.p < 0.05 });
      }
    }
    return out;
  }
  function robustFactors() {
    const concepts = P.models.static.hazard_ratios.map((h) => h.covariate)
      .filter((c) => !["polity2_entry", "conflict_entry", "Gov_Non code"].includes(c)).concat(["polity2", "conflict", "gdp"]);
    return concepts.filter((c) => {
      const res = across(c);
      const hrs = res.filter((r) => r.hr !== null).map((r) => r.hr);
      return res.length >= 3 && res.every((r) => r.sig) && (hrs.every((h) => h < 1) || hrs.every((h) => h > 1));
    });
  }

  /** « Comment lire ce graphique » : repères en langage courant, avec des chiffres de l'analyse, et liens vers le glossaire. */
  function howTo(kind, params, terms, extra) {
    const items = I18n.tList(`analyse.howto.${kind}.items`, params).concat(extra || []);
    return el("details", { class: "howto" }, [
      el("summary", {}, [el("span", { class: "howto-mark", "aria-hidden": "true", text: "?" }), t(`analyse.howto.${kind}.title`)]),
      el("ul", {}, items.map((s) => el("li", { text: s }))),
      el("p", { class: "howto-gl" }, [t("analyse.howto.glossary") + " "].concat(terms.flatMap((k, i) =>
        [i ? " · " : "", el("a", { href: `#gl-${k}`, text: t(`analyse.gl.${k}.term`) })]))),
    ]);
  }

  let resizers = [];
  const onResize = (fn) => resizers.push(fn);
  let rt;
  window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => resizers.forEach((fn) => fn()), 150); });
  /** Dessin d'un graphique une fois sa place connue, et à chaque changement de taille de la fenêtre. */
  const drawn = (fn) => { requestAnimationFrame(fn); onResize(fn); };

  // ------------------------------------------------------------------ éléments de mise en page
  let grid = null;
  /** Carte du tableau de bord : question, réponse en une phrase, graphique (body) et détail replié (more). */
  function card(id, num, title, answer, { wide = false } = {}) {
    const body = el("div", { class: "dcard-body" });
    const more = el("div", { class: "dcard-more" });
    const details = el("details", { class: "more" }, [el("summary", {}, [el("span", { text: t("dash.more") })]), more]);
    const sec = el("section", { class: "dcard panel" + (wide ? " wide" : ""), id, "aria-labelledby": `${id}-title` }, [
      el("header", { class: "dcard-head" }, [el("span", { class: "dcard-num", text: num }), el("h2", { id: `${id}-title`, text: title })]),
      answer ? el("p", { class: "dcard-answer", text: answer }) : null,
      body, details]);
    grid.appendChild(sec);
    return { sec, body, more };
  }
  /** Sous-partie du détail : titre et phrase « en clair ». */
  function subhead(parent, title, plain, lead) {
    parent.appendChild(el("h3", { class: "sub-title", text: title }));
    if (plain) parent.appendChild(el("p", { class: "sub-plain", text: plain }));
    if (lead) parent.appendChild(el("p", { class: "note sub-lead", text: lead }));
  }
  function block(parent, title, label, children) {
    const b = el("div", { class: "block" }, [
      el("div", { class: "block-title" }, [el("h3", { text: title }), label ? el("span", { class: "label", text: label }) : null]),
    ].concat(children || []));
    parent.appendChild(b);
    return b;
  }
  function table(headers, bodyRows, { numeric = [], onRow = null } = {}) {
    const tbl = el("table", { class: "data" });
    tbl.appendChild(el("thead", {}, el("tr", {}, headers.map((h, i) => el("th", { scope: "col", class: numeric.includes(i) ? "num" : "", text: h })))));
    const tb = el("tbody");
    bodyRows.forEach((cells, ri) => {
      const tr = el("tr", { class: onRow ? "clickable" : "" }, cells.map((c, i) =>
        el("td", { class: numeric.includes(i) ? "num" : "" }, c instanceof Node ? c : String(c))));
      if (onRow) onRow(tr, ri);
      tb.appendChild(tr);
    });
    tbl.appendChild(tb);
    return tbl;
  }
  const yesNo = (v, yes = t("common.yes"), no = t("common.no")) => el("span", { class: v ? "yes" : "no", text: v ? yes : no });
  const legend = (items) => el("ul", { class: "clegend" }, items.map(([color, label]) =>
    el("li", {}, [el("span", { class: "key", style: { background: color } }), label])));

  // ------------------------------------------------------------------ chiffres clés
  function kpis() {
    const s = E.sample, km = E.km_overall, cv = MOD.performance.c_index_cv;
    const box = el("div", { class: "dash-kpis" });
    box.appendChild(el("div", { class: "kpi hero" }, [
      el("span", { class: "label", text: t("dash.kpi.median") }),
      el("div", { class: "v" }, [el("span", { text: fmt(km.median) }), el("small", { text: t("units.yearsWord", { count: km.median }) })]),
      el("div", { class: "s", text: t("dash.kpi.medianSub", { range: I18n.rangeN(km.median_lo, km.median_hi) }) }),
    ]));
    [["parties", fmt(s.spells), t("analyse.s00.kpiPartiesSub", { from: s.first_accession, to: s.last_accession, end: s.last_year })],
     ["fallen", Core.pct((100 * s.events) / s.spells), t("units.falls", { count: s.events })],
     ["countries", fmt(s.countries), t("units.partyYears", { count: s.party_years })],
     ["cindex", fmt(cv.mean, 2), t("dash.kpi.cindexSub")],
    ].forEach(([key, value, sub]) => box.appendChild(el("div", { class: "kpi" }, [
      el("span", { class: "label", text: t(`dash.kpi.${key}`) }), el("div", { class: "v", text: value }),
      el("div", { class: "s", text: sub })])));
    report.appendChild(box);
  }

  // ------------------------------------------------------------------ 01 survie au pouvoir
  function cardSurvival() {
    const km = E.km_overall;
    const c = card("survie", "01", t("dash.survival.title"), t("dash.survival.answer", {
      median: years(km.median), pct: Core.pct(kmAt(km.curve, PLAIN_YEARS) * 100), years: years(PLAIN_YEARS) }), { wide: true });
    const seg = el("div", { class: "seg", role: "group", "aria-label": t("analyse.s02.groupAria") });
    const legendHost = el("div");
    const host = el("div", { class: "chart-host" });
    c.body.append(el("div", { class: "seg-row" }, [seg]), legendHost, host);

    // détail : phrase complète, tableau des médianes du regroupement affiché, test du log-rank, mode d'emploi
    const byOrigin = E.km_by.origin.groups.filter((gr) => gr.median !== null).sort((a, b) => a.median - b.median);
    const low = byOrigin[0], high = byOrigin[byOrigin.length - 1];
    subhead(c.more, t("analyse.s02.title"), t("analyse.s02.plain", {
      median: years(km.median), pct: Core.pct(kmAt(km.curve, PLAIN_YEARS) * 100), years: years(PLAIN_YEARS),
      low: years(low.median), lowGroup: Labels.originShort(low.level), high: years(high.median), highGroup: Labels.originShort(high.level) }),
      t("analyse.s02.lead"));
    const tableHost = el("div", { class: "block" });
    const lr = el("p", { class: "note" });
    c.more.append(tableHost, lr, howTo("km", { pct: Core.pct(kmAt(km.curve, PLAIN_YEARS) * 100), years: years(PLAIN_YEARS),
                                               median: years(km.median), censored: fmt(E.sample.censored), year: E.sample.last_year },
                                       ["median", "censoring", "ci", "pvalue"]));

    const GROUPS = ["all", "origin", "governance", "era"];
    const NOT_CODED = "Non codé";        // modalité de la stratégie de gouvernance (notebook 02)
    let current = "all", highlighted = null;
    const groupLabel = (key, level) => key === "origin" ? Labels.originShort(level)
      : key === "governance" ? Labels.governanceShort(level) : Labels.era(level);
    const H = (k) => t(`analyse.s02.col.${k}`);
    function draw() {
      legendHost.innerHTML = "";
      tableHost.innerHTML = "";
      lr.textContent = "";
      if (current === "all") {
        Charts.km(host, [{ key: "all", label: t("analyse.km.all"), curve: km.curve, hl: true }],
                  { band: km.curve, median: km.median, height: 300 });
        tableHost.appendChild(table([H("group"), H("parties"), H("falls"), H("median"), H("ci")],
          [[t("analyse.km.all"), fmt(E.sample.spells), fmt(E.sample.events), years(km.median), I18n.rangeN(km.median_lo, km.median_hi)]],
          { numeric: [1, 2, 3, 4] }));
        return;
      }
      const data = E.km_by[current];
      // « Non codé » n'est pas une stratégie (02_eda_and_data_processing.ipynb) : ni tracé ni comparé ; il reste dans le
      // tableau, grisé
      const outside = (gr) => current === "governance" && gr.level === NOT_CODED;
      const shown = data.groups.filter((gr) => !outside(gr));
      // Par défaut, la durée médiane la plus longue (bleu) et la plus courte (rouge) ; au survol d'une ligne, ce groupe
      const finite = shown.filter((gr) => gr.median !== null).sort((a, b) => b.median - a.median);
      const longest = finite[0].level, shortest = finite[finite.length - 1].level;
      const series = shown.map((gr) => {
        const lab = groupLabel(current, gr.level);
        if (highlighted !== null) return { key: gr.level, label: lab, curve: gr.curve, hl: gr.level === highlighted };
        return { key: gr.level, label: lab, curve: gr.curve, hl: gr.level === longest || gr.level === shortest,
                 color: gr.level === longest ? Charts.COLOR.protect : Charts.COLOR.harm };
      });
      if (highlighted === null) {
        legendHost.appendChild(legend([[Charts.COLOR.protect, t("dash.survival.longest", { group: groupLabel(current, longest) })],
                                       [Charts.COLOR.harm, t("dash.survival.shortest", { group: groupLabel(current, shortest) })],
                                       [Charts.COLOR.none, t("dash.survival.others")]]));
      }
      Charts.km(host, series, { height: 300 });
      const sorted = [...data.groups].sort((a, b) => (b.median ?? 999) - (a.median ?? 999));
      tableHost.appendChild(table([H("group"), H("parties"), H("falls"), H("median"), H("ci")],
        sorted.map((gr) => [groupLabel(current, gr.level), fmt(gr.spells), fmt(gr.events),
                            gr.median === null ? t("analyse.s02.notReached") : years(gr.median),
                            I18n.rangeN(gr.median_lo, gr.median_hi)]),
        { numeric: [1, 2, 3, 4], onRow: (tr, i) => {
          const lvl = sorted[i].level;
          if (outside(sorted[i])) { tr.classList.remove("clickable"); tr.classList.add("muted-row"); return; }
          if (lvl === highlighted) tr.classList.add("row-hl");
          tr.addEventListener("mouseenter", () => { highlighted = lvl; draw(); });
          tr.addEventListener("mouseleave", () => { highlighted = null; draw(); });
        } }));
      // Stratégie : le test compare les trois stratégies codées, sans « Non codé » (02_eda_and_data_processing.ipynb)
      const lrc = current === "governance" ? data.logrank_coded : null;
      const test = lrc ? { chi2: lrc.chi2, p: lrc.p, df: lrc.df }
        : { chi2: data.logrank_chi2, p: data.logrank_p, df: data.logrank_df };
      lr.textContent = t("analyse.s02.logrank", {
        chi: I18n.iso(`χ²(${test.df}) = ${I18n.raw(test.chi2, 1)}`), p: pval(test.p),
        verdict: t(test.p < 0.05 ? "analyse.s02.differ" : "analyse.s02.noDiffer") });
      if (current === "governance") lr.textContent += " " + t("analyse.s02.notCodedNote");
    }
    GROUPS.forEach((key) => {
      const b = el("button", { type: "button", "aria-pressed": String(key === current),
                               text: key === "all" ? t("dash.survival.all") : t(`analyse.s02.group.${key}`) });
      b.addEventListener("click", () => {
        current = key; highlighted = null;
        seg.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
        draw();
      });
      seg.appendChild(b);
    });
    drawn(draw);
  }

  // ------------------------------------------------------------------ 02 facteurs (modèle de Cox statique)
  function cardFactors() {
    const best = protective(), worst = harmful();
    const c = card("facteurs", "02", t("dash.factors.title"), best && worst
      ? t("dash.factors.answer", { best: I18n.cap(factorName(best.key)), k1: fmt(1 / best.hr, 1), worst: factorName(worst.key), k2: fmt(worst.hr, 1) })
      : t("dash.factors.answerNone"));
    const host = el("div", { class: "chart-host" });
    c.body.append(host, el("p", { class: "note chart-note", text: t("dash.factors.note", {
      origin: Labels.originShort("Dictator-Created"), strategy: Labels.governanceShort("Policy-Based") }) }));
    drawn(() => Charts.effects(host, Findings.staticEffects(P), { legendLabels: {
      protect: t("dash.factors.protect"), harm: t("dash.factors.harm"), none: t("dash.factors.none") } }));
    forestDetails(c.more, best, worst);
    robustnessDetails(c.more);
  }

  /** Les quatre modèles de Cox côte à côte (forest plot). */
  function forestDetails(parent, best, worst) {
    const plain = [
      best ? t("analyse.s03.plainBest", { name: factorName(best.key), k: fmt(1 / best.hr, 1), formula: hrFormula(best.hr) }) : null,
      worst ? t("analyse.s03.plainWorst", { name: factorName(worst.key), k: fmt(worst.hr, 1), formula: hrFormula(worst.hr) }) : null,
    ].filter(Boolean).join(" ") || t("analyse.s03.plainNone");
    subhead(parent, t("analyse.s03.title"), plain, t("analyse.s03.lead"));
    const ph = P.proportional_hazards;
    const cut = ph.cut_years;
    const late = rows(ph.early_late);
    const COLS = [
      { key: "static", title: t("analyse.model.static"), note: t("analyse.s03.noteStatic") },
      { key: "static_gdp", title: t("analyse.model.staticGdp"), note: t("analyse.s03.noteStaticGdp") },
      { key: "corrected", title: t("analyse.model.corrected"), note: t("analyse.s03.noteCorrected", { cut }) },
      { key: "timevarying", title: t("analyse.model.timevarying"), note: t("analyse.s03.noteTv") },
    ];
    const pick = (model, names) => {
      const hr = P.models[model].hazard_ratios;
      for (const n of names) { const r = hr.find((h) => h.covariate === n); if (r) return r; }
      return null;
    };
    const lateOf = (cv) => {
      const r = late.find((l) => l.covariate === cv && l.period === "late");
      return r ? { hr: r.HR, lo: r["lower 95%"], hi: r["upper 95%"], p: null, late: true } : null;
    };
    const ROWS = [
      ["groupOrigin", [["Origin_Communist"], ["Origin_Independence"], ["Origin_Revolution"], ["Origin_Elite Coalition"],
                       ["Origin_Military"], ["Origin_Merger/Split"]]],
      ["groupGov", [["Gov_Clientelist"], ["Gov_Repressive"], ["Gov_Non code"]]],
      ["groupInst", [["Marxist?"]]],
      ["groupContext", [["polity2_entry", "polity2_lag1"], ["conflict_entry", "conflict_active_lag1"], ["log_gdppc_entry", "log_gdppc_lag1"]]],
    ];
    const LOGMIN = Math.log10(0.1), LOGMAX = Math.log10(10);
    const pos = (v) => Core.clamp(((Math.log10(v) - LOGMIN) / (LOGMAX - LOGMIN)) * 100, 0, 100);
    const TICKS = [0.25, 1, 4];

    const wrap = el("div", { class: "forest", style: { "--cols": COLS.length } });
    wrap.appendChild(el("div", { class: "forest-head" }, [el("span", { class: "col", text: t("analyse.s03.covariate") })].concat(COLS.map((c) => {
      const mdl = P.models[c.key];
      return el("span", { class: "col" }, [c.title, el("small", { text: t("analyse.s03.colSample", {
        note: c.note, parties: t("units.parties", { count: mdl.spells }), falls: t("units.falls", { count: mdl.events }) }) })]);
    }))));
    function cell(rec, rowLabel, colTitle, extra = "") {
      const box = el("div", { class: "forest-cell", dir: "ltr" });
      const s = svg("svg", { "aria-hidden": "true" });
      s.appendChild(svg("line", { x1: "50%", x2: "50%", y1: 0, y2: 26, stroke: "rgba(148,163,184,.3)" }));
      if (rec) {
        const sig = rec.p !== null ? rec.p < 0.05 : (rec.lo > 1 || rec.hi < 1);
        s.appendChild(svg("line", { x1: `${pos(rec.lo)}%`, x2: `${pos(rec.hi)}%`, y1: 13, y2: 13,
                                   stroke: sig ? "#e9edf2" : "#6f7a8a", "stroke-width": 1.5 }));
        s.appendChild(svg("circle", { cx: `${pos(rec.hr)}%`, cy: 13, r: 4, fill: sig ? "#e9edf2" : "#04060a",
                                     stroke: sig ? "#e9edf2" : "#aab4c1", "stroke-width": 1.5 }));
        box.addEventListener("mousemove", (e) => Core.tooltip.show(
          `<div class="t-head">${escape(colTitle + extra)}</div>${escape(rowLabel)}<br>` +
          escape(I18n.iso(`HR ${I18n.raw(rec.hr, 2)} [${I18n.raw(rec.lo, 2)} – ${I18n.raw(rec.hi, 2)}]`)) +
          " · " + escape(rec.p !== null ? pval(rec.p) : t("analyse.s03.ci95")), e.clientX, e.clientY));
        box.addEventListener("mouseleave", () => Core.tooltip.hide());
      }
      box.appendChild(s);
      return box;
    }
    ROWS.forEach(([group, items]) => {
      wrap.appendChild(el("div", { class: "forest-group", text: t(`analyse.s03.${group}`) }));
      items.forEach((names) => {
        const n0 = names[0];
        const label = n0.startsWith("Origin_") ? Labels.originShort(n0.slice(7))
          : n0 === "Gov_Non code" ? t("analyse.s03.notCoded")
          : n0.startsWith("Gov_") ? Labels.governanceShort(n0.slice(4))
          : Labels.covariateShort(n0);
        const dim = n0 === "Gov_Non code";
        const r = el("div", { class: "forest-row" + (dim ? " dim" : "") }, [el("span", { class: "name", text: label })]);
        COLS.forEach((c) => {
          const rec = pick(c.key, names);
          const nph = c.key === "corrected" && ph.corrected_covariates.includes(names[0]);
          r.appendChild(cell(rec && { ...rec }, label, c.title, nph ? t("analyse.s03.beforeCut", { cut }) : ""));
        });
        wrap.appendChild(r);
      });
    });
    wrap.appendChild(el("div", { class: "forest-group", text: t("analyse.s03.lateGroup", { cut }) }));
    ph.corrected_covariates.forEach((cv) => {
      const label = t("analyse.s03.lateRow", { label: Labels.covariateShort(cv), cut });
      const r = el("div", { class: "forest-row" }, [el("span", { class: "name", text: label })]);
      COLS.forEach((c) => r.appendChild(c.key === "corrected" ? cell(lateOf(cv), label, c.title) : el("div")));
      wrap.appendChild(r);
    });
    const axis = el("div", { class: "forest-axis" }, [el("span", { class: "label", text: t("analyse.s03.axis") })]);
    COLS.forEach(() => {
      const a = svg("svg", { "aria-hidden": "true", direction: "ltr" });
      TICKS.forEach((v) => a.appendChild(svg("text", { x: `${pos(v)}%`, y: 12, "text-anchor": "middle", fill: "#6f7a8a",
        "font-size": 10.5, "font-family": "JetBrains Mono, monospace", text: I18n.raw(v, v < 1 ? 2 : 0) })));
      axis.appendChild(el("div", { dir: "ltr" }, a));
    });
    wrap.appendChild(axis);
    parent.appendChild(el("div", { class: "forest-scroll" }, wrap));
    parent.appendChild(el("p", { class: "note", style: { marginTop: "14px" }, text: t("analyse.s03.note") }));
    parent.appendChild(howTo("forest", {}, ["hr", "ci", "pvalue"], best ? [t("analyse.howto.forest.example", {
      name: factorName(best.key), formula: hrFormula(best.hr), k: fmt(1 / best.hr, 1) })] : []));
  }

  /** Hypothèses et robustesse : test de Schoenfeld, effets avant / après le seuil, V-Dem au lieu de Polity2. */
  function robustnessDetails(parent) {
    const ph = P.proportional_hazards;
    const cut = ph.cut_years;
    // Conclusions du modèle statique significatives avec Polity2 ou avec V-Dem (sans la modalité « non codée »),
    // et celles qui restent les mêmes avec les deux mesures (même règle que src/site_text.py, vdem_summary)
    const sigRows = rows(P.vdem_robustness.static).filter((r) => r._index !== "Gov_Non code" && (r["p Polity2"] < 0.05 || r["p V-Dem"] < 0.05));
    const same = sigRows.filter((r) => r.robuste).length;
    const factors = t("units.factors", { count: ph.corrected_covariates.length });
    subhead(parent, t("analyse.s04.title"), t(same === sigRows.length ? "analyse.s04.plainAll" : "analyse.s04.plainSome",
      { factors, cut: years(cut), count: sigRows.length, same: fmt(same) }), t("analyse.s04.lead"));
    const g = el("div", { class: "grid-2" });
    parent.appendChild(g);
    const sch = rows(ph.schoenfeld).sort((a, b) => a.p - b.p);
    const pOnly = (p) => (p < 0.001 ? I18n.iso(`< ${I18n.raw(0.001, 3)}`) : fmt(p, 3));
    block(g, t("analyse.s04.schoenfeld"), t("analyse.s04.schoenfeldLabel"), [
      table([t("analyse.s04.col.covariate"), t("analyse.s04.col.stat"), "p", t("analyse.s04.col.corrected")], sch.map((r) => [
        cov(r._index), fmt(r.test_statistic, 2), pOnly(r.p), yesNo(ph.corrected_covariates.includes(r._index))]), { numeric: [1, 2] }),
      el("p", { class: "note", style: { marginTop: "10px" }, text: t("analyse.s04.schoenfeldNote", { cut }) }),
    ]);
    const right = el("div");
    g.appendChild(right);
    const early = rows(ph.early_late);
    const f = (r) => I18n.iso(`${I18n.raw(r.HR, 2)} [${I18n.raw(r["lower 95%"], 2)}–${I18n.raw(r["upper 95%"], 2)}]`);
    block(right, t("analyse.s04.earlyLate"), t("units.years", { count: cut }), [
      table([t("analyse.s04.col.covariate"), t("analyse.s04.col.before"), t("analyse.s04.col.after")], ph.corrected_covariates.map((cv) => {
        const e = early.find((r) => r.covariate === cv && r.period === "early");
        const l = early.find((r) => r.covariate === cv && r.period === "late");
        return [cov(cv), f(e), f(l)];
      }), { numeric: [1, 2] })]);
    const wald = rows(ph.wald_by_cut);
    block(right, t("analyse.s04.wald"), t("analyse.s04.waldLabel"), [
      table([t("analyse.s04.col.cut"), "χ²", t("analyse.s04.col.pJoint")], wald.map((r) => [
        t("units.years", { count: r._index }), fmt(r[Object.keys(r).find((k) => k.startsWith("Wald"))], 2), fmt(r["p joint"], 3)]),
        { numeric: [1, 2] }),
      el("p", { class: "note", style: { marginTop: "10px" }, text: t("analyse.s04.waldNote", {
        cut: t("units.years", { count: cut }), p: pval(ph.wald_p_at_cut),
        remaining: ph.remaining_violations.length ? I18n.list(ph.remaining_violations.map(cov)) : t("analyse.s04.none") }) }),
    ]);

    // V-Dem
    const vd = P.vdem_robustness;
    const vbox = el("div", { class: "block" });
    parent.appendChild(vbox);
    const seg = el("div", { class: "seg", role: "group", "aria-label": t("analyse.s04.modelAria") });
    const host = el("div");
    block(vbox, t("analyse.s04.vdem"), t("analyse.s04.vdemLabel", { r: fmt(vd.correlation_pearson, 2), count: vd.party_years_both }), [
      el("div", { class: "seg-row" }, [seg, el("span", { class: "note", text: t("analyse.s04.vdemScale") })]),
      host,
      el("div", { class: "prose", style: { marginTop: "14px" }, html: markdown(TX(P).vdem_summary) }),
    ]);
    const draw = (key) => {
      host.innerHTML = "";
      host.appendChild(table([t("analyse.s04.col.covariate"), t("analyse.s04.col.hrPolity"), "p", t("analyse.s04.col.hrVdem"), "p",
                              t("analyse.s04.col.robust")], rows(vd[key]).map((r) => [
        cov(r._index), fmt(r["HR Polity2"], 2), fmt(r["p Polity2"], 3), fmt(r["HR V-Dem"], 2), fmt(r["p V-Dem"], 3),
        yesNo(r.robuste, t("analyse.s04.same"), t("analyse.s04.different"))]), { numeric: [1, 2, 3, 4] }));
    };
    ["static", "timevarying"].forEach((k, i) => {
      const b = el("button", { type: "button", "aria-pressed": String(i === 0), text: t(`analyse.model.${k}`) });
      b.addEventListener("click", () => { seg.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); draw(k); });
      seg.appendChild(b);
    });
    draw("static");
    // Exemple « avant / après » : la covariable dont l'effet change le plus entre les deux périodes
    const change = ph.corrected_covariates.map((cv) => {
      const e = early.find((r) => r.covariate === cv && r.period === "early").HR;
      const l = early.find((r) => r.covariate === cv && r.period === "late").HR;
      return { cv, e, l, gap: Math.abs(Math.log(l / e)) };
    }).sort((a, b) => b.gap - a.gap)[0];
    parent.appendChild(howTo("robust", { factors, cut: years(cut) }, ["pvalue", "hr", "ci"], change ? [t("analyse.howto.robust.example", {
      name: factorName(change.cv), before: hrFormula(change.e), after: hrFormula(change.l) })] : []));
  }

  // ------------------------------------------------------------------ 03 prédiction (modèle de Cox et apprentissage automatique)
  function cardPrediction() {
    const groups = Findings.predictionGroups(M);
    const cox = groups.A.find((r) => r.ref);
    const better = Findings.mlBetter(M).map(Labels.model);
    const c = card("prediction", "03", t("dash.prediction.title"), better.length
      ? t("dash.prediction.answerBetter", { c: fmt(cox.mean, 2), models: I18n.list(better) })
      : t("dash.prediction.answer", { c: fmt(cox.mean, 2) }));
    const host = el("div", { class: "chart-host" });
    c.body.appendChild(host);
    drawn(() => Charts.scores(host, [{ title: t("dash.prediction.groupA"), rows: groups.A },
                                     { title: t("dash.prediction.groupB"), rows: groups.B }],
                              { chanceLabel: t("dash.prediction.chance"), perfectLabel: t("dash.prediction.perfect") }));
    benchmarkDetails(c.more);
  }

  function benchmarkDetails(parent) {
    const verdicts = Object.entries(M.task_a.verdicts).concat(Object.entries(M.task_b.verdicts));
    const better = verdicts.filter(([, v]) => v.better).map(([m]) => Labels.model(m));
    const coxC = M.task_a.metrics.find((r) => r.model === "Cox").harrell_c.mean;
    subhead(parent, t("analyse.s05.title"),
            better.length ? t("analyse.s05.plainBetter", { models: I18n.list(better), count: verdicts.length, c: fmt(coxC, 2) })
                          : t("analyse.s05.plainNone", { count: verdicts.length, c: fmt(coxC, 2) }),
            t("analyse.s05.lead", { folds: M.protocol.folds, repeats: M.protocol.repeats }));
    const T = TX(M);
    parent.appendChild(el("div", { class: "prose", html: markdown(T.q1 + "\n\n" + T.covariates) }));
    const comp = rows(M.comparison);
    const g = el("div", { class: "tasks" });
    parent.appendChild(g);
    [["task_a", "taskA", "harrell_c", "harrell", "ibs", "ibs"],
     ["task_b", "taskB", "roc_auc", "rocAuc", "log_loss", "logLoss"]].forEach(([tk, tname, m1, l1, m2, l2]) => {
      const task = M[tk];
      const verdictOf = (model) => {
        const row = comp.find((x) => x["Tâche"].startsWith(tk === "task_a" ? "A" : "B") && x["Modèle"] === model);
        const v = row ? row.Verdict : "";
        const strong = v === "référence" || v.includes("meilleur");
        return el("span", { class: "badge" + (strong ? " strong" : v.includes("pas de différence") ? "" : " weak"), text: Labels.verdict(v) });
      };
      const ms = (r) => (r ? I18n.iso(`${I18n.raw(r.mean, 3)} ± ${I18n.raw(r.sd, 3)}`) : "—");
      block(g, t(`analyse.s05.${tname}`), t("analyse.s05.taskLabel", {
        parties: t("units.parties", { count: task.spells }), falls: t("units.falls", { count: task.events }) }), [
        el("div", { class: "wide" }, table([t("analyse.s05.col.model"), t("analyse.s05.col.meanSd", { metric: t(`analyse.s05.metric.${l1}`) }),
               t(`analyse.s05.metric.${l2}`), t("analyse.s05.col.verdict")], task.metrics.map((r) => [
          Labels.model(r.model), ms(r[m1]), r[m2] ? fmt(r[m2].mean, 3) : "—", verdictOf(r.model)]), { numeric: [1, 2] }))]);
    });
    parent.appendChild(howTo("bench", { folds: fmt(M.protocol.folds), repeats: fmt(M.protocol.repeats),
                                        evaluations: fmt(M.protocol.evaluations) }, ["cindex", "pvalue"]));

    const interp = M.interpretation;
    const permBox = el("div", { class: "perm-grid" });
    interp.permutation.forEach((p) => {
      const rk = rows(p.ranking);
      const max = Math.max(...rk.map((r) => r["importance moyenne"]), 1e-9);
      permBox.appendChild(el("div", { class: "perm" }, [
        el("h4", {}, [Labels.model(p.model), el("span", { text: t("analyse.s05.task", { task: p.task }) })]),
      ].concat(rk.map((r) => {
        const pc = r["p Cox (final_panel)"];
        const sig = pc !== null && pc < 0.05;
        const row = el("div", { class: "perm-row" + (sig ? " sig" : "") }, [
          el("span", { text: Labels.factor(r.facteur) }),
          el("span", { class: "bar" }, el("i", { style: { width: `${Math.max(0, (100 * r["importance moyenne"]) / max)}%` } })),
          el("span", { class: "flag", text: sig ? "●" : "" })]);
        row.addEventListener("mousemove", (e) => Core.tooltip.show(
          `<div class="t-head">${escape(Labels.model(p.model))}</div>` +
          escape(t("analyse.s05.permTipRank", { factor: cov(r.facteur), rank: r.rang })) + "<br>" +
          escape(t("analyse.s05.permTipImportance", { value: fmt(r["importance moyenne"], 4), sd: fmt(r["écart-type"], 4) })) +
          (pc !== null ? "<br>" + escape(t("analyse.s05.permTipP", { p: fmt(pc, 3) })) : ""), e.clientX, e.clientY));
        row.addEventListener("mouseleave", () => Core.tooltip.hide());
        return row;
      }))));
    });
    block(parent, t("analyse.s05.perm"), t("analyse.s05.permLabel"), [permBox]);

    const g2 = el("div", { class: "grid-2" });
    parent.appendChild(g2);
    block(g2, t("analyse.s05.linear"), t("analyse.s05.linearLabel"), [
      table([t("analyse.s05.col.variable"), t("analyse.s05.col.model"), t("analyse.s05.col.r2"), t("analyse.s05.col.shape")],
        rows(interp.linearity).map((r, i) => [
          cov(r.variable), Labels.model(r["modèle"]), fmt(r["R² droite"], 2), T.linearity_shapes[i]]), { numeric: [2] }),
      el("div", { class: "prose", style: { marginTop: "12px" }, html: markdown(T.q2_note) })]);
    block(g2, t("analyse.s05.shap"), t("analyse.s05.shapLabel"), [
      table([t("analyse.s05.col.covariate"), "Spearman", t("analyse.s05.col.hrCox"), t("analyse.s05.col.sameSign")],
        rows(interp.shap_direction).map((r) => [
          cov(r.covariable), fmt(r["Spearman (valeur, SHAP)"], 2), fmt(Math.exp(r["log HR Cox time-varying"]), 2),
          yesNo(r["même sens"])]), { numeric: [1, 2] })]);
    parent.appendChild(el("div", { class: "prose block", html: markdown(T.practical) }));
  }

  // ------------------------------------------------------------------ 04 caractéristiques des pays (04_demographics)
  function cardCountry() {
    if (!DM) return;
    const T = TX(DM);
    const order = rows(DM.candidates).map((r) => r.variable);
    const label = (v) => T.labels[order.indexOf(v)];
    const c = card("pays", "04", t("dash.country.title"), DM.kept.length
      ? t("dash.country.answerKept", { list: I18n.list(DM.kept.map(label)) })
      : t("dash.country.answer", { tested: fmt(DM.decision.data.length) }));
    const host = el("div", { class: "chart-host" });
    c.body.appendChild(host);
    const blocks = Findings.countryRows(DM);
    // Les gains visibles sur le graphique ne sont pas significatifs (test corrigé) : on le dit sous le graphique
    if (blocks.every((r) => r.p >= 0.05)) c.body.appendChild(el("p", { class: "note chart-note", text: t("dash.country.noteNone") }));
    drawn(() => Charts.dumbbell(host, blocks.map((r) => ({ label: r.name, a: r.a, b: r.b,
      tip: () => `<div class="t-head">${escape(r.name)}</div>` + escape(t("dash.country.tip",
        { variable: r.variable, pair: I18n.iso(`${I18n.raw(r.a, 3)} → ${I18n.raw(r.b, 3)}`), p: pval(r.p) })) })),
      { legendLabels: { a: t("dash.country.m0"), b: t("dash.country.best") } }));
    countryDetails(c.more);
  }

  /** Variables des pays ajoutées une à une au modèle existant, selon des règles fixées avant les résultats. Les
      textes viennent de src/site_text.py (demo_texts) ; les tableaux, des exports du notebook. */
  function countryDetails(parent) {
    const T = TX(DM);
    const dec = rows(DM.decision);
    const comb = Object.fromEntries(rows(DM.models.combined).map((r) => [r.variable, r]));
    const order = rows(DM.candidates).map((r) => r.variable);
    const label = (v) => T.labels[order.indexOf(v)];
    const unit = (v) => T.units[order.indexOf(v)];
    const blockName = (b) => T.block_names["ABC".indexOf(b)];
    const untestable = Object.keys(DM.screening.dropped).concat(Object.keys(DM.screening.removed_for_sample));
    subhead(parent, t("analyse.country.title"), DM.kept.length
      ? t("analyse.country.plainKept", { list: I18n.list(DM.kept.map(label)) })
      : t("analyse.country.plainNone", { tested: fmt(dec.length), untestable: fmt(untestable.length), list: I18n.list(untestable.map(label)) }),
      t("analyse.country.lead", { folds: DM.protocol.folds, repeats: DM.protocol.repeats }));
    parent.appendChild(el("div", { class: "prose", html: markdown(T.answer + "\n\n" + T.near) }));
    const cols = (keys) => keys.map((k) => t(`analyse.country.col.${k}`));
    const wide = (tbl) => el("div", { class: "wide" }, tbl);

    // Variables testées : hazard ratio en tâche A, p ajustée de Holm, les quatre conditions de la décision
    const mark = (ok) => (ok === null || ok === undefined ? el("span", { class: "dim", text: "—" }) : yesNo(ok, "✓", "✗"));
    const hrCi = (r) => I18n.iso(`${I18n.raw(r["A HR"], 2)} [${I18n.raw(r["A IC bas"], 2)} – ${I18n.raw(r["A IC haut"], 2)}]`);
    block(parent, t("analyse.country.tested"), t("analyse.country.testedLabel"), [
      wide(table(cols(["block", "variable", "unit", "hr", "holm", "c1", "c2", "c3", "c4", "kept"]), dec.map((r, i) => [
        i === 0 || dec[i - 1].bloc !== r.bloc ? blockName(r.bloc) : "", label(r.variable), unit(r.variable),
        hrCi(comb[r.variable]), fmt(r["p Holm"], 3),
        mark(r["1. Holm < 0,05"]), mark(r["2. même sens"]), mark(r["3. C > M0"]), mark(r["4. contrôle"]), yesNo(r.retenue)]),
        { numeric: [3, 4] })),
      el("p", { class: "note", style: { marginTop: "10px" }, text: t("analyse.country.testedNote") }),
    ]);

    // Prédiction : dans chaque bloc, le modèle existant, le bloc seul, le meilleur ajout et le mélange, sur les mêmes partis
    const testsA = rows(DM.cv.task_a.tests);
    const score = (task, comp, model, key) => {
      const r = DM.cv[task].metrics.find((x) => x.comparison === comp && x.model === model);
      return r ? I18n.iso(`${I18n.raw(r[key].mean, 3)} ± ${I18n.raw(r[key].sd, 3)}`) : "—";
    };
    const VERDICT = { "référence": "ref", "meilleur que M0": "better", "moins bon que M0": "worse" };
    const badge = (comp, model) => {
      const r = testsA.find((x) => x["comparaison"] === comp && x["modèle"] === model);
      const key = (r && VERDICT[r.verdict]) || "none";
      return el("span", { class: "badge" + (key === "ref" || key === "better" ? " strong" : key === "worse" ? " weak" : ""),
                          text: t(`analyse.country.verdict.${key}`) });
    };
    const predRows = [];
    ["A", "B", "C"].forEach((b) => {
      const info = DM.blocks[b];
      if (!info || !info.retained.length) return;
      const comp = `bloc ${b}`;
      const [m1, m2, m3] = info.models;
      const best = testsA.filter((r) => r["comparaison"] === comp && r["modèle"].startsWith(`${m2}·`))
        .sort((x, y) => y["C de Harrell : écart"] - x["C de Harrell : écart"])[0];
      [["M0", t("analyse.country.m0")], [m1, t("analyse.country.alone")],
       [best["modèle"], t("analyse.country.best", { name: label(best["modèle"].split("·")[1]) })],
       [m3, t("analyse.country.blend")]].forEach(([model, desc], i) => predRows.push([
        i === 0 ? blockName(b) : "", desc, score("task_a", comp, model, "harrell_c"), score("task_b", comp, model, "roc_auc"),
        badge(comp, model)]));
    });
    block(parent, t("analyse.country.prediction"), t("analyse.country.predictionLabel"), [
      wide(table(cols(["block", "model", "cA", "aucB", "verdict"]), predRows, { numeric: [2, 3] })),
      el("div", { class: "prose", style: { marginTop: "14px" }, html: markdown(T.blocks.map((x) => "- " + x).join("\n")) }),
    ]);

    // Variables sans assez de données : estimations descriptives, hors règles
    const desc = rows(DM.models.descriptive);
    const fitted = (r) => r["HR (B, réduit)"] !== null;
    const reduced = (r) => (fitted(r)
      ? I18n.iso(`${I18n.raw(r["HR (B, réduit)"], 2)} [${I18n.raw(r["IC bas (B, réduit)"], 2)} – ${I18n.raw(r["IC haut (B, réduit)"], 2)}]`)
        + " · " + pval(r["p (B, réduit)"])
      : t("analyse.country.tooFew"));
    /** Lecture en langage courant, même règle que src/site_text.py (demo_link). */
    const reading = (r) => (!fitted(r) ? "—" : t(`analyse.country.link.${
      r["p (B, réduit)"] >= 0.05 ? "none" : r["HR (B, réduit)"] < 1 ? "lower" : "higher"}`));
    block(parent, t("analyse.country.untestable"), t("analyse.country.untestableLabel"), [
      wide(table(cols(["variable", "falls", "since", "reduced", "reading"]), desc.map((r) => [
        label(r.variable), I18n.iso(`${I18n.raw(r["chutes (A)"])} / ${I18n.raw(r["chutes (B)"])}`),
        r["première année (B)"] === null ? "—" : I18n.iso(String(r["première année (B)"])), reduced(r), reading(r)]),
        { numeric: [1, 2] })),
      el("div", { class: "prose", style: { marginTop: "14px" }, html: markdown(T.untestable) }),
    ]);
    parent.appendChild(el("div", { class: "prose block", html: markdown(T.comparison) }));
    block(parent, t("analyse.country.limits"), "04_demographics", [
      el("div", { class: "prose", html: markdown(T.limits.map((x) => "- " + x).join("\n") + "\n\n" + T.recommendation) })]);
    parent.appendChild(howTo("country", { tested: fmt(dec.length), c: fmt(DM.cv.full_sample_m0.harrell_c.mean, 2) },
                             ["hr", "holm", "cindex"]));
  }

  // ------------------------------------------------------------------ 05 chocs (05_shocks)
  function cardShocks() {
    if (!SH) return;
    const T = TX(SH);
    const order = rows(SH.candidates).map((r) => r.variable);
    const label = (v) => T.labels[order.indexOf(v)];
    const tested = rows(SH.decision).length;
    const c = card("chocs", "05", t("dash.shocks.title"), SH.kept.length
      ? t("dash.shocks.answerKept", { list: I18n.list(SH.kept.map(label)) })
      : t("dash.shocks.answer", { tested: fmt(tested) }));
    const host = el("div", { class: "chart-host" });
    c.body.append(host, el("p", { class: "note chart-note", text: t("dash.shocks.note") }));
    drawn(() => Charts.effects(host, Findings.shockEffects(SH), { legendLabels: {
      protect: t("dash.factors.protect"), harm: t("dash.factors.harm"), none: t("dash.factors.none") } }));
    shocksDetails(c.more);
  }

  /** Chocs de l'année précédente ajoutés un à un au modèle time-varying existant, selon des règles fixées avant les
      résultats. Textes : src/site_text.py (shocks_texts) ; tableaux : exports du notebook, sans valeur pays-année. */
  function shocksDetails(parent) {
    const T = TX(SH);
    const order = rows(SH.candidates).map((r) => r.variable);
    const at = (list, v) => list[order.indexOf(v)];
    const label = (v) => at(T.labels, v);
    const cols = (keys) => keys.map((k) => t(`analyse.shocks.col.${k}`));
    const wide = (tbl) => el("div", { class: "wide" }, tbl);
    const mark = (ok) => yesNo(ok, "✓", "✗");
    const signed = (v) => I18n.iso(`${v >= 0 ? "+" : "−"}${I18n.raw(Math.abs(v), 3)}`);
    subhead(parent, t("analyse.shocks.title"), null,
            t("analyse.shocks.lead", { folds: SH.protocol.folds, repeats: SH.protocol.repeats }));
    parent.appendChild(el("div", { class: "prose", html: markdown(T.answer + "\n\n" + T.near) }));

    // Décision : hazard ratio, p-value avant et après la correction de Holm, les trois conditions
    const dec = rows(SH.decision);
    block(parent, t("analyse.shocks.decision"), t("analyse.shocks.decisionLabel"), [
      wide(table(cols(["shock", "unit", "hr", "p", "holm", "c1", "auc", "c2", "period", "c3", "kept"]), dec.map((r) => [
        label(r.variable), at(T.units, r.variable),
        I18n.iso(`${I18n.raw(r.HR, 2)} [${I18n.raw(r["IC bas"], 2)} – ${I18n.raw(r["IC haut"], 2)}]`),
        pval(r.p), fmt(r["p Holm"], 3), mark(r["1. Holm < 0,05"]),
        `${signed(r["écart ROC-AUC"])} (${pval(r["p corrigée ROC-AUC"])})`, mark(r["2. ROC-AUC > M0"]),
        `${I18n.iso(I18n.raw(r["HR (époque)"], 2))} (${pval(r["p (époque)"])})`, mark(r["3. époque"]), yesNo(r.retenue)]),
        { numeric: [2, 3, 4, 6, 8] })),
      el("p", { class: "note", style: { marginTop: "10px" }, text: t("analyse.shocks.decisionNote") }),
    ]);

    // Couverture : définition exacte, parti-années, chutes, parti-années qui suivent un choc
    const retained = new Set(SH.screening.retained);
    block(parent, t("analyse.shocks.coverage"), t("analyse.shocks.coverageLabel"), [
      wide(table(cols(["shock", "definition", "obs", "falls", "withShock", "tested"]), rows(SH.coverage).map((r) => [
        label(r.variable), at(T.definitions, r.variable), fmt(r["parti-années"]), fmt(r.chutes),
        fmt(r["parti-années avec choc"]), yesNo(retained.has(r.variable))]), { numeric: [2, 3, 4] })),
    ]);

    // Prédiction : le modèle existant, les chocs seuls, chaque choc ajouté au modèle existant, le mélange
    const tests = rows(SH.cv.task_b.tests);
    const score = (model) => {
      const r = SH.cv.task_b.metrics.find((x) => x.comparison === "chocs" && x.model === model);
      return I18n.iso(`${I18n.raw(r.roc_auc.mean, 3)} ± ${I18n.raw(r.roc_auc.sd, 3)}`);
    };
    const VERDICT = { "référence": "ref", "meilleur que M0": "better", "moins bon que M0": "worse" };
    const predRow = (model, desc) => {
      const r = tests.find((x) => x["comparaison"] === "chocs" && x["modèle"] === model);
      const key = VERDICT[r.verdict] || "none";
      return [desc, score(model), model === "M0" ? "—" : `${signed(r["ROC-AUC : écart"])} (${pval(r["ROC-AUC : p corrigée"])})`,
              el("span", { class: "badge" + (key === "ref" || key === "better" ? " strong" : key === "worse" ? " weak" : ""),
                           text: t(`analyse.shocks.verdict.${key}`) })];
    };
    const predRows = [predRow("M0", t("analyse.shocks.model.m0")), predRow("K1", t("analyse.shocks.model.alone"))]
      .concat(dec.map((r) => predRow(`K2·${r.variable}`, t("analyse.shocks.model.plus", { name: label(r.variable) }))))
      .concat([predRow("K3", t("analyse.shocks.model.blend"))]);
    block(parent, t("analyse.shocks.prediction"), t("analyse.shocks.predictionLabel"), [
      wide(table(cols(["model", "rocAuc", "diff", "verdict"]), predRows, { numeric: [1, 2] })),
      el("div", { class: "prose", style: { marginTop: "14px" }, html: markdown(T.prediction) }),
    ]);
    if (T.untestable) parent.appendChild(el("div", { class: "prose block", html: markdown(T.untestable) }));
    block(parent, t("analyse.shocks.limits"), "05_shocks", [
      el("div", { class: "prose", html: markdown(T.limits.map((x) => "- " + x).join("\n") + "\n\n" + T.recommendation) })]);
    parent.appendChild(howTo("shocks", {}, ["hr", "holm", "pvalue"]));
  }

  // ------------------------------------------------------------------ 06 le parti et son dirigeant (06_party_leaders)
  const LEADERS = "partis et dirigeants";          // nom de la comparaison dans la validation croisée du notebook
  function cardLeaders() {
    if (!LD) return;
    const T = TX(LD);
    const order = rows(LD.candidates).map((r) => r.variable);
    const label = (v) => T.labels[order.indexOf(v)];
    const c = card("dirigeants", "06", t("dash.leaders.title"), LD.kept.length
      ? t("dash.leaders.answerKept", { list: I18n.list(LD.kept.map(label)) })
      : t("dash.leaders.answer", { tested: fmt(LD.decision.data.length) }));
    const host = el("div", { class: "chart-host" });
    c.body.append(host, el("p", { class: "note chart-note", text: t("dash.leaders.note") }));
    // Effets tous proches de ×1 : deux décimales, sinon ÷1,04 et ×1,02 s'afficheraient « ÷1,0 » et « ×1,0 »
    drawn(() => Charts.effects(host, Findings.leaderEffects(LD), { digits: 2, legendLabels: {
      protect: t("dash.factors.protect"), harm: t("dash.factors.harm"), none: t("dash.factors.none") } }));
    leadersDetails(c.more);
  }

  /** Caractéristiques du parti et de son dirigeant ajoutées une à une au modèle existant, dans les deux tâches, selon
      des règles fixées avant les résultats. Textes : src/site_text.py (leaders_texts) ; tableaux : exports du
      notebook, sans valeur dirigeant par dirigeant ni valeur de LEAD. */
  function leadersDetails(parent) {
    const T = TX(LD);
    const order = rows(LD.candidates).map((r) => r.variable);
    const at = (list, v) => list[order.indexOf(v)];
    const label = (v) => at(T.labels, v);
    const cols = (keys) => keys.map((k) => t(`analyse.leaders.col.${k}`));
    const wide = (tbl) => el("div", { class: "wide" }, tbl);
    /** Valeur sur laquelle porte une condition, suivie de ✓ ou ✗. */
    const check = (text, ok) => el("span", {}, [text, " ", yesNo(ok, "✓", "✗")]);
    const signed = (v) => I18n.iso(`${v >= 0 ? "+" : "−"}${I18n.raw(Math.abs(v), 3)}`);
    subhead(parent, t("analyse.leaders.title"), null,
            t("analyse.leaders.lead", { folds: LD.protocol.folds, repeats: LD.protocol.repeats }));
    parent.appendChild(el("div", { class: "prose", html: markdown(T.answer + "\n\n" + T.near) }));

    // Décision : hazard ratio en tâche A, puis chaque condition avec la valeur sur laquelle elle porte ; l'unité du
    // hazard ratio sous le nom de la variable
    const dec = rows(LD.decision);
    block(parent, t("analyse.leaders.decision"), t("analyse.leaders.decisionLabel"), [
      wide(table(cols(["variable", "hrA", "p", "c1", "c2", "c3", "c4", "kept"]), dec.map((r) => [
        el("span", {}, [label(r.variable), el("span", { class: "note", style: { display: "block" }, text: at(T.units, r.variable) })]),
        I18n.iso(`${I18n.raw(r["HR (A)"], 2)} [${I18n.raw(r["IC bas (A)"], 2)} – ${I18n.raw(r["IC haut (A)"], 2)}]`),
        pval(r["p (A)"]),
        check(fmt(r["p Holm"], 3), r["1. Holm < 0,05"]),
        check(I18n.iso(I18n.raw(r["HR (B)"], 2)), r["2. même sens"]),
        check(`${signed(r["écart C (A)"])} (${pval(r["p corrigée C"])})`, r["3. C > M0"]),
        check(`${I18n.iso(I18n.raw(r["HR contrôlé (A)"], 2))} (${pval(r["p contrôlé (A)"])})`, r["4. contrôles"]),
        yesNo(r.retenue)]), { numeric: [1, 2, 3, 4, 5, 6] })),
      el("p", { class: "note", style: { marginTop: "10px" }, text: t("analyse.leaders.decisionNote") }),
    ]);

    // Couverture : définition exacte, partis et chutes de la tâche A, parti-années et chutes de la tâche B
    const retained = new Set(LD.screening.retained);
    block(parent, t("analyse.leaders.coverage"), t("analyse.leaders.coverageLabel"), [
      wide(table(cols(["variable", "definition", "partiesA", "fallsA", "obsB", "fallsB", "tested"]),
        rows(LD.coverage).map((r) => [
          label(r.variable), at(T.definitions, r.variable), fmt(r["A : partis"]), fmt(r["A : chutes"]),
          fmt(r["B : parti-années"]), fmt(r["B : chutes"]), yesNo(retained.has(r.variable))]),
        { numeric: [2, 3, 4, 5] })),
    ]);

    // Quel dirigeant : la table revue à la main (tâche A) et la règle appliquée à chaque parti-année (tâche B)
    const last = LD.protocol.archigos_last_year;
    const RULE = { "Archigos, 31 décembre": "archigos", "dirigeant de la table (première année)": "first",
                   "parti sans lien": "noLink", [`après ${last}`]: "after" };
    block(parent, t("analyse.leaders.leader"), t("analyse.leaders.leaderLabel"), [
      el("div", { class: "prose", html: markdown(T.method) }),
      el("div", { style: { marginTop: "14px" } }, table(cols(["rule", "obs", "falls"]),
        rows(LD.task_b_leader_rules).map((r) => [
          RULE[r.leader_rule] ? t(`analyse.leaders.rule.${RULE[r.leader_rule]}`, { year: last }) : r.leader_rule,
          fmt(r["parti-années"]), fmt(r.chutes)]), { numeric: [1, 2] })),
    ]);

    // Prédiction : le modèle existant, les variables seules, chaque variable ajoutée au modèle existant, le mélange ;
    // les mêmes partis (tâche A) et les mêmes parti-années (tâche B) pour tous les modèles
    const VERDICT = { "référence": "ref", "meilleur que M0": "better", "moins bon que M0": "worse" };
    const METRIC = { task_a: ["harrell_c", "C de Harrell"], task_b: ["roc_auc", "ROC-AUC"] };
    const scoreCells = (task, model) => {
      const [key, name] = METRIC[task];
      const m = LD.cv[task].metrics.find((x) => x.comparison === LEADERS && x.model === model);
      const r = rows(LD.cv[task].tests).find((x) => x["comparaison"] === LEADERS && x["modèle"] === model);
      const verdict = VERDICT[r.verdict] || "none";
      return [I18n.iso(`${I18n.raw(m[key].mean, 3)} ± ${I18n.raw(m[key].sd, 3)}`),
              model === "M0" ? "—" : `${signed(r[`${name} : écart`])} (${pval(r[`${name} : p corrigée`])})`,
              el("span", { class: "badge" + (verdict === "ref" || verdict === "better" ? " strong" : verdict === "worse" ? " weak" : ""),
                           text: t(`analyse.leaders.verdict.${verdict}`) })];
    };
    const models = [["M0", t("analyse.leaders.model.m0")], ["P1", t("analyse.leaders.model.alone")]]
      .concat(dec.map((r) => [`P2·${r.variable}`, t("analyse.leaders.model.plus", { name: label(r.variable) })]))
      .concat([["P3", t("analyse.leaders.model.blend")]]);
    block(parent, t("analyse.leaders.prediction"), t("analyse.leaders.predictionLabel"), [
      wide(table(cols(["model", "cA", "diffA", "verdictA", "aucB", "diffB", "verdictB"]),
        models.map(([model, desc]) => [desc, ...scoreCells("task_a", model), ...scoreCells("task_b", model)]),
        { numeric: [1, 2, 4, 5] })),
      el("div", { class: "prose", style: { marginTop: "14px" }, html: markdown(T.prediction) }),
    ]);
    parent.appendChild(el("div", { class: "prose block", html: markdown(T.testable) }));
    block(parent, t("analyse.leaders.limits"), "06_party_leaders", [
      el("div", { class: "prose", html: markdown(T.limits.map((x) => "- " + x).join("\n") + "\n\n" + T.recommendation) })]);
    parent.appendChild(howTo("leaders", { tested: fmt(dec.length) }, ["hr", "holm", "cindex"]));
  }

  // ------------------------------------------------------------------ 07 données
  function cardData() {
    const ps = P.sample, s = E.sample;
    const c = card("donnees", "07", t("dash.data.title"), t("dash.data.answer", {
      parties: t("units.parties", { count: s.spells }), countries: t("units.countries", { count: s.countries }), year: s.last_year }));
    const host = el("div", { class: "chart-host" });
    c.body.appendChild(host);
    const steps = [
      { label: t("dash.data.steps.all"), n: ps.named_spells + ps.junta_spells_excluded },
      { label: t("dash.data.steps.named"), n: ps.named_spells },
      { label: t("dash.data.steps.model"), n: ps.static_spells },
      { label: t("dash.data.steps.falls"), n: ps.static_events },
    ];
    drawn(() => Charts.funnel(host, steps));
    dataDetails(c.more);
  }

  function dataDetails(parent) {
    const ps = P.sample;
    subhead(parent, t("analyse.s01.title"), t("analyse.s01.plain", {
      regimes: t("units.regimes", { count: ps.named_spells + ps.junta_spells_excluded }),
      named: t("units.parties", { count: ps.named_spells }), used: fmt(ps.static_spells),
      coded: Core.pct(E.checks.governance_coded_pct) }), t("analyse.s01.lead"));
    const steps = [
      [ps.named_spells + ps.junta_spells_excluded, t("analyse.s01.flowAll")],
      [ps.named_spells, t("analyse.s01.flowNamed", { count: ps.junta_spells_excluded })],
      [ps.events_all, t("analyse.s01.flowFalls")],
      [ps.static_spells, t("analyse.s01.flowStatic", { falls: t("units.falls", { count: ps.static_events }) })],
      [ps.tv_spells, t("analyse.s01.flowTv", { falls: t("units.falls", { count: ps.tv_events }),
                                                rows: t("units.partyYears", { count: ps.tv_intervals }) })],
    ];
    parent.appendChild(el("div", { class: "flow" }, steps.map(([n, d]) =>
      el("div", { class: "flow-step" }, [el("span", { class: "n", text: fmt(n) }), el("span", { class: "d", text: d })]))));

    const g = el("div", { class: "grid-2", style: { marginTop: "26px" } });
    parent.appendChild(g);
    // couverture des sources
    const coverage = el("div", { class: "coverage" });
    const covRows = rows(E.coverage.table);
    const byYear = E.coverage.by_year;
    covRows.forEach((r) => {
      const col = byYear.columns.indexOf(r._index);
      const vals = byYear.data.map((d) => d[col]);
      const yrs = byYear.index;
      const W = 300, H = 22;
      const xs = (i) => (i / (yrs.length - 1)) * W;
      let d = `M0,${H}`;
      vals.forEach((v, i) => { d += `L${xs(i).toFixed(1)},${(H - ((v || 0) / 100) * (H - 2)).toFixed(1)}`; });
      d += `L${W},${H}Z`;
      const name = Labels.source(r._index);
      const spark = svg("svg", { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: "none", role: "img", direction: "ltr",
                                 "aria-label": t("analyse.s01.coverageAria", { source: name }) },
        [svg("path", { d, fill: "rgba(233,237,242,0.14)", stroke: "#aab4c1", "stroke-width": 1, "vector-effect": "non-scaling-stroke" })]);
      spark.addEventListener("mousemove", (e) => {
        const rect = spark.getBoundingClientRect();
        const i = Core.clamp(Math.round(((e.clientX - rect.left) / rect.width) * (yrs.length - 1)), 0, yrs.length - 1);
        Core.tooltip.show(`<div class="t-head">${escape(name)} · ${yrs[i]}</div>` +
          escape(t("analyse.s01.coverageTip", { pct: Core.pct(vals[i] || 0) })), e.clientX, e.clientY);
      });
      spark.addEventListener("mouseleave", () => Core.tooltip.hide());
      coverage.appendChild(el("div", { class: "cov-row" }, [
        el("span", { class: "name", text: name }), el("span", { class: "spark-box", dir: "ltr" }, spark),
        el("span", { class: "pct", text: Core.pct(r["couverture totale (%)"]) }),
        el("span", { class: "range", text: I18n.range(r["première année"], r["dernière année"]) }),
      ]));
    });
    const c = E.checks;
    const checks = el("div", { class: "checks compact" }, [
      ["checkMarxist", Core.pct(c.pct_marxist_communist), t("analyse.s01.checkMarxistSub", { pct: Core.pct(c.pct_marxist_other) })],
      ["checkCorr", fmt(c.corr_polity_vdem, 2), t("analyse.s01.checkCorrSub", { count: c.party_years_polity_vdem })],
      ["checkGov", Core.pct(c.governance_coded_pct), t("analyse.s01.checkGovSub")],
      ["checkMacro", Core.pct(c.macro_complete_pct), t("analyse.s01.checkMacroSub")],
    ].map(([key, v, sub]) => el("div", { class: "check" }, [
      el("span", { class: "label", text: t(`analyse.s01.${key}`) }), el("span", { class: "v", text: v }), el("span", { class: "s", text: sub })])));
    block(g, t("analyse.s01.coverage"), t("analyse.s01.coverageLabel", { range: I18n.range(E.sample.first_year, E.sample.last_year) }),
          [coverage, checks]);
    // choix de modélisation
    block(g, t("analyse.s01.synthesis"), t("analyse.s01.synthesisSource"), [
      el("div", { class: "prose", html: markdown(TX(E).synthesis.map((s, i) => `${i + 1}. ${s}`).join("\n")) })]);
  }

  // ------------------------------------------------------------------ pour aller plus loin
  /** Références bibliographiques (dans leur langue d'origine, identiques sur les trois versions du site). */
  const REFS = [
    ["Miller, M. K. (2020).", "The Autocratic Ruling Parties Dataset: Origins, Durability, and Death. Journal of Conflict Resolution, 64(4), 756–782."],
    ["Coppedge, M., Gerring, J., et al. (2026).", "V-Dem Country-Year Dataset v16. Varieties of Democracy (V-Dem) Project. https://doi.org/10.23696/vdemds26"],
    ["Marshall, M. G., & Gurr, T. R. (2020).", "Polity5: Political Regime Characteristics and Transitions, 1800–2018. Center for Systemic Peace."],
    ["Goemans, H. E., Gleditsch, K. S., & Chiozza, G. (2009).", "Introducing Archigos: A Dataset of Political Leaders. Journal of Peace Research, 46(2), 269–283."],
    ["Ellis, C. M., Horowitz, M. C., & Stam, A. C. (2015).", "Introducing the LEAD Data Set. International Interactions, 41(4), 718–741; via Miller, S. V. (2022), peacesciencer, Conflict Management and Peace Science, 39(6)."],
    ["Bell, C., Besaw, C., & Frank, M. (2021).", "The Rulers, Elections, and Irregular Governance (REIGN) Dataset. One Earth Future."],
    ["Gleditsch, N. P., et al. (2002); Davies, S., et al. (2026).", "UCDP/PRIO Armed Conflict Dataset. Journal of Peace Research."],
    ["Bolt, J., & van Zanden, J. L. (2024).", "Maddison Project Database 2023. https://doi.org/10.34894/INZBF2"],
    ["Natural Earth.", "Admin 0 – Countries, 1:50m."],
    ["Cox, D. R. (1972).", "Regression Models and Life-Tables. JRSS B, 34(2), 187–202."],
    ["Lin, D. Y., & Wei, L. J. (1989).", "The Robust Inference for the Cox Proportional Hazards Model. JASA, 84(408)."],
    ["Grambsch, P. M., & Therneau, T. M. (1994).", "Proportional hazards tests and diagnostics based on weighted residuals. Biometrika, 81(3)."],
    ["Nadeau, C., & Bengio, Y. (2003).", "Inference for the Generalization Error. Machine Learning, 52(3)."],
    ["Ishwaran, H., et al. (2008).", "Random survival forests. The Annals of Applied Statistics, 2(3)."],
    ["Magaloni, B. (2006).", "Voting for Autocracy: Hegemonic Party Survival and Its Demise in Mexico. Cambridge University Press."],
    ["Davidson-Pilon, C. (2019).", "lifelines: survival analysis in Python. JOSS, 4(40), 1317."],
    ["United Nations, DESA, Population Division (2024).", "World Population Prospects 2024."],
    ["World Bank (2026).", "World Development Indicators (unemployment: ILO modelled estimates, ILOSTAT)."],
    ["Delforge, D., et al. (2025).", "EM-DAT: the Emergency Events Database. International Journal of Disaster Risk Reduction. Data: CRED / UCLouvain, EM-DAT archive v2 (2026). https://doi.org/10.14428/DVN/I0LTPH"],
    ["NOAA National Centers for Environmental Information (2026).", "NCEI/WDS Global Significant Earthquake Database. https://doi.org/10.7289/V5TD9V7K"],
    ["Lacina, B., & Gleditsch, N. P. (2005).", "Monitoring Trends in Global Combat: A New Dataset of Battle Deaths. European Journal of Population, 21(2–3), 145–166; PRIO Battle Deaths Dataset v3.1."],
    ["Davies, S., Pettersson, T., & Öberg, M. (2026).", "Organized violence 1989–2025, and violent political protests. Journal of Peace Research, 63(4); UCDP Battle-Related Deaths Dataset v26.1."],
    ["World Peace Foundation (2025).", "Historic Famines (WPF Famine Dataset), processed by Our World in Data."],
    ["FAO (2026).", "FAOSTAT: Production Indices. Food and Agriculture Organization of the United Nations."],
    ["Vogt, M., Bormann, N.-C., Rüegger, S., Cederman, L.-E., Hunziker, P., & Girardin, L. (2015).", "Integrating Data on Ethnicity, Geography, and Conflict: The Ethnic Power Relations Data Set Family. Journal of Conflict Resolution, 59(7)."],
    ["Alesina, A., Devleeschauwer, A., Easterly, W., Kurlat, S., & Wacziarg, R. (2003).", "Fractionalization. Journal of Economic Growth, 8(2); via Teorell, J., et al. (2026), The Quality of Government Standard Dataset, version Jan26."],
    ["Clio-Infra (2018).", "Average Years of Education (via V-Dem v16)."],
    ["Spannagel, J., & Kinzelbach, K. (2022).", "The Academic Freedom Index and its indicators: Introduction to new global time-series V-Dem data. Quality & Quantity."],
    ["Holm, S. (1979).", "A Simple Sequentially Rejective Multiple Test Procedure. Scandinavian Journal of Statistics, 6(2)."],
  ];
  /** Les notions du tableau de bord, définies en langage courant ; chaque exemple vient des chiffres exportés. */
  const GLOSSARY = ["hr", "censoring", "median", "cindex", "pvalue", "ci", "holm"];

  function moreSection() {
    const box = el("section", { class: "dash-more", "aria-labelledby": "plus-title" },
                   [el("h2", { class: "label", id: "plus-title", text: t("dash.moreTitle") })]);
    report.appendChild(box);
    const acc = (id, title, build) => {
      const body = el("div", { class: "acc-body" });
      box.appendChild(el("details", { class: "acc", id }, [el("summary", {}, [el("span", { text: title })]), body]));
      build(body);
    };
    acc("conclusion", t("dash.acc.conclusion"), (b) => b.appendChild(el("div", { class: "prose", html: markdown(TX(P).conclusion) })));
    acc("questions", t("dash.acc.questions"), (b) => {
      const robust = robustFactors();
      b.appendChild(el("p", { class: "sub-plain", text: robust.length
        ? t("analyse.s06.plain", { count: robust.length, list: I18n.list(robust.map(factorName)) }) : t("analyse.s06.plainNone") }));
      b.appendChild(el("p", { class: "note sub-lead", text: t("analyse.s06.lead") }));
      TX(P).research_questions.forEach((q, i) => {
        b.appendChild(el("details", { class: "qa" }, [
          el("summary", {}, [el("span", { class: "n", text: String(i + 1).padStart(2, "0") }), el("span", { text: q.title })]),
          el("div", { class: "prose", html: markdown(q.body) }),
        ]));
      });
    });
    acc("limites", t("dash.acc.limits"), (b) => {
      const ps = P.sample;
      b.appendChild(el("p", { class: "sub-plain", text: t("analyse.s07.plain", {
        parties: t("units.parties", { count: ps.named_spells }), censored: fmt(ps.named_spells - ps.events_all),
        year: E.sample.last_year, clientelist: t("units.parties", { count: P.facts.governance_counts_static.Clientelist }) }) }));
      b.appendChild(el("div", { class: "prose", html: markdown(TX(P).limits) }));
      block(b, t("analyse.s07.ml"), "03_ml_survival", [
        el("div", { class: "prose", html: markdown(TX(M).noise.map((n) => "- " + n).join("\n")) })]);
    });
    acc("sources", t("dash.acc.sources"), (b) => {
      b.appendChild(el("p", { class: "sub-plain", text: t("analyse.s08.plain", { date: I18n.iso(S.built) }) }));
      b.appendChild(el("ul", { class: "refs" }, REFS.map(([a, x]) => el("li", { dir: "ltr" }, [el("strong", { text: a }), " " + x]))));
      b.appendChild(el("p", { class: "note", text: t("analyse.s08.note", { date: S.built }) }));
    });
    acc("glossaire", t("dash.acc.glossary"), (b) => {
      const s = E.sample, km = E.km_overall, best = protective();
      const params = {
        censoring: { censored: fmt(s.censored), total: t("units.parties", { count: s.spells }), year: s.last_year },
        median: { median: years(km.median), range: I18n.rangeN(km.median_lo, km.median_hi) },
        cindex: { c: fmt(MOD.performance.c_index_cv.mean, 2) },
      };
      const examples = best ? {
        hr: t("analyse.gl.hr.example", { name: factorName(best.key), formula: hrFormula(best.hr), k: fmt(1 / best.hr, 1) }),
        pvalue: t("analyse.gl.pvalue.example", { name: factorName(best.key), p: pval(best.p) }),
        ci: t("analyse.gl.ci.example", { name: factorName(best.key), range: I18n.rangeN(best.lo, best.hi, 2) }),
      } : {};
      b.appendChild(el("dl", { class: "glossary" }, GLOSSARY.map((k) => el("div", { class: "gl-item", id: `gl-${k}` }, [
        el("dt", { text: t(`analyse.gl.${k}.term`) }),
        el("dd", {}, [t(`analyse.gl.${k}.def`, params[k] || {}), examples[k] ? el("span", { class: "gl-example", text: examples[k] }) : null]),
      ]))));
    });
  }

  // ------------------------------------------------------------------ rendu complet
  function render() {
    const current = [...document.querySelectorAll(".dcard, .acc")].find((s) => s.getBoundingClientRect().bottom > 120);
    report.innerHTML = "";
    resizers = [];
    kpis();
    grid = el("div", { class: "dash-grid" });
    report.appendChild(grid);
    [cardSurvival, cardFactors, cardPrediction, cardCountry, cardShocks, cardLeaders, cardData].forEach((fn) => fn());
    moreSection();
    if (current && current.id) {
      const target = document.getElementById(current.id);
      if (target) target.scrollIntoView({ block: "start" });
    }
  }
  /** Lien vers une carte ou une notion (#survie, #gl-hr) : ouvre la partie repliée qui la contient, puis y va. */
  function goTo(id) {
    const target = id && document.getElementById(id);
    if (!target) return;
    const folded = target.closest("details");
    if (folded) folded.open = true;
    target.scrollIntoView({ block: "start" });
  }
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const target = document.getElementById(a.getAttribute("href").slice(1));
    const folded = target && target.closest("details");
    if (folded && !folded.open) folded.open = true;
  });
  render();
  if (location.hash) requestAnimationFrame(() => goTo(decodeURIComponent(location.hash.slice(1))));
  I18n.onChange(() => { Core.tooltip.hide(); render(); });
  // Page prête (pour les tests) une fois les graphiques dessinés, au même rafraîchissement de l'écran
  requestAnimationFrame(() => { window.__ready = true; document.documentElement.dataset.ready = "1"; });
})();
