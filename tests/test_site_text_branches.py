"""Branches of the texts of src/site_text.py that the current results never reach: a variable kept, a variable that
meets every condition but one (for each condition), no variable or several variables that cannot be tested.

The texts are rebuilt from altered copies of the exports of notebooks 04, 05 and 06
(data/processed/site_results_{demo,shocks,leaders}.json); the files themselves are not changed. A text must never
present a failed condition as met."""
import copy
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "src"))
import site_text as ST  # noqa: E402

LANGS = ("fr", "en", "ar")
# For each export: its text builder, its conditions in order, the English words that show a condition as met in the
# list of an "almost kept" paragraph (None: the paragraph does not list them) and those that state its failure
BUILDERS = {
    "demo": {"build": ST.demo_texts,
             "conditions": ["1. Holm < 0,05", "2. même sens", "3. C > M0", "4. contrôle"],
             "met": {1: "in task A (", 2: "the same direction in task B", 3: "a C-index gain",
                     4: "the effect survives the control"},
             "failed": {1: "does not remain significant after the Holm correction",
                        2: "changes direction between tasks A and B", 3: "does not clearly improve the C-index",
                        4: "does not survive the control"}},
    "shocks": {"build": ST.shocks_texts,
               "conditions": ["1. Holm < 0,05", "2. ROC-AUC > M0", "3. époque"],
               "met": {1: "after the Holm correction", 2: "a ROC-AUC gain in cross-validation",
                       3: "an effect that survives the period control"},
               "failed": {1: "does not remain significant after the Holm correction",
                          2: "does not clearly improve the ROC-AUC", 3: "does not survive the period control"}},
    "leaders": {"build": ST.leaders_texts,
                "conditions": ["1. Holm < 0,05", "2. même sens", "3. C > M0", "4. contrôles"],
                "met": None,
                "failed": {1: "does not remain significant after the Holm correction", 2: "changes direction in task B",
                           3: "does not clearly improve the C-index", 4: "does not survive the period and GDP controls"}},
}
EXPORTS = {name: PROC / f"site_results_{name}.json" for name in BUILDERS}
pytestmark = pytest.mark.skipif(not all(p.exists() for p in EXPORTS.values()),
                                reason="run notebooks 04, 05 and 06 first")


@pytest.fixture(scope="module")
def exports():
    return {name: json.loads(path.read_text(encoding="utf-8")) for name, path in EXPORTS.items()}


def col(split, name):
    return split["columns"].index(name)


def cell(split, row, name):
    return split["data"][row][col(split, name)]


def set_conditions(D, row, conditions, failing=None):
    """Every condition of one row met, except `failing` (a column name), which is not."""
    dec = D["decision"]
    for c in conditions:
        dec["data"][row][col(dec, c)] = c != failing


def check_text(texts):
    """Same keys in the three languages, no placeholder or missing value left, Latin digits in Arabic."""
    assert set(texts) == set(LANGS)
    ST.same_text_in_all_languages(texts)
    for lang in LANGS:
        body = json.dumps(texts[lang], ensure_ascii=False)
        assert not re.search(r"\{\w+\}|\bnan\b|\bNaN\b|\binf\b", body), lang
        if lang != "en":                       # "None has a p-value..." is an English sentence
            assert not re.search(r"\bNone\b", body), lang
    assert not re.search("[٠-٩]", json.dumps(texts["ar"], ensure_ascii=False))


def paragraphs(text, lang="en"):
    head = {"fr": "**Presque ", "en": "**Almost kept: ", "ar": "**"}[lang]
    return [p.strip() for p in text.split(head)[1:]] if lang != "ar" else text.count("**") // 2


def near_cases():
    """(export, row, failing condition number): one case per condition; for notebook 04, a variable of block A (three
    conditions) and one of block B (four conditions)."""
    cases = []
    for name, spec in BUILDERS.items():
        n = len(spec["conditions"])
        if name == "demo":
            cases += [(name, "A", k) for k in range(1, 4)] + [(name, "B", k) for k in range(1, 5)]
        else:
            cases += [(name, None, k) for k in range(1, n + 1)]
    return cases


def demo_row(D, block):
    dec = D["decision"]
    return next(i for i, r in enumerate(dec["data"]) if r[col(dec, "bloc")] == block)


@pytest.mark.parametrize("name, block, k", near_cases())
def test_almost_kept_lists_only_the_conditions_met(exports, name, block, k):
    spec = BUILDERS[name]
    base = exports[name]
    row = demo_row(base, block) if name == "demo" else 0
    conditions = list(spec["conditions"])
    if name == "demo" and cell(base["decision"], row, "4. contrôle") is None:
        conditions = conditions[:3]                       # block A: no control, three conditions
    D = copy.deepcopy(base)
    set_conditions(D, row, conditions, failing=conditions[k - 1])
    texts = spec["build"](D)
    check_text(texts)
    before = paragraphs(spec["build"](base)["en"]["near"])
    new = [p for p in paragraphs(texts["en"]["near"]) if p not in before]
    assert len(new) == 1, new                             # the altered variable, and only it, is almost kept
    paragraph = new[0]
    assert spec["failed"][k] in paragraph
    if spec["met"]:
        listed = paragraph.split("conditions: ", 1)[1].split(". But ", 1)[0]
        assert spec["met"][k] not in listed                # a failed condition is never shown as met
        for j in range(1, len(conditions) + 1):
            if j != k:
                assert spec["met"][j] in listed, (j, listed)
    for lang in ("fr", "ar"):                              # the same paragraphs in the three languages
        n_en = len(paragraphs(texts["en"]["near"]))
        n = len(paragraphs(texts[lang]["near"], lang)) if lang == "fr" else paragraphs(texts[lang]["near"], lang)
        assert n == n_en, lang


@pytest.mark.parametrize("name", list(BUILDERS))
def test_kept_variable(exports, name):
    spec = BUILDERS[name]
    D = copy.deepcopy(exports[name])
    row = demo_row(D, "B") if name == "demo" else 0
    set_conditions(D, row, spec["conditions"])
    D["decision"]["data"][row][col(D["decision"], "retenue")] = True
    D["kept"] = [cell(D["decision"], row, "variable")]
    texts = spec["build"](D)
    check_text(texts)
    assert texts["en"]["answer"].startswith("According to the rules set before the results, 1 variable")


@pytest.mark.parametrize("name", ["demo", "shocks"])
def test_no_untestable_variable(exports, name):
    D = copy.deepcopy(exports[name])
    D["screening"].update({"dropped": {}, "removed_for_sample": {}, "removed_reason": {}})
    check_text(BUILDERS[name]["build"](D))


def test_untestable_leader_variables(exports):
    D = copy.deepcopy(exports["leaders"])
    D["screening"].update({"dropped": {"leader_rebel": "100 chutes en Tâche A, 110 en Tâche B"},
                           "removed_for_sample": {"leader_university": {"falls_a": 100, "falls_b": 110}},
                           "removed_reason": {"leader_university": "échantillon commun"}})
    texts = ST.leaders_texts(D)
    check_text(texts)
    for v in ("leader_rebel", "leader_university"):
        assert ST.LEADER_VARS[v]["en"][0] in texts["en"]["testable"], v
