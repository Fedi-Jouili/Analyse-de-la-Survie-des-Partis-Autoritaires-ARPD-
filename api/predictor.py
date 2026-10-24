"""Survival prediction from the exported Cox model (src/cox_static_model.json).

Depends only on numpy and the standard library: no lifelines, no pickle.
The model is the corrected static Cox model of notebooks/final_panel.ipynb (Section 6.3):
covariates listed in `nph_covariates` have one effect during the first `cut_years` years
in power and another afterwards (`<covariate>_x_late` terms).
"""
import json

import numpy as np

SCHEMA_VERSION = 1
DEFAULT_HORIZON = 30          # years shown by default
BAND_PERCENTILES = (2.5, 97.5)
MIN_SPELLS = 20               # below this many training spells, a choice triggers a warning

BOOLEAN_LABELS = {
    "marxist": ("une idéologie marxiste-léniniste", "pas d'idéologie marxiste-léniniste"),
    "conflict_entry": ("un conflit armé à l'entrée au pouvoir", "pas de conflit armé à l'entrée au pouvoir"),
}


def load_model(path):
    """Read and check the exported model; arrays are converted to numpy."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version {data.get('schema_version')} != {SCHEMA_VERSION}")
    model, boot = data["model"], data["bootstrap"]
    features, base = model["features"], model["base_features"]
    expected = base + [f"{v}_x_late" for v in model["nph_covariates"]]
    if features != expected:
        raise ValueError("feature order differs from base_features + _x_late terms")
    if [spec["feature"] for spec in model["inputs"]] != base:
        raise ValueError("inputs do not match base_features")
    n_times = model["t_max"] + 1
    arrays = {
        "beta": np.array(model["coefficients"]),
        "mean": np.array(model["norm_mean"]),
        "H0": np.array(model["baseline_cumulative_hazard"]),
        "boot_beta": np.array(boot["coefficients"]),
        "boot_mean": np.array(boot["norm_mean"]),
        "boot_H0": np.array(boot["baseline_cumulative_hazard"]),
    }
    n_boot = boot["replicates"]
    shapes = {"beta": (len(features),), "mean": (len(features),), "H0": (n_times,),
              "boot_beta": (n_boot, len(features)), "boot_mean": (n_boot, len(features)),
              "boot_H0": (n_boot, n_times)}
    for name, shape in shapes.items():
        if arrays[name].shape != shape:
            raise ValueError(f"{name} has shape {arrays[name].shape}, expected {shape}")
    if not 0 <= model["cut_years"] <= model["t_max"]:
        raise ValueError("cut_years outside 0..t_max")
    data["arrays"] = arrays
    return data


def feature_vectors(data, profile):
    """Covariate vectors (early period, late period) for a profile, in the model's feature order."""
    model = data["model"]
    values = {}
    for spec in model["inputs"]:
        if "fixed" in spec:
            values[spec["feature"]] = float(spec["fixed"])
        elif "level" in spec:
            values[spec["feature"]] = float(profile[spec["input"]] == spec["level"])
        else:
            values[spec["feature"]] = float(profile[spec["input"]])
    early, late = dict(values), dict(values)
    for v in model["nph_covariates"]:
        early[f"{v}_x_late"], late[f"{v}_x_late"] = 0.0, values[v]
    return (np.array([early[f] for f in model["features"]]),
            np.array([late[f] for f in model["features"]]))


def survival_curves(beta, mean, H0, x_early, x_late, cut):
    """S(t) at t = 0..t_max. beta, mean, H0 may carry a leading replicate axis.

    lifelines centres covariates: the risk of x is exp((x - mean) . beta) and H0 is the baseline
    at the mean profile. The early risk applies up to the cut, the late risk afterwards.
    """
    r_early = np.exp(((x_early - mean) * beta).sum(axis=-1))[..., None]
    r_late = np.exp(((x_late - mean) * beta).sum(axis=-1))[..., None]
    t = np.arange(H0.shape[-1])
    H0_cut = H0[..., cut:cut + 1]
    H = np.where(t <= cut, r_early * H0, r_early * H0_cut + r_late * (H0 - H0_cut))
    return np.exp(-H)


