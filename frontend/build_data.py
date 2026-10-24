"""Build the data files of the website (frontend/data/*.js).

Run from the project root:   python frontend/build_data.py

Inputs (all produced or downloaded earlier in the project):
- data/processed/arpd_panel_merged.csv           party-year panel (01_data_merging.ipynb)
- data/raw/V-Dem-CY-Full+Others-v16.csv           V-Dem, for regime classes, polyarchy and leader names
  (falls back to V-Dem-CY-Core-v16.csv, without leader names, if the full file is absent)
- data/raw/ne_50m_admin_0_countries.geojson       Natural Earth 1:50m country borders and names in French,
                                                  English and Arabic (public domain)
- data/raw/ne_50m_admin_0_breakaway_disputed_areas.geojson  Natural Earth 1:50m disputed areas (public domain), used
                                                  to draw Crimea and Western Sahara according to the UN position
- data/processed/site_results_{eda,panel,ml,demo,shocks,leaders}.json  results exported by notebooks 02,
                                                  final_panel, 03, 04, 05 and 06
- data/processed/ml_static.csv                    spells of the static model (final_panel.ipynb, Section 7.3)
- src/cox_static_model.json                       exported Cox model (final_panel.ipynb, Section 7.4)

Outputs (JavaScript files, so the site also works when opened directly from disk). Every name shown on the
site is given in the three languages of the site: {"fr": ..., "en": ..., "ar": ...}.
- frontend/data/countries.js   simplified country polygons
- frontend/data/atlas.js       regime of every country, every year (globe page)
- frontend/data/stats.js       notebook results (analysis page)
- frontend/data/model.js       Cox model + analog spells (simulation page)
"""
import json
import re
from datetime import date
from pathlib import Path

import geopandas as gpd
import shapely
import numpy as np
import pandas as pd
from shapely.geometry import mapping

ROOT = Path(__file__).resolve().parents[1]
RAW, PROCESSED, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed", ROOT / "frontend" / "data"
YEAR_MIN, YEAR_MAX = 1946, 2024
YEARS = list(range(YEAR_MIN, YEAR_MAX + 1))
SIMPLIFY_DEGREES = 0.04

# Same translation as 01_data_merging.ipynb: the ARPD uses Polity codes for these states
ARPD_TO_COW = {364: 365, 818: 816, 529: 530, 347: 345, 624: 625}
# ARPD states absent from V-Dem: ISO3 code of their polygon
ARPD_ONLY = {58: "ATG", 835: "BRN", 55: "GRD", 769: "PAK", 990: "WSM", 331: "SMR", 955: "TON"}
# V-Dem codes that differ from the Natural Earth codes
VDEM_ALIASES = {"XKX": "KOS", "SML": "SOL"}
LANGS = ("fr", "en", "ar")


def names(fr, en, ar):
    return {"fr": fr, "en": en, "ar": ar}


# Historical states without a polygon of their own: shown in the card of the polygon covering them today
SECONDARY = {"DDR": ("DEU", names("Allemagne de l'Est (RDA)", "East Germany (GDR)", "ألمانيا الشرقية")),
             "VDR": ("VNM", names("Viêt Nam du Sud", "South Vietnam", "فيتنام الجنوبية")),
             "YMD": ("YEM", names("Yémen du Sud", "South Yemen", "اليمن الجنوبي")),
             "PSG": ("PSX", names("Gaza", "Gaza", "غزة")),
             "ZZB": ("TZA", names("Zanzibar", "Zanzibar", "زنجبار")),
             "PSB": ("PSX", names("Palestine mandataire", "Mandatory Palestine", "فلسطين الانتدابية"))}
