"""Checks of the table of leaders reviewed by hand (data/raw/arpd_leaders_archigos.csv), of the downloads of
src/download_party_leader_data.py and of the files written by notebooks/06_party_leaders.ipynb (characteristics of the
ruling party and of its leader).

The tests of the notebook's outputs are skipped until the notebook has been run; those that need Archigos or LEAD are
skipped when these files are missing (LEAD is not in the repository: the download script gets it again)."""
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
OUTPUTS = ["ml_static_leaders.csv", "ml_timevarying_leaders.csv", "leaders_cv_taskA.csv", "leaders_cv_taskB.csv",
           "site_results_leaders.json"]
needs_notebook = pytest.mark.skipif(not all((PROC / f).exists() for f in OUTPUTS),
                                    reason="run notebooks/06_party_leaders.ipynb first")
needs_archigos = pytest.mark.skipif(not (RAW / "arch_annual.csv").exists(), reason="data/raw/arch_annual.csv is missing")
needs_lead = pytest.mark.skipif(not (RAW / "lead" / "LEAD.csv").exists(),
                                reason="run python src/download_party_leader_data.py first")

VARIABLES = ["party_age", "leader_age", "leader_irregular", "leader_military", "leader_rebel", "leader_university",
             "leader_experience"]
LEADER_VARIABLES = VARIABLES[1:]
TABLE_COLUMNS = ["spell_id", "entry_year", "ccode", "obsid", "leader", "leader_start", "review", "note"]
LEAD_COLUMNS = {"leveledu", "milservice", "combat", "rebel", "warwin", "warloss", "rebelwin", "rebelloss", "yrsexper",
                "physhealth", "mentalhealth"}
# Columns that would identify a country-year, a party-year or a leader: never in the export
IDENTIFYING_COLUMNS = {"cow", "ccode", "year", "panel_year", "lag_year", "entry_year", "Country", "country", "spell_id",
                       "row_id", "obsid", "leader", "leader_start"}
OBSID = re.compile(r"\b[A-Z]{3}-\d{4}(?:-\d+)?\b")          # Archigos leader identifiers: CUB-1959, ALG-1962-2
ARCHIGOS_LAST_YEAR = 2015


def table(split):
    """A table exported in pandas' "split" format."""
    return pd.DataFrame(split["data"], columns=split["columns"])


@pytest.fixture(scope="module")
def links():
    return pd.read_csv(RAW / "arpd_leaders_archigos.csv", keep_default_na=False)


@pytest.fixture(scope="module")
def archigos():
    """One row per Archigos leader (obsid), and the leader on 31 December of each country-year."""
    arch = pd.read_csv(RAW / "arch_annual.csv", low_memory=False)
    arch["year"] = arch["startdate"].str[:4].astype(int)
    leaders = (arch.sort_values("startdate").groupby("obsid")
                   .agg(leader=("leader", "first"), ccode=("ccode", "first"), start=("startdate", "first"),
                        end=("enddate", "last"), yrborn=("yrborn", "first")))
    leaders["yrborn"] = pd.to_numeric(leaders["yrborn"], errors="coerce")
    arch["dec31"] = arch["enddate"].str[5:] == "12-31"
    dec31 = (arch.sort_values(["ccode", "year", "dec31", "startdate"]).groupby(["ccode", "year"]).tail(1)
                 .set_index(["ccode", "year"])["obsid"])
    return leaders, dec31


