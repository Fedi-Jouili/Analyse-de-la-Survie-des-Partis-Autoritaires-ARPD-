"""Images and Wikipedia extracts for the country card of the Atlas: the flag of the state in each year, the logo of the
ruling party, the portraits of the leaders, and the first sentences of the Wikipedia article on the party or the ruler.

Run from the project root (needs internet; about 2 hours 30 the first time, at one request per second as Wikimedia
limits anonymous clients, plus the pauses it asks for; under a minute afterwards thanks to the cache):
    python frontend/build_media.py
then rebuild the site data with `python frontend/build_data.py`.

Sources, none of which needs a registration:
- Wikidata (https://www.wikidata.org, CC0), read through Special:EntityData: dated flags (P41, with P163 for the
  adoption date), the items and logos (P154) of the parties, the demonyms of the countries (P1549), the links between
  items and Wikipedia articles;
- Wikipedia in French, English and Arabic (CC BY-SA 4.0): the articles on the leaders (short description, categories of
  birth and death, free lead image) and the first sentences of the articles;
- Wikimedia Commons (https://commons.wikimedia.org): the image files, each under its own free licence; the author and the
  licence of every file are copied with it and shown on the site.
The requests identify the project in their User-Agent, without any personal data.

Rules:
- a flag is shown only for a year covered by its dates in Wikidata (or by the years in its file name, or by the adoption
  date of the current flag): no flag rather than a wrong flag;
- each ARPD party is linked to the English Wikipedia article checked by hand in data/raw/atlas_party_wikipedia.csv
  (by period when the party changed name and Wikipedia has one article per name);
- a V-Dem leader is linked to an English Wikipedia article only if the article is about a person (categories of birth or
  "Living people") alive in the years concerned, whose name is close to V-Dem's and who is linked to the country (its
  name or demonym in the short description or the categories); the portrait is the free lead image of the article.
  Names are first tried as titles (50 per request); the search, one request per name, is kept for the main leaders.

Writes data/raw/wikimedia_atlas.json, read by frontend/build_data.py. API answers are cached in data/raw/wikimedia_cache/
(not in the repository).
"""
import difflib
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_data import RAW, SECONDARY, STATE_ITEMS, VDEM_ALIASES, YEAR_MAX, YEAR_MIN, state_item  # noqa: E402

CACHE = RAW / "wikimedia_cache"
OUT_JSON = RAW / "wikimedia_atlas.json"
PARTY_TABLE = RAW / "atlas_party_wikipedia.csv"
USER_AGENT = "ARPD-atlas-media/1.0 (student research project on authoritarian ruling parties; Python urllib)"
WIKIDATA, COMMONS = "https://www.wikidata.org/w/api.php", "https://commons.wikimedia.org/w/api.php"
LANGS = ("fr", "en", "ar")
SITES = "|".join(f"{lang}wiki" for lang in LANGS)
THUMB_WIDTH = 120          # pixels; a standard Wikimedia thumbnail size
EXTRACT_CHARS = 320        # first sentences of a Wikipedia article, up to about this length


def wikipedia(lang):
    return f"https://{lang}.wikipedia.org/w/api.php"


# ---------------------------------------------------------------- HTTP (cached, polite)
_last_request = [0.0]


PAUSE = 1.0                # seconds between two requests: Wikimedia limits the rate of anonymous clients


ATTEMPTS = 20


