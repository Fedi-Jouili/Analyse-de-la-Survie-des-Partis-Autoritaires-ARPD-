/* Prédiction de survie à partir du modèle de Cox exporté (src/cox_static_model.json).
   Portage fidèle de api/predictor.py : mêmes formules, mêmes règles d'avertissement.
   L'équivalence avec la version Python est vérifiée par tests/test_frontend_model.py. */
(function (root) {
  "use strict";

  const DEFAULT_HORIZON = 30;
  const BAND_PERCENTILES = [2.5, 97.5];
  const MIN_SPELLS = 20;

  const BOOLEAN_LABELS = {
    marxist: ["une idéologie marxiste-léniniste", "pas d'idéologie marxiste-léniniste"],
    conflict_entry: ["un conflit armé à l'entrée au pouvoir", "pas de conflit armé à l'entrée au pouvoir"],
  };

  /** Vecteurs de covariables (période précoce, période tardive) dans l'ordre du modèle. */
  function featureVectors(data, profile) {
    const model = data.model;
    const values = {};
    for (const spec of model.inputs) {
      if ("fixed" in spec) values[spec.feature] = spec.fixed;
      else if ("level" in spec) values[spec.feature] = profile[spec.input] === spec.level ? 1 : 0;
      else values[spec.feature] = Number(profile[spec.input]);
    }
    const early = Object.assign({}, values);
    const late = Object.assign({}, values);
    for (const v of model.nph_covariates) {
      early[v + "_x_late"] = 0;
      late[v + "_x_late"] = values[v];
    }
    return [model.features.map((f) => early[f]), model.features.map((f) => late[f])];
  }

  function risk(beta, mean, x) {
    let s = 0;
    for (let j = 0; j < beta.length; j++) s += (x[j] - mean[j]) * beta[j];
    return Math.exp(s);
  }

  /** S(t) pour t = 0..H0.length-1 (lifelines centre les covariables sur leur moyenne). */
  function survivalCurve(beta, mean, H0, xEarly, xLate, cut) {
    const rE = risk(beta, mean, xEarly);
    const rL = risk(beta, mean, xLate);
    const H0cut = H0[cut];
    return H0.map((h, t) => Math.exp(-(t <= cut ? rE * h : rE * H0cut + rL * (h - H0cut))));
  }

  /** Percentile à interpolation linéaire (méthode par défaut de numpy). */
  function percentile(sorted, q) {
    const pos = (sorted.length - 1) * q / 100;
    const lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  }

  function supportWarnings(data, profile) {
    const support = data.support, form = data.form;
    const out = [];
    const checks = [
      [`l'origine « ${profile.origin} »`, support.origin[profile.origin]],
      [`la stratégie « ${profile.governance} »`, support.governance[profile.governance]],
    ];
    for (const [name, [labTrue, labFalse]] of Object.entries(BOOLEAN_LABELS)) {
      const value = Boolean(profile[name]);
      checks.push([value ? labTrue : labFalse, support[name][value ? "true" : "false"]]);
    }
    for (const [label, n] of checks) {
      if (n < MIN_SPELLS) {
        out.push(`Seulement ${n} partis de l'échantillon d'estimation ont ${label} ` +
                 `(seuil d'alerte : ${MIN_SPELLS}) : la prédiction est peu précise pour ce choix.`);
      }
    }
    const nCombo = support.origin_x_governance[profile.origin][profile.governance];
    if (nCombo === 0) {
      out.push(`Aucun parti de l'échantillon ne combine l'origine « ${profile.origin} » et la stratégie ` +
               `« ${profile.governance} » (parmi les ${data.sample.spells - support.governance_not_coded} ` +
               "partis dont la stratégie est codée) : la prédiction est une extrapolation.");
    }
    const pol = form.polity2_entry;
    if (!(pol.p05 <= profile.polity2_entry && profile.polity2_entry <= pol.p95)) {
      const g = (v) => String(Number(v.toPrecision(6)));
      out.push(`Le score Polity2 choisi (${profile.polity2_entry}) est en dehors de l'intervalle où se situent ` +
               `90 % des partis de l'échantillon (${g(pol.p05)} à ${g(pol.p95)}).`);
    }
    return out;
  }

  /** Les mêmes avertissements sous forme de codes et de valeurs, dans le même ordre (traduits par le site). */
  function supportDetails(data, profile) {
    const support = data.support, form = data.form;
    const out = [];
    const checks = [
      ["origin", profile.origin, support.origin[profile.origin]],
      ["governance", profile.governance, support.governance[profile.governance]],
    ];
    for (const name of Object.keys(BOOLEAN_LABELS)) {
      const value = Boolean(profile[name]);
      checks.push([name, value, support[name][value ? "true" : "false"]]);
    }
    for (const [variable, value, n] of checks) {
      if (n < MIN_SPELLS) out.push({ code: "small_group", values: { variable, value, n, threshold: MIN_SPELLS } });
    }
    if (support.origin_x_governance[profile.origin][profile.governance] === 0) {
      out.push({ code: "unseen_combination", values: { origin: profile.origin, governance: profile.governance,
                                                       coded: data.sample.spells - support.governance_not_coded } });
    }
    const pol = form.polity2_entry;
    if (!(pol.p05 <= profile.polity2_entry && profile.polity2_entry <= pol.p95)) {
      out.push({ code: "polity_outside_range", values: { value: profile.polity2_entry, p05: pol.p05, p95: pol.p95 } });
    }
    return out;
  }

  /** Courbe, médiane, bande bootstrap à 95 % et avertissements pour un profil. */
  function predict(data, profile, horizon = DEFAULT_HORIZON) {
    const model = data.model, boot = data.bootstrap;
    const tMax = model.t_max;
    const notes = [], noteDetails = [];
    let horizonUsed = Math.trunc(horizon);
    if (horizonUsed > tMax) {
      notes.push(`Horizon ramené de ${horizonUsed} à ${tMax} ans, la plus longue durée observée dans les données.`);
      noteDetails.push({ code: "horizon_capped", values: { requested: horizonUsed, used: tMax } });
      horizonUsed = tMax;
    }
    const [xE, xL] = featureVectors(data, profile);
    const cut = model.cut_years;
    const survival = survivalCurve(model.coefficients, model.norm_mean, model.baseline_cumulative_hazard, xE, xL, cut)
      .slice(0, horizonUsed + 1);
    const curves = boot.coefficients.map((b, i) =>
      survivalCurve(b, boot.norm_mean[i], boot.baseline_cumulative_hazard[i], xE, xL, cut));
    const lower = [], upper = [];
    for (let t = 0; t <= horizonUsed; t++) {
      const col = curves.map((c) => c[t]).sort((a, b) => a - b);
      lower.push(percentile(col, BAND_PERCENTILES[0]));
      upper.push(percentile(col, BAND_PERCENTILES[1]));
    }
    const below = survival.findIndex((s) => s <= 0.5);
    const median = below >= 0
      ? { years: below, reached: true, text: `La moitié des partis comparables a quitté le pouvoir après ${below} ans.` }
      : { years: null, reached: false,
          text: `Médiane non atteinte : plus de la moitié des partis comparables sont encore au pouvoir après ${horizonUsed} ans.` };
    return {
      times: Array.from({ length: horizonUsed + 1 }, (_, t) => t),
      survival,
      band: { level: 0.95, lower, upper, replicates: boot.coefficients.length },
      median,
      horizon_requested: Math.trunc(horizon),
      horizon_used: horizonUsed,
      notes,
      warnings: supportWarnings(data, profile),
      note_details: noteDetails,
      warning_details: supportDetails(data, profile),
    };
  }

  /** Effets multiplicatifs (hazard ratios) de chaque choix par rapport au profil de référence. */
  function levers(data, profile) {
    const model = data.model;
    const beta = Object.fromEntries(model.features.map((f, i) => [f, model.coefficients[i]]));
    const out = [];
    const add = (feature, label) => {
      const early = Math.exp(beta[feature]);
      const lateKey = feature + "_x_late";
      const late = lateKey in beta ? Math.exp(beta[feature] + beta[lateKey]) : null;
      out.push({ feature, label, early, late });
    };
    if (profile.origin !== data.form.origin.reference) add("Origin_" + profile.origin, "origin");
    if (profile.governance !== data.form.governance.reference) add("Gov_" + profile.governance, "governance");
    if (profile.marxist) add("Marxist?", "marxist");
    if (profile.conflict_entry) add("conflict_entry", "conflict_entry");
    const pol = Math.exp(beta.polity2_entry * (profile.polity2_entry - data.form.polity2_entry.median));
    out.push({ feature: "polity2_entry", label: "polity2", early: pol, late: null,
               delta: profile.polity2_entry - data.form.polity2_entry.median });
    return out;
  }

  const Survival = { DEFAULT_HORIZON, MIN_SPELLS, featureVectors, survivalCurve, predict, supportWarnings, supportDetails, levers };
  if (typeof module !== "undefined" && module.exports) module.exports = Survival;
  else root.Survival = Survival;
})(typeof window !== "undefined" ? window : globalThis);
