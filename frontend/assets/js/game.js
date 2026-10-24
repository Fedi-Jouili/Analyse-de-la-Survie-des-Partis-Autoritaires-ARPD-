/* Règles du jeu de la simulation : confiance d'une prédiction, étoiles des défis et calibrage des défis.
   Fonctions pures, sans navigateur : testées avec Node (tests/js/run_game.js, tests/test_frontend_game.py). */
(function (root) {
  "use strict";

  /** Confiance d'une prédiction, lue dans ses avertissements (Survival.predict(...).warning_details) :
      - élevée : aucun avertissement ;
      - moyenne : un seul avertissement, soit un choix porté par peu de partis mais au moins LOW_N
        (small_group, n ≥ 10), soit un score Polity2 hors de l'intervalle de 90 % des partis (polity_outside_range) ;
      - faible : une combinaison origine × stratégie jamais observée (unseen_combination), un choix porté par
        moins de LOW_N partis (small_group, n < 10), ou au moins deux avertissements.
      Un horizon ramené à la plus longue durée observée (horizon_capped) est une note, pas un avertissement. */
  const LOW_N = 10;
  const LEVELS = ["low", "medium", "high"];
  /** Étoiles possibles dans un défi selon la confiance de la prédiction. */
  const MAX_STARS = { high: 3, medium: 2, low: 1 };

  function confidence(details) {
    const reasons = (details || []).filter((d) => d.code !== "horizon_capped");
    let level = "high";
    if (reasons.length >= 2) level = "low";
    else if (reasons.length === 1) {
      const d = reasons[0];
      const weak = d.code === "unseen_combination" || (d.code === "small_group" && d.values.n < LOW_N);
      level = weak ? "low" : "medium";
    }
    return { level, reasons };
  }

  /** Probabilité en pour cent entier, telle qu'elle est affichée. */
  const shownPct = (p) => Math.round(p * 100);
  /** Étoiles gagnées par la seule probabilité : un seuil est atteint quand le pourcentage affiché l'atteint. */
  const starsFor = (p, thresholds) => thresholds.filter((s) => shownPct(p) >= Math.round(s * 100)).length;

  /** Résultat d'un défi : étoiles gagnées par la probabilité (earned), plafonnées par la confiance (stars). */
  function grade(p, thresholds, details) {
    const conf = confidence(details);
    const earned = starsFor(p, thresholds);
    const stars = Math.min(earned, MAX_STARS[conf.level]);
    return { earned, stars, capped: stars < earned, level: conf.level, reasons: conf.reasons, max: MAX_STARS[conf.level] };
  }

  /** Tous les profils que le joueur peut composer : 7 origines × 3 stratégies × 2² interrupteurs × 21 scores Polity2
      = 1 764 profils (form : D.form du modèle exporté). */
  function profiles(form) {
    const out = [];
    const pol = form.polity2_entry;
    for (const origin of form.origin.levels) for (const governance of form.governance.levels)
      for (const marxist of [false, true]) for (const conflict_entry of [false, true])
        for (let p = pol.min_allowed; p <= pol.max_allowed; p++) {
          out.push({ origin, governance, marxist, conflict_entry, polity2_entry: p });
        }
    return out;
  }
  const matches = (profile, lock) => Object.entries(lock).every(([k, v]) => profile[k] === v);

  /** Meilleur niveau de confiance que permettent les paramètres imposés d'un défi, avec un profil qui l'atteint.
      details(profile) : avertissements du profil (Survival.supportDetails). */
  function bestLevel(lock, all, details) {
    let best = null;
    for (const p of all) {
      if (!matches(p, lock)) continue;
      const level = confidence(details(p)).level;
      if (!best || LEVELS.indexOf(level) > LEVELS.indexOf(best.level)) best = { level, profile: p };
      if (level === "high") break;
    }
    return best;
  }

  /** Calibrage d'un défi sur les 1 764 profils possibles :
      1. profils compatibles avec les paramètres imposés ;
      2. meilleur niveau de confiance atteint parmi eux : il fixe le nombre d'étoiles possibles du défi
         (3 en confiance élevée ; 2 pour le coup d'État, car toute origine militaire repose sur 17 partis) ;
      3. sommet = meilleure probabilité d'être encore au pouvoir à la durée visée parmi les profils de ce niveau,
         arrondie au pour cent inférieur : le meilleur profil bien documenté obtient toutes les étoiles possibles ;
      4. seuils : ★ = 50 % (l'objectif du défi), ★★★ = sommet, ★★ = milieu des deux, arrondi au pour cent inférieur ;
      5. si ces trois seuils ne sont pas trois pourcentages distincts (sommet < 52 %), la durée visée est raccourcie
         de 5 ans et le calcul recommence.
      survivalAt(profile, T) : probabilité prédite d'être encore au pouvoir après T ans. */
  function calibrate(lock, target, all, { survivalAt, details }) {
    const pool = all.filter((p) => matches(p, lock)).map((p) => ({ p, level: confidence(details(p)).level }));
    const level = pool.reduce((b, x) => (LEVELS.indexOf(x.level) > LEVELS.indexOf(b) ? x.level : b), "low");
    const top = pool.filter((x) => x.level === level).map((x) => x.p);
    for (let T = target; T >= 5; T -= 5) {
      const peak = Math.floor(Math.max(...top.map((p) => survivalAt(p, T))) * 100 + 1e-9);
      const mid = Math.floor((50 + peak) / 2);
      if (peak >= 52) return { target: T, stars: [0.5, mid / 100, peak / 100], level, max: MAX_STARS[level] };
    }
    return null;
  }

  /** Défis : paramètres imposés, durée visée (années) et seuils des étoiles (probabilité d'être encore au pouvoir
      à cette durée). Calibrés par calibrate() sur le modèle exporté sans la monarchie (octobre 2026) ;
      tests/test_frontend_game.py vérifie que ces valeurs suivent toujours la règle. Durées visées au départ :
      président 10 ans, coup d'État 15, ouverture 20, guerre 30, indépendance 40 ; la règle les a raccourcies pour le
      coup d'État (10), l'ouverture (15) et l'indépendance (25), faute de profil au-dessus de 52 % à la durée prévue. */
  const CHALLENGES = [
    { id: "president", lock: { origin: "Dictator-Created", governance: "Policy-Based" }, target: 10, stars: [0.5, 0.54, 0.59] },
    { id: "coup", lock: { origin: "Military" }, target: 10, stars: [0.5, 0.63, 0.76] },
    { id: "opening", lock: { polity2_entry: 6 }, target: 15, stars: [0.5, 0.55, 0.6] },
    { id: "war", lock: { conflict_entry: true }, target: 30, stars: [0.5, 0.52, 0.55] },
    { id: "independence", lock: { origin: "Independence" }, target: 25, stars: [0.5, 0.53, 0.57] },
  ];

  const Game = { LOW_N, LEVELS, MAX_STARS, CHALLENGES, confidence, starsFor, grade, profiles, matches, bestLevel, calibrate };
  if (typeof module !== "undefined" && module.exports) module.exports = Game;
  else root.Game = Game;
})(typeof window !== "undefined" ? window : globalThis);