def fetch_json(full):
    """GET a URL as JSON, one request at a time. When the server is busy (429, 5xx), wait as long as it asks
    (Retry-After), and at least 15 s, doubled at each new attempt up to 8 minutes."""
    for attempt in range(ATTEMPTS):
        wait = _last_request[0] + PAUSE - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.time()
        request = urllib.request.Request(full, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < ATTEMPTS - 1:
                retry = e.headers.get("Retry-After")
                pause = max(int(retry) if retry and retry.isdigit() else 0, 15 * 2 ** min(attempt, 5))
                print(f"    HTTP {e.code} (Retry-After : {retry or '-'}) : nouvel essai dans {pause} s", flush=True)
                time.sleep(pause + 2)
                continue
            raise
        except urllib.error.URLError:
            if attempt < ATTEMPTS - 1:
                time.sleep(10 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"no answer from {full}")


def cached(key, compute):
    """Disk cache of the answers (data/raw/wikimedia_cache/): a rerun sends no request already answered."""
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    path = CACHE / digest[:2] / f"{digest}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = compute()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def api(url, params):
    """GET a Wikimedia Action API (JSON, format version 2), cached."""
    params = {**params, "format": "json", "formatversion": "2"}
    full = url + "?" + urllib.parse.urlencode(sorted(params.items()))

    def get():
        for _ in range(5):
            data = fetch_json(full)
            if data.get("error", {}).get("code") != "maxlag":
                return data
            time.sleep(10)
        raise RuntimeError(f"Wikidata lag: {full}")
    return cached(full, get)


# ---------------------------------------------------------------- Wikidata
def entity(item, props):
    """One Wikidata item from Special:EntityData (served from Wikimedia's cache, lighter for the API than wbgetentities
    on big items such as countries), reduced to the properties needed, its English label and its Wikipedia links in
    the three languages of the site. Redirected items are returned under the id asked for. Cached."""
    def get():
        data = fetch_json(f"https://www.wikidata.org/wiki/Special:EntityData/{item}.json")
        e = next(iter(data.get("entities", {}).values()), {})
        return {"claims": {p: e.get("claims", {}).get(p, []) for p in props},
                "labels": {"en": e.get("labels", {}).get("en", {})},
                "sitelinks": {k: v for k, v in e.get("sitelinks", {}).items() if k in SITES.split("|")}}
    return cached(f"entity:{item}:{','.join(props)}", get)


def time_year(value):
    """Wikidata time value -> year (None for unknown values)."""
    if not isinstance(value, dict) or "time" not in value:
        return None
    m = re.match(r"([+-])(\d+)-", value["time"])
    return (int(m.group(2)) if m.group(1) == "+" else -int(m.group(2))) if m else None


def value_of(v):
    """Item id, time (as a year), monolingual text or string of a data value."""
    if isinstance(v, dict):
        return v["id"] if "id" in v else v["text"] if "text" in v else time_year(v)
    return v


def statements(entity, prop):
    """[(value, {qualifier: [values]}, rank)] of a property."""
    out = []
    for c in entity.get("claims", {}).get(prop, []):
        snak = c.get("mainsnak", {})
        if snak.get("snaktype") != "value":
            continue
        quals = {q: [value_of(s["datavalue"]["value"]) for s in snaks if s.get("snaktype") == "value"]
                 for q, snaks in c.get("qualifiers", {}).items()}
        out.append((value_of(snak["datavalue"]["value"]), quals, c.get("rank")))
    return out


def first(entity, prop):
    vals = statements(entity, prop)
    preferred = [v for v, _, rank in vals if rank == "preferred"]
    return (preferred or [v for v, _, _ in vals] or [None])[0]


def label(entity, lang="en"):
    return entity.get("labels", {}).get(lang, {}).get("value")


def sitelinks(entity):
    return {lang: entity["sitelinks"][f"{lang}wiki"]["title"] for lang in LANGS
            if f"{lang}wiki" in entity.get("sitelinks", {})}


# ---------------------------------------------------------------- flags
NOT_NATIONAL_FLAG = re.compile(r"war flag|naval|ensign|royal standard|standard of the|dark version|presidential|"
                               r"governor|jack\b", re.I)
YEARS_IN_NAME = re.compile(r"\((?:[^()]*?\D)?(\d{4})\s*[–—-]\s*(\d{4})(?:\D[^()]*)?\)|\((\d{4})\)")


def flag_timeline(state, flag_items):
    """Dated flags of a state item: [(first year, last year or None, file, preferred)]."""
    timeline, undated = [], []
    for file, quals, rank in statements(state, "P41"):
        if NOT_NATIONAL_FLAG.search(file):
            continue
        start = next((y for y in quals.get("P580", []) if isinstance(y, int)), None)
        end = next((y for y in quals.get("P582", []) if isinstance(y, int)), None)
        if start is None:
            m = YEARS_IN_NAME.search(file)
            if m and m.group(1):
                start, end = int(m.group(1)), end or int(m.group(2))
            elif m:
                start, end = int(m.group(3)), end or int(m.group(3))
        if start is None:
            undated.append((file, rank == "preferred"))
        else:
            timeline.append((start, end, file, rank == "preferred"))
    # A flag without dates gets the adoption date of its flag item (P163 of the state -> P571 or P580)
    for file, preferred in undated:
        for item in flag_items:
            if first(item, "P18") == file:
                start = first(item, "P571") or first(item, "P580")
                if isinstance(start, int):
                    end = first(item, "P582") or first(item, "P576")
                    timeline.append((start, end if isinstance(end, int) else None, file, preferred))
                break
    return sorted(timeline, key=lambda t: (t[0], t[1] or 9999))


# ---------------------------------------------------------------- text
OPEN, CLOSE = "(（", ")）"
IPA = re.compile(r"[ˈˌːəɪʊʃʒθðŋɐɛɔæʁʀχɣɾ]")
SPELLING = re.compile(r"[ˈˌːəɪʊʃʒθðŋɐɛɔæʁʀχɣ]|[;؛]|listen|écouter|prononc|pronunc|pronounced|تلفظ|استمع|\blit\.|\bIPA\b|"
                      r"\bAPI\b|"
                      r"\b(?:Arabic|Persian|French|Spanish|Russian|Chinese|Portuguese|arabe|persan|russe|chinois)\b\s*:")


LABELLED = re.compile(r"^\s*[(（]\s*[^():（）]{0,30}?\s*:")      # "(Spanish: …)", "(thaï : …)", "(بالإنجليزية: …)"
SLASHED = re.compile(r"\s*/[^/\n]{1,80}/")                     # "János Kádár /ˈjaːnoʃ ˈkaːdaːr/"


def drop_parentheses(text):
    """The text without the parentheses that hold a pronunciation, a name in another language, a long aside (over 90
    characters) or almost nothing. Nested parentheses are judged from the innermost: "(arabe : … (alharakat …))" goes
    as a whole. An opening never closed that holds a label or a pronunciation is dropped up to the end of the last
    "label: name" (the next comma) or the next parenthesis: "(en somali : …, en arabe : علي مهدي محمد, né le …" keeps
    ", né le …", "(, تلفظ بالإسبانية: /…/ (4 ديسمبر 1892…" keeps "(4 ديسمبر 1892…"."""
    keep = [True] * len(text)

    def visible(a, b):
        return "".join(c for c, k in zip(text[a:b], keep[a:b]) if k)

    def drop(a, b):                                            # with the spaces before
        while a > 0 and text[a - 1].isspace():
            a -= 1
        keep[a:b] = [False] * (b - a)
    stack, dropped_end = [], None
    for i, ch in enumerate(text):
        if ch in OPEN:
            stack.append(i)
        elif ch in CLOSE and stack:
            start = stack.pop()
            s = visible(start, i + 1)
            if SPELLING.search(s) or len(s) > 90 or LABELLED.match(s) or len(s[1:-1].strip()) <= 3:
                drop(start, i + 1)
                dropped_end = i + 1
        elif ch in CLOSE:                                      # closing never opened: "(… ؛ 16 أكتوبر) 1919 – 1969)"
            if dropped_end is not None and i - dropped_end <= 40:
                drop(dropped_end, i + 1)                       # the end of the aside just dropped
            else:
                keep[i] = False
    for start in stack:                                        # openings never closed (no parenthesis up to `end`)
        end = next((j for j in range(start + 1, len(text)) if text[j] in OPEN), None)
        if end is None or not (LABELLED.match(text[start:end]) or SPELLING.search(text[start:end])):
            continue
        colon = text.rfind(":", start, end)
        stop = next((j for j in range(max(colon, start) + 1, end) if text[j] in ",،"), end)
        while stop > start and text[stop - 1].isspace():
            stop -= 1
        drop(start, stop)
    return "".join(c for c, k in zip(text, keep) if k)


def clean_extract(text):
    """First sentences of an article intro, without pronunciations, transliterations or names in other languages,
    up to EXTRACT_CHARS."""
    text = (text or "").strip().split("\n")[0]
    previous = None
    while previous != text:                                    # square brackets (phonetics, notes), innermost first
        previous = text
        text = re.sub(r"\s*\[[^\[\]]*\]", "", text)
    text = drop_parentheses(text)
    text = SLASHED.sub(lambda m: "" if IPA.search(m.group(0)) else m.group(0), text)
    text = re.sub(r"\s+([‎‏]?[,.;:،])", r"\1", re.sub(r"\s{2,}", " ", text)).strip()
    text = re.sub(r"([,،])\s*([,،.])", r"\2", text)
    text = re.sub(r"[,،]\s*([(（])", r" \1", text)               # "Kádár, (né …)" once the pronunciation is gone
    text = re.sub(r"([(（])\s*[,;،؛]\s*", r"\1", text)            # "(, 27 April 1910 – …)": a name dropped by Wikipedia
    text = re.sub(r"\s*[,;،؛]\s*([)）])", r"\1", text)
    out = ""
    for sentence in re.split(r"(?<=[.!?؟])\s+", text):
        if out and len(out) + len(sentence) + 1 > EXTRACT_CHARS:
            break
        out = f"{out} {sentence}".strip()
    if len(out) > EXTRACT_CHARS + 80:                          # one very long sentence
        out = out[:EXTRACT_CHARS].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return out


def resolve(q):
    """Requested title -> page title, through normalisations and redirects."""
    hop = {n["from"]: n["to"] for n in q.get("normalized", []) + q.get("redirects", [])}

    def follow(t):
        for _ in range(4):
            t = hop.get(t, t)
        return t
    return follow


def extracts(lang, titles):
    """{title: cleaned extract} for Wikipedia articles (20 titles per request, the TextExtracts limit for intros)."""
    out = {}
    titles = sorted(set(titles))
    for i in range(0, len(titles), 20):
        batch = titles[i:i + 20]
        data = api(wikipedia(lang), {"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1,
                                     "exlimit": 20, "titles": "|".join(batch), "redirects": 1})
        q = data.get("query", {})
        follow = resolve(q)
        texts = {p["title"]: clean_extract(p.get("extract", "")) for p in q.get("pages", [])}
        for t in batch:
            if texts.get(follow(t)):
                out[t] = texts[follow(t)]
    return out


def page_info(titles):
    """English Wikipedia articles: {asked title: {title, qid, description, categories, image}} for existing articles
    that are not disambiguation pages. 50 titles per request; categories may continue on later requests."""
    out = {}
    titles = sorted({t for t in titles if t})
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        params = {"action": "query", "titles": "|".join(batch), "redirects": 1,
                  "prop": "pageprops|description|categories|pageimages", "ppprop": "wikibase_item|disambiguation",
                  "clshow": "!hidden", "cllimit": "max", "pilicense": "free", "piprop": "name"}
        pages, hops, cont = {}, {"normalized": [], "redirects": []}, {}
        while True:
            data = api(wikipedia("en"), {**params, **cont})
            q = data.get("query", {})
            for k in hops:
                hops[k] += q.get(k, [])
            for p in q.get("pages", []):
                page = pages.setdefault(p["title"], {"title": p["title"], "missing": bool(p.get("missing")),
                                                     "categories": [], "description": "", "image": None, "qid": None,
                                                     "disambiguation": False})
                props = p.get("pageprops", {})
                page["qid"] = props.get("wikibase_item") or page["qid"]
                page["disambiguation"] |= "disambiguation" in props
                page["description"] = p.get("description") or page["description"]
                page["image"] = p.get("pageimage") or page["image"]
                page["categories"] += [c["title"].split(":", 1)[1] for c in p.get("categories", [])]
            if "continue" not in data:
                break
            cont = data["continue"]
        follow = resolve(hops)
        for t in batch:
            page = pages.get(follow(t))
            if page and not page["missing"] and not page["disambiguation"] and page["qid"]:
                out[t] = page
    return out


def langlinks(titles):
    """{English title: {"fr": title, "ar": title}} through the interlanguage links of English Wikipedia (50 titles per
    request and language)."""
    out = {}
    for lang in ("fr", "ar"):
        for i in range(0, len(titles), 50):
            batch = titles[i:i + 50]
            cont = {}
            while True:
                data = api(wikipedia("en"), {"action": "query", "titles": "|".join(batch), "prop": "langlinks",
                                             "lllang": lang, "lllimit": "max", **cont})
                for p in data.get("query", {}).get("pages", []):
                    for link in p.get("langlinks", []):
                        out.setdefault(p["title"], {})[lang] = link["title"]
                if "continue" not in data:
                    break
                cont = data["continue"]
    return out


def search(text, n=4):
    data = api(wikipedia("en"), {"action": "query", "list": "search", "srsearch": text, "srlimit": n,
                                 "srnamespace": 0, "srprop": ""})
    return [r["title"] for r in data.get("query", {}).get("search", [])]


def plain(html_text, limit=80):
    text = re.sub(r"<[^>]+>", " ", html.unescape(html_text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def credit_author(text):
    """Author of a Commons file without the wiki boilerplate: "User:SKopp , User:Madden" -> "SKopp, Madden", "Unknown
    author Unknown author" -> "Unknown author", "No machine-readable author provided. Fornax assumed (…)" -> "Fornax";
    "See file history below for details." -> "" (the credit links to the file page, which gives that history)."""
    text = re.sub(r"(?<![/\w])(?:[a-z]{2,3}:)?(?:User|Utilisateur):", "", text)
    text = re.sub(r"No machine-readable author provided\.\s*(.+?)\s+assumed\b.*", r"\1", text)
    text = re.sub(r"\([^()]*\bsee\b[^()]*\bhistory\b[^()]*\)|\(\s*talk(?:\s*·\s*contribs)?\s*\)|"
                  r"(?<!\bto )(?<!\band )\[\s*\d+\s*\]", "", text, flags=re.I)
    text = re.sub(r"(?:Various,?\s*)?\bsee\s+(?:the\s+)?(?:(?:file|upload)\s+)?history\b[^.;)]*[.;]?"
                  r"(?:\s*For further informations?\b.*)?|\bsee (?:above|below)\b\.?", "", text, flags=re.I)
    text = re.sub(r"\b(Unknown(?: author| source| artist| photographer)?|Anonymous)(?:\s+\1)+\b", r"\1", text,
                  flags=re.I)
    text = re.sub(r"\s+([,.;:)])", r"\1", re.sub(r"\(\s+", "(", text))
    text = re.sub(r"\s{2,}", " ", text).strip(" ,;:-").lstrip(". ")
    return "" if re.match(r"own work\b", text, flags=re.I) else text     # "Own work": the uploader, unnamed


def files_info(names):
    """Commons metadata of image files: thumbnail URL, file page, licence, author."""
    out = {}
    names = sorted(set(n for n in names if n))
    for i in range(0, len(names), 50):
        if i % 1000 == 0:
            print(f"  fichiers : {i} / {len(names)}", flush=True)
        batch = names[i:i + 50]
        data = api(COMMONS, {"action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
                             "iiurlwidth": THUMB_WIDTH, "titles": "|".join("File:" + n for n in batch)})
        q = data.get("query", {})
        follow = resolve(q)
        pages = {p["title"]: p for p in q.get("pages", [])}
        for n in batch:
            page = pages.get(follow("File:" + n), {})
            info = (page.get("imageinfo") or [None])[0]
            if not info or not info.get("mime", "").startswith("image/"):
                continue                                   # missing, or a file of Wikipedia, not Commons
            meta = info.get("extmetadata", {})

            def value(k):
                return meta.get(k, {}).get("value", "")
            if str(value("NonFree")).strip().lower() in ("true", "1"):
                continue
            artist = plain(value("Artist"))                # the source (Credit) only when no author is given at all
            out[n] = {"thumb": info.get("thumburl") or info["url"], "page": info["descriptionurl"],
                      "licence": plain(value("LicenseShortName"), 40) or "Wikimedia Commons",
                      "licence_url": value("LicenseUrl"),
                      "author": credit_author(artist if artist else plain(value("Credit"))),
                      "w": info.get("thumbwidth"), "h": info.get("thumbheight")}
    return out


# ---------------------------------------------------------------- people
def fold(text):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", text)


# Main leaders of autocracies that the automatic matching cannot find (typing errors in V-Dem, distant
# transliterations, titles), linked by hand to their English Wikipedia article (checked on 2026-10-21).
# Not linked: "Georgios Andreou Papandreou", the name V-Dem gives both to Georgios Papandreou (Greece, 1964) and to his
# grandson George Papandreou (2009-2010); one link would put the wrong portrait on one of the two periods.
LEADER_TITLES = {
    "Sergey Semyonovich Biriuzov": "Sergey Biryuzov", "Aboubakar Sangoulé Lamizana": "Sangoulé Lamizana",
    "U Nu": "U Nu", "Ne Win": "Ne Win", "Jean-Bédal Bokassa I": "Jean-Bédel Bokassa",
    "Alfonso Lopoz Michelsen": "Alfonso López Michelsen", "Joseph Kasavubu": "Joseph Kasa-Vubu",
    "Galo Lincoln Plaza Lasso de la Veg": "Galo Plaza", "Faruq I": "Farouk of Egypt", "Fuad II": "Fuad II of Egypt",
    "Teshafi Teezaz Aklilu Abte-Wold": "Aklilu Habte-Wold", "Hailu Yimenu": "Hailu Yimenu",
    "Manuel Saturninoda Costa": "Manuel Saturnino da Costa",
    "Alamara Ntchina Nhassè": "Alamara Nhassé", "Nuri Pashaas-Said": "Nuri al-Said",
    "Muzahim al-Bajaji": "Muzahim al-Pachachi", "Ali Jaudat al-Aiyubi": "Ali Jawdat Al-Ayyubi",
    "Matthew Bunker Ridgway": "Matthew Ridgway", "Ali Hassan al-Majid": "Ali Hassan al-Majid",
    "Mukhammedkalyy Abylgaziev": "Mukhammedkalyi Abylgaziev", "Khalifa al-Ghwayl": "Khalifa al-Ghawil",
    "Faiz Mustafa al-Sarraj": "Fayez al-Sarraj", "Hastings Kamuzu Banda": "Hastings Banda",
    "Dato'Seri Mahathir bin Mohamad": "Mahathir Mohamad", "Miguel Alemán Váldez": "Miguel Alemán Valdés",
    "Muhammad VI": "Mohammed VI of Morocco", "Major Gen. Iskandar Mirza": "Iskander Mirza",
    "Mihai I": "Michael I of Romania", "Fahd": "Fahd of Saudi Arabia", "Sergej Kraigher": "Sergej Kraigher",
    "Veselin Djuranovic": "Veselin Đuranović", "Salem Ali Rubayyi": "Salim Rubai Ali", "Li Tsung-jen": "Li Zongren",
    "Sir Richard Gordon Turnbull": "Richard Turnbull (colonial administrator)",
}


def skeleton(word):
    """Consonants of a word, for transliterations: Muhammad / Mohammed -> mhmmd, Faruq / Farouk -> frk."""
    word = word.replace("ou", "u").replace("q", "k").replace("ph", "f")
    return re.sub(r"[aeiouy]", "", word)


def close_names(vdem_name, candidate):
    """At least one significant word of V-Dem's name is close to a word of the candidate's name (transliterations:
    Hafiz al-Asad / Hafez al-Assad, Muhammad VI / Mohammed VI, Faruq / Farouk)."""
    words = [w for w in fold(vdem_name).split() if len(w) >= 3 and w not in ("bin", "ibn", "abu", "abd", "ould")]
    other = [w for w in fold(candidate).split() if len(w) >= 3]
    return any(difflib.SequenceMatcher(None, a, b).ratio() >= 0.8 or (len(skeleton(a)) >= 3 and skeleton(a) == skeleton(b))
               for a in words for b in other)


BIRTH, DEATH = re.compile(r"^(\d{3,4}) births$"), re.compile(r"^(\d{3,4}) deaths$")
BIRTH_DECADE = re.compile(r"^(\d{3})0s births$")          # "1910s births": year of birth known to the decade


def alive_person(page, y0, y1, by_hand=False):
    """The article is about a person (categories of birth, or "Living people") alive, and at least 10, from y0 to y1.
    For a link checked by hand, a category of death is enough and there is no minimum age (Fuad II was king at one)."""
    cats = page["categories"]
    born = next((int(m.group(1)) for c in cats for m in [BIRTH.match(c)] if m), None)
    if born is None:
        born = next((int(m.group(1)) * 10 for c in cats for m in [BIRTH_DECADE.match(c)] if m), None)
    died = next((int(m.group(1)) for c in cats for m in [DEATH.match(c)] if m), None)
    if born is None and "Living people" not in cats and not any(c.startswith("Year of birth") for c in cats) \
            and not (by_hand and died is not None):
        return False
    return not ((born is not None and born > y0 - (0 if by_hand else 10)) or (died is not None and died < y1 - 1))


def is_person(page, name, y0, y1, country_words):
    """The article is about a person alive from y0 to y1, with a name close to V-Dem's, linked to the country."""
    if not alive_person(page, y0, y1) or not close_names(name, page["title"]):
        return False
    text = " " + fold(page["description"] + " " + " ".join(page["categories"])) + " "
    return any(f" {w} " in text for w in country_words)


def name_variants(name):
    """Titles to try for a V-Dem name: the full name, then shorter forms (first and last word, first words)."""
    w = name.split()
    out = [name]
    if len(w) > 2:
        out += [f"{w[0]} {w[-1]}", " ".join(w[:3]), " ".join(w[:2]), f"{w[0]} {w[-2]}"]
    return list(dict.fromkeys(out))


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    print("Images et extraits Wikipédia de l'Atlas")

    # ------------------------------------------------ states and their flags
    import geopandas as gpd
    world = gpd.read_file(RAW / "ne_50m_admin_0_countries.geojson", ignore_geometry=True)
    polygon_item = dict(zip(world["ADM0_A3"], world["WIKIDATAID"]))
    code_item = {}
    for _, row in world.iterrows():
        for code in (row["ADM0_A3"], row["ISO_A3"], row["ISO_A3_EH"]):
            if isinstance(code, str) and code != "-99":
                code_item.setdefault(code, row["WIKIDATAID"])
    state_ids = sorted(set(polygon_item.values()) | {q for periods in STATE_ITEMS.values() for _, q in periods if q})
    state_claims = {}
    for n, q in enumerate(state_ids):
        if n % 50 == 0:
            print(f"  États : {n} / {len(state_ids)}")
        state_claims[q] = entity(q, ("P41", "P163", "P1549"))
    names = state_claims                 # the reduced items carry their English label
    flag_ids = sorted({f for e in state_claims.values() for f, _, _ in statements(e, "P163")})
    flag_items = {f: entity(f, ("P18", "P571", "P580", "P582", "P576")) for f in flag_ids}
    flags = {}
    for q, e in state_claims.items():
        own = [flag_items[f] for f, _, _ in statements(e, "P163") if f in flag_items]
        flags[q] = {"label": label(e), "flags": [list(t) for t in flag_timeline(e, own)]}
    for code, periods in STATE_ITEMS.items():
        for _, q in periods:
            if q:
                print(f"  {code} -> {q} {flags.get(q, {}).get('label')}")
    print(f"  drapeaux : {sum(bool(v['flags']) for v in flags.values())} États sur {len(flags)} ont au moins un "
          "drapeau daté")

    # ------------------------------------------------ parties (reviewed table)
    table = pd.read_csv(PARTY_TABLE, dtype=str, keep_default_na=False)
    titles = sorted({t for t in table["enwiki_title"] if t})
    resolved = {}
    for i in range(0, len(titles), 50):
        data = api(wikipedia("en"), {"action": "query", "titles": "|".join(titles[i:i + 50]), "redirects": 1,
                                     "prop": "pageprops", "ppprop": "wikibase_item"})
        q = data["query"]
        follow = resolve(q)
        pages = {p["title"]: p for p in q["pages"]}
        for t in titles[i:i + 50]:
            resolved[t] = pages.get(follow(t), {}).get("pageprops", {}).get("wikibase_item")
    missing = [t for t, q in resolved.items() if not q]
    assert not missing, f"Wikipedia titles without a Wikidata item: {missing}"
    party_items = {q: entity(q, ("P154", "P576")) for q in sorted(set(resolved.values()))}
    parties = {}
    for r in table.itertuples(index=False):
        key = f"{r.country}|{r.party}"
        parties.setdefault(key, [])
        if not r.enwiki_title:
            continue
        q = resolved[r.enwiki_title]
        e = party_items[q]

        def since(s):
            return next((y for y in s[1].get("P580", []) if isinstance(y, int)), None)
        # The most recent logo (preferred statements first); its start date, if any, limits the years it is shown
        logos = sorted(statements(e, "P154"), key=lambda s: (s[2] != "preferred", -(since(s) or 0)))
        logo = logos[0] if logos else None
        dissolved = first(e, "P576")
        parties[key].append({
            "first": int(r.first_year) if r.first_year else None, "last": int(r.last_year) if r.last_year else None,
            "title": r.enwiki_title, "qid": q, "label": label(e),
            "logo": logo[0] if logo else None, "logo_since": since(logo) if logo else None,
            "dissolved": dissolved if isinstance(dissolved, int) else None, "wiki": sitelinks(e)})
    print(f"  partis : {len(parties)} ; avec un article : {sum(bool(v) for v in parties.values())} ; "
          f"avec un logo : {sum(any(i['logo'] for i in v) for v in parties.values())}")

    # ------------------------------------------------ leaders (V-Dem) -> English Wikipedia articles
    vdem = RAW / "V-Dem-CY-Full+Others-v16.csv"
    vd = pd.read_csv(vdem, usecols=["country_text_id", "country_name", "year", "v2exnamhos", "v2exnamhog", "v2ex_hosw",
                                    "v2x_regime", "v2svindep"], low_memory=False)
    vd = vd[vd["year"].between(YEAR_MIN, YEAR_MAX)]
    people = {}                     # (name, state) -> years, country name, main leader at least once, extract needed
    for r in vd.itertuples(index=False):
        hos = r.v2exnamhos if isinstance(r.v2exnamhos, str) else None
        hog = r.v2exnamhog if isinstance(r.v2exnamhog, str) else None
        main = hog if hog and hog != hos and not pd.isna(r.v2ex_hosw) and r.v2ex_hosw < 0.5 else hos
        autocracy = r.v2x_regime in (0, 1) and r.v2svindep != 0
        for name in (hos, hog):
            if name:
                p = people.setdefault((name, r.country_text_id), {"years": set(), "extract": False, "main": False,
                                                                  "country": r.country_name})
                p["years"].add(int(r.year))
                p["main"] |= name == main
                p["extract"] |= bool(autocracy and name == main)

    def items_of(state, years):
        poly = code_item.get(VDEM_ALIASES.get(state, state)) or polygon_item.get(SECONDARY.get(state, (None,))[0])
        return {q for y in years for q in [state_item(state, y, poly), poly] if q}

    def demonyms(q):
        """English demonyms of a country item (P1549 is a monolingual text, in many languages)."""
        return [c["mainsnak"]["datavalue"]["value"]["text"] for c in state_claims.get(q, {}).get("claims", {}).get("P1549", [])
                if c["mainsnak"].get("snaktype") == "value" and c["mainsnak"]["datavalue"]["value"].get("language") == "en"]

    def country_words(state, p):
        words = {p["country"]} | {w for q in items_of(state, p["years"]) for w in [label(names.get(q, {}))] + demonyms(q)
                                  if w}
        parts = {fold(part).strip() for w in words for part in re.split(r"[/()]", w) if fold(part).strip()}
        return {w for w in parts if len(w) >= 4}

    found = {}

    def try_titles(candidates):
        """candidates: {(name, state): [titles]} -> fill `found` with the first title that passes is_person."""
        info = page_info([t for ts in candidates.values() for t in ts])
        for (name, state), ts in candidates.items():
            if (name, state) in found:                # linked by hand
                continue
            p = people[(name, state)]
            words = country_words(state, p)
            for t in ts:
                page = info.get(t)
                if page and is_person(page, name, min(p["years"]), max(p["years"]), words):
                    found[(name, state)] = page
                    break

    # Links checked by hand first: the article must exist and be about a person alive in the years concerned
    manual = {k: LEADER_TITLES[k[0]] for k in people if k[0] in LEADER_TITLES}
    manual_pages = page_info(manual.values())
    for (name, state), title in manual.items():
        page, p = manual_pages.get(title), people[(name, state)]
        if page and alive_person(page, min(p["years"]), max(p["years"]), by_hand=True):
            found[(name, state)] = page
        else:
            print(f"  ATTENTION : lien manuel non vérifié : {name} -> {title}")
    try_titles({k: name_variants(k[0]) for k in people})       # same requests as before: answers taken from the cache
    print(f"  dirigeants : {len(found)} sur {len(people)} trouvés par leur nom")
    # Search (one request per name, the slow part) only for the main leaders, whose portrait leads the card
    for attempt, query in ((1, lambda name, p: f"{name} {p['country']}"), (2, lambda name, p: name)):
        todo = [k for k in sorted(people) if k not in found and people[k]["main"]]
        candidates = {}
        for n, (name, state) in enumerate(todo):
            if n % 100 == 0:
                print(f"  recherche (passe {attempt}) : {n} / {len(todo)}")
            candidates[(name, state)] = search(query(name, people[(name, state)]))
        try_titles(candidates)
        print(f"  dirigeants : {len(found)} sur {len(people)} après la recherche {attempt}")
    links = langlinks(sorted({page["title"] for page in found.values()}))
    matched, unmatched = {}, []
    for (name, state), p in sorted(people.items()):
        page = found.get((name, state))
        if page:
            matched[f"{name}|{state}"] = {"qid": page["qid"], "title": page["title"], "image": page["image"],
                                          "description": page["description"],
                                          "wiki": {"en": page["title"], **links.get(page["title"], {})},
                                          "extract": p["extract"]}
        else:
            unmatched.append(f"{name}|{state}")
    print(f"  dirigeants : {len(matched)} reliés sur {len(people)} ; avec portrait : "
          f"{sum(bool(v['image']) for v in matched.values())}")

    # ------------------------------------------------ Wikipedia extracts (parties, and rulers of autocracies)
    wanted = {lang: set() for lang in LANGS}
    for items in parties.values():
        for it in items:
            for lang, title in it["wiki"].items():
                wanted[lang].add(title)
    for v in matched.values():
        if v["extract"]:
            for lang, title in v["wiki"].items():
                wanted[lang].add(title)
    texts = {lang: extracts(lang, titles) for lang, titles in wanted.items()}
    print("  extraits : " + ", ".join(f"{lang} {len(t)}" for lang, t in texts.items()))

    # ------------------------------------------------ image files (Commons)
    used = {f for v in flags.values() for _, _, f, _ in v["flags"]} | \
           {it["logo"] for items in parties.values() for it in items if it["logo"]} | \
           {v["image"] for v in matched.values() if v["image"]}
    files = files_info(used)
    print(f"  fichiers : {len(files)} sur {len(used)} (les autres ne sont pas des images libres de Commons)")

    OUT_JSON.write_text(json.dumps({
        "created": date.today().isoformat(),
        "user_agent": USER_AGENT,
        "sources": {"wikidata": "https://www.wikidata.org (CC0)",
                    "commons": "https://commons.wikimedia.org (licence of each file)",
                    "wikipedia": "https://{fr,en,ar}.wikipedia.org (CC BY-SA 4.0)"},
        "states": flags, "parties": parties, "people": matched, "unmatched_people": sorted(unmatched),
        "extracts": texts, "files": files,
    }, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    print(f"  {OUT_JSON.relative_to(RAW.parents[1])} : {OUT_JSON.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
