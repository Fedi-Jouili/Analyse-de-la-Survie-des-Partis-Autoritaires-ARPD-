"""Checks of the website's data files (frontend/data/*.js, built by frontend/build_data.py) and of its
dictionaries (frontend/assets/i18n/*.js): schemas, every ARPD party-year drawn on the globe, the three
languages present for every text and name, and the same keys in the three dictionaries."""
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / "frontend"
sys.path.insert(0, str(FRONT))
from build_data import ANNEXED, NO_PARTY_EXCEPTIONS, expand_image  # noqa: E402
LANGS = ("fr", "en", "ar")
YEAR_MIN, YEAR_MAX = 1946, 2024
PLURAL = {"zero", "one", "two", "few", "many", "other"}


def load_site(name, variable):
    text = (FRONT / "data" / name).read_text(encoding="utf-8")
    return json.loads(text.split(f"window.SITE.{variable} = ", 1)[1].rstrip().rstrip(";"))


def load_dict(lang):
    text = (FRONT / "assets" / "i18n" / f"{lang}.js").read_text(encoding="utf-8")
    return json.loads(text.split(f"window.I18N_DICT.{lang} = ", 1)[1].rstrip().rstrip(";"))


def is_plural(value):
    return isinstance(value, dict) and "other" in value and set(value) <= PLURAL


def flatten(d, prefix=""):
    """Dictionary -> {dotted key: leaf}; plural objects are leaves."""
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and not is_plural(v):
            out.update(flatten(v, key + "."))
        else:
            out[key] = v
    return out


def is_names(value):
    return isinstance(value, dict) and set(value) == set(LANGS) and all(isinstance(value[l], str) and value[l].strip()
                                                                          for l in LANGS)


@pytest.fixture(scope="module")
def atlas():
    return load_site("atlas.js", "atlas")


@pytest.fixture(scope="module")
def countries():
    return load_site("countries.js", "countries")


@pytest.fixture(scope="module")
def stats():
    return load_site("stats.js", "stats")


@pytest.fixture(scope="module")
def game():
    return load_site("model.js", "game")


@pytest.fixture(scope="module")
def dicts():
    return {lang: load_dict(lang) for lang in LANGS}


# ---------------------------------------------------------------- data schemas
def test_countries_schema(countries):
    assert countries["type"] == "FeatureCollection" and len(countries["features"]) > 200
    for f in countries["features"]:
        assert f["id"] == f["properties"]["id"]
        assert is_names(f["properties"]["name"]), f["id"]
        assert f["geometry"]["type"] in ("Polygon", "MultiPolygon")


def test_atlas_schema(atlas, countries):
    assert atlas["years"] == [YEAR_MIN, YEAR_MAX]
    assert atlas["fields"] == ["category", "spell", "vdem_regime", "polyarchy_x1000", "leader", "label", "inherited",
                               "flag"]
    ids = {f["id"] for f in countries["features"]}
    assert set(atlas["polygons"]) == ids
    n_years = YEAR_MAX - YEAR_MIN + 1
    n_images = len(atlas["images"])
    for pid, poly in atlas["polygons"].items():
        assert len(poly["rows"]) == n_years, pid
        for cat, spell, regime, polyarchy, leader, label, inherited, flag in poly["rows"]:
            assert 0 <= cat < len(atlas["categories"])
            assert -1 <= spell < len(atlas["spells"])
            assert regime in (-1, 0, 1, 2, 3) and -1 <= polyarchy <= 1000
            assert -1 <= leader < len(atlas["leaders"])
            assert 0 <= label < len(atlas["labels"]) and inherited in (0, 1, 2)
            assert -1 <= flag < n_images
        for sec in poly["secondary"]:
            assert is_names(sec["label"])
            assert len(sec["rows"]) == sec["last"] - sec["first"] + 1
            assert all(r is None or (len(r) == 6 and -1 <= r[5] < n_images) for r in sec["rows"])
    assert all(is_names(lab) for lab in atlas["labels"])
    for s in atlas["spells"]:
        assert is_names(s["label"]) and s["start"] <= s["end"]