def support_warnings(data, profile):
    """Warnings when the profile rests on few training spells (rules: constants at the top)."""
    support, form = data["support"], data["form"]
    out = []
    checks = [(f"l'origine « {profile['origin']} »", support["origin"][profile["origin"]]),
              (f"la stratégie « {profile['governance']} »", support["governance"][profile["governance"]])]
    for name, (label_true, label_false) in BOOLEAN_LABELS.items():
        value = bool(profile[name])
        checks.append((label_true if value else label_false, support[name]["true" if value else "false"]))
    for label, n in checks:
        if n < MIN_SPELLS:
            out.append(f"Seulement {n} partis de l'échantillon d'estimation ont {label} "
                       f"(seuil d'alerte : {MIN_SPELLS}) : la prédiction est peu précise pour ce choix.")
    n_combo = support["origin_x_governance"][profile["origin"]][profile["governance"]]
    if n_combo == 0:
        out.append(f"Aucun parti de l'échantillon ne combine l'origine « {profile['origin']} » et la stratégie "
                   f"« {profile['governance']} » (parmi les {data['sample']['spells'] - support['governance_not_coded']} "
                   "partis dont la stratégie est codée) : la prédiction est une extrapolation.")
    pol = form["polity2_entry"]
    if not pol["p05"] <= profile["polity2_entry"] <= pol["p95"]:
        out.append(f"Le score Polity2 choisi ({profile['polity2_entry']}) est en dehors de l'intervalle où se situent "
                   f"90 % des partis de l'échantillon ({pol['p05']:g} à {pol['p95']:g}).")
    return out


def support_details(data, profile):
    """The warnings of support_warnings() as codes and values, in the same order (translated by the website).

    small_group: {variable, value, n, threshold} · unseen_combination: {origin, governance, coded} ·
    polity_outside_range: {value, p05, p95}
    """
    support, form = data["support"], data["form"]
    out = []
    checks = [("origin", profile["origin"], support["origin"][profile["origin"]]),
              ("governance", profile["governance"], support["governance"][profile["governance"]])]
    for name in BOOLEAN_LABELS:
        value = bool(profile[name])
        checks.append((name, value, support[name]["true" if value else "false"]))
    for variable, value, n in checks:
        if n < MIN_SPELLS:
            out.append({"code": "small_group",
                        "values": {"variable": variable, "value": value, "n": n, "threshold": MIN_SPELLS}})
    if support["origin_x_governance"][profile["origin"]][profile["governance"]] == 0:
        out.append({"code": "unseen_combination",
                    "values": {"origin": profile["origin"], "governance": profile["governance"],
                               "coded": data["sample"]["spells"] - support["governance_not_coded"]}})
    pol = form["polity2_entry"]
    if not pol["p05"] <= profile["polity2_entry"] <= pol["p95"]:
        out.append({"code": "polity_outside_range",
                    "values": {"value": profile["polity2_entry"], "p05": pol["p05"], "p95": pol["p95"]}})
    return out


def predict(data, profile, horizon=DEFAULT_HORIZON):
    """Survival curve, median, 95% bootstrap band and warnings for one profile.

    profile: origin (str), governance (str), marxist, conflict_entry (bool),
    polity2_entry (int). Validation of the values is the caller's job (see api/main.py).
    """
    model, arr = data["model"], data["arrays"]
    t_max = model["t_max"]
    notes, note_details = [], []
    horizon_used = int(horizon)
    if horizon_used > t_max:
        notes.append(f"Horizon ramené de {horizon_used} à {t_max} ans, la plus longue durée observée dans les données.")
        note_details.append({"code": "horizon_capped", "values": {"requested": horizon_used, "used": t_max}})
        horizon_used = t_max
    x_early, x_late = feature_vectors(data, profile)
    cut = model["cut_years"]
    surv = survival_curves(arr["beta"], arr["mean"], arr["H0"], x_early, x_late, cut)[: horizon_used + 1]
    boot = survival_curves(arr["boot_beta"], arr["boot_mean"], arr["boot_H0"], x_early, x_late, cut)
    lower, upper = np.percentile(boot[:, : horizon_used + 1], BAND_PERCENTILES, axis=0)

    below = np.flatnonzero(surv <= 0.5)
    if below.size:
        median = {"years": int(below[0]), "reached": True,
                  "text": f"La moitié des partis comparables a quitté le pouvoir après {int(below[0])} ans."}
    else:
        median = {"years": None, "reached": False,
                  "text": f"Médiane non atteinte : plus de la moitié des partis comparables sont encore au pouvoir "
                          f"après {horizon_used} ans."}
    return {
        "times": list(range(horizon_used + 1)),
        "survival": surv.tolist(),
        "band": {"level": 0.95, "lower": lower.tolist(), "upper": upper.tolist(),
                 "replicates": int(arr["boot_beta"].shape[0])},
        "median": median,
        "horizon_requested": int(horizon),
        "horizon_used": horizon_used,
        "notes": notes,
        "warnings": support_warnings(data, profile),
        # The same notes and warnings as codes and values, for translation (not part of the API response)
        "note_details": note_details,
        "warning_details": support_details(data, profile),
    }
