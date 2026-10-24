"""Tests of the API (api/main.py)."""
import json

import pytest
from fastapi.testclient import TestClient

from api.main import T_MAX, app

client = TestClient(app)
VALID = {"origin": "Dictator-Created", "governance": "Policy-Based", "marxist": False,
         "conflict_entry": False, "polity2_entry": -3}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_model_info_never_offers_not_coded():
    r = client.get("/model")
    assert r.status_code == 200
    body = r.json()
    assert all("non cod" not in g.lower() for g in body["form"]["governance"]["levels"])
    assert "Gov_Non code" not in json.dumps(body, ensure_ascii=False)
    assert body["limits"] and body["form"]["horizon"]["max"] == T_MAX


def test_predict_valid():
    r = client.post("/predict", json={**VALID, "horizon": 20})
    assert r.status_code == 200
    body = r.json()
    assert body["times"] == list(range(21)) and len(body["survival"]) == 21
    assert body["profile"] == VALID


@pytest.mark.parametrize("change", [
    {"origin": "Unknown"},
    {"governance": "Autre"},
    {"governance": "Non code"},
    {"governance": "Non codé"},
    {"polity2_entry": 11},
    {"polity2_entry": -11},
    {"polity2_entry": 5.5},
    {"polity2_entry": "5"},
    {"marxist": 1},
    {"horizon": 0},
    {"horizon": T_MAX + 1},
    {"extra_field": 1},
])
def test_predict_rejects_invalid(change):
    assert client.post("/predict", json={**VALID, **change}).status_code == 422


@pytest.mark.parametrize("field", list(VALID))
def test_predict_rejects_missing_field(field):
    payload = {k: v for k, v in VALID.items() if k != field}
    assert client.post("/predict", json=payload).status_code == 422


def test_api_runs_without_heavy_or_pickle_dependencies():
    """Import the API in a fresh interpreter: lifelines, pandas, scikit-learn and joblib must not be loaded,
    and no API module may import pickle."""
    import ast
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    code = ("import sys; import api.main; "
            "print(','.join(m for m in ('lifelines', 'pandas', 'sklearn', 'joblib') if m in sys.modules))")
    # stdin=DEVNULL: the child must not inherit the console's input handle (Windows cannot always duplicate it)
    out = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, check=True,
                         stdin=subprocess.DEVNULL)
    assert out.stdout.strip() == ""
    for name in ("main.py", "predictor.py"):
        tree = ast.parse((root / "api" / name).read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        assert not imported & {"pickle", "joblib", "lifelines", "pandas", "sklearn"}
