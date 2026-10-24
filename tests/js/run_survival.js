// Runs the website's survival predictor (frontend/assets/js/survival.js) on profiles read from stdin.
global.window = global;
require("../../frontend/data/model.js");
const Survival = require("../../frontend/assets/js/survival.js");

let input = "";
process.stdin.on("data", (d) => { input += d; });
process.stdin.on("end", () => {
  const data = window.SITE.game.model;
  const out = JSON.parse(input).map((r) => Survival.predict(data, r.profile, r.horizon));
  process.stdout.write(JSON.stringify(out));
});
