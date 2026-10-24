/* Résultats repris par l'accueil et le tableau de bord (page Analyse) : mêmes règles de sélection, mêmes libellés.
   Les chiffres viennent des exports des notebooks (frontend/data/stats.js). */
(function () {
  "use strict";

  const t = I18n.t;
  /** Tableau « split » de pandas -> liste d'objets. */
  const rows = (split) => split.data.map((r, i) =>
    Object.assign({ _index: split.index[i] }, Object.fromEntries(split.columns.map((c, j) => [c, r[j]]))));

  /** Nom d'un facteur sur une ligne de graphique : « Origine : Révolution », « Idéologie marxiste-léniniste ». */
  function factorLabel(c) {
    if (c.startsWith("Origin_")) return t("analyse.s02.group.origin") + t("common.colon") + Labels.originShort(c.slice(7));
    if (c.startsWith("Gov_")) return t("analyse.s02.group.governance") + t("common.colon") + Labels.governanceShort(c.slice(4));
    return Labels.covariateShort(c);
  }
  /** Nom d'un facteur dans une phrase (« l'origine révolutionnaire »). */
  const factorName = (c) => (I18n.get("analyse.factorName") || {})[c] || Labels.covariate(c);

  /** Facteurs du modèle de Cox statique en multiplicateurs du risque, du plus protecteur au plus défavorable :
      variables indicatrices seulement (ni Polity2, dont l'effet est donné par point, ni la modalité « non codée »,
      qui n'est pas une stratégie). */
  function staticEffects(P) {
    return P.models.static.hazard_ratios
      .filter((h) => !/polity2|gdppc|Non code/.test(h.covariate))
      .map((h) => ({ key: h.covariate, label: factorLabel(h.covariate), hr: h.hr, lo: h.lo, hi: h.hi, p: h.p }))
      .sort((a, b) => a.hr - b.hr);
  }
  const significant = (P) => staticEffects(P).filter((r) => r.p < 0.05);
  const protective = (P) => significant(P).find((r) => r.hr < 1) || null;
  const harmful = (P) => [...significant(P)].reverse().find((r) => r.hr > 1) || null;

  /** Scores en validation croisée : C de Harrell (tâche A, durée au pouvoir), ROC-AUC (tâche B, chute dans l'année). */
  function predictionGroups(M) {
    const pick = (list, key, ref) => list.filter((r) => r[key]).map((r) => ({
      model: r.model, label: Labels.model(r.model), mean: r[key].mean, sd: r[key].sd, ref: r.model === ref }));
    return { A: pick(M.task_a.metrics, "harrell_c", "Cox"), B: pick(M.task_b.metrics, "roc_auc", "Cox time-varying") };
  }
  /** Modèles d'apprentissage automatique qui prédisent mieux que le modèle de Cox selon les règles de 03_ml_survival. */
  const mlBetter = (M) => Object.entries(M.task_a.verdicts).concat(Object.entries(M.task_b.verdicts))
    .filter(([, v]) => v.better).map(([m]) => m);

  /** Test des caractéristiques des pays (04_demographics) : pour chaque bloc, C de Harrell du modèle existant et de
      son meilleur ajout, sur les mêmes partis (tâche A). */
  function countryRows(DM) {
    const T = DM.texts[I18n.lang] || DM.texts.fr;
    const order = rows(DM.candidates).map((r) => r.variable);
    const label = (v) => T.labels[order.indexOf(v)];
    const tests = rows(DM.cv.task_a.tests);
    const score = (comp, model) => DM.cv.task_a.metrics.find((x) => x.comparison === comp && x.model === model).harrell_c.mean;
    return ["A", "B", "C"].filter((b) => DM.blocks[b] && DM.blocks[b].retained.length).map((b) => {
      const comp = `bloc ${b}`, m2 = DM.blocks[b].models[1];
      const best = tests.filter((r) => r["comparaison"] === comp && r["modèle"].startsWith(`${m2}·`))
        .sort((x, y) => y["C de Harrell : écart"] - x["C de Harrell : écart"])[0];
      return { block: b, name: T.block_names["ABC".indexOf(b)], variable: label(best["modèle"].split("·")[1]),
               a: score(comp, "M0"), b: score(comp, best["modèle"]), gap: best["C de Harrell : écart"],
               p: best["C de Harrell : p corrigée"] };
    });
  }

  /** Chocs testés par 05_shocks.ipynb : hazard ratio dans M0 + le choc (Tâche B, erreurs groupées par pays), du plus
      faible au plus fort ; la couleur suit la p-value corrigée par la méthode de Holm, comme la décision. */
  function shockEffects(SH) {
    const T = SH.texts[I18n.lang] || SH.texts.fr;
    const order = rows(SH.candidates).map((r) => r.variable);
    return rows(SH.decision).map((r) => ({
      key: r.variable, label: T.labels[order.indexOf(r.variable)], hr: r.HR, lo: r["IC bas"], hi: r["IC haut"],
      p: r["p Holm"], pText: t("dash.shocks.pHolm", { p: I18n.pval(r["p Holm"]) }),
    })).sort((a, b) => a.hr - b.hr);
  }

  /** Caractéristiques du parti et de son dirigeant testées par 06_party_leaders.ipynb : hazard ratio dans M0 + la
      variable (Tâche A, erreurs groupées par pays), du plus faible au plus fort ; la couleur suit la p-value corrigée
      par la méthode de Holm, comme la décision. */
  function leaderEffects(LD) {
    const T = LD.texts[I18n.lang] || LD.texts.fr;
    const order = rows(LD.candidates).map((r) => r.variable);
    return rows(LD.decision).map((r) => ({
      key: r.variable, label: T.labels[order.indexOf(r.variable)], hr: r["HR (A)"], lo: r["IC bas (A)"],
      hi: r["IC haut (A)"], p: r["p Holm"], pText: t("dash.leaders.pHolm", { p: I18n.pval(r["p Holm"]) }),
    })).sort((a, b) => a.hr - b.hr);
  }

  window.Findings = { rows, factorLabel, factorName, staticEffects, significant, protective, harmful, predictionGroups,
                      mlBetter, countryRows, shockEffects, leaderEffects };
})();
