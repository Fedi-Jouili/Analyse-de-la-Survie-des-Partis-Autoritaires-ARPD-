/* Graphiques partagés par l'accueil et le tableau de bord (page Analyse).
   Les tracés (SVG) se lisent de gauche à droite dans les trois langues ; les étiquettes et les valeurs sont en HTML,
   pour suivre le sens d'écriture de la page. Couleurs validées sur le fond du site (méthode « dataviz ») :
   bleu = le facteur protège, rouge = il fragilise, gris = pas d'effet net ; une série seule est dessinée à l'encre.
   Chaque graphique réagit au survol et au clavier (infobulle), et son tableau équivalent figure dans le détail. */
(function () {
  "use strict";

  const { el, svg, escape } = Core;
  const t = I18n.t;
  const COLOR = { protect: "#3987e5", harm: "#e66767", none: "#4b5563", ink: "#e9edf2", ink2: "#aab4c1", ink3: "#6f7a8a",
                  hair: "rgba(148,163,184,0.13)", hairStrong: "rgba(148,163,184,0.26)", surface: "#0a0f16" };
  const years = (v) => t("units.years", { count: v });

  /** Valeur d'une courbe de Kaplan-Meier (en escalier) après v années. */
  const kmAt = (curve, v) => { let r = curve.s[0]; for (let i = 0; i < curve.t.length && curve.t[i] <= v; i++) r = curve.s[i]; return r; };

  /** Infobulle au survol et au focus clavier d'un élément (html() rend le contenu au moment voulu). */
  function hover(node, html) {
    node.tabIndex = 0;
    const show = (x, y) => Core.tooltip.show(html(), x, y);
    node.addEventListener("pointermove", (e) => show(e.clientX, e.clientY));
    node.addEventListener("pointerleave", () => Core.tooltip.hide());
    node.addEventListener("focus", () => { const r = node.getBoundingClientRect(); show(r.left + r.width / 2, r.bottom); });
    node.addEventListener("blur", () => Core.tooltip.hide());
  }

  /** Barre horizontale à bout arrondi (4 px), carrée du côté de la ligne de base. */
  function bar(x0, x1, y, h, fill) {
    const left = Math.min(x0, x1), w = Math.abs(x1 - x0);
    const r = Math.min(4, w / 2, h / 2);
    if (w < 0.5) return svg("rect", { x: left, y, width: 1, height: h, fill });
    const d = x1 >= x0
      ? `M${left},${y}H${left + w - r}Q${left + w},${y} ${left + w},${y + r}V${y + h - r}Q${left + w},${y + h} ${left + w - r},${y + h}H${left}Z`
      : `M${left + w},${y}H${left + r}Q${left},${y} ${left},${y + r}V${y + h - r}Q${left},${y + h} ${left + r},${y + h}H${left + w}Z`;
    return svg("path", { d, fill });
  }

  /** Lignes « étiquette | tracé | valeur » : le tracé est dessiné une fois la ligne posée (sa largeur est connue). */
  function rowsLayout(host, cls, items, drawTrack) {
    host.innerHTML = "";
    const box = el("div", { class: `crows ${cls}` });
    host.appendChild(box);
    const tracks = items.map((item) => {
      const track = el("div", { class: "crow-track", dir: "ltr" });
      const row = el("div", { class: "crow" + (item.cls ? " " + item.cls : "") },
                     [el("span", { class: "crow-label", text: item.label }), track, el("span", { class: "crow-value", text: item.value || "" })]);
      if (item.tip) hover(row, item.tip);
      box.appendChild(row);
      return track;
    });
    tracks.forEach((track, i) => {
      const W = Math.max(track.clientWidth, 80);
      const s = svg("svg", { width: W, height: 22, viewBox: `0 0 ${W} 22`, "aria-hidden": "true" });
      drawTrack(s, W, items[i]);
      track.appendChild(s);
    });
    return box;
  }
  /** Axe sous des lignes : graduations [{v, label}] placées par x(v, W). */
  function axisRow(box, ticks, x) {
    const track = el("div", { class: "crow-track", dir: "ltr" });
    box.appendChild(el("div", { class: "crow crow-axis", "aria-hidden": "true" }, [el("span"), track, el("span")]));
    const W = Math.max(track.clientWidth, 80);
    const s = svg("svg", { width: W, height: 16, viewBox: `0 0 ${W} 16` });
    // Sur un écran étroit, les graduations qui se toucheraient sont retirées ; les deux extrémités restent
    const span = ({ v, label, anchor }) => {
      const w = label.replace(/[⁦-⁩]/g, "").length * 6.4, c = x(v, W);
      return anchor === "start" ? [c, c + w] : anchor === "end" ? [c - w, c] : [c - w / 2, c + w / 2];
    };
    const apart = (a, b) => span(a)[1] + 6 <= span(b)[0];
    const kept = [];
    ticks.forEach((tk) => { if (!kept.length || apart(kept[kept.length - 1], tk)) kept.push(tk); });
    const lastTick = ticks[ticks.length - 1];
    if (kept[kept.length - 1] !== lastTick) {
      while (kept.length > 1 && !apart(kept[kept.length - 1], lastTick)) kept.pop();
      kept.push(lastTick);
    }
    // Une étiquette qui contient des mots arabes est isolée de droite à gauche ; les nombres et symboles (÷4, ×1) non
    kept.forEach(({ v, label, anchor }) => s.appendChild(svg("text", {
      x: x(v, W), y: 11, "text-anchor": anchor || "middle", fill: COLOR.ink3, "font-size": 10.5,
      "font-family": "JetBrains Mono, IBM Plex Sans Arabic, monospace",
      text: /[؀-ۿ]/.test(label) ? I18n.svgLabel(label) : label })));
    track.appendChild(s);
  }
  function legend(items) {
    return el("ul", { class: "clegend" }, items.map(([color, label, shape]) =>
      el("li", {}, [el("span", { class: "key" + (shape === "dot" ? " dot" : ""), style: { background: color } }), label])));
  }

  // ------------------------------------------------------------------ survie (Kaplan-Meier)
  /** Courbes de survie en escalier ; series = [{key, label, curve, hl}] ; les séries mises en avant ont une étiquette
      directe, les autres restent en gris (contexte). */
  function km(host, series, { band = null, median = null, height = 260, axis = true } = {}) {
    host.setAttribute("dir", "ltr");
    const W = Math.max(host.clientWidth, 280), H = height;
    const longest = Math.max(4, ...series.filter((s) => s.hl && s.label).map((s) => s.label.length));
    const m = { l: axis ? 36 : 4, r: series.some((s) => s.hl && s.label) ? 18 + 6.4 * longest : 8, t: axis ? 24 : 10, b: axis ? 42 : 6 };
    const tMax = Math.max(...series.map((s) => s.curve.t[s.curve.t.length - 1]));
    const x = (v) => m.l + (v / tMax) * (W - m.l - m.r);
    const y = (v) => m.t + (1 - v) * (H - m.t - m.b);
    const root = svg("svg", { class: "chart", viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: "img",
                               "aria-label": t("analyse.km.aria") });
    if (axis) {
      const grid = svg("g", { class: "grid" });
      [0, 0.25, 0.5, 0.75, 1].forEach((v) => {
        grid.appendChild(svg("line", { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v) }));
        root.appendChild(svg("text", { x: m.l - 8, y: y(v) + 3.5, "text-anchor": "end", text: I18n.raw(v * 100) + "%" }));
      });
      root.appendChild(grid);
      for (let v = 0; v <= tMax; v += tMax > 80 ? 20 : 10) {   // abscisse : années au pouvoir
        root.appendChild(svg("text", { x: x(v), y: H - 24, "text-anchor": "middle", text: String(v) }));
      }
      // titres des axes, pour un lecteur qui découvre ce type de courbe
      root.appendChild(svg("text", { x: 2, y: 10, class: "axis-title", "text-anchor": "start", text: I18n.svgLabel(t("analyse.km.axisY")) }));
      root.appendChild(svg("text", { x: W - m.r, y: H - 5, class: "axis-title", "text-anchor": "end", text: I18n.svgLabel(t("analyse.km.axisX")) }));
    }
    const stepPath = (curve, key = "s") => {
      let d = `M${x(curve.t[0])},${y(curve[key][0])}`;
      for (let i = 1; i < curve.t.length; i++) d += `H${x(curve.t[i]).toFixed(1)}V${y(curve[key][i]).toFixed(1)}`;
      return d;
    };
    if (band) {
      let d = `M${x(band.t[0])},${y(band.hi[0])}`;
      for (let i = 1; i < band.t.length; i++) d += `H${x(band.t[i]).toFixed(1)}V${y(band.hi[i]).toFixed(1)}`;
      for (let i = band.t.length - 1; i >= 0; i--) d += `V${y(band.lo[i]).toFixed(1)}H${x(band.t[Math.max(i - 1, 0)]).toFixed(1)}`;
      root.appendChild(svg("path", { d: d + "Z", fill: "rgba(233,237,242,0.08)", stroke: "none" }));
    }
    if (median !== null) {
      root.appendChild(svg("line", { x1: m.l, x2: x(median), y1: y(0.5), y2: y(0.5), stroke: "rgba(233,237,242,.35)" }));
      root.appendChild(svg("line", { x1: x(median), x2: x(median), y1: y(0.5), y2: y(0), stroke: "rgba(233,237,242,.35)" }));
      root.appendChild(svg("circle", { cx: x(median), cy: y(0.5), r: 4, fill: COLOR.ink, stroke: COLOR.surface, "stroke-width": 2 }));
      root.appendChild(svg("text", { x: x(median) + 8, y: y(0.5) - 8, class: "lbl hl",
                                     text: I18n.svgLabel(t("analyse.km.median", { years: years(median) })) }));
    }
    const paths = {};
    series.filter((s) => !s.hl).concat(series.filter((s) => s.hl)).forEach((s) => {
      paths[s.key] = svg("path", { d: stepPath(s.curve), fill: "none", stroke: s.hl ? (s.color || COLOR.ink) : COLOR.none,
                                   "stroke-width": s.hl ? 2 : 1.2, "stroke-linejoin": "round", "stroke-linecap": "round" });
      root.appendChild(paths[s.key]);
    });
    series.filter((s) => s.hl && s.label).forEach((s) => {
      const last = s.curve.s[s.curve.s.length - 1];
      root.appendChild(svg("text", { x: x(s.curve.t[s.curve.t.length - 1]) + 6, y: y(last) + 3.5, class: "lbl hl",
                                     text: I18n.svgLabel(s.label) }));
    });
    // survol : réticule et infobulle avec toutes les séries mises en avant
    const cross = svg("line", { y1: m.t, y2: H - m.b, stroke: "rgba(233,237,242,.5)", visibility: "hidden" });
    root.appendChild(cross);
    const hit = svg("rect", { x: m.l, y: m.t, width: Math.max(1, W - m.l - m.r), height: H - m.t - m.b, fill: "transparent" });
    hit.addEventListener("pointermove", (e) => {
      const rect = root.getBoundingClientRect();
      const v = Math.max(0, Math.round(((e.clientX - rect.left) * (W / rect.width) - m.l) / (W - m.l - m.r) * tMax));
      cross.setAttribute("x1", x(v)); cross.setAttribute("x2", x(v)); cross.setAttribute("visibility", "visible");
      const shown = series.filter((s) => s.hl || series.length === 1);
      Core.tooltip.show(`<div class="t-head">${escape(t("analyse.km.tipHead", { years: years(v) }))}</div>` + shown.map((s) =>
        escape(t("analyse.km.tipLine", { label: s.label || t("analyse.km.all"), pct: Core.pct(kmAt(s.curve, v) * 100) }))).join("<br>"),
        e.clientX, e.clientY);
    });
    hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); Core.tooltip.hide(); });
    root.appendChild(hit);
    host.innerHTML = "";
    host.appendChild(root);
    return paths;
  }

  // ------------------------------------------------------------------ effets (multiplicateurs du risque)
  const LOG4 = Math.log(4);
  /** Texte d'un multiplicateur : « ÷2,5 » quand le risque baisse, « ×1,7 » quand il monte. */
  const multiplier = (hr, digits = 1) =>
    (hr < 1 ? I18n.iso("÷" + I18n.raw(1 / hr, digits)) : I18n.iso("×" + I18n.raw(hr, digits)));
  /** rows = [{label, hr, lo, hi, p, pText?}] : barre depuis ×1, vers la gauche (bleu) si le facteur protège, vers la
      droite (rouge) s'il fragilise ; grise si l'effet n'est pas significatif. Échelle logarithmique de ÷4 à ×4.
      pText remplace la p-value dans l'infobulle (par exemple, une p-value corrigée) ; digits : décimales des
      multiplicateurs (2 quand les effets sont tous proches de ×1). */
  function effects(host, rows, { legendLabels = null, digits = 1 } = {}) {
    const x = (v, W) => (W / 2) * (1 + Math.max(-1, Math.min(1, Math.log(v) / LOG4)));
    const color = (r) => (r.p >= 0.05 ? COLOR.none : r.hr < 1 ? COLOR.protect : COLOR.harm);
    const items = rows.map((r) => ({
      label: r.label, value: multiplier(r.hr, digits), cls: r.p >= 0.05 ? "muted" : "",
      tip: () => `<div class="t-head">${escape(r.label)}</div><strong>${escape(multiplier(r.hr, digits))}</strong> · ` +
                 escape(I18n.iso(`HR ${I18n.raw(r.hr, 2)} [${I18n.raw(r.lo, 2)} – ${I18n.raw(r.hi, 2)}]`)) + " · " +
                 escape(r.pText || I18n.pval(r.p)),
      r,
    }));
    host.innerHTML = "";
    const wrap = el("div", { class: "cchart" });
    if (legendLabels) wrap.appendChild(legend([[COLOR.protect, legendLabels.protect], [COLOR.harm, legendLabels.harm],
                                               [COLOR.none, legendLabels.none]]));
    host.appendChild(wrap);
    const rowsHost = el("div");
    wrap.appendChild(rowsHost);
    const box = rowsLayout(rowsHost, "fx", items, (s, W, item) => {
      s.appendChild(svg("line", { x1: W / 2, x2: W / 2, y1: 0, y2: 22, stroke: COLOR.hairStrong }));
      s.appendChild(bar(x(1, W), x(item.r.hr, W), 5, 12, color(item.r)));
    });
    axisRow(box, [{ v: 0.25, label: "÷4", anchor: "start" }, { v: 0.5, label: "÷2" }, { v: 1, label: "×1" },
                  { v: 2, label: "×2" }, { v: 4, label: "×4", anchor: "end" }], x);
    return wrap;
  }

  // ------------------------------------------------------------------ scores de prédiction (0,5 = hasard, 1 = parfait)
  /** groups = [{title, rows: [{label, mean, sd, ref}]}] : barre de 0,5 à la moyenne, trait ± un écart-type ;
      le modèle de référence est à l'encre, les autres en gris. */
  function scores(host, groups, { lo = 0.5, hi = 1, chanceLabel, perfectLabel } = {}) {
    const x = (v, W) => ((Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo)) * (W - 2) + 1;
    host.innerHTML = "";
    const wrap = el("div", { class: "cchart" });
    host.appendChild(wrap);
    let box = null;
    groups.forEach((g) => {
      wrap.appendChild(el("div", { class: "cgroup", text: g.title }));
      const rowsHost = el("div");
      wrap.appendChild(rowsHost);
      box = rowsLayout(rowsHost, "sc", g.rows.map((r) => ({
        label: r.label, value: I18n.raw(r.mean, 3), cls: r.ref ? "ref" : "",
        tip: () => `<div class="t-head">${escape(g.title)}</div><strong>${escape(I18n.iso(I18n.raw(r.mean, 3) + " ± " + I18n.raw(r.sd, 3)))}</strong> · ${escape(r.label)}`,
        r,
      })), (s, W, item) => {
        s.appendChild(svg("rect", { x: 0, y: 10, width: W, height: 2, fill: COLOR.hair }));
        s.appendChild(bar(x(lo, W), x(item.r.mean, W), 5, 12, item.r.ref ? COLOR.ink : COLOR.ink3));
        const a = x(item.r.mean - item.r.sd, W), b = x(item.r.mean + item.r.sd, W);
        s.appendChild(svg("line", { x1: a, x2: b, y1: 18.5, y2: 18.5, stroke: COLOR.ink2, "stroke-width": 1 }));
      });
    });
    if (box) axisRow(box, [{ v: lo, label: chanceLabel || I18n.raw(lo, 1), anchor: "start" },
                           { v: (lo + hi) / 2, label: I18n.raw((lo + hi) / 2, 2) },
                           { v: hi, label: perfectLabel || I18n.raw(hi, 0), anchor: "end" }], x);
    return wrap;
  }

  // ------------------------------------------------------------------ avant → après (deux valeurs par ligne)
  /** rows = [{label, a, b, tip}] : point gris (a, avant) relié à un point bleu (b, après). */
  function dumbbell(host, rows, { legendLabels, digits = 3 } = {}) {
    const vals = rows.flatMap((r) => [r.a, r.b]);
    const lo = Math.floor((Math.min(...vals) - 0.01) * 50) / 50, hi = Math.ceil((Math.max(...vals) + 0.01) * 50) / 50;
    const x = (v, W) => 8 + ((v - lo) / (hi - lo)) * (W - 16);
    host.innerHTML = "";
    const wrap = el("div", { class: "cchart" });
    if (legendLabels) wrap.appendChild(legend([[COLOR.ink3, legendLabels.a, "dot"], [COLOR.protect, legendLabels.b, "dot"]]));
    host.appendChild(wrap);
    const rowsHost = el("div");
    wrap.appendChild(rowsHost);
    const box = rowsLayout(rowsHost, "db", rows.map((r) => ({
      label: r.label, value: I18n.iso(`${I18n.raw(r.a, digits)} → ${I18n.raw(r.b, digits)}`), tip: r.tip, r,
    })), (s, W, item) => {
      s.appendChild(svg("line", { x1: x(item.r.a, W), x2: x(item.r.b, W), y1: 11, y2: 11, stroke: COLOR.ink2, "stroke-width": 2 }));
      s.appendChild(svg("circle", { cx: x(item.r.a, W), cy: 11, r: 5, fill: COLOR.ink3, stroke: COLOR.surface, "stroke-width": 2 }));
      s.appendChild(svg("circle", { cx: x(item.r.b, W), cy: 11, r: 5, fill: COLOR.protect, stroke: COLOR.surface, "stroke-width": 2 }));
    });
    const step = (hi - lo) > 0.12 ? 0.05 : 0.02;
    const ticks = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) ticks.push({ v, label: I18n.raw(v, 2) });
    axisRow(box, ticks, x);
    return wrap;
  }

  // ------------------------------------------------------------------ entonnoir (effectifs successifs)
  /** steps = [{label, n}] : une barre par étape, proportionnelle à l'effectif (une seule série, en bleu). */
  function funnel(host, steps) {
    const max = Math.max(...steps.map((s) => s.n));
    host.innerHTML = "";
    const wrap = el("div", { class: "cchart" });
    host.appendChild(wrap);
    rowsLayout(wrap, "fn", steps.map((s) => ({ label: s.label, value: I18n.n(s.n), r: s })), (s, W, item) => {
      s.appendChild(bar(0, Math.max(2, (item.r.n / max) * W), 4, 14, COLOR.protect));
    });
    return wrap;
  }

  window.Charts = { km, effects, scores, dumbbell, funnel, kmAt, multiplier, COLOR };
})();
