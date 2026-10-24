/* Page 01 : Atlas. Globe 3D des régimes, curseur temporel, dossier pays, vue en liste. */
(function () {
  "use strict";

  const { el, svg, escape } = Core;
  const t = I18n.t;
  const A = window.SITE.atlas;
  const GEO = window.SITE.countries;
  const Y0 = A.years[0], Y1 = A.years[1];
  const CAT = A.categories;
  const FEATURES = GEO.features;
  const FEAT = Object.fromEntries(FEATURES.map((f) => [f.id, f]));
  const AUTOCRATIC = new Set(["party", "military", "monarchy", "other_arpd", "other_vdem"]);
  const HEX = Labels.HEX;
  const LEGEND_OF = {};
  Labels.LEGEND.forEach((g) => g.cats.forEach((c) => { LEGEND_OF[c] = g.key; }));

  const state = {
    year: 1975, mode: "type", relief: false, selected: null, hovered: null, view: "globe",
    playing: false, timer: null, hidden: new Set(), pointer: { x: 0, y: 0 },
    sort: { key: "type", dir: 1 },
  };

  // ------------------------------------------------------------------ accès aux données
  /** Nom dans la langue du site ({fr, en, ar}). */
  const nm = (names) => (names ? names[I18n.lang] || names.fr : "");
  const row = (pid, year) => A.polygons[pid].rows[year - Y0];
  const catOf = (r) => CAT[r[0]];
  const spellOf = (r) => (r && r[1] >= 0 ? A.spells[r[1]] : null);
  const labelOf = (r) => nm(A.labels[r[5]]);
  const polyName = (pid) => nm(FEAT[pid].properties.name);
  const ageOf = (r, year) => { const s = spellOf(r); return s ? year - s.start + 1 : 0; };
  const years = (n) => t("units.years", { count: n });

  // ------------------------------------------------------------------ images et extraits Wikipédia
  // Images de Wikimedia Commons (drapeaux, logos, portraits) : [chemin, forme, hôte, licence, auteur] ;
  // personnes : [élément Wikidata, image, {langue : titre Wikipédia}] (frontend/build_media.py). Les images sont
  // chargées depuis les serveurs de Wikimedia à l'ouverture d'une fiche ; hors ligne, elles sont simplement masquées.
  const IMAGES = A.images || [], PEOPLE = A.people || [], HOSTS = A.image_hosts || [];
  const THUMB = A.image_width || 120;
  /** Adresse de l'image (règle inverse de compact_image dans build_data.py) : 0 original, 1 vignette, 2 vignette PNG
      d'un SVG, 3 adresse complète. */
  function thumbUrl(i) {
    const [path, kind, host] = IMAGES[i];
    if (kind === 0 || kind === 3) return HOSTS[host] + path;
    const name = path.slice(path.lastIndexOf("/") + 1);
    return `${HOSTS[host]}thumb/${path}/${THUMB}px-${name}${kind === 2 ? ".png" : ""}`;
  }
  /** Nom du fichier sur Commons (pour le lien vers sa page, qui donne l'auteur et la licence complète). */
  function fileName(i) {
    const parts = IMAGES[i][0].split("/");
    return parts[0] === "thumb" ? parts[3] : parts[parts.length - 1];
  }
  const filePage = (i) => "https://commons.wikimedia.org/wiki/File:" + fileName(i);
  const imageCredit = (i) => [IMAGES[i][4], IMAGES[i][3]].filter(Boolean).join(" · ");
  /** Crédit d'un portrait ; en français, « de » s'élide devant une voyelle : « Portrait d'Augusto Pinochet ». */
  function portraitCredit(name) {
    const text = t("atlas.media.creditPortrait", { name });
    const vowel = "AEIOU".includes(name.normalize("NFD").charAt(0).toUpperCase());
    return I18n.lang === "fr" && vowel ? text.replace(`de ${name}`, `d'${name}`) : text;
  }
  /** Image de Commons ; si elle ne se charge pas (hors ligne), elle est masquée et onFail est appelé. */
  function picture(i, cls, alt, onFail) {
    if (i === undefined || i === null || i < 0) return null;
    return el("img", { class: cls, src: thumbUrl(i), alt, title: imageCredit(i), loading: "lazy", decoding: "async",
                       referrerpolicy: "no-referrer", onerror: (e) => { e.target.hidden = true; if (onFail) onFail(e.target); } });
  }
  /** Image principale manquante : la figure disparaît et le paragraphe reprend toute la largeur. */
  const dropFigure = (img) => {
    const fig = img.closest("figure");
    if (fig) { fig.hidden = true; fig.parentElement.classList.add("no-figure"); }
  };
  /** Article et logo du parti pour une année (un parti renommé peut avoir un article par nom). */
  const partyItem = (s, year) => (s && s.media
    ? s.media.find(([a, b]) => (a === null || a <= year) && (b === null || b >= year)) || null : null);
  /** Dirigeant principal (V-Dem) : le chef du gouvernement s'il a plus de pouvoir sur le gouvernement que le chef de
      l'État (v2ex_hosw), sinon le chef de l'État. */
  function mainLeader(r) {
    if (r[4] < 0) return null;
    const L = A.leaders[r[4]];
    const hog = L[4] === 1 && L[2];
    return { name: hog ? L[2] : L[0], title: hog ? L[3] : L[1], person: hog ? L[6] : L[5] };
  }
  /** Article Wikipédia de la fiche : celui du parti au pouvoir ; sinon, dans une autocratie, celui du dirigeant
      principal ; rien pour une démocratie. Seulement dans la langue de la page. */
  function wikiTitle(r, year) {
    const s = spellOf(r);
    let titles = null;
    if (s && s.party) titles = (partyItem(s, year) || [])[5] || null;
    else if (AUTOCRATIC.has(catOf(r))) {
      const m = mainLeader(r);
      titles = m && m.person >= 0 ? PEOPLE[m.person][2] : null;
    }
    return titles ? titles[I18n.lang] || null : null;
  }
  const wikiLoads = {};
  /** Extraits Wikipédia d'une langue (data/wiki_{lang}.js), chargés à la première fiche ouverte dans cette langue. */
  function wikiTexts(lang) {
    if (!wikiLoads[lang]) {
      wikiLoads[lang] = new Promise((resolve) => {
        const done = () => resolve(window.SITE[`wiki_${lang}`] || {});
        if (window.SITE[`wiki_${lang}`]) { done(); return; }
        const s = document.createElement("script");
        s.src = `data/wiki_${lang}.js`;
        s.onload = done;
        s.onerror = () => resolve({});
        document.head.appendChild(s);
      });
    }
    return wikiLoads[lang];
  }

  // ------------------------------------------------------------------ couleurs
  function hexToRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
  function rgbToHex([r, g, b]) { return "#" + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, "0")).join(""); }
  function mix(a, b, k) { const x = hexToRgb(a), y = hexToRgb(b); return rgbToHex(x.map((v, i) => v + (y[i] - v) * k)); }
  function rampColor(stops, value) {
    if (value <= stops[0][0]) return stops[0][1];
    for (let i = 1; i < stops.length; i++) {
      if (value <= stops[i][0]) {
        const [v0, c0] = stops[i - 1], [v1, c1] = stops[i];
        return mix(c0, c1, (value - v0) / (v1 - v0));
      }
    }
    return stops[stops.length - 1][1];
  }
  // Longévité : une teinte (ambre), du sombre au clair ; démocratie : une teinte (bleu), du sombre au clair
  const AGE_STOPS = [[1, "#2b2414"], [5, "#5c4714"], [10, "#8d6511"], [20, "#c98500"], [40, "#efb64a"], [60, "#ffe2a8"]];
  const VDEM_STOPS = [[0, "#101a2a"], [0.25, "#1c3a63"], [0.5, "#2a5f9e"], [0.75, "#5f9be0"], [1, "#b9dbff"]];

  function baseColor(pid) {
    const r = row(pid, state.year);
    const cat = catOf(r);
    if (state.mode === "type") {
      if (state.hidden.has(LEGEND_OF[cat])) return mix(HEX[cat], HEX.nodata, 0.82);
      return HEX[cat];
    }
    if (state.mode === "age") {
      if (r[1] >= 0) return rampColor(AGE_STOPS, ageOf(r, state.year));
      if (cat === "other_vdem") return "#1e2126";
      if (cat === "democracy") return "#151c26";
      return HEX[cat];
    }
    return r[3] >= 0 ? rampColor(VDEM_STOPS, r[3] / 1000) : HEX[cat === "dependent" ? "dependent" : "nodata"];
  }
  function capColor(f) {
    let c = baseColor(f.id);
    if (f.id === state.selected) c = mix(c, "#ffffff", 0.28);
    else if (f.id === state.hovered) c = mix(c, "#ffffff", 0.16);
    return c;
  }
  // Parois visibles seulement en mode relief : à plat, elles ne servent à rien et peuvent transparaître
  const sideColor = (f) => (state.relief ? mix(baseColor(f.id), "#000000", 0.45) : "rgba(0,0,0,0)");
  const strokeColor = (f) => (f.id === state.selected ? "#e9edf2" : f.id === state.hovered ? "rgba(233,237,242,0.6)" : "rgba(160,180,205,0.16)");
  function altitude(f) {
    const r = row(f.id, state.year);
    let a = 0.01;
    if (state.relief && AUTOCRATIC.has(catOf(r)) && r[1] >= 0) a += Math.min(ageOf(r, state.year), 70) / 70 * 0.07;
    if (f.id === state.selected) a += 0.012;
    else if (f.id === state.hovered) a += 0.006;
    return a;
  }

  // ------------------------------------------------------------------ géométrie
  function centroid(f) {
    const g = f.geometry;
    const polys = g.type === "Polygon" ? [g.coordinates] : g.coordinates;
    let best = null, bestA = 0;
    for (const p of polys) {
      const ring = p[0];
      let a = 0, cx = 0, cy = 0;
      for (let i = 0; i < ring.length; i++) {
        const [x0, y0] = ring[i], [x1, y1] = ring[(i + 1) % ring.length];
        const c = x0 * y1 - x1 * y0;
        a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c;
      }
      a /= 2;
      if (Math.abs(a) > bestA) { bestA = Math.abs(a); best = { lng: cx / (6 * a), lat: cy / (6 * a), area: bestA }; }
    }
    return best || { lng: 0, lat: 0, area: 0 };
  }
  const CENTER = Object.fromEntries(FEATURES.map((f) => [f.id, centroid(f)]));

  // ------------------------------------------------------------------ statistiques annuelles
  /** États (et non polygones) d'une année : un territoire d'union compte avec son État ; les États
      historiques sans polygone propre (RDA, Viêt Nam du Sud…) comptent à part. */
  function statesOfYear(year) {
    const states = new Map();
    for (const pid of Object.keys(A.polygons)) {
      const r = row(pid, year);
      const cat = catOf(r);
      if (cat === "nodata") continue;
      const key = "l" + r[5];
      if (!states.has(key) || r[6] === 0) states.set(key, { cat, pid, spell: r[1], names: A.labels[r[5]] });
      for (const sec of A.polygons[pid].secondary) {
        const sr = year >= sec.first && year <= sec.last ? sec.rows[year - sec.first] : null;
        if (sr) states.set("s" + sec.label.fr, { cat: CAT[sr[0]], pid, spell: sr[1], names: sec.label });
      }
    }
    return [...states.values()];
  }
  const YEARS = Array.from({ length: Y1 - Y0 + 1 }, (_, i) => Y0 + i);
  const COUNTS = YEARS.map((y) => {
    const c = {};
    for (const s of statesOfYear(y)) { const k = LEGEND_OF[s.cat]; c[k] = (c[k] || 0) + 1; }
    return c;
  });
  const autocraciesIn = (counts) => ["party", "military", "monarchy", "other_arpd"].reduce((s, k) => s + (counts[k] || 0), 0);

  // ------------------------------------------------------------------ globe
  // Le globe est créé après le premier rendu des panneaux et de la ligne du temps : la page n'est jamais vide.
  // Sans WebGL, la vue Liste s'ouvre d'elle-même et toute la page reste utilisable.
  const container = document.getElementById("globe");
  const loading = document.getElementById("globe-loading");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const MAX_PIXEL_RATIO = 1.5;     // plafond de résolution du rendu sur les écrans à haute densité
  const MIN_FPS = 30;              // sous ce rythme au démarrage, le rendu passe à 1 pixel par pixel CSS
  let globe = null, controls = null, HIDDEN_SIDE = null;
  state.render = { webgl: null, pixelRatio: null, fps: null };

  /** WebGL disponible ? Le contexte d'essai est libéré aussitôt (les navigateurs limitent le nombre de contextes). */
  function webglAvailable() {
    try {
      if (!window.WebGLRenderingContext) return false;
      const c = document.createElement("canvas");
      const gl = c.getContext("webgl2") || c.getContext("webgl");
      const lose = gl && gl.getExtension("WEBGL_lose_context");
      if (lose) lose.loseContext();
      return Boolean(gl);
    } catch (e) {
      return false;
    }
  }

  function initGlobe() {
    if (typeof Globe !== "function" || !webglAvailable()) { noGlobe(); return; }
    try {
      globe = new Globe(container, { rendererConfig: { antialias: true, alpha: true }, animateIn: !reduceMotion });
    } catch (err) {
      console.warn(err);
      globe = null;
      noGlobe();
      return;
    }
    globe
      .backgroundColor("rgba(0,0,0,0)")
      .width(container.clientWidth).height(container.clientHeight)
      .showAtmosphere(true).atmosphereColor("#8fb4e6").atmosphereAltitude(0.17)
      .showGraticules(true)
      .polygonsData(FEATURES)
      .polygonCapCurvatureResolution(2)
      .polygonsTransitionDuration(reduceMotion ? 0 : 520)
      .ringLat((d) => d.lat).ringLng((d) => d.lng)
      .ringColor((d) => (k) => `rgba(${d.rgb},${Math.max(0, 1 - k)})`)
      .ringMaxRadius((d) => d.r).ringPropagationSpeed((d) => d.speed).ringRepeatPeriod((d) => d.period)
      .onPolygonHover(onHover)
      .onPolygonClick((f) => select(f ? f.id : null, { fly: false }))
      .onGlobeReady(() => { loading.classList.add("done"); window.__globeReady = true; probeFrameRate(); });
    const material = globe.globeMaterial();
    material.color.set("#07101a");
    if (material.emissive) material.emissive.set("#03070d");
    material.shininess = 6;
    // À plat, les parois des polygones sont invisibles : un matériau « visible: false » évite que three.js trie et
    // mélange à chaque image ~240 parois transparentes (gain mesuré : 12 → 25 images/s environ sur un GPU intégré)
    HIDDEN_SIDE = new material.constructor({ visible: false });
    setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO));
    globe.pointOfView(state.selected ? viewOf(state.selected) : { lat: 28, lng: 18, altitude: 2.35 });
    controls = globe.controls();
    controls.autoRotate = rotateToggle.checked;
    controls.autoRotateSpeed = 0.32;
    controls.enableDamping = true;
    controls.minDistance = 130;
    controls.maxDistance = 520;
    state.render.webgl = true;
    repaint();
  }

  /** Résolution du rendu (pixels de rendu par pixel CSS), appliquée au moteur et à sa chaîne de rendu. */
  function setPixelRatio(ratio) {
    globe.renderer().setPixelRatio(ratio);
    const composer = globe.postProcessingComposer && globe.postProcessingComposer();
    if (composer && composer.setPixelRatio) composer.setPixelRatio(ratio);
    state.render.pixelRatio = ratio;
  }

  /** Rythme d'affichage pendant les premières secondes (après l'animation d'arrivée) : sous MIN_FPS images par seconde,
      le rendu passe à 1 pixel par pixel CSS, soit jusqu'à 2,25 fois moins de pixels à dessiner à un ratio de 1,5. */
  function probeFrameRate() {
    let frames = 0, t0 = null;
    const step = (now) => {
      if (document.visibilityState !== "visible") { setTimeout(probeFrameRate, 1000); return; }   // onglet caché : plus tard
      if (t0 === null) t0 = now;
      frames += 1;
      if (now - t0 < 2000) { requestAnimationFrame(step); return; }
      state.render.fps = Math.round(((frames - 1) / ((now - t0) / 1000)) * 10) / 10;
      if (state.render.fps < MIN_FPS && state.render.pixelRatio > 1) setPixelRatio(1);
    };
    setTimeout(() => requestAnimationFrame(step), 1000);
  }

  /** Sans WebGL : message, vue Liste ouverte d'office, commandes du globe désactivées. */
  function noGlobe() {
    state.render.webgl = false;
    document.body.classList.add("no-globe");
    loading.hidden = true;
    const globeButton = document.querySelector('#view-seg button[data-view="globe"]');
    globeButton.disabled = true;
    globeButton.setAttribute("aria-disabled", "true");
    document.getElementById("list-note").hidden = false;
    setView("list");
  }

  function repaint() {
    if (!globe) return;
    globe
      .polygonCapColor((f) => capColor(f))
      .polygonSideMaterial(() => (state.relief ? null : HIDDEN_SIDE))
      .polygonSideColor((f) => sideColor(f))
      .polygonStrokeColor((f) => strokeColor(f))
      .polygonAltitude((f) => altitude(f));
  }

  window.addEventListener("resize", () => { if (globe) globe.width(container.clientWidth).height(container.clientHeight); });
  // Sur ordinateur, le globe s'arrête au-dessus de la ligne du temps (--globe-bottom) : sa taille suit son conteneur
  if (window.ResizeObserver) {
    new ResizeObserver(() => { if (globe) globe.width(container.clientWidth).height(container.clientHeight); }).observe(container);
  }
  container.addEventListener("pointermove", (e) => {
    state.pointer = { x: e.clientX, y: e.clientY };
    if (state.hovered) showTooltip(state.hovered);
  });
  container.addEventListener("pointerleave", () => Core.tooltip.hide());

  function onHover(f) {
    const id = f ? f.id : null;
    if (id === state.hovered) return;
    state.hovered = id;
    container.style.cursor = id ? "pointer" : "";
    repaint();
    if (id) showTooltip(id); else Core.tooltip.hide();
  }
  function showTooltip(pid) {
    const r = row(pid, state.year);
    const cat = catOf(r);
    const name = polyName(pid);
    const lab = labelOf(r);
    const s = spellOf(r);
    let detail = Labels.cat(cat);
    if (s) detail += " · " + t("atlas.inPower", { years: years(ageOf(r, state.year)) });
    Core.tooltip.show(
      `<div class="t-head">${escape(lab !== name ? `${name} · ${lab}` : name)} · ${state.year}</div>` +
      `<span class="swatch" style="background:${HEX[cat]};margin-inline-end:8px"></span>${escape(detail)}`,
      state.pointer.x, state.pointer.y);
  }

  function viewOf(pid) {
    const c = CENTER[pid];
    return { lat: c.lat, lng: c.lng, altitude: Math.max(0.9, Math.min(2.0, 0.75 + Math.sqrt(c.area) / 30)) };
  }
  function flyTo(pid) {
    if (!globe) return;                  // globe pas encore créé : il s'ouvrira sur ce pays
    globe.pointOfView(viewOf(pid), reduceMotion ? 0 : 1100);
  }

  /** Anneaux sur les pays où un régime arrive ou tombe dans l'année (aucun si l'utilisateur limite les animations). */
  function emitRings(year) {
    if (!globe || reduceMotion) return;
    const rings = [];
    for (const s of A.spells) {
      if (!s.poly || !CENTER[s.poly]) continue;
      const c = CENTER[s.poly];
      if (s.start === year) rings.push({ lat: c.lat, lng: c.lng, rgb: "233,237,242", r: 4.5, speed: 2.6, period: 1100 });
      if (s.end === year && !s.ongoing) rings.push({ lat: c.lat, lng: c.lng, rgb: "208,59,59", r: 7, speed: 3.6, period: 1300 });
    }
    globe.ringsData(rings);
    clearTimeout(emitRings.timer);
    emitRings.timer = setTimeout(() => globe.ringsData([]), 2600);
  }

  // ------------------------------------------------------------------ panneau « situation mondiale »
  // Sur téléphone (≤ 860 px), une carte repliable au-dessus de la ligne du temps, fermée par défaut ;
  // son résumé donne l'année et le nombre d'autocraties.
  const world = document.getElementById("world");
  const worldToggle = document.getElementById("world-toggle");
  const phone = window.matchMedia("(max-width: 860px)");
  // La carte, le dossier et la liste se posent entre les commandes et la ligne du temps, dont les hauteurs varient
  // avec la langue et les polices : elles sont mesurées (variables CSS --timeline-space et --controls-space)
  const atlasNode = document.querySelector(".atlas");
  const timelineNode = document.querySelector(".timeline");
  const controlsNode = document.querySelector(".hud-controls");
  function measureLayout() {
    const box = atlasNode.getBoundingClientRect();
    const space = Math.ceil(box.bottom - timelineNode.getBoundingClientRect().top);
    atlasNode.style.setProperty("--timeline-space", `${space}px`);
    atlasNode.style.setProperty("--controls-space", `${Math.ceil(controlsNode.getBoundingClientRect().bottom - box.top)}px`);
    // Ordinateur : le globe s'arrête au-dessus de la ligne du temps, qui ne le masque plus ; téléphone : plein écran
    atlasNode.style.setProperty("--globe-bottom", phone.matches ? "0px" : `${space + 8}px`);
  }
  if (window.ResizeObserver) new ResizeObserver(measureLayout).observe(timelineNode);
  if (window.ResizeObserver) new ResizeObserver(measureLayout).observe(controlsNode);
  window.addEventListener("resize", measureLayout);
  measureLayout();
  function setWorldOpen(open) {
    world.classList.toggle("open", open);
    worldToggle.setAttribute("aria-expanded", String(open));
  }
  worldToggle.addEventListener("click", () => setWorldOpen(!world.classList.contains("open")));
  setWorldOpen(!phone.matches);
  phone.addEventListener("change", (e) => setWorldOpen(!e.matches));

  const legendNode = document.getElementById("legend");
  const kpiNode = document.getElementById("kpi-autocracies");
  function renderWorld() {
    const y = state.year;
    const counts = COUNTS[y - Y0];
    const sovereign = Object.entries(counts).filter(([k]) => k !== "dependent").reduce((s, [, v]) => s + v, 0);
    const autoc = autocraciesIn(counts);
    document.getElementById("world-year").textContent = y;
    document.getElementById("world-summary").textContent = `${y} · ${t("atlas.autocracies", { count: autoc })}`;
    // Premier affichage sans animation : le compteur est juste avant même que le globe ne soit prêt
    if (kpiNode.dataset.value === undefined) { Core.setText(kpiNode, Core.fmt(autoc)); kpiNode.dataset.value = String(autoc); }
    else Core.animateNumber(kpiNode, autoc, { duration: 520 });
    document.getElementById("kpi-share").textContent = t("atlas.kpiShare", {
      pct: Core.pct(sovereign ? (100 * autoc) / sovereign : 0), states: t("atlas.sovereignStates", { count: sovereign }) });

    legendNode.innerHTML = "";
    const note = document.getElementById("legend-note");
    if (state.mode === "type") {
      const max = Math.max(1, ...Labels.LEGEND.map((g) => counts[g.key] || 0));
      for (const g of Labels.LEGEND) {
        if (g.key === "nodata") continue;
        const n = counts[g.key] || 0;
        const li = el("li", { class: state.hidden.has(g.key) ? "off" : "", role: "button", tabindex: "0",
                              "aria-pressed": String(!state.hidden.has(g.key)), title: t("atlas.legendToggle") }, [
          el("span", { class: "swatch", style: { background: HEX[g.cats[0]], outline: g.key === "dependent" ? "1px solid var(--hair-strong)" : "" } }),
          el("span", { text: Labels.cat(g.key) }),
          el("span", { class: "n", text: Core.fmt(n) }),
          el("span", { class: "bar" }, el("i", { style: { width: `${(100 * n) / max}%` } })),
        ]);
        const toggle = () => {
          if (state.hidden.has(g.key)) state.hidden.delete(g.key); else state.hidden.add(g.key);
          repaint(); renderWorld();
          legendNode.querySelector(`[data-key="${g.key}"]`)?.focus();
        };
        li.dataset.key = g.key;
        li.addEventListener("click", toggle);
        li.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } });
        legendNode.appendChild(li);
      }
      note.textContent = t("atlas.legendNoteType");
    } else {
      const stops = state.mode === "age" ? AGE_STOPS : VDEM_STOPS;
      const ramp = `linear-gradient(90deg, ${stops.map(([, c], i) => `${c} ${(100 * i) / (stops.length - 1)}%`).join(", ")})`;
      legendNode.appendChild(el("li", { class: "ramp-row", dir: "ltr", style: { cursor: "default" } }, [
        el("span", { class: "ramp", style: { background: ramp } }),
        el("span", { class: "ramp-ticks" }, stops.map(([v]) =>
          el("span", { text: state.mode === "age" ? (v === 60 ? "60+" : String(v)) : I18n.raw(v, 2) }))),
      ]));
      note.textContent = t(state.mode === "age" ? "atlas.legendNoteAge" : "atlas.legendNoteVdem");
    }
    renderEvents();
    renderOldest();
  }

  function eventItem(s, kind, y) {
    const what = s.party || Labels.regimeType(s.type);
    const sub = kind === "fall"
      ? t("atlas.fallAfter", { years: years(y - s.start + 1) }) + (s.ended ? " · " + Labels.ended(s.ended) : "")
      : t("atlas.accession") + (s.gained ? " · " + Labels.gained(s.gained) : "");
    return el("button", { class: "event", type: "button", onclick: () => s.poly && select(s.poly, { fly: true }) }, [
      el("span", { class: "sym", "aria-hidden": "true", text: kind === "fall" ? "↓" : "↑" }),
      el("span", {}, [el("strong", { text: nm(s.label) }), " — ", el("bdi", { text: what }), el("span", { class: "sub", text: sub })]),
    ]);
  }
  function renderEvents() {
    const y = state.year;
    const box = document.getElementById("events");
    const starts = A.spells.filter((s) => s.start === y);
    const ends = A.spells.filter((s) => s.end === y && !s.ongoing);
    document.getElementById("events-count").textContent = `${starts.length} ↑ · ${ends.length} ↓`;
    box.innerHTML = "";
    if (!starts.length && !ends.length) box.appendChild(el("span", { class: "muted", text: t("atlas.noEvents") }));
    ends.forEach((s) => box.appendChild(eventItem(s, "fall", y)));
    starts.forEach((s) => box.appendChild(eventItem(s, "start", y)));
  }

  function renderOldest() {
    const y = state.year;
    const list = document.getElementById("oldest");
    list.innerHTML = "";
    A.spells.filter((s) => s.start <= y && s.end >= y)
      .sort((a, b) => a.start - b.start).slice(0, 5)
      .forEach((s) => {
        list.appendChild(el("li", {}, el("button", { type: "button", onclick: () => s.poly && select(s.poly, { fly: true }) }, [
          el("span", {}, [nm(s.label), el("bdi", { class: "party", text: s.party || Labels.regimeType(s.type) || "" })]),
          el("span", { class: "yrs", text: years(y - s.start + 1) }),
        ])));
      });
  }

  // ------------------------------------------------------------------ dossier pays
  const dossier = document.getElementById("dossier");
  const dossierBody = document.getElementById("dossier-body");

  /** inherited : 0 = régime propre, 1 = le territoire fait partie d'un autre État, 2 = annexion non reconnue
      (dite par une note) ; notes : clés atlas.status.* qui s'appliquent à ce territoire cette année. */
  function regimeParagraph(r, year, inherited, territory, notes = []) {
    const cat = catOf(r);
    const label = labelOf(r);
    const s = spellOf(r);
    const H = I18n.tHtml;
    const parts = notes.map((key) => H(`atlas.status.${key}`));
    if (inherited === 1) parts.push(H("atlas.narr.inherited", { territory, state: label }));
    if (cat === "nodata") return parts.concat(H("atlas.narr.noData", { year })).join(" ");
    if (cat === "dependent") {
      if (!notes.length) parts.push(H("atlas.narr.dependent", { year }));
      return parts.join(" ");
    }
    if (s) {
      const ord = I18n.ordinal(year - s.start + 1);
      if (s.party) {
        parts.push(H("atlas.narr.party", { party: s.party, start: s.start, ord, year }));
        const traits = [];
        if (s.origin) traits.push(t("atlas.narr.traitOrigin", { value: Labels.origin(s.origin) }));
        if (s.gained) traits.push(t("atlas.narr.traitGained", { value: Labels.gained(s.gained) }));
        if (s.marxist === 1) traits.push(t("atlas.narr.traitMarxist"));
        if (traits.length) parts.push(escape(I18n.cap(traits.join(t("common.listSep")))) + t("common.period"));
        if (s.governance) parts.push(H("atlas.narr.governance", { value: Labels.governance(s.governance) }));
      } else {
        parts.push(H("atlas.narr.noParty", { type: I18n.cap(Labels.regimeType(s.type)), start: s.start, ord, year }));
        if (s.gained) parts.push(H("atlas.narr.gained", { value: Labels.gained(s.gained) }));
      }
      const how = s.ended ? t("atlas.narr.how", { value: Labels.ended(s.ended) }) : "";
      if (s.ongoing && s.end >= Y1) parts.push(H("atlas.narr.ongoing", { last: Y1 }));
      else if (s.end > year) parts.push(H("atlas.narr.willEnd", { end: s.end, how }));
      else parts.push(H("atlas.narr.lastYear", { how }));
    } else if (cat === "other_vdem") {
      parts.push(H("atlas.narr.otherVdem", { regime: Labels.vdemRegimeInSentence(r[2]), year }));
    } else if (cat === "democracy") {
      parts.push(H("atlas.narr.democracy", { regime: Labels.vdemRegimeInSentence(r[2]), year }));
    }
    return parts.join(" ");
  }

  /** Portrait d'une personne (index dans PEOPLE), ou -1. */
  const portraitOf = (person) => (person >= 0 ? PEOPLE[person][1] : -1);

  function leaderBlock(r) {
    if (r[4] < 0) return null;
    const [hos, hosTitle, hog, hogTitle, , hosPerson, hogPerson] = A.leaders[r[4]];
    // Le nom est écrit à côté du portrait : l'image est décorative (alt vide)
    const item = (role, name, title, person) => el("div", { class: "d-leader" }, [
      picture(portraitOf(person), "d-avatar", ""),
      el("span", {}, [el("span", { class: "role", text: role }), el("bdi", { text: name }),
        title ? el("span", { class: "title" }, [" · ", el("bdi", { text: title })]) : null])]);
    return el("div", { class: "d-leaders" }, [
      item(t(hog ? "atlas.headOfState" : "atlas.headOfStateAndGov"), hos, hosTitle, hosPerson),
      hog ? item(t("atlas.headOfGov"), hog, hogTitle, hogPerson) : null,
    ]);
  }

  /** Image principale de la fiche : le logo du parti au pouvoir (s'il était déjà utilisé cette année-là), sinon le
      portrait du dirigeant principal. {node, credits: [[libellé, image]]} ou null. */
  function cardFigure(r, year) {
    const s = spellOf(r);
    const item = s && s.party ? partyItem(s, year) : null;
    if (item && item[2] >= 0 && (item[3] === null || item[3] <= year)) {
      return {
        node: el("figure", { class: "d-figure logo" }, [
          picture(item[2], "", t("atlas.media.logoAlt", { party: s.party }), dropFigure),
          el("figcaption", { text: t(item[4] ? "atlas.media.logoCurrent" : "atlas.media.logoCaption") })]),
        credits: [[t("atlas.media.creditLogo"), item[2]]],
      };
    }
    const m = mainLeader(r);
    const img = m ? portraitOf(m.person) : -1;
    if (img < 0) return null;
    return {
      node: el("figure", { class: "d-figure portrait" }, [
        picture(img, "", t("atlas.media.portraitAlt", { name: m.name }), dropFigure),
        el("figcaption", {}, [el("bdi", { text: m.name }), m.title ? el("span", { class: "title", text: m.title }) : null])]),
      credits: [[portraitCredit(m.name), img]],
    };
  }

  /** Extrait Wikipédia (chargé à la demande) avec sa source et sa licence ; rien si l'article n'existe pas dans la
      langue de la page. */
  function wikiBox(title) {
    const box = el("blockquote", { class: "d-wiki", hidden: true });
    const lang = I18n.lang;
    wikiTexts(lang).then((texts) => {
      if (!texts[title] || !box.isConnected || I18n.lang !== lang) return;
      const url = `https://${lang}.wikipedia.org/wiki/${encodeURIComponent(title.replace(/ /g, "_"))}`;
      box.append(el("p", { text: texts[title] }), el("footer", {}, [
        el("a", { href: url, target: "_blank", rel: "noopener", text: t("atlas.media.wikiSource", { title }) }), " · ",
        el("a", { href: `https://creativecommons.org/licenses/by-sa/4.0/deed.${lang}`, target: "_blank", rel: "noopener license",
                  text: "CC BY-SA 4.0" })]));
      box.hidden = false;
    });
    return box;
  }

  /** Crédits des images de la fiche (auteur, licence, lien vers la page du fichier) et du texte. */
  function creditsBlock(credits, withText) {
    const seen = new Set();
    const items = credits.filter(([, i]) => i >= 0 && !seen.has(i) && seen.add(i));
    if (!items.length && !withText) return null;
    return el("details", { class: "d-credits d-section" }, [
      el("summary", { text: t("atlas.media.credits") }),
      el("ul", {}, items.map(([what, i]) => el("li", {}, [what + t("common.colon"),
        el("a", { href: filePage(i), target: "_blank", rel: "noopener", text: imageCredit(i) || "Wikimedia Commons" })]))),
      el("p", { class: "note", text: t("atlas.media.creditNote") })]);
  }

  function detailList(r) {
    const s = spellOf(r);
    const rows = [];
    const D = (k) => t(`atlas.detail.${k}`);
    if (s) {
      rows.push([D("regime"), s.party ? Labels.cat("party") : I18n.cap(Labels.regimeType(s.type))]);
      if (s.party) rows.push([D("party"), el("bdi", { text: s.party })]);
      rows.push([D("inPower"), s.ongoing && s.end >= Y1 ? t("atlas.detail.spanOngoing", { start: s.start })
                                                     : t("atlas.detail.span", { start: s.start, end: s.end })]);
      if (s.founded) rows.push([D("founded"), String(s.founded)]);
      if (s.origin) rows.push([D("origin"), Labels.origin(s.origin)]);
      if (s.gained) rows.push([D("gained"), Labels.gained(s.gained)]);
      if (s.party) rows.push([D("strategy"), s.governance ? Labels.governance(s.governance) : t("atlas.detail.notCoded")]);
      if (s.party) rows.push([D("marxist"), t(s.marxist === 1 ? "common.yes" : "common.no")]);
      if (s.independence === 1) rows.push([D("independence"), t("atlas.detail.sinceIndependence")]);
      if (s.renamed) rows.push([D("renamed"), String(s.renamed)]);
      if (!(s.ongoing && s.end >= Y1) && s.ended) rows.push([D("end"), `${s.end} · ${Labels.ended(s.ended)}`]);
    }
    if (r[2] >= 0) rows.push(["V-Dem", Labels.vdemRegime(r[2])]);
    if (r[3] >= 0) rows.push([D("polyarchy"), I18n.iso(`${I18n.raw(r[3] / 1000, 2)} / 1`)]);
    const dl = el("dl", { class: "kv" });
    rows.forEach(([k, v]) => { dl.appendChild(el("dt", { text: k })); dl.appendChild(el("dd", {}, v)); });
    return dl;
  }

  function stripFor(pid) {
    const wrap = el("div");
    const strip = el("div", { class: "strip", dir: "ltr", role: "img", "aria-label": t("atlas.stripAria", { range: I18n.range(Y0, Y1) }) });
    YEARS.forEach((y) => {
      const r = row(pid, y);
      const cell = el("span", { style: { background: HEX[catOf(r)] } });
      cell.addEventListener("mouseenter", (e) => Core.tooltip.show(
        `<div class="t-head">${y}</div>${escape(Labels.cat(catOf(r)))}${spellOf(r) && spellOf(r).party ? " · " + escape(spellOf(r).party) : ""}`,
        e.clientX, e.clientY));
      cell.addEventListener("mouseleave", () => Core.tooltip.hide());
      cell.addEventListener("click", () => setYear(y));
      strip.appendChild(cell);
    });
    strip.appendChild(el("i", { class: "cursor", style: { left: `${((state.year - Y0 + 0.5) / YEARS.length) * 100}%` } }));
    wrap.appendChild(strip);
    wrap.appendChild(el("div", { class: "strip-axis", dir: "ltr" }, [String(Y0), "1970", "1990", "2010", String(Y1)].map((x) => el("span", { text: x }))));
    return wrap;
  }

  function sparkFor(pid) {
    const vals = YEARS.map((y) => row(pid, y)[3]);
    if (vals.every((v) => v < 0)) return null;
    const W = 352, H = 44;
    const x = (i) => (i / (YEARS.length - 1)) * W;
    const yv = (v) => H - 4 - (v / 1000) * (H - 8);
    let d = "", open = false;
    vals.forEach((v, i) => {
      if (v < 0) { open = false; return; }
      d += `${open ? "L" : "M"}${x(i).toFixed(1)},${yv(v).toFixed(1)}`;
      open = true;
    });
    const i = state.year - Y0;
    const cur = vals[i];
    return svg("svg", { class: "spark", viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: "none", role: "img", direction: "ltr",
                        "aria-label": t("atlas.sparkAria", { range: I18n.range(Y0, Y1) }) }, [
      svg("line", { x1: 0, x2: W, y1: yv(500), y2: yv(500), stroke: "rgba(148,163,184,.18)", "stroke-dasharray": "2 3" }),
      svg("path", { d, fill: "none", stroke: "#aab4c1", "stroke-width": 1.4, "vector-effect": "non-scaling-stroke" }),
      svg("line", { x1: x(i), x2: x(i), y1: 0, y2: H, stroke: "#e9edf2", "stroke-width": 1, "vector-effect": "non-scaling-stroke" }),
      cur >= 0 ? svg("circle", { cx: x(i), cy: yv(cur), r: 2.6, fill: "#e9edf2" }) : null,
    ]);
  }

  function renderDossier() {
    const pid = state.selected;
    if (!pid) return;
    const y = state.year;
    const r = row(pid, y);
    const cat = catOf(r);
    const territory = polyName(pid);
    const label = labelOf(r);
    const inherited = r[6];
    const notes = (A.polygons[pid].notes || []).filter(([first, last]) => y >= first && y <= last).map((n) => n[2]);
    const scroll = dossierBody.scrollTop;
    dossierBody.innerHTML = "";
    // En-tête : drapeau de l'État cette année-là (s'il est documenté), nom, territoire
    dossierBody.appendChild(el("div", { class: "d-head" }, [
      picture(r[7], "d-flag", t("atlas.media.flagAlt", { state: label, year: y })),
      el("h2", { class: "d-title", id: "dossier-title", text: label })]));
    dossierBody.appendChild(el("div", { class: "d-sub" }, [
      label !== territory ? t("atlas.territory", { name: territory }) + " · " : "", el("span", { class: "mono", text: String(y) })]));
    dossierBody.appendChild(el("span", { class: "chip" }, [
      el("span", { class: "swatch", style: { background: HEX[cat], outline: cat === "dependent" || cat === "nodata" ? "1px solid var(--hair-strong)" : "" } }),
      Labels.cat(cat)]));
    // Logo du parti ou portrait du dirigeant, à côté du paragraphe sur le régime ; puis l'extrait Wikipédia
    const figure = cat === "nodata" ? null : cardFigure(r, y);
    const narrative = el("p", { class: "d-narrative", html: regimeParagraph(r, y, inherited, territory, notes) });
    dossierBody.appendChild(figure ? el("div", { class: "d-intro" }, [figure.node, narrative]) : narrative);
    const title = cat === "nodata" ? null : wikiTitle(r, y);
    if (title) dossierBody.appendChild(wikiBox(title));
    if (cat !== "nodata") dossierBody.appendChild(detailList(r));
    const credits = [[t("atlas.media.creditFlag"), r[7]]].concat(figure ? figure.credits : []);
    const leaders = leaderBlock(r);
    if (leaders) {
      dossierBody.appendChild(el("div", { class: "d-section" }, [
        el("span", { class: "label", text: t("atlas.leaders", { year: y }) }), leaders]));
      const L = A.leaders[r[4]];
      [[L[0], L[5]], [L[2], L[6]]].forEach(([name, person]) => {
        if (name) credits.push([portraitCredit(name), portraitOf(person)]);
      });
    }
    dossierBody.appendChild(el("div", { class: "d-section" }, [
      el("span", { class: "label", text: t("atlas.trajectory", { range: I18n.range(Y0, Y1) }) }), stripFor(pid)]));
    const spark = sparkFor(pid);
    if (spark) {
      dossierBody.appendChild(el("div", { class: "d-section" }, [
        el("span", { class: "label", text: t("atlas.polyarchyTitle") }), spark]));
    }
    for (const sec of A.polygons[pid].secondary) {
      const sr = y >= sec.first && y <= sec.last ? sec.rows[y - sec.first] : null;
      const box = el("div", { class: "secondary-state" }, [
        el("span", { class: "label", text: t("atlas.secondaryTitle") }),
        el("div", { class: "name", text: nm(sec.label) }),
        el("div", { class: "muted", text: I18n.range(sec.first, sec.last) }),
      ]);
      if (sr) {
        // Ligne de l'État historique [catégorie, spell, régime V-Dem, indice, dirigeants, drapeau], complétée par
        // l'étiquette du polygone (non affichée : pas d'héritage)
        const full = sr.slice(0, 5).concat([r[5], 0, sr[5]]);
        const secFlag = picture(sr[5], "d-flag small", t("atlas.media.flagAlt", { state: nm(sec.label), year: y }));
        if (secFlag) box.insertBefore(secFlag, box.querySelector(".name"));
        box.appendChild(el("p", { class: "d-narrative", html: regimeParagraph(full, y, 0, territory) }));
        const l = leaderBlock(full);
        if (l) box.appendChild(l);
        credits.push([t("atlas.media.creditFlagOf", { state: nm(sec.label) }), sr[5]]);
      } else {
        box.appendChild(el("p", { class: "note", text: t("atlas.secondaryOut", { year: y }) }));
      }
      dossierBody.appendChild(el("div", { class: "d-section" }, box));
    }
    const creditsNode = creditsBlock(credits, Boolean(title));
    if (creditsNode) dossierBody.appendChild(creditsNode);
    dossierBody.appendChild(el("p", { class: "note d-section", text: t("atlas.dossierSources") }));
    dossierBody.scrollTop = scroll;
  }

  let lastFocus = null;
  function select(pid, { fly = false } = {}) {
    state.selected = pid;
    repaint();
    if (!pid) { closeDossier(); return; }
    if (fly) flyTo(pid);
    setRotation(false);
    if (dossier.hidden) lastFocus = document.activeElement;
    dossier.hidden = false;
    document.body.classList.add("dossier-open");
    renderDossier();
    renderList();
  }
  function closeDossier() {
    if (!state.selected && dossier.hidden) return;
    state.selected = null;
    dossier.hidden = true;
    document.body.classList.remove("dossier-open");
    repaint();
    renderList();
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
    lastFocus = null;
  }
  document.getElementById("dossier-close").addEventListener("click", closeDossier);

  // ------------------------------------------------------------------ vue en liste
  const listPanel = document.getElementById("list-panel");
  const listBody = document.getElementById("list-body");
  // first : sens du premier clic ; les valeurs absentes (pas de parti, pas de durée) restent en fin de liste
  const COLUMNS = [
    { key: "name", first: 1, value: (d) => d.name, cmp: (a, b) => I18n.compare(a, b) },
    { key: "type", first: 1, value: (d) => d.typeRank, cmp: (a, b) => a - b },
    { key: "party", first: 1, value: (d) => d.party, cmp: (a, b) => I18n.compare(a, b) },
    { key: "years", first: -1, value: (d) => (d.age > 0 ? d.age : null), cmp: (a, b) => a - b },
  ];
  const TYPE_ORDER = ["party", "military", "monarchy", "other_arpd", "other_vdem", "democracy", "dependent"];

  function listRows() {
    return statesOfYear(state.year).map((s) => {
      const sp = s.spell >= 0 ? A.spells[s.spell] : null;
      return { pid: s.pid, cat: s.cat, name: nm(s.names), party: sp ? sp.party : null,
               regime: sp && !sp.party ? Labels.regimeType(sp.type) : null,
               age: sp ? state.year - sp.start + 1 : -1, typeRank: TYPE_ORDER.indexOf(s.cat) };
    });
  }
  function renderList() {
    if (state.view !== "list") return;
    const col = COLUMNS.find((c) => c.key === state.sort.key);
    const data = listRows().sort((a, b) => {
      const va = col.value(a), vb = col.value(b);
      if (va === null || vb === null) return (va === null) - (vb === null) || I18n.compare(a.name, b.name);
      return col.cmp(va, vb) * state.sort.dir || I18n.compare(a.name, b.name);
    });
    document.getElementById("list-title").textContent = t("atlas.list.title", { year: state.year });
    document.getElementById("list-count").textContent = t("atlas.list.count", { count: data.length });
    const table = el("table", { class: "data list-table" });
    const head = el("tr");
    COLUMNS.forEach((c) => {
      const active = state.sort.key === c.key;
      const th = el("th", { scope: "col", class: c.key === "years" ? "num" : "",
                            "aria-sort": active ? (state.sort.dir > 0 ? "ascending" : "descending") : "none" });
      const b = el("button", { type: "button", class: "sort" + (active ? " on" : "") }, [
        t(`atlas.list.col.${c.key}`), el("span", { class: "arrow", "aria-hidden": "true", text: active ? (state.sort.dir > 0 ? "↑" : "↓") : "↕" })]);
      b.addEventListener("click", () => {
        state.sort = { key: c.key, dir: state.sort.key === c.key ? -state.sort.dir : c.first };
        renderList();
        listBody.querySelector(`th:nth-child(${COLUMNS.indexOf(c) + 1}) button`)?.focus();
      });
      th.appendChild(b);
      head.appendChild(th);
    });
    table.appendChild(el("thead", {}, head));
    const tb = el("tbody");
    data.forEach((d) => {
      const tr = el("tr", { tabindex: "0", class: "clickable" + (d.pid === state.selected ? " row-hl" : ""),
                            "aria-label": t("atlas.list.open", { name: d.name }) }, [
        el("td", { class: "name" }, el("bdi", { text: d.name })),
        el("td", {}, [el("span", { class: "swatch", style: { background: HEX[d.cat] } }), " ", Labels.cat(d.cat)]),
        el("td", {}, d.party ? el("bdi", { text: d.party }) : el("span", { class: "dim", text: d.regime || "—" })),
        el("td", { class: "num", text: d.age > 0 ? I18n.n(d.age) : "—" }),
      ]);
      const open = () => select(d.pid, { fly: true });
      tr.addEventListener("click", open);
      tr.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
        else if (e.key === "ArrowDown") { e.preventDefault(); tr.nextElementSibling?.focus(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); tr.previousElementSibling?.focus(); }
      });
      tb.appendChild(tr);
    });
    table.appendChild(tb);
    const scroll = listBody.scrollTop;
    listBody.innerHTML = "";
    listBody.appendChild(table);
    listBody.scrollTop = scroll;
  }
  function setView(view) {
    if (view === "globe" && state.render.webgl === false) return;      // pas de globe sans WebGL : la liste reste
    state.view = view;
    document.querySelectorAll("#view-seg button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === view)));
    listPanel.hidden = view !== "list";
    document.body.classList.toggle("list-open", view === "list");
    if (view === "list") { renderList(); setRotation(false); }
  }
  document.querySelectorAll("#view-seg button").forEach((b) => b.addEventListener("click", () => setView(b.dataset.view)));
  document.getElementById("list-close").addEventListener("click", () => setView("globe"));

  // ------------------------------------------------------------------ ligne du temps
  const slider = document.getElementById("year-slider");
  const historyNode = document.getElementById("history");
  const STACK = ["party", "military", "monarchy", "other_arpd"];

  function renderHistory() {
    const W = historyNode.clientWidth || 800, H = historyNode.clientHeight || 84;
    historyNode.setAttribute("viewBox", `0 0 ${W} ${H}`);
    historyNode.innerHTML = "";
    historyNode.setAttribute("aria-label", t("atlas.historyAria", { range: I18n.range(Y0, Y1) }));
    const totals = COUNTS.map((c) => STACK.reduce((s, k) => s + (c[k] || 0), 0));
    const max = Math.max(...totals);
    const x = (i) => (i / (YEARS.length - 1)) * W;
    const y = (v) => H - 2 - (v / max) * (H - 10);
    const base = YEARS.map(() => 0);
    STACK.forEach((k) => {
      const top = COUNTS.map((c, i) => base[i] + (c[k] || 0));
      let d = `M${x(0)},${y(base[0])}`;
      top.forEach((v, i) => { d += `L${x(i).toFixed(1)},${y(v).toFixed(1)}`; });
      for (let i = YEARS.length - 1; i >= 0; i--) d += `L${x(i).toFixed(1)},${y(base[i]).toFixed(1)}`;
      historyNode.appendChild(svg("path", { d: d + "Z", fill: HEX[k], opacity: 0.82, stroke: "#04060a", "stroke-width": 0.8 }));
      top.forEach((v, i) => { base[i] = v; });
    });
    historyNode.appendChild(svg("text", { x: 2, y: 9, fill: "#6f7a8a", "font-size": 10, class: "history-max",
                                          text: I18n.svgLabel(t("atlas.autocracies", { count: max })) }));
    const cursor = svg("line", { id: "history-cursor", y1: 0, y2: H, stroke: "#e9edf2", "stroke-width": 1 });
    historyNode.appendChild(cursor);
    moveCursor();
    const hit = svg("rect", { x: 0, y: 0, width: W, height: H, fill: "transparent", style: "cursor:crosshair" });
    const yearAt = (e) => {
      const rect = historyNode.getBoundingClientRect();
      return Core.clamp(Math.round(Y0 + ((e.clientX - rect.left) / rect.width) * (Y1 - Y0)), Y0, Y1);
    };
    hit.addEventListener("mousemove", (e) => {
      const yr = yearAt(e);
      const c = COUNTS[yr - Y0];
      Core.tooltip.show(`<div class="t-head">${yr}</div>` + STACK.map((k) =>
        `<span class="swatch" style="background:${HEX[k]};margin-inline-end:6px"></span>${escape(Labels.cat(k))}${escape(t("common.colon"))}<span class="mono">${Core.fmt(c[k] || 0)}</span>`).join("<br>"),
        e.clientX, e.clientY);
    });
    hit.addEventListener("mouseleave", () => Core.tooltip.hide());
    hit.addEventListener("click", (e) => setYear(yearAt(e)));
    historyNode.appendChild(hit);
  }
  function moveCursor() {
    const c = document.getElementById("history-cursor");
    if (!c) return;
    const W = historyNode.clientWidth || 800;
    const xv = ((state.year - Y0) / (Y1 - Y0)) * W;
    c.setAttribute("x1", xv); c.setAttribute("x2", xv);
  }
  // Graphique de la ligne du temps, affiché ou masqué (choix gardé dans le navigateur). Masqué, la ligne du temps se
  // réduit à l'année et au curseur, et le globe, posé au-dessus d'elle, s'agrandit.
  const GRAPH_KEY = "observatoire-atlas-graphique";
  const graphToggle = document.getElementById("graph-toggle");
  let graphShown = true;
  try { graphShown = localStorage.getItem(GRAPH_KEY) !== "0"; } catch (e) { /* stockage indisponible : affiché */ }
  function setGraph(show, { save = true } = {}) {
    graphShown = show;
    timelineNode.classList.toggle("compact", !show);
    graphToggle.setAttribute("aria-expanded", String(show));
    graphToggle.textContent = t(show ? "atlas.graphHide" : "atlas.graphShow");
    if (save) { try { localStorage.setItem(GRAPH_KEY, show ? "1" : "0"); } catch (e) { /* le choix vaut pour la page */ } }
    if (show) renderHistory();
    measureLayout();
  }
  graphToggle.addEventListener("click", () => setGraph(!graphShown));

  function renderTicks() {
    const box = document.getElementById("ticks");
    box.innerHTML = "";
    for (const yr of [1946, 1960, 1970, 1980, 1990, 2000, 2010, 2024]) {
      box.appendChild(el("span", { text: yr, style: { left: `${((yr - Y0) / (Y1 - Y0)) * 100}%` } }));
    }
  }

  // Annonce de l'année pour les lecteurs d'écran (une seule fois quand l'animation tourne)
  const live = document.getElementById("year-live");
  let liveTimer = null;
  function announce() {
    clearTimeout(liveTimer);
    liveTimer = setTimeout(() => {
      const autoc = autocraciesIn(COUNTS[state.year - Y0]);
      live.textContent = t("atlas.announce", { year: state.year, count: autoc });
    }, state.playing ? 1500 : 350);
  }

  function setYear(y, { rings = true } = {}) {
    y = Core.clamp(y, Y0, Y1);
    if (y === state.year && slider.value == y) return;
    state.year = y;
    slider.value = y;
    slider.setAttribute("aria-valuetext", String(y));
    document.getElementById("year-display").textContent = y;
    repaint();
    renderWorld();
    moveCursor();
    if (rings) emitRings(y);
    if (state.selected) renderDossier();
    if (state.hovered) showTooltip(state.hovered);
    renderList();
    announce();
  }
  slider.addEventListener("input", () => setYear(Number(slider.value)));
  document.getElementById("year-prev").addEventListener("click", () => setYear(state.year - 1));
  document.getElementById("year-next").addEventListener("click", () => setYear(state.year + 1));

  const playBtn = document.getElementById("play");
  function setPlaying(on) {
    state.playing = on;
    playBtn.textContent = on ? "❚❚" : "▶";
    playBtn.setAttribute("aria-label", t(on ? "atlas.pause" : "atlas.play"));
    playBtn.setAttribute("aria-pressed", String(on));
    clearInterval(state.timer);
    if (on) {
      if (state.year >= Y1) setYear(Y0);
      state.timer = setInterval(() => {
        if (state.year >= Y1) { setPlaying(false); return; }
        setYear(state.year + 1);
      }, 700);
    }
  }
  playBtn.addEventListener("click", () => setPlaying(!state.playing));

  // ------------------------------------------------------------------ commandes
  document.querySelectorAll("#mode-seg button").forEach((b) => b.addEventListener("click", () => {
    state.mode = b.dataset.mode;
    document.querySelectorAll("#mode-seg button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    repaint(); renderWorld();
  }));
  document.getElementById("relief-toggle").addEventListener("change", (e) => { state.relief = e.target.checked; repaint(); });
  const rotateToggle = document.getElementById("rotate-toggle");
  function setRotation(on) { if (controls) controls.autoRotate = on; rotateToggle.checked = on; }
  rotateToggle.checked = !reduceMotion;          // pas de rotation automatique si l'utilisateur limite les animations
  rotateToggle.addEventListener("change", (e) => setRotation(e.target.checked));

  // Recherche : noms actuels et noms historiques, dans la langue du site
  const search = document.getElementById("search-input");
  const datalist = document.getElementById("country-list");
  let searchIndex = new Map();
  function buildSearch() {
    searchIndex = new Map();
    FEATURES.forEach((f) => searchIndex.set(nm(f.properties.name), f.id));
    (I18n.get("atlas.historicalNames") || []).forEach(([n, id]) => searchIndex.set(n, id));
    datalist.innerHTML = "";
    [...searchIndex.keys()].sort(I18n.compare).forEach((n) => datalist.appendChild(el("option", { value: n })));
  }
  search.addEventListener("change", () => {
    const query = search.value.trim().toLowerCase();
    const key = [...searchIndex.keys()].find((k) => k.toLowerCase() === query);
    if (key) { select(searchIndex.get(key), { fly: true }); search.blur(); }
  });

  document.addEventListener("keydown", (e) => {
    const tag = e.target.tagName;
    if ((tag === "INPUT" && e.target.type !== "range") || tag === "TR" || tag === "SELECT") return;
    // Flèches : année précédente / suivante. La ligne du temps reste de gauche à droite dans les trois langues.
    if (e.target.type === "range") return;           // le curseur gère lui-même les flèches
    if (e.key === "ArrowLeft") { e.preventDefault(); setYear(state.year - 1); }
    else if (e.key === "ArrowRight") { e.preventDefault(); setYear(state.year + 1); }
    else if (e.key === " " && tag !== "BUTTON" && !e.target.closest("[role=button]")) { e.preventDefault(); setPlaying(!state.playing); }
    else if (e.key === "Escape") { if (state.selected) closeDossier(); else if (state.view === "list" && state.render.webgl !== false) setView("globe"); }
  });
  window.addEventListener("resize", () => { if (graphShown) renderHistory(); });

  // ------------------------------------------------------------------ langue
  function renderLanguage() {
    buildSearch();
    setGraph(graphShown, { save: false });
    renderHistory();
    renderWorld();
    renderList();
    if (state.selected) renderDossier();
    setPlaying(state.playing);
    Core.tooltip.hide();
  }
  I18n.onChange(renderLanguage);

  // ------------------------------------------------------------------ démarrage
  // Panneaux, ligne du temps et liste d'abord ; le globe ensuite, une fois la page affichée.
  renderTicks();
  buildSearch();
  setGraph(graphShown, { save: false });
  renderHistory();
  slider.value = state.year;
  document.getElementById("year-display").textContent = state.year;
  setPlaying(false);
  renderWorld();
  // Lien direct (depuis la simulation) : atlas.html#pays=CUB&annee=1975
  const link = new URLSearchParams(location.hash.slice(1));
  if (Number(link.get("annee"))) setYear(Number(link.get("annee")), { rings: false });
  if (FEATURES.some((f) => f.id === link.get("pays"))) select(link.get("pays"), { fly: true });
  if (link.get("vue") === "liste") setView("list");
  window.Atlas = { setYear, select, setView, setWorldOpen, state, globe: () => globe };   // pour les tests
  window.__uiReady = true;
  let started = false;
  const start = () => {
    if (started) return;
    started = true;
    initGlobe();
    window.__ready = true;
  };
  requestAnimationFrame(() => setTimeout(start, 0));
  setTimeout(start, 500);          // onglet en arrière-plan : requestAnimationFrame n'y est pas appelé
})();
