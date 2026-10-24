"""The website's JavaScript predictor must reproduce api/predictor.py exactly."""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from api.main import DEFAULT_MODEL_PATH
from api.predictor import load_model, predict

ROOT = Path(__file__).resolve().parents[1]
DATA = load_model(DEFAULT_MODEL_PATH)
FORM = DATA["form"]

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")


def requests_to_check(n=80, seed=1):
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        profile = {
            "origin": str(rng.choice(FORM["origin"]["levels"])),
            "governance": str(rng.choice(FORM["governance"]["levels"])),
            "marxist": bool(rng.randint(2)),
            "conflict_entry": bool(rng.randint(2)), "polity2_entry": int(rng.randint(-10, 11)),
        }
        out.append({"profile": profile, "horizon": int(rng.choice([1, 10, 30, 60, DATA["model"]["t_max"] + 5]))})
    return out


def test_model_file_matches_exported_json():
    text = (ROOT / "frontend" / "data" / "model.js").read_text(encoding="utf-8")
    embedded = json.loads(text.split("window.SITE.game = ", 1)[1].rstrip().rstrip(";"))["model"]
    exported = json.loads(DEFAULT_MODEL_PATH.read_text(encoding="utf-8"))
    assert embedded == exported, "frontend/data/model.js is stale: run python frontend/build_data.py"


def test_javascript_predictor_equals_python():
    reqs = requests_to_check()
    run = subprocess.run(["node", str(ROOT / "tests" / "js" / "run_survival.js")], input=json.dumps(reqs),
                         capture_output=True, text=True, encoding="utf-8", check=True)
    js = json.loads(run.stdout)
    worst = 0.0
    for req, got in zip(reqs, js):
        ref = predict(DATA, req["profile"], req["horizon"])
        for key in ("times", "horizon_used", "horizon_requested", "median", "notes", "warnings",
                    "note_details", "warning_details"):
            assert got[key] == ref[key], (key, req)
        for a, b in [(got["survival"], ref["survival"]), (got["band"]["lower"], ref["band"]["lower"]),
                     (got["band"]["upper"], ref["band"]["upper"])]:
            worst = max(worst, float(np.max(np.abs(np.array(a) - np.array(b)))))
    assert worst < 1e-9, worst
