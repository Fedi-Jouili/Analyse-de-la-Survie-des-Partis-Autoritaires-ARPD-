/* Page 03 : Simulation. Le joueur compose un régime ; le modèle de Cox prédit sa durée au pouvoir.
   Deux modes : libre, et défis (paramètres imposés, objectif de durée, étoiles).
   Chaque prédiction affiche sa confiance ; dans un défi, une confiance moyenne ou faible plafonne les étoiles
   (règles et calibrage des défis : assets/js/game.js).
   Le profil, le défi et la langue tiennent dans l'adresse (#o=…&g=…), qui sert de lien de partage. */
(function () {
  "use strict";

  const { el, svg, escape } = Core;
  const t = I18n.t;
  const G = window.SITE.game;
  const D = G.model;                       // modèle exporté (src/cox_static_model.json)
  const FORM = D.form, SUP = D.support, SAMPLE = D.sample;
  const TMAX = D.model.t_max;
  const CUT = D.model.cut_years;
  const NPH = new Set(D.model.nph_covariates);
  const BETA = Object.fromEntries(D.model.features.map((f, i) => [f, D.model.coefficients[i]]));
  const REF = {
    origin: FORM.origin.reference, governance: FORM.governance.reference,
    marxist: false, conflict_entry: false,
    polity2_entry: Math.round(FORM.polity2_entry.median),
  };
  const ORIGINS = [FORM.origin.reference].concat(FORM.origin.levels.filter((o) => o !== FORM.origin.reference));
  const GOVS = FORM.governance.levels;
  const SWITCHES = [{ key: "marxist", feature: "Marxist?" }, { key: "conflict_entry", feature: "conflict_entry" }];
  const { CHALLENGES, MAX_STARS } = Game;
  // v3 : défis recalibrés sur le modèle sans la monarchie (les meilleurs scores de la v2 ne sont pas comparables)
  const STORE_KEY = "observatoire-defis-v3";

  const state = { mode: "free", challenge: null, profile: { ...REF }, horizon: Math.min(Survival.DEFAULT_HORIZON, TMAX),
                  log: [], result: null };
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const hr = (f) => Math.exp(BETA[f]);
  const hrLate = (f) => Math.exp(BETA[f] + BETA[f + "_x_late"]);
  const x2 = (v) => I18n.times(v, 2);
  const effectText = (f) => (NPH.has(f) ? I18n.iso(`×${I18n.raw(hr(f), 2)} → ×${I18n.raw(hrLate(f), 2)}`) : x2(hr(f)));
  const signed = (v) => I18n.signed(v);
  const years = (n) => t("units.years", { count: n });
  const pctRange = (lo, hi) => (I18n.lang === "fr" ? `${I18n.raw(lo)}–${I18n.raw(hi)} %` : I18n.iso(`${I18n.raw(lo)}–${I18n.raw(hi)}%`));
  const nm = (names) => (names ? names[I18n.lang] || names.fr : "");
  const locked = (key) => Boolean(state.challenge && key in state.challenge.lock);

  // ------------------------------------------------------------------ confiance de la prédiction
  const ALL = Game.profiles(FORM);
  const detailsOf = (p) => Survival.supportDetails(D, p);
  const starsLabel = (n) => t("sim.conf.stars", { count: n });
  const levelLabel = (level) => t("sim.conf.label", { level: t(`sim.conf.level.${level}`) });
  const bestOf = {};
  /** Meilleure confiance que permettent les paramètres imposés d'un défi, et ses raisons quand elle n'est pas élevée. */
  function challengeBest(ch) {
    if (!bestOf[ch.id]) {
      const b = Game.bestLevel(ch.lock, ALL, detailsOf);
      bestOf[ch.id] = { level: b.level, max: MAX_STARS[b.level], reasons: Game.confidence(detailsOf(b.profile)).reasons };
    }
    return bestOf[ch.id];
  }

  /** Raison courte d'un avertissement, avec ses chiffres (« la stratégie clientéliste repose sur 8 partis »). */
  function reasonText(d) {
    const v = d.values;
    if (d.code === "small_group") {
      const parties = t("units.parties", { count: v.n });
      if (v.variable === "origin") return t("sim.conf.reason.origin", { value: Labels.originShort(v.value), parties });
      if (v.variable === "governance") return t("sim.conf.reason.governance", { value: Labels.governance(v.value), parties });
      return t("sim.conf.reason.switch", { value: t(`sim.warn.what.${v.variable}.${v.value ? "yes" : "no"}`), parties });
    }
    if (d.code === "unseen_combination") {
      return t("sim.conf.reason.unseen", { origin: Labels.originShort(v.origin), governance: Labels.governanceShort(v.governance) });
    }
    if (d.code === "polity_outside_range") {
      return t("sim.conf.reason.polity", { value: signed(v.value), range: I18n.rangeN(v.p05, v.p95, 1) });
    }
    return d.code;
  }
  const reasonsText = (reasons) => reasons.map(reasonText).join(t("common.listSep"));

  /** Icône de confiance : trois barres, autant de pleines que le niveau (la couleur de statut n'est jamais seule). */
  function confIcon(level) {
    const filled = Game.LEVELS.indexOf(level) + 1;
    return svg("svg", { class: "conf-icon", viewBox: "0 0 14 12", "aria-hidden": "true" }, [0, 1, 2].map((i) =>
      svg("rect", { x: i * 5 + 0.5, y: 8.5 - i * 4, width: 3, height: 3 + i * 4, class: i < filled ? "on" : "off" })));
  }
  const confTag = (level, extra = "") => el("span", { class: `conf conf-${level}${extra ? " " + extra : ""}` },
    [confIcon(level), el("span", { class: "conf-text", text: levelLabel(level) })]);

  /** Infobulle de la confiance : ses raisons, ou ce qui la rend élevée. */
  function confTip(level, reasons) {
    const pol = FORM.polity2_entry;
    const lines = level === "high"
      ? [t("sim.conf.tipHigh", { parties: t("units.parties", { count: Survival.MIN_SPELLS }), range: I18n.rangeN(pol.p05, pol.p95, 1) })]
      : reasons.map((d) => I18n.cap(reasonText(d)) + t("common.period"))
          .concat([t("sim.conf.tipLimit", { stars: starsLabel(MAX_STARS[level]) })]);
    return { html: `<div class="t-head">${escape(levelLabel(level))}</div>` + lines.map(escape).join("<br>"), text: lines.join(" ") };
  }

  /** Confiance à côté de la médiane : survol ou focus pour les raisons ; clic pour la fiabilité détaillée. */
  function renderConfidence(res) {
    const box = document.getElementById("confidence");
    const { level, reasons } = Game.confidence(res.warning_details);
    const tip = confTip(level, reasons);
    const btn = el("button", { type: "button", class: "conf-btn", "aria-describedby": "conf-why" }, confTag(level));
    const show = (x, y) => Core.tooltip.show(tip.html, x, y);
    btn.addEventListener("mousemove", (e) => show(e.clientX, e.clientY));
    btn.addEventListener("mouseleave", () => Core.tooltip.hide());
    btn.addEventListener("focus", () => { const r = btn.getBoundingClientRect(); show(r.left, r.bottom); });
    btn.addEventListener("blur", () => Core.tooltip.hide());
    btn.addEventListener("click", () => {
      const panel = document.getElementById("warnings-panel");
      if (level === "high" || panel.hidden) return;
      Core.tooltip.hide();
      panel.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
    });
    box.innerHTML = "";
    box.appendChild(btn);
    box.appendChild(el("span", { id: "conf-why", class: "sr-only", text: tip.text }));
  }

  // ------------------------------------------------------------------ meilleurs scores (navigateur)
  function loadBest() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY) || "{}") || {}; } catch (e) { return {}; }
  }
  function saveBest(id, stars, p) {
    const best = loadBest();
    if (!best[id] || stars > best[id].stars || (stars === best[id].stars && p > best[id].p)) {
      best[id] = { stars, p: Math.round(p * 1000) / 1000 };
      try { localStorage.setItem(STORE_KEY, JSON.stringify(best)); } catch (e) { /* sans stockage : score non conservé */ }
    }
  }

  // ------------------------------------------------------------------ adresse = lien de partage
  function encodeState() {
    const p = state.profile;
    const q = new URLSearchParams({ o: p.origin, g: p.governance, m: Number(p.marxist),
                                    c: Number(p.conflict_entry), p: p.polity2_entry, h: state.horizon });
    if (state.challenge) q.set("d", state.challenge.id);
    q.set("lang", I18n.lang);
    return q.toString();
  }
  function writeHash() {
    const hash = "#" + encodeState();
    if (location.hash === hash) return;
    try { history.replaceState(history.state, "", hash); } catch (e) { location.replace(hash); }
  }
  function readHash() {
    const q = new URLSearchParams(location.hash.slice(1));
    if (![...q.keys()].length) return;
    const p = { ...REF };
    if (FORM.origin.levels.includes(q.get("o"))) p.origin = q.get("o");
    if (GOVS.includes(q.get("g"))) p.governance = q.get("g");
    for (const [key, k] of [["marxist", "m"], ["conflict_entry", "c"]]) {
      if (q.has(k)) p[key] = q.get(k) === "1";
    }
    const pol = Number(q.get("p"));
    if (q.has("p") && Number.isInteger(pol) && pol >= -10 && pol <= 10) p.polity2_entry = pol;
    const h = Number(q.get("h"));
    if (Number.isInteger(h) && h >= 10 && h <= TMAX) state.horizon = h;
    const ch = CHALLENGES.find((c) => c.id === q.get("d"));
    state.profile = p;
    if (ch) {
      state.mode = "challenge";
      state.challenge = ch;
      Object.assign(state.profile, ch.lock);
      state.horizon = Math.max(state.horizon, ch.target);
    }
  }

  // ------------------------------------------------------------------ commandes
  const originBox = document.getElementById("origin-tiles");
  const govBox = document.getElementById("gov-tiles");
  const switchBox = document.getElementById("switches");
  const polity = document.getElementById("polity");
  const horizon = document.getElementById("horizon");

  function tile(group, value, title, n, effect, isRef) {
    const isLocked = locked(group);
    const b = el("button", { class: "tile" + (isRef ? " ref" : "") + (isLocked ? " locked" : ""), type: "button", role: "radio",
                             "aria-checked": String(state.profile[group] === value), "data-value": value,
                             disabled: isLocked && state.profile[group] !== value ? true : null,
                             "aria-disabled": isLocked ? "true" : null }, [
      el("span", { class: "t" }, [title, isRef ? el("span", { class: "ref-tag", text: t("sim.refTag") }) : null,
                                  isLocked && state.profile[group] === value ? el("span", { class: "lock", "aria-label": t("sim.lockedAria"), text: "🔒" }) : null]),
      el("span", { class: "m" }, [el("span", { text: t("units.parties", { count: n }) }), el("span", { class: "hr", text: isRef ? "" : effect })]),
    ]);
    b.addEventListener("click", () => {
      if (locked(group)) return;
      state.profile[group] = value;
      b.parentNode.querySelectorAll(".tile").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
      update();
    });
    return b;
  }

  function buildControls() {
    originBox.innerHTML = "";
    ORIGINS.forEach((o) => originBox.appendChild(tile("origin", o, Labels.originShort(o), SUP.origin[o],
      effectText("Origin_" + o), o === FORM.origin.reference)));
    govBox.innerHTML = "";
    GOVS.forEach((g) => govBox.appendChild(tile("governance", g, Labels.governanceShort(g), SUP.governance[g],
      g === FORM.governance.reference ? "" : effectText("Gov_" + g), g === FORM.governance.reference)));
    switchBox.innerHTML = "";
    SWITCHES.forEach((s) => {
      const isLocked = locked(s.key);
      const input = el("input", { type: "checkbox", id: `sw-${s.key}`, disabled: isLocked ? true : null });
      input.checked = state.profile[s.key];
      input.addEventListener("change", () => { state.profile[s.key] = input.checked; update(); });
      const meta = t("sim.switchMeta", { parties: t("units.parties", { count: SUP[s.key].true }), effect: effectText(s.feature) }) +
        (NPH.has(s.feature) ? " " + t("sim.afterCut", { cut: years(CUT) }) : "");
      switchBox.appendChild(el("div", { class: "switch-row" + (isLocked ? " locked" : "") }, [
        el("label", { class: "info", for: `sw-${s.key}` }, [t(`sim.switch.${s.key}`),
          isLocked ? el("span", { class: "lock", "aria-label": t("sim.lockedAria"), text: " 🔒" }) : null,
          el("small", { text: meta })]),
        el("label", { class: "toggle", "aria-label": t(`sim.switch.${s.key}`) }, [input, el("span", { class: "track", "aria-hidden": "true" })]),
      ]));
    });
    const pol = FORM.polity2_entry;
    polity.disabled = locked("polity2_entry");
    document.getElementById("polity-field").classList.toggle("locked", locked("polity2_entry"));
    const band = document.getElementById("polity-band");
    band.style.left = `${((pol.p05 + 10) / 20) * 100}%`;
    band.style.width = `${((pol.p95 - pol.p05) / 20) * 100}%`;
    document.getElementById("polity-help").textContent =
      t("sim.polityHelp", { range: I18n.rangeN(pol.p05, pol.p95, 1), effect: x2(hr("polity2_entry")) }) +
      (locked("polity2_entry") ? " " + t("sim.lockedNote") : "");
    horizon.max = TMAX;
    horizon.min = state.challenge ? state.challenge.target : 10;
    syncControls();
  }
  polity.addEventListener("input", () => { state.profile.polity2_entry = Number(polity.value); update(); });
  horizon.addEventListener("input", () => { state.horizon = Number(horizon.value); update(); });

  function syncControls() {
    originBox.querySelectorAll(".tile").forEach((x) => x.setAttribute("aria-checked", String(x.dataset.value === state.profile.origin)));
    govBox.querySelectorAll(".tile").forEach((x) => x.setAttribute("aria-checked", String(x.dataset.value === state.profile.governance)));
    SWITCHES.forEach((s) => { document.getElementById(`sw-${s.key}`).checked = state.profile[s.key]; });
    polity.value = state.profile.polity2_entry;
    polity.setAttribute("aria-valuetext", signed(state.profile.polity2_entry));
    horizon.value = state.horizon;
    horizon.setAttribute("aria-valuetext", years(state.horizon));
  }

  document.getElementById("reset").addEventListener("click", () => {
    state.profile = { ...REF, ...(state.challenge ? state.challenge.lock : {}) };
    syncControls();
    update();
  });

  // ------------------------------------------------------------------ modes et défis
  const modeSeg = document.getElementById("mode-seg");
  const challengeBox = document.getElementById("challenges");
  const challengeCard = document.getElementById("challenge-card");

  function lockText(ch) {
    return Object.entries(ch.lock).map(([k, v]) => {
      if (k === "origin") return t("sim.ch.lockOrigin", { value: Labels.originShort(v) });
      if (k === "governance") return t("sim.ch.lockGov", { value: Labels.governanceShort(v) });
      if (k === "polity2_entry") return t("sim.ch.lockPolity", { value: signed(v) });
      return t(`sim.switch.${k}`);
    }).join(" · ");
  }
  const starText = (n) => "★".repeat(n) + "☆".repeat(3 - n);

  function renderChallenges() {
    modeSeg.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === state.mode)));
    challengeBox.hidden = state.mode !== "challenge";
    challengeBox.innerHTML = "";
    if (state.mode !== "challenge") return;
    const best = loadBest();
    challengeBox.appendChild(el("p", { class: "note", text: t("sim.ch.intro") }));
    challengeBox.appendChild(el("p", { class: "note", text: t("sim.conf.rule", {
      medium: starsLabel(MAX_STARS.medium), low: starsLabel(MAX_STARS.low) }) }));
    const list = el("div", { class: "challenge-list", role: "radiogroup", "aria-label": t("sim.modeChallenge") });
    CHALLENGES.forEach((ch) => {
      const b = best[ch.id];
      const top = challengeBest(ch);
      const card = el("button", { type: "button", class: "challenge", role: "radio",
                                  "aria-checked": String(state.challenge === ch) }, [
        el("span", { class: "ch-title", text: t(`sim.challenges.${ch.id}.title`) }),
        el("span", { class: "ch-target", text: t("sim.ch.target", { years: years(ch.target) }) }),
        el("span", { class: "ch-lock", text: lockText(ch) + (top.max < 3
          ? " · " + t("sim.conf.challengeMaxShort", { stars: starsLabel(top.max) }) : "") }),
        el("span", { class: "ch-best", "aria-label": b ? t("sim.ch.bestAria", { count: b.stars }) : t("sim.ch.notPlayed"),
                     text: b ? starText(b.stars) : "☆☆☆" }),
      ]);
      card.addEventListener("click", () => startChallenge(ch));
      list.appendChild(card);
    });
    challengeBox.appendChild(list);
  }
  function setMode(mode) {
    state.mode = mode;
    state.result = null;
    if (mode === "free") {
      state.challenge = null;
    } else if (!state.challenge) {
      startChallenge(CHALLENGES[0]);
      return;
    }
    refreshAll();
  }
  function startChallenge(ch) {
    state.mode = "challenge";
    state.challenge = ch;
    state.result = null;
    state.profile = { ...REF, ...ch.lock };
    state.horizon = Math.min(TMAX, Math.max(30, ch.target));
    refreshAll();
  }
  modeSeg.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => setMode(b.dataset.mode)));

  function renderChallengeCard() {
    const ch = state.challenge;
    challengeCard.hidden = !ch;
    challengeCard.innerHTML = "";
    if (!ch) return;
    const head = el("div", { class: "panel-head" }, [
      el("h3", { class: "label", text: t("sim.ch.cardLabel") }),
      el("span", { class: "mono dim", text: t("sim.ch.starsRule", { a: Core.pct(ch.stars[0] * 100), b: Core.pct(ch.stars[1] * 100),
                                                                    c: Core.pct(ch.stars[2] * 100) }) })]);
    const body = el("div", { class: "panel-body ch-body" });
    body.appendChild(el("div", { class: "ch-name", text: t(`sim.challenges.${ch.id}.title`) }));
    body.appendChild(el("p", { class: "ch-brief", text: t(`sim.challenges.${ch.id}.brief`) }));
    body.appendChild(el("p", { class: "ch-goal", text: t("sim.ch.goal", { years: years(ch.target) }) }));
    const top = challengeBest(ch);
    if (top.max < 3) {
      body.appendChild(el("p", { class: "ch-cap-note", text: t("sim.conf.challengeMax", {
        stars: starsLabel(top.max), reasons: reasonsText(top.reasons) }) }));
    }
    const r = state.result;
    if (r && r.id === ch.id) {
      // Pas de piste quand le défi a donné tout ce qu'il peut donner (coup d'État : 2 étoiles au plus)
      const hint = r.stars >= top.max ? null : r.capped ? "sim.ch.hintCapped" : r.stars ? "sim.ch.hintMore" : "sim.ch.hint";
      const res = el("div", { class: "ch-result " + (r.stars ? "won" : "lost") }, [
        el("div", { class: "ch-verdict" }, [
          el("span", { class: "stars", "aria-hidden": "true", text: starText(r.stars) }),
          el("strong", { text: r.stars ? t("sim.ch.won", { count: r.stars }) : t("sim.ch.lost") }),
          confTag(r.level, "small")]),
        r.capped ? el("p", { class: "ch-capped", text: t("sim.conf.capped", {
          possible: t("sim.conf.possible", { count: r.earned }), limit: t("sim.conf.limit", { count: r.stars }),
          reasons: reasonsText(r.reasons) }) }) : null,
        el("p", { text: t("sim.ch.prob", { years: years(ch.target), p: Core.pct(r.p * 100), range: pctRange(r.lo * 100, r.hi * 100) }) }),
        el("p", { text: t("sim.ch.history", { pct: Core.pct(r.km * 100), years: years(ch.target) }) }),
        r.median !== null ? el("p", { text: t("sim.ch.medianRank", { median: years(r.median), pct: Core.pct(r.beat * 100) }) }) : null,
        hint ? el("p", { class: "note", text: t(hint) }) : null,
      ]);
      body.appendChild(res);
    } else {
      body.appendChild(el("p", { class: "note", text: t("sim.ch.howTo") }));
    }
    challengeCard.appendChild(head);
    challengeCard.appendChild(body);
  }

  // ------------------------------------------------------------------ calculs auxiliaires
  const KM = G.km_overall.curve;
  const kmAt = (v) => { let s = 1; for (let i = 0; i < KM.t.length && KM.t[i] <= v; i++) s = KM.s[i]; return s; };
  const crossing = (curve) => { const i = curve.findIndex((s) => s <= 0.5); return i >= 0 ? i : null; };
  const profileText = (p) => [Labels.originShort(p.origin), Labels.governanceShort(p.governance),
    p.marxist ? t("sim.short.marxist") : null,
    p.conflict_entry ? t("sim.short.conflict") : null, `Polity2 ${signed(p.polity2_entry)}`].filter(Boolean).join(" · ");

  // ------------------------------------------------------------------ rendu
  function renderHero(res, animate) {
    const valueNode = document.getElementById("median-value");
    const unit = document.getElementById("median-unit");
    const sub = document.getElementById("median-sub");
    const lowT = crossing(res.band.lower), highT = crossing(res.band.upper);
    if (res.median.reached) {
      Core.animateNumber(valueNode, res.median.years, { duration: animate ? 1400 : 450, from: animate ? 0 : null });
      unit.textContent = t("units.yearsWord", { count: res.median.years });
    } else {
      Core.setText(valueNode, I18n.iso(`> ${res.horizon_used}`));
      unit.textContent = t("units.yearsWord", { count: res.horizon_used });
    }
    const medianText = res.median.reached ? t("sim.medianReached", { years: years(res.median.years) })
                                          : t("sim.medianNotReached", { years: years(res.horizon_used) });
    const bandText = lowT === null ? t("sim.bandBeyond", { years: years(res.horizon_used) })
      : highT === null ? t("sim.bandOpen", { low: years(lowT), years: years(res.horizon_used) })
      : t("sim.bandRange", { range: I18n.range(lowT, highT), unit: t("units.yearsWord", { count: highT }) });
    sub.textContent = `${medianText} ${bandText}`;
    const probs = document.getElementById("probs");
    probs.innerHTML = "";
    [5, 10, 20, 30].map((v) => Math.min(v, res.horizon_used)).filter((v, i, a) => a.indexOf(v) === i).forEach((v) => {
      const s = res.survival[v], lo = res.band.lower[v], hi = res.band.upper[v];
      const meter = el("div", { class: "meter", dir: "ltr" }, [el("s", { style: { left: `${lo * 100}%`, width: `${(hi - lo) * 100}%` } }),
                                                              el("i", { style: { width: "0%" } })]);
      probs.appendChild(el("div", { class: "prob" }, [
        el("span", { class: "label", text: t("sim.atYears", { years: years(v) }) }),
        el("span", { class: "v", text: Core.pct(s * 100) }),
        el("span", { class: "b", text: pctRange(lo * 100, hi * 100) }), meter]));
      requestAnimationFrame(() => { meter.querySelector("i").style.width = `${s * 100}%`; });
    });
  }

  function renderCurve(res, animate) {
    const host = document.getElementById("curve");
    const W = Math.max(host.clientWidth, 300), H = W < 480 ? 260 : 330;
    const m = { l: 40, r: 16, t: 14, b: 30 };
    const T = res.horizon_used;
    const x = (v) => m.l + (v / T) * (W - m.l - m.r);
    const y = (v) => m.t + (1 - v) * (H - m.t - m.b);
    const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, height: H, role: "img", "aria-label": t("sim.chart.aria", { years: years(T) }) });
    [0, 0.25, 0.5, 0.75, 1].forEach((v) => {
      root.appendChild(svg("line", { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), stroke: v === 0.5 ? "rgba(148,163,184,.3)" : "rgba(148,163,184,.12)",
                                     "stroke-dasharray": v === 0.5 ? "2 4" : null }));
      root.appendChild(svg("text", { x: m.l - 8, y: y(v) + 3.5, "text-anchor": "end", text: `${I18n.raw(v * 100)}%` }));
    });
    const step = T > 40 ? 10 : 5;
    const ticks = [];
    for (let v = 0; v <= T; v += step) ticks.push(v);
    if (T - ticks[ticks.length - 1] < step / 2) ticks.pop();       // évite deux graduations collées
    ticks.push(T);
    ticks.forEach((v, i) => root.appendChild(svg("text", { x: x(v), y: H - 10, "text-anchor": i === ticks.length - 1 ? "end" : "middle",
                                                          text: i === ticks.length - 1 ? I18n.svgLabel(years(v)) : String(v) })));
    if (CUT < T) {
      root.appendChild(svg("line", { x1: x(CUT), x2: x(CUT), y1: m.t, y2: H - m.b, stroke: "rgba(148,163,184,.28)", "stroke-dasharray": "3 4" }));
      root.appendChild(svg("text", { x: x(CUT) + 6, y: m.t + 10, class: "halo", text: I18n.svgLabel(t("sim.chart.cut", { years: years(CUT) })) }));
    }
    const target = state.challenge ? state.challenge.target : null;
    if (target !== null && target <= T) {
      root.appendChild(svg("line", { x1: x(target), x2: x(target), y1: m.t, y2: H - m.b, stroke: "rgba(250,178,25,.55)", "stroke-dasharray": "5 3" }));
      root.appendChild(svg("text", { x: x(target) - 6, y: H - m.b - 8, "text-anchor": "end", class: "halo target-label",
                                     text: I18n.svgLabel(t("sim.chart.target", { years: years(target) })) }));
    }
    // bande bootstrap
    let d = `M${x(0)},${y(res.band.upper[0])}`;
    for (let v = 1; v <= T; v++) d += `L${x(v).toFixed(1)},${y(res.band.upper[v]).toFixed(1)}`;
    for (let v = T; v >= 0; v--) d += `L${x(v).toFixed(1)},${y(res.band.lower[v]).toFixed(1)}`;
    root.appendChild(svg("path", { d: d + "Z", fill: "rgba(233,237,242,0.12)" }));
    // historique (Kaplan-Meier, tous les partis) et profil de référence
    let km = `M${x(0)},${y(1)}`;
    for (let i = 1; i < KM.t.length && KM.t[i] <= T; i++) km += `H${x(KM.t[i]).toFixed(1)}V${y(KM.s[i]).toFixed(1)}`;
    km += `H${x(T)}`;
    root.appendChild(svg("path", { d: km, fill: "none", stroke: "#6f7a8a", "stroke-width": 1.4, "stroke-dasharray": "4 4" }));
    const isRef = JSON.stringify(state.profile) === JSON.stringify(REF);
    const ref = Survival.predict(D, REF, T);
    if (!isRef) {
      root.appendChild(svg("path", { d: ref.survival.map((s, v) => `${v ? "L" : "M"}${x(v).toFixed(1)},${y(s).toFixed(1)}`).join(""),
                                     fill: "none", stroke: "#454e5b", "stroke-width": 1.5 }));
    }
    const main = svg("path", { d: res.survival.map((s, v) => `${v ? "L" : "M"}${x(v).toFixed(1)},${y(s).toFixed(1)}`).join(""),
                               fill: "none", stroke: "#e9edf2", "stroke-width": 2.2, "stroke-linejoin": "round",
                               style: "filter: drop-shadow(0 0 6px rgba(233,237,242,.35))" });
    root.appendChild(main);
    if (res.median.reached) {
      const tm = res.median.years;
      root.appendChild(svg("line", { x1: x(tm), x2: x(tm), y1: y(0.5), y2: H - m.b, stroke: "#e9edf2", "stroke-dasharray": "2 3", opacity: 0.7 }));
      root.appendChild(svg("circle", { cx: x(tm), cy: y(0.5), r: 4, fill: "#04060a", stroke: "#e9edf2", "stroke-width": 1.5 }));
      root.appendChild(svg("text", { x: x(tm) + 8, y: y(0.5) - 8, class: "halo", fill: "#e9edf2", text: I18n.svgLabel(t("sim.chart.median", { years: years(tm) })) }));
    }
    // réticule
    const cross = svg("line", { y1: m.t, y2: H - m.b, stroke: "rgba(233,237,242,.5)", visibility: "hidden" });
    const dot = svg("circle", { r: 3.5, fill: "#e9edf2", visibility: "hidden" });
    root.appendChild(cross); root.appendChild(dot);
    const hit = svg("rect", { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent" });
    hit.addEventListener("mousemove", (e) => {
      const r = root.getBoundingClientRect();
      const v = Core.clamp(Math.round((((e.clientX - r.left) * (W / r.width)) - m.l) / (W - m.l - m.r) * T), 0, T);
      cross.setAttribute("x1", x(v)); cross.setAttribute("x2", x(v)); cross.setAttribute("visibility", "visible");
      dot.setAttribute("cx", x(v)); dot.setAttribute("cy", y(res.survival[v])); dot.setAttribute("visibility", "visible");
      Core.tooltip.show(`<div class="t-head">${escape(t("sim.chart.tipHead", { years: years(v) }))}</div>` +
        escape(t("sim.chart.tipYours", { pct: Core.pct(res.survival[v] * 100), range: pctRange(res.band.lower[v] * 100, res.band.upper[v] * 100) })) + "<br>" +
        (isRef ? "" : escape(t("sim.chart.tipRef", { pct: Core.pct(ref.survival[v] * 100) })) + "<br>") +
        escape(t("sim.chart.tipHistory", { pct: Core.pct(kmAt(v) * 100) })), e.clientX, e.clientY);
    });
    hit.addEventListener("mouseleave", () => { cross.setAttribute("visibility", "hidden"); dot.setAttribute("visibility", "hidden"); Core.tooltip.hide(); });
    root.appendChild(hit);
    host.innerHTML = "";
    host.appendChild(root);
    if (animate && !reduceMotion) {
      const len = main.getTotalLength();
      main.style.strokeDasharray = `${len}`;
      main.style.strokeDashoffset = `${len}`;
      main.getBoundingClientRect();
      main.style.transition = "stroke-dashoffset 1.4s cubic-bezier(0.2, 0.7, 0.1, 1)";
      main.style.strokeDashoffset = "0";
    }
    const legend = document.getElementById("chart-legend");
    legend.innerHTML = "";
    [["", "sim.legend.yours"], ["band", "sim.legend.band"], isRef ? null : ["ref", "sim.legend.ref"],
     ["dash", "sim.legend.history"], target !== null ? ["target", "sim.legend.target"] : null].filter(Boolean).forEach(([cls, key]) => {
      legend.appendChild(el("span", {}, [el("i", { class: cls }), t(key, { count: G.sample_all.spells })]));
    });
  }

  const activeLevers = () => Survival.levers(D, state.profile).filter((lv) => lv.label !== "polity2" || lv.delta !== 0).length;

  function renderLevers() {
    const box = document.getElementById("levers");
    box.innerHTML = "";
    const levers = Survival.levers(D, state.profile);
    const DOMAIN = [Math.log(0.15), Math.log(6.5)];
    const pos = (v) => Core.clamp(((Math.log(v) - DOMAIN[0]) / (DOMAIN[1] - DOMAIN[0])) * 100, 0, 100);
    const p = state.profile;
    const nameOf = (lv) => ({
      origin: [t("sim.lever.origin", { value: Labels.originShort(p.origin) }), t("sim.lever.vs", { value: Labels.originShort(FORM.origin.reference) })],
      governance: [t("sim.lever.governance", { value: Labels.governanceShort(p.governance) }), t("sim.lever.vs", { value: Labels.governanceShort(FORM.governance.reference) })],
      marxist: [t("sim.switch.marxist"), t("sim.lever.vsNo")],
      conflict_entry: [t("sim.switch.conflict_entry"), t("sim.lever.vsNoConflict")],
      polity2: [`Polity2 ${signed(p.polity2_entry)}`, t("sim.lever.vsMedian", { value: signed(FORM.polity2_entry.median) })],
    }[lv.label]);
    let early = 1, late = 1;
    levers.forEach((lv) => {
      early *= lv.early; late *= lv.late === null ? lv.early : lv.late;
      const [name, vs] = nameOf(lv);
      const bar = svg("svg", { "aria-hidden": "true" }, [
        svg("line", { x1: `${pos(1)}%`, x2: `${pos(1)}%`, y1: 2, y2: 20, stroke: "rgba(148,163,184,.4)" }),
        svg("line", { x1: `${pos(1)}%`, x2: `${pos(lv.early)}%`, y1: lv.late === null ? 11 : 7, y2: lv.late === null ? 11 : 7,
                      stroke: "#e9edf2", "stroke-width": 3 }),
        lv.late === null ? null : svg("line", { x1: `${pos(1)}%`, x2: `${pos(lv.late)}%`, y1: 15, y2: 15, stroke: "#6f7a8a", "stroke-width": 3 }),
      ]);
      box.appendChild(el("div", { class: "lever" }, [
        el("span", { class: "name" }, [name, el("small", { text: vs })]),
        el("span", { class: "lever-bar", dir: "ltr" }, bar),
        el("span", { class: "val" }, [x2(lv.early), lv.late === null ? null :
          el("small", { text: t("sim.lever.late", { cut: years(CUT), value: x2(lv.late) }) })]),
      ]));
    });
    if (activeLevers() === 0) {
      box.appendChild(el("p", { class: "note", style: { marginTop: "10px" }, text: t("sim.lever.refNote") }));
      return;
    }
    box.appendChild(el("p", { class: "note", style: { marginTop: "10px" }, html: I18n.tHtml("sim.lever.combined", {
      early: I18n.html(`<strong>${escape(x2(early))}</strong>`), late: I18n.html(`<strong>${escape(x2(late))}</strong>`),
      cut: CUT }) }));
  }

  const rankBig = el("div", { class: "rank-big" });
  function renderRank(res) {
    const box = document.getElementById("rank");
    const v = res.median.reached ? res.median.years : res.horizon_used;
    const before = (1 - kmAt(v)) * 100;
    box.innerHTML = "";
    box.appendChild(el("span", { class: "label", text: t("sim.rank.label") }));
    box.appendChild(rankBig);
    Core.animateNumber(rankBig, Math.round(before), { duration: 700, format: (n) => Core.pct(n) });
    box.appendChild(el("p", { class: "rank-text", text: res.median.reached
      ? t("sim.rank.reached", { count: G.sample_all.spells, pct: Core.pct(before), years: years(v) })
      : t("sim.rank.notReached", { years: years(v), pct: Core.pct(before) }) }));
    // nuage des durées observées (spells du modèle)
    const W = 400, H = 56;
    const maxD = Math.max(...G.analogs.map((a) => a.duration));
    const xs = (dd) => 4 + (dd / maxD) * (W - 8);
    const plot = svg("svg", { class: "strip-plot", viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: "none", role: "img",
                               "aria-label": t("sim.rank.plotAria") });
    G.analogs.forEach((a, i) => {
      const yy = 8 + ((i * 37) % 31);
      plot.appendChild(svg("circle", { cx: xs(a.duration), cy: yy, r: 2, fill: a.event ? "#6f7a8a" : "none", stroke: "#6f7a8a", "stroke-width": 0.8 }));
    });
    plot.appendChild(svg("line", { x1: xs(v), x2: xs(v), y1: 0, y2: H - 10, stroke: "#e9edf2", "stroke-width": 1.5 }));
    const nearEnd = xs(v) > W * 0.6;
    plot.appendChild(svg("text", { x: nearEnd ? xs(v) - 4 : xs(v) + 4, y: H - 1, "text-anchor": nearEnd ? "end" : "start", fill: "#e9edf2",
                                   "font-size": 10, class: "plot-label",
                                   text: I18n.svgLabel(res.median.reached ? t("sim.rank.yourMedian", { years: years(v) }) : I18n.iso(`> ${years(v)}`)) }));
    box.appendChild(el("div", { class: "strip-box", dir: "ltr" }, plot));
    box.appendChild(el("p", { class: "note", text: t("sim.rank.note", { year: SAMPLE.observation_end_year }) }));
  }

  function warningText(d) {
    const v = d.values;
    if (d.code === "small_group") {
      const what = v.variable === "origin" ? t("sim.warn.whatOrigin", { value: Labels.originShort(v.value) })
        : v.variable === "governance" ? t("sim.warn.whatGov", { value: Labels.governanceShort(v.value) })
        : t(`sim.warn.what.${v.variable}.${v.value ? "yes" : "no"}`);
      return t("sim.warn.smallGroup", { n: I18n.n(v.n), what, threshold: I18n.n(v.threshold) });
    }
    if (d.code === "unseen_combination") {
      return t("sim.warn.unseen", { origin: Labels.originShort(v.origin), governance: Labels.governanceShort(v.governance), coded: I18n.n(v.coded) });
    }
    if (d.code === "polity_outside_range") {
      return t("sim.warn.polity", { value: signed(v.value), range: I18n.rangeN(v.p05, v.p95, 1) });
    }
    if (d.code === "horizon_capped") return t("sim.warn.horizon", { requested: years(v.requested), used: years(v.used) });
    return d.code;
  }
  function renderWarnings(res) {
    const panel = document.getElementById("warnings-panel");
    const box = document.getElementById("warnings");
    const items = res.note_details.concat(res.warning_details);
    panel.hidden = items.length === 0;
    box.innerHTML = "";
    items.forEach((d) => box.appendChild(el("div", { class: "warning-box", text: warningText(d) })));
  }

  function renderAnalogs() {
    const box = document.getElementById("analogs");
    const feats = G.analog_features;
    const idx = (f) => feats.indexOf(f);
    const p = state.profile;
    const scored = G.analogs.map((a) => {
      const x = a.x;
      const origin = feats.filter((f) => f.startsWith("Origin_")).find((f) => x[idx(f)] === 1);
      const aOrigin = origin ? origin.slice(7) : FORM.origin.reference;
      const notCoded = x[idx("Gov_Non code")] === 1;
      const gov = notCoded ? null : (["Gov_Repressive", "Gov_Clientelist"].find((f) => x[idx(f)] === 1) || "Gov_" + FORM.governance.reference).slice(4);
      const dist = (aOrigin === p.origin ? 0 : 3) + (gov === null ? 1 : gov === p.governance ? 0 : 2) +
        (x[idx("Marxist?")] === Number(p.marxist) ? 0 : 1) +
        (x[idx("conflict_entry")] === Number(p.conflict_entry) ? 0 : 1) + Math.abs(x[idx("polity2_entry")] - p.polity2_entry) / 5;
      return { a, dist, gov };
    }).sort((u, v) => u.dist - v.dist || v.a.duration - u.a.duration).slice(0, 6);
    document.getElementById("analog-count").textContent = t("sim.analog.count", { count: G.analogs.length });
    box.innerHTML = "";
    scored.forEach(({ a, gov }) => {
      const link = a.poly ? el("a", { href: I18n.href(`atlas.html#pays=${encodeURIComponent(a.poly)}&annee=${Math.max(a.start, 1946)}`),
                                      text: t("sim.analog.atlas") }) : null;
      box.appendChild(el("div", { class: "analog" }, [
        el("span", { class: "who" }, [nm(a.label), el("small", {}, [el("bdi", { text: a.party }), " · ",
          I18n.range(a.start, a.ongoing ? "…" : a.end), gov === null ? " · " + t("sim.analog.notCoded") : ""])]),
        el("span", { class: "dur" }, [years(a.duration),
          el("small", { text: a.event ? t("sim.analog.fell", { year: a.end }) : t("sim.analog.still") }), link]),
      ]));
    });
    box.appendChild(el("p", { class: "note", style: { marginTop: "8px" }, text: t("sim.analog.note") }));
  }

  function spark(curve, w = 80, h = 22) {
    const T = curve.length - 1;
    return svg("svg", { viewBox: `0 0 ${w} ${h}`, "aria-hidden": "true" }, [
      svg("path", { d: curve.map((s, v) => `${v ? "L" : "M"}${((v / T) * w).toFixed(1)},${(2 + (1 - s) * (h - 4)).toFixed(1)}`).join(""),
                    fill: "none", stroke: "#aab4c1", "stroke-width": 1.2 })]);
  }
  function renderLog() {
    const box = document.getElementById("log");
    box.innerHTML = "";
    if (!state.log.length) {
      box.appendChild(el("p", { class: "note", text: t("sim.log.empty") }));
      return;
    }
    const score = (r) => (r.median === null ? 1e6 + r.sLast : r.median);
    const best = state.log.reduce((b, r) => (score(r) > score(b) ? r : b), state.log[0]);
    state.log.slice().reverse().forEach((r) => {
      const ch = r.challenge ? CHALLENGES.find((c) => c.id === r.challenge) : null;
      const row = el("button", { class: "log-row" + (r === best && state.log.length > 1 ? " best" : ""), type: "button",
                                 title: t("sim.log.reload") }, [
        el("span", { class: "n", text: String(r.n).padStart(2, "0") }),
        el("span", {}, [ch ? el("strong", { text: t(`sim.challenges.${ch.id}.title`) + " · " + starText(r.stars) + " — " }) : null,
                        profileText(r.profile), confTag(r.level, "mini")]),
        el("span", { class: "spark-box", dir: "ltr" }, spark(r.curve)),
        el("span", { class: "m", text: r.median === null ? I18n.iso(`> ${r.horizon}`) : years(r.median) }),
      ]);
      row.addEventListener("click", () => {
        const target = ch || null;
        state.mode = target ? "challenge" : "free";
        state.challenge = target;
        state.result = null;
        state.profile = { ...r.profile };
        state.horizon = r.horizon;
        refreshAll({ animate: true });
      });
      box.appendChild(row);
    });
  }

  function renderStatic() {
    document.getElementById("sim-lead").textContent = t("sim.lead", {
      parties: t("units.parties", { count: SAMPLE.spells }), countries: t("units.countries", { count: SAMPLE.countries }),
      falls: t("units.falls", { count: SAMPLE.events }), from: SAMPLE.first_year_in_power, to: SAMPLE.observation_end_year });
    document.getElementById("model-info").textContent = t("sim.modelInfo", { count: D.bootstrap.replicates });
    document.getElementById("disclaimer").textContent = t("sim.disclaimer", {
      replicates: I18n.n(D.bootstrap.replicates), from: SAMPLE.first_year_in_power, to: SAMPLE.observation_end_year,
      cindex: I18n.n(D.performance.c_index_cv.mean, 2) });
    document.getElementById("run").textContent = t(state.challenge ? "sim.submit" : "sim.run");
  }

  function update({ animate = false } = {}) {
    const res = Survival.predict(D, state.profile, state.horizon);
    document.getElementById("horizon-value").textContent = years(state.horizon);
    document.getElementById("polity-value").textContent = signed(state.profile.polity2_entry);
    polity.setAttribute("aria-valuetext", signed(state.profile.polity2_entry));
    horizon.setAttribute("aria-valuetext", years(state.horizon));
    const active = activeLevers();
    document.getElementById("param-count").textContent = active === 0 ? t("sim.paramRef") : t("sim.paramActive", { count: active });
    renderHero(res, animate);
    renderConfidence(res);
    renderCurve(res, animate);
    renderLevers();
    renderRank(res);
    renderWarnings(res);
    renderAnalogs();
    writeHash();
    return res;
  }

  function refreshAll({ animate = false } = {}) {
    renderStatic();
    renderChallenges();
    buildControls();
    renderChallengeCard();
    renderLog();
    update({ animate });
  }

  document.getElementById("run").addEventListener("click", () => {
    const res = update({ animate: true });
    const hero = document.querySelector(".hero");
    hero.classList.remove("flash"); void hero.offsetWidth; hero.classList.add("flash");
    const entry = { n: state.log.length + 1, profile: { ...state.profile }, horizon: state.horizon,
                    median: res.median.reached ? res.median.years : null, curve: res.survival,
                    sLast: res.survival[res.survival.length - 1], challenge: null, stars: 0,
                    level: Game.confidence(res.warning_details).level };
    const ch = state.challenge;
    if (ch) {
      const T = ch.target;
      const p = res.survival[T];
      // Étoiles gagnées par la probabilité, plafonnées par la confiance ; c'est la valeur plafonnée qui est enregistrée
      const g = Game.grade(p, ch.stars, res.warning_details);
      state.result = { id: ch.id, p, lo: res.band.lower[T], hi: res.band.upper[T], stars: g.stars, earned: g.earned,
                       capped: g.capped, level: g.level, reasons: g.reasons, km: kmAt(T),
                       median: res.median.reached ? res.median.years : null,
                       beat: res.median.reached ? 1 - kmAt(res.median.years) : null };
      saveBest(ch.id, g.stars, p);
      entry.challenge = ch.id;
      entry.stars = g.stars;
      renderChallenges();
      renderChallengeCard();
      challengeCard.classList.remove("flash"); void challengeCard.offsetWidth; challengeCard.classList.add("flash");
    }
    state.log.push(entry);
    if (state.log.length > 10) state.log.shift();
    renderLog();
  });
  document.getElementById("clear-log").addEventListener("click", () => { state.log = []; renderLog(); });

  // Lien de partage
  const shareStatus = document.getElementById("share-status");
  function copied(ok) {
    shareStatus.textContent = t(ok ? "sim.shareCopied" : "sim.shareFailed");
    clearTimeout(copied.timer);
    copied.timer = setTimeout(() => { shareStatus.textContent = ""; }, 3500);
  }
  document.getElementById("share").addEventListener("click", () => {
    writeHash();
    const url = location.href;
    const fallback = () => {
      const input = el("input", { value: url, readonly: true, style: { position: "fixed", opacity: "0" } });
      document.body.appendChild(input);
      input.select();
      let ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      input.remove();
      copied(ok);
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(() => copied(true), fallback);
    else fallback();
  });

  let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => update(), 150); });
  window.addEventListener("hashchange", () => {
    if (location.hash === "#" + encodeState()) return;
    readHash();
    refreshAll();
  });
  I18n.onChange(() => { Core.tooltip.hide(); refreshAll(); });

  readHash();
  refreshAll({ animate: true });
  window.Simulation = { state, update, refreshAll, startChallenge, CHALLENGES };   // pour les tests
  window.__ready = true;
})();
