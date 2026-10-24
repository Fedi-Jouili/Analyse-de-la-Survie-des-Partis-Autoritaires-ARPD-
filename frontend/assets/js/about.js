/* Page 04 : À propos. Méthode, sources (références bibliographiques, identiques dans les trois langues),
   crédits et licences. Les textes viennent des dictionnaires (clé « about »). */
(function () {
  "use strict";

  const { el } = Core;
  const t = I18n.t;

  /** Références des données : celles de final_panel.ipynb (section 12), plus Archigos (Crossref), REIGN
      (citation proposée par ses auteurs), les sources du test des caractéristiques des pays (04_demographics.ipynb),
      celles du test des chocs (05_shocks.ipynb) et LEAD (06_party_leaders.ipynb). */
  const SOURCES = [
    ["arpd", "Miller, M. K. (2020). The Autocratic Ruling Parties Dataset: Origins, Durability, and Death. Journal of Conflict Resolution, 64(4), 756–782.",
     "https://doi.org/10.1177/0022002719876000"],
    ["vdem", "Coppedge, M., Gerring, J., Knutsen, C. H., Lindberg, S. I., Teorell, J., et al. (2026). V-Dem Country-Year Dataset v16. Varieties of Democracy (V-Dem) Project.",
     "https://doi.org/10.23696/vdemds26"],
    ["polity", "Marshall, M. G., & Gurr, T. R. (2020). Polity5: Political Regime Characteristics and Transitions, 1800–2018. Center for Systemic Peace.", null],
    ["archigos", "Goemans, H. E., Gleditsch, K. S., & Chiozza, G. (2009). Introducing Archigos: A Dataset of Political Leaders. Journal of Peace Research, 46(2), 269–283.",
     "https://doi.org/10.1177/0022343308100719"],
    ["reign", "Bell, C., Besaw, C., & Frank, M. (2021). The Rulers, Elections, and Irregular Governance (REIGN) Dataset. Broomfield, CO: One Earth Future.",
     "https://oefdatascience.github.io/REIGN.github.io/"],
    ["ucdp", "Gleditsch, N. P., Wallensteen, P., Eriksson, M., Sollenberg, M., & Strand, H. (2002). Armed Conflict 1946–2001: A New Dataset. Journal of Peace Research, 39(5), 615–637; Davies, S., Pettersson, T., & Öberg, M. (2026). Organized violence 1989–2025, and violent political protests. Journal of Peace Research, 63(4), 705–723.",
     "https://doi.org/10.1177/0022343302039005007"],
    ["maddison", "Bolt, J., & van Zanden, J. L. (2024). Maddison-style estimates of the evolution of the world economy: A new 2023 update. Journal of Economic Surveys, 39(2), 631–671. Data: Maddison Project Database 2023.",
     "https://doi.org/10.34894/INZBF2"],
    ["naturalearth", "Natural Earth. Admin 0 – Countries, 1:50m, version 5.", "https://www.naturalearthdata.com/"],
    // Test des caractéristiques des pays (notebooks/04_demographics.ipynb)
    ["wpp", "United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024.",
     "https://population.un.org/wpp/"],
    ["wdi", "World Bank (2026). World Development Indicators. Unemployment: International Labour Organization, ILO modelled estimates (ILOSTAT).",
     "https://data.worldbank.org/"],
    ["epr", "Vogt, M., Bormann, N.-C., Rüegger, S., Cederman, L.-E., Hunziker, P., & Girardin, L. (2015). Integrating Data on Ethnicity, Geography, and Conflict: The Ethnic Power Relations Data Set Family. Journal of Conflict Resolution, 59(7), 1327–1342.",
     "https://doi.org/10.1177/0022002715591215"],
    ["qog", "Alesina, A., Devleeschauwer, A., Easterly, W., Kurlat, S., & Wacziarg, R. (2003). Fractionalization. Journal of Economic Growth, 8(2), 155–194; data from Teorell, J., et al. (2026). The Quality of Government Standard Dataset, version Jan26.",
     "https://doi.org/10.18157/qogstdjan26"],
    ["clio", "Clio-Infra (2018). Average Years of Education. Clio-Infra Project (Database), via V-Dem v16.", "https://clio-infra.eu/"],
    ["afi", "Spannagel, J., & Kinzelbach, K. (2022). The Academic Freedom Index and its indicators: Introduction to new global time-series V-Dem data. Quality & Quantity.",
     null],
    // Test des chocs (notebooks/05_shocks.ipynb) ; UCDP et Maddison sont cités plus haut
    ["emdat", "Delforge, D., et al. (2025). EM-DAT: the Emergency Events Database. International Journal of Disaster Risk Reduction. Data: CRED / UCLouvain, EM-DAT archive v2 (2026).",
     "https://doi.org/10.14428/DVN/I0LTPH"],
    ["noaa", "NOAA National Centers for Environmental Information (2026). NCEI/WDS Global Significant Earthquake Database.",
     "https://doi.org/10.7289/V5TD9V7K"],
    ["prio", "Lacina, B., & Gleditsch, N. P. (2005). Monitoring Trends in Global Combat: A New Dataset of Battle Deaths. European Journal of Population, 21(2–3), 145–166. Data: PRIO Battle Deaths Dataset v3.1.",
     "https://www.prio.org/data/1"],
    ["famine", "World Peace Foundation (2025). Historic Famines (WPF Famine Dataset), processed by Our World in Data.",
     "https://ourworldindata.org/famines"],
    ["faostat", "FAO (2026). FAOSTAT: Production Indices. Food and Agriculture Organization of the United Nations.",
     "https://www.fao.org/faostat/"],
    // Test du parti et de son dirigeant (notebooks/06_party_leaders.ipynb) ; Archigos est cité plus haut
    ["lead", "Ellis, C. M., Horowitz, M. C., & Stam, A. C. (2015). Introducing the LEAD Data Set. International Interactions, 41(4), 718–741. Data: LEAD v1, via Miller, S. V. (2022), peacesciencer: An R Package for Quantitative Peace Science Research, Conflict Management and Peace Science, 39(6), 755–779.",
     "https://doi.org/10.1080/03050629.2015.1016157"],
    // Fiche pays de l'Atlas (frontend/build_media.py)
    ["wikidata", "Wikidata. Flags (P41, P163), party logos (P154), people and portraits (P18), links to Wikipedia.",
     "https://www.wikidata.org/"],
    ["commons", "Wikimedia Commons. Image files of the flags, logos and portraits, each under its own licence.",
     "https://commons.wikimedia.org/"],
    ["wikipedia", "Wikipedia (French, English and Arabic editions). First sentences of the articles on the parties and the rulers.",
     "https://www.wikipedia.org/"],
  ];
  /** Bibliothèques, polices et licences (licences lues dans les fichiers ou sur les sites des projets). */
  const CREDITS = [
    ["globe", "globe.gl 2.46.2 — © Vasco Asturiano", "MIT", "https://github.com/vasturiano/globe.gl"],
    ["three", "three.js — © three.js authors", "MIT", "https://threejs.org/"],
    ["naturalearth", "Natural Earth", null, "https://www.naturalearthdata.com/about/terms-of-use/"],
    ["vdem", "V-Dem v16", "CC BY-SA 4.0", "https://v-dem.net/data/the-v-dem-dataset/"],
    ["wikidata", "Wikidata", "CC0 1.0", "https://www.wikidata.org/wiki/Wikidata:Licensing"],
    ["commons", "Wikimedia Commons", "per-file", "https://commons.wikimedia.org/wiki/Commons:Licensing"],
    ["wikipedia", "Wikipedia", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"],
    ["fonts", "Cormorant Garamond · Inter · JetBrains Mono · Amiri · IBM Plex Sans Arabic", "SIL Open Font License 1.1",
     "https://fonts.google.com/"],
  ];

  function render() {
    const method = document.getElementById("method");
    method.innerHTML = "";
    (I18n.get("about.method") || []).forEach((line) => method.appendChild(el("li", { text: line })));

    const sources = document.getElementById("sources");
    sources.innerHTML = "";
    SOURCES.forEach(([key, citation, url]) => {
      sources.appendChild(el("li", {}, [
        el("span", { class: "role", text: t(`about.sources.${key}`) }),
        el("bdi", { class: "citation", dir: "ltr", text: citation }),
        url ? el("a", { href: url, rel: "noopener", dir: "ltr", text: url.replace(/^https:\/\//, "") }) : null,
      ]));
    });

    const credits = document.getElementById("credits");
    credits.innerHTML = "";
    CREDITS.forEach(([key, name, licence, url]) => {
      credits.appendChild(el("li", {}, [
        el("bdi", { class: "name", dir: "ltr", text: name }),
        el("span", { class: "licence", text: licence === "per-file" ? t("about.licencePerFile")
          : licence ? `${t("about.licence")}${t("common.colon")}${licence}` : t("about.publicDomain") }),
        el("span", { class: "what", text: t(`about.credits.${key}`) }),
        el("a", { href: url, rel: "noopener", dir: "ltr", text: url.replace(/^https:\/\//, "") }),
      ]));
    });

    document.getElementById("built").textContent = t("about.built", { date: window.SITE.stats.built });
  }

  render();
  I18n.onChange(render);
  window.__ready = true;
})();