# Territories that belonged to another state: (head state, first year, last year)
UNION_MEMBERS = {
    **{c: ("RUS", 1946, 1991) for c in ["UKR", "BLR", "MDA", "GEO", "ARM", "AZE", "KAZ", "KGZ", "TJK", "TKM",
                                         "UZB", "EST", "LVA", "LTU"]},
    **{c: ("SRB", 1946, 1991) for c in ["HRV", "SVN", "BIH", "MKD"]},
    "MNE": ("SRB", 1946, 2005), "KOS": ("SRB", 1946, 2007), "SVK": ("CZE", 1946, 1992),
    "ERI": ("ETH", 1952, 1992), "BGD": ("PAK", 1947, 1971), "SSD": ("SDN", 1956, 2010), "TLS": ("IDN", 1976, 1999),
}
# Annexations that were not recognised: the card says "annexed by ... (annexation not recognised)" instead of "part
# of" (inherited = 2 in the rows). Baltic states: annexed by the USSR in 1940, independence restored in 1991
# (Britannica, "Baltic states"). East Timor: annexed by Indonesia in 1976, never recognised by the UN (Security Council
# resolutions 384 and 389); Indonesia leaves after the referendum of 30 August 1999 (Britannica, "East Timor").
ANNEXED = {"EST", "LVA", "LTU", "TLS"}
# Status notes shown in the card of a territory (keys atlas.status.* of the dictionaries): [(first, last, key)]
TERRITORY_NOTES = {
    **{c: [(1946, 1991, "annexedUSSR")] for c in ("EST", "LVA", "LTU")},
    "TLS": [(1976, 1999, "annexedIndonesia")],
    "UKR": [(2014, YEAR_MAX, "crimea")],
    "SAH": [(YEAR_MIN, 1975, "spanishSahara"), (1976, YEAR_MAX, "westernSahara")],
}
# Territories without V-Dem data drawn as non-sovereign ("dependent"), with the name of the time. Western Sahara: Spanish
# colony until the Madrid Accords of November 1975, then a non-self-governing territory on the UN list.
DEPENDENT_TERRITORIES = {
    "SAH": [(YEAR_MIN, 1975, names("Sahara espagnol", "Spanish Sahara", "الصحراء الإسبانية")),
            (1976, YEAR_MAX, names("Sahara occidental", "Western Sahara", "الصحراء الغربية"))],
}
# Borders according to the UN position. The default Natural Earth file shows who controls the ground: Crimea inside
# Russia, the part of Western Sahara administered by Morocco inside Morocco. These areas are taken from the Natural Earth
# file of disputed areas and given back: (polygon that loses the area, polygon that receives it, BRK_A3 of the area).
UN_TERRITORIES = [
    ("RUS", "UKR", "B89"),   # Crimea: the 2014 annexation is not recognised (UN General Assembly resolution 68/262)
    ("MAR", "SAH", "B19"),   # Western Sahara: non-self-governing territory, largely administered by Morocco
]
# Names of states whose name changed over time (otherwise: Natural Earth NAME_FR, NAME_EN, NAME_AR)
HISTORICAL_LABELS = {
    "RUS": [(1991, names("URSS", "Soviet Union", "الاتحاد السوفيتي"))],
    "SRB": [(1991, names("Yougoslavie", "Yugoslavia", "يوغوسلافيا")),
            (2002, names("Yougoslavie (RFY)", "Yugoslavia (FRY)", "يوغوسلافيا الاتحادية")),
            (2005, names("Serbie-et-Monténégro", "Serbia and Montenegro", "صربيا والجبل الأسود"))],
    "CZE": [(1992, names("Tchécoslovaquie", "Czechoslovakia", "تشيكوسلوفاكيا"))],
    "DEU": [(1948, names("Allemagne (occupée)", "Germany (occupied)", "ألمانيا (تحت الاحتلال)")),
            (1990, names("Allemagne de l'Ouest (RFA)", "West Germany (FRG)", "ألمانيا الغربية"))],
    "VNM": [(1975, names("Viêt Nam du Nord", "North Vietnam", "فيتنام الشمالية"))],
    "YEM": [(1989, names("Yémen du Nord", "North Yemen", "اليمن الشمالي"))],
}
# Wikidata items of the states whose flag the country card shows (frontend/build_media.py). By default, the item of the
# polygon (Natural Earth WIKIDATAID); for the periods of HISTORICAL_LABELS and the states of SECONDARY, the historical
# state: [(last year, item)], in order. None: no flag (Germany under Allied occupation had no national flag; Gaza,
# Zanzibar and Mandatory Palestine are not sovereign states in the years shown).
STATE_ITEMS = {
    "RUS": [(1991, "Q15180")],                                        # Soviet Union
    "SRB": [(1991, "Q83286"), (2002, "Q838261"), (2005, "Q37024")],   # SFR Yugoslavia, FR Yugoslavia, Serbia and Montenegro
    "CZE": [(1992, "Q33946")],                                        # Czechoslovakia
    "DEU": [(1948, None), (1990, "Q713750")],                         # Allied occupation, then West Germany
    "VNM": [(1975, "Q172640")],                                       # North Vietnam
    "YEM": [(1989, "Q267584")],                                       # North Yemen (Yemen Arab Republic)
    "DDR": [(YEAR_MAX, "Q16957")], "VDR": [(YEAR_MAX, "Q180573")], "YMD": [(YEAR_MAX, "Q199841")],
    "PSG": [(YEAR_MAX, None)], "ZZB": [(YEAR_MAX, None)], "PSB": [(YEAR_MAX, None)],
}


def state_item(state, year, polygon_item):
    """Wikidata item of a state in a year (see STATE_ITEMS), or None."""
    for last, item in STATE_ITEMS.get(state, []):
        if year <= last:
            return item
    return polygon_item


def flag_in(timeline, year):
    """Flag in use at the end of a year, from a timeline [(first year, last year or None, file, preferred)]: among the
    flags whose dates cover the year, the most recently adopted (a flag replaced during the year gives way to the new
    one), preferred statements first. None when no dated flag covers the year."""
    cands = [t for t in timeline if t[0] <= year and (t[1] is None or t[1] >= year)]
    return max(cands, key=lambda t: (t[0], t[3]))[2] if cands else None
# Regime categories drawn on the globe
# "dependent": colony or other non-sovereign territory (V-Dem v2svindep = 0) without an ARPD regime
CATEGORIES = ["nodata", "party", "military", "monarchy", "other_arpd", "other_vdem", "democracy", "dependent"]
ARPD_TYPE_TO_CATEGORY = {"party": "party", "military": "military", "military_monarchy": "military",
                         "monarchy": "monarchy"}
