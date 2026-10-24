"""Checks of the files written by notebooks/05_shocks.ipynb (shocks of the previous year: sudden-onset natural
disasters, major earthquakes, battle deaths, wars between states, famines, food production, severe recessions).

The tests only read the notebook's outputs; they are skipped until the notebook has been run."""
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
PROC, RAW = ROOT / "data" / "processed", ROOT / "data" / "raw"
OUTPUTS = ["shocks_country_year.csv", "ml_timevarying_shocks.csv", "shocks_cv_taskB.csv", "site_results_shocks.json"]
pytestmark = pytest.mark.skipif(not all((PROC / f).exists() for f in OUTPUTS),
                                reason="run notebooks/05_shocks.ipynb first")

BINARY = ["quake", "interstate_war", "famine", "food_drop", "recession"]
RATES = ["disaster_deaths", "battle_deaths"]          # log(1 + deaths per million people)
# Columns that would identify a country-year (or a party-year): never in the export read by the website
COUNTRY_YEAR_COLUMNS = {"cow", "year", "panel_year", "lag_year", "Country", "country", "iso3", "spell_id", "row_id"}


def table(split):
    """A table exported in pandas' "split" format."""
    return pd.DataFrame(split["data"], columns=split["columns"])


@pytest.fixture(scope="module")
def results():
    return json.loads((PROC / "site_results_shocks.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tv():
    return pd.read_csv(PROC / "ml_timevarying_shocks.csv")


@pytest.fixture(scope="module")
def country_year():
    return pd.read_csv(PROC / "shocks_country_year.csv")


@pytest.fixture(scope="module")
def variables(results):
    return table(results["candidates"])["variable"].tolist()


@pytest.fixture(scope="module")
def features():
    meta = json.loads((PROC / "ml_metadata.json").read_text(encoding="utf-8"))
    return meta["timevarying"]["features"]


def test_variables(variables):
    assert variables == ["disaster_deaths", "quake", "battle_deaths", "interstate_war", "famine", "food_drop",
                         "recession"]


def test_existing_data_unchanged(tv, features):
    base = pd.read_csv(PROC / "ml_timevarying.csv")
    assert len(tv) == len(base) and set(tv["row_id"]) == set(base["row_id"])
    shared = ["spell_id", "Country", "panel_year", "start", "stop", "event"] + features
    same = tv.set_index("row_id").loc[base["row_id"], shared].reset_index(drop=True)
    pd.testing.assert_frame_equal(same, base[shared], check_dtype=False)


def test_value_of_the_previous_year_only(tv, country_year, variables):
    """No value after the year of the risk: each party-year gets the shock of the previous year, never a value carried
    forward from an earlier year."""
    assert (tv["lag_year"] == tv["panel_year"] - 1).all()
    assert not country_year.duplicated(["cow", "year"]).any()
    values = country_year.set_index(["cow", "year"])[variables]
    expected = values.reindex(pd.MultiIndex.from_arrays([tv["cow"], tv["lag_year"]]))
    np.testing.assert_array_equal(tv[[f"{v}_lag1" for v in variables]].to_numpy(float), expected.to_numpy(float))


def test_cow_code_fixed_within_spell(tv):
    assert tv.groupby("spell_id")["cow"].nunique().max() == 1


@pytest.mark.parametrize("v", BINARY)
def test_binary_shocks(country_year, v):
    values = country_year[v].dropna()
    assert len(values) and set(values.unique()) <= {0, 1} and values.sum() > 0


@pytest.mark.parametrize("v", RATES)
def test_death_rates(country_year, v):
    values = country_year[v].dropna()
    assert len(values) and (values >= 0).all() and (values > 0).any()


def test_sources_cover_their_years(country_year, results):
    """Event datasets give 0 in the years they cover; outside these years, and for series, the value stays missing."""
    cy = country_year
    assert cy.loc[cy["year"] >= 1946, "interstate_war"].notna().all() and cy.loc[cy["year"] < 1946, "interstate_war"].isna().all()
    assert cy.loc[cy["year"] <= 2023, "famine"].notna().all() and cy.loc[cy["year"] > 2023, "famine"].isna().all()
    assert cy["quake"].notna().all()
    first = results["splice"]["first_year"]
    assert cy.loc[cy["year"] < first, "battle_deaths"].isna().all()
    assert cy.dropna(subset=["food_drop"])["year"].min() >= 1962          # FAOSTAT starts in 1961: changes from 1962
    assert cy.dropna(subset=["recession"])["year"].max() <= 2022          # Maddison 2023 stops in 2022


def test_events_attributed_to_the_state_of_their_date(country_year):
    """A few well-known events, attributed to the state that existed at their date."""
    cy = country_year.set_index(["cow", "year"])
    checks = [((365, 1952), "quake", 1),           # Kamchatka earthquake (USSR)
              ((436, 1973), "famine", 1),          # Sahel famine 1969-1974 (Niger, in the WPF table)
              ((850, 1977), "famine", 1),          # East Timor famine, territory under Indonesian control
              ((625, 1990), "famine", 1)]          # famine in today's South Sudan, then part of Sudan
    for key, v, expected in checks:
        if key in cy.index:
            assert cy.loc[key, v] == expected, (key, v)
    if (770, 1970) in cy.index:                    # 1970 Bhola cyclone in East Pakistan
        assert cy.loc[(770, 1970), "disaster_deaths"] > 5


def test_coverage_and_screening(results, tv, features):
    cov = table(results["coverage"]).set_index("variable")
    for v, row in cov.iterrows():
        b = tv[f"{v}_lag1"].notna()
        assert row["parti-années"] == b.sum() and row["chutes"] == (b & tv["event"].eq(1)).sum()
        assert row["parti-années avec choc"] == (tv[f"{v}_lag1"] > 0).sum()
    screening, protocol = results["screening"], results["protocol"]
    assert set(screening["dropped"]) == set(cov.index[cov["chutes"] < protocol["min_falls"]])
    assert set(screening["retained"]) == set(cov.index) - set(screening["dropped"]) - set(screening["removed_for_sample"])
    largest = protocol["largest_model_parameters"]
    assert largest == len(features) + 2                                     # M0 + the shock + the period control
    sample = tv.dropna(subset=features + [f"{v}_lag1" for v in screening["retained"]])
    info = results["sample"]
    assert (info["rows_tv"], info["spells_tv"], info["events_tv"]) == (len(sample), sample["spell_id"].nunique(),
                                                                         sample["event"].sum())
    assert info["row_ids_sha1"] == hashlib.sha1("|".join(map(str, sorted(sample["row_id"]))).encode("utf-8")).hexdigest()
    assert info["events_tv"] >= protocol["min_falls"] and info["events_tv"] / largest >= protocol["min_events_per_parameter"]
    for v in screening["removed_for_sample"]:      # put back, a removed variable leaves too few falls per parameter
        s = tv.dropna(subset=features + [f"{x}_lag1" for x in screening["retained"] + [v]])
        assert s["event"].sum() / largest < protocol["min_events_per_parameter"] or s["event"].sum() < protocol["min_falls"]


def test_splice_rule(results):
    s = results["splice"]
    assert s["spliced"] == (s["correlation_log"] >= results["protocol"]["concordance_min"])
    assert s["first_year"] == (1946 if s["spliced"] else 1989)
    assert s["matched_conflict_years"] > 500


def test_compared_models_use_same_party_years(results):
    cv = pd.read_csv(PROC / "shocks_cv_taskB.csv")
    folds = cv.groupby(["comparison", "repetition", "fold"])[["n_train", "n_test", "events_test"]].nunique()
    assert (folds == 1).all().all()
    assert (cv.groupby(["comparison", "model"]).size() == results["protocol"]["evaluations"]).all()
    n = results["sample"]["rows_tv"]
    for _, d in cv[cv["comparison"] == "chocs"].groupby(["model", "repetition"]):
        assert d["n_test"].sum() == n and (d["n_train"] + d["n_test"] == n).all()


def test_decision_rules(results):
    d = table(results["decision"]).set_index("variable")
    combined = table(results["models"]["combined"]).set_index("variable")
    tests = table(results["cv"]["task_b"]["tests"]).set_index("modèle")
    alpha = results["protocol"]["alpha"]
    np.testing.assert_allclose(d["p Holm"], multipletests(d["p"], method="holm")[1])
    assert (d["1. Holm < 0,05"] == (d["p Holm"] < alpha)).all()
    assert (d["2. ROC-AUC > M0"] == ((d["écart ROC-AUC"] > 0) & (d["p corrigée ROC-AUC"] < alpha))).all()
    for v, r in d.iterrows():
        c = combined.loc[v]
        assert r["3. époque"] == bool(np.sign(c["époque coef"]) == np.sign(c["coef"]) and c["époque p"] < alpha), v
        assert r["écart ROC-AUC"] == pytest.approx(tests.loc[f"K2·{v}", "ROC-AUC : écart"])
    kept = d["1. Holm < 0,05"] & d["2. ROC-AUC > M0"] & d["3. époque"]
    assert (d["retenue"] == kept).all()
    assert sorted(results["kept"]) == sorted(d.index[kept])
    if not results["kept"]:
        assert results["final_model"] is None
    assert results["coef_check_max_gap"] < 1e-3      # clustered form of the model = project's time-varying model


def walk_tables(obj, path=""):
    if isinstance(obj, dict):
        if {"columns", "index", "data"} <= set(obj):
            yield path, obj
        for k, v in obj.items():
            yield from walk_tables(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_tables(v, f"{path}[{i}]")


def test_export_has_no_country_year_values(results):
    """Only result tables are exported (EM-DAT's licence forbids distributing adapted data)."""
    tables = list(walk_tables(results))
    assert tables
    for path, split in tables:
        assert not COUNTRY_YEAR_COLUMNS & set(map(str, split["columns"])), path
        assert len(split["data"]) < 100, path


def test_site_texts(results, variables):
    sys.path.insert(0, str(ROOT / "src"))
    from site_text import shocks_texts
    texts = results["texts"]
    assert set(texts) == {"fr", "en", "ar"}
    assert shocks_texts(results) == json.loads(json.dumps(texts))       # the export holds the current texts
    codes = [v for v in variables if "_" in v]          # "famine", "quake", "recession" are also ordinary words
    for lang, t in texts.items():
        assert len(t["labels"]) == len(t["definitions"]) == len(t["units"]) == len(variables)
        body = json.dumps(t, ensure_ascii=False)
        assert "`" not in body and not [c for c in codes if re.search(rf"\b{c}\b", body)], lang
    assert not re.search("[٠-٩]", json.dumps(texts["ar"], ensure_ascii=False))


def test_shocks_are_not_simulation_inputs(variables):
    for path in (ROOT / "src" / "cox_static_model.json", ROOT / "frontend" / "data" / "model.js"):
        text = path.read_text(encoding="utf-8")
        assert not [v for v in variables if re.search(rf"\b{v}\b", text)], path


def test_downloads_logged():
    log = json.loads((RAW / "shocks_sources.json").read_text(encoding="utf-8"))
    assert {"260430_emdat_archive.xlsx", "noaa_significant_earthquakes.csv", "PRIO_BattleDeaths_v3.1.xls",
            "ucdp-brd-conf-261-csv.zip", "ucdp_translate_conf.csv", "owid_famines.csv",
            "Production_Indices_E_All_Data_(Normalized).zip"} <= set(log)
    for name, info in log.items():
        assert {"url", "downloaded", "bytes", "sha256"} <= set(info), name
        path = RAW / name
        if path.exists():   # EM-DAT, PRIO and the famine list are not committed: the notebook downloads them again
            assert path.stat().st_size == info["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"]


def test_restricted_files_are_not_committed():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for name in ["data/raw/260430_emdat_archive.xlsx", "data/raw/PRIO_BattleDeaths_v3.1.xls", "data/raw/owid_famines.csv",
                 "data/processed/shocks_country_year.csv", "data/processed/ml_timevarying_shocks.csv"]:
        assert name in ignored, name