def test_no_party_periods_split_by_regime(atlas):
    """Libya had no ruling party from 1951 on, but three regimes: Idris's monarchy, Qaddafi's personalist regime,
    then civil war. The globe shows them separately, and never an accession mode that the ARPD does not give."""
    libya = sorted((s for s in atlas["spells"] if s["country"] == "Libya"), key=lambda s: s["start"])
    assert [s["type"] for s in libya][:3] == ["monarchy", "personal", "civil_war"] or \
           [s["type"] for s in libya][:2] == ["monarchy", "personal"], [(s["start"], s["type"]) for s in libya]
    assert libya[0]["start"] == 1951 and libya[0]["end"] == 1969 and libya[1]["start"] == 1970
    assert all(s["gained"] is None and s["ended"] is None for s in atlas["spells"] if s["party"] is None)
    assert sum(s["ongoing"] for s in libya) == 1 and libya[-1]["ongoing"] == 1


def test_every_arpd_party_year_is_drawn(atlas):
    """Every ARPD party-year from 1946 to 2024 is drawn on a polygon (directly, through a union or as a secondary
    state). A polygon shows one regime per year: when two parties of the same state share a year (a handover),
    the globe shows one of them and the other is listed in that year's events; no other party-year is missing."""
    panel = pd.read_csv(ROOT / "data" / "processed" / "arpd_panel_merged.csv",
                        usecols=["Country", "Party", "Year in Power", "panel_year"], low_memory=False)
    panel = panel.loc[panel["panel_year"].between(YEAR_MIN, YEAR_MAX), ["Country", "Party", "Year in Power", "panel_year"]]
    # Periods without a party that the globe closes earlier than the ARPD (NO_PARTY_EXCEPTIONS of build_data.py)
    for (country, start), exception in NO_PARTY_EXCEPTIONS.items():
        if "end" in exception:
            panel = panel[~((panel["Country"].str.strip() == country) & (panel["Party"] == "N")
                            & (panel["Year in Power"] == start) & (panel["panel_year"] > exception["end"]))]
    # A period without a party (Party = "N") may be split into several regimes: find the segment of each year
    segments = {}
    for i, s in enumerate(atlas["spells"]):
        segments.setdefault((s["country"], s["party"] if s["party"] is not None else "N", s["arpd_start"]), []).append(i)

    def spell_of(country, party, start, year):
        found = [i for i in segments[(country, party, start)]
                 if (atlas["spells"][i]["start"] if atlas["spells"][i]["start"] > start else start) <= year
                 <= atlas["spells"][i]["end"]]
        assert len(found) == 1, (country, party, start, year, found)
        return found[0]
    expected = {(spell_of(country.strip(), party, int(start), int(year)), int(year))
                for country, party, start, year in panel.itertuples(index=False, name=None)}
    drawn = set()
    for poly in atlas["polygons"].values():
        drawn |= {(row[1], YEAR_MIN + i) for i, row in enumerate(poly["rows"]) if row[1] >= 0}
        for sec in poly["secondary"]:
            drawn |= {(row[1], sec["first"] + i) for i, row in enumerate(sec["rows"]) if row and row[1] >= 0}
    assert len(expected) > 6000
    spells = atlas["spells"]
    drawn_state_years = {(spells[sp]["state"], year) for sp, year in drawn}
    assert {(spells[sp]["state"], year) for sp, year in expected} <= drawn_state_years
    hidden = expected - drawn
    for sp, year in hidden:
        handover = [o for o, y in drawn if y == year and o != sp and spells[o]["state"] == spells[sp]["state"]]
        assert handover and year in (spells[sp]["start"], spells[sp]["end"]), (sp, year)
    assert len(hidden) <= 5, sorted(hidden)


def test_no_party_periods_closed_after_2015(atlas):
    """Sri Lanka's personalist period ends with Rajapaksa's defeat (2015); the Taliban form a new period from 2021."""
    def row(pid, year):
        return atlas["polygons"][pid]["rows"][year - YEAR_MIN]
    sri_lanka = [s for s in atlas["spells"] if s["country"] == "Sri Lanka" and s["arpd_start"] == 2010]
    assert [(s["end"], s["ongoing"]) for s in sri_lanka] == [(2015, 0)]
    assert all(row("LKA", y)[1] == -1 for y in range(2016, YEAR_MAX + 1))
    afghanistan = sorted((s for s in atlas["spells"] if s["country"] == "Afghanistan" and s["arpd_start"] == 2001),
                         key=lambda s: s["start"])
    assert (afghanistan[-1]["start"], afghanistan[-1]["type"], afghanistan[-1]["ongoing"]) == (2021, "theocracy", 1)
    assert afghanistan[-2]["end"] == 2020 and afghanistan[-2]["ongoing"] == 0