@pytest.fixture(scope="module")
def results():
    return json.loads((PROC / "site_results_leaders.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------- table reviewed by hand
def test_one_reviewed_row_per_party(links):
    static = pd.read_csv(PROC / "ml_static.csv")
    assert list(links.columns) == TABLE_COLUMNS
    assert len(links) == len(static) == 224 and links["spell_id"].is_unique
    assert set(links["spell_id"]) == set(static["spell_id"])
    assert links["review"].isin(["vérifié", "corrigé"]).all()
    assert (links["note"].str.len() > 10).all()
    assert ((links["obsid"] == "") <= (links["review"] == "corrigé")).all()   # a missing link is always a correction
    assert ((links["obsid"] == "") == (links["leader"] == "")).all()


@needs_archigos
def test_links_match_archigos(links, archigos):
    leaders, _ = archigos
    linked = links[links["obsid"] != ""]
    assert linked["obsid"].isin(leaders.index).all()
    found = leaders.loc[linked["obsid"]]
    assert (found["leader"].to_numpy() == linked["leader"].to_numpy()).all()
    assert (found["start"].to_numpy() == linked["leader_start"].to_numpy()).all()
    assert (found["ccode"].to_numpy() == linked["ccode"].to_numpy()).all()        # a leader of the same country
    # in office in the entry year or the next one (a party's leader can take office after its arrival in power)
    start, end = found["start"].str[:4].astype(int).to_numpy(), found["end"].str[:4].astype(int).to_numpy()
    assert (start <= linked["entry_year"].to_numpy() + 1).all() and (end >= linked["entry_year"].to_numpy()).all()


@needs_archigos
@pytest.mark.parametrize("spell, name, code, year", [
    ("Cuba_26th of July Movement", "Castro", 40, 1959),
    ("Tunisia_Neo-Destour Party", "Bourguiba", 616, 1956),
    ("Yemen_General People's Congress", "Saleh", 678, 1993),
])
def test_known_leaders_checked_in_archigos(links, archigos, spell, name, code, year):
    leaders, _ = archigos
    row = links[links["spell_id"].str.startswith(spell)]
    assert len(row) == 1
    row = row.iloc[0]
    assert row["entry_year"] == year and row["obsid"] in leaders.index
    leader = leaders.loc[row["obsid"]]            # read in the source, not in the table
    assert name in leader["leader"] and leader["ccode"] == code
    assert int(leader["start"][:4]) <= year + 1 and int(leader["end"][:4]) >= year


# ---------------------------------------------------------------------------------------- downloads
def test_downloads_logged():
    log = json.loads((RAW / "party_leader_sources.json").read_text(encoding="utf-8"))
    for name in ("LEAD.rda", "arch_annual.csv"):
        info = log[name]
        assert {"url", "downloaded", "bytes", "sha256", "version", "licence"} <= set(info), name
        path = (RAW / "lead" / name) if name.startswith("LEAD") else RAW / name
        if path.exists():         # LEAD is not committed: src/download_party_leader_data.py downloads it again
            assert path.stat().st_size == info["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"]
    assert re.fullmatch(r"https://raw\.githubusercontent\.com/svmiller/peacesciencer/[0-9a-f]{40}/data/LEAD\.rda",
                        log["LEAD.rda"]["url"])               # a fixed commit, not a branch
    assert log["LEAD.rda"]["commit"] in log["LEAD.rda"]["url"]
    assert {"V-Party v2", "DPI 2023", "PLAD v7"} == set(log["sources_non_utilisées"])
    for info in log["sources_non_utilisées"].values():
        assert info["formulaire"] and info["raison"].startswith("non testable")
    assert "@" not in log["user_agent"]                       # no personal data in the requests


def test_restricted_files_are_not_committed():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for name in ["data/raw/lead/", "data/processed/ml_static_leaders.csv", "data/processed/ml_timevarying_leaders.csv"]:
        assert name in ignored, name


# ---------------------------------------------------------------------------------------- notebook outputs
@needs_notebook
def test_existing_data_unchanged():
    meta = json.loads((PROC / "ml_metadata.json").read_text(encoding="utf-8"))
    for new, base, key, features in (("ml_static_leaders.csv", "ml_static.csv", "spell_id", meta["static"]["features"]),
                                     ("ml_timevarying_leaders.csv", "ml_timevarying.csv", "row_id",
                                      meta["timevarying"]["features"])):
        n, b = pd.read_csv(PROC / new), pd.read_csv(PROC / base)
        assert len(n) == len(b) and set(n[key]) == set(b[key])
        shared = [c for c in b.columns if c != key]
        same = n.set_index(key).loc[b[key], shared].reset_index(drop=True)
        pd.testing.assert_frame_equal(same, b[shared], check_dtype=False)
        assert set(features) <= set(shared)


@needs_notebook
@needs_archigos
def test_leader_of_each_task(links, archigos):
    """Task A: the leader of the table, in the entry year. Task B: the Archigos leader on 31 December of the previous
    year, except before the arrival of the leader of the table (his values then) and for the parties without a link
    (no leader values); nothing after 2015, nothing carried forward from one leader to another."""
    leaders, dec31 = archigos
    s = pd.read_csv(PROC / "ml_static_leaders.csv", keep_default_na=False, na_values=[""])
    link = links.set_index("spell_id")
    assert (s["obsid"].fillna("") == s["spell_id"].map(link["obsid"])).all()
    no_link = s["obsid"].isna()
    assert s.loc[no_link, LEADER_VARIABLES].isna().all().all()
    born = s["obsid"].map(leaders["yrborn"])
    has = born.notna() & ~no_link
    np.testing.assert_allclose(s.loc[has, "leader_age"], s.loc[has, "entry_year"] - born[has])

    t = pd.read_csv(PROC / "ml_timevarying_leaders.csv", keep_default_na=False, na_values=[""])
    assert (t["lag_year"] == t["panel_year"] - 1).all()
    assert t.loc[t["lag_year"] > ARCHIGOS_LAST_YEAR, LEADER_VARIABLES].isna().all().all()
    without = t["spell_id"].isin(links.loc[links["obsid"] == "", "spell_id"])
    assert t.loc[without, LEADER_VARIABLES].isna().all().all()
    assert t.groupby("spell_id")["party_age"].nunique(dropna=False).max() == 1     # the age at entry, every year
    yearly = t["leader_rule"] == "Archigos, 31 décembre"
    expected = [dec31.get((c, y), "") for c, y in zip(t.loc[yearly, "cow"].replace({679: 678}), t.loc[yearly, "lag_year"])]
    assert (t.loc[yearly, "obsid"].to_numpy() == np.array(expected)).all()
    first = t["leader_rule"] == "dirigeant de la table (première année)"
    in_table = t["spell_id"].isin(link.index)
    assert (t.loc[first & in_table, "obsid"] == t.loc[first & in_table, "spell_id"].map(link["obsid"])).all()
    born_b = t["obsid"].map(leaders["yrborn"])
    has_b = born_b.notna()
    np.testing.assert_allclose(t.loc[has_b, "leader_age"], t.loc[has_b, "lag_year"] - born_b[has_b])


@needs_notebook
@needs_lead
def test_lead_values_copied_without_recoding():
    lead = pd.read_csv(RAW / "lead" / "LEAD.csv").set_index("obsid")
    for name in ("ml_static_leaders.csv", "ml_timevarying_leaders.csv"):
        d = pd.read_csv(PROC / name, keep_default_na=False, na_values=[""]).dropna(subset=["obsid"])
        d = d[d["obsid"].isin(lead.index)]
        src = lead.loc[d["obsid"]]
        for v, col in (("leader_military", "milservice"), ("leader_rebel", "rebel"), ("leader_experience", "yrsexper")):
            np.testing.assert_array_equal(d[v].to_numpy(float), src[col].to_numpy(float))
        university = np.where(src["leveledu"].isna(), np.nan, (src["leveledu"] >= 2).astype(float))
        np.testing.assert_array_equal(d["leader_university"].to_numpy(float), university)


@needs_notebook
def test_coverage_and_screening(results):
    s = pd.read_csv(PROC / "ml_static_leaders.csv")
    t = pd.read_csv(PROC / "ml_timevarying_leaders.csv")
    cov = table(results["coverage"]).set_index("variable")
    assert list(cov.index) == VARIABLES
    for v, row in cov.iterrows():
        a, b = s[v].notna(), t[v].notna()
        assert row["A : partis"] == a.sum() and row["A : chutes"] == (a & s["event"].eq(1)).sum()
        assert row["B : parti-années"] == b.sum() and row["B : chutes"] == (b & t["event"].eq(1)).sum()
    screening, protocol = results["screening"], results["protocol"]
    assert protocol["largest_model_parameters"] == {"A": 15, "B": 15}
    cand = screening["retained"]
    meta = json.loads((PROC / "ml_metadata.json").read_text(encoding="utf-8"))
    sa = s.dropna(subset=meta["static"]["features"] + cand + ["log_gdppc_entry"])
    tb = t.dropna(subset=meta["timevarying"]["features"] + cand)
    info = results["sample"]
    assert (info["spells"], info["events"]) == (len(sa), sa["event"].sum())
    assert (info["rows_tv"], info["events_tv"]) == (len(tb), tb["event"].sum())
    assert info["spell_ids_sha1"] == hashlib.sha1("|".join(sorted(sa["spell_id"])).encode("utf-8")).hexdigest()
    assert info["row_ids_sha1"] == hashlib.sha1("|".join(map(str, sorted(tb["row_id"]))).encode("utf-8")).hexdigest()
    for events in (info["events"], info["events_tv"]):
        assert events >= protocol["min_falls"] and events / 15 >= protocol["min_events_per_parameter"]
    assert set(screening["dropped"]) == {v for v in VARIABLES
                                         if min(cov.loc[v, "A : chutes"], cov.loc[v, "B : chutes"]) < protocol["min_falls"]}


@needs_notebook
def test_compared_models_use_same_rows(results):
    for task, n in (("A", results["sample"]["spells"]), ("B", results["sample"]["rows_tv"])):
        cv = pd.read_csv(PROC / f"leaders_cv_task{task}.csv")
        folds = cv.groupby(["comparison", "repetition", "fold"])[["n_train", "n_test", "events_test"]].nunique()
        assert (folds == 1).all().all()
        assert (cv.groupby(["comparison", "model"]).size() == results["protocol"]["evaluations"]).all()
        for _, d in cv[cv["comparison"] == "partis et dirigeants"].groupby(["model", "repetition"]):
            assert d["n_test"].sum() == n and (d["n_train"] + d["n_test"] == n).all()


@needs_notebook
def test_decision_rules(results):
    d = table(results["decision"]).set_index("variable")
    combined = table(results["models"]["combined"]).set_index("variable")
    tests = table(results["cv"]["task_a"]["tests"]).set_index("modèle")
    alpha = results["protocol"]["alpha"]
    np.testing.assert_allclose(d["p Holm"], multipletests(d["p (A)"], method="holm")[1])
    assert (d["1. Holm < 0,05"] == (d["p Holm"] < alpha)).all()
    for v, r in d.iterrows():
        c = combined.loc[v]
        assert r["2. même sens"] == bool(np.sign(c["A coef"]) == np.sign(c["B coef"])), v
        assert r["écart C (A)"] == pytest.approx(tests.loc[f"P2·{v}", "C de Harrell : écart"])
        assert r["3. C > M0"] == bool(r["écart C (A)"] > 0 and r["p corrigée C"] < alpha), v
        assert r["4. contrôles"] == bool(np.sign(c["contrôle A coef"]) == np.sign(c["A coef"]) and c["contrôle A p"] < alpha
                                         and np.sign(c["contrôle B coef"]) == np.sign(c["A coef"])), v
    kept = d["1. Holm < 0,05"] & d["2. même sens"] & d["3. C > M0"] & d["4. contrôles"]
    assert (d["retenue"] == kept).all()
    assert sorted(results["kept"]) == sorted(d.index[kept])
    if not results["kept"]:
        assert results["final_model"] is None
    assert results["coef_check_max_gap"] < 1e-3      # clustered form of the model = project's time-varying model
    assert results["protocol"]["rules_written"] <= results["protocol"]["rules_approved"] <= results["created"]


def walk_tables(obj, path=""):
    if isinstance(obj, dict):
        if {"columns", "index", "data"} <= set(obj):
            yield path, obj
        for k, v in obj.items():
            yield from walk_tables(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_tables(v, f"{path}[{i}]")


@needs_notebook
def test_export_has_no_lead_or_leader_values(results):
    """Only result tables are exported: no country-year, no party-year, no leader, no LEAD value (LEAD has no
    licence allowing redistribution)."""
    tables = list(walk_tables(results))
    assert tables
    for path, split in tables:
        columns = set(map(str, split["columns"]))
        assert not IDENTIFYING_COLUMNS & columns and not LEAD_COLUMNS & columns, path
        assert len(split["data"]) < 100, path
    assert not OBSID.search(json.dumps(results, ensure_ascii=False))


@needs_notebook
def test_site_texts(results, links):
    """Texts of the Analyse card in French, English and Arabic, rebuilt from the export's numbers by src/site_text.py:
    no variable code, no leader's name, no Archigos identifier; Arabic uses Latin digits."""
    sys.path.insert(0, str(ROOT / "src"))
    from site_text import leaders_texts
    texts = results["texts"]
    assert set(texts) == {"fr", "en", "ar"}
    assert leaders_texts(results) == json.loads(json.dumps(texts))       # the export holds the current texts
    names = [n for n in links["leader"].unique() if n]
    for lang, t in texts.items():
        assert len(t["labels"]) == len(t["definitions"]) == len(t["units"]) == len(VARIABLES)
        body = json.dumps(t, ensure_ascii=False)
        assert "`" not in body and not [v for v in VARIABLES if v in body], lang
        assert not OBSID.search(body) and not [n for n in names if re.search(rf"\b{re.escape(n)}\b", body)], lang
    assert not re.search("[٠-٩]", json.dumps(texts["ar"], ensure_ascii=False))


def test_leaders_are_not_simulation_inputs():
    for path in (ROOT / "src" / "cox_static_model.json", ROOT / "frontend" / "data" / "model.js"):
        if path.exists():
            text = path.read_text(encoding="utf-8")
            assert not [v for v in VARIABLES if re.search(rf"\b{v}\b", text)], path
