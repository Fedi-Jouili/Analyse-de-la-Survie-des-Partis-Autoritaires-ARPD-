/* Langues du site : français, anglais, arabe.
   Dictionnaires : assets/i18n/{fr,en,ar}.js (window.I18N_DICT). Chargé dans <head>, avant tout le reste.
   Langue = paramètre ?lang= (ou lang= dans le #), sinon choix enregistré, sinon langue du navigateur, sinon français.
   Nombres : mêmes conventions que src/site_text.py. En arabe, chiffres latins ; les nombres et les formules sont
   isolés (LRI … PDI) pour se lire de gauche à droite dans le texte de droite à gauche. */
(function () {
  "use strict";

  const LANGS = ["fr", "en", "ar"];
  const NAMES = { fr: "FR", en: "EN", ar: "العربية" };
  const LOCALES = { fr: "fr-FR", en: "en-GB", ar: "ar" };
  const STORE_KEY = "observatoire-langue";
  const LRI = "⁦", PDI = "⁩", NNBSP = " ", MINUS = "−";
  const DICTS = window.I18N_DICT || {};

  function detect() {
    const fromQuery = new URLSearchParams(location.search).get("lang");
    if (LANGS.includes(fromQuery)) return fromQuery;
    const fromHash = new URLSearchParams(location.hash.slice(1)).get("lang");
    if (LANGS.includes(fromHash)) return fromHash;
    try {
      const saved = localStorage.getItem(STORE_KEY);
      if (LANGS.includes(saved)) return saved;
    } catch (e) { /* stockage indisponible (fichier local, navigation privée) */ }
    for (const l of navigator.languages || [navigator.language || ""]) {
      const code = String(l).slice(0, 2).toLowerCase();
      if (LANGS.includes(code)) return code;
    }
    return "fr";
  }

  let lang = detect();
  const listeners = [];
  const pluralCache = {};
  const plural = () => (pluralCache[lang] = pluralCache[lang] || new Intl.PluralRules(LOCALES[lang]));

  // Typographie française : espace fine insécable avant ? ! ; : » et après « (avec une espace ordinaire, le signe
  // peut passer seul à la ligne). Les fichiers gardent des espaces ordinaires ; le dictionnaire français est corrigé
  // une seule fois, au chargement (le faire à chaque appel ralentirait l'Atlas, qui lit des milliers de libellés).
  function frenchSpaces(text) {
    return text.replace(/ ([?!;:»])/g, NNBSP + "$1").replace(/« /g, "«" + NNBSP);
  }
  function frenchTypography(v) {
    if (typeof v === "string") return frenchSpaces(v);
    if (Array.isArray(v)) return v.map(frenchTypography);
    if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, frenchTypography(x)]));
    return v;
  }
  const SHOWN = Object.assign({}, DICTS, { fr: frenchTypography(DICTS.fr) });

  function lookup(key, l) {
    return key.split(".").reduce((o, k) => (o && typeof o === "object" ? o[k] : undefined), SHOWN[l]);
  }
  const PLURAL_KEYS = ["zero", "one", "two", "few", "many", "other"];
  const isPlural = (v) => v && typeof v === "object" && !Array.isArray(v) && "other" in v &&
    Object.keys(v).every((k) => PLURAL_KEYS.includes(k));

  function resolve(key, params) {
    let v = lookup(key, lang);
    if (v === undefined) v = lookup(key, "fr");
    if (v === undefined) {
      console.warn(`i18n : clé absente « ${key} »`);
      return key;
    }
    if (isPlural(v)) {
      const n = Number(params.count);
      v = v[plural().select(n)] !== undefined ? v[plural().select(n)] : v.other;
    }
    return v;
  }

  // ------------------------------------------------------------------ nombres
  function raw(value, digits = 0) {
    const rounded = Number(Number(value).toFixed(digits));
    const [int, frac] = Math.abs(rounded).toFixed(digits).split(".");
    const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, lang === "fr" ? NNBSP : ",");
    const text = frac ? grouped + (lang === "fr" ? "," : ".") + frac : grouped;
    return (rounded < 0 ? MINUS : "") + text;
  }
  const bad = (v) => v === null || v === undefined || Number.isNaN(Number(v));
  // Îlot de gauche à droite en arabe ; ses espaces sont insécables pour qu'une formule ne soit jamais coupée
  const iso = (text) => (lang === "ar" ? LRI + String(text).replace(/ /g, " ") + PDI : String(text));

  // Paramètres insérés dans un texte français (le dictionnaire, lui, est déjà corrigé)
  const typo = (s) => (lang === "fr" && typeof s === "string" ? frenchSpaces(s) : s);

  const I18n = {
    LANGS,
    get lang() { return lang; },
    get dir() { return lang === "ar" ? "rtl" : "ltr"; },
    get locale() { return LOCALES[lang]; },

    /** Texte d'une clé ; {count} est formaté et choisit la forme du pluriel. */
    t(key, params = {}) {
      const v = resolve(key, params);
      if (typeof v !== "string") return v;
      return typo(fill(v, params));
    },
    /** Liste de textes d'une clé (tableau du dictionnaire), chacun complété par les mêmes paramètres. */
    tList(key, params = {}) {
      const v = I18n.get(key);
      return Array.isArray(v) ? v.map((s) => typo(fill(String(s), params))) : [];
    },
    /** Même chose pour un gabarit HTML du dictionnaire : les paramètres sont échappés (sauf I18n.html(...)). */
    tHtml(key, params = {}) {
      const v = resolve(key, params);
      return typo(String(v).replace(/\{(\w+)\}/g, (m, k) => {
        if (!(k in params)) return m;
        const p = params[k];
        if (p && typeof p === "object" && "__html" in p) return p.__html;
        return escapeHtml(k === "count" ? I18n.n(p) : String(p));
      }));
    },
    html(text) { return { __html: text }; },
    has(key) { return lookup(key, lang) !== undefined; },
    /** Valeur brute du dictionnaire (objet ou liste). */
    get(key) { const v = lookup(key, lang); return v === undefined ? lookup(key, "fr") : v; },
    /** Typographie française d'un texte (ou de toutes les chaînes d'un objet), quelle que soit la langue affichée :
        sert aux textes générés en français (frontend/data/stats.js). */
    frenchTypography,

    raw,
    iso,
    n(value, digits = 0) { return bad(value) ? "—" : iso(raw(value, digits)); },
    pct(value, digits = 0) {
      if (bad(value)) return "—";
      const text = raw(value, digits);
      return lang === "fr" ? `${text}${NNBSP}%` : iso(`${text}%`);
    },
    signed(value, digits = 0) {
      if (bad(value)) return "—";
      const text = raw(value, digits);
      return iso(text.startsWith(MINUS) || Number(text.replace(/[^\d]/g, "")) === 0 ? text : "+" + text);
    },
    /** Étiquette de texte dans un graphique (SVG de gauche à droite) : en arabe, isolée de droite à gauche
        pour que « 10 سنوات » ne se lise pas à l'envers. */
    svgLabel(text) { return lang === "ar" ? `⁧${text}⁩` : String(text); },
    times(value, digits = 2) { return bad(value) ? "—" : iso("×" + raw(value, digits)); },
    /** Intervalle « a–b » lu de gauche à droite (nombres déjà formatés ou années). */
    range(a, b) { return iso(`${a}–${b}`); },
    rangeN(a, b, digits = 0) { return iso(`${bad(a) ? "—" : raw(a, digits)}–${bad(b) ? "—" : raw(b, digits)}`); },
    pval(p) {
      if (bad(p)) return "—";
      return iso(p < 0.001 ? `p < ${raw(0.001, 3)}` : `p = ${raw(p, 3)}`);
    },
    /** Nombre ordinal d'une année au pouvoir (1re, 2nd, الـ3). */
    ordinal(n) {
      if (lang === "fr") return n === 1 ? "1re" : `${n}e`;
      if (lang === "ar") return `الـ${n}`;
      const s = ["th", "st", "nd", "rd"], v = n % 100;
      return n + (s[(v - 20) % 10] || s[v] || s[0]);
    },
    /** Liste « a, b et c » dans la langue du site. */
    list(items) {
      items = items.filter(Boolean);
      if (items.length <= 1) return items.join("");
      if (lang === "ar") return items[0] + items.slice(1).map((x) => "، و" + x).join("");
      return items.slice(0, -1).join(", ") + (lang === "fr" ? " et " : " and ") + items[items.length - 1];
    },
    compare(a, b) { return String(a).localeCompare(String(b), LOCALES[lang]); },
    cap(text) { return lang === "ar" || !text ? text : text.charAt(0).toUpperCase() + text.slice(1); },

    /** Lien interne qui garde la langue : href("simulation.html#o=Communist"). */
    href(path) {
      const [base, hash] = path.split("#");
      const [file, query] = base.split("?");
      const q = new URLSearchParams(query || "");
      q.set("lang", lang);
      return `${file}?${q.toString()}${hash !== undefined ? "#" + hash : ""}`;
    },

    set(next) {
      if (!LANGS.includes(next) || next === lang) return;
      lang = next;
      try { localStorage.setItem(STORE_KEY, lang); } catch (e) { /* sans stockage, la langue tient dans l'URL */ }
      try {
        const url = new URL(location.href);
        url.searchParams.set("lang", lang);
        history.replaceState(history.state, "", url);
      } catch (e) { /* history.replaceState refusé sur file:// */ }
      I18n.apply(document);
      listeners.forEach((fn) => { try { fn(lang); } catch (err) { console.error(err); } });
    },
    onChange(fn) { listeners.push(fn); },

    /** Traduit les éléments statiques : data-i18n (texte), data-i18n-html, data-i18n-attr="attr:clé;attr:clé". */
    apply(root) {
      const html = document.documentElement;
      html.lang = lang;
      html.dir = I18n.dir;
      root.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = I18n.t(node.dataset.i18n); });
      root.querySelectorAll("[data-i18n-html]").forEach((node) => { node.innerHTML = I18n.t(node.dataset.i18nHtml); });
      root.querySelectorAll("[data-i18n-attr]").forEach((node) => {
        node.dataset.i18nAttr.split(";").forEach((pair) => {
          const [attr, key] = pair.split(":").map((s) => s.trim());
          if (attr && key) node.setAttribute(attr, I18n.t(key));
        });
      });
      root.querySelectorAll("a[data-nav]").forEach((a) => { a.href = I18n.href(a.dataset.nav); });
      const sw = document.getElementById("lang-switch");
      if (sw) {
        sw.setAttribute("aria-label", I18n.t("common.language"));
        sw.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
      }
    },

    /** Sélecteur de langue dans la barre de commande. */
    mountSwitcher() {
      const sw = document.getElementById("lang-switch");
      if (!sw || sw.childElementCount) return;
      LANGS.forEach((l) => {
        const b = document.createElement("button");
        b.type = "button";
        b.dataset.lang = l;
        b.lang = l;
        if (l === "ar") b.dir = "rtl";
        b.textContent = NAMES[l];
        b.setAttribute("aria-pressed", String(l === lang));
        b.addEventListener("click", () => I18n.set(l));
        sw.appendChild(b);
      });
    },
  };

  function fill(text, params) {
    return text.replace(/\{(\w+)\}/g, (m, k) => (k in params ? (k === "count" ? I18n.n(params[k]) : String(params[k])) : m));
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // Langue et sens d'écriture posés avant le rendu du corps de la page
  document.documentElement.lang = lang;
  document.documentElement.dir = I18n.dir;
  document.addEventListener("DOMContentLoaded", () => {
    I18n.mountSwitcher();
    I18n.apply(document);
  });
  window.I18n = I18n;
})();
