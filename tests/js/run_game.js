// Runs the game rules of the website (frontend/assets/js/game.js) for tests/test_frontend_game.py.
// stdin:  {"confidence": [details, ...], "grades": [{"p", "thresholds", "details"}, ...]}
// stdout: the confidence levels and grades asked for, the level of every possible profile, the challenges as
//         defined in game.js and the calibration rule applied to the current model.
global.window = global;
require("../../frontend/data/model.js");
const Survival = require("../../frontend/assets/js/survival.js");
const Game = require("../../frontend/assets/js/game.js");

let input = "";
process.stdin.on("data", (d) => { input += d; });
process.stdin.on("end", () => {
  const req = JSON.parse(input || "{}");
  const D = window.SITE.game.model;
  const all = Game.profiles(D.form);
  const details = (p) => Survival.supportDetails(D, p);
  const curves = new Map();
  const curve = (p) => {
    const key = JSON.stringify(p);
    if (!curves.has(key)) {
      curves.set(key, Survival.survivalCurve(D.model.coefficients, D.model.norm_mean, D.model.baseline_cumulative_hazard,
                                             ...Survival.featureVectors(D, p), D.model.cut_years));
    }
    return curves.get(key);
  };
  const hooks = { survivalAt: (p, T) => curve(p)[T], details };
  const challenges = Game.CHALLENGES.map((ch) => {
    const calibration = Game.calibrate(ch.lock, ch.target, all, hooks);
    // Best profile at the best level of confidence, and the grade it gets
    const pool = all.filter((p) => Game.matches(p, ch.lock));
    const atLevel = pool.filter((p) => Game.confidence(details(p)).level === calibration.level);
    const best = atLevel.reduce((b, p) => (curve(p)[ch.target] > curve(b)[ch.target] ? p : b), atLevel[0]);
    const levels = { high: 0, medium: 0, low: 0 };
    pool.forEach((p) => { levels[Game.confidence(details(p)).level] += 1; });
    return { ...ch, calibration, levels, best, bestP: curve(best)[ch.target],
             bestGrade: Game.grade(curve(best)[ch.target], ch.stars, details(best)) };
  });
  process.stdout.write(JSON.stringify({
    confidence: (req.confidence || []).map((d) => Game.confidence(d).level),
    grades: (req.grades || []).map((g) => Game.grade(g.p, g.thresholds, g.details)),
    profiles: all.map((p) => ({ profile: p, level: Game.confidence(details(p)).level })),
    challenges,
  }));
});
