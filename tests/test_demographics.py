"""Checks of the files written by notebooks/04_demographics.ipynb (country characteristics: demography and public
services, ethnicity and religion, employment, education and academic freedom).

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
OUTPUTS = ["ml_static_demo.csv", "ml_timevarying_demo.csv", "demo_country_year.csv", "demo_epr_mapping.csv",
           "demo_cv_taskA.csv", "demo_cv_taskB.csv", "site_results_demo.json"]
pytestmark = pytest.mark.skipif(not all((PROC / f).exists() for f in OUTPUTS),
                                reason="run notebooks/04_demographics.ipynb first")

BLOCKS = ("A", "B", "C")
# Regions from COW code ranges; the first one missing from the indicators is the reference (Afrique)
REGIONS = [("Amériques", 2, 165), ("Europe", 200, 399), ("Afrique", 400, 626), ("Moyen-Orient", 630, 698),
           ("Asie et Océanie", 700, 990)]
# Comparisons of the cross-validation and the sample each one uses
SAMPLE_OF = {"bloc A": "A", "bloc B": "B", "bloc C": "C", "F": "A+B+C"}
# Variables that the common sample of a block also requires (block C: GDP per capita at entry, for the S2p control)
NEEDS = {"A": [], "B": [], "C": ["log_gdppc_entry"]}
# Covariates added by the control of a block, in task A and in task B (the time-varying model already has GDP)
CONTROL_ADDS = {"A": (0, 0), "B": (4, 4), "C": (1, 0)}


def table(split):
    """A table exported in pandas' "split" format."""
    return pd.DataFrame(split["data"], columns=split["columns"])