def test_borders_follow_the_un_position(countries):
    """Crimea belongs to Ukraine and Western Sahara is one territory, distinct from Morocco (UN position). Areas of the
    simplified polygons, in an equal-area projection, against the usual figures (Ukraine 603,500 km², Western
    Sahara 266,000 km²)."""
    geo = {f["id"]: shape(f["geometry"]) for f in countries["features"]}

    def km2(pid):
        return gpd.GeoSeries([geo[pid]], crs=4326).to_crs("ESRI:54034").area.iloc[0] / 1e6
    assert km2("UKR") == pytest.approx(603_500, rel=0.025)
    assert km2("SAH") == pytest.approx(266_000, rel=0.025)
    for place, lon, lat, pid in [("Simferopol", 34.10, 44.95, "UKR"), ("Sevastopol", 33.52, 44.60, "UKR"),
                                 ("Laayoune", -13.20, 27.15, "SAH"), ("Dakhla", -15.95, 23.70, "SAH"),
                                 ("Rabat", -6.84, 34.02, "MAR"), ("Moscow", 37.62, 55.75, "RUS")]:
        inside = [p for p, g in geo.items() if g.contains(Point(lon, lat))]
        assert inside == [pid], (place, inside)


def test_annexations_and_western_sahara(atlas):
    """Unrecognised annexations (Baltic states 1946-1991, East Timor 1976-1999) say "annexed by", not "part of";
    Western Sahara is a Spanish colony until 1975, then a non-self-governing territory."""
    labels = atlas["labels"]
    dependent = atlas["categories"].index("dependent")

    def row(pid, year):
        return atlas["polygons"][pid]["rows"][year - YEAR_MIN]
    assert ANNEXED == {"EST", "LVA", "LTU", "TLS"}
    for pid, first, last in [("EST", 1946, 1991), ("LVA", 1946, 1991), ("LTU", 1946, 1991), ("TLS", 1976, 1999)]:
        # Annexed every year, except a last year in which the ARPD already gives the territory its own regime
        annexed = [y for y in range(first, last + 1) if row(pid, y)[6] == 2]
        assert annexed == list(range(first, annexed[-1] + 1)) and annexed[-1] >= last - 1, pid
        assert all(row(pid, y)[6] == 0 and row(pid, y)[1] >= 0 for y in range(annexed[-1] + 1, last + 1)), pid
        assert row(pid, last + 1)[6] == 0, pid
        assert [n[:2] for n in atlas["polygons"][pid]["notes"]] == [[first, annexed[-1]]], pid
    assert all(row("UKR", y)[6] == 1 for y in range(1946, 1992))        # Soviet republic: "part of"
    assert ["crimea"] == [n[2] for n in atlas["polygons"]["UKR"]["notes"] if n[0] <= 2014 <= n[1]]
    for year, name in [(1946, "Sahara espagnol"), (1975, "Sahara espagnol"), (1976, "Sahara occidental"),
                       (YEAR_MAX, "Sahara occidental")]:
        cat, spell, _, _, _, label, inherited, flag = row("SAH", year)
        assert (cat, spell, labels[label]["fr"], inherited, flag) == (dependent, -1, name, 0, -1), year


@pytest.fixture(scope="module")
def media(atlas):
    """Flags, logos and portraits of the Atlas card (frontend/build_media.py); skipped when they were not collected."""
    if not atlas.get("media_created"):
        pytest.skip("data/raw/wikimedia_atlas.json absent: run frontend/build_media.py")
    wiki = {lang: load_site(f"wiki_{lang}.js", f"wiki_{lang}") for lang in LANGS}
    files = []
    for path, kind, host, licence, author in atlas["images"]:     # file name, as in atlas.js (fileName)
        parts = path.split("/")
        files.append(unquote(parts[3] if parts[0] == "thumb" else parts[-1]).replace("_", " "))
    return {"wiki": wiki, "files": files}


def flag_file(atlas, media, pid, year):
    i = atlas["polygons"][pid]["rows"][year - YEAR_MIN][7]
    return media["files"][i] if i >= 0 else None


