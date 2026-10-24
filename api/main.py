"""API of the authoritarian party survival model.

Run from the project root:  uvicorn api.main:app --reload
Environment variables:
- ARPD_MODEL_PATH   path of the exported model (default: src/cox_static_model.json)
- ARPD_CORS_ORIGINS comma-separated allowed origins (default: none, CORS disabled)
"""
import os
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from .predictor import DEFAULT_HORIZON, load_model, predict

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "src" / "cox_static_model.json"
MODEL = load_model(os.environ.get("ARPD_MODEL_PATH", DEFAULT_MODEL_PATH))
T_MAX = MODEL["model"]["t_max"]
FORM = MODEL["form"]

OriginLevel = Literal[tuple(FORM["origin"]["levels"])]
GovernanceLevel = Literal[tuple(FORM["governance"]["levels"])]


class Profile(BaseModel):
    """A party profile at its entry into power. Strict: no type coercion, no extra field."""
    model_config = ConfigDict(strict=True, extra="forbid")

    origin: OriginLevel
    governance: GovernanceLevel
    marxist: bool
    conflict_entry: bool
    polity2_entry: int = Field(ge=FORM["polity2_entry"]["min_allowed"], le=FORM["polity2_entry"]["max_allowed"])


class PredictRequest(Profile):
    horizon: int = Field(default=min(DEFAULT_HORIZON, T_MAX), ge=1, le=T_MAX)


class Band(BaseModel):
    level: float
    lower: list[float]
    upper: list[float]
    replicates: int


class Median(BaseModel):
    years: Optional[int]
    reached: bool
    text: str


class PredictResponse(BaseModel):
    profile: Profile
    times: list[int]
    survival: list[float]
    band: Band
    median: Median
    horizon_requested: int
    horizon_used: int
    notes: list[str]
    warnings: list[str]


def limits_texts():
    """Limits of the model, in French, built from the values stored in the exported model."""
    s, perf = MODEL["sample"], MODEL["performance"]
    cv = perf["c_index_cv"]
    return [
        "Les résultats décrivent des associations observées dans les données, pas des effets causaux.",
        f"Le pouvoir de discrimination est modeste : C-index de {cv['mean']:.2f} (écart-type {cv['sd']:.2f}) "
        f"en validation croisée par pays, contre {perf['c_index_in_sample']['value']:.2f} sur les données "
        "d'estimation (0.5 = hasard, 1 = classement parfait).",
        f"Le modèle est estimé sur {s['spells']} partis autoritaires nommés de {s['countries']} pays, arrivés au "
        f"pouvoir à partir de {s['first_year_in_power']} et observés jusqu'en {s['observation_end_year']} "
        f"({s['events']} chutes, {s['censored']} partis encore au pouvoir).",
        f"Les chutes postérieures à {s['arpd_last_year']} ({s['post_arpd_events_hand_coded']} dans l'échantillon) "
        "ont été codées à la main à partir de sources publiques.",
        "La modalité « Non codé » de la stratégie de gouvernance n'est pas proposée : ce n'est pas une stratégie, "
        "mais une absence de codage dans les données de Miller (2020).",
    ]


app = FastAPI(
    title="Survie des partis autoritaires",
    description="Prédiction de la survie au pouvoir d'un parti autoritaire (modèle de Cox, données ARPD).",
    version=str(MODEL["schema_version"]),
)
cors_origins = [o.strip() for o in os.environ.get("ARPD_CORS_ORIGINS", "").split(",") if o.strip()]
if cors_origins:
    app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type"])


@app.get("/health")
def health():
    return {"status": "ok", "schema_version": MODEL["schema_version"], "model_created": MODEL["created"]}


@app.get("/model")
def model_info():
    default_profile = {
        "origin": FORM["origin"]["reference"], "governance": FORM["governance"]["reference"],
        "marxist": False, "conflict_entry": False,
        "polity2_entry": int(round(FORM["polity2_entry"]["median"])),
        "horizon": min(DEFAULT_HORIZON, T_MAX),
    }
    return {
        "form": {**FORM, "horizon": {"min": 1, "max": T_MAX, "default": min(DEFAULT_HORIZON, T_MAX)}},
        "defaults": default_profile,
        "support": MODEL["support"],
        "sample": MODEL["sample"],
        "performance": MODEL["performance"],
        "uncertainty": {"method": MODEL["bootstrap"]["method"], "replicates": MODEL["bootstrap"]["replicates"],
                        "level": 0.95},
        "limits": limits_texts(),
        "model_created": MODEL["created"],
    }


@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    profile = request.model_dump(exclude={"horizon"})
    return {"profile": profile, **predict(MODEL, profile, request.horizon)}