VDEM_COLUMNS = ["country_text_id", "COWcode", "year", "v2x_regime", "v2x_polyarchy", "v2svindep",
                "v2exnamhos", "v2extithos", "v2exnamhog", "v2extithog", "v2exhoshog", "v2ex_hosw"]


def write_js(name, variable, payload):
    path = OUT / name
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    path.write_text(f"window.SITE = window.SITE || {{}};\nwindow.SITE.{variable} = {text};\n", encoding="utf-8")
    print(f"  {path.relative_to(ROOT)} : {path.stat().st_size / 1024:.0f} Ko")


def year_runs(years):
    """[1946, 1947, 1950] -> [(1946, 1947), (1950, 1950)]."""
    runs = []
    for y in sorted(years):
        if runs and y == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], y)
        else:
            runs.append((y, y))
    return runs


def clean(value):
    """NaN -> None, numpy -> python."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    return value


# ---------------------------------------------------------------- geometry
def un_borders(world):
    """Move the areas of UN_TERRITORIES to the polygon of the territory they belong to (see UN_TERRITORIES)."""
    disputed = gpd.read_file(RAW / "ne_50m_admin_0_breakaway_disputed_areas.geojson").set_index("BRK_A3")
    geoms = dict(zip(world["id"], world.geometry))

    def polygons_of(g):
        return [p for part in getattr(g, "geoms", [g]) for p in getattr(part, "geoms", [part]) if p.geom_type == "Polygon"]

    for donor, receiver, code in UN_TERRITORIES:
        area = disputed.loc[code, "geometry"]
        geoms[receiver] = shapely.MultiPolygon(polygons_of(shapely.union(geoms[receiver], geoms[donor].intersection(area))))
        # The two files do not share every vertex: drop the slivers (< 0.001 square degree) left along the area
        rest = polygons_of(geoms[donor].difference(area))
        geoms[donor] = shapely.MultiPolygon([p for p in rest if p.area >= 1e-3 or not p.intersects(area.buffer(0.05))])
    return [geoms[i] for i in world["id"]]


def build_polygons():
    world = gpd.read_file(RAW / "ne_50m_admin_0_countries.geojson")
    world["id"] = world["ADM0_A3"]
    assert world["id"].is_unique
    world["geometry"] = un_borders(world)
    simplified = world.geometry.simplify(SIMPLIFY_DEGREES, preserve_topology=True)
    # Grille de 0,01° : arrondit les coordonnées en gardant des polygones valides (pas d'auto-intersection).
    # Les micro-États qui disparaissent à cette précision (Vatican…) gardent leur géométrie simplifiée.
    gridded = shapely.make_valid(shapely.set_precision(simplified.values, grid_size=0.01))
    world["geometry"] = [g if not g.is_empty else s for g, s in zip(gridded, simplified.values)]
    features, code_to_id = [], {}
    polygon_item = dict(zip(world["id"], world["WIKIDATAID"]))      # Wikidata item of each polygon (flags)
    for _, row in world.iterrows():
        geom = row.geometry
        if geom.geom_type == "GeometryCollection":      # make_valid may return lines next to polygons
            geom = shapely.MultiPolygon([g for g in geom.geoms if g.geom_type == "Polygon"] +
                                        [p for g in geom.geoms if g.geom_type == "MultiPolygon" for p in g.geoms])
        geom = mapping(geom)

        def rnd(coords):
            if coords and isinstance(coords[0], (list, tuple)):
                return [rnd(c) for c in coords]
            return [round(coords[0], 2), round(coords[1], 2)]

        geom = {"type": geom["type"], "coordinates": rnd(geom["coordinates"])}
        features.append({"type": "Feature", "id": row["id"],
                         "properties": {"id": row["id"],
                                        "name": names(row["NAME_FR"] or row["NAME"], row["NAME_EN"] or row["NAME"],
                                                      row["NAME_AR"] or row["NAME"])},
                         "geometry": geom})
        for code in (row["ADM0_A3"], row["ISO_A3"], row["ISO_A3_EH"]):
            if isinstance(code, str) and code != "-99":
                code_to_id.setdefault(code, row["id"])
    polygon_names = {f["id"]: f["properties"]["name"] for f in features}
    return features, code_to_id, polygon_names, polygon_item


# ---------------------------------------------------------------- V-Dem
def load_vdem():
    full = RAW / "V-Dem-CY-Full+Others-v16.csv"
    path = full if full.exists() else RAW / "V-Dem-CY-Core-v16.csv"
    header = pd.read_csv(path, nrows=0).columns
    cols = [c for c in VDEM_COLUMNS if c in header]
    vd = pd.read_csv(path, usecols=cols, low_memory=False)
    vd = vd[vd["year"].between(YEAR_MIN, YEAR_MAX)]
    has_names = "v2exnamhos" in vd.columns
    print(f"  V-Dem : {path.name} ({'avec' if has_names else 'sans'} noms des dirigeants)")
    return vd, has_names


# ---------------------------------------------------------------- images et extraits Wikipédia (build_media.py)
MEDIA_FILE = RAW / "wikimedia_atlas.json"
# Hosts of the Commons images: originals, and thumbnails (the Commons API gives thumbnails on thumb.wikimedia.org since
# 2026; the tracking parameters it adds to their address are removed)
IMAGE_HOSTS = ["https://upload.wikimedia.org/wikipedia/commons/", "https://thumb.wikimedia.org/wikipedia/commons/"]
COMMONS_PAGE = "https://commons.wikimedia.org/wiki/File:"


THUMB_WIDTH = 120          # width of the thumbnails requested by build_media.py


def compact_image(path):
    """Image address on its host -> (path, kind): 0 original "a/ab/Name.jpg"; 1 thumbnail "thumb/a/ab/Name.jpg/120px-
    Name.jpg" and 2 rendered SVG ".../120px-Name.svg.png", both stored as "a/ab/Name"; 3 any other address, as is."""
    if re.fullmatch(r"[0-9a-f]/[0-9a-f]{2}/[^/]+", path):
        return path, 0
    m = re.fullmatch(r"thumb/([0-9a-f]/[0-9a-f]{2}/([^/]+))/(.+)", path)
    if m and m.group(3) == f"{THUMB_WIDTH}px-{m.group(2)}":
        return m.group(1), 1
    if m and m.group(3) == f"{THUMB_WIDTH}px-{m.group(2)}.png":
        return m.group(1), 2
    return path, 3