def test_media_tables(atlas, media):
    """Every image is a free file of Wikimedia Commons with its licence; people and parties point to existing images
    and to Wikipedia extracts of the right language; no personal data in the User-Agent of the collection."""
    assert atlas["image_hosts"] == ["https://upload.wikimedia.org/wikipedia/commons/",
                                    "https://thumb.wikimedia.org/wikipedia/commons/"]
    assert atlas["image_width"] == 120
    snapshot = json.loads((ROOT / "data" / "raw" / "wikimedia_atlas.json").read_text(encoding="utf-8"))
    thumbs = {v["thumb"].split("?")[0] for v in snapshot["files"].values()}
    for path, kind, host, licence, author in atlas["images"]:
        assert "?" not in path and licence.strip() and host in (0, 1) and kind in (0, 1, 2, 3)
        assert re.match(r"^(thumb/)?[0-9a-f]/[0-9a-f]{2}/", path), path
        assert atlas["image_hosts"][host] + expand_image(path, kind) in thumbs, path   # same address as Commons gave
    n_images = len(atlas["images"])
    for qid, image, titles in atlas["people"]:
        assert re.fullmatch(r"Q\d+", qid) and -1 <= image < n_images and set(titles) <= set(LANGS)
        assert all(t in media["wiki"][lang] for lang, t in titles.items())
    n_people = len(atlas["people"])
    for hos, hos_title, hog, hog_title, main, hos_person, hog_person in atlas["leaders"]:
        assert main in (0, 1) and (main == 0 or hog) and -1 <= hos_person < n_people and -1 <= hog_person < n_people
    for s in atlas["spells"]:
        assert ("media" in s) == bool(s["party"])
        for first, last, logo, since, exists, titles in s.get("media", []):
            assert -1 <= logo < n_images and exists in (0, 1)
            assert all(t in media["wiki"][lang] for lang, t in titles.items())
    for lang in LANGS:
        assert media["wiki"][lang] and all(0 < len(text) <= 420 for text in media["wiki"][lang].values()), lang
    assert "@" not in snapshot["user_agent"]


def test_flags_by_period(atlas, media):
    """The flag is the one of the state shown, in force at the end of the year; none when no dated flag covers the year
    and none for territories that are not sovereign."""
    dependent = atlas["categories"].index("dependent")
    nodata = atlas["categories"].index("nodata")
    for poly in atlas["polygons"].values():
        assert all(r[7] == -1 for r in poly["rows"] if r[0] in (dependent, nodata))
    assert flag_file(atlas, media, "LBY", 1960) == "Flag of Libya.svg"                 # Kingdom, 1951-1969
    assert flag_file(atlas, media, "LBY", 1990) == "Flag of Libya (1977–2011).svg"     # green flag of Gaddafi
    assert flag_file(atlas, media, "AFG", 2022) == "Flag of the Taliban.svg"
    assert flag_file(atlas, media, "UKR", 1980) == flag_file(atlas, media, "RUS", 1980) == "Flag of the Soviet Union.svg"
    assert flag_file(atlas, media, "RUS", 2000) == "Flag of Russia.svg"
    assert flag_file(atlas, media, "IRN", 1990) == "Flag of Iran.svg"
    assert flag_file(atlas, media, "DEU", 1947) is None                                # no German flag under occupation
    assert flag_file(atlas, media, "SAH", 2000) is None                                # non-self-governing territory


def test_people_and_parties(atlas, media):
    """Leaders are linked to the right people (checked on well-known cases) and parties to their articles."""
    def leader(pid, year):
        r = atlas["polygons"][pid]["rows"][year - YEAR_MIN]
        return atlas["leaders"][r[4]]

    def english_title(person):
        return atlas["people"][person][2].get("en") if person >= 0 else None
    assert english_title(leader("CUB", 1980)[5]) == "Fidel Castro"
    assert english_title(leader("CHL", 1980)[5]) == "Augusto Pinochet"
    assert english_title(leader("IRQ", 1990)[5]) == "Saddam Hussein"
    assert english_title(leader("RUS", 1990)[5]) == "Mikhail Gorbachev"
    thai = leader("THA", 1960)                    # the head of government (Sarit) rules, not the king
    assert thai[4] == 1 and english_title(thai[6]) == "Sarit Thanarat"
    by_party = {(s["country"], s["party"]): s for s in atlas["spells"] if s["party"]}
    cpsu = by_party[("USSR", "Communist Party of the Soviet Union")]["media"]
    assert cpsu[0][5].get("en") == "Communist Party of the Soviet Union" and cpsu[0][2] >= 0
    tunisia = [s for (c, p), s in by_party.items() if c == "Tunisia" and p.startswith("Neo-Destour")][0]["media"]
    assert [m[5].get("en") for m in tunisia] == ["Neo Destour", "Socialist Destourian Party",
                                                 "Democratic Constitutional Rally"]


