/* Utilitaires communs aux pages. Les nombres suivent la langue du site (assets/js/i18n.js). */
(function () {
  "use strict";

  // Textes générés en français (frontend/data/stats.js) : même typographie que les dictionnaires
  const stats = window.SITE && window.SITE.stats;
  if (stats) {
    Object.values(stats).forEach((block) => {
      if (block && block.texts && block.texts.fr) block.texts.fr = I18n.frenchTypography(block.texts.fr);
    });
  }

  const Core = {
    /** Nombre dans la langue du site (4 233,5 · 4,233.5 ; isolé en arabe). */
    fmt(value, digits = 0) { return I18n.n(value, digits); },
    pct(value, digits = 0) { return I18n.pct(value, digits); },
    /** p-value lisible. */
    pval(p) { return I18n.pval(p); },
    clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); },
    lerp(a, b, t) { return a + (b - a) * t; },

    /** Création d'élément : el("div", {class: "x", text: "…"}, [enfants]). */
    el(tag, attrs = {}, children = []) {
      const node = document.createElement(tag);
      for (const [k, v] of Object.entries(attrs)) {
        if (v === null || v === undefined || v === false) continue;
        if (k === "class") node.className = v;
        else if (k === "text") node.textContent = v;
        else if (k === "html") node.innerHTML = v;
        else if (k === "style" && typeof v === "object") {
          for (const [prop, val] of Object.entries(v)) {
            if (prop.startsWith("--")) node.style.setProperty(prop, val);   // variables CSS
            else node.style[prop] = val;
          }
        }
        else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v === true ? "" : v);
      }
      for (const c of [].concat(children)) {
        if (c === null || c === undefined || c === false) continue;
        node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
      }
      return node;
    },
    svg(tag, attrs = {}, children = []) {
      const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
      for (const [k, v] of Object.entries(attrs)) {
        if (v === null || v === undefined) continue;
        if (k === "text") node.textContent = v;
        else node.setAttribute(k, v);
      }
      for (const c of [].concat(children)) if (c) node.appendChild(c);
      return node;
    },
    escape(text) {
      return String(text).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    },

    /** Mini rendu Markdown (gras, italique, code, listes, paragraphes, citations), sans HTML brut. */
    markdown(text) {
      const inline = (s) => Core.escape(s)
        .replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/(^|[^*])\*(?!\s)(.+?)\*(?!\*)/g, "$1<em>$2</em>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\$\\chi\^2\(([^)]*)\)\$/g, "χ²($1)")
        .replace(/\$([^$]+)\$/g, "$1");
      const out = [];
      let list = null;
      for (const raw of String(text).split("\n")) {
        const line = raw.trim();
        const item = line.match(/^[*-]\s+(.*)$/) || line.match(/^\d+\.\s+(.*)$/);
        if (item) {
          if (!list) { list = []; }
          list.push(`<li>${inline(item[1])}</li>`);
          continue;
        }
        if (list) { out.push(`<ul>${list.join("")}</ul>`); list = null; }
        if (!line) continue;
        if (line.startsWith(">")) out.push(`<blockquote>${inline(line.replace(/^>\s*/, ""))}</blockquote>`);
        else if (/^#{1,4}\s/.test(line)) out.push(`<h4>${inline(line.replace(/^#+\s*/, ""))}</h4>`);
        else out.push(`<p>${inline(line)}</p>`);
      }
      if (list) out.push(`<ul>${list.join("")}</ul>`);
      return out.join("");
    },

    /** Compteur animé (feedback cinétique) ; format(v) met en forme chaque valeur intermédiaire. */
    animateNumber(node, to, { digits = 0, duration = 900, format = null, from = null } = {}) {
      const show = format || ((v) => Core.fmt(v, digits));
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const start = from !== null ? from : parseFloat(node.dataset.value || "0") || 0;
      node.dataset.value = String(to);
      const id = (node._animId = (node._animId || 0) + 1);   // une nouvelle animation annule la précédente
      if (reduce || !Number.isFinite(to)) { node.textContent = show(to); return; }
      const t0 = performance.now();
      const step = (now) => {
        if (node._animId !== id) return;
        const t = Core.clamp((now - t0) / duration, 0, 1);
        const e = 1 - Math.pow(1 - t, 4);
        node.textContent = show(start + (to - start) * e);
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    },
    /** Arrête un compteur en cours et affiche directement un texte. */
    setText(node, text) {
      node._animId = (node._animId || 0) + 1;
      node.dataset.value = "0";
      node.textContent = text;
    },

    /** Infobulle partagée. */
    tooltip: (() => {
      let node = null;
      return {
        show(html, x, y) {
          if (!node) { node = Core.el("div", { class: "tooltip", role: "status" }); document.body.appendChild(node); }
          node.innerHTML = html;
          const w = node.offsetWidth, h = node.offsetHeight;
          const px = x + w + 30 > window.innerWidth ? x - w - 28 : x;
          const py = y + h + 30 > window.innerHeight ? y - h - 28 : y;
          node.style.left = px + "px"; node.style.top = py + "px";
          node.classList.add("on");
        },
        hide() { if (node) node.classList.remove("on"); },
      };
    })(),

    /** Barre de commande : horloge UTC et date des données. */
    initCommandBar() {
      const clock = document.getElementById("utc-clock");
      if (clock) {
        const tick = () => {
          const d = new Date();
          clock.textContent = d.toISOString().slice(11, 19) + " UTC";
        };
        tick();
        setInterval(tick, 1000);
      }
      const built = document.getElementById("data-built");
      const date = (window.SITE && (window.SITE.atlas || window.SITE.stats || {}).built) || null;
      if (built && date) built.textContent = date;
    },
  };

  window.Core = Core;
  document.addEventListener("DOMContentLoaded", () => Core.initCommandBar());
})();