def expand_image(path, kind):
    """Inverse of compact_image (the same rule is written in atlas.js, thumbUrl)."""
    if kind in (0, 3):
        return path
    name = path.rsplit("/", 1)[1]
    return f"thumb/{path}/{THUMB_WIDTH}px-{name}" + (".png" if kind == 2 else "")


class Media:
    """Flags, party logos, portraits and Wikipedia extracts collected by build_media.py (data/raw/wikimedia_atlas.json),
    turned into compact tables for the site: images = [path, kind (compact_image), host (IMAGE_HOSTS), licence, author],
    people = [Wikidata item, image, {language: Wikipedia title}]. Without the file, the site shows no image and no
    extract."""

    def __init__(self, polygon_item):
        self.data = json.loads(MEDIA_FILE.read_text(encoding="utf-8")) if MEDIA_FILE.exists() else None
        self.polygon_item = polygon_item
        self.images, self.image_index = [], {}
        self.people, self.person_index = [], {}

    def image(self, name):
        """Index of an image file (-1 when unknown or not a free image of Wikimedia Commons)."""
        info = self.data["files"].get(name) if self.data and name else None
        if not info:
            return -1
        if name not in self.image_index:
            thumb, page = info["thumb"].split("?")[0], info["page"]
            host = next((i for i, h in enumerate(IMAGE_HOSTS) if thumb.startswith(h)), None)
            assert host is not None and page.startswith(COMMONS_PAGE), (name, thumb)
            path, kind = compact_image(thumb[len(IMAGE_HOSTS[host]):])
            assert IMAGE_HOSTS[host] + expand_image(path, kind) == thumb, (name, thumb)
            self.image_index[name] = len(self.images)
            self.images.append([path, kind, host, info["licence"], info["author"]])
        return self.image_index[name]

    def titles(self, wiki):
        """{language: Wikipedia title} restricted to the articles whose extract was collected."""
        return {lang: t for lang, t in wiki.items() if t in self.data["extracts"].get(lang, {})}

    def flag(self, state, year, polygon):
        """Image of the flag of a state at the end of a year (-1 when no dated flag covers the year)."""
        item = state_item(state, year, self.polygon_item.get(polygon)) if self.data else None
        return self.image(flag_in(self.data["states"].get(item, {}).get("flags", []), year)) if item else -1

    def person(self, name, state):
        """Index of a V-Dem leader in the people table (-1 when not linked to a Wikidata person)."""
        p = self.data["people"].get(f"{name}|{state}") if self.data and name else None
        if not p:
            return -1
        wiki = self.titles(p["wiki"]) if p["extract"] else {}
        if p["qid"] not in self.person_index:
            self.person_index[p["qid"]] = len(self.people)
            self.people.append([p["qid"], self.image(p["image"]), wiki])
        elif wiki:
            self.people[self.person_index[p["qid"]]][2] = wiki
        return self.person_index[p["qid"]]

    def party(self, country, party):
        """Articles of a party by period: [[first year, last year, logo, logo used since, party still exists, titles]]."""
        items = self.data["parties"].get(f"{country}|{party}", []) if self.data else []
        return [[it["first"], it["last"], self.image(it["logo"]), it["logo_since"], int(it["dissolved"] is None),
                 self.titles(it["wiki"])] for it in items]

    def extracts(self, spells):
        """{language: {title: extract}} of the articles used by the spells and the people."""
        used = {lang: set() for lang in LANGS}
        for wiki in [p[2] for p in self.people] + [it[5] for s in spells for it in s.get("media", [])]:
            for lang, title in wiki.items():
                used[lang].add(title)
        return {lang: {t: self.data["extracts"][lang][t] for t in sorted(used[lang])} if self.data else {}
                for lang in LANGS}


