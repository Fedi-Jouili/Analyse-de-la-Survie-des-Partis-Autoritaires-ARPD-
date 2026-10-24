"""Export notebook results as JSON for the website (read by frontend/build_data.py).

Only conversion helpers live here: the numbers themselves are computed in the notebooks.
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def jsonable(obj):
    """Convert pandas / numpy objects to plain JSON values (NaN and infinities become None).

    DataFrames use the 'split' layout: {"columns": [...], "index": [...], "data": [[...], ...]}.
    """
    if isinstance(obj, pd.DataFrame):
        return {"columns": [jsonable(c) for c in obj.columns],
                "index": [jsonable(i) for i in obj.index],
                "data": [[jsonable(v) for v in row] for row in obj.itertuples(index=False, name=None)]}
    if isinstance(obj, pd.Series):
        return {str(jsonable(k)): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {"|".join(map(str, k)) if isinstance(k, tuple) else str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, np.ndarray, pd.Index)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        value = float(obj)
        return value if math.isfinite(value) else None
    if obj is None or isinstance(obj, (str, int)):
        return obj
    if pd.isna(obj):
        return None
    return str(obj)


def write_json(path, obj):
    """Write `obj` as UTF-8 JSON and return the file size in kB."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(jsonable(obj), f, ensure_ascii=False, indent=1)
    return path.stat().st_size / 1024


def hazard_ratios(model):
    """Hazard ratios of a fitted lifelines model: one record per covariate."""
    s = model.summary
    return [{"covariate": str(v), "hr": float(r["exp(coef)"]), "lo": float(r["exp(coef) lower 95%"]),
             "hi": float(r["exp(coef) upper 95%"]), "p": float(r["p"])} for v, r in s.iterrows()]


def km_curve(kmf):
    """Survival function of a fitted KaplanMeierFitter with its 95% confidence band."""
    sf = kmf.survival_function_.iloc[:, 0]
    ci = kmf.confidence_interval_
    return {"t": [float(t) for t in sf.index], "s": [float(v) for v in sf.values],
            "lo": [float(v) for v in ci.iloc[:, 0].values], "hi": [float(v) for v in ci.iloc[:, 1].values]}