@pytest.fixture(scope="module")
def results():
    return json.loads((PROC / "site_results_demo.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def static():
    return pd.read_csv(PROC / "ml_static_demo.csv")


@pytest.fixture(scope="module")
def tv():
    return pd.read_csv(PROC / "ml_timevarying_demo.csv")


@pytest.fixture(scope="module")
def country_year():
    return pd.read_csv(PROC / "demo_country_year.csv")


@pytest.fixture(scope="module")
def variables(results):
    """Candidate and comparison variables, in the order of the notebook."""
    return table(results["candidates"])["variable"].tolist()


@pytest.fixture(scope="module")
def features():
    meta = json.loads((PROC / "ml_metadata.json").read_text(encoding="utf-8"))
    return meta["static"]["features"], meta["timevarying"]["features"]


def test_merge_keys_unique(static, tv, country_year):
    assert static["spell_id"].is_unique
    assert tv["row_id"].is_unique
    assert not tv.duplicated(["spell_id", "panel_year"]).any()
    assert country_year[["cow", "year"]].notna().all().all()
    assert not country_year.duplicated(["cow", "year"]).any()


def test_existing_data_unchanged(static, tv):
    for name, demo, key in (("ml_static.csv", static, "spell_id"), ("ml_timevarying.csv", tv, "row_id")):
        base = pd.read_csv(PROC / name)
        assert len(demo) == len(base) and set(demo[key]) == set(base[key])
        same = demo.set_index(key).loc[base[key], [c for c in base.columns if c != key]].reset_index(drop=True)
        pd.testing.assert_frame_equal(same, base.drop(columns=key), check_dtype=False)


def test_values_at_entry_and_previous_year(static, tv, country_year, variables):
    cy = country_year.set_index(["cow", "year"])[variables]
    # Task A: value of the entry year only, never taken from another year
    expected = cy.reindex(pd.MultiIndex.from_arrays([static["cow"], static["entry_year"]]))
    np.testing.assert_array_equal(static[[f"{v}_entry" for v in variables]].to_numpy(float), expected.to_numpy(float))
    # Task B: value of the previous year, then carried forward within the spell (final_panel.ipynb, 3.3)
    t = tv.sort_values(["spell_id", "panel_year"])
    lagged = cy.reindex(pd.MultiIndex.from_arrays([t["cow"], t["panel_year"] - 1])).set_axis(t.index)
    expected = lagged.groupby(t["spell_id"]).ffill()
    np.testing.assert_array_equal(t[[f"{v}_lag1" for v in variables]].to_numpy(float), expected.to_numpy(float))


def test_cow_code_fixed_within_spell(static, tv):
    assert tv.groupby("spell_id")["cow"].nunique().max() == 1
    shared = static.merge(tv.groupby("spell_id", as_index=False)["cow"].first(), on="spell_id", suffixes=("", "_tv"))
    assert len(shared) and (shared["cow"] == shared["cow_tv"]).all()


def test_epr_mapping_covers_arpd_countries(static, tv, country_year):
    mapping = pd.read_csv(PROC / "demo_epr_mapping.csv")
    assert mapping["cow"].notna().all()
    assert set(static["cow"]) | set(tv["cow"]) <= set(mapping["cow"])
    # The only Gleditsch-Ward codes that differ from COW: Germany, Serbia, Yemen
    differ = mapping[mapping["gwid"] != mapping["cow"]]
    assert set(zip(differ["gwid"], differ["cow"])) == {(260, 255), (340, 345), (678, 679)}
    for _, d in mapping.groupby("cow"):           # at most one EPR state per COW code and year
        d = d.sort_values("first_year")
        assert (d["first_year"].to_numpy()[1:] > d["last_year"].to_numpy()[:-1]).all()
    # Every ARPD country-year inside an EPR period has a value, except the years of state collapse
    for cows, years in ((static["cow"], static["entry_year"]), (tv["cow"], tv["panel_year"] - 1)):
        keys = pd.DataFrame({"cow": cows.to_numpy(), "year": years.to_numpy()}).merge(mapping, on="cow")
        inside = keys[(keys["first_year"] <= keys["year"]) & (keys["year"] <= keys["last_year"])]
        values = inside[["cow", "year"]].drop_duplicates().merge(country_year, on=["cow", "year"], how="left")
        assert len(values)
        assert (values["epr_excluded"].notna() | values["epr_state_collapse"].eq(True)).all()


@pytest.mark.parametrize("v, low, high", [
    ("epr_excluded", 0, 1), ("al_ethnic2000", 0, 1), ("al_religion2000", 0, 1), ("academic_freedom", 0, 1),
    ("youth_share", 0, 100), ("old_share", 0, 100), ("urban_share", 0, 100), ("gini", 0, 100),
    ("unemployment", 0, 100), ("youth_unemployment", 0, 100), ("unemployment_advanced", 0, 100),
    ("bachelor_share", 0, 100), ("tertiary_enrol", 0, 200), ("education_years", 0, 20)])
def test_shares_and_indexes_in_range(static, tv, country_year, v, low, high):
    for values in (country_year[v], static[f"{v}_entry"], tv[f"{v}_lag1"]):
        values = values.dropna()
        assert len(values) and values.between(low, high).all(), v


def test_epr_groups_and_state_collapse(country_year):
    groups = country_year["epr_groups"].dropna()
    assert (groups >= 0).all() and (groups == groups.round()).all()
    collapse = country_year["epr_state_collapse"].eq(True)
    assert collapse.any() and country_year.loc[collapse, ["epr_excluded", "epr_groups"]].isna().all().all()


def test_series_start_where_the_sources_start(country_year):
    """Harmonised unemployment rates (ILO modelled estimates) start in 1991; the education series of Clio-Infra stops
    in 2010: no value is invented outside these years."""
    for v in ("unemployment", "youth_unemployment"):
        assert country_year.dropna(subset=[v])["year"].min() == 1991
    assert country_year.dropna(subset=["education_years"])["year"].max() == 2010


def test_fractionalization_one_value_per_country(country_year):
    assert (country_year.groupby("cow")[["al_ethnic2000", "al_religion2000"]].nunique() <= 1).all().all()


def test_only_expected_new_columns(static, tv, variables):
    """Diversity, exclusion and state-treatment measures only: no majority religion, no specific group."""
    regions = {f"region_{name}" for name, *_ in REGIONS[:2] + REGIONS[3:]}
    for demo, base, extra, suffix in ((static, "ml_static.csv", {"cow", "entry_year", "log_gdppc_entry"}, "_entry"),
                                      (tv, "ml_timevarying.csv", {"cow"}, "_lag1")):
        new = set(demo.columns) - set(pd.read_csv(PROC / base, nrows=0).columns)
        assert new == extra | {"region"} | regions | {f"{v}{suffix}" for v in variables}


def test_regions_follow_cow_ranges(static, tv):
    for demo in (static, tv):
        expected = [next(name for name, low, high in REGIONS if low <= c <= high) for c in demo["cow"]]
        assert demo["region"].tolist() == expected
        for name, *_ in REGIONS:
            if f"region_{name}" in demo:
                assert (demo[f"region_{name}"] == demo["region"].eq(name).astype(int)).all()


def test_coverage_table_matches_csvs(results, static, tv):
    coverage = table(results["coverage"]).set_index("variable")
    for v, row in coverage.iterrows():
        a, b = static[f"{v}_entry"].notna(), tv[f"{v}_lag1"].notna()
        assert row["A : spells"] == a.sum()
        assert row["A : chutes"] == (a & static["event"].eq(1)).sum()
        assert row["B : parti-années"] == b.sum()
        assert row["B : spells"] == tv.loc[b, "spell_id"].nunique()
        assert row["B : chutes"] == (b & tv["event"].eq(1)).sum()
    # Variables with fewer than MIN_FALLS falls in a task are dropped; the others are retained, unless they leave their
    # block's common sample too small (Section 4.3 of the notebook)
    candidates = table(results["candidates"]).query("rôle == 'candidate'")["variable"]
    falls = coverage.loc[candidates, ["A : chutes", "B : chutes"]].min(axis=1)
    screening = results["screening"]
    assert set(screening["dropped"]) == set(falls.index[falls < results["protocol"]["min_falls"]])
    retained = {v for b in BLOCKS for v in screening["retained"][b]}
    assert retained == set(candidates) - set(screening["dropped"]) - set(screening["removed_for_sample"])
    assert set(screening["removed_for_sample"]) == set(screening["removed_reason"])
    # Share of spells with a value, by decade of entry into power
    decade = (static["entry_year"] // 10 * 10).astype(str) + "s"
    by_decade = table(results["coverage_by_decade"]).set_index("index")
    for v, row in by_decade.iterrows():
        share = 100 * static[f"{v}_entry"].notna().groupby(decade).mean()
        assert (row[share.index] - share).abs().max() <= 0.5 + 1e-9


def common_sample(static, tv, features, variables, needs=()):
    static_features, tv_features = features
    sa = static.dropna(subset=static_features + [f"{v}_entry" for v in variables] + list(needs))
    tb = tv.dropna(subset=tv_features + [f"{v}_lag1" for v in variables])
    return sa, tb


def test_samples_match_export(results, static, tv, features):
    retained = results["screening"]["retained"]
    active = [b for b in BLOCKS if retained[b]]
    groups = {b: (retained[b], NEEDS[b]) for b in active}
    groups["A+B+C"] = ([v for b in active for v in retained[b]], sorted({n for b in active for n in NEEDS[b]}))
    for name, (variables, needs) in groups.items():
        sa, tb = common_sample(static, tv, features, variables, needs)
        info = results["samples"][name]
        assert (info["spells"], info["events"], info["countries"]) == (len(sa), sa["event"].sum(), sa["Country"].nunique())
        assert (info["rows_tv"], info["spells_tv"], info["events_tv"]) == (len(tb), tb["spell_id"].nunique(), tb["event"].sum())
        assert info["spell_ids_sha1"] == hashlib.sha1("|".join(sorted(sa["spell_id"])).encode("utf-8")).hexdigest()
    # Each block keeps enough falls, and at least MIN_EPP falls per parameter for its largest model
    protocol = results["protocol"]
    for b in active:
        info = results["samples"][b]
        assert min(info["events"], info["events_tv"]) >= protocol["min_falls"]
        add_a, add_b = CONTROL_ADDS[b]
        assert info["events"] / (len(features[0]) + 1 + add_a) >= protocol["min_events_per_parameter"]
        assert info["events_tv"] / (len(features[1]) + 1 + add_b) >= protocol["min_events_per_parameter"]


def test_removed_variables_would_break_the_block(results, static, tv, features):
    """A candidate removed from its block (Section 4.3) leaves too few falls per parameter when it is put back."""
    protocol, retained = results["protocol"], results["screening"]["retained"]
    for v, b in results["screening"]["removed_for_sample"].items():
        sa, tb = common_sample(static, tv, features, retained[b] + [v], NEEDS[b])
        add_a, add_b = CONTROL_ADDS[b]
        epp = min(sa["event"].sum() / (len(features[0]) + 1 + add_a), tb["event"].sum() / (len(features[1]) + 1 + add_b))
        assert epp < protocol["min_events_per_parameter"] or min(sa["event"].sum(), tb["event"].sum()) < protocol["min_falls"]


@pytest.mark.parametrize("task", ["A", "B"])
def test_compared_models_use_same_spells(results, task):
    cv = pd.read_csv(PROC / f"demo_cv_task{task}.csv")
    protocol = results["protocol"]
    assert set(cv["comparison"]) <= set(SAMPLE_OF)
    # Within a comparison, every model is scored on the same training and test sets of every fold
    folds = cv.groupby(["comparison", "repetition", "fold"])[["n_train", "n_test", "events_test"]].nunique()
    assert (folds == 1).all().all()
    assert (cv.groupby(["comparison", "model"]).size() == protocol["evaluations"]).all()
    # ... and these sets cover the comparison's common sample: each spell (party-year) is tested once per repetition
    size = "spells" if task == "A" else "rows_tv"
    for (comparison, _, _), d in cv.groupby(["comparison", "model", "repetition"]):
        n = results["samples"][SAMPLE_OF[comparison]][size]
        assert d["n_test"].sum() == n and (d["n_train"] + d["n_test"] == n).all()
    # M0 is the reference of every comparison
    assert cv.groupby("comparison")["model"].apply(lambda m: "M0" in set(m)).all()


def test_full_sample_reference_reproduces_03(results):
    ref = pd.read_csv(PROC / "ml_results_taskA.csv").query("model == 'Cox'")
    assert results["cv"]["full_sample_m0"]["harrell_c"]["mean"] == pytest.approx(ref["harrell_c"].mean(), abs=1e-12)


def test_decision_rules(results):
    d = table(results["decision"]).set_index("variable")
    combined = table(results["models"]["combined"]).set_index("variable")
    alpha = results["protocol"]["alpha"]
    np.testing.assert_allclose(d["p Holm"], multipletests(d["p (A)"], method="holm")[1])
    assert (d["1. Holm < 0,05"] == (d["p Holm"] < alpha)).all()
    assert (d["2. même sens"] == (np.sign(np.log(d["HR (A)"])) == np.sign(np.log(d["HR (B)"])))).all()
    assert (d["3. C > M0"] == ((d["écart C (A)"] > 0) & (d["p corrigée C"] < alpha))).all()
    # Condition 4: region control for block B, GDP control for block C, none for block A
    assert d.loc[d["bloc"] == "A", "4. contrôle"].isna().all()
    assert set(d.loc[d["bloc"] == "B", "contrôle"]) <= {"région"} and set(d.loc[d["bloc"] == "C", "contrôle"]) <= {"PIB"}
    for v, r in d[d["bloc"] != "A"].iterrows():
        c = combined.loc[v]
        assert r["4. contrôle"] == bool(np.sign(c["contrôle A coef"]) == np.sign(c["A coef"]) and c["contrôle A p"] < alpha)
    kept = (d["1. Holm < 0,05"] & d["2. même sens"] & d["3. C > M0"]
            & (d["bloc"].eq("A") | d["4. contrôle"].eq(True)))
    assert (d["retenue"] == kept).all()
    assert sorted(results["kept"]) == sorted(d.index[kept])
    if not results["kept"]:
        assert results["final_model"] is None


def test_events_per_parameter(results):
    epp = table(results["events_per_parameter"])
    minimum = results["protocol"]["min_events_per_parameter"]
    assert ((epp["chutes"] / epp["paramètres"] >= minimum) == epp["estimable"]).all()
    compared = {"M0 (bloc A)", "D1", "D2 (une candidate)", "M0 (bloc B)", "E1", "E2 (une candidate)",
                "E2r (une candidate + région)", "M0 (bloc C)", "S1", "S2 (une candidate)", "S2p (une candidate + PIB)"}
    assert epp.loc[epp["modèle"].isin(compared), "estimable"].all()


def test_descriptive_models_only_for_untestable_variables(results, features):
    """Variables that cannot be tested get descriptive estimates only, and only from models with enough falls."""
    desc = table(results["models"]["descriptive"]).set_index("variable")
    screening, minimum = results["screening"], results["protocol"]["min_events_per_parameter"]
    assert list(desc.index) == list(screening["dropped"]) + list(screening["removed_for_sample"])
    reduced = len(results["protocol"]["reduced_tv_model"]) + 1
    for v, r in desc.iterrows():
        assert pd.notna(r["HR (A, M0 + variable)"]) == (r["chutes (A)"] / (len(features[0]) + 1) >= minimum), v
        assert pd.notna(r["HR (B, réduit)"]) == (r["chutes (B)"] / reduced >= minimum), v


def test_site_texts(results):
    sys.path.insert(0, str(ROOT / "src"))
    from site_text import demo_texts
    texts = results["texts"]
    assert set(texts) == {"fr", "en", "ar"}
    assert demo_texts(results) == json.loads(json.dumps(texts))       # the export holds the current texts
    names = table(results["candidates"])["variable"].tolist()
    codes = [v for v in names if "_" in v or v.startswith("v2")]          # dataset codes, not words of the text
    for lang, t in texts.items():
        assert len(t["labels"]) == len(t["units"]) == len(names) and len(t["block_names"]) == 3
        body = json.dumps(t, ensure_ascii=False)
        assert "`" not in body and not [c for c in codes if re.search(rf"\b{c}\b", body)], lang
    assert not re.search("[٠-٩]", json.dumps(texts["ar"], ensure_ascii=False))


def test_candidates_are_not_simulation_inputs(variables):
    for path in (ROOT / "src" / "cox_static_model.json", ROOT / "frontend" / "data" / "model.js"):
        text = path.read_text(encoding="utf-8")
        assert not [v for v in variables if v in text], path


def test_downloads_logged():
    log = json.loads((RAW / "demo_sources.json").read_text(encoding="utf-8"))
    assert {"worldbank_wdi_demography.csv", "worldbank_wdi_labour_education.csv"} <= set(log)
    for name, info in log.items():
        assert {"url", "downloaded", "bytes", "sha256"} <= set(info), name
        path = RAW / name
        if path.exists():   # QoG and EPR are not committed (terms of use): the notebook downloads them again
            assert path.stat().st_size == info["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"]


def test_restricted_files_are_not_committed():
    """QoG and EPR do not allow redistribution: their files and the tables built with their values stay out of git."""
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for name in ["data/raw/qog_std_cs_jan26.csv", "data/raw/EPR-2021.csv", "data/processed/demo_country_year.csv",
                 "data/processed/ml_static_demo.csv", "data/processed/ml_timevarying_demo.csv"]:
        assert name in ignored, name