# ---------------------------------------------------------------- périodes sans parti
# L'ARPD ne suit que les partis : toutes les années d'un pays sans parti au pouvoir forment une seule ligne
# (Party = "N"), qui peut couvrir plusieurs régimes (Libye : monarchie d'Idris 1951-1969, régime de Kadhafi
# 1969-2011, guerre civile ensuite). Le globe découpe ces périodes selon les régimes de Geddes, Wright & Frantz
# (gwf_casename du panel) ; au-delà de leur couverture, le régime est « non classé » plutôt que deviné.
GWF_TO_TYPE = {"monarchy": "monarchy", "personal": "personal", "military": "military", "military personal": "military",
               "indirect military": "military", "provisional military": "military", "warlordism": "civil_war",
               "foreign-occupied": "occupation", "provisional": "transitional", "civilian provisional": "transitional"}


# Types du panel assez précis pour être gardés quand GWF ne classe pas la période ; « militaire » ne l'est pas : il vient
# souvent du remplissage automatique des périodes sans parti (toute la Libye de 1951 à 2024, par exemple)
SPECIFIC_TYPES = {"theocracy", "failed_state", "transitional", "occupation", "civil_war", "personal", "monarchy"}


def no_party_segments(rows):
    """Lignes d'une période sans parti (triées par année) -> [(lignes, type de régime)], un segment par régime GWF.
    Type : celui de GWF s'il se traduit ; sinon le type précis du panel ; sinon « non classé »."""
    case = rows["gwf_casename"].fillna("").to_numpy()
    cuts = [0] + [i for i in range(1, len(rows)) if case[i] != case[i - 1]] + [len(rows)]
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = rows.iloc[a:b]
        if not case[a] and out:
            # Fin de la couverture de GWF (vers 2020), pas un changement de régime : le régime précédent continue
            out[-1] = (pd.concat([out[-1][0], seg]), out[-1][1])
            continue
        gwf = GWF_TO_TYPE.get(str(seg["gwf_regimetype"].iloc[0]).strip()) if case[a] else None
        detail = seg["regime_type_detail"].mode()
        detail = detail.iloc[0] if len(detail) else None
        out.append((seg, gwf or (detail if detail in SPECIFIC_TYPES else "unclassified")))
    return out


# Exceptions du globe : périodes sans parti que l'ARPD (arrêté en 2015) laisse ouvertes, alors que le régime a changé
# depuis. Clé : (pays, année d'arrivée de la période dans l'ARPD).
# - "end" : dernière année de la période (dernière année civile au pouvoir) ; les années suivantes viennent de V-Dem.
# - "split" : [(première année, type)] : nouvelle période à partir de cette année.
NO_PARTY_EXCEPTIONS = {
    # Sri Lanka : Mahinda Rajapaksa perd l'élection présidentielle du 8 janvier 2015 face à Maithripala Sirisena.
    # Source : Britannica, « Mahinda Rajapaksa » ; Wikipedia, « 2015 Sri Lankan presidential election ».
    ("Sri Lanka", 2010): {"end": 2015},
    # Afghanistan : les talibans prennent Kaboul le 15 août 2021 et rétablissent l'Émirat islamique, dirigé par un chef
    # religieux (Haibatullah Akhundzada). Source : Britannica, « Taliban » ; Wikipedia, « Fall of Kabul (2021) ».
    ("Afghanistan", 2001): {"split": [(2021, "theocracy")]},
}


def split_at(segments, first_year, rtype):
    """Segments of a period without a party, cut at first_year: the later years form one new period of type rtype."""
    before = [(seg[seg["panel_year"] < first_year], t) for seg, t in segments]
    after = pd.concat([seg[seg["panel_year"] >= first_year] for seg, _ in segments])
    return [(s, t) for s, t in before if len(s)] + ([(after, rtype)] if len(after) else [])


