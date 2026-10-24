"""French typography of the website: a narrow no-break space before ? ! ; : » and after «, so that these signs never
wrap alone to the next line. The dictionaries and the generated texts keep ordinary spaces; assets/js/i18n.js
(I18n.t, tHtml, tList, get) and assets/js/core.js (generated texts of frontend/data/stats.js) put the right space
when the page is in French. Runs tests/js/run_typography.js with Node; skipped without Node."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")


def test_french_texts_use_no_break_spaces():
    run = subprocess.run(["node", str(ROOT / "tests" / "js" / "run_typography.js")], cwd=ROOT, capture_output=True,
                         text=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=120)
    assert run.returncode == 0, run.stderr[-2000:]
    report = json.loads(run.stdout)
    assert report["generatedBlocks"] >= 6                  # eda, panel, ml, demo, shocks, leaders
    assert not report["found"], report["found"][:10]


def test_other_languages_are_not_changed():
    """Only French gets the narrow spaces: the English and Arabic texts are shown as written."""
    script = (
        "const vm=require('vm'),fs=require('fs');"
        "const ctx={location:{search:'?lang=en',hash:'',href:'http://localhost/'},navigator:{languages:['en']},"
        "localStorage:{getItem:()=>null,setItem(){}},document:{documentElement:{},addEventListener(){}},"
        "console,URLSearchParams,Intl,history:{}};ctx.window=ctx;vm.createContext(ctx);"
        "for(const f of ['frontend/assets/i18n/fr.js','frontend/assets/i18n/en.js','frontend/assets/js/i18n.js'])"
        "vm.runInContext(fs.readFileSync(f,'utf8'),ctx);"
        "console.log(JSON.stringify(ctx.I18n.t('dash.leaders.title')))"
    )
    run = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                         stdin=subprocess.DEVNULL, timeout=60)
    assert run.returncode == 0, run.stderr[-2000:]
    assert json.loads(run.stdout) == "Do the party and its leader matter?"