def test_monarchy_is_not_a_model_choice(game, stats):
    """Monarchy (coded year by year, descriptive only) is in no model: not in the exported Cox model, not among the
    simulation's choices, not among the hazard ratios shown on the analysis page."""
    model = game["model"]
    assert "Monarchy" not in model["model"]["features"] and "monarchy" not in model["form"]["booleans"]
    assert "monarchy" not in model["support"] and "Monarchy" not in game["analog_features"]
    for block in stats["panel"]["models"].values():
        assert "Monarchy" not in {h["covariate"] for h in block["hazard_ratios"]}


def test_stats_texts_in_three_languages(stats):
    for block in ("eda", "panel", "ml", "demo", "shocks", "leaders"):
        texts = stats[block]["texts"]
        assert set(texts) == set(LANGS), block
        keys = set(texts["fr"])
        for lang in LANGS:
            assert set(texts[lang]) == keys, (block, lang)
            for k, v in texts[lang].items():
                items = v if isinstance(v, list) else [v]
                assert items, (block, lang, k)
                for item in items:
                    strings = [item["title"], item["body"]] if isinstance(item, dict) else [item]
                    assert all(isinstance(s, str) and s.strip() for s in strings), (block, lang, k)
            for k, v in texts["fr"].items():
                if isinstance(v, list):
                    assert len(texts[lang][k]) == len(v), (block, lang, k)
    assert len(stats["ml"]["texts"]["fr"]["linearity_shapes"]) == len(stats["ml"]["interpretation"]["linearity"]["data"])
    # No dataset code left in running text ("Clientelist" is a correct English word); Arabic uses Latin digits
    for lang in LANGS:
        body = json.dumps(stats["panel"]["texts"][lang], ensure_ascii=False)
        assert "Dictator-Created" not in body and "Policy-Based" not in body, lang
        if lang != "en":
            assert "Clientelist" not in body, lang
    assert not re.search("[٠-٩]", json.dumps(stats["panel"]["texts"]["ar"], ensure_ascii=False))
    assert not re.search("[٠-٩]", json.dumps(stats["demo"]["texts"]["ar"], ensure_ascii=False))
    assert not re.search("[٠-٩]", json.dumps(stats["shocks"]["texts"]["ar"], ensure_ascii=False))
    assert not re.search("[٠-٩]", json.dumps(stats["leaders"]["texts"]["ar"], ensure_ascii=False))