# ---------------------------------------------------------------- main build
def build_atlas(features, code_to_id, ne_names, media):
    vd, has_names = load_vdem()
    cow_to_vdem = (vd.dropna(subset=["COWcode"]).sort_values("year")
                   .drop_duplicates("COWcode", keep="last").set_index("COWcode")["country_text_id"].to_dict())

    def polygon_of(state):
        """(polygon id, secondary label or None) of a state code."""
        if state in SECONDARY:
            return SECONDARY[state]
        code = VDEM_ALIASES.get(state, state)
        return (code_to_id.get(code), None)

    # --- ARPD spells from the panel
    panel = pd.read_csv(PROCESSED / "arpd_panel_merged.csv", low_memory=False)
    panel["Country"] = panel["Country"].str.strip()
    panel["state"] = panel["ccode"].map(lambda c: ARPD_ONLY.get(c) or cow_to_vdem.get(ARPD_TO_COW.get(c, c)))
    missing_state = sorted(panel.loc[panel["state"].isna(), "Country"].unique())
    assert not missing_state, f"ARPD countries without code: {missing_state}"
    keys = ["Country", "Party", "Year in Power"]
    spells, arpd_year = [], {}
    for k, rows in panel.sort_values("panel_year").groupby(keys, sort=False):
        exception = NO_PARTY_EXCEPTIONS.get((k[0], int(k[2])), {}) if k[1] == "N" else {}
        if "end" in exception:
            rows = rows[rows["panel_year"] <= exception["end"]]
        r, lr = rows.iloc[0], rows.iloc[-1]
        if k[1] != "N":
            segments = [(rows, r["regime_type_detail"])]
        else:
            segments = no_party_segments(rows)
            for first_year, rtype in exception.get("split", []):
                segments = split_at(segments, first_year, rtype)
        for i, (seg, rtype) in enumerate(segments):
            is_last = i == len(segments) - 1 and "end" not in exception
            if k[1] == "N":
                # Période sans parti : l'ARPD brut ne donne ni le mode d'accès ni la fin ; les valeurs du panel
                # viennent d'un remplissage automatique et ne sont pas affichées
                gained, ended = None, None
            else:
                gained, ended = clean(r["How Power Gained"]), clean(lr["How Power Ended"])
            spells.append({
                "state": r["state"], "country": r["Country"], "party": None if k[1] == "N" else k[1],
                "start": int(seg["panel_year"].iloc[0]) if i else int(k[2]), "end": int(seg["panel_year"].iloc[-1]),
                "arpd_start": int(k[2]), "ongoing": int(is_last and lr["Censored"] == 1),
                "type": rtype, "origin": clean(r["Origin"]), "gained": gained, "ended": ended,
                "marxist": clean(r["Marxist?"]), "governance": clean(r["Governance Strategy"]),
                "founded": clean(r["Year Founded"]), "independence": clean(r["In Power from Independence?"]),
                "renamed": clean(r["Renaming?"]),
            })
            for y in seg["panel_year"]:
                if YEAR_MIN <= y <= YEAR_MAX:
                    arpd_year[(r["state"], int(y))] = len(spells) - 1

    # --- V-Dem per state-year, leader names. Each leader entry: [head of state, title, head of government, title,
    # main executive (0 = head of state, 1 = head of government: V-Dem's v2ex_hosw < 0.5, the head of government has
    # more power over the cabinet), person of the head of state, person of the head of government] (people: Media)
    leaders, leader_index = [], {}
    vdem_year = {}
    for r in vd.itertuples(index=False):
        rec = r._asdict()
        ld = -1
        if has_names and isinstance(rec.get("v2exnamhos"), str):
            same = rec.get("v2exhoshog") == 1 or not isinstance(rec.get("v2exnamhog"), str)
            hos, hog, hosw = rec["v2exnamhos"], None if same else rec.get("v2exnamhog"), rec.get("v2ex_hosw")
            state = rec["country_text_id"]
            tup = (hos, clean(rec.get("v2extithos")), hog, None if same else clean(rec.get("v2extithog")),
                   int(bool(hog) and not pd.isna(hosw) and hosw < 0.5),
                   media.person(hos, state), media.person(hog, state) if hog else -1)
            ld = leader_index.setdefault(tup, len(leaders))
            if ld == len(leaders):
                leaders.append(list(tup))
        regime = rec["v2x_regime"]
        poly = rec["v2x_polyarchy"]
        indep = rec.get("v2svindep")
        vdem_year[(rec["country_text_id"], int(rec["year"]))] = (
            -1 if pd.isna(regime) else int(regime), -1 if pd.isna(poly) else int(round(poly * 1000)), ld,
            0 if indep == 0 else 1)

    # --- labels
    labels, label_index = [], {}

    def label_id(name):
        key = tuple(name[lang] for lang in LANGS)
        if key not in label_index:
            label_index[key] = len(labels)
            labels.append(name)
        return label_index[key]

    def state_label(state, year):
        poly, secondary_label = polygon_of(state)
        if secondary_label:
            return secondary_label
        for until, text in HISTORICAL_LABELS.get(state, []):
            if year <= until:
                return text
        return ne_names.get(poly) or names(state, state, state)

    for s in spells:      # name of the state when the spell began (or in 1946 for older spells)
        s["label"] = state_label(s["state"], max(s["start"], YEAR_MIN))
        s["poly"] = polygon_of(s["state"])[0]
        if s["party"]:    # Wikipedia articles and logo of the party, by period
            s["media"] = media.party(s["country"], s["party"])

    def record(state, year):
        """[category, spell, vdem regime, polyarchy x1000, leader] of a state in a year, or None."""
        sp = arpd_year.get((state, year), -1)
        vr, px, ld, indep = vdem_year.get((state, year), (-1, -1, -1, 1))
        if sp >= 0:
            cat = ARPD_TYPE_TO_CATEGORY.get(spells[sp]["type"], "other_arpd")
        elif indep == 0:
            cat = "dependent"
        elif vr in (0, 1):
            cat = "other_vdem"
        elif vr in (2, 3):
            cat = "democracy"
        else:
            return None
        return [CATEGORIES.index(cat), sp, vr, px, ld]

    def flag(rec, state, year):
        """Flag of the state shown in a row; none for non-sovereign territories or without data."""
        if rec is None or CATEGORIES[rec[0]] in ("nodata", "dependent"):
            return -1
        return media.flag(state, year, polygon_of(state)[0])

    # States of each polygon (primary) and secondary states
    states_of_polygon = {}
    for state in set(panel["state"]) | {s for s, _ in vdem_year}:
        poly, secondary_label = polygon_of(state)
        if poly is None:
            continue
        states_of_polygon.setdefault(poly, {"primary": set(), "secondary": set()})[
            "secondary" if secondary_label else "primary"].add(state)
    unmatched = sorted({s for s in set(panel["state"]) | {s for s, _ in vdem_year} if polygon_of(s)[0] is None})

    polygons = {}
    for f in features:
        pid = f["id"]
        info = states_of_polygon.get(pid, {"primary": set(), "secondary": set()})
        own = sorted(info["primary"])
        rows = []
        for y in YEARS:
            rec, lab, inherited, shown = None, None, 0, None
            member = UNION_MEMBERS.get(pid)
            own_arpd = any((s, y) in arpd_year for s in own)
            if member and member[1] <= y <= member[2] and not own_arpd:
                rec, lab, shown = record(member[0], y), state_label(member[0], y), member[0]
                inherited = 2 if pid in ANNEXED else 1
            else:
                for s in own:
                    rec = record(s, y)
                    if rec:
                        lab, shown = state_label(s, y), s
                        break
            dependent = [name for first, last, name in DEPENDENT_TERRITORIES.get(pid, []) if first <= y <= last]
            if rec is None and dependent:
                rows.append([CATEGORIES.index("dependent"), -1, -1, -1, -1, label_id(dependent[0]), 0, -1])
            elif rec is None:
                rows.append([0, -1, -1, -1, -1, label_id(ne_names[pid]), 0, -1])
            else:
                rows.append(rec + [label_id(lab), inherited, flag(rec, shown, y)])
        secondary = []
        for s in sorted(info["secondary"]):
            years = {y: record(s, y) for y in YEARS}
            years = {y: r + [flag(r, s, y)] for y, r in years.items() if r}
            if years:
                secondary.append({"label": SECONDARY[s][1], "first": min(years), "last": max(years),
                                  "rows": [years.get(y) for y in range(min(years), max(years) + 1)]})
        # An annexation note only applies to the years drawn as annexed (not when the territory has its own regime)
        notes = []
        for first, last, key in TERRITORY_NOTES.get(pid, []):
            years = [y for y in range(first, last + 1) if pid not in ANNEXED or rows[y - YEAR_MIN][6] == 2]
            notes += [[a, b, key] for a, b in year_runs(years)]
        polygons[pid] = {"rows": rows, "secondary": secondary, "notes": notes}

    # Checks: every ARPD spell-year in range is drawn on a polygon (directly, by union, or as secondary)
    drawn = set()
    for pid, p in polygons.items():
        for i, row in enumerate(p["rows"]):
            if row[1] >= 0:
                drawn.add((row[1], YEARS[i]))
        for sec in p["secondary"]:
            for i, row in enumerate(sec["rows"]):
                if row and row[1] >= 0:
                    drawn.add((row[1], sec["first"] + i))
    expected = {(sp, y) for (_, y), sp in arpd_year.items()}
    lost = expected - drawn
    print(f"  ARPD : {len(spells)} spells, {len(expected)} spell-années dans {YEAR_MIN}-{YEAR_MAX}, "
          f"{len(lost)} non dessinées ; V-Dem sans polygone : {unmatched}")
    assert not lost, sorted(lost)[:10]

    return {
        "years": [YEAR_MIN, YEAR_MAX], "categories": CATEGORIES,
        # Polygon rows; the rows of secondary states have the first five fields and the flag
        "fields": ["category", "spell", "vdem_regime", "polyarchy_x1000", "leader", "label", "inherited", "flag"],
        "labels": labels, "leaders": leaders, "spells": spells, "polygons": polygons,
        "has_leader_names": has_names,
        "images": media.images, "image_hosts": IMAGE_HOSTS, "image_width": THUMB_WIDTH, "people": media.people,
        "media_created": media.data["created"] if media.data else None,
    }, spells


