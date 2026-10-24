/* Libellés des catégories des données (ARPD, V-Dem, modèle) dans la langue du site.
   Les textes sont dans les dictionnaires (clé « labels ») ; un code absent du dictionnaire s'affiche tel quel. */
(function () {
  "use strict";

  /** Couleurs des types de régime (palette validée pour le daltonisme sur fond sombre). */
  const HEX = {
    nodata: "#0e131a", party: "#c98500", military: "#d55181", monarchy: "#3987e5",
    other_arpd: "#9a958a", other_vdem: "#9a958a", democracy: "#263445", dependent: "#161c25",
  };
  /** Ordre et regroupement de la légende du globe. */
  const LEGEND = [
    { key: "party", cats: ["party"] },
    { key: "military", cats: ["military"] },
    { key: "monarchy", cats: ["monarchy"] },
    { key: "other_arpd", cats: ["other_arpd", "other_vdem"] },
    { key: "democracy", cats: ["democracy"] },
    { key: "dependent", cats: ["dependent"] },
    { key: "nodata", cats: ["nodata"] },
  ];

  const pick = (group, code) => {
    const d = I18n.get(`labels.${group}`) || {};
    return d[code] !== undefined ? d[code] : code;
  };

  window.Labels = {
    HEX,
    LEGEND,
    cat: (c) => pick("category", c),
    regimeType: (t) => pick("regimeType", t),
    origin: (o) => pick("origin", o),
    originShort: (o) => pick("originShort", o),
    gained: (g) => pick("gained", g),
    ended: (e) => pick("ended", e),
    governance: (g) => pick("governance", g),
    governanceShort: (g) => pick("governanceShort", g),
    /** Classe V-Dem v2x_regime (0 à 3) : libellé court, et forme utilisée dans une phrase. */
    vdemRegime: (i) => (I18n.get("labels.vdemRegime") || [])[i] || "—",
    vdemRegimeInSentence: (i) => (I18n.get("labels.vdemRegimeInSentence") || [])[i] || "—",
    covariate: (c) => pick("covariate", c),
    /** Libellé court (lignes du forest plot) ; à défaut, le libellé complet. */
    covariateShort: (c) => { const d = I18n.get("labels.covariateShort") || {}; return d[c] !== undefined ? d[c] : pick("covariate", c); },
    factor: (f) => pick("factor", f),
    model: (m) => pick("model", m),
    source: (s) => pick("source", s),
    era: (e) => pick("era", e),
    verdict: (v) => pick("verdict", v),
  };
})();
