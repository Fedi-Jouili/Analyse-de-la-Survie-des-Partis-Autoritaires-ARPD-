"""Tests of api/predictor.py against the lifelines model exported by final_panel.ipynb."""
import joblib
import numpy as np
import pytest

from api.main import DEFAULT_MODEL_PATH
from api.predictor import MIN_SPELLS, feature_vectors, load_model, predict
from panel_model import predict_survival

ROOT = DEFAULT_MODEL_PATH.parents[1]
DATA = load_model(DEFAULT_MODEL_PATH)
T_MAX = DATA["model"]["t_max"]
FORM = DATA["form"]


def random_profiles(n, seed=0):
    rng = np.random.RandomState(seed)
    return [{
        "origin": rng.choice(FORM["origin"]["levels"]),
        "governance": rng.choice(FORM["governance"]["levels"]),
        "marxist": bool(rng.randint(2)),
        "conflict_entry": bool(rng.randint(2)),
        "polity2_entry": int(rng.randint(-10, 11)),
    } for _ in range(n)]


PROFILES = random_profiles(100)


@pytest.fixture(scope="module")
def lifelines_model():
    model = joblib.load(ROOT / "src" / "cph_static_model.pkl")
    meta = joblib.load(ROOT / "src" / "model_features.pkl")
    return model, meta


def test_equivalent_to_lifelines(lifelines_model):
    model, meta = lifelines_model
    times = np.arange(T_MAX + 1)
    worst = 0.0
    for profile in PROFILES:
        x_early, _ = feature_vectors(DATA, profile)
        base = dict(zip(DATA["model"]["features"], x_early))
        values = {f: base[f] for f in meta["features"]}
        reference = predict_survival(model, values, times, meta["cut_years"], meta["nph_covariates"]).values
        ours = np.array(predict(DATA, profile, horizon=T_MAX)["survival"])
        worst = max(worst, float(np.abs(ours - reference).max()))
    assert worst < 1e-9


def test_not_coded_governance_fixed_to_zero():
    specs = {s["feature"]: s for s in DATA["model"]["inputs"]}
    assert specs["Gov_Non code"] == {"feature": "Gov_Non code", "fixed": 0.0}
    assert "Non code" not in FORM["governance"]["levels"]


@pytest.mark.parametrize("profile", PROFILES[:20])
def test_curve_properties(profile):
    out = predict(DATA, profile, horizon=T_MAX)
    s, lo, hi = (np.array(out["survival"]), np.array(out["band"]["lower"]), np.array(out["band"]["upper"]))
    assert s[0] == 1.0
    assert np.all(np.diff(s) <= 1e-12)
    assert np.all((s >= 0) & (s <= 1)) and np.all((lo >= 0) & (hi <= 1))
    assert np.all(lo <= hi)
    assert out["band"]["replicates"] == DATA["bootstrap"]["replicates"]


def test_deterministic():
    assert predict(DATA, PROFILES[0]) == predict(DATA, PROFILES[0])


def test_clientelist_small_group_warning():
    n = DATA["support"]["governance"]["Clientelist"]
    assert n < MIN_SPELLS
    profile = {**PROFILES[0], "governance": "Clientelist"}
    warnings = predict(DATA, profile)["warnings"]
    assert any(f"Seulement {n} partis" in w and "Clientelist" in w for w in warnings)


def test_horizon_capped_by_predictor():
    out = predict(DATA, PROFILES[0], horizon=T_MAX + 10)
    assert out["horizon_used"] == T_MAX and out["horizon_requested"] == T_MAX + 10
    assert len(out["survival"]) == T_MAX + 1
    assert out["notes"]


def test_median_not_reached():
    profile, horizon = PROFILES[0], 2
    out = predict(DATA, profile, horizon=horizon)
    assert min(out["survival"]) > 0.5            # precondition: S stays above 0.5 over the horizon
    assert out["median"] == {"years": None, "reached": False, "text": out["median"]["text"]}


def test_median_reached_is_first_crossing():
    out = predict(DATA, PROFILES[0], horizon=T_MAX)
    s = np.array(out["survival"])
    if out["median"]["reached"]:
        m = out["median"]["years"]
        assert s[m] <= 0.5 and np.all(s[:m] > 0.5)
    else:
        assert np.all(s > 0.5)


@pytest.mark.parametrize("profile", PROFILES)
def test_structured_warnings_match_texts(profile):
    """note_details / warning_details: one coded entry per French text, in the same order."""
    out = predict(DATA, profile, horizon=T_MAX + 3)
    assert len(out["warning_details"]) == len(out["warnings"])
    assert len(out["note_details"]) == len(out["notes"])
    codes = {"small_group", "unseen_combination", "polity_outside_range"}
    for detail, text in zip(out["warning_details"], out["warnings"]):
        assert detail["code"] in codes
        if detail["code"] == "small_group":
            assert f"Seulement {detail['values']['n']} partis" in text
        elif detail["code"] == "unseen_combination":
            assert detail["values"]["origin"] in text and detail["values"]["governance"] in text
        else:
            assert f"({detail['values']['value']})" in text
    assert out["note_details"] == [{"code": "horizon_capped", "values": {"requested": T_MAX + 3, "used": T_MAX}}]


def test_api_response_unchanged_by_details():
    """The coded details are for the website: the API response model does not expose them."""
    from api.main import PredictResponse
    assert "warning_details" not in PredictResponse.model_fields
    assert "note_details" not in PredictResponse.model_fields