def demo_results(demo):
    """Results of 04_demographics.ipynb shown on the analysis page: model tables, scores and texts only. The
    country-year values (some come from QoG, whose terms forbid redistribution) are not copied to the site."""
    return {
        "source": demo["source"], "created": demo["created"], "protocol": demo["protocol"], "blocks": demo["blocks"],
        "totals": demo["totals"], "candidates": demo["candidates"], "coverage": demo["coverage"],
        "screening": demo["screening"], "samples": demo["samples"], "decision": demo["decision"], "kept": demo["kept"],
        "models": {"combined": demo["models"]["combined"], "descriptive": demo["models"]["descriptive"]},
        "cv": {"task_a": {"metrics": demo["cv"]["task_a"]["metrics"], "tests": demo["cv"]["task_a"]["tests"]},
               "task_b": {"metrics": demo["cv"]["task_b"]["metrics"], "tests": demo["cv"]["task_b"]["tests"]},
               "full_sample_m0": demo["cv"]["full_sample_m0"]},
        "texts": demo["texts"],
    }


def shocks_results(shocks):
    """Results of 05_shocks.ipynb shown on the analysis page: model tables, scores and texts only. The country-year
    values (some come from EM-DAT, whose licence forbids distributing adapted data) are not copied to the site."""
    return {
        "source": shocks["source"], "created": shocks["created"], "protocol": shocks["protocol"],
        "totals": shocks["totals"], "candidates": shocks["candidates"], "coverage": shocks["coverage"],
        "screening": shocks["screening"], "sample": shocks["sample"], "splice": shocks["splice"],
        "decision": shocks["decision"], "kept": shocks["kept"],
        "models": {"combined": shocks["models"]["combined"], "descriptive": shocks["models"]["descriptive"]},
        "cv": shocks["cv"], "texts": shocks["texts"],
    }


