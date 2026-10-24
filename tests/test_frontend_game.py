"""Game rules of the website (frontend/assets/js/game.js), run with Node: confidence of a prediction, star cap of the
challenges, and calibration of the challenges on every profile a player can build."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from api.main import DEFAULT_MODEL_PATH
from api.predictor import load_model, support_details

ROOT = Path(__file__).resolve().parents[1]
DATA = load_model(DEFAULT_MODEL_PATH)
FORM = DATA["form"]

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")


def small(variable, value, n):
    return {"code": "small_group", "values": {"variable": variable, "value": value, "n": n, "threshold": 20}}


UNSEEN = {"code": "unseen_combination", "values": {"origin": "Communist", "governance": "Policy-Based", "coded": 68}}
POLITY = {"code": "polity_outside_range", "values": {"value": -10, "p05": -8.85, "p95": 6}}
HORIZON = {"code": "horizon_capped", "values": {"requested": 90, "used": 77}}

CONFIDENCE_CASES = [
    ([], "high"),
    ([HORIZON], "high"),                                   # a capped horizon is a note, not weak evidence
    ([small("origin", "Military", 17)], "medium"),
    ([small("origin", "Merger/Split", 10)], "medium"),     # n = 10: still medium
    ([POLITY], "medium"),
    ([POLITY, HORIZON], "medium"),
    ([small("origin", "Merger/Split", 9)], "low"),         # n < 10
    ([small("governance", "Clientelist", 8)], "low"),
    ([UNSEEN], "low"),
    ([small("origin", "Military", 17), POLITY], "low"),    # two warnings
    ([small("origin", "Military", 17), small("governance", "Clientelist", 8), POLITY], "low"),
]

T3 = [0.5, 0.6, 0.65]
GRADE_CASES = [  # (p, thresholds, details) -> (earned, stars, capped)
    (0.70, T3, [], (3, 3, False)),
    (0.70, T3, [small("governance", "Clientelist", 8)], (3, 1, True)),
    (0.70, T3, [POLITY], (3, 2, True)),
    (0.62, T3, [POLITY], (2, 2, False)),
    (0.62, T3, [UNSEEN], (2, 1, True)),
    (0.55, T3, [UNSEEN], (1, 1, False)),
    (0.40, T3, [UNSEEN], (0, 0, False)),
    (0.4951, T3, [], (1, 1, False)),                       # shown as 50 %: the goal is reached as displayed
    (0.4949, T3, [], (0, 0, False)),
    (0.6449, T3, [], (2, 2, False)),
    (0.6451, T3, [], (3, 3, False)),
]


def rule(details):
    """The confidence rule, written again from its specification."""
    warnings = [d for d in details if d["code"] != "horizon_capped"]
    if not warnings:
        return "high"
    d = warnings[0]
    if len(warnings) >= 2 or d["code"] == "unseen_combination" or (d["code"] == "small_group" and d["values"]["n"] < 10):
        return "low"
    return "medium"


@pytest.fixture(scope="module")
def game():
    request = {"confidence": [d for d, _ in CONFIDENCE_CASES],
               "grades": [{"p": p, "thresholds": t, "details": d} for p, t, d, _ in GRADE_CASES]}
    run = subprocess.run(["node", str(ROOT / "tests" / "js" / "run_game.js")], input=json.dumps(request),
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(run.stdout)


def test_confidence_rule(game):
    assert [rule(d) for d, _ in CONFIDENCE_CASES] == [level for _, level in CONFIDENCE_CASES]
    assert game["confidence"] == [level for _, level in CONFIDENCE_CASES]


def test_star_cap(game):
    got = [(g["earned"], g["stars"], g["capped"]) for g in game["grades"]]
    assert got == [expected for *_, expected in GRADE_CASES]
    for g in game["grades"]:
        assert g["stars"] <= {"high": 3, "medium": 2, "low": 1}[g["level"]]


def test_confidence_of_every_profile(game):
    """Every profile a player can build (7 origins x 3 strategies x 2^2 switches x 21 Polity2 scores), with the
    warnings computed by the API's predictor (api/predictor.py)."""
    assert FORM["booleans"] == ["marxist", "conflict_entry"]       # no monarchy choice
    n = len(FORM["origin"]["levels"]) * len(FORM["governance"]["levels"]) * 2 ** 2 * 21
    assert len(game["profiles"]) == n == 1764
    for row in game["profiles"]:
        assert row["level"] == rule(support_details(DATA, row["profile"])), row["profile"]
    levels = {row["level"] for row in game["profiles"]}
    assert levels == {"high", "medium", "low"}


def test_challenges_follow_the_calibration_rule(game):
    for ch in game["challenges"]:
        cal = ch["calibration"]
        assert cal is not None, ch["id"]
        assert (cal["target"], cal["stars"]) == (ch["target"], ch["stars"]), ch["id"]
        assert ch["stars"][0] == 0.5 and ch["stars"][0] < ch["stars"][1] < ch["stars"][2], ch["id"]


def test_every_challenge_reaches_its_maximum(game):
    """With the best documented profile, every challenge gives all its stars: 3 when a high-confidence profile
    exists, fewer only when the imposed settings themselves rest on few parties (no high-confidence profile)."""
    for ch in game["challenges"]:
        cal, grade = ch["calibration"], ch["bestGrade"]
        assert grade["level"] == cal["level"] and grade["stars"] == cal["max"], ch["id"]
        if cal["max"] < 3:
            assert ch["levels"]["high"] == 0, ch["id"]
        else:
            assert grade["level"] == "high" and grade["earned"] == 3, ch["id"]
    assert [ch["id"] for ch in game["challenges"] if ch["calibration"]["max"] < 3] == ["coup"]