def test_shock_results_on_the_site(stats):
    """The analysis page gets the results of 05_shocks.ipynb (tables, scores, texts), never the country-year values:
    some come from EM-DAT, whose licence forbids distributing adapted data."""
    shocks = stats["shocks"]
    assert set(shocks) == {"source", "created", "protocol", "totals", "candidates", "coverage", "screening", "sample",
                           "splice", "decision", "kept", "models", "cv", "texts"}
    assert set(shocks["models"]) == {"combined", "descriptive"}
    n = len(shocks["candidates"]["data"])
    for lang in LANGS:
        assert len(shocks["texts"][lang]["labels"]) == len(shocks["texts"][lang]["definitions"]) == n

    def tables(obj):
        if isinstance(obj, dict):
            if {"columns", "index", "data"} <= set(obj):
                yield obj
            for v in obj.values():
                yield from tables(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from tables(v)
    for split in tables(shocks):
        assert not {"cow", "year", "panel_year", "lag_year", "Country", "spell_id", "row_id"} & set(split["columns"])


def test_strategy_logrank_excludes_not_coded(stats):
    """Card 01 compares the coded strategies only: « Non codé » is not a strategy (02_eda_and_data_processing.ipynb)."""
    gov = stats["eda"]["km_by"]["governance"]
    coded = [g for g in gov["groups"] if g["level"] != "Non codé"]
    assert len(coded) == len(gov["groups"]) - 1
    assert gov["logrank_coded"]["excluded"] == ["Non codé"]
    assert gov["logrank_coded"]["df"] == len(coded) - 1 == gov["logrank_df"] - 1
    assert 0 < gov["logrank_coded"]["p"] < 1


def split_tables(obj):
    """Every table in pandas' "split" format inside an export."""
    if isinstance(obj, dict):
        if {"columns", "index", "data"} <= set(obj):
            yield obj
        for v in obj.values():
            yield from split_tables(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from split_tables(v)


def test_leader_results_on_the_site(stats):
    """The analysis page gets the results of 06_party_leaders.ipynb (tables, scores, texts), never the values of a
    leader, a party-year or LEAD, whose licence is not stated."""
    leaders = stats["leaders"]
    assert set(leaders) == {"source", "created", "protocol", "totals", "links", "candidates", "coverage",
                            "task_b_leader_rules", "screening", "sample", "decision", "kept", "models", "cv", "texts"}
    assert set(leaders["models"]) == {"combined", "descriptive"}
    n = len(leaders["candidates"]["data"])
    for lang in LANGS:
        assert len(leaders["texts"][lang]["labels"]) == len(leaders["texts"][lang]["definitions"]) == n
    # The page translates the leader rule of each party-year from these labels (analyse.js, leadersDetails)
    last = leaders["protocol"]["archigos_last_year"]
    assert {r[0] for r in leaders["task_b_leader_rules"]["data"]} <= {
        "Archigos, 31 décembre", "dirigeant de la table (première année)", "parti sans lien", f"après {last}"}
    for split in split_tables(leaders):
        columns = set(map(str, split["columns"]))
        assert not {"cow", "ccode", "year", "panel_year", "lag_year", "Country", "spell_id", "row_id", "obsid",
                    "leader", "leader_start"} & columns
        assert not {"leveledu", "milservice", "rebel", "yrsexper"} & columns
    assert not re.search(r"\b[A-Z]{3}-\d{4}(?:-\d+)?\b", json.dumps(leaders, ensure_ascii=False))


def test_country_results_on_the_site(stats):
    """The analysis page gets the results of 04_demographics.ipynb (tables, scores, texts), never the country-year
    values: some come from QoG, whose terms forbid redistribution."""
    demo = stats["demo"]
    assert set(demo) == {"source", "created", "protocol", "blocks", "totals", "candidates", "coverage", "screening",
                         "samples", "decision", "kept", "models", "cv", "texts"}
    assert set(demo["models"]) == {"combined", "descriptive"}
    n = len(demo["candidates"]["data"])
    for lang in LANGS:
        assert len(demo["texts"][lang]["labels"]) == n


def test_game_data(game):
    assert set(game) >= {"model", "analogs", "analog_features", "km_overall", "sample_all"}
    assert len(game["analogs"]) == game["model"]["sample"]["spells"]
    for a in game["analogs"]:
        assert is_names(a["label"]) and len(a["x"]) == len(game["analog_features"])


# ---------------------------------------------------------------- dictionaries
def test_same_keys_in_the_three_dictionaries(dicts):
    flat = {lang: flatten(d) for lang, d in dicts.items()}
    for lang in ("en", "ar"):
        assert set(flat[lang]) == set(flat["fr"]), (lang, sorted(set(flat["fr"]) ^ set(flat[lang]))[:10])


def test_dictionary_values_and_placeholders(dicts):
    flat = {lang: flatten(d) for lang, d in dicts.items()}

    def placeholders(value):
        if isinstance(value, dict):
            return set().union(*(placeholders(v) for v in value.values())) - {"count"}
        if isinstance(value, list):
            return set().union(set(), *(placeholders(v) for v in value))
        return set(re.findall(r"\{(\w+)\}", value)) - {"count"} if isinstance(value, str) else set()

    def strings(value):
        if isinstance(value, dict):
            return [s for v in value.values() for s in strings(v)]
        if isinstance(value, list):
            return [s for v in value for s in strings(v)]
        return [value]

    for key, value in flat["fr"].items():
        for lang in LANGS:
            other = flat[lang][key]
            assert all(isinstance(s, str) and s.strip() for s in strings(other)), (lang, key)
            assert placeholders(other) == placeholders(value), (lang, key)
        if is_plural(value):
            assert is_plural(flat["ar"][key]) or "{count}" not in flat["ar"][key], key
    # Arabic plurals use the six CLDR categories
    for key, value in flat["ar"].items():
        if is_plural(value):
            assert set(value) == PLURAL, key


def test_keys_used_by_the_pages_exist(dicts):
    flat = flatten(dicts["fr"])
    used = set()
    for path in list(FRONT.glob("*.html")) + list((FRONT / "assets" / "js").glob("*.js")):
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".html":
            used |= set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', text))
            for attr in re.findall(r'data-i18n-attr="([^"]+)"', text):
                used |= {pair.split(":")[1].strip() for pair in attr.split(";")}
        used |= set(re.findall(r'\b(?:t|I18n\.t|I18n\.tHtml|I18n\.tList|I18n\.get)\(\s*"([a-z]\w*\.[\w.]+)"', text))
    missing = sorted(k for k in used if k not in flat and not any(f.startswith(k + ".") for f in flat))
    assert not missing, missing


def test_every_dictionary_key_is_used(dicts):
    """No key stays in the dictionaries without a page that uses it. A key built at run time counts through its
    prefix: t(`analyse.shocks.col.${k}`) uses every key of analyse.shocks.col."""
    flat = flatten(dicts["fr"])
    used, prefixes = set(), set()
    for path in list(FRONT.glob("*.html")) + list((FRONT / "assets" / "js").glob("*.js")):
        text = path.read_text(encoding="utf-8")
        used |= set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', text))
        for attr in re.findall(r'data-i18n-attr="([^"]+)"', text):
            used |= {pair.split(":")[1].strip() for pair in attr.split(";")}
        used |= set(re.findall(r'["\'`]([a-z]\w*\.[\w.]+)["\'`]', text))
        prefixes |= set(re.findall(r'`([a-z]\w*(?:\.\w+)*)\.\$\{', text))
        prefixes |= {p.rstrip(".") for p in re.findall(r'["\']([a-z]\w*(?:\.\w+)+\.)["\']', text)}

    def is_used(key):
        parts = key.split(".")
        return key in used or any(".".join(parts[:i]) in used | prefixes for i in range(1, len(parts)))
    unused = sorted(k for k in flat if not is_used(k))
    assert not unused, unused


def test_keys_built_by_the_analysis_page_exist(dicts):
    """Keys that the analysis page builds at run time (table columns, verdicts, « how to read » boxes) exist. Most are
    in the folded details, which the browser test does not read."""
    flat = flatten(dicts["fr"])
    text = (FRONT / "assets" / "js" / "analyse.js").read_text(encoding="utf-8")
    # t(`analyse.shocks.verdict.${key}`): the part before ${ is a branch of the dictionary
    prefixes = set(re.findall(r"\bt\(`([a-z]\w*(?:\.\w+)*)\.\$\{", text))
    assert "analyse.leaders.col" in prefixes and "analyse.leaders.verdict" in prefixes
    assert not [p for p in prefixes if not any(k.startswith(p + ".") for k in flat)]
    for p in (p for p in prefixes if p.endswith(".verdict")):
        assert {f"{p}.{v}" for v in ("ref", "better", "worse", "none")} <= set(flat), p
    # const cols = (keys) => keys.map((k) => t(`analyse.leaders.col.${k}`)); then cols(["variable", "unit", ...])
    checked = 0
    for body in re.split(r"\n  function ", text):
        prefix = re.search(r"const cols = \(keys\) => keys\.map\(\(k\) => t\(`([\w.]+)\.\$\{k\}`\)\)", body)
        for group in re.findall(r"\bcols\(\[([^\]]*)\]\)", body) if prefix else []:
            for key in re.findall(r'"(\w+)"', group):
                assert f"{prefix.group(1)}.{key}" in flat, (prefix.group(1), key)
                checked += 1
    assert checked >= 30
    # howTo("leaders", ...) reads analyse.howto.leaders.title and .items
    for kind in set(re.findall(r'\bhowTo\("(\w+)"', text)):
        assert f"analyse.howto.{kind}.title" in flat and f"analyse.howto.{kind}.items" in flat, kind
    rules = re.search(r"const RULE = \{(.*?)\};", text, re.S).group(1)
    assert {f"analyse.leaders.rule.{k}" for k in re.findall(r':\s*"(\w+)"', rules)} <= set(flat)


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip, self.texts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.texts.append(data.strip())


@pytest.mark.parametrize("page", ["index", "atlas", "analyse", "simulation", "about"])
def test_no_untranslated_text_in_html(page):
    """Visible text comes from the dictionaries: the HTML only keeps numbers, symbols and proper names."""
    parser = TextCollector()
    parser.feed((FRONT / f"{page}.html").read_text(encoding="utf-8"))
    allowed = re.compile(r"^(?:[\d\s·:—–‹›▶✕]+|Fedi Jouili)$")
    leftovers = [t for t in parser.texts if not allowed.match(t)]
    assert not leftovers, leftovers