def leaders_results(leaders):
    """Results of 06_party_leaders.ipynb shown on the analysis page: model tables, scores and texts only. No value
    of a leader, a party-year or LEAD (whose licence is not stated) is copied to the site."""
    return {
        "source": leaders["source"], "created": leaders["created"], "protocol": leaders["protocol"],
        "totals": leaders["totals"], "links": leaders["links"], "candidates": leaders["candidates"],
        "coverage": leaders["coverage"], "task_b_leader_rules": leaders["task_b_leader_rules"],
        "screening": leaders["screening"], "sample": leaders["sample"], "decision": leaders["decision"],
        "kept": leaders["kept"],
        "models": {"combined": leaders["models"]["combined"], "descriptive": leaders["models"]["descriptive"]},
        "cv": leaders["cv"], "texts": leaders["texts"],
    }


def build_stats():
    eda = json.loads((PROCESSED / "site_results_eda.json").read_text(encoding="utf-8"))
    panel = json.loads((PROCESSED / "site_results_panel.json").read_text(encoding="utf-8"))
    ml = json.loads((PROCESSED / "site_results_ml.json").read_text(encoding="utf-8"))
    demo = json.loads((PROCESSED / "site_results_demo.json").read_text(encoding="utf-8"))
    shocks = json.loads((PROCESSED / "site_results_shocks.json").read_text(encoding="utf-8"))
    leaders = json.loads((PROCESSED / "site_results_leaders.json").read_text(encoding="utf-8"))
    model = json.loads((ROOT / "src" / "cox_static_model.json").read_text(encoding="utf-8"))
    return {"eda": eda, "panel": panel, "ml": ml, "demo": demo_results(demo), "shocks": shocks_results(shocks),
            "leaders": leaders_results(leaders),
            "model": {"sample": model["sample"], "performance": model["performance"],
                      "created": model["created"]}}


def build_model(atlas_spells, ne_names):
    model = json.loads((ROOT / "src" / "cox_static_model.json").read_text(encoding="utf-8"))
    static = pd.read_csv(PROCESSED / "ml_static.csv").set_index("spell_id")
    features = model["model"]["base_features"]
    by_key = {(s["country"], s["party"], s["start"]): s for s in atlas_spells}
    analogs = []
    for sid, r in static.iterrows():
        country, rest = sid.split("_", 1)          # spell_id = "<Country>_<Party>_<Year in Power>"
        party, year = rest.rsplit("_", 1)
        s = by_key[(country.strip(), party, int(year))]   # some ARPD names end with a space
        analogs.append({"label": s["label"], "poly": s["poly"], "party": party, "start": s["start"], "end": s["end"],
                        "ongoing": s["ongoing"], "duration": int(r["duration"]), "event": int(r["event"]),
                        "x": [float(r[f]) for f in features]})
    eda = json.loads((PROCESSED / "site_results_eda.json").read_text(encoding="utf-8"))
    return {"model": model, "analogs": analogs, "analog_features": features,
            "km_overall": eda["km_overall"], "sample_all": eda["sample"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Construction des données du site")
    features, code_to_id, ne_names, polygon_item = build_polygons()
    write_js("countries.js", "countries", {"type": "FeatureCollection", "features": features})
    media = Media(polygon_item)
    print(f"  Images et extraits : {MEDIA_FILE.name} du {media.data['created']}" if media.data else
          f"  Images et extraits : {MEDIA_FILE.name} absent (lancer frontend/build_media.py)")
    atlas, spells = build_atlas(features, code_to_id, ne_names, media)
    atlas["built"] = date.today().isoformat()
    write_js("atlas.js", "atlas", atlas)
    # First sentences of the Wikipedia articles, one file per language, loaded by the Atlas when a card opens
    for lang, texts in media.extracts(spells).items():
        write_js(f"wiki_{lang}.js", f"wiki_{lang}", texts)
    write_js("stats.js", "stats", {**build_stats(), "built": date.today().isoformat()})
    write_js("model.js", "game", build_model(spells, ne_names))


if __name__ == "__main__":
    main()
