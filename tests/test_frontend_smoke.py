"""Smoke test of the website in a headless browser (tests/js/smoke_pages.js).

Every page, in French, English and Arabic, at 1600 px and 390 px wide: no console error, <html lang> and dir set,
no horizontal overflow, no untranslated key left on screen; the home page and the Analyse dashboard draw their
charts. On a computer, the Atlas's globe ends above the timeline, whose chart a button hides and shows. On a phone,
the Atlas's "world situation" card is closed by default and never covers the timeline, the controls or a country
card. Without WebGL, the Atlas opens its List view with a message. The site is served from frontend/ by a local
server.

Needs Node.js, the npm package puppeteer-core and a Chromium-based browser (Edge or Chrome); skipped otherwise.
- puppeteer-core is found by Node's usual resolution, or in the folder given by ARPD_NODE_PATH (a node_modules folder);
- the browser is ARPD_BROWSER, or Edge / Chrome / Chromium at their usual places.
Set ARPD_SKIP_BROWSER=1 to skip this test.
"""
import functools
import json
import os
import shutil
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tests" / "js" / "smoke_pages.js"
BROWSER_CANDIDATES = [
    os.environ.get("ARPD_BROWSER"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]
PAGES, LANGS, WIDTHS = ["index", "atlas", "analyse", "simulation", "about"], ["fr", "en", "ar"], [1600, 390]
# Charts drawn by each page: home (survival, factors, prediction, country, shocks), dashboard (the same five + party
# and leader + data)
MIN_CHARTS = {"index": 5, "analyse": 7}


def node_env():
    env = dict(os.environ)
    if os.environ.get("ARPD_NODE_PATH"):
        env["NODE_PATH"] = os.pathsep.join(filter(None, [os.environ["ARPD_NODE_PATH"], env.get("NODE_PATH")]))
    return env


def puppeteer_available():
    if shutil.which("node") is None:
        return False
    run = subprocess.run(["node", "-e", "require.resolve('puppeteer-core')"], cwd=ROOT, env=node_env(),
                         capture_output=True, stdin=subprocess.DEVNULL)
    return run.returncode == 0


BROWSER = next((b for b in BROWSER_CANDIDATES if b and Path(b).exists()), None)
pytestmark = pytest.mark.skipif(
    bool(os.environ.get("ARPD_SKIP_BROWSER")) or BROWSER is None or not puppeteer_available(),
    reason="needs Node.js, puppeteer-core (ARPD_NODE_PATH) and a Chromium-based browser (ARPD_BROWSER)")


class Server(ThreadingHTTPServer):
    request_queue_size = 64            # the browser opens many connections at once


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def report():
    server = Server(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT / "frontend")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        run = subprocess.run(["node", str(SCRIPT), f"http://127.0.0.1:{server.server_port}", BROWSER],
                             cwd=ROOT, env=node_env(), capture_output=True, text=True, encoding="utf-8",
                             stdin=subprocess.DEVNULL, timeout=3600)
    finally:
        server.shutdown()
    assert run.returncode == 0, run.stderr[-3000:]
    return json.loads(run.stdout)


@pytest.fixture(scope="module")
def loads(report):
    """The page loads of the main browser (WebGL in software rendering)."""
    return [r for r in report if not r.get("variant")]


def test_every_page_loads_without_error(loads):
    assert {(r["page"], r["lang"], r["width"]) for r in loads} == {(p, l, w) for p in PAGES for l in LANGS for w in WIDTHS}
    failures = [(r["page"], r["lang"], r["width"], r["errors"]) for r in loads if not r["ready"] or r["errors"]]
    assert not failures, failures


def test_language_and_direction(loads):
    wrong = [(r["page"], r["lang"], r.get("htmlLang"), r.get("dir")) for r in loads
             if r.get("htmlLang") != r["lang"] or r.get("dir") != ("rtl" if r["lang"] == "ar" else "ltr") or not r.get("title")]
    assert not wrong, wrong


def test_no_horizontal_overflow(report):
    overflow = [(r["page"], r["lang"], r["width"], r.get("variant"), r.get("overflow")) for r in report
                if r.get("overflow", 99) > 1]
    assert not overflow, overflow


def test_no_untranslated_text(loads):
    leftovers = [(r["page"], r["lang"], r["width"], r.get("keys"), r.get("braces"), r.get("empty")) for r in loads
                 if r.get("keys") or r.get("braces") or r.get("empty") or "evalError" in r]
    assert not leftovers, leftovers


def test_french_typography(loads):
    """In French, ? ! ; : » and « keep a narrow no-break space (assets/js/i18n.js): none wraps alone to a new line."""
    wrong = [(r["page"], r["width"], r.get("typo")) for r in loads if r["lang"] == "fr" and r.get("typo")]
    assert not wrong, wrong


def test_home_and_dashboard_draw_their_charts(loads):
    missing = [(r["page"], r["lang"], r["width"], r.get("charts")) for r in loads
               if r["page"] in MIN_CHARTS and (r.get("charts") or 0) < MIN_CHARTS[r["page"]]]
    assert not missing, missing


def test_atlas_chart_button_and_globe_above_timeline(loads):
    runs = {r["lang"]: r.get("chartToggle") for r in loads if r["page"] == "atlas" and r["width"] == 1600}
    assert set(runs) == set(LANGS)
    for lang, g in runs.items():
        assert g and "evalError" not in g, (lang, g)
        for state in ("shown", "hidden", "again"):                          # the timeline never hides the globe
            assert g[state]["globeBottom"] <= g[state]["timelineTop"] + 1, (lang, state, g[state])
        assert g["shown"]["chart"] and g["shown"]["expanded"] == "true", (lang, g)
        assert not g["hidden"]["chart"] and g["hidden"]["expanded"] == "false", (lang, g)
        assert g["hidden"]["timelineHeight"] < g["shown"]["timelineHeight"], (lang, g)
        assert g["again"]["chart"] and g["again"]["expanded"] == "true", (lang, g)
        assert g["shown"]["label"] and g["hidden"]["label"] and g["shown"]["label"] != g["hidden"]["label"], (lang, g)


def test_atlas_world_card_on_phone(loads):
    cards = {r["lang"]: r.get("worldCard") for r in loads if r["page"] == "atlas" and r["width"] == 390}
    assert set(cards) == set(LANGS)
    for lang, card in cards.items():
        assert card and "evalError" not in card, (lang, card)
        assert card["closed"]["visible"] and card["closed"]["expanded"] == "false", (lang, card)
        assert card["closed"]["summary"], (lang, card)                       # year and number of autocracies
        assert card["open"]["visible"] and card["open"]["expanded"] == "true", (lang, card)
        for state in ("closed", "open", "withCard"):
            assert not card[state]["covers"], (lang, state, card[state])
        assert not card["withCard"]["visible"], (lang, card)                 # hidden while a country card is open


def test_atlas_without_webgl_opens_the_list(report):
    runs = [r for r in report if r.get("variant") == "no-webgl"]
    assert len(runs) == 2
    for r in runs:
        assert r["ready"] and not r["errors"], r
        assert r["webgl"] is False and r["view"] == "list" and r["listVisible"], r
        assert r["rows"] > 100 and r["message"].strip() and r["globeButtonDisabled"], r
