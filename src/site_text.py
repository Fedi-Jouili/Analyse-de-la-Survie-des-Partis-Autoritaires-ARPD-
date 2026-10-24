"""Texts of the website's Analyse page in French, English and Arabic.

The notebooks display their own French texts. The website needs the same statements in three
languages, so the functions below rebuild them from the payload each notebook exports
(data/processed/site_results_*.json): every language states exactly the same numbers.

    eda_texts(site_eda)       02_eda_and_data_processing.ipynb, Section 7
    panel_texts(site_panel)   final_panel.ipynb, Section 13 (uses site_panel["facts"])
    ml_texts(site_ml)         03_ml_survival.ipynb, Section 8
    demo_texts(site_demo)     04_demographics.ipynb, Section 10
    shocks_texts(site_shocks) 05_shocks.ipynb, Section 10
    leaders_texts(site_leaders) 06_party_leaders.ipynb, Section 10

Each function returns {"fr": {...}, "en": {...}, "ar": {...}} with Markdown strings. Dataset codes are
replaced by the labels of docs/glossary.md. Arabic uses Latin digits, like the rest of the site;
formulas and signed numbers are wrapped in Unicode isolates (LRI ... PDI) so that they read left to
right inside right-to-left text.
"""
import numpy as np

from site_export import jsonable

LANGS = ("fr", "en", "ar")
ALPHA = 0.05
R2_LINEAR = 0.9                      # 03_ml_survival.ipynb, Section 6.2
LRI, PDI = "⁦", "⁩"
NNBSP = " "                     # French thousands separator and space before "%"
MINUS = "−"


# ---------------------------------------------------------------- numbers
NBSP = " "


def iso(lang, text):
    """Left-to-right island inside Arabic text (no change in French and English). Its spaces do not break,
    so that a formula never wraps across two lines."""
    return f"{LRI}{text.replace(' ', NBSP)}{PDI}" if lang == "ar" else text


def raw(lang, value, digits=0):
    """Number without isolate: French 4 233,5 ; English and Arabic 4,233.5 ; minus sign U+2212."""
    rounded = round(float(value), digits)
    text = f"{abs(rounded):,.{digits}f}"
    if lang == "fr":
        text = text.replace(",", NNBSP).replace(".", ",")
    return (MINUS if rounded < 0 else "") + text


def num(lang, value, digits=0):
    return iso(lang, raw(lang, value, digits))


def signed(lang, value, digits):
    text = raw(lang, value, digits)
    return iso(lang, text if text.startswith(MINUS) else "+" + text)


def gnum(lang, value):
    """Shortest form of a number (Python's :g), with the decimal separator of the language."""
    text = f"{value:g}".replace("-", MINUS)
    return iso(lang, text.replace(".", ",") if lang == "fr" else text)


def pct(lang, value, digits=0):
    text = raw(lang, value, digits)
    return f"{text}{NNBSP}%" if lang == "fr" else iso(lang, f"{text}%")


def p_raw(lang, p, digits=3):
    return f"p{NBSP}<{NBSP}{raw(lang, 0.001, 3)}" if p < 0.001 else f"p{NBSP}={NBSP}{raw(lang, p, digits)}"


def p_txt(lang, p, digits=3):
    return iso(lang, p_raw(lang, p, digits))


def p_corrected(lang, p):
    """'p corrigée = 0,018' / 'corrected p = 0.018' / 'p = 0.018 بعد التصحيح'."""
    value = f"< {raw(lang, 0.001, 3)}" if p < 0.001 else f"= {raw(lang, p, 3)}"
    return {"fr": f"p corrigée {value}", "en": f"corrected p {value}", "ar": f"{iso(lang, 'p ' + value)} بعد التصحيح"}[lang]


def hr_txt(lang, hr, p=None):
    text = f"HR{NBSP}={NBSP}{raw(lang, hr, 2)}"
    if p is not None:
        text += f" ({p_raw(lang, p)})"
    return iso(lang, text)


# ---------------------------------------------------------------- words
ARROW = {"fr": "→", "en": "→", "ar": "←"}
SEMI = {"fr": " ; ", "en": "; ", "ar": "؛ "}
COMMA = {"fr": ", ", "en": ", ", "ar": "، "}

# Nouns counted in the texts. Arabic: CLDR plural categories, which match the grammar of
# counted nouns (3-10: plural; 11-99: singular accusative; 100, 200...: singular genitive).
NOUNS = {
    "party": {"fr": ("parti", "partis"), "en": ("party", "parties"),
              "ar": {"zero": "{n} حزب", "one": "حزب واحد", "two": "حزبين", "few": "{n} أحزاب",
                     "many": "{n} حزبًا", "other": "{n} حزب"}},
    "fall": {"fr": ("chute", "chutes"), "en": ("fall", "falls"),
             "ar": {"zero": "{n} حالة سقوط", "one": "حالة سقوط واحدة", "two": "حالتي سقوط",
                    "few": "{n} حالات سقوط", "many": "{n} حالة سقوط", "other": "{n} حالة سقوط"}},
    "country": {"fr": ("pays", "pays"), "en": ("country", "countries"),
                "ar": {"zero": "{n} بلد", "one": "بلد واحد", "two": "بلدين", "few": "{n} بلدان",
                       "many": "{n} بلدًا", "other": "{n} بلد"}},
    "year": {"fr": ("an", "ans"), "en": ("year", "years"),
             "ar": {"zero": "{n} سنة", "one": "سنة واحدة", "two": "سنتين", "few": "{n} سنوات",
                    "many": "{n} سنة", "other": "{n} سنة"}},
    "regime": {"fr": ("régime", "régimes"), "en": ("regime", "regimes"),
               "ar": {"zero": "{n} نظام", "one": "نظام واحد", "two": "نظامين", "few": "{n} أنظمة",
                      "many": "{n} نظامًا", "other": "{n} نظام"}},
    "model": {"fr": ("modèle", "modèles"), "en": ("model", "models"),
              "ar": {"zero": "{n} نموذج", "one": "نموذج واحد", "two": "نموذجين", "few": "{n} نماذج",
                     "many": "{n} نموذجًا", "other": "{n} نموذج"}},
    "obs": {"fr": ("parti-année", "parti-années"), "en": ("party-year", "party-years"),
            "ar": {"zero": "{n} مشاهدة", "one": "مشاهدة واحدة", "two": "مشاهدتين", "few": "{n} مشاهدات",
                   "many": "{n} مشاهدة", "other": "{n} مشاهدة"}},
    "effect": {"fr": ("effet", "effets"), "en": ("effect", "effects"),
               "ar": {"zero": "{n} أثر", "one": "أثر واحد", "two": "أثرين", "few": "{n} آثار",
                      "many": "{n} أثرًا", "other": "{n} أثر"}},
    "way": {"fr": ("façon", "façons"), "en": ("way", "ways"),
            "ar": {"zero": "{n} طريقة", "one": "طريقة واحدة", "two": "طريقتين", "few": "{n} طرق",
                   "many": "{n} طريقة", "other": "{n} طريقة"}},
    "variable": {"fr": ("variable", "variables"), "en": ("variable", "variables"),
                 "ar": {"zero": "{n} متغير", "one": "متغير واحد", "two": "متغيرين", "few": "{n} متغيرات",
                        "many": "{n} متغيرًا", "other": "{n} متغير"}},
}


def ar_category(n):
    n = abs(int(n))
    if n in (0, 1, 2):
        return ("zero", "one", "two")[n]
    if 3 <= n % 100 <= 10:
        return "few"
    if 11 <= n % 100 <= 99:
        return "many"
    return "other"


def count(lang, n, noun):
    """'12 partis', '1 party', '12 حزبًا' (number and noun agree)."""
    forms = NOUNS[noun][lang]
    if lang == "ar":
        return forms[ar_category(n)].format(n=num("ar", n))
    singular = n <= 1 if lang == "fr" else n == 1
    return f"{num(lang, n)} {forms[0] if singular else forms[1]}"


def join(lang, items):
    """'a, b et c' / 'a, b and c' / 'a، وb، وc'."""
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    if lang == "ar":
        return items[0] + "".join(f"، و{'' if it[0].isalpha() and '؀' <= it[0] <= 'ۿ' else ' '}{it}"
                                  for it in items[1:])
    word = " et " if lang == "fr" else " and "
    return ", ".join(items[:-1]) + word + items[-1]


def cap(text):
    return text[0].upper() + text[1:] if text else text


# ---------------------------------------------------------------- labels (docs/glossary.md)
MODEL_NAMES = {"static": {"fr": "statique", "en": "static", "ar": "الثابت"},
               "corrected": {"fr": "corrigé", "en": "corrected", "ar": "المصحَّح"},
               "timevarying": {"fr": "time-varying", "en": "time-varying", "ar": "المتغير زمنيًا"}}

# Heading of a factor (bullet) and its name inside a sentence
FACTORS = {
    "Origin_Communist": {"fr": ("Origine communiste", "origine communiste"),
                         "en": ("Communist origin", "communist origin"),
                         "ar": ("الأصل الشيوعي", "الأصل الشيوعي")},
    "Origin_Elite Coalition": {"fr": ("Coalition d'élites", "origine « coalition d'élites »"),
                               "en": ("Elite coalition", "elite-coalition origin"),
                               "ar": ("ائتلاف النخب", "أصل ائتلاف النخب")},
    "Origin_Independence": {"fr": ("Lutte pour l'indépendance", "origine « lutte pour l'indépendance »"),
                            "en": ("Independence movement", "independence-movement origin"),
                            "ar": ("حركة الاستقلال", "أصل حركة الاستقلال")},
    "Origin_Merger/Split": {"fr": ("Fusion ou scission", "origine « fusion ou scission »"),
                            "en": ("Merger or split", "merger-or-split origin"),
                            "ar": ("الاندماج أو الانشقاق", "أصل الاندماج أو الانشقاق")},
    "Origin_Military": {"fr": ("Origine militaire", "origine militaire"),
                        "en": ("Military origin", "military origin"),
                        "ar": ("الأصل العسكري", "الأصل العسكري")},
    "Origin_Revolution": {"fr": ("Révolution", "origine révolutionnaire"),
                          "en": ("Revolution", "revolutionary origin"),
                          "ar": ("الثورة", "الأصل الثوري")},
    "Marxist?": {"fr": ("Idéologie marxiste-léniniste", "idéologie marxiste-léniniste"),
                 "en": ("Marxist-Leninist ideology", "Marxist-Leninist ideology"),
                 "ar": ("الأيديولوجيا الماركسية اللينينية", "الأيديولوجيا الماركسية اللينينية")},
    "Gov_Repressive": {"fr": ("Stratégie répressive", "stratégie répressive"),
                       "en": ("Repressive strategy", "repressive strategy"),
                       "ar": ("الاستراتيجية القمعية", "الاستراتيجية القمعية")},
    "Gov_Clientelist": {"fr": ("Stratégie clientéliste", "stratégie clientéliste"),
                        "en": ("Clientelist strategy", "clientelist strategy"),
                        "ar": ("استراتيجية الزبائنية", "استراتيجية الزبائنية")},
    "polity2": {"fr": (f"Score Polity2 (de {MINUS}10 à +10)", "score Polity2"),
                "en": (f"Polity2 score ({MINUS}10 to +10)", "Polity2 score"),
                "ar": (f"مؤشر Polity2 (من {iso('ar', MINUS + '10')} إلى {iso('ar', '+10')})", "مؤشر Polity2")},
    "conflict_entry": {"fr": ("Conflit armé à l'entrée", "conflit armé à l'entrée au pouvoir"),
                       "en": ("Armed conflict at entry", "armed conflict at entry into power"),
                       "ar": ("النزاع المسلح عند الوصول إلى السلطة", "النزاع المسلح عند الوصول إلى السلطة")},
    "conflict": {"fr": ("Conflit armé (UCDP)", "conflit armé"), "en": ("Armed conflict (UCDP)", "armed conflict"),
                 "ar": ("النزاع المسلح (UCDP)", "النزاع المسلح")},
    "gdp": {"fr": ("PIB par habitant", "PIB par habitant"), "en": ("GDP per capita", "GDP per capita"),
            "ar": ("نصيب الفرد من الناتج المحلي الإجمالي", "نصيب الفرد من الناتج المحلي الإجمالي")},
}
# Short names of origins in a list ("communiste, indépendance et révolution")
ORIGIN_SHORT = {
    "Origin_Communist": {"fr": "communiste", "en": "communist", "ar": "الأصل الشيوعي"},
    "Origin_Elite Coalition": {"fr": "coalition d'élites", "en": "elite coalition", "ar": "ائتلاف النخب"},
    "Origin_Independence": {"fr": "lutte pour l'indépendance", "en": "independence movement", "ar": "حركة الاستقلال"},
    "Origin_Merger/Split": {"fr": "fusion ou scission", "en": "merger or split", "ar": "الاندماج أو الانشقاق"},
    "Origin_Military": {"fr": "militaire", "en": "military", "ar": "الأصل العسكري"},
    "Origin_Revolution": {"fr": "révolution", "en": "revolution", "ar": "الثورة"},
}
MODEL_ML = {"KM": {"fr": "Kaplan-Meier", "en": "Kaplan-Meier", "ar": "كابلان-ماير"},
            "Cox": {"fr": "Cox", "en": "Cox", "ar": "كوكس"},
            "RSF": {"fr": "forêt aléatoire de survie", "en": "random survival forest", "ar": "غابة البقاء العشوائية"},
            "GBSA": {"fr": "gradient boosting de survie", "en": "gradient-boosted survival model",
                     "ar": "نموذج التعزيز المتدرج للبقاء"},
            "Temps seul": {"fr": "durée seule", "en": "duration only", "ar": "المدة وحدها"},
            "Cox time-varying": {"fr": "Cox time-varying", "en": "time-varying Cox", "ar": "كوكس المتغير زمنيًا"},
            "Logistique": {"fr": "régression logistique", "en": "logistic regression", "ar": "الانحدار اللوجستي"},
            "LightGBM": {"fr": "LightGBM", "en": "LightGBM", "ar": "LightGBM"}}
IN_TASK = {"fr": "en tâche {t}", "en": "in task {t}", "ar": "في المهمة {t}"}


def records(split):
    """pandas 'split' table -> list of dicts (the index under '_index')."""
    return [dict(zip(["_index"] + split["columns"], [i] + list(row))) for i, row in zip(split["index"], split["data"])]


def same_text_in_all_languages(texts):
    """Check that the three languages have the same keys and list lengths (used by the tests too)."""
    ref = texts["fr"]
    for lang in LANGS:
        assert set(texts[lang]) == set(ref), lang
        for k, v in ref.items():
            if isinstance(v, list):
                assert len(texts[lang][k]) == len(v), (lang, k)
    return texts


# ================================================================= 02_eda_and_data_processing
def eda_texts(site_eda):
    E = jsonable(site_eda)
    s, km, chk = E["sample"], E["km_overall"], E["checks"]
    cov = {r["_index"]: r for r in records(E["coverage"]["table"])}
    polity_last = cov["Polity5 (polity2)"]["dernière année"]
    ucdp_first = cov["UCDP (conflit)"]["première année"]
    gdp_cov = cov["Maddison (PIB par habitant)"]["couverture totale (%)"]
    p_origin = E["km_by"]["origin"]["logrank_p"]
    out = {}
    for lang in LANGS:
        n, c = s["spells"], s["censored"]
        a = ARROW[lang]
        if lang == "fr":
            synthesis = [
                f"**Censure** : {count(lang, c, 'party')} sur {num(lang, n)} sont encore au pouvoir à la fin de "
                f"l'observation (observations censurées) ; la médiane de survie (Kaplan-Meier) est de "
                f"{count(lang, round(km['median']), 'year')} ({count(lang, round(km['raw_median']), 'year')} en médiane "
                f"brute, qui ignore la censure) {a} modèles de survie (Cox), qui traitent la censure, plutôt qu'une "
                "régression sur les durées observées.",
                f"**Origine** : les courbes de survie diffèrent selon l'origine (test du log-rank, {p_txt(lang, p_origin)}) "
                f"{a} l'origine est la covariable centrale des modèles, avec les partis créés par un dictateur (le groupe "
                "le plus nombreux) comme référence et les modalités rares regroupées.",
                f"**Stratégie de gouvernance** : codée pour {pct(lang, chk['governance_coded_pct'])} des partis, de façon "
                f"non aléatoire {a} pas d'imputation à partir de l'origine ; modalité explicite « non codée », "
                "interprétée comme une différence entre partis codés et non codés, pas comme une stratégie.",
                f"**Idéologie** : {pct(lang, chk['pct_marxist_communist'])} des partis d'origine communiste sont "
                f"marxistes-léninistes {a} l'effet de l'idéologie se lit avec prudence, une fois l'origine contrôlée.",
                f"**Niveau démocratique** : Polity2 et V-Dem sont corrélés à {num(lang, chk['corr_polity_vdem'], 2)}, "
                f"mais Polity2 s'arrête en {polity_last} {a} Polity2 dans les modèles principaux, V-Dem en test de "
                "robustesse (`final_panel.ipynb`, section 5.4).",
                f"**Variables macro** : couverture incomplète (conflit absent avant {ucdp_first}, PIB Maddison disponible "
                f"pour {pct(lang, gdp_cov)} des parti-années) {a} valeurs de la première année dans le modèle statique "
                "(sans remplacement par une année ultérieure), valeurs de l'année précédente et entrée tardive dans "
                "le modèle time-varying.",
                f"**Variables propres aux juntes** (`Military`, `Violence`, `Occupation`) {a} non utilisées pour les "
                f"partis nommés ; `Monarchy`, codée année par année (monarchie qui gouverne réellement), ne concerne que "
                f"{count(lang, chk['monarchy_spells'], 'party')} à leur arrivée au pouvoir {a} retirée des modèles, "
                "gardée comme variable descriptive.",
            ]
        elif lang == "en":
            synthesis = [
                f"**Censoring**: {num(lang, c)} of {count(lang, n, 'party')} are still in power at the end of the "
                f"observation period (censored observations); the Kaplan-Meier median survival is "
                f"{count(lang, round(km['median']), 'year')} ({count(lang, round(km['raw_median']), 'year')} for the "
                f"raw median, which ignores censoring) {a} survival models (Cox), which handle censoring, rather than "
                "a regression on observed durations.",
                f"**Origin**: survival curves differ by origin (log-rank test, {p_txt(lang, p_origin)}) {a} origin is "
                "the central covariate of the models, with dictator-created parties (the largest group) as the "
                "reference and rare categories merged.",
                f"**Governance strategy**: coded for {pct(lang, chk['governance_coded_pct'])} of parties, and not at "
                f"random {a} no imputation from origin; an explicit “not coded” category, read as a difference between "
                "coded and uncoded parties, not as a strategy.",
                f"**Ideology**: {pct(lang, chk['pct_marxist_communist'])} of communist-origin parties are "
                f"Marxist-Leninist {a} the effect of ideology must be read with caution once origin is controlled for.",
                f"**Democracy level**: Polity2 and V-Dem are correlated at {num(lang, chk['corr_polity_vdem'], 2)}, but "
                f"Polity2 stops in {polity_last} {a} Polity2 in the main models, V-Dem as a robustness check "
                "(`final_panel.ipynb`, Section 5.4).",
                f"**Macro variables**: incomplete coverage (no conflict data before {ucdp_first}, Maddison GDP "
                f"available for {pct(lang, gdp_cov)} of party-years) {a} first-year values in the static model (never "
                "replaced by a later year), previous-year values and late entry in the time-varying model.",
                f"**Junta-only variables** (`Military`, `Violence`, `Occupation`) {a} not used for named parties; "
                f"`Monarchy`, coded year by year (a monarchy that actually governs), applies to only "
                f"{count(lang, chk['monarchy_spells'], 'party')} when they came to power {a} removed from the models, "
                "kept as a descriptive variable.",
            ]
        else:
            synthesis = [
                f"**الرقابة**: لا يزال {num(lang, c)} من أصل {count(lang, n, 'party')} في السلطة عند نهاية فترة الرصد "
                f"(مشاهدات مراقَبة)؛ ويبلغ وسيط مدة البقاء وفق كابلان-ماير {count(lang, round(km['median']), 'year')} "
                f"({count(lang, round(km['raw_median']), 'year')} للوسيط الخام الذي يتجاهل الرقابة) {a} نماذج البقاء "
                "(كوكس) التي تعالج الرقابة، بدلًا من انحدار على المدد المرصودة.",
                f"**الأصل**: تختلف منحنيات البقاء باختلاف أصل الحزب (اختبار لوغ-رانك، {p_txt(lang, p_origin)}) {a} "
                "الأصل هو المتغير التفسيري المحوري في النماذج، مع اعتماد الأحزاب التي أسسها حاكم مستبد (الفئة الأكبر "
                "عددًا) فئةً مرجعية ودمج الفئات النادرة.",
                f"**استراتيجية الحكم**: مرمَّزة لـ{pct(lang, chk['governance_coded_pct'])} فقط من الأحزاب، وبصورة غير "
                f"عشوائية {a} لا تُستكمل القيم الناقصة انطلاقًا من الأصل، بل تُخصَّص فئة صريحة «غير مرمَّزة» تُفهم على "
                "أنها فرق بين الأحزاب المرمَّزة وغير المرمَّزة، لا على أنها استراتيجية.",
                f"**الأيديولوجيا**: {pct(lang, chk['pct_marxist_communist'])} من الأحزاب ذات الأصل الشيوعي ماركسية "
                f"لينينية {a} ينبغي قراءة أثر الأيديولوجيا بحذر بعد ضبط أثر الأصل.",
                f"**مستوى الديمقراطية**: يبلغ معامل الارتباط بين Polity2 و V-Dem "
                f"{num(lang, chk['corr_polity_vdem'], 2)}، لكن بيانات Polity2 تتوقف عام {polity_last} {a} يُستخدم "
                "Polity2 في النماذج الرئيسية و V-Dem في اختبار المتانة (`final_panel.ipynb`، القسم 5.4).",
                f"**المتغيرات الكلية**: تغطية ناقصة (لا بيانات عن النزاعات قبل عام {ucdp_first}، وبيانات Maddison عن "
                f"الناتج المحلي متوفرة لـ{pct(lang, gdp_cov)} من مشاهدات حزب-سنة) {a} قيم السنة الأولى في النموذج "
                "الثابت (دون الاستعاضة عنها بسنة لاحقة)، وقيم السنة السابقة مع الدخول المتأخر في النموذج المتغير زمنيًا.",
                f"**المتغيرات الخاصة بالمجالس العسكرية** (`Military`، `Violence`، `Occupation`) {a} لا تُستخدم مع "
                "الأحزاب المسمّاة؛ أما `Monarchy`، المرمَّز سنةً بسنة (ملكية تحكم فعلًا)، فلا يخص إلا "
                f"{count(lang, chk['monarchy_spells'], 'party')} عند وصولها إلى السلطة {a} حُذف من النماذج وأُبقي "
                "متغيرًا وصفيًا.",
            ]
        out[lang] = {"synthesis": synthesis}
    return same_text_in_all_languages(out)


# ================================================================= final_panel
class PanelResults:
    """Hazard ratios of the three Cox models, read from the exported payload (final_panel.ipynb, 9.2)."""
    EQUIV = {"polity2": {"static": "polity2_entry", "corrected": "polity2_entry", "timevarying": "polity2_lag1"},
             "conflict": {"static": "conflict_entry", "corrected": "conflict_entry", "timevarying": "conflict_active_lag1"},
             "gdp": {"timevarying": "log_gdppc_lag1"}}

    def __init__(self, P):
        self.P = P
        self.hr = {m: {h["covariate"]: h for h in b["hazard_ratios"]} for m, b in P["models"].items()}
        ph = P["proportional_hazards"]
        self.cut, self.nph = ph["cut_years"], ph["corrected_covariates"]
        self.late = {(r["covariate"], r["period"]): r for r in records(ph["early_late"])}

    def across(self, concept):
        names = self.EQUIV.get(concept, {m: concept for m in ("static", "corrected", "timevarying")})
        out = []
        for m, var in names.items():
            if var not in self.hr[m]:
                continue
            if m == "corrected" and var in self.nph:
                e, l = self.late[(var, "early")], self.late[(var, "late")]
                sig = any(r["lower 95%"] > 1 or r["upper 95%"] < 1 for r in (e, l))
                out.append({"model": m, "hr": None, "sig": bool(sig), "early": e["HR"], "late": l["HR"]})
            else:
                r = self.hr[m][var]
                out.append({"model": m, "hr": r["hr"], "p": r["p"], "sig": r["p"] < ALPHA})
        return out

    @staticmethod
    def is_robust(res):
        hrs = [r["hr"] for r in res if r["hr"] is not None]
        same = all(h < 1 for h in hrs) or all(h > 1 for h in hrs)
        return len(res) >= 3 and all(r["sig"] for r in res) and same


def model_result(lang, r, cut):
    name = ("النموذج " if lang == "ar" else "") + MODEL_NAMES[r["model"]][lang]
    if r["hr"] is None:
        e, l = raw(lang, r["early"], 2), raw(lang, r["late"], 2)
        return {"fr": f"{name} : {iso(lang, 'HR = ' + e)} avant {cut} ans, {iso(lang, l)} après",
                "en": f"{name}: {iso(lang, 'HR = ' + e)} before {cut} years, {iso(lang, l)} after",
                "ar": f"{name}: {iso(lang, 'HR = ' + e)} قبل {count(lang, cut, 'year')} و{iso(lang, l)} بعدها"}[lang]
    sep = " : " if lang == "fr" else ": "
    return f"{name}{sep}{hr_txt(lang, r['hr'], r['p'])}"


def verdict(lang, res, robust):
    n_sig = sum(r["sig"] for r in res)
    k = len(res)
    if robust:
        return {"fr": f"significatif dans les {k} modèles", "en": f"significant in all {k} models",
                "ar": "ذو دلالة إحصائية في النماذج الثلاثة" if k == 3 else f"ذو دلالة إحصائية في النماذج كلها ({num(lang, k)})"}[lang]
    if n_sig == 0:
        return {"fr": "non significatif", "en": "not significant", "ar": "غير دالّ إحصائيًا"}[lang]
    return {"fr": f"significatif dans {n_sig} modèle{'s' if n_sig > 1 else ''} sur {k}",
            "en": f"significant in {n_sig} of {k} models",
            "ar": f"دالّ إحصائيًا في {count(lang, n_sig, 'model')} من أصل {num(lang, k)}"}[lang]


def concept_sentence(lang, R, concept, title):
    res = R.across(concept)
    detail = SEMI[lang].join(model_result(lang, r, R.cut) for r in res)
    return f"{title} — {detail} {ARROW[lang]} **{verdict(lang, res, R.is_robust(res))}**."


def dem_sentence(lang, row, model):
    """V-Dem against Polity2 for the democracy level (final_panel.ipynb, 5.4)."""
    name = MODEL_NAMES[model][lang]
    hp, pp, hv, pv = row["HR Polity2"], row["p Polity2"], row["HR V-Dem"], row["p V-Dem"]
    up = hv > 1
    if row["robuste"]:
        return {
            "fr": f"dans le modèle {name}, un niveau démocratique plus élevé {'augmente' if up else 'réduit'} le risque "
                  f"de chute avec V-Dem ({iso(lang, 'HR = ' + raw(lang, hv, 2))} par 0,1 point, {p_txt(lang, pv)}) comme "
                  f"avec Polity2 ({iso(lang, 'HR = ' + raw(lang, hp, 2))} par point, {p_txt(lang, pp)})",
            "en": f"in the {name} model, a higher democracy level {'increases' if up else 'reduces'} the risk of falling "
                  f"with V-Dem ({iso(lang, 'HR = ' + raw(lang, hv, 2))} per 0.1 point, {p_txt(lang, pv)}) as with Polity2 "
                  f"({iso(lang, 'HR = ' + raw(lang, hp, 2))} per point, {p_txt(lang, pp)})",
            "ar": f"في النموذج {name}، يؤدي ارتفاع مستوى الديمقراطية إلى {'زيادة' if up else 'خفض'} خطر السقوط باستخدام "
                  f"V-Dem ‏({iso(lang, 'HR = ' + raw(lang, hv, 2))} لكل {num(lang, 0.1, 1)} نقطة، {p_txt(lang, pv)}) كما "
                  f"باستخدام Polity2 ‏({iso(lang, 'HR = ' + raw(lang, hp, 2))} لكل نقطة، {p_txt(lang, pp)})",
        }[lang]
    return {
        "fr": f"dans le modèle {name}, l'effet du niveau démocratique n'est pas robuste au changement de mesure "
              f"(Polity2 : {hr_txt(lang, hp, pp)} ; V-Dem : {hr_txt(lang, hv, pv)})",
        "en": f"in the {name} model, the effect of the democracy level is not robust to the change of measure "
              f"(Polity2: {hr_txt(lang, hp, pp)}; V-Dem: {hr_txt(lang, hv, pv)})",
        "ar": f"في النموذج {name}، لا يصمد أثر مستوى الديمقراطية أمام تغيير المقياس "
              f"(Polity2: {hr_txt(lang, hp, pp)}؛ V-Dem: {hr_txt(lang, hv, pv)})",
    }[lang]


def vdem_summary(lang, P):
    vd = P["vdem_robustness"]
    samples = {r["_index"]: r for r in records(vd["samples"])}
    tabs = {k: {r["_index"]: r for r in records(vd[k])} for k in ("static", "timevarying")}
    dem_s, dem_t = tabs["static"]["niveau démocratique"], tabs["timevarying"]["niveau démocratique"]

    def sig_rows(tab):
        rows = [r for k, r in tab.items() if k != "Gov_Non code"]
        return [r for r in rows if r["p Polity2"] < ALPHA or r["p V-Dem"] < ALPHA]

    sig_s, sig_t = sig_rows(tabs["static"]), sig_rows(tabs["timevarying"])
    rob_s, rob_t = sum(r["robuste"] for r in sig_s), sum(r["robuste"] for r in sig_t)
    not_robust = [r["_index"] for r in sig_s + sig_t if not r["robuste"]]
    e_tv_v, e_tv_p = samples["Time-varying, V-Dem"]["chutes"], samples["Time-varying, Polity2"]["chutes"]
    e_s_v, e_s_p = samples["Statique, V-Dem"]["chutes"], samples["Statique, Polity2"]["chutes"]
    diff = signed(lang, e_tv_v - e_tv_p, 0)
    r, rho, n = vd["correlation_pearson"], vd["correlation_spearman"], vd["party_years_both"]
    ds, dt = dem_sentence(lang, dem_s, "static"), dem_sentence(lang, dem_t, "timevarying")
    nr = ", ".join(f"`{v}`" for v in not_robust)
    if lang == "fr":
        return (f"Sur les {count(lang, n, 'obs')} où les deux mesures existent, Polity2 et V-Dem sont fortement liés "
                f"(corrélation de Pearson {num(lang, r, 2)}, de Spearman {num(lang, rho, 2)}). Avec V-Dem, le modèle "
                f"time-varying conserve {count(lang, e_tv_v, 'fall')} contre {num(lang, e_tv_p)} avec Polity2 ({diff}), "
                f"et le modèle statique {num(lang, e_s_v)} contre {num(lang, e_s_p)}. {cap(ds)} ; {dt}. Parmi les "
                f"covariables significatives dans au moins une des deux versions, {rob_s} sur {len(sig_s)} sont robustes "
                f"dans le modèle statique et {rob_t} sur {len(sig_t)} dans le modèle time-varying"
                + (f" (non robustes : {nr})." if not_robust else ".")
                + " La modalité « non codée » n'entre pas dans ce décompte (ce n'est pas une stratégie).")
    if lang == "en":
        return (f"Over the {count(lang, n, 'obs')} where both measures exist, Polity2 and V-Dem are strongly related "
                f"(Pearson correlation {num(lang, r, 2)}, Spearman {num(lang, rho, 2)}). With V-Dem, the time-varying "
                f"model keeps {count(lang, e_tv_v, 'fall')} against {num(lang, e_tv_p)} with Polity2 ({diff}), and the "
                f"static model {num(lang, e_s_v)} against {num(lang, e_s_p)}. {cap(ds)}; {dt}. Among the covariates "
                f"significant in at least one of the two versions, {rob_s} of {len(sig_s)} are robust in the static "
                f"model and {rob_t} of {len(sig_t)} in the time-varying model"
                + (f" (not robust: {nr})." if not_robust else ".")
                + " The “not coded” category is left out of this count (it is not a strategy).")
    return (f"على {count(lang, n, 'obs')} (حزب-سنة) يتوفر فيها المقياسان، يرتبط Polity2 و V-Dem ارتباطًا قويًا "
            f"(معامل ارتباط بيرسون {num(lang, r, 2)}، وسبيرمان {num(lang, rho, 2)}). وباستخدام V-Dem يحتفظ النموذج "
            f"المتغير زمنيًا بـ{count(lang, e_tv_v, 'fall')} مقابل {num(lang, e_tv_p)} باستخدام Polity2 ‏({diff})، "
            f"ويحتفظ النموذج الثابت بـ{num(lang, e_s_v)} مقابل {num(lang, e_s_p)}. {ds}؛ {dt}. ومن بين المتغيرات "
            f"التفسيرية ذات الدلالة في إحدى الصيغتين على الأقل، يصمد {num(lang, rob_s)} من أصل {num(lang, len(sig_s))} "
            f"في النموذج الثابت و{num(lang, rob_t)} من أصل {num(lang, len(sig_t))} في النموذج المتغير زمنيًا"
            + (f" (غير المتينة: {nr})." if not_robust else ".")
            + " ولا تدخل فئة «غير مرمَّزة» في هذا الحساب، فهي ليست استراتيجية.")


def research_questions(lang, P, R, F):
    vd = P["vdem_robustness"]
    dem_s = {r["_index"]: r for r in records(vd["static"])}["niveau démocratique"]
    dem_t = {r["_index"]: r for r in records(vd["timevarying"])}["niveau démocratique"]
    hr = R.hr
    items = []

    # --- Origine
    origin_vars = [h for h in hr["static"] if h.startswith("Origin_")]
    robust_origins = [v for v in origin_vars if R.is_robust(R.across(v))]
    intro = {"fr": "Par rapport aux partis créés par un dictateur :", "en": "Compared with dictator-created parties:",
             "ar": "مقارنةً بالأحزاب التي أسسها حاكم مستبد:"}[lang]
    body = intro + "\n\n" + "\n".join("- " + concept_sentence(lang, R, v, FACTORS[v][lang][0]) for v in origin_vars) + "\n\n"
    if robust_origins:
        lower = all(hr["static"][v]["hr"] < 1 for v in robust_origins)
        names = join(lang, [ORIGIN_SHORT[v][lang] for v in robust_origins])
        body += {
            "fr": f"Les origines suivantes sont associées à un risque de chute {'plus faible' if lower else 'différent'} "
                  f"dans les trois modèles : {names}. C'est le résultat le plus stable de l'analyse. Il rejoint la "
                  "question centrale de Miller (2020), qui construit l'ARPD pour relier l'origine des partis autoritaires "
                  "à leur durabilité.",
            "en": f"The following origins are associated with a {'lower' if lower else 'different'} risk of falling in "
                  f"all three models: {names}. This is the most stable result of the analysis. It echoes the central "
                  "question of Miller (2020), who built the ARPD to link the origins of authoritarian parties to their "
                  "durability.",
            "ar": f"ترتبط الأصول التالية بخطر سقوط {'أقل' if lower else 'مختلف'} في النماذج الثلاثة: {names}. وهذه هي "
                  "النتيجة الأكثر ثباتًا في التحليل، وهي تتّسق مع السؤال المحوري لدى ميلر (2020) الذي أنشأ قاعدة بيانات "
                  "ARPD لربط أصول الأحزاب السلطوية بمدى ديمومتها.",
        }[lang]
    else:
        body += {"fr": "Aucune origine n'est significative dans les trois modèles.",
                 "en": "No origin is significant in all three models.",
                 "ar": "لا يوجد أصل ذو دلالة إحصائية في النماذج الثلاثة."}[lang]
    items.append(({"fr": "Origine du parti", "en": "Party origin", "ar": "أصل الحزب"}[lang], body))

    # --- Idéologie
    body = concept_sentence(lang, R, "Marxist?", FACTORS["Marxist?"][lang][0])
    if not any(r["sig"] for r in R.across("Marxist?")):
        p = pct(lang, F["pct_marxist_communist"])
        body += {
            "fr": f" L'idéologie n'a pas d'effet propre mesurable une fois l'origine prise en compte : {p} des partis "
                  "d'origine communiste sont aussi codés marxistes-léninistes, si bien que les deux variables portent en "
                  "grande partie la même information.",
            "en": f" Ideology has no measurable effect of its own once origin is taken into account: {p} of "
                  "communist-origin parties are also coded Marxist-Leninist, so the two variables largely carry the same "
                  "information.",
            "ar": f" لا يظهر للأيديولوجيا أثر مستقل قابل للقياس بعد أخذ الأصل في الحسبان: فـ{p} من الأحزاب ذات الأصل "
                  "الشيوعي مرمَّزة أيضًا على أنها ماركسية لينينية، ولذلك يحمل المتغيران المعلومة نفسها إلى حدّ كبير.",
        }[lang]
    items.append(({"fr": "Idéologie", "en": "Ideology", "ar": "الأيديولوجيا"}[lang], body))

    # --- Stratégie de gouvernance
    g = F["governance_counts_named"]
    total = sum(g.values())
    coded = total - g["Non code"]
    head = {
        "fr": f"Codée par Miller (2020) pour {num(lang, coded)} partis sur {num(lang, total)} : {num(lang, g['Policy-Based'])} "
              f"fondées sur les politiques publiques, {num(lang, g['Repressive'])} répressives, "
              f"{num(lang, g['Clientelist'])} clientélistes. Par rapport aux politiques publiques :",
        "en": f"Coded by Miller (2020) for {num(lang, coded)} of {count(lang, total, 'party')}: {num(lang, g['Policy-Based'])} "
              f"policy-based, {num(lang, g['Repressive'])} repressive, {num(lang, g['Clientelist'])} clientelist. "
              "Compared with policy-based strategies:",
        "ar": f"رمَّز ميلر (2020) استراتيجية الحكم لـ{num(lang, coded)} من أصل {count(lang, total, 'party')}: "
              f"{num(lang, g['Policy-Based'])} منها قائمة على السياسات العامة، و{num(lang, g['Repressive'])} قمعية، "
              f"و{num(lang, g['Clientelist'])} زبائنية. مقارنةً بالاستراتيجية القائمة على السياسات العامة:",
    }[lang]
    body = (head + "\n\n" + "\n".join("- " + concept_sentence(lang, R, v, FACTORS[v][lang][0])
                                      for v in ("Gov_Repressive", "Gov_Clientelist")) + "\n\n")
    cl = R.across("Gov_Clientelist")
    cl_hrs = [r["hr"] for r in cl if r["hr"] is not None]
    if sum(r["sig"] for r in cl) >= 2 and all(h < 1 for h in cl_hrs):
        n_cl = count(lang, g["Clientelist"], "party")
        body += {
            "fr": "L'effet protecteur d'une stratégie clientéliste est cohérent avec l'analyse de Magaloni (2006), pour "
                  "qui la distribution de ressources aux électeurs et aux élites est un mécanisme central de survie des "
                  f"partis hégémoniques. Il repose toutefois sur {n_cl} seulement et doit être lu avec prudence.",
            "en": "The protective effect of a clientelist strategy is consistent with Magaloni (2006), for whom "
                  "distributing resources to voters and elites is a central survival mechanism of hegemonic parties. "
                  f"It rests, however, on only {n_cl} and must be read with caution.",
            "ar": "ويتّسق الأثر الحمائي لاستراتيجية الزبائنية مع تحليل ماغالوني (2006)، التي ترى أن توزيع الموارد على "
                  f"الناخبين والنخب آلية محورية لبقاء الأحزاب المهيمنة. غير أن هذا الأثر يستند إلى {n_cl} فقط، "
                  "وينبغي قراءته بحذر.",
        }[lang]
    items.append(({"fr": "Stratégie de gouvernance", "en": "Governance strategy", "ar": "استراتيجية الحكم"}[lang], body))

    # --- Niveau démocratique
    body = concept_sentence(lang, R, "polity2", FACTORS["polity2"][lang][0])
    st = hr["static"]["polity2_entry"]
    if st["p"] < ALPHA and st["hr"] > 1:
        h10 = num(lang, st["hr"] ** 10, 2)
        body += {
            "fr": " Dans le modèle statique, un régime plus ouvert de 10 points sur l'échelle Polity2 au moment de "
                  f"l'entrée au pouvoir a un risque de chute multiplié par {h10}. Les partis autoritaires durent donc moins "
                  "longtemps dans les régimes les plus ouverts.",
            "en": " In the static model, a regime 10 points more open on the Polity2 scale at entry into power has its "
                  f"risk of falling multiplied by {h10}. Authoritarian parties therefore last less long in the most open "
                  "regimes.",
            "ar": " في النموذج الثابت، يُضرب خطر السقوط في "
                  f"{h10} لدى نظام أكثر انفتاحًا بعشر نقاط على مقياس Polity2 عند الوصول إلى السلطة. فالأحزاب السلطوية "
                  "تدوم إذن مدة أقصر في الأنظمة الأكثر انفتاحًا.",
        }[lang]
    ds, dt = dem_sentence(lang, dem_s, "static"), dem_sentence(lang, dem_t, "timevarying")
    body += {"fr": f" Robustesse (section 5.4, V-Dem au lieu de Polity2) : {ds} ; {dt}.",
             "en": f" Robustness (Section 5.4, V-Dem instead of Polity2): {ds}; {dt}.",
             "ar": f" المتانة (القسم 5.4، باستخدام V-Dem بدل Polity2): {ds}؛ {dt}."}[lang]
    items.append(({"fr": "Niveau démocratique", "en": "Democracy level", "ar": "مستوى الديمقراطية"}[lang], body))

    # --- Conflit
    body = concept_sentence(lang, R, "conflict", FACTORS["conflict"][lang][0])
    tv = hr["timevarying"]["conflict_active_lag1"]
    tv_sig = tv["p"] < ALPHA
    st_sig = hr["static"]["conflict_entry"]["p"] < ALPHA
    if tv_sig:
        up = tv["hr"] > 1
        body += {"fr": f" Un conflit en cours l'année précédente {'augmente' if up else 'réduit'} le risque de chute "
                       "(modèle time-varying).",
                 "en": f" An ongoing conflict in the previous year {'increases' if up else 'reduces'} the risk of falling "
                       "(time-varying model).",
                 "ar": f" يؤدي وجود نزاع جارٍ في السنة السابقة إلى {'زيادة' if up else 'خفض'} خطر السقوط (النموذج المتغير "
                       "زمنيًا)."}[lang]
    if not st_sig:
        body += {"fr": " Un conflit au moment de l'entrée au pouvoir n'a pas d'effet moyen significatif (modèle statique).",
                 "en": " A conflict at the time of entry into power has no significant average effect (static model).",
                 "ar": " أما النزاع عند الوصول إلى السلطة فليس له أثر متوسط ذو دلالة إحصائية (النموذج الثابت)."}[lang]
    late_diff_sig = False
    if "conflict_entry" in R.nph:
        e, l = R.late[("conflict_entry", "early")]["HR"], R.late[("conflict_entry", "late")]["HR"]
        p_late = hr["corrected"]["conflict_entry_x_late"]["p"]
        late_diff_sig = p_late < ALPHA
        he, hl = iso(lang, "HR = " + raw(lang, e, 2)), iso(lang, "HR = " + raw(lang, l, 2))
        body += {
            "fr": f" Le modèle corrigé indique toutefois un effet qui change avec le temps : {he} pendant les {R.cut} "
                  f"premières années au pouvoir, puis {hl} ; la différence entre les deux périodes "
                  f"{'est' if late_diff_sig else 'n’est pas'} significative ({p_txt(lang, p_late)}).",
            "en": f" The corrected model nevertheless shows an effect that changes over time: {he} during the first "
                  f"{R.cut} years in power, then {hl}; the difference between the two periods is "
                  f"{'' if late_diff_sig else 'not '}significant ({p_txt(lang, p_late)}).",
            "ar": f" غير أن النموذج المصحَّح يُظهر أثرًا يتغير مع الزمن: {he} خلال السنوات الـ{num(lang, R.cut)} الأولى "
                  f"في السلطة، ثم {hl}؛ والفرق بين الفترتين {'ذو دلالة إحصائية' if late_diff_sig else 'ليس ذا دلالة إحصائية'} "
                  f"({p_txt(lang, p_late)}).",
        }[lang].replace("n’est", "n'est")
    if tv_sig and not st_sig and not late_diff_sig:
        body += {"fr": " C'est donc surtout la conflictualité pendant le règne, que seul le modèle time-varying mesure, "
                       "qui est associée au risque de chute.",
                 "en": " It is therefore mainly conflict during the party's rule, which only the time-varying model "
                       "measures, that is associated with the risk of falling.",
                 "ar": " وبذلك فإن النزاعات خلال فترة الحكم، التي لا يقيسها إلا النموذج المتغير زمنيًا، هي التي ترتبط "
                       "أساسًا بخطر السقوط."}[lang]
    items.append(({"fr": "Conflit armé", "en": "Armed conflict", "ar": "النزاع المسلح"}[lang], body))

    # --- PIB
    a, b = hr["timevarying"]["log_gdppc_lag1"], hr["static_gdp"]["log_gdppc_entry"]
    none_sig = a["p"] >= ALPHA and b["p"] >= ALPHA
    e_const = iso(lang, f"e ≈ {raw(lang, 2.7, 1)}")
    body = {
        "fr": f"Time-varying : {hr_txt(lang, a['hr'], a['p'])} ; variante statique avec PIB (section 5.1.c) : "
              f"{hr_txt(lang, b['hr'], b['p'])}. Les HR sont exprimés par unité de log, soit un PIB par habitant "
              f"multiplié par {e_const}. "
              + ("Aucun effet significatif du niveau de richesse n'est mis en évidence." if none_sig
                 else "Le niveau de richesse a un effet significatif dans au moins un des deux modèles."),
        "en": f"Time-varying model: {hr_txt(lang, a['hr'], a['p'])}; static variant with GDP (Section 5.1.c): "
              f"{hr_txt(lang, b['hr'], b['p'])}. Hazard ratios are per log unit, i.e. GDP per capita multiplied by "
              f"{e_const}. "
              + ("No significant effect of wealth is found." if none_sig
                 else "Wealth has a significant effect in at least one of the two models."),
        "ar": f"النموذج المتغير زمنيًا: {hr_txt(lang, a['hr'], a['p'])}؛ الصيغة الثابتة مع الناتج المحلي (القسم 5.1.c): "
              f"{hr_txt(lang, b['hr'], b['p'])}. وتُحسب نسب الخطر لكل وحدة لوغاريتمية، أي عند ضرب نصيب الفرد من الناتج "
              f"في {e_const}. "
              + ("لا يظهر أي أثر ذي دلالة إحصائية لمستوى الثروة." if none_sig
                 else "لمستوى الثروة أثر ذو دلالة إحصائية في واحد على الأقل من النموذجين."),
    }[lang]
    items.append(({"fr": "Richesse (PIB par habitant, Maddison)", "en": "Wealth (GDP per capita, Maddison)",
                   "ar": "الثروة (نصيب الفرد من الناتج المحلي، Maddison)"}[lang], body))
    return [{"title": t, "body": b} for t, b in items]


def limits(lang, P, F):
    s, ph, m = P["sample"], P["proportional_hazards"], P["models"]
    n = s["named_spells"]
    cens = n - s["events_all"]
    lost_static = n - s["static_spells"]
    lost_tv = s["events_all"] - s["tv_events"]
    nc_hr = {h["covariate"]: h for h in m["static"]["hazard_ratios"]}["Gov_Non code"]["hr"]
    wald_sig = ph["wald_p_at_cut"] < ALPHA
    nph = join(lang, [FACTORS[v][lang][1] if v in FACTORS else f"`{v}`" for v in ph["corrected_covariates"]])
    remaining = (join(lang, [f"`{v}`" for v in ph["remaining_violations"]]) if ph["remaining_violations"]
                 else {"fr": "aucune", "en": "none", "ar": "لا شيء"}[lang])
    cs, cc = num(lang, m["static"]["c_index_in_sample"], 3), num(lang, m["corrected"]["c_index_in_sample"], 3)
    rate = pct(lang, cens / n * 100, 1)
    delay = count(lang, round(F["tv_median_late_entry"]), "year")
    pw = p_txt(lang, ph["wald_p_at_cut"], 4)
    cut = ph["cut_years"]
    if lang == "fr":
        items = [
            f"**Biais de sélection (juntes exclues)** : {count(lang, s['junta_spells_excluded'], 'regime')} sans parti nommé "
            "(`Party = \"N\"`) sont exclus ; les conclusions ne portent que sur les partis nommés.",
            f"**Peu d'observations censurées** : {count(lang, cens, 'party')} sur {num(lang, n)} sont encore au pouvoir en fin "
            f"d'observation (taux de censure de {rate}). Si ces partis sont structurellement plus robustes, la censure est "
            "informative et les estimations sont biaisées.",
            f"**Dépendance intra-pays** : {count(lang, F['countries_multiple_spells'], 'country')} connaissent plusieurs "
            f"partis au pouvoir successifs (jusqu'à {num(lang, F['max_spells_per_country'])}). Les erreurs standards sont "
            "groupées par pays dans les modèles statique et corrigé (`cluster_col=\"Country\"`), mais pas dans le modèle "
            "time-varying, dont les p-values sont donc probablement trop optimistes.",
            f"**Conflits avant 1946** : UCDP ne commence qu'en 1946. Le conflit à l'entrée est inconnu pour "
            f"{count(lang, F['conflict_entry_missing'], 'party')} ; avec les autres valeurs manquantes, le modèle statique "
            f"perd {num(lang, lost_static)} partis sur {num(lang, n)}. Dans le modèle time-varying, "
            f"{num(lang, F['tv_late_entries'])} partis sur {num(lang, s['tv_spells'])} entrent dans l'analyse après leur "
            f"arrivée au pouvoir (troncature à gauche ; retard médian de {delay}, le plus souvent parce que la valeur de "
            "l'année précédente du pays n'existe pas pour la première année).",
            f"**Événements perdus par le modèle time-varying** : {count(lang, s['tv_events'], 'fall')} conservées sur "
            f"{num(lang, s['events_all'])}, faute de données macro complètes ({count(lang, lost_tv, 'fall')} perdues).",
            f"**PIB incomplet** : le PIB Maddison manque pour {pct(lang, F['gdp_missing_pct'], 1)} des parti-années (pays "
            "non couverts, comme l'Allemagne de l'Est ou la Corée du Nord).",
            f"**Stratégie de gouvernance partiellement codée** : Miller (2020) ne la code que pour "
            f"{pct(lang, F['governance_coded_pct'])} des partis. Les partis non codés forment une modalité à part, dont "
            f"l'effet ({hr_txt(lang, nc_hr)}) montre que les données manquent de façon non aléatoire ; il ne s'interprète "
            "pas comme une stratégie.",
            "**Monarchie retirée des modèles** : codée par nos soins année par année (un monarque gouverne réellement), "
            f"elle ne concerne que {count(lang, F['monarchy_named_spells'], 'party')} à leur arrivée au pouvoir "
            f"({count(lang, F['monarchy_named_party_years'], 'obs')}), trop peu pour estimer un effet ; elle reste dans "
            "le panel comme variable descriptive.",
            f"**Extension post-2015 codée à la main** : {count(lang, F['post2015_events'], 'fall')} postérieures à 2015 ont "
            "été codées à partir de sources publiques (`01_data_merging.ipynb`, section 9 ; voir aussi `final.ipynb`, "
            "section 4.0). Certains cas relèvent d'un choix de codage (fusion, changement de nom).",
            f"**Risques proportionnels** : la correction précoce / tardive porte sur {nph} ; au seuil retenu de "
            f"{count(lang, cut, 'year')}, les effets tardifs {'diffèrent' if wald_sig else 'ne diffèrent pas'} "
            f"significativement des effets précoces (test de Wald, {pw}). Après correction, le test de Cox avec "
            f"interaction temporelle signale encore : {remaining}.",
            f"**Pouvoir prédictif mesuré sur les données d'estimation** : les C-index (statique {cs}, corrigé {cc}) sont "
            "calculés sur l'échantillon qui a servi à estimer les modèles, et sont donc optimistes (la validation croisée "
            "de `final.ipynb`, section 6.2, illustre cet écart).",
        ]
    elif lang == "en":
        items = [
            f"**Selection bias (juntas excluded)**: {count(lang, s['junta_spells_excluded'], 'regime')} without a named "
            "party (`Party = \"N\"`) are excluded; the conclusions apply to named parties only.",
            f"**Few censored observations**: {num(lang, cens)} of {count(lang, n, 'party')} are still in power at the end "
            f"of the observation period (censoring rate {rate}). If these parties are structurally more robust, censoring "
            "is informative and the estimates are biased.",
            f"**Within-country dependence**: {count(lang, F['countries_multiple_spells'], 'country')} have several "
            f"successive ruling parties (up to {num(lang, F['max_spells_per_country'])}). Standard errors are clustered "
            "by country in the static and corrected models (`cluster_col=\"Country\"`), but not in the time-varying "
            "model, whose p-values are therefore probably too optimistic.",
            f"**Conflicts before 1946**: UCDP starts in 1946. Conflict at entry is unknown for "
            f"{count(lang, F['conflict_entry_missing'], 'party')}; with the other missing values, the static model loses "
            f"{num(lang, lost_static)} of {count(lang, n, 'party')}. In the time-varying model, "
            f"{num(lang, F['tv_late_entries'])} of {count(lang, s['tv_spells'], 'party')} enter the analysis after their "
            f"accession to power (left truncation; median delay of {delay}, mostly because the country's previous-year "
            "value does not exist for the first year).",
            f"**Events lost by the time-varying model**: {num(lang, s['tv_events'])} of {count(lang, s['events_all'], 'fall')} "
            f"are kept, for lack of complete macro data ({count(lang, lost_tv, 'fall')} lost).",
            f"**Incomplete GDP**: Maddison GDP is missing for {pct(lang, F['gdp_missing_pct'], 1)} of party-years "
            "(countries not covered, such as East Germany or North Korea).",
            f"**Governance strategy only partly coded**: Miller (2020) codes it for only "
            f"{pct(lang, F['governance_coded_pct'])} of parties. Uncoded parties form a separate category, whose effect "
            f"({hr_txt(lang, nc_hr)}) shows that the data are not missing at random; it is not to be read as a strategy.",
            "**Monarchy removed from the models**: coded by us year by year (a monarch actually governs), it applies "
            f"to only {count(lang, F['monarchy_named_spells'], 'party')} when they came to power "
            f"({count(lang, F['monarchy_named_party_years'], 'obs')}), too few to estimate an effect; it stays in the "
            "panel as a descriptive variable.",
            f"**Post-2015 extension coded by hand**: {count(lang, F['post2015_events'], 'fall')} after 2015 were coded "
            "from public sources (`01_data_merging.ipynb`, Section 9; see also `final.ipynb`, Section 4.0). Some cases "
            "involve a coding choice (merger, change of name).",
            f"**Proportional hazards**: the early/late correction applies to {nph}; at the chosen cut-off of "
            f"{count(lang, cut, 'year')}, late effects {'differ' if wald_sig else 'do not differ'} significantly from "
            f"early effects (Wald test, {pw}). After correction, the Cox test with a time interaction still flags: "
            f"{remaining}.",
            f"**Predictive power measured on the estimation data**: the C-indices (static {cs}, corrected {cc}) are "
            "computed on the sample used to estimate the models, and are therefore optimistic (the cross-validation "
            "in `final.ipynb`, Section 6.2, illustrates the gap).",
        ]
    else:
        items = [
            f"**انحياز الاختيار (استبعاد المجالس العسكرية)**: استُبعد {count(lang, s['junta_spells_excluded'], 'regime')} "
            "بلا حزب مسمّى (`Party = \"N\"`)، ولا تنطبق الاستنتاجات إلا على الأحزاب المسمّاة.",
            f"**قلة المشاهدات المراقَبة**: لا يزال {num(lang, cens)} من أصل {count(lang, n, 'party')} في السلطة عند "
            f"نهاية فترة الرصد (معدل رقابة {rate}). وإذا كانت هذه الأحزاب أكثر صمودًا بطبيعتها، فإن الرقابة لا تكون "
            "عشوائية وتكون التقديرات متحيزة.",
            f"**الاعتماد داخل البلد الواحد**: شهد {count(lang, F['countries_multiple_spells'], 'country')} أكثر من حزب "
            f"حاكم متعاقب (حتى {num(lang, F['max_spells_per_country'])}). وقد جُمِّعت الأخطاء المعيارية حسب البلد في "
            "النموذجين الثابت والمصحَّح (`cluster_col=\"Country\"`)، لكن ليس في النموذج المتغير زمنيًا، ولذلك يُرجَّح أن "
            "تكون قيمه الاحتمالية متفائلة أكثر من اللازم.",
            f"**النزاعات قبل عام 1946**: تبدأ بيانات UCDP عام 1946، ولذلك فإن وجود نزاع عند الوصول إلى السلطة مجهول "
            f"لـ{count(lang, F['conflict_entry_missing'], 'party')}؛ ومع القيم الناقصة الأخرى يفقد النموذج الثابت "
            f"{num(lang, lost_static)} من أصل {count(lang, n, 'party')}. وفي النموذج المتغير زمنيًا، يدخل "
            f"{num(lang, F['tv_late_entries'])} من أصل {count(lang, s['tv_spells'], 'party')} التحليلَ بعد وصولها إلى "
            f"السلطة (البتر من اليسار؛ بتأخر وسيطه {delay})، وغالبًا لأن قيمة السنة السابقة للبلد غير متوفرة للسنة "
            "الأولى.",
            f"**أحداث يفقدها النموذج المتغير زمنيًا**: يحتفظ النموذج بـ{num(lang, s['tv_events'])} من أصل "
            f"{count(lang, s['events_all'], 'fall')} بسبب نقص البيانات الكلية ({count(lang, lost_tv, 'fall')} مفقودة).",
            f"**بيانات ناتج محلي ناقصة**: بيانات Maddison عن الناتج المحلي مفقودة لـ{pct(lang, F['gdp_missing_pct'], 1)} "
            "من مشاهدات حزب-سنة (بلدان غير مشمولة، مثل ألمانيا الشرقية أو كوريا الشمالية).",
            f"**استراتيجية حكم مرمَّزة جزئيًا**: لم يرمِّزها ميلر (2020) إلا لـ{pct(lang, F['governance_coded_pct'])} من "
            f"الأحزاب. وتشكّل الأحزاب غير المرمَّزة فئة مستقلة يُظهر أثرها ({hr_txt(lang, nc_hr)}) أن البيانات ناقصة "
            "بصورة غير عشوائية؛ ولا يُفسَّر هذا الأثر على أنه استراتيجية.",
            "**حذف الملكية من النماذج**: رمَّزناها سنةً بسنة (ملك يحكم فعلًا)، ولا تخص إلا "
            f"{count(lang, F['monarchy_named_spells'], 'party')} عند وصولها إلى السلطة "
            f"({count(lang, F['monarchy_named_party_years'], 'obs')})، وهو عدد أقل من أن يسمح بتقدير أثرها؛ "
            "وتبقى في البيانات متغيرًا وصفيًا.",
            f"**امتداد ما بعد 2015 مرمَّز يدويًا**: رُمِّزت {count(lang, F['post2015_events'], 'fall')} لاحقة لعام 2015 "
            "انطلاقًا من مصادر عامة (`01_data_merging.ipynb`، القسم 9؛ وانظر أيضًا `final.ipynb`، القسم 4.0). وتنطوي "
            "بعض الحالات على خيار في الترميز (اندماج، تغيير اسم).",
            f"**المخاطر المتناسبة**: يشمل تصحيح الأثر المبكر/المتأخر {nph}؛ وعند العتبة المعتمدة البالغة "
            f"{count(lang, cut, 'year')} {'تختلف' if wald_sig else 'لا تختلف'} الآثار المتأخرة اختلافًا ذا دلالة عن "
            f"الآثار المبكرة (اختبار والد، {pw}). وبعد التصحيح، لا يزال اختبار كوكس مع التفاعل الزمني يشير إلى: "
            f"{remaining}.",
            f"**قوة تنبؤية مقيسة على بيانات التقدير**: حُسبت مؤشرات التوافق (الثابت {cs}، المصحَّح {cc}) على العيّنة "
            "نفسها التي قُدِّرت بها النماذج، ولذلك فهي متفائلة (ويوضّح التحقق المتقاطع في `final.ipynb`، القسم 6.2، هذا "
            "الفارق).",
        ]
    return "\n".join("* " + it for it in items)


def conclusion(lang, P, R, F):
    s, hr = P["sample"], R.hr
    n_obs, n_ev = s["static_spells"], s["static_events"]
    n_cens = n_obs - n_ev
    concepts = [v for v in hr["static"] if v not in ("polity2_entry", "conflict_entry", "Gov_Non code")]
    concepts += ["polity2", "conflict", "gdp"]
    robust, partial, absent = [], [], []
    for c in concepts:
        res = R.across(c)
        if not res:
            continue
        n_sig = sum(r["sig"] for r in res)
        hrs = [r["hr"] for r in res if r["hr"] is not None]
        name = FACTORS[c][lang][1]
        if R.is_robust(res):
            kind = {"fr": ("protecteur", "aggravant"), "en": ("protective", "aggravating"),
                    "ar": ("أثر حمائي", "أثر يزيد الخطر")}[lang][0 if hrs[0] < 1 else 1]
            where = {"fr": "HR statique", "en": "static HR", "ar": "في النموذج الثابت"}[lang]
            hr_s = iso(lang, "HR = " + raw(lang, hrs[0], 2))
            robust.append({"fr": f"{name} ({kind}, {where} = {raw(lang, hrs[0], 2)})",
                           "en": f"{name} ({kind}, {where} = {raw(lang, hrs[0], 2)})",
                           "ar": f"{name} ({kind}، {hr_s} {where})"}[lang])
        elif n_sig > 0:
            partial.append({"fr": f"{name} ({n_sig} modèle{'s' if n_sig > 1 else ''} sur {len(res)})",
                            "en": f"{name} ({n_sig} of {len(res)} models)",
                            "ar": f"{name} (في {count(lang, n_sig, 'model')} من أصل {num(lang, len(res))})"}[lang])
        else:
            absent.append(name)
    robust_vars = [c for c in concepts if R.is_robust(R.across(c))]
    static_name = {c: R.EQUIV.get(c, {}).get("static", c) for c in robust_vars}
    in_gdp = [c for c in robust_vars if static_name[c] in hr["static_gdp"]]
    still = [c for c in in_gdp if hr["static_gdp"][static_name[c]]["p"] < ALPHA]
    small = ""
    for gv in [c for c in robust_vars if c.startswith("Gov_")]:
        a = count(lang, F["governance_counts_static"][gv[4:]], "party")
        b = num(lang, F["governance_counts_named"][gv[4:]])
        small += {"fr": f" L'effet de la {FACTORS[gv][lang][1]} repose sur {a} du modèle statique ({b} dans l'ensemble "
                        "des données) seulement et doit être confirmé sur un codage plus complet.",
                  "en": f" The effect of the {FACTORS[gv][lang][1]} rests on only {a} of the static model ({b} in the full "
                        "data) and needs to be confirmed with more complete coding.",
                  "ar": f" ويستند أثر {FACTORS[gv][lang][1]} إلى {a} فقط من أحزاب النموذج الثابت ({b} في مجمل البيانات)، "
                        "ويلزم تأكيده بترميز أكثر اكتمالًا."}[lang]
    sep = SEMI[lang]
    robust_txt = sep.join(robust) if robust else {"fr": "aucun facteur", "en": "no factor", "ar": "لا يوجد أي عامل"}[lang]
    partial_txt = ({"fr": "D'autres facteurs ne sont significatifs que dans une partie des modèles : ",
                    "en": "Other factors are significant in only some of the models: ",
                    "ar": "وثمة عوامل أخرى ذات دلالة في بعض النماذج فقط: "}[lang] + sep.join(partial) + ". "
                   if partial else "")
    absent_txt = ({"fr": "Aucun effet significatif n'est trouvé pour : ", "en": "No significant effect is found for: ",
                   "ar": "ولم يظهر أي أثر ذي دلالة إحصائية لكلٍّ من: "}[lang] + COMMA[lang].join(absent) + "."
                  if absent else "")
    vs = vdem_summary(lang, P)
    c_static = num(lang, P["models"]["static"]["c_index_in_sample"], 2)
    tv_n = s["tv_spells"]
    k, mx = len(still), len(in_gdp)
    if lang == "fr":
        return (
            "***Réponse à la problématique.***\n"
            "La question posée est : quels facteurs structurels, institutionnels et temporels (conflit, PIB, niveau "
            "démocratique) influencent la durée de vie des partis autoritaires ? Sur "
            f"{count(lang, n_obs, 'party')} nommés dans le modèle statique ({count(lang, n_ev, 'fall')}, "
            f"{count(lang, n_cens, 'party')} encore au pouvoir), les facteurs associés de façon significative à la durée "
            f"de vie dans les trois modèles sont : {robust_txt}.{small} {partial_txt}{absent_txt}\n\n"
            "***Robustesse.***\n"
            f"Les trois modèles diffèrent par leur échantillon ({count(lang, n_obs, 'party')} pour le modèle statique, "
            f"{num(lang, tv_n)} pour le modèle time-varying), par la mesure des variables macro (valeur à l'entrée au "
            "pouvoir ou valeur de l'année précédente) et par le traitement de la non-proportionnalité. Les effets "
            "significatifs dans les trois modèles ne dépendent donc pas de ces choix. Dans la variante statique avec PIB "
            f"(section 5.1.c), {k} des {mx} effets robustes qui y sont estimés restent significatifs. Le pouvoir "
            f"discriminant reste modéré (C-index de {c_static} sur les données d'estimation) : ces facteurs expliquent "
            "une partie seulement de la durée de vie des partis.\n\n"
            "***Perspectives.***\n"
            f"(1) Un modèle à fragilité (*frailty*) par pays tiendrait compte des "
            f"{count(lang, F['countries_multiple_spells'], 'country')} qui connaissent plusieurs partis au pouvoir "
            f"successifs. (2) Un modèle à risques concurrents distinguerait les {count(lang, F['end_modes'], 'way')} dont "
            "un parti quitte le pouvoir (élection, coup d'État, révolution…), dont les déterminants n'ont pas de raison "
            f"d'être les mêmes. (3) Polity5 s'arrête en {F['polity_last_year']} ; l'indice de démocratie électorale de "
            f"V-Dem (`v2x_polyarchy`), disponible pour {pct(lang, F['vdem_coverage_pct'])} des parti-années, a été "
            f"utilisé comme test de robustesse (section 5.4) : {vs[0].lower() + vs[1:]} Une analyse fondée entièrement "
            "sur V-Dem permettrait d'étendre le niveau démocratique jusqu'en 2024 dans tous les modèles."
        )
    if lang == "en":
        return (
            "***Answer to the research question.***\n"
            "The question is: which structural, institutional and time-varying factors (conflict, GDP, democracy level) "
            f"influence how long authoritarian parties last? Of the {count(lang, n_obs, 'party')} in the static model "
            f"({count(lang, n_ev, 'fall')}, {count(lang, n_cens, 'party')} still in power), the factors significantly "
            f"associated with survival in all three models are: {robust_txt}.{small} {partial_txt}{absent_txt}\n\n"
            "***Robustness.***\n"
            f"The three models differ in their sample ({count(lang, n_obs, 'party')} for the static model, "
            f"{num(lang, tv_n)} for the time-varying model), in how macro variables are measured (value at entry into "
            "power or previous-year value) and in how non-proportionality is handled. The effects that are significant "
            "in all three models therefore do not depend on these choices. In the static variant with GDP "
            f"(Section 5.1.c), {k} of the {mx} robust effects estimated there remain significant. Discrimination remains "
            f"moderate (C-index of {c_static} on the estimation data): these factors explain only part of how long "
            "parties last.\n\n"
            "***Outlook.***\n"
            f"(1) A frailty model by country would account for the {count(lang, F['countries_multiple_spells'], 'country')} "
            "with several successive ruling parties. (2) A competing-risks model would distinguish the "
            f"{count(lang, F['end_modes'], 'way')} in which a party leaves power (election, coup, revolution…), whose "
            f"determinants have no reason to be the same. (3) Polity5 stops in {F['polity_last_year']}; V-Dem's "
            f"electoral democracy index (`v2x_polyarchy`), available for {pct(lang, F['vdem_coverage_pct'])} of "
            f"party-years, was used as a robustness check (Section 5.4): {vs[0].lower() + vs[1:]} An analysis based "
            "entirely on V-Dem would extend the democracy level to 2024 in all models."
        )
    return (
        "***الإجابة عن إشكالية البحث.***\n"
        "السؤال المطروح هو: ما العوامل البنيوية والمؤسسية والزمنية (النزاع، والناتج المحلي، ومستوى الديمقراطية) التي "
        f"تؤثر في مدة بقاء الأحزاب السلطوية في الحكم؟ من بين {count(lang, n_obs, 'party')} مسمّى في النموذج الثابت "
        f"({count(lang, n_ev, 'fall')}، و{count(lang, n_cens, 'party')} ما زالت في السلطة)، فإن العوامل المرتبطة ارتباطًا "
        f"ذا دلالة إحصائية بمدة البقاء في النماذج الثلاثة هي: {robust_txt}.{small} {partial_txt}{absent_txt}\n\n"
        "***المتانة.***\n"
        f"تختلف النماذج الثلاثة من حيث عيّنتها ({count(lang, n_obs, 'party')} في النموذج الثابت و{num(lang, tv_n)} في "
        "النموذج المتغير زمنيًا)، ومن حيث قياس المتغيرات الكلية (القيمة عند الوصول إلى السلطة أو قيمة السنة السابقة)، "
        "ومن حيث معالجة عدم تناسب المخاطر. ولذلك فإن الآثار ذات الدلالة في النماذج الثلاثة لا تتوقف على هذه الخيارات. "
        f"وفي الصيغة الثابتة مع الناتج المحلي (القسم 5.1.c)، يظل {num(lang, k)} من أصل {count(lang, mx, 'effect')} "
        f"متينة مقدَّرة فيها ذا دلالة إحصائية. وتبقى القدرة التمييزية متوسطة (مؤشر توافق {c_static} على بيانات "
        "التقدير): فهذه العوامل لا تفسر إلا جزءًا من مدة بقاء الأحزاب.\n\n"
        "***آفاق.***\n"
        f"(1) من شأن نموذج هشاشة (*frailty*) على مستوى البلد أن يراعي {count(lang, F['countries_multiple_spells'], 'country')} "
        "شهدت أكثر من حزب حاكم متعاقب. (2) ومن شأن نموذج المخاطر المتنافسة أن يميّز بين الطرق الـ"
        f"{num(lang, F['end_modes'])} التي يغادر بها الحزب السلطة (انتخابات، انقلاب، ثورة…)، إذ لا يوجد ما يدعو إلى أن "
        f"تكون محدداتها واحدة. (3) تتوقف بيانات Polity5 عام {F['polity_last_year']}؛ وقد استُخدم مؤشر الديمقراطية "
        f"الانتخابية من V-Dem ‏(`v2x_polyarchy`)، المتوفر لـ{pct(lang, F['vdem_coverage_pct'])} من مشاهدات حزب-سنة، "
        f"اختبارًا للمتانة (القسم 5.4): {vs} ومن شأن تحليل قائم بالكامل على V-Dem أن يمدّ قياس مستوى الديمقراطية حتى "
        "عام 2024 في جميع النماذج."
    )


def panel_texts(site_panel):
    P = jsonable(site_panel)
    F = P["facts"]
    R = PanelResults(P)
    return same_text_in_all_languages({lang: {
        "research_questions": research_questions(lang, P, R, F),
        "limits": limits(lang, P, F),
        "conclusion": conclusion(lang, P, R, F),
        "vdem_summary": vdem_summary(lang, P),
    } for lang in LANGS})


# ================================================================= 03_ml_survival
def describe_shape(lang, x, y):
    """Shape of a non-linear partial-dependence curve (rules of 03_ml_survival.ipynb, Section 6.2)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    amplitude = y.max() - y.min()
    i_min, i_max = int(np.argmin(y)), int(np.argmax(y))
    interior = lambda i: 0 < i < len(y) - 1  # noqa: E731
    if interior(i_min) and min(y[0], y[-1]) - y[i_min] >= amplitude / 4:
        v = gnum(lang, x[i_min])
        return {"fr": f"en U (minimum vers {v})", "en": f"U-shaped (minimum near {v})",
                "ar": f"على شكل U (الحد الأدنى قرب {v})"}[lang]
    if interior(i_max) and y[i_max] - max(y[0], y[-1]) >= amplitude / 4:
        v = gnum(lang, x[i_max])
        return {"fr": f"en cloche (maximum vers {v})", "en": f"bell-shaped (maximum near {v})",
                "ar": f"على شكل جرس (الحد الأقصى قرب {v})"}[lang]
    up = y[-1] > y[0]
    steps = np.abs(np.diff(y))
    j = int(np.argmax(steps))
    if steps[j] > 0.5 * abs(y[-1] - y[0]):
        a, b = gnum(lang, x[j]), gnum(lang, x[j + 1])
        return {"fr": f"{'croissante' if up else 'décroissante'} avec un seuil entre {a} et {b}",
                "en": f"{'increasing' if up else 'decreasing'} with a threshold between {a} and {b}",
                "ar": f"{'متزايدة' if up else 'متناقصة'} مع عتبة بين {a} و{b}"}[lang]
    return {"fr": f"{'croissante' if up else 'décroissante'} avec un plateau",
            "en": f"{'increasing' if up else 'decreasing'} with a plateau",
            "ar": f"{'متزايدة' if up else 'متناقصة'} ثم مستقرة"}[lang]


def ml_texts(site_ml):
    M = jsonable(site_ml)
    tests_a, tests_b = records(M["task_a"]["tests"]), records(M["task_b"]["tests"])

    def test(tests, model, ref, metric):
        return next(r for r in tests if r["modèle"] == model and r["référence"] == ref and r["métrique"] == metric)

    km_test = test(tests_a, "Cox", "KM", "ibs")
    cov_test = test(tests_b, "Cox time-varying", "Temps seul", "log_loss")
    verdicts = [("A", m, v) for m, v in M["task_a"]["verdicts"].items()] + \
               [("B", m, v) for m, v in M["task_b"]["verdicts"].items()]
    better = [(t, m) for t, m, v in verdicts if v["better"]]
    metrics_a = {r["model"]: r for r in M["task_a"]["metrics"]}
    noise = []
    for metric in ("uno_c", "ibs"):
        sd = float(np.mean([metrics_a[m][metric]["sd"] for m in ("Cox", "RSF", "GBSA")]))
        gap = max(abs(r["différence moyenne"]) for r in tests_a if r["référence"] == "Cox" and r["métrique"] == metric)
        noise.append((metric, sd, gap))
    lin = records(M["interpretation"]["linearity"])
    pdc = M["interpretation"]["partial_dependence"]
    out = {}
    for lang in LANGS:
        def model_task(t, m):
            return f"{MODEL_ML[m][lang]} {IN_TASK[lang].format(t=t)}"

        if better:
            q1 = {"fr": f"Selon les règles fixées en 3.4 et 4.4, {join(lang, [model_task(t, m) for t, m in better])} prédit "
                        "mieux que le modèle de Cox de sa tâche.",
                  "en": f"According to the rules set in 3.4 and 4.4, {join(lang, [model_task(t, m) for t, m in better])} "
                        "predicts better than the Cox model of its task.",
                  "ar": f"وفق القواعد المحدَّدة في القسمين 3.4 و4.4، يتفوّق {join(lang, [model_task(t, m) for t, m in better])} "
                        "في التنبؤ على نموذج كوكس الخاص بمهمته."}[lang]
        else:
            lst = COMMA[lang].join(model_task(t, m) for t, m, _ in verdicts)
            q1 = {"fr": f"Dans les deux cadres, aucun des {len(verdicts)} modèles comparés au modèle de Cox ({lst}) ne "
                        "prédit mieux que lui selon les règles fixées en 3.4 et 4.4 : **les modèles de Cox ne sont pas "
                        "surpassés**, que la survie soit prédite à partir de la situation à l'entrée au pouvoir ou année "
                        "par année.",
                  "en": f"In both settings, none of the {len(verdicts)} models compared with the Cox model ({lst}) predicts "
                        "better than it according to the rules set in 3.4 and 4.4: **the Cox models are not "
                        "outperformed**, whether survival is predicted from the situation at entry into power or year "
                        "by year.",
                  "ar": f"في الإطارين كليهما، لا يتفوّق أيٌّ من النماذج الـ{num(lang, len(verdicts))} المقارَنة بنموذج "
                        f"كوكس ({lst}) عليه في التنبؤ وفق القواعد المحدَّدة في القسمين 3.4 و4.4: **لم يتفوّق أيّ نموذج "
                        "على نماذج كوكس**، سواء تم التنبؤ بالبقاء انطلاقًا من الوضع عند الوصول إلى السلطة أو سنةً "
                        "بسنة."}[lang]
        improves_a = km_test["p corrigée"] < ALPHA and km_test["différence moyenne"] < 0
        improves_b = cov_test["p corrigée"] < ALPHA and cov_test["différence moyenne"] < 0
        da = iso(lang, raw(lang, km_test["différence moyenne"], 4) if km_test["différence moyenne"] < 0
                 else "+" + raw(lang, km_test["différence moyenne"], 4))
        db = iso(lang, raw(lang, cov_test["différence moyenne"], 4) if cov_test["différence moyenne"] < 0
                 else "+" + raw(lang, cov_test["différence moyenne"], 4))
        pa, pb = p_corrected(lang, km_test["p corrigée"]), p_corrected(lang, cov_test["p corrigée"])
        both = improves_a and improves_b
        covariates = {
            "fr": ("Les covariables apportent bien de l'information : " if both else "Apport des covariables : ")
                  + f"en tâche A, le modèle de Cox {'améliore' if improves_a else 'n’améliore pas'} significativement le "
                  f"score de Brier intégré par rapport à Kaplan-Meier (écart {da}, {pa}) ; en tâche B, le Cox "
                  f"time-varying {'améliore' if improves_b else 'n’améliore pas'} significativement la perte logarithmique "
                  f"par rapport à la durée seule (écart {db}, {pb}).",
            "en": ("The covariates do carry information: " if both else "What the covariates add: ")
                  + f"in task A, the Cox model {'significantly improves' if improves_a else 'does not significantly improve'} "
                  f"the integrated Brier score compared with Kaplan-Meier (difference {da}, {pa}); in task B, the "
                  f"time-varying Cox model {'significantly improves' if improves_b else 'does not significantly improve'} "
                  f"the log loss compared with duration alone (difference {db}, {pb}).",
            "ar": ("تحمل المتغيرات التفسيرية معلومات فعلية: " if both else "ما تضيفه المتغيرات التفسيرية: ")
                  + f"في المهمة A، {'يحسّن' if improves_a else 'لا يحسّن'} نموذج كوكس درجة براير المتكاملة تحسينًا ذا "
                  f"دلالة مقارنةً بكابلان-ماير (فارق {da}، {pa})؛ وفي المهمة B، "
                  f"{'يحسّن' if improves_b else 'لا يحسّن'} نموذج كوكس المتغير زمنيًا الخسارة اللوغاريتمية تحسينًا ذا "
                  f"دلالة مقارنةً بالمدة وحدها (فارق {db}، {pb}).",
        }[lang].replace("n’améliore", "n'améliore")
        q2_note = ({"fr": "Ces écarts n'améliorent toutefois pas la prédiction (question 1) : les modèles qui peuvent les "
                          "capter ne font pas mieux que le modèle de Cox, ce qui suggère qu'ils sont faibles ou mal estimés "
                          "avec ce nombre de chutes.",
                    "en": "These departures do not improve prediction, however (question 1): the models able to capture "
                          "them do no better than the Cox model, which suggests they are weak or poorly estimated with this "
                          "number of falls.",
                    "ar": "غير أن هذه الانحرافات لا تحسّن التنبؤ (السؤال 1): فالنماذج القادرة على التقاطها لا تتفوق على "
                          "نموذج كوكس، مما يوحي بأنها ضعيفة أو سيئة التقدير مع هذا العدد من حالات السقوط."}
                   if not better else
                   {"fr": "Au moins un modèle capable de capter ces écarts prédit mieux que le modèle de Cox (question 1) : "
                          "ils méritent d'être modélisés explicitement.",
                    "en": "At least one model able to capture these departures predicts better than the Cox model "
                          "(question 1): they deserve to be modelled explicitly.",
                    "ar": "يتفوّق نموذج واحد على الأقل من النماذج القادرة على التقاط هذه الانحرافات على نموذج كوكس في "
                          "التنبؤ (السؤال 1): ولذلك تستحق أن تُنمذَج صراحةً."})[lang]
        practical = ({"fr": "**Conclusion pratique.** Les modèles d'apprentissage automatique ne prédisent pas mieux que les "
                            "modèles de Cox, dans aucun des deux cadres. Nous conservons donc les modèles de Cox de "
                            "`final_panel.ipynb` pour le rapport (inférence : hazard ratios, intervalles de confiance, "
                            "tests) et le modèle de Cox statique corrigé (section 6.3 de `final_panel.ipynb`) pour "
                            "l'application web : à performance égale, il est interprétable et ses prédictions s'expliquent "
                            "par des effets estimés et testés.",
                      "en": "**Practical conclusion.** Machine-learning models do not predict better than the Cox models "
                            "in either setting. We therefore keep the Cox models of `final_panel.ipynb` for the report "
                            "(inference: hazard ratios, confidence intervals, tests) and the corrected static Cox model "
                            "(Section 6.3 of `final_panel.ipynb`) for the web application: with equal performance, it is "
                            "interpretable and its predictions are explained by estimated and tested effects.",
                      "ar": "**الخلاصة العملية.** لا تتفوّق نماذج تعلّم الآلة على نماذج كوكس في التنبؤ في أيٍّ من "
                            "الإطارين. لذلك نحتفظ بنماذج كوكس في `final_panel.ipynb` للتقرير (الاستدلال: نسب الخطر، "
                            "وفترات الثقة، والاختبارات)، وبنموذج كوكس الثابت المصحَّح (القسم 6.3 من "
                            "`final_panel.ipynb`) لتطبيق الويب: فهو، مع تساوي الأداء، قابل للتفسير، وتُفسَّر تنبؤاته "
                            "بآثار مقدَّرة ومختبَرة."}
                     if not better else
                     {"fr": "**Conclusion pratique.** Au moins un modèle d'apprentissage automatique prédit mieux que le "
                            "modèle de Cox selon les règles fixées : le choix du modèle de l'application web doit être "
                            "réexaminé.",
                      "en": "**Practical conclusion.** At least one machine-learning model predicts better than the Cox "
                            "model according to the rules set: the choice of the web application's model must be "
                            "reconsidered.",
                      "ar": "**الخلاصة العملية.** يتفوّق نموذج واحد على الأقل من نماذج تعلّم الآلة على نموذج كوكس وفق "
                            "القواعد المحدَّدة: يجب إعادة النظر في اختيار نموذج تطبيق الويب."})[lang]
        noise_lines = []
        for metric, sd, gap in noise:
            larger = sd > gap
            name = {"uno_c": {"fr": "le C-index d'Uno", "en": "Uno's C-index", "ar": "مؤشر التوافق لأونو"},
                    "ibs": {"fr": "le score de Brier intégré", "en": "the integrated Brier score",
                            "ar": "درجة براير المتكاملة"}}[metric][lang]
            noise_lines.append({
                "fr": f"Pour {name}, la dispersion entre plis (écart-type moyen {num(lang, sd, 3)}) est "
                      f"{'plus grande' if larger else 'plus petite'} que le plus grand écart moyen avec le modèle de Cox "
                      f"({num(lang, gap, 3)}).",
                "en": f"For {name}, the spread between folds (mean standard deviation {num(lang, sd, 3)}) is "
                      f"{'larger' if larger else 'smaller'} than the largest mean difference with the Cox model "
                      f"({num(lang, gap, 3)}).",
                "ar": f"بالنسبة إلى {name}، يكون التشتت بين الطيّات (متوسط الانحراف المعياري {num(lang, sd, 3)}) "
                      f"{'أكبر' if larger else 'أصغر'} من أكبر فارق متوسط مع نموذج كوكس ({num(lang, gap, 3)}).",
            }[lang])
        shapes = []
        for r in lin:
            if r["R² droite"] >= R2_LINEAR:
                shapes.append({"fr": "proche de linéaire", "en": "close to linear", "ar": "قريبة من الخطية"}[lang])
            else:
                c = pdc[r["variable"]]
                shapes.append(describe_shape(lang, c["x"], c["y"]))
        out[lang] = {"q1": q1, "covariates": covariates, "q2_note": q2_note, "practical": practical,
                     "noise": noise_lines, "linearity_shapes": shapes}
    return same_text_in_all_languages(out)


# ================================================================= 04_demographics
# Names of the country variables (docs/glossary.md), units of their hazard ratios and names of the blocks
DEMO_VARS = {
    "youth_share": {"fr": "part des 15-24 ans parmi les adultes", "en": "share of 15-24-year-olds among adults",
                    "ar": f"نسبة الشباب ({iso('ar', '15-24')} سنة) بين البالغين"},
    "old_share": {"fr": "part des 65 ans et plus", "en": "share of people aged 65 and over",
                  "ar": f"نسبة من بلغوا {iso('ar', '65')} سنة فأكثر"},
    "life_exp": {"fr": "espérance de vie à la naissance", "en": "life expectancy at birth",
                 "ar": "متوسط العمر المتوقع عند الولادة"},
    "school_enrol": {"fr": "scolarisation dans le secondaire", "en": "secondary school enrolment",
                     "ar": "الالتحاق بالتعليم الثانوي"},
    "urban_share": {"fr": "part de la population urbaine", "en": "urban population share", "ar": "نسبة سكان المدن"},
    "gini": {"fr": "inégalités de revenu (indice de Gini)", "en": "income inequality (Gini index)",
             "ar": "عدم المساواة في الدخل (مؤشر جيني)"},
    "v2stfisccap": {"fr": "capacité fiscale de l'État", "en": "state fiscal capacity", "ar": "القدرة الضريبية للدولة"},
    "v2clrspct": {"fr": "administration publique impartiale", "en": "impartial public administration",
                  "ar": "إدارة عامة محايدة"},
    "v2peedueq": {"fr": "égalité d'accès à l'éducation", "en": "equal access to education",
                  "ar": "المساواة في الوصول إلى التعليم"},
    "v2pehealth": {"fr": "égalité d'accès aux soins", "en": "equal access to health care",
                   "ar": "المساواة في الوصول إلى الرعاية الصحية"},
    "epr_excluded": {"fr": "population exclue du pouvoir (ethnicité)", "en": "population excluded from power (ethnicity)",
                     "ar": "السكان المُقصَون عن السلطة (الانتماء الإثني)"},
    "epr_groups": {"fr": "groupes ethniques politiquement pertinents", "en": "politically relevant ethnic groups",
                   "ar": "المجموعات الإثنية ذات الثقل السياسي"},
    "v2pepwrsoc": {"fr": "pouvoir réparti entre groupes sociaux", "en": "power distributed by social group",
                   "ar": "توزّع السلطة بين الفئات الاجتماعية"},
    "v2clrelig": {"fr": "liberté religieuse", "en": "freedom of religion", "ar": "الحرية الدينية"},
    "v2csrlgrep": {"fr": "absence de répression des organisations religieuses",
                   "en": "no repression of religious organisations", "ar": "غياب قمع المنظمات الدينية"},
    "unemployment": {"fr": "chômage", "en": "unemployment", "ar": "البطالة"},
    "youth_unemployment": {"fr": "chômage des 15-24 ans", "en": "youth unemployment (15-24)",
                           "ar": f"بطالة الشباب ({iso('ar', '15-24')} سنة)"},
    "unemployment_advanced": {"fr": "chômage des diplômés du supérieur", "en": "unemployment of university graduates",
                              "ar": "بطالة خريجي التعليم العالي"},
    "tertiary_enrol": {"fr": "scolarisation dans le supérieur", "en": "tertiary enrolment",
                       "ar": "الالتحاق بالتعليم العالي"},
    "bachelor_share": {"fr": "part de diplômés du supérieur (licence ou plus)",
                       "en": "share of university graduates (bachelor's or more)",
                       "ar": "نسبة حاملي الشهادات الجامعية (الإجازة فما فوق)"},
    "education_years": {"fr": "années moyennes d'études", "en": "average years of schooling",
                        "ar": "متوسط سنوات الدراسة"},
    "academic_freedom": {"fr": "liberté académique", "en": "academic freedom", "ar": "الحرية الأكاديمية"},
    "al_ethnic2000": {"fr": "fractionnalisation ethnique (vers 2000)", "en": "ethnic fractionalization (around 2000)",
                      "ar": f"التجزؤ الإثني (نحو عام {iso('ar', '2000')})"},
    "al_religion2000": {"fr": "fractionnalisation religieuse (vers 2000)", "en": "religious fractionalization (around 2000)",
                        "ar": f"التجزؤ الديني (نحو عام {iso('ar', '2000')})"},
}
DEMO_UNITS = {
    "+10 points": {"fr": "+10 points", "en": "+10 points", "ar": f"{iso('ar', '+10')} نقاط"},
    "+5 points": {"fr": "+5 points", "en": "+5 points", "ar": f"{iso('ar', '+5')} نقاط"},
    "+10 ans": {"fr": "+10 ans", "en": "+10 years", "ar": f"{iso('ar', '+10')} سنوات"},
    "+1 point V-Dem": {"fr": "+1 point V-Dem", "en": "+1 V-Dem point", "ar": f"{iso('ar', '+1')} نقطة على مقياس V-Dem"},
    "+10 points de population": {"fr": "+10 points de population", "en": "+10 percentage points of the population",
                                 "ar": f"{iso('ar', '+10')} نقاط مئوية من السكان"},
    "+1 groupe": {"fr": "+1 groupe", "en": "+1 group", "ar": f"{iso('ar', '+1')} مجموعة"},
    "+0.1": {"fr": "+0,1", "en": "+0.1", "ar": iso("ar", "+0.1")},
    "+1 année": {"fr": "+1 année", "en": "+1 year", "ar": f"{iso('ar', '+1')} سنة"},
}
DEMO_BLOCKS = {"A": {"fr": "Démographie et services publics", "en": "Demography and public services",
                     "ar": "الديموغرافيا والخدمات العامة"},
               "B": {"fr": "Ethnicité et religion", "en": "Ethnicity and religion", "ar": "الإثنية والدين"},
               "C": {"fr": "Emploi, éducation et liberté académique", "en": "Employment, education and academic freedom",
                     "ar": "العمل والتعليم والحرية الأكاديمية"}}
DEMO_VERDICT = {"meilleur que M0": {"fr": "mieux que le modèle existant", "en": "better than the existing model",
                                    "ar": "أفضل من النموذج القائم"},
                "moins bon que M0": {"fr": "moins bien que le modèle existant", "en": "worse than the existing model",
                                     "ar": "أسوأ من النموذج القائم"},
                "pas de différence nette": {"fr": "pas de différence nette", "en": "no clear difference",
                                            "ar": "لا فرق واضح"}}


def demo_link(lang, hr, p):
    """Plain-language reading of a hazard ratio: no clear link, lower or higher risk of falling."""
    if p >= ALPHA:
        return {"fr": "pas de lien net avec la durée", "en": "no clear link with duration",
                "ar": "لا علاقة واضحة بالمدة"}[lang]
    lower = hr < 1
    return {"fr": "risque de chute plus faible" if lower else "risque de chute plus élevé",
            "en": "lower risk of falling" if lower else "higher risk of falling",
            "ar": "خطر سقوط أقل" if lower else "خطر سقوط أعلى"}[lang]


def demo_texts(site_demo):
    D = jsonable(site_demo)
    dec = records(D["decision"])
    comb = {r["variable"]: r for r in records(D["models"]["combined"])}
    frac = {r["variable"]: r for r in records(D["models"]["fractionalization"])}
    desc = records(D["models"]["descriptive"])
    cov = {r["variable"]: r for r in records(D["coverage"])}
    cands = records(D["candidates"])
    tests_a = records(D["cv"]["task_a"]["tests"])
    metrics_a = {(r["comparison"], r["model"]): r for r in D["cv"]["task_a"]["metrics"]}
    blocks, kept, totals = D["blocks"], D["kept"], D["totals"]
    screening = D["screening"]
    untestable = list(screening["dropped"]) + list(screening["removed_for_sample"])
    active = [b for b in ("A", "B", "C") if blocks[b]["retained"]]
    min_epp = D["protocol"]["min_events_per_parameter"]

    def test_row(comp, model):
        return next(r for r in tests_a if r["comparaison"] == comp and r["modèle"] == model)

    out = {}
    for lang in LANGS:
        var = lambda v: DEMO_VARS[v][lang]  # noqa: E731
        unit = lambda v: DEMO_UNITS[comb[v]["unité"] if v in comb else next(  # noqa: E731
            r["unité du HR"] for r in cands if r["variable"] == v)][lang]

        # ---- answer
        n = len(dec)
        if kept:
            answer = {"fr": f"Selon les règles fixées avant les résultats, {count(lang, len(kept), 'variable')} sur "
                            f"{num(lang, n)} {'remplit' if len(kept) == 1 else 'remplissent'} les quatre conditions : "
                            f"{join(lang, [var(v) for v in kept])}.",
                      "en": f"According to the rules set before the results, {count(lang, len(kept), 'variable')} out of "
                            f"{num(lang, n)} {'meets' if len(kept) == 1 else 'meet'} the four conditions: "
                            f"{join(lang, [var(v) for v in kept])}.",
                      "ar": f"وفق القواعد المحدَّدة قبل النتائج، تستوفي الشروط الأربعة المتغيراتُ التالية: "
                            f"{join(lang, [var(v) for v in kept])}."}[lang]
        else:
            answer = {"fr": f"Selon les règles fixées avant les résultats, **aucune des {num(lang, n)} caractéristiques "
                            "des pays testées n'améliore le modèle existant** : aucune ne remplit les quatre conditions "
                            "(effet significatif après la correction de Holm, même sens dans les deux cadres, gain de "
                            "C-index en validation croisée et, pour les blocs B et C, effet qui résiste au contrôle de la "
                            "région ou du PIB par habitant).",
                      "en": f"According to the rules set before the results, **none of the {num(lang, n)} country "
                            "characteristics tested improves the existing model**: none meets the four conditions "
                            "(significant effect after the Holm correction, same direction in both settings, a C-index "
                            "gain in cross-validation and, for blocks B and C, an effect that survives the region or "
                            "GDP-per-capita control).",
                      "ar": f"وفق القواعد المحدَّدة قبل النتائج، **لا تُحسِّن أيٌّ من خصائص البلدان المختبَرة، وعددها "
                            f"{num(lang, n)}، النموذجَ القائم**: لا تستوفي أيٌّ منها الشروط الأربعة (أثر ذو دلالة بعد "
                            "تصحيح هولم، والاتجاه نفسه في الإطارين، وتحسُّن مؤشر التوافق في التحقق المتقاطع، وبالنسبة "
                            "إلى الكتلتين B وC، أثر يصمد عند ضبط المنطقة أو نصيب الفرد من الناتج المحلي الإجمالي)."}[lang]
        sig = [r for r in dec if r["p (A)"] < ALPHA]
        holm = [r for r in dec if r["1. Holm < 0,05"]]
        if sig:
            items = join(lang, [f"{var(r['variable'])} ({p_txt(lang, r['p (A)'])})" for r in sig])
            held = join(lang, [var(r["variable"]) for r in holm])
            after = ({"fr": f"après correction sur les {num(lang, n)} variables, aucune ne reste significative.",
                      "en": f"after correcting over the {num(lang, n)} variables, none remains significant.",
                      "ar": f"وبعد التصحيح على المتغيرات الـ{num(lang, n)}، لم يبقَ أيٌّ منها ذا دلالة."}[lang] if not holm else
                     {"fr": f"après correction, {'une seule reste significative' if len(holm) == 1 else 'restent significatives'} : "
                            f"{held}.",
                      "en": f"after correction, {'only one remains significant' if len(holm) == 1 else 'these remain significant'}: "
                            f"{held}.",
                      "ar": f"وبعد التصحيح، تبقى ذات دلالة: {held}."}[lang])
            answer += {"fr": f" Avant la correction pour comparaisons multiples, {count(lang, len(sig), 'variable')} "
                             f"{'avait' if len(sig) == 1 else 'avaient'} une p-value inférieure à 0,05 : {items} ; {after}",
                       "en": f" Before correcting for multiple comparisons, {count(lang, len(sig), 'variable')} had a p-value "
                             f"below 0.05: {items}; {after}",
                       "ar": f" قبل تصحيح المقارنات المتعددة، كانت قيمة p أقل من {iso(lang, '0.05')} لدى "
                             f"{count(lang, len(sig), 'variable')}: {items}؛ {after}"}[lang]

        # ---- variables that meet every condition but one
        regime_r = {r["index"]: r for r in records(D["regime_correlations"])}
        near_parts = []
        for r in dec:
            v, b = r["variable"], r["bloc"]
            failed = [i for i, ok in ((1, r["1. Holm < 0,05"]), (2, r["2. même sens"]), (3, r["3. C > M0"])) if not ok]
            failed += [4] if r["4. contrôle"] is False else []
            if v in kept or len(failed) != 1:
                continue
            n_cond = 4 if r["4. contrôle"] is not None else 3
            c = comb[v]
            region = b == "B"
            ctrl = {"fr": "de la région" if region else "du PIB par habitant",
                    "en": "for region" if region else "for GDP per capita",
                    "ar": "المنطقة" if region else "نصيب الفرد من الناتج المحلي الإجمالي"}[lang]
            hold = iso(lang, f"p = {raw(lang, r['p Holm'], 3)}")
            ctrl_hr = (f"{hr_txt(lang, c['contrôle A HR'])}{COMMA[lang]}{p_txt(lang, c['contrôle A p'])}"
                       if r["4. contrôle"] is not None else "")
            what = {
                1: {"fr": f"son effet ne reste pas significatif après la correction de Holm ({hold})",
                    "en": f"its effect does not remain significant after the Holm correction ({hold})",
                    "ar": f"لا يبقى أثره ذا دلالة بعد تصحيح هولم ({hold})"},
                2: {"fr": f"son effet change de sens entre les tâches A et B ({hr_txt(lang, r['HR (B)'])} en tâche B)",
                    "en": f"its effect changes direction between tasks A and B ({hr_txt(lang, r['HR (B)'])} in task B)",
                    "ar": f"يتغيّر اتجاه أثره بين المهمتين A وB ({hr_txt(lang, r['HR (B)'])} في المهمة B)"},
                3: {"fr": f"son ajout au modèle existant n'améliore pas nettement le C-index en validation croisée "
                          f"({signed(lang, r['écart C (A)'], 3)}, {p_corrected(lang, r['p corrigée C'])})",
                    "en": f"adding it to the existing model does not clearly improve the C-index in cross-validation "
                          f"({signed(lang, r['écart C (A)'], 3)}, {p_corrected(lang, r['p corrigée C'])})",
                    "ar": f"لا تُحسِّن إضافته إلى النموذج القائم مؤشرَ التوافق في التحقق المتقاطع تحسينًا واضحًا "
                          f"({signed(lang, r['écart C (A)'], 3)}، {p_corrected(lang, r['p corrigée C'])})"},
                4: {"fr": f"son effet ne résiste pas au contrôle {ctrl} ({ctrl_hr})",
                    "en": f"its effect does not survive the control {ctrl} ({ctrl_hr})",
                    "ar": f"لا يصمد أثره عند ضبط {ctrl} ({ctrl_hr})"},
            }[failed[0]][lang]
            # Only the conditions that are met are listed, in their order
            gain = f"{signed(lang, r['écart C (A)'], 3)}{COMMA[lang]}{p_corrected(lang, r['p corrigée C'])}"
            met = {
                1: {"fr": f"{hr_txt(lang, r['HR (A)'])} pour {unit(v)} en tâche A ({hold} après la correction de Holm)",
                    "en": f"{hr_txt(lang, r['HR (A)'])} per {unit(v)} in task A ({hold} after the Holm correction)",
                    "ar": f"{hr_txt(lang, r['HR (A)'])} لكل {unit(v)} في المهمة A ({hold} بعد تصحيح هولم)"},
                2: {"fr": f"le même sens en tâche B ({hr_txt(lang, r['HR (B)'])})",
                    "en": f"the same direction in task B ({hr_txt(lang, r['HR (B)'])})",
                    "ar": f"الاتجاه نفسه في المهمة B ({hr_txt(lang, r['HR (B)'])})"},
                3: {"fr": f"un gain de C-index en validation croisée ({gain})",
                    "en": f"a C-index gain in cross-validation ({gain})",
                    "ar": f"تحسُّن مؤشر التوافق في التحقق المتقاطع ({gain})"},
                4: {"fr": f"l'effet résiste au contrôle {ctrl} ({ctrl_hr})",
                    "en": f"the effect survives the control {ctrl} ({ctrl_hr})",
                    "ar": f"يصمد الأثر عند ضبط {ctrl} ({ctrl_hr})"},
            }
            items = [met[k][lang] for k in range(1, n_cond + 1) if k not in failed]
            if lang == "ar":
                listed = items[0] + "".join(f"، و{x}" for x in items[1:])
            else:
                word = {"fr": "et", "en": "and"}[lang]
                listed = ", ".join(items[:-1]) + (", " if len(items) > 2 else " ") + f"{word} {items[-1]}"
            regime = ""
            if v in regime_r:
                rr = num(lang, regime_r[v]["polity2_entry"], 2)
                regime = {"fr": f" ; cet indicateur décrit aussi le comportement du régime (corrélation de {rr} avec le "
                                "score Polity2 à l'entrée)",
                          "en": f"; this indicator also describes the regime's own behaviour (correlation of {rr} with "
                                "the Polity2 score at entry)",
                          "ar": f"؛ ويصف هذا المؤشر أيضًا سلوك النظام نفسه (ارتباط قدره {rr} بمؤشر Polity2 عند الوصول "
                                "إلى السلطة)"}[lang]
            higher = r["HR (A)"] > 1
            near_parts.append({
                "fr": f"**Presque retenue : {var(v)}.** Elle remplit {num(lang, n_cond - 1)} des {num(lang, n_cond)} "
                      f"conditions : {listed}. Mais {what}. Plus sa valeur est élevée, plus le risque de chute est "
                      f"{'élevé' if higher else 'faible'}, à valeurs égales des facteurs du modèle existant, dont le score "
                      f"Polity2{regime}. C'est une association, pas un effet.",
                "en": f"**Almost kept: {var(v)}.** It meets {num(lang, n_cond - 1)} of the {num(lang, n_cond)} conditions: "
                      f"{listed}. But {what}. The higher its value, the {'higher' if higher else 'lower'} the risk of "
                      f"falling, other factors of the existing model being equal, including the Polity2 score{regime}. It "
                      f"is an association, not an effect.",
                "ar": f"**متغير كاد يُحتفَظ به: {var(v)}.** يستوفي {num(lang, n_cond - 1)} من أصل {num(lang, n_cond)} شروط: "
                      f"{listed}. لكن {what}. وكلما ارتفعت قيمته {'ارتفع' if higher else 'انخفض'} خطر السقوط، مع تساوي "
                      f"عوامل النموذج القائم، ومنها مؤشر Polity2{regime}. إنها علاقة ارتباط لا أثر سببي.",
            }[lang])
        near_txt = " ".join(near_parts) if near_parts else {
            "fr": "Aucune variable ne remplit toutes les conditions sauf une.",
            "en": "No variable meets all the conditions but one.",
            "ar": "لا يوجد متغير يستوفي كل الشروط إلا شرطًا واحدًا."}[lang]

        # ---- one paragraph per block
        block_lines = []
        for b in active:
            m1, m2, m3 = blocks[b]["models"]
            comp = f"bloc {b}"
            s = D["samples"][b]
            c0 = metrics_a[(comp, "M0")]["harrell_c"]["mean"]
            t1, t3 = test_row(comp, m1), test_row(comp, m3)
            c1, c3 = metrics_a[(comp, m1)]["harrell_c"]["mean"], metrics_a[(comp, m3)]["harrell_c"]["mean"]
            best = max((r for r in tests_a if r["comparaison"] == comp and r["modèle"].startswith(m2 + "·")),
                       key=lambda r: r["C de Harrell : écart"])
            bv = best["modèle"].split("·")[1]
            sample = join(lang, [count(lang, s["spells"], "party"), count(lang, s["events"], "fall")])
            d1 = f"{signed(lang, t1['C de Harrell : écart'], 3)}{COMMA[lang]}{p_corrected(lang, t1['C de Harrell : p corrigée'])}"
            db = f"{signed(lang, best['C de Harrell : écart'], 3)} ({p_corrected(lang, best['C de Harrell : p corrigée'])})"
            one = len(blocks[b]["retained"]) == 1
            name = DEMO_BLOCKS[b][lang]
            block_lines.append({
                "fr": f"**{name}** — {sample} en tâche A. Sur ces partis, le modèle existant atteint un C-index de "
                      f"{num(lang, c0, 3)}. Les variables du bloc seules obtiennent {num(lang, c1, 3)} (écart {d1}) : "
                      f"{DEMO_VERDICT[t1['verdict']][lang]}. Mélangées au modèle existant, avec un poids moyen de "
                      f"{num(lang, t3['poids moyen du bloc'], 2)} pour le bloc, elles obtiennent {num(lang, c3, 3)} : "
                      f"{DEMO_VERDICT[t3['verdict']][lang]}. "
                      + (f"Seule variable testée : {var(bv)}, qui change le C-index de {db}." if one else
                         f"Meilleur ajout au modèle existant : {var(bv)}, qui change le C-index de {db}."),
                "en": f"**{name}** — {sample} in task A. On these parties, the existing model reaches a C-index of "
                      f"{num(lang, c0, 3)}. The block's variables alone reach {num(lang, c1, 3)} (difference {d1}): "
                      f"{DEMO_VERDICT[t1['verdict']][lang]}. Blended with the existing model, with an average weight of "
                      f"{num(lang, t3['poids moyen du bloc'], 2)} for the block, they reach {num(lang, c3, 3)}: "
                      f"{DEMO_VERDICT[t3['verdict']][lang]}. "
                      + (f"Only variable tested: {var(bv)}, which changes the C-index by {db}." if one else
                         f"Best addition to the existing model: {var(bv)}, which changes the C-index by {db}."),
                "ar": f"**{name}** — {sample} في المهمة A. على هذه الأحزاب، يبلغ مؤشر التوافق للنموذج القائم "
                      f"{num(lang, c0, 3)}. وتبلغ متغيرات الكتلة وحدها {num(lang, c1, 3)} (فارق {d1}): "
                      f"{DEMO_VERDICT[t1['verdict']][lang]}. وعند مزجها بالنموذج القائم، بوزن متوسط قدره "
                      f"{num(lang, t3['poids moyen du bloc'], 2)} للكتلة، تبلغ {num(lang, c3, 3)}: "
                      f"{DEMO_VERDICT[t3['verdict']][lang]}. "
                      + (f"المتغير الوحيد المختبَر: {var(bv)}؛ يتغيّر معه مؤشر التوافق بمقدار {db}." if one else
                         f"أفضل إضافة إلى النموذج القائم: {var(bv)}؛ يتغيّر معها مؤشر التوافق بمقدار {db}."),
            }[lang])

        # ---- comparison with the fractionalization indexes
        comparison = ""
        if "epr_excluded" in comb and {"al_ethnic2000", "al_religion2000"} <= set(frac):
            e, fe, fr_ = comb["epr_excluded"], frac["al_ethnic2000"], frac["al_religion2000"]
            comparison = {
                "fr": f"**Pour comparaison** (hors règles), la part de la population exclue du pouvoir (EPR) a un "
                      f"{hr_txt(lang, e['A HR'], e['A p'])} pour 10 points de population ({demo_link(lang, e['A HR'], e['A p'])}), "
                      f"et la fractionnalisation ethnique d'Alesina et al. (2003) un {hr_txt(lang, fe['HR (A)'], fe['p (A)'])} "
                      f"pour 0,1 ({demo_link(lang, fe['HR (A)'], fe['p (A)'])}).",
                "en": f"**For comparison** (outside the rules), the share of the population excluded from power (EPR) has "
                      f"{hr_txt(lang, e['A HR'], e['A p'])} per 10 points of population ({demo_link(lang, e['A HR'], e['A p'])}), "
                      f"and the ethnic fractionalization of Alesina et al. (2003) {hr_txt(lang, fe['HR (A)'], fe['p (A)'])} "
                      f"per 0.1 ({demo_link(lang, fe['HR (A)'], fe['p (A)'])}).",
                "ar": f"**للمقارنة** (خارج القواعد)، لنسبة السكان المُقصَين عن السلطة (EPR) {hr_txt(lang, e['A HR'], e['A p'])} "
                      f"لكل {iso(lang, '10')} نقاط من السكان ({demo_link(lang, e['A HR'], e['A p'])})، وللتجزؤ الإثني "
                      f"لدى أليسينا وآخرين (2003) {hr_txt(lang, fe['HR (A)'], fe['p (A)'])} لكل {iso(lang, '0.1')} "
                      f"({demo_link(lang, fe['HR (A)'], fe['p (A)'])}).",
            }[lang]
            if e["A p"] >= ALPHA and fe["p (A)"] >= ALPHA:
                comparison += {"fr": " Ni la mesure politique de l'exclusion ni la mesure démographique de la diversité "
                                     "ethnique ne sont liées de façon nette à la durée des partis.",
                               "en": " Neither the political measure of exclusion nor the demographic measure of ethnic "
                                     "diversity is clearly linked to how long parties last.",
                               "ar": " لا يرتبط المقياس السياسي للإقصاء ولا المقياس الديموغرافي للتنوع الإثني ارتباطًا "
                                     "واضحًا بمدة بقاء الأحزاب."}[lang]
            comparison += {"fr": f" La fractionnalisation religieuse a un {hr_txt(lang, fr_['HR (A)'], fr_['p (A)'])} pour 0,1",
                           "en": f" Religious fractionalization has {hr_txt(lang, fr_['HR (A)'], fr_['p (A)'])} per 0.1",
                           "ar": f" وللتجزؤ الديني {hr_txt(lang, fr_['HR (A)'], fr_['p (A)'])} لكل {iso(lang, '0.1')}"}[lang]
            if fr_["p (A)"] < ALPHA:
                within = fr_["p (A, région)"] < ALPHA
                comparison += {
                    "fr": f" : les partis de pays plus divers sur le plan religieux ont en moyenne un "
                          f"{demo_link(lang, fr_['HR (A)'], fr_['p (A)'])} ; avec les indicateurs de région "
                          f"({hr_txt(lang, fr_['HR (A, région)'])}{COMMA[lang]}{p_txt(lang, fr_['p (A, région)'])}), le lien "
                          + ("subsiste à l'intérieur des régions" if within else "ne survit pas au contrôle régional")
                          + ". C'est une association, pas un effet",
                    "en": f": parties in countries with more religious diversity have, on average, a "
                          f"{demo_link(lang, fr_['HR (A)'], fr_['p (A)'])}; with region indicators "
                          f"({hr_txt(lang, fr_['HR (A, région)'])}{COMMA[lang]}{p_txt(lang, fr_['p (A, région)'])}), the link "
                          + ("holds within regions" if within else "does not survive the region control")
                          + ". It is an association, not an effect",
                    "ar": f": فللأحزاب في البلدان الأكثر تنوعًا دينيًا، في المتوسط، {demo_link(lang, fr_['HR (A)'], fr_['p (A)'])}؛ "
                          f"ومع مؤشرات المنطقة ({hr_txt(lang, fr_['HR (A, région)'])}{COMMA[lang]}{p_txt(lang, fr_['p (A, région)'])})، "
                          + ("تبقى العلاقة قائمة داخل المناطق" if within else "لا تصمد العلاقة عند ضبط المنطقة")
                          + ". إنها علاقة ارتباط لا أثر سببي",
                }[lang]
            comparison += {"fr": ". Ces indices, mesurés vers 2000, après le début de la plupart des périodes au pouvoir, "
                                 "peuvent refléter l'action des régimes eux-mêmes : ils ne servent que de comparaison.",
                           "en": ". These indexes, measured around 2000, after most periods in power had begun, may "
                                 "reflect what the regimes themselves did: they serve only as a comparison.",
                           "ar": ". قيست هذه المؤشرات نحو عام 2000، بعد بدء معظم فترات الحكم، وقد تعكس ما فعلته الأنظمة "
                                 "نفسها: لذلك لا تُستعمَل إلا للمقارنة."}[lang]

        # ---- variables that cannot be tested
        untestable_txt = ""
        if untestable:
            rows = {r["variable"]: r for r in desc}
            with_m0 = [v for v in untestable if rows[v]["HR (A, M0 + variable)"] is not None]

            untestable_txt = {
                "fr": f"**Variables non testables.** {cap(count(lang, len(untestable), 'variable'))} n'ont pas assez de "
                      f"données pour les règles : {join(lang, [var(v) for v in untestable])}. Le tableau donne, à titre "
                      "descriptif, leur hazard ratio dans un modèle réduit (la variable, le PIB par habitant et le score "
                      "Polity2 de l'année précédente), estimé sur les années où elles existent.",
                "en": f"**Untestable variables.** {cap(count(lang, len(untestable), 'variable'))} lack the data needed for "
                      f"the rules: {join(lang, [var(v) for v in untestable])}. For description only, the table gives their "
                      "hazard ratio in a reduced model (the variable, GDP per capita and the Polity2 score of the previous "
                      "year), fitted on the years where they exist.",
                "ar": f"**متغيرات لا يمكن اختبارها.** لا تتوفر لـ{count(lang, len(untestable), 'variable')} بيانات كافية "
                      f"لتطبيق القواعد: {join(lang, [var(v) for v in untestable])}. على سبيل الوصف فقط، يعطي الجدول نسبة "
                      "الخطر لكلٍّ منها في نموذج مختزل (المتغير، ونصيب الفرد من الناتج المحلي الإجمالي، ومؤشر Polity2 "
                      "للسنة السابقة)، مقدَّر على السنوات التي يتوفر فيها.",
            }[lang]
            for v in with_m0:
                r = rows[v]
                untestable_txt += {
                    "fr": f" Avec le modèle existant en tâche A : {var(v)}, "
                          f"{hr_txt(lang, r['HR (A, M0 + variable)'], r['p (A, M0 + variable)'])} pour {unit(v)} "
                          f"({demo_link(lang, r['HR (A, M0 + variable)'], r['p (A, M0 + variable)'])}).",
                    "en": f" With the existing model in task A: {var(v)}, "
                          f"{hr_txt(lang, r['HR (A, M0 + variable)'], r['p (A, M0 + variable)'])} per {unit(v)} "
                          f"({demo_link(lang, r['HR (A, M0 + variable)'], r['p (A, M0 + variable)'])}).",
                    "ar": f" ومع النموذج القائم في المهمة A: {var(v)}، "
                          f"{hr_txt(lang, r['HR (A, M0 + variable)'], r['p (A, M0 + variable)'])} لكل {unit(v)} "
                          f"({demo_link(lang, r['HR (A, M0 + variable)'], r['p (A, M0 + variable)'])}).",
                }[lang]
            untestable_txt += {"fr": " Ces estimations portent sur des échantillons plus petits, souvent plus récents : "
                                     "elles ne sont comparables ni au modèle existant ni entre elles, et ne comptent pas "
                                     "dans la décision.",
                               "en": " These estimates rest on smaller, often more recent samples: they are comparable "
                                     "neither with the existing model nor with one another, and do not count in the "
                                     "decision.",
                               "ar": " تقوم هذه التقديرات على عينات أصغر وأحدث في الغالب: فهي لا تُقارَن بالنموذج القائم "
                                     "ولا ببعضها، ولا تدخل في القرار."}[lang]

        # ---- limits
        unemp, educ = cov.get("unemployment"), cov.get("education_years")
        lost = totals["events"] - D["samples"]["A"]["events"] if "A" in D["samples"] else 0
        limits = []
        if unemp and educ:
            limits.append({
                "fr": f"**Chômage et éducation : peu de données.** Les taux de chômage harmonisés (estimations du BIT) "
                      f"commencent en 1991 et ne couvrent que {count(lang, unemp['A : chutes'], 'fall')} en tâche A et "
                      f"{num(lang, unemp['B : chutes'])} en tâche B ; les années moyennes d'études (Clio-Infra), "
                      "interpolées entre des observations espacées, s'arrêtent en 2010 ; les diplômes du supérieur sont "
                      "rarement mesurés pour ces régimes. Le nombre d'« intellectuels » n'est donc mesuré "
                      "qu'indirectement.",
                "en": f"**Unemployment and education: little data.** Harmonised unemployment rates (ILO estimates) start "
                      f"in 1991 and cover only {count(lang, unemp['A : chutes'], 'fall')} in task A and "
                      f"{num(lang, unemp['B : chutes'])} in task B; average years of schooling (Clio-Infra), interpolated "
                      "between distant observations, stop in 2010; university degrees are rarely measured for these "
                      "regimes. The number of \"intellectuals\" is therefore measured only indirectly.",
                "ar": f"**البطالة والتعليم: بيانات قليلة.** تبدأ معدلات البطالة الموحَّدة (تقديرات منظمة العمل الدولية) "
                      f"عام 1991، ولا تغطي إلا {count(lang, unemp['A : chutes'], 'fall')} في المهمة A و"
                      f"{num(lang, unemp['B : chutes'])} في المهمة B؛ ويتوقف متوسط سنوات الدراسة (Clio-Infra)، المستكمَل "
                      "بالاستيفاء بين ملاحظات متباعدة، عند عام 2010؛ ونادرًا ما تُقاس الشهادات الجامعية في هذه الأنظمة. "
                      "لذلك لا يُقاس عدد «المثقفين» إلا بصورة غير مباشرة.",
            }[lang])
        limits.append({
            "fr": f"**Couverture avant 1960.** Les séries des Nations unies et de la Banque mondiale commencent en 1950 et "
                  f"1960 : le bloc A perd {num(lang, lost)} des {count(lang, totals['events'], 'fall')}, surtout parmi les "
                  "partis arrivés au pouvoir dans les années 1940 et 1950. Chaque bloc est donc comparé au modèle "
                  "existant réestimé sur ses propres partis.",
            "en": f"**Coverage before 1960.** The United Nations and World Bank series start in 1950 and 1960: block A "
                  f"loses {num(lang, lost)} of the {count(lang, totals['events'], 'fall')}, mostly among parties that came "
                  "to power in the 1940s and 1950s. Each block is therefore compared with the existing model refitted on "
                  "its own parties.",
            "ar": f"**التغطية قبل عام 1960.** تبدأ سلاسل الأمم المتحدة والبنك الدولي عامي 1950 و1960: تفقد الكتلة A "
                  f"{num(lang, lost)} من أصل {count(lang, totals['events'], 'fall')}، معظمها بين الأحزاب التي وصلت إلى "
                  "السلطة في الأربعينيات والخمسينيات. لذلك تُقارَن كل كتلة بالنموذج القائم بعد إعادة تقديره على أحزابها.",
        }[lang])
        limits.append({
            "fr": "**Des indicateurs qui décrivent aussi le régime.** La liberté religieuse, la répression des "
                  "organisations religieuses, la répartition du pouvoir entre groupes sociaux et la liberté académique "
                  "dépendent en partie des choix du régime : un lien avec sa durée ne dirait pas si la société ou le "
                  "régime en est à l'origine.",
            "en": "**Indicators that also describe the regime.** Freedom of religion, the repression of religious "
                  "organisations, the distribution of power between social groups and academic freedom depend partly "
                  "on the regime's own choices: a link with its duration would not tell whether society or the regime "
                  "drives it.",
            "ar": "**مؤشرات تصف النظام أيضًا.** تتوقف الحرية الدينية وقمع المنظمات الدينية وتوزّع السلطة بين الفئات "
                  "الاجتماعية والحرية الأكاديمية جزئيًا على خيارات النظام نفسه: فالعلاقة بمدة بقائه لا تبيّن هل المجتمع "
                  "أم النظام هو مصدرها.",
        }[lang])
        limits.append({
            "fr": "**Fractionnalisation mesurée après coup.** Les indices d'Alesina et al. (2003) datent d'environ 2000, "
                  "après le début de la plupart des périodes au pouvoir ; ils peuvent refléter l'action des régimes "
                  "eux-mêmes (exodes, expulsions, violences de masse).",
            "en": "**Fractionalization measured afterwards.** The indexes of Alesina et al. (2003) date from around 2000, "
                  "after most periods in power had begun; they may reflect what the regimes themselves did (exoduses, "
                  "expulsions, mass violence).",
            "ar": "**تجزؤ مقيس بعد الأحداث.** تعود مؤشرات أليسينا وآخرين (2003) إلى نحو عام 2000، أي بعد بدء معظم فترات "
                  "الحكم؛ وقد تعكس ما فعلته الأنظمة نفسها (موجات نزوح، وعمليات طرد، وعنف جماعي).",
        }[lang])
        limits.append({
            "fr": f"**Peu de chutes.** Les modèles combinés restent juste au-dessus de {num(lang, min_epp)} chutes par "
                  "paramètre : un effet modeste peut passer inaperçu, et l'absence de gain ne prouve pas l'absence de "
                  "tout lien.",
            "en": f"**Few falls.** The combined models stay just above {num(lang, min_epp)} falls per parameter: a modest "
                  "effect can go unnoticed, and the absence of a gain does not prove the absence of any link.",
            "ar": f"**قلة حالات السقوط.** تبقى النماذج المركّبة فوق {num(lang, min_epp)} حالات سقوط لكل معلَمة بقليل: قد "
                  "يمرّ أثر متواضع دون أن يُلاحَظ، وغياب التحسّن لا يثبت غياب أي علاقة.",
        }[lang])

        recommendation = ({
            "fr": "**Conséquence pour le simulateur.** Aucune variable n'étant retenue, le modèle du simulateur ne change "
                  "pas. Ces caractéristiques décrivent des pays, pas des choix d'un parti : elles ne deviendraient de "
                  "toute façon pas des réglages du jeu.",
            "en": "**What this means for the simulator.** Since no variable is kept, the simulator's model does not "
                  "change. These characteristics describe countries, not choices made by a party: they would not "
                  "become settings of the game in any case.",
            "ar": "**ما يعنيه ذلك للمحاكي.** بما أنه لم يُحتفَظ بأي متغير، لا يتغيّر نموذج المحاكي. تصف هذه الخصائص "
                  "البلدانَ لا خيارات الحزب: ولن تصبح في أي حال من إعدادات اللعبة.",
        } if not kept else {
            "fr": "**Conséquence pour le simulateur.** Les variables retenues décrivent des pays, pas des choix d'un "
                  "parti : elles ne deviennent pas des réglages du jeu, et les intégrer au modèle du simulateur "
                  "demanderait de réexaminer le modèle exporté et ses tests.",
            "en": "**What this means for the simulator.** The variables kept describe countries, not choices made by a "
                  "party: they do not become settings of the game, and adding them to the simulator's model would "
                  "require reviewing the exported model and its tests.",
            "ar": "**ما يعنيه ذلك للمحاكي.** تصف المتغيرات المحتفَظ بها البلدانَ لا خيارات الحزب: فهي لا تصبح من "
                  "إعدادات اللعبة، وإدراجها في نموذج المحاكي يتطلب مراجعة النموذج المصدَّر واختباراته.",
        })[lang]

        out[lang] = {
            "answer": answer, "near": near_txt, "blocks": block_lines, "comparison": comparison, "untestable": untestable_txt,
            "limits": limits, "recommendation": recommendation,
            "labels": [var(r["variable"]) for r in cands],
            "units": [DEMO_UNITS[r["unité du HR"]][lang] for r in cands],
            "block_names": [DEMO_BLOCKS[b][lang] for b in ("A", "B", "C")],
        }
    return same_text_in_all_languages(out)


# ================================================================= 05_shocks
# Names of the shocks (docs/glossary.md): heading of a chart row, name inside a sentence
SHOCK_VARS = {
    "disaster_deaths": {"fr": ("Catastrophes naturelles soudaines", "une catastrophe naturelle soudaine"),
                        "en": ("Sudden-onset natural disasters", "a sudden-onset natural disaster"),
                        "ar": ("الكوارث الطبيعية المفاجئة", "كارثة طبيعية مفاجئة")},
    "quake": {"fr": ("Grand séisme", "un grand séisme"), "en": ("Major earthquake", "a major earthquake"),
              "ar": ("زلزال كبير", "زلزال كبير")},
    "battle_deaths": {"fr": ("Morts au combat", "des morts au combat"), "en": ("Battle deaths", "battle deaths"),
                      "ar": ("قتلى المعارك", "قتلى المعارك")},
    "interstate_war": {"fr": ("Guerre entre États", "une guerre avec un autre État"),
                       "en": ("War between states", "a war with another state"),
                       "ar": ("حرب بين الدول", "حرب مع دولة أخرى")},
    "famine": {"fr": ("Famine", "une famine"), "en": ("Famine", "a famine"), "ar": ("مجاعة", "مجاعة")},
    "food_drop": {"fr": ("Choc alimentaire", "une chute de la production alimentaire"),
                  "en": ("Food production shock", "a fall in food production"),
                  "ar": ("صدمة غذائية", "تراجع الإنتاج الغذائي")},
    "recession": {"fr": ("Récession sévère", "une récession sévère"), "en": ("Severe recession", "a severe recession"),
                  "ar": ("ركود حاد", "ركود حاد")},
}
# Exact definitions, with their source
SHOCK_DEFS = {
    "disaster_deaths": {"fr": "morts des séismes, volcans, glissements de terrain, tempêtes, températures extrêmes, "
                              "inondations et feux, pour 1 million d'habitants (EM-DAT)",
                        "en": "deaths in earthquakes, volcanic eruptions, landslides, storms, extreme temperatures, "
                              "floods and wildfires, per million people (EM-DAT)",
                        "ar": "ضحايا الزلازل والبراكين والانهيارات الأرضية والعواصف ودرجات الحرارة القصوى والفيضانات "
                              "والحرائق، لكل مليون نسمة (EM-DAT)"},
    "quake": {"fr": "séisme de magnitude 7,5 ou plus dans le pays (NOAA)",
              "en": "earthquake of magnitude 7.5 or more in the country (NOAA)",
              "ar": f"زلزال بقوة {iso('ar', '7.5')} درجة أو أكثر في البلد (NOAA)"},
    "battle_deaths": {"fr": "morts au combat des conflits armés situés dans le pays, pour 1 million d'habitants "
                            "(PRIO, UCDP)",
                      "en": "battle deaths in armed conflicts located in the country, per million people (PRIO, UCDP)",
                      "ar": "قتلى المعارك في النزاعات المسلحة الواقعة في البلد، لكل مليون نسمة (PRIO وUCDP)"},
    "interstate_war": {"fr": "le pays est l'un des deux camps d'un conflit armé entre États, avec au moins 25 morts au "
                             "combat dans l'année (UCDP/PRIO)",
                       "en": "the country is one of the two sides of an armed conflict between states, with at least "
                             "25 battle deaths in the year (UCDP/PRIO)",
                       "ar": f"البلد أحد طرفَي نزاع مسلح بين الدول، مع {iso('ar', '25')} قتيلًا على الأقل في المعارك "
                             "خلال السنة (UCDP/PRIO)"},
    "famine": {"fr": "famine d'au moins 100 000 morts en cours dans le pays (World Peace Foundation)",
               "en": "famine killing at least 100,000 people under way in the country (World Peace Foundation)",
               "ar": f"مجاعة جارية في البلد أودت بحياة {iso('ar', '100,000')} شخص على الأقل (World Peace Foundation)"},
    "food_drop": {"fr": "baisse d'au moins 10 % en un an de la production alimentaire par habitant (FAOSTAT)",
                  "en": "fall of at least 10% in one year in food production per person (FAOSTAT)",
                  "ar": f"انخفاض الإنتاج الغذائي للفرد بنسبة {iso('ar', '10%')} على الأقل خلال سنة (FAOSTAT)"},
    "recession": {"fr": "baisse d'au moins 5 % en un an du PIB par habitant (Maddison)",
                  "en": "fall of at least 5% in one year in GDP per capita (Maddison)",
                  "ar": f"انخفاض نصيب الفرد من الناتج المحلي الإجمالي بنسبة {iso('ar', '5%')} على الأقل خلال سنة "
                        "(Maddison)"},
}
# Unit of a hazard ratio: (table heading, phrase after the hazard ratio in a sentence)
SHOCK_UNITS = {"×10": {"fr": ("morts par million ×10", "pour 10 fois plus de morts par million d'habitants"),
                       "en": ("deaths per million ×10", "for ten times as many deaths per million people"),
                       "ar": (f"قتلى لكل مليون {iso('ar', '×10')}", "عند تضاعف عدد القتلى لكل مليون نسمة عشر مرات")},
               "choc": {"fr": ("année qui suit un choc", "l'année qui suit le choc"),
                        "en": ("year after a shock", "in the year after the shock"),
                        "ar": ("سنة تلي الصدمة", "في السنة التي تلي الصدمة")}}


def shocks_texts(site_shocks):
    D = jsonable(site_shocks)
    dec = records(D["decision"])
    cands = records(D["candidates"])
    cov = {r["variable"]: r for r in records(D["coverage"])}
    desc = {r["variable"]: r for r in records(D["models"]["descriptive"])}
    test = {r["modèle"]: r for r in records(D["cv"]["task_b"]["tests"]) if r["comparaison"] == "chocs"}
    auc = {r["model"]: r["roc_auc"]["mean"] for r in D["cv"]["task_b"]["metrics"] if r["comparison"] == "chocs"}
    kept, screening, sample, splice = D["kept"], D["screening"], D["sample"], D["splice"]
    protocol = D["protocol"]
    min_epp, min_falls = protocol["min_events_per_parameter"], protocol["min_falls"]
    untestable = list(screening["dropped"]) + list(screening["removed_for_sample"])
    unit_of = {r["variable"]: r["unité du HR"] for r in cands}

    out = {}
    for lang in LANGS:
        head = lambda v: SHOCK_VARS[v][lang][0]  # noqa: E731
        name = lambda v: SHOCK_VARS[v][lang][1]  # noqa: E731
        per = lambda v: SHOCK_UNITS[unit_of[v]][lang][1]  # noqa: E731
        low = lambda v: head(v) if lang == "ar" else head(v).lower()  # noqa: E731
        n = len(dec)

        # ---- answer
        if kept:
            answer = {"fr": f"Selon les règles fixées avant les résultats, {count(lang, len(kept), 'variable')} sur "
                            f"{num(lang, n)} {'remplit' if len(kept) == 1 else 'remplissent'} les trois conditions : "
                            f"{join(lang, [head(v).lower() for v in kept])}.",
                      "en": f"According to the rules set before the results, {count(lang, len(kept), 'variable')} out of "
                            f"{num(lang, n)} {'meets' if len(kept) == 1 else 'meet'} the three conditions: "
                            f"{join(lang, [head(v).lower() for v in kept])}.",
                      "ar": f"وفق القواعد المحدَّدة قبل النتائج، تستوفي الشروط الثلاثة الصدماتُ التالية: "
                            f"{join(lang, [head(v) for v in kept])}."}[lang]
        else:
            answer = {"fr": f"Selon les règles fixées avant les résultats, **aucun des {num(lang, n)} chocs testés ne "
                            "change de façon mesurable le risque qu'un parti perde le pouvoir l'année suivante** : "
                            "aucun ne remplit les trois conditions (effet significatif après la correction de Holm, "
                            "gain de ROC-AUC en validation croisée, effet qui résiste au contrôle de l'époque).",
                      "en": f"According to the rules set before the results, **none of the {num(lang, n)} shocks tested "
                            "measurably changes the risk that a party loses power the following year**: none meets "
                            "the three conditions (significant effect after the Holm correction, a ROC-AUC gain in "
                            "cross-validation, an effect that survives the period control).",
                      "ar": f"وفق القواعد المحدَّدة قبل النتائج، **لا تغيّر أيٌّ من الصدمات المختبَرة، وعددها "
                            f"{num(lang, n)}، خطرَ فقدان الحزب للسلطة في السنة التالية تغييرًا قابلًا للقياس**: لا "
                            "تستوفي أيٌّ منها الشروط الثلاثة (أثر ذو دلالة بعد تصحيح هولم، وتحسُّن ROC-AUC في التحقق "
                            "المتقاطع، وأثر يصمد عند ضبط الحقبة الزمنية)."}[lang]
        sig = [r for r in dec if r["p"] < ALPHA]
        holm = [r for r in dec if r["1. Holm < 0,05"]]
        if sig:
            items = join(lang, [f"{head(r['variable']).lower() if lang != 'ar' else head(r['variable'])} "
                                f"({hr_txt(lang, r['HR'], r['p'])})" for r in sig])
            held = join(lang, [head(r["variable"]).lower() if lang != "ar" else head(r["variable"]) for r in holm])
            after = ({"fr": "après la correction de Holm, aucun ne reste significatif.",
                      "en": "after the Holm correction, none remains significant.",
                      "ar": "وبعد تصحيح هولم، لم يبقَ أيٌّ منها ذا دلالة."}[lang] if not holm else
                     {"fr": f"après la correction de Holm, {'seul reste significatif' if len(holm) == 1 else 'restent significatifs'} : {held}.",
                      "en": f"after the Holm correction, {'only this one remains' if len(holm) == 1 else 'these remain'} significant: {held}.",
                      "ar": f"وبعد تصحيح هولم، يبقى ذا دلالة: {held}."}[lang])
            answer += {"fr": f" Avant la correction pour comparaisons multiples, {count(lang, len(sig), 'variable')} "
                             f"{'avait' if len(sig) == 1 else 'avaient'} une p-value inférieure à 0,05 : {items} ; {after}",
                       "en": f" Before correcting for multiple comparisons, {count(lang, len(sig), 'variable')} had a "
                             f"p-value below 0.05: {items}; {after}",
                       "ar": f" قبل تصحيح المقارنات المتعددة، كانت قيمة p أقل من {iso(lang, '0.05')} لدى "
                             f"{count(lang, len(sig), 'variable')}: {items}؛ {after}"}[lang]
        elif not kept:
            c = min(dec, key=lambda r: r["p"])
            ci = iso(lang, f"{raw(lang, c['IC bas'], 2)}–{raw(lang, c['IC haut'], 2)}")
            answer += {"fr": f" Aucun n'a de p-value inférieure à 0,05, même avant correction. Le plus proche du seuil : "
                             f"{low(c['variable'])}, {hr_txt(lang, c['HR'], c['p'])} {per(c['variable'])} "
                             f"(intervalle de confiance à 95 % : {ci}).",
                       "en": f" None has a p-value below 0.05, even before correction. Closest to the threshold: "
                             f"{low(c['variable'])}, {hr_txt(lang, c['HR'], c['p'])} {per(c['variable'])} "
                             f"(95% confidence interval: {ci}).",
                       "ar": f" لا تقلّ قيمة p عن {iso(lang, '0.05')} لدى أيٍّ من الصدمات، حتى قبل التصحيح. الأقرب إلى "
                             f"العتبة: {low(c['variable'])}، {hr_txt(lang, c['HR'], c['p'])} {per(c['variable'])} "
                             f"(فترة الثقة {iso(lang, '95%')}: {ci})."}[lang]

        # ---- shocks that meet every condition but one
        near_parts = []
        for r in dec:
            v = r["variable"]
            ok = {1: r["1. Holm < 0,05"], 2: r["2. ROC-AUC > M0"], 3: r["3. époque"]}
            failed = [k for k, x in ok.items() if not x]
            if v in kept or len(failed) != 1:
                continue
            hold = iso(lang, f"p = {raw(lang, r['p Holm'], 3)}")
            gain = f"{signed(lang, r['écart ROC-AUC'], 3)}{COMMA[lang]}{p_corrected(lang, r['p corrigée ROC-AUC'])}"
            period = f"{hr_txt(lang, r['HR (époque)'])}{COMMA[lang]}{p_txt(lang, r['p (époque)'])}"
            met = {1: {"fr": f"{hr_txt(lang, r['HR'])} {per(v)}, {hold} après la correction de Holm",
                       "en": f"{hr_txt(lang, r['HR'])} {per(v)}, {hold} after the Holm correction",
                       "ar": f"{hr_txt(lang, r['HR'])} {per(v)}، و{hold} بعد تصحيح هولم"},
                   2: {"fr": f"un gain de ROC-AUC en validation croisée ({gain})",
                       "en": f"a ROC-AUC gain in cross-validation ({gain})",
                       "ar": f"تحسُّن ROC-AUC في التحقق المتقاطع ({gain})"},
                   3: {"fr": f"un effet qui résiste au contrôle de l'époque ({period})",
                       "en": f"an effect that survives the period control ({period})",
                       "ar": f"أثر يصمد عند ضبط الحقبة الزمنية ({period})"}}
            what = {1: {"fr": f"son effet ({hr_txt(lang, r['HR'], r['p'])} avant correction) ne reste pas significatif "
                              f"après la correction de Holm ({hold})",
                        "en": f"its effect ({hr_txt(lang, r['HR'], r['p'])} before correction) does not remain "
                              f"significant after the Holm correction ({hold})",
                        "ar": f"لا يبقى أثره ({hr_txt(lang, r['HR'], r['p'])} قبل التصحيح) ذا دلالة بعد تصحيح هولم ({hold})"},
                    2: {"fr": f"il n'améliore pas nettement la ROC-AUC en validation croisée ({gain})",
                        "en": f"it does not clearly improve the ROC-AUC in cross-validation ({gain})",
                        "ar": f"لا يحسّن ROC-AUC في التحقق المتقاطع تحسينًا واضحًا ({gain})"},
                    3: {"fr": f"son effet ne résiste pas au contrôle de l'époque ({period})",
                        "en": f"its effect does not survive the period control ({period})",
                        "ar": f"لا يصمد أثره عند ضبط الحقبة الزمنية ({period})"}}[failed[0]][lang]
            parts = join(lang, [met[k][lang] for k in (1, 2, 3) if ok[k]])
            higher = r["HR"] > 1
            near_parts.append({
                "fr": f"**Presque retenu : {head(v).lower()}.** Il remplit deux des trois conditions : {parts}. Mais "
                      f"{what}. Après {name(v)}, le risque de chute est {'plus élevé' if higher else 'plus faible'} "
                      "l'année suivante, à valeurs égales des facteurs du modèle existant : c'est une association, pas "
                      "un effet.",
                "en": f"**Almost kept: {head(v).lower()}.** It meets two of the three conditions: {parts}. But {what}. "
                      f"After {name(v)}, the risk of falling is {'higher' if higher else 'lower'} the following year, "
                      "other factors of the existing model being equal: it is an association, not an effect.",
                "ar": f"**صدمة كاد يُحتفَظ بها: {head(v)}.** تستوفي شرطين من الشروط الثلاثة: {parts}. لكن {what}. "
                      f"بعد {name(v)} يكون خطر السقوط {'أعلى' if higher else 'أقل'} في السنة التالية، مع تساوي عوامل "
                      "النموذج القائم: إنها علاقة ارتباط لا أثر سببي.",
            }[lang])
        near_txt = " ".join(near_parts) if near_parts else {
            "fr": "Aucun choc ne remplit toutes les conditions sauf une.",
            "en": "No shock meets all the conditions but one.",
            "ar": "لا توجد صدمة تستوفي كل الشروط إلا شرطًا واحدًا."}[lang]

        # ---- prediction
        t1, t3 = test["K1"], test["K3"]
        best = max((r for r in dec), key=lambda r: r["écart ROC-AUC"])
        obs = join(lang, [count(lang, sample["rows_tv"], "obs"), count(lang, sample["events_tv"], "fall")])
        d1 = f"{signed(lang, t1['ROC-AUC : écart'], 3)}{COMMA[lang]}{p_corrected(lang, t1['ROC-AUC : p corrigée'])}"
        db = f"{signed(lang, best['écart ROC-AUC'], 3)} ({p_corrected(lang, best['p corrigée ROC-AUC'])})"
        w = num(lang, t3["poids moyen des chocs"], 2)
        prediction = {
            "fr": f"**Prédiction.** Sur l'échantillon commun ({obs}), le modèle existant atteint une ROC-AUC de "
                  f"{num(lang, auc['M0'], 3)}. Les chocs seuls obtiennent {num(lang, auc['K1'], 3)} (écart {d1}) : "
                  f"{DEMO_VERDICT[t1['verdict']][lang]}. Mélangés au modèle existant, avec un poids moyen de {w} pour "
                  f"les chocs, ils obtiennent {num(lang, auc['K3'], 3)} : {DEMO_VERDICT[t3['verdict']][lang]}. Meilleur "
                  f"ajout au modèle existant : {head(best['variable']).lower()}, qui change la ROC-AUC de {db}.",
            "en": f"**Prediction.** On the common sample ({obs}), the existing model reaches a ROC-AUC of "
                  f"{num(lang, auc['M0'], 3)}. The shocks alone reach {num(lang, auc['K1'], 3)} (difference {d1}): "
                  f"{DEMO_VERDICT[t1['verdict']][lang]}. Blended with the existing model, with an average weight of {w} "
                  f"for the shocks, they reach {num(lang, auc['K3'], 3)}: {DEMO_VERDICT[t3['verdict']][lang]}. Best "
                  f"addition to the existing model: {head(best['variable']).lower()}, which changes the ROC-AUC by {db}.",
            "ar": f"**التنبؤ.** على العينة المشتركة ({obs})، يبلغ ROC-AUC للنموذج القائم {num(lang, auc['M0'], 3)}. "
                  f"وتبلغ الصدمات وحدها {num(lang, auc['K1'], 3)} (فارق {d1}): {DEMO_VERDICT[t1['verdict']][lang]}. "
                  f"وعند مزجها بالنموذج القائم، بوزن متوسط قدره {w} للصدمات، تبلغ {num(lang, auc['K3'], 3)}: "
                  f"{DEMO_VERDICT[t3['verdict']][lang]}. أفضل إضافة إلى النموذج القائم: {head(best['variable'])}؛ "
                  f"يتغيّر معها ROC-AUC بمقدار {db}.",
        }[lang]

        # ---- shocks that cannot be tested
        untestable_parts = []
        for v in untestable:
            c = cov[v]
            if v == "battle_deaths" and not splice["spliced"]:
                r_ = num(lang, splice["correlation_log"], 2)
                why = {"fr": f"les deux sources (PRIO jusqu'en 1988, UCDP ensuite) ne concordent pas assez sur leurs "
                             f"années communes, 1989-2008 (corrélation de {r_} conflit par conflit, pour un seuil fixé à "
                             f"0,8 avant les résultats) ; limitée à UCDP, la série commence en 1989 et ne couvre que "
                             f"{count(lang, c['chutes'], 'fall')}, pour un minimum de {num(lang, min_falls)}",
                       "en": f"the two sources (PRIO up to 1988, UCDP afterwards) do not agree enough over their common "
                             f"years, 1989-2008 (correlation of {r_} conflict by conflict, for a threshold set at 0.8 "
                             f"before the results); limited to UCDP, the series starts in 1989 and covers only "
                             f"{count(lang, c['chutes'], 'fall')}, for a minimum of {num(lang, min_falls)}",
                       "ar": f"لا يتوافق المصدران (PRIO حتى عام 1988 وUCDP بعده) بما يكفي في سنواتهما المشتركة "
                             f"{iso(lang, '1989-2008')} (ارتباط قدره {r_} نزاعًا بنزاع، والعتبة المحدَّدة قبل النتائج "
                             f"{iso(lang, '0.8')})؛ وباقتصارها على UCDP تبدأ السلسلة عام 1989 ولا تغطي إلا "
                             f"{count(lang, c['chutes'], 'fall')}، والحد الأدنى {num(lang, min_falls)}"}[lang]
            elif v in screening["dropped"]:
                why = {"fr": f"la série ne couvre que {count(lang, c['chutes'], 'fall')}, pour un minimum de "
                             f"{num(lang, min_falls)}",
                       "en": f"the series covers only {count(lang, c['chutes'], 'fall')}, for a minimum of "
                             f"{num(lang, min_falls)}",
                       "ar": f"لا تغطي السلسلة إلا {count(lang, c['chutes'], 'fall')}، والحد الأدنى {num(lang, min_falls)}"}[lang]
            else:
                info = screening["removed_for_sample"][v]
                epp_ = num(lang, info["events_per_parameter"], 1)
                fao = {"fr": " (FAOSTAT ne publie ces indices que pour les pays actuels, depuis leur création)",
                       "en": " (FAOSTAT publishes these indexes only for today's countries, since their creation)",
                       "ar": " (لا تنشر FAOSTAT هذه المؤشرات إلا للبلدان الحالية، منذ نشأتها)"}[lang] if v == "food_drop" else ""
                why = {"fr": f"la série manque pour trop de parti-années{fao} : l'ajouter réduirait l'échantillon commun à "
                             f"{count(lang, info['falls'], 'fall')}, soit {epp_} chutes par paramètre pour un minimum de "
                             f"{num(lang, min_epp)}",
                       "en": f"the series is missing for too many party-years{fao}: adding it would reduce the common "
                             f"sample to {count(lang, info['falls'], 'fall')}, that is {epp_} falls per parameter for a "
                             f"minimum of {num(lang, min_epp)}",
                       "ar": f"تنقص السلسلة في عدد كبير من المشاهدات{fao}: وإضافتها تقلّص العينة المشتركة إلى "
                             f"{count(lang, info['falls'], 'fall')}، أي {epp_} حالة سقوط لكل معلَمة، والحد الأدنى "
                             f"{num(lang, min_epp)}"}[lang]
            extra, described = "", False
            dr = desc.get(v, {})
            for key, where in (("M0 + variable", {"fr": "avec le modèle existant, sur les années où la série existe",
                                                  "en": "with the existing model, on the years where the series exists",
                                                  "ar": "مع النموذج القائم، على السنوات التي تتوفر فيها السلسلة"}),
                               ("réduit", {"fr": "dans un modèle réduit (le choc, le PIB par habitant et le score Polity2 "
                                                 "de l'année précédente)",
                                           "en": "in a reduced model (the shock, GDP per capita and the Polity2 score "
                                                 "of the previous year)",
                                           "ar": "في نموذج مختزل (الصدمة، ونصيب الفرد من الناتج المحلي الإجمالي، "
                                                 "ومؤشر Polity2 للسنة السابقة)"})):
                if dr.get(f"HR ({key})") is None:
                    continue
                hr_, p_ = dr[f"HR ({key})"], dr[f"p ({key})"]
                described = True
                extra += {"fr": f" À titre descriptif, {where['fr']} : {hr_txt(lang, hr_, p_)} {per(v)} "
                                f"({demo_link(lang, hr_, p_)}).",
                          "en": f" For description only, {where['en']}: {hr_txt(lang, hr_, p_)} {per(v)} "
                                f"({demo_link(lang, hr_, p_)}).",
                          "ar": f" على سبيل الوصف فقط، {where['ar']}: {hr_txt(lang, hr_, p_)} {per(v)} "
                                f"({demo_link(lang, hr_, p_)})."}[lang]
                break
            untestable_parts.append((f"**{head(v)}** : {why}.{extra}" if lang == "fr" else f"**{head(v)}**: {why}.{extra}",
                                     described))
        untestable_txt = ""
        if untestable_parts:
            untestable_txt = {"fr": "**Chocs non testables.** ", "en": "**Shocks that cannot be tested.** ",
                              "ar": "**صدمات لا يمكن اختبارها.** "}[lang] + " ".join(p for p, _ in untestable_parts)
            if any(d for _, d in untestable_parts):
                untestable_txt += {"fr": " Ces estimations descriptives ne comptent pas dans la décision.",
                                   "en": " These descriptive estimates do not count in the decision.",
                                   "ar": " لا تدخل هذه التقديرات الوصفية في القرار."}[lang]

        # ---- limits
        rare = [v for v in (r["variable"] for r in dec) if cov[v]["parti-années avec choc"] < 100]
        rare_txt = join(lang, [f"{low(v)} ({count(lang, cov[v]['parti-années avec choc'], 'obs')})" for v in rare])
        limits = [
            {"fr": "**Causalité inverse.** Une famine, une guerre ou une récession peut venir du régime lui-même, ou de "
                   "la crise qui le fait tomber ; le décalage d'un an ne l'exclut pas. Seul le grand séisme est un choc "
                   "vraiment extérieur au régime.",
             "en": "**Reverse causation.** A famine, a war or a recession can be caused by the regime itself, or by the "
                   "crisis that brings it down; the one-year lag does not rule this out. Only the major earthquake is "
                   "a shock truly external to the regime.",
             "ar": "**السببية العكسية.** قد تنتج المجاعة أو الحرب أو الركود عن النظام نفسه، أو عن الأزمة التي تُسقطه؛ "
                   "ولا يستبعد فارق السنة ذلك. والزلزال الكبير وحده صدمة خارجية حقًّا عن النظام."},
            {"fr": "**Recensement inégal.** Les catastrophes sont moins bien recensées avant 2000 et dans les régimes "
                   "fermés ; le contrôle de l'époque ne corrige qu'une tendance commune à tous les pays.",
             "en": "**Uneven recording.** Disasters are less well recorded before 2000 and in closed regimes; the period "
                   "control only corrects a trend shared by all countries.",
             "ar": "**تسجيل غير متكافئ.** تُسجَّل الكوارث بصورة أقل اكتمالًا قبل عام 2000 وفي الأنظمة المغلقة؛ ولا يصحّح "
                   "ضبط الحقبة الزمنية إلا اتجاهًا مشتركًا بين جميع البلدان."},
            {"fr": "**Chutes de la même année.** Un choc qui renverse un régime dans l'année même (une invasion, comme en "
                   "Irak en 2003) n'est pas vu : chaque chute est reliée aux chocs de l'année précédente.",
             "en": "**Falls in the same year.** A shock that topples a regime within the same year (an invasion, as in "
                   "Iraq in 2003) is not seen: each fall is linked to the shocks of the previous year.",
             "ar": "**السقوط في السنة نفسها.** لا تُرصَد الصدمة التي تُسقط نظامًا في السنة ذاتها (غزو، كما في العراق "
                   "عام 2003): فكل حالة سقوط تُربَط بصدمات السنة السابقة."},
            {"fr": f"**Peu d'événements.** Certains chocs sont rares{' : ' + rare_txt if rare else ''}. Leurs effets "
                   "sont estimés avec une grande imprécision, et l'absence d'effet net ne prouve pas l'absence de tout "
                   "lien.",
             "en": f"**Few events.** Some shocks are rare{': ' + rare_txt if rare else ''}. Their effects are estimated "
                   "with great uncertainty, and the absence of a clear effect does not prove the absence of any link.",
             "ar": f"**قلة الأحداث.** بعض الصدمات نادرة{': ' + rare_txt if rare else ''}. تُقدَّر آثارها بقدر كبير من "
                   "عدم الدقة، وغياب أثر واضح لا يثبت غياب أي علاقة."},
            {"fr": "**Attribution des événements.** Un événement compte pour l'État qui existait à sa date ; les "
                   "territoires dépendants ne comptent pour aucun parti.",
             "en": "**Attribution of events.** An event counts for the state that existed at its date; dependent "
                   "territories count for no party.",
             "ar": "**نسبة الأحداث.** يُحتسَب الحدث للدولة التي كانت قائمة في تاريخه؛ ولا تُحتسَب الأقاليم التابعة لأي حزب."},
        ]
        limits = [x[lang] for x in limits]

        recommendation = ({
            "fr": "**Conséquence pour le simulateur.** Aucun choc n'étant retenu, le modèle du simulateur ne change pas. "
                  "Les chocs décrivent ce qui arrive au pays, pas des choix d'un parti : ils ne deviendraient de toute "
                  "façon pas des réglages du jeu.",
            "en": "**What this means for the simulator.** Since no shock is kept, the simulator's model does not change. "
                  "Shocks describe what happens to a country, not choices made by a party: they would not become "
                  "settings of the game in any case.",
            "ar": "**ما يعنيه ذلك للمحاكي.** بما أنه لم يُحتفَظ بأي صدمة، لا يتغيّر نموذج المحاكي. تصف الصدمات ما يصيب "
                  "البلد لا خيارات الحزب: ولن تصبح في أي حال من إعدادات اللعبة.",
        } if not kept else {
            "fr": "**Conséquence pour le simulateur.** Les chocs retenus décrivent ce qui arrive au pays, pas des choix "
                  "d'un parti : ils ne deviennent pas des réglages du jeu, et le modèle du simulateur ne change pas.",
            "en": "**What this means for the simulator.** The shocks kept describe what happens to a country, not "
                  "choices made by a party: they do not become settings of the game, and the simulator's model does "
                  "not change.",
            "ar": "**ما يعنيه ذلك للمحاكي.** تصف الصدمات المحتفَظ بها ما يصيب البلد لا خيارات الحزب: فهي لا تصبح من "
                  "إعدادات اللعبة، ولا يتغيّر نموذج المحاكي.",
        })[lang]

        out[lang] = {
            "answer": answer, "near": near_txt, "prediction": prediction, "untestable": untestable_txt,
            "limits": limits, "recommendation": recommendation,
            "labels": [head(r["variable"]) for r in cands],
            "definitions": [SHOCK_DEFS[r["variable"]][lang] for r in cands],
            "units": [SHOCK_UNITS[r["unité du HR"]][lang][0] for r in cands],
        }
    return same_text_in_all_languages(out)


# ================================================================= 06_party_leaders
# Names of the characteristics (docs/glossary.md): heading of a chart row, name inside a sentence
LEADER_VARS = {
    "party_age": {"fr": ("Âge du parti à son arrivée au pouvoir", "l'âge du parti à son arrivée au pouvoir"),
                  "en": ("Party's age at entry into power", "the party's age at entry into power"),
                  "ar": ("عمر الحزب عند وصوله إلى السلطة", "عمر الحزب عند وصوله إلى السلطة")},
    "leader_age": {"fr": ("Âge du dirigeant", "l'âge du dirigeant"), "en": ("Leader's age", "the leader's age"),
                   "ar": ("عمر القائد", "عمر القائد")},
    "leader_irregular": {"fr": ("Arrivée irrégulière du dirigeant", "l'arrivée irrégulière du dirigeant au pouvoir"),
                         "en": ("Leader's irregular entry", "the leader's irregular entry into power"),
                         "ar": ("وصول القائد إلى السلطة بطريقة غير نظامية", "وصول القائد إلى السلطة بطريقة غير نظامية")},
    "leader_military": {"fr": ("Service militaire du dirigeant", "le service militaire du dirigeant"),
                        "en": ("Leader's military service", "the leader's military service"),
                        "ar": ("الخدمة العسكرية للقائد", "الخدمة العسكرية للقائد")},
    "leader_rebel": {"fr": ("Passé rebelle du dirigeant", "le passé du dirigeant dans un groupe rebelle"),
                     "en": ("Leader's rebel past", "the leader's past in a rebel group"),
                     "ar": ("ماضي القائد في جماعة متمردة", "ماضي القائد في جماعة متمردة")},
    "leader_university": {"fr": ("Études universitaires du dirigeant", "les études universitaires du dirigeant"),
                          "en": ("Leader's university education", "the leader's university education"),
                          "ar": ("التعليم الجامعي للقائد", "التعليم الجامعي للقائد")},
    "leader_experience": {"fr": ("Expérience politique du dirigeant", "l'expérience politique du dirigeant"),
                          "en": ("Leader's political experience", "the leader's political experience"),
                          "ar": ("الخبرة السياسية للقائد", "الخبرة السياسية للقائد")},
}
# Exact definitions, with their source
LEADER_DEFS = {
    "party_age": {"fr": "années écoulées entre la fondation du parti et son arrivée au pouvoir ; la même valeur chaque "
                        "année en tâche B (ARPD)",
                  "en": "years between the party's founding and its arrival in power; the same value every year in "
                        "task B (ARPD)",
                  "ar": "عدد السنوات بين تأسيس الحزب ووصوله إلى السلطة؛ القيمة نفسها كل سنة في المهمة B (ARPD)"},
    "leader_age": {"fr": "âge du dirigeant effectif l'année d'entrée au pouvoir (tâche A) ou l'année précédente "
                         "(tâche B) (Archigos)",
                   "en": "age of the effective leader in the year of entry into power (task A) or in the previous year "
                         "(task B) (Archigos)",
                   "ar": "عمر القائد الفعلي في سنة الوصول إلى السلطة (المهمة A) أو في السنة السابقة (المهمة B) (Archigos)"},
    "leader_irregular": {"fr": "le dirigeant est arrivé au pouvoir de façon irrégulière : coup d'État, révolte, "
                               "assassinat… (Archigos)",
                         "en": "the leader came to power irregularly: coup, revolt, assassination… (Archigos)",
                         "ar": "وصل القائد إلى السلطة بطريقة غير نظامية: انقلاب أو تمرّد أو اغتيال… (Archigos)"},
    "leader_military": {"fr": "le dirigeant a fait un service militaire avant d'arriver au pouvoir (LEAD)",
                        "en": "the leader served in the military before taking power (LEAD)",
                        "ar": "أدّى القائد خدمة عسكرية قبل وصوله إلى السلطة (LEAD)"},
    "leader_rebel": {"fr": "le dirigeant a appartenu à un groupe rebelle avant d'arriver au pouvoir (LEAD)",
                     "en": "the leader belonged to a rebel group before taking power (LEAD)",
                     "ar": "انتمى القائد إلى جماعة متمردة قبل وصوله إلى السلطة (LEAD)"},
    "leader_university": {"fr": "le dirigeant a fait des études à l'université ou au-delà (LEAD)",
                          "en": "the leader studied at university or beyond (LEAD)",
                          "ar": "تلقّى القائد تعليمًا جامعيًا أو أعلى (LEAD)"},
    "leader_experience": {"fr": "années d'expérience politique du dirigeant avant son arrivée au pouvoir (LEAD)",
                          "en": "years of political experience of the leader before taking power (LEAD)",
                          "ar": "سنوات الخبرة السياسية للقائد قبل وصوله إلى السلطة (LEAD)"},
}
# Unit of a hazard ratio: (table heading, phrase after the hazard ratio in a sentence)
LEADER_UNITS = {"10 ans de plus": {"fr": ("10 ans de plus", "pour 10 ans de plus"),
                                   "en": ("10 more years", "for 10 more years"),
                                   "ar": (f"{iso('ar', '10')} سنوات إضافية", f"لكل {iso('ar', '10')} سنوات إضافية")},
                "oui plutôt que non": {"fr": ("oui plutôt que non", "pour « oui » plutôt que « non »"),
                                       "en": ("yes rather than no", "for “yes” rather than “no”"),
                                       "ar": ("نعم بدلًا من لا", "عند «نعم» بدلًا من «لا»")}}


def leaders_texts(site_leaders):
    D = jsonable(site_leaders)
    dec = records(D["decision"])
    cands = records(D["candidates"])
    cov = {r["variable"]: r for r in records(D["coverage"])}
    comp = "partis et dirigeants"
    test_a = {r["modèle"]: r for r in records(D["cv"]["task_a"]["tests"]) if r["comparaison"] == comp}
    test_b = {r["modèle"]: r for r in records(D["cv"]["task_b"]["tests"]) if r["comparaison"] == comp}
    c_idx = {r["model"]: r["harrell_c"]["mean"] for r in D["cv"]["task_a"]["metrics"] if r["comparison"] == comp}
    auc = {r["model"]: r["roc_auc"]["mean"] for r in D["cv"]["task_b"]["metrics"] if r["comparison"] == comp}
    kept, screening, sample, links, protocol = D["kept"], D["screening"], D["sample"], D["links"], D["protocol"]
    rules = {r["leader_rule"]: r for r in records(D["task_b_leader_rules"])}
    after = rules.get("après 2015", {"parti-années": 0, "chutes": 0})
    last = protocol["archigos_last_year"]
    largest = protocol["largest_model_parameters"]
    min_falls, min_epp = protocol["min_falls"], protocol["min_events_per_parameter"]
    untestable = list(screening["dropped"]) + list(screening["removed_for_sample"])
    unit_of = {r["variable"]: r["unité du HR"] for r in cands}

    out = {}
    for lang in LANGS:
        head = lambda v: LEADER_VARS[v][lang][0]  # noqa: E731
        name = lambda v: LEADER_VARS[v][lang][1]  # noqa: E731
        per = lambda v: LEADER_UNITS[unit_of[v]][lang][1]  # noqa: E731
        year = lambda y: iso(lang, str(y))  # noqa: E731
        n = len(dec)

        # ---- answer
        if kept:
            answer = {"fr": f"Selon les règles fixées avant les résultats, {count(lang, len(kept), 'variable')} sur "
                            f"{num(lang, n)} {'remplit' if len(kept) == 1 else 'remplissent'} les quatre conditions : "
                            f"{join(lang, [name(v) for v in kept])}.",
                      "en": f"According to the rules set before the results, {count(lang, len(kept), 'variable')} out of "
                            f"{num(lang, n)} {'meets' if len(kept) == 1 else 'meet'} the four conditions: "
                            f"{join(lang, [name(v) for v in kept])}.",
                      "ar": f"وفق القواعد المحدَّدة قبل النتائج، تستوفي الشروط الأربعة المتغيراتُ التالية: "
                            f"{join(lang, [name(v) for v in kept])}."}[lang]
        else:
            answer = {"fr": f"Selon les règles fixées avant les résultats, **aucune des {num(lang, n)} caractéristiques du "
                            "parti et de son dirigeant testées n'apporte d'information au-delà du modèle existant** : "
                            "aucune ne remplit les quatre conditions (effet significatif en tâche A après la correction "
                            "de Holm, même sens en tâche B, gain de C-index en validation croisée, effet qui survit aux "
                            "contrôles de l'époque et du PIB).",
                      "en": f"According to the rules set before the results, **none of the {num(lang, n)} characteristics "
                            "of the party and its leader tested adds information beyond the existing model**: none "
                            "meets the four conditions (significant effect in task A after the Holm correction, same "
                            "direction in task B, a C-index gain in cross-validation, an effect that survives the period "
                            "and GDP controls).",
                      "ar": f"وفق القواعد المحدَّدة قبل النتائج، **لا تضيف أيٌّ من خصائص الحزب وقائده المختبَرة، وعددها "
                            f"{num(lang, n)}، معلوماتٍ تتجاوز النموذج القائم**: لا تستوفي أيٌّ منها الشروط الأربعة (أثر "
                            "ذو دلالة في المهمة A بعد تصحيح هولم، والاتجاه نفسه في المهمة B، وتحسُّن مؤشر التوافق في "
                            "التحقق المتقاطع، وأثر يصمد عند ضبط الحقبة الزمنية والناتج المحلي)."}[lang]
        sig = [r for r in dec if r["p (A)"] < ALPHA]
        holm = [r for r in dec if r["1. Holm < 0,05"]]
        if sig:
            items = join(lang, [f"{name(r['variable'])} ({hr_txt(lang, r['HR (A)'], r['p (A)'])})" for r in sig])
            held = join(lang, [name(r["variable"]) for r in holm])
            after_holm = ({"fr": "après la correction de Holm, aucune ne reste significative.",
                           "en": "after the Holm correction, none remains significant.",
                           "ar": "وبعد تصحيح هولم، لم يبقَ أيٌّ منها ذا دلالة."}[lang] if not holm else
                          {"fr": f"après la correction de Holm, {'reste significative' if len(holm) == 1 else 'restent significatives'} : {held}.",
                           "en": f"after the Holm correction, {'only this one remains' if len(holm) == 1 else 'these remain'} significant: {held}.",
                           "ar": f"وبعد تصحيح هولم، يبقى ذا دلالة: {held}."}[lang])
            answer += {"fr": f" Avant la correction pour comparaisons multiples, {count(lang, len(sig), 'variable')} "
                             f"{'avait' if len(sig) == 1 else 'avaient'} en tâche A une p-value inférieure à 0,05 : "
                             f"{items} ; {after_holm}",
                       "en": f" Before correcting for multiple comparisons, {count(lang, len(sig), 'variable')} had a "
                             f"p-value below 0.05 in task A: {items}; {after_holm}",
                       "ar": f" قبل تصحيح المقارنات المتعددة، كانت قيمة p في المهمة A أقل من {iso(lang, '0.05')} لدى "
                             f"{count(lang, len(sig), 'variable')}: {items}؛ {after_holm}"}[lang]
        elif not kept:
            c = min(dec, key=lambda r: r["p (A)"])
            ci = iso(lang, f"{raw(lang, c['IC bas (A)'], 2)}–{raw(lang, c['IC haut (A)'], 2)}")
            v = c["variable"]
            answer += {"fr": f" Aucune n'a de p-value inférieure à 0,05, même avant correction. La plus proche du seuil : "
                             f"{name(v)}, {hr_txt(lang, c['HR (A)'], c['p (A)'])} {per(v)} en tâche A (intervalle de "
                             f"confiance à 95 % : {ci}) et {hr_txt(lang, c['HR (B)'], c['p (B)'])} en tâche B.",
                       "en": f" None has a p-value below 0.05, even before correction. Closest to the threshold: "
                             f"{name(v)}, {hr_txt(lang, c['HR (A)'], c['p (A)'])} {per(v)} in task A (95% confidence "
                             f"interval: {ci}) and {hr_txt(lang, c['HR (B)'], c['p (B)'])} in task B.",
                       "ar": f" لا تقلّ قيمة p عن {iso(lang, '0.05')} لدى أيٍّ منها، حتى قبل التصحيح. الأقرب إلى العتبة: "
                             f"{name(v)}، {hr_txt(lang, c['HR (A)'], c['p (A)'])} {per(v)} في المهمة A (فترة الثقة "
                             f"{iso(lang, '95%')}: {ci})، و{hr_txt(lang, c['HR (B)'], c['p (B)'])} في المهمة B."}[lang]

        # ---- variables that meet every condition but one
        near_parts = []
        for r in dec:
            v = r["variable"]
            ok = {1: r["1. Holm < 0,05"], 2: r["2. même sens"], 3: r["3. C > M0"], 4: r["4. contrôles"]}
            failed = [k for k, x in ok.items() if not x]
            if v in kept or len(failed) != 1:
                continue
            hold = iso(lang, f"p = {raw(lang, r['p Holm'], 3)}")
            gain = f"{signed(lang, r['écart C (A)'], 3)}{COMMA[lang]}{p_corrected(lang, r['p corrigée C'])}"
            ctrl = f"{hr_txt(lang, r['HR contrôlé (A)'])}{COMMA[lang]}{p_txt(lang, r['p contrôlé (A)'])}"
            what = {1: {"fr": f"son effet ne reste pas significatif après la correction de Holm ({hold})",
                        "en": f"its effect does not remain significant after the Holm correction ({hold})",
                        "ar": f"لا يبقى أثره ذا دلالة بعد تصحيح هولم ({hold})"},
                    2: {"fr": f"son effet change de sens en tâche B ({hr_txt(lang, r['HR (B)'])})",
                        "en": f"its effect changes direction in task B ({hr_txt(lang, r['HR (B)'])})",
                        "ar": f"يتغيّر اتجاه أثره في المهمة B ({hr_txt(lang, r['HR (B)'])})"},
                    3: {"fr": f"son ajout au modèle existant n'améliore pas nettement le C-index en validation croisée "
                              f"({gain})",
                        "en": f"adding it to the existing model does not clearly improve the C-index in cross-validation "
                              f"({gain})",
                        "ar": f"لا تُحسِّن إضافته إلى النموذج القائم مؤشرَ التوافق في التحقق المتقاطع تحسينًا واضحًا ({gain})"},
                    4: {"fr": f"son effet ne survit pas aux contrôles de l'époque et du PIB ({ctrl} en tâche A)",
                        "en": f"its effect does not survive the period and GDP controls ({ctrl} in task A)",
                        "ar": f"لا يصمد أثره عند ضبط الحقبة الزمنية والناتج المحلي ({ctrl} في المهمة A)"}}[failed[0]][lang]
            higher = r["HR (A)"] > 1
            near_parts.append({
                "fr": f"**Presque retenue : {name(v)}.** Elle remplit trois des quatre conditions "
                      f"({hr_txt(lang, r['HR (A)'], r['p (A)'])} {per(v)} en tâche A), mais {what}. Le risque de chute "
                      f"est {'plus élevé' if higher else 'plus faible'}, à valeurs égales des facteurs du modèle "
                      "existant : c'est une association, pas un effet.",
                "en": f"**Almost kept: {name(v)}.** It meets three of the four conditions "
                      f"({hr_txt(lang, r['HR (A)'], r['p (A)'])} {per(v)} in task A), but {what}. The risk of falling "
                      f"is {'higher' if higher else 'lower'}, other factors of the existing model being equal: it is an "
                      "association, not an effect.",
                "ar": f"**متغير كاد يُحتفَظ به: {name(v)}.** يستوفي ثلاثة من الشروط الأربعة "
                      f"({hr_txt(lang, r['HR (A)'], r['p (A)'])} {per(v)} في المهمة A)، لكن {what}. ويكون خطر السقوط "
                      f"{'أعلى' if higher else 'أقل'}، مع تساوي عوامل النموذج القائم: إنها علاقة ارتباط لا أثر سببي.",
            }[lang])
        near_txt = " ".join(near_parts) if near_parts else {
            "fr": "Aucune variable ne remplit toutes les conditions sauf une.",
            "en": "No variable meets all the conditions but one.",
            "ar": "لا يوجد متغير يستوفي كل الشروط إلا شرطًا واحدًا."}[lang]

        # ---- prediction (task A: C-index; task B: ROC-AUC)
        t1, t3 = test_a["P1"], test_a["P3"]
        best = max(dec, key=lambda r: r["écart C (A)"])
        spells = join(lang, [count(lang, sample["spells"], "party"), count(lang, sample["events"], "fall")])
        obs = join(lang, [count(lang, sample["rows_tv"], "obs"), count(lang, sample["events_tv"], "fall")])
        d1 = f"{signed(lang, t1['C de Harrell : écart'], 3)}{COMMA[lang]}{p_corrected(lang, t1['C de Harrell : p corrigée'])}"
        db = f"{signed(lang, best['écart C (A)'], 3)} ({p_corrected(lang, best['p corrigée C'])})"
        w = num(lang, t3["poids moyen du bloc"], 2)
        b1, b3 = DEMO_VERDICT[test_b["P1"]["verdict"]][lang], DEMO_VERDICT[test_b["P3"]["verdict"]][lang]
        prediction = {
            "fr": f"**Prédiction.** Tâche A, sur l'échantillon commun ({spells}) : le modèle existant atteint un C-index "
                  f"de {num(lang, c_idx['M0'], 3)}. Les variables seules obtiennent {num(lang, c_idx['P1'], 3)} (écart "
                  f"{d1}) : {DEMO_VERDICT[t1['verdict']][lang]}. Mélangées au modèle existant, avec un poids moyen de {w} "
                  f"pour le bloc, elles obtiennent {num(lang, c_idx['P3'], 3)} : {DEMO_VERDICT[t3['verdict']][lang]}. "
                  f"Meilleur ajout au modèle existant : {name(best['variable'])}, qui change le C-index de {db}. "
                  f"Tâche B ({obs}) : ROC-AUC de {num(lang, auc['M0'], 3)} pour le modèle existant, "
                  f"{num(lang, auc['P1'], 3)} pour les variables seules ({b1}) et {num(lang, auc['P3'], 3)} pour le "
                  f"mélange ({b3}).",
            "en": f"**Prediction.** Task A, on the common sample ({spells}): the existing model reaches a C-index of "
                  f"{num(lang, c_idx['M0'], 3)}. The variables alone reach {num(lang, c_idx['P1'], 3)} (difference "
                  f"{d1}): {DEMO_VERDICT[t1['verdict']][lang]}. Blended with the existing model, with an average weight "
                  f"of {w} for the block, they reach {num(lang, c_idx['P3'], 3)}: {DEMO_VERDICT[t3['verdict']][lang]}. "
                  f"Best addition to the existing model: {name(best['variable'])}, which changes the C-index by {db}. "
                  f"Task B ({obs}): ROC-AUC of {num(lang, auc['M0'], 3)} for the existing model, "
                  f"{num(lang, auc['P1'], 3)} for the variables alone ({b1}) and {num(lang, auc['P3'], 3)} for the "
                  f"blend ({b3}).",
            "ar": f"**التنبؤ.** المهمة A، على العينة المشتركة ({spells}): يبلغ مؤشر التوافق للنموذج القائم "
                  f"{num(lang, c_idx['M0'], 3)}. وتبلغ المتغيرات وحدها {num(lang, c_idx['P1'], 3)} (فارق {d1}): "
                  f"{DEMO_VERDICT[t1['verdict']][lang]}. وعند مزجها بالنموذج القائم، بوزن متوسط قدره {w} للكتلة، تبلغ "
                  f"{num(lang, c_idx['P3'], 3)}: {DEMO_VERDICT[t3['verdict']][lang]}. أفضل إضافة إلى النموذج القائم: "
                  f"{name(best['variable'])}؛ يتغيّر معها مؤشر التوافق بمقدار {db}. المهمة B ({obs}): يبلغ ROC-AUC "
                  f"{num(lang, auc['M0'], 3)} للنموذج القائم، و{num(lang, auc['P1'], 3)} للمتغيرات وحدها ({b1})، "
                  f"و{num(lang, auc['P3'], 3)} للمزيج ({b3}).",
        }[lang]

        # ---- which leader
        method = {
            "fr": f"**Quel dirigeant.** En tâche A, chaque parti est relié au dirigeant qui l'a mené au pouvoir, dans une "
                  f"table revue à la main avec Archigos et Wikipédia : le lien automatique (le dirigeant effectif "
                  f"d'Archigos au 31 décembre de l'année d'entrée) est confirmé pour {num(lang, links['automatic_confirmed'])} "
                  f"partis sur {num(lang, links['spells'])}, remplacé par un autre dirigeant pour "
                  f"{num(lang, links['other_leader'])} et retiré pour {num(lang, links['no_link'])}, dont les dirigeants "
                  f"effectifs n'appartenaient pas au parti. En tâche B, c'est le dirigeant effectif d'Archigos au "
                  f"31 décembre de l'année précédente (la première année du parti, le dirigeant de la table ; aucun "
                  f"pour un parti sans lien). Archigos s'arrêtant en {year(last)}, les années suivantes n'ont pas de "
                  f"valeurs du dirigeant ({count(lang, after['parti-années'], 'obs')}, "
                  f"{count(lang, after['chutes'], 'fall')}).",
            "en": f"**Which leader.** In task A, each party is linked to the leader who brought it to power, in a table "
                  f"reviewed by hand with Archigos and Wikipedia: the automatic link (Archigos's effective leader on "
                  f"31 December of the entry year) is confirmed for {num(lang, links['automatic_confirmed'])} parties "
                  f"out of {num(lang, links['spells'])}, replaced by another leader for {num(lang, links['other_leader'])} "
                  f"and removed for {num(lang, links['no_link'])}, whose effective leaders did not belong to the party. "
                  f"In task B, it is Archigos's effective leader on 31 December of the previous year (in the party's "
                  f"first year, the leader of the table; none for a party without a link). Since Archigos ends in "
                  f"{year(last)}, the following years have no leader values ({count(lang, after['parti-années'], 'obs')}, "
                  f"{count(lang, after['chutes'], 'fall')}).",
            "ar": f"**أيّ قائد.** في المهمة A، يُربَط كل حزب بالقائد الذي أوصله إلى السلطة، في جدول رُوجع يدويًا بالاستعانة "
                  f"بـArchigos وويكيبيديا: أُكِّد الربط الآلي (القائد الفعلي في Archigos يوم {iso(lang, '31')} ديسمبر من "
                  f"سنة الوصول إلى السلطة) لـ{count(lang, links['automatic_confirmed'], 'party')} من أصل "
                  f"{num(lang, links['spells'])}، واستُبدل بقائد آخر لـ{count(lang, links['other_leader'], 'party')}، "
                  f"وأُلغي لـ{count(lang, links['no_link'], 'party')} لم يكن قادتها الفعليون من الحزب. وفي المهمة B، هو "
                  f"القائد الفعلي في Archigos يوم {iso(lang, '31')} ديسمبر من السنة السابقة (في السنة الأولى للحزب، قائد "
                  f"الجدول؛ ولا قائد لحزب بلا ربط). وبما أن Archigos تتوقف عام {year(last)}، لا توجد قيم للقائد في "
                  f"السنوات اللاحقة ({count(lang, after['parti-années'], 'obs')}، {count(lang, after['chutes'], 'fall')}).",
        }[lang]

        # ---- testable or not
        if untestable:
            parts = []
            for v in untestable:
                if v in screening["dropped"]:
                    why = {"fr": f"{count(lang, cov[v]['A : chutes'], 'fall')} en tâche A et "
                                 f"{count(lang, cov[v]['B : chutes'], 'fall')} en tâche B, pour un minimum de "
                                 f"{num(lang, min_falls)}",
                           "en": f"{count(lang, cov[v]['A : chutes'], 'fall')} in task A and "
                                 f"{count(lang, cov[v]['B : chutes'], 'fall')} in task B, for a minimum of "
                                 f"{num(lang, min_falls)}",
                           "ar": f"{count(lang, cov[v]['A : chutes'], 'fall')} في المهمة A و"
                                 f"{count(lang, cov[v]['B : chutes'], 'fall')} في المهمة B، والحد الأدنى "
                                 f"{num(lang, min_falls)}"}[lang]
                else:
                    info = screening["removed_for_sample"][v]
                    why = {"fr": f"l'ajouter réduirait l'échantillon commun à {count(lang, info['falls_a'], 'fall')} en "
                                 f"tâche A et {count(lang, info['falls_b'], 'fall')} en tâche B, pour un minimum de "
                                 f"{num(lang, min_epp)} chutes par paramètre",
                           "en": f"adding it would reduce the common sample to {count(lang, info['falls_a'], 'fall')} in "
                                 f"task A and {count(lang, info['falls_b'], 'fall')} in task B, for a minimum of "
                                 f"{num(lang, min_epp)} falls per parameter",
                           "ar": f"إضافته تقلّص العينة المشتركة إلى {count(lang, info['falls_a'], 'fall')} في المهمة A "
                                 f"و{count(lang, info['falls_b'], 'fall')} في المهمة B، والحد الأدنى "
                                 f"{num(lang, min_epp)} حالات سقوط لكل معلَمة"}[lang]
                parts.append(f"**{head(v)}** : {why}." if lang == "fr" else f"**{head(v)}**: {why}.")
            testable = {"fr": "**Variables non testables.** ", "en": "**Variables that cannot be tested.** ",
                        "ar": "**متغيرات لا يمكن اختبارها.** "}[lang] + " ".join(parts)
        else:
            epp_a, epp_b = num(lang, sample["events"] / largest["A"], 1), num(lang, sample["events_tv"] / largest["B"], 1)
            testable = {
                "fr": f"**Toutes les variables sont testables.** Chacune garde au moins {num(lang, min_falls)} chutes "
                      f"dans chaque tâche, et l'échantillon commun en garde {num(lang, sample['events'])} en tâche A et "
                      f"{num(lang, sample['events_tv'])} en tâche B, soit {epp_a} et {epp_b} chutes par paramètre pour "
                      f"le plus grand modèle prévu (minimum {num(lang, min_epp)}).",
                "en": f"**All variables can be tested.** Each keeps at least {num(lang, min_falls)} falls in each task, "
                      f"and the common sample keeps {num(lang, sample['events'])} in task A and "
                      f"{num(lang, sample['events_tv'])} in task B, that is {epp_a} and {epp_b} falls per parameter for "
                      f"the largest planned model (minimum {num(lang, min_epp)}).",
                "ar": f"**كل المتغيرات قابلة للاختبار.** يحتفظ كلٌّ منها بما لا يقل عن {num(lang, min_falls)} حالة سقوط "
                      f"في كل مهمة، وتحتفظ العينة المشتركة بـ{count(lang, sample['events'], 'fall')} في المهمة A "
                      f"و{count(lang, sample['events_tv'], 'fall')} في المهمة B، أي {epp_a} و{epp_b} حالة سقوط لكل "
                      f"معلَمة في أكبر نموذج مخطَّط له (الحد الأدنى {num(lang, min_epp)}).",
            }[lang]

        # ---- limits
        limits = [
            {"fr": "**Qui est « le dirigeant ».** Archigos code le dirigeant effectif du pays, qui n'est pas toujours le "
                   "chef du parti (le roi d'une monarchie, un président ou un Premier ministre quand le secrétaire "
                   f"général du parti n'est pas codé). La table de la tâche A a été revue à la main "
                   f"({num(lang, links['other_leader'])} dirigeants corrigés, {num(lang, links['no_link'])} partis sans "
                   "lien) ; en tâche B, le dirigeant de chaque année vient d'Archigos, sans revue année par année.",
             "en": "**Who “the leader” is.** Archigos codes the country's effective leader, who is not always the head "
                   "of the party (the king of a monarchy, a president or a prime minister when the party's general "
                   f"secretary is not coded). The table of task A was reviewed by hand ({num(lang, links['other_leader'])} "
                   f"leaders corrected, {num(lang, links['no_link'])} parties without a link); in task B, the leader of "
                   "each year comes from Archigos, without a year-by-year review.",
             "ar": "**من هو «القائد».** يرمّز Archigos القائدَ الفعلي للبلد، وليس دائمًا رئيسَ الحزب (ملك في نظام ملكي، "
                   "أو رئيس أو رئيس وزراء حين لا يُرمَّز الأمين العام للحزب). رُوجع جدول المهمة A يدويًا (صُحِّح القائد "
                   f"لـ{count(lang, links['other_leader'], 'party')}، وأُلغي الربط لـ{count(lang, links['no_link'], 'party')})؛ "
                   "أما في المهمة B فيأتي قائد كل سنة من Archigos دون مراجعة سنة بسنة."},
            {"fr": f"**Couverture.** Archigos s'arrête en {year(last)} et LEAD en {year(2004)} : un dirigeant arrivé plus "
                   "tard n'a pas de valeurs LEAD. Les échantillons communs sont donc plus anciens que l'échantillon "
                   "complet.",
             "en": f"**Coverage.** Archigos ends in {year(last)} and LEAD in {year(2004)}: a leader who took power later "
                   "has no LEAD values. The common samples are therefore older than the full sample.",
             "ar": f"**التغطية.** تتوقف Archigos عام {year(last)} وLEAD عام {year(2004)}: ولا قيم في LEAD لقائد وصل "
                   "إلى السلطة بعد ذلك. لذلك فالعينات المشتركة أقدم من العينة الكاملة."},
            {"fr": "**Âge du parti.** Il dépend de l'année de fondation codée par l'ARPD ; pour un parti issu d'une fusion "
                   "ou d'un changement de nom, la date retenue peut être discutée.",
             "en": "**Party's age.** It depends on the founding year coded by the ARPD; for a party born of a merger or "
                   "a change of name, the date chosen can be debated.",
             "ar": "**عمر الحزب.** يتوقف على سنة التأسيس التي يرمّزها ARPD؛ وبالنسبة إلى حزب نشأ عن اندماج أو تغيير اسم، "
                   "قد يكون التاريخ المعتمَد موضع نقاش."},
            {"fr": "**Recoupement avec le modèle existant.** Un dirigeant arrivé par un coup d'État ou passé par l'armée "
                   "dirige souvent un parti d'origine militaire, un ancien rebelle un parti d'origine révolutionnaire : "
                   "la question posée est ce que la variable ajoute au-delà de ces covariables.",
             "en": "**Overlap with the existing model.** A leader who came to power in a coup or served in the military "
                   "often heads a party of military origin, a former rebel a party of revolutionary origin: the question "
                   "is what the variable adds beyond these covariates.",
             "ar": "**التداخل مع النموذج القائم.** كثيرًا ما يقود الحزبَ ذا الأصل العسكري قائدٌ وصل بانقلاب أو خدم في "
                   "الجيش، ويقود الحزبَ ذا الأصل الثوري متمردٌ سابق: والسؤال المطروح هو ما يضيفه المتغير بعد هذه "
                   "المتغيرات المشترَكة."},
            {"fr": "**Associations, pas causes.** Les caractéristiques d'un dirigeant ne sont pas tirées au hasard : un "
                   "parti peut choisir un dirigeant âgé parce qu'il est déjà solide, ou un militaire parce qu'il est "
                   "menacé.",
             "en": "**Associations, not causes.** A leader's characteristics are not drawn at random: a party may choose "
                   "an older leader because it is already strong, or a soldier because it is under threat.",
             "ar": "**علاقات ارتباط لا أسباب.** لا تُسحَب خصائص القائد عشوائيًا: فقد يختار الحزب قائدًا مسنًّا لأنه قوي "
                   "أصلًا، أو عسكريًا لأنه مهدَّد."},
            {"fr": f"**Peu de chutes.** L'échantillon commun de la tâche A garde {num(lang, sample['events'])} chutes, "
                   f"soit {num(lang, sample['events'] / largest['A'], 1)} par paramètre pour le plus grand modèle "
                   f"prévu ; avec la correction de Holm sur {num(lang, n)} variables, un effet modeste peut passer "
                   "inaperçu.",
             "en": f"**Few falls.** The common sample of task A keeps {num(lang, sample['events'])} falls, that is "
                   f"{num(lang, sample['events'] / largest['A'], 1)} per parameter for the largest planned model; with "
                   f"the Holm correction over {num(lang, n)} variables, a modest effect can go unnoticed.",
             "ar": f"**قلة حالات السقوط.** تحتفظ العينة المشتركة للمهمة A بـ{count(lang, sample['events'], 'fall')}، أي "
                   f"{num(lang, sample['events'] / largest['A'], 1)} لكل معلَمة في أكبر نموذج مخطَّط له؛ ومع تصحيح هولم "
                   f"على {count(lang, n, 'variable')}، قد يمرّ أثر متواضع دون أن يُلاحَظ."},
        ]
        limits = [x[lang] for x in limits]

        recommendation = ({
            "fr": "**Conséquence pour le simulateur.** Aucune variable n'étant retenue, le modèle du simulateur ne change "
                  "pas, et aucune ne devient un réglage du jeu.",
            "en": "**What this means for the simulator.** Since no variable is kept, the simulator's model does not "
                  "change, and none becomes a setting of the game.",
            "ar": "**ما يعنيه ذلك للمحاكي.** بما أنه لم يُحتفَظ بأي متغير، لا يتغيّر نموذج المحاكي، ولا يصبح أيٌّ منها من "
                  "إعدادات اللعبة.",
        } if not kept else {
            "fr": "**Conséquence pour le simulateur.** Le modèle du simulateur ne change pas : une variable retenue décrit "
                  "le parti ou son dirigeant, et ne deviendrait un réglage du jeu qu'après une décision explicite, prise "
                  "après la lecture de ces résultats.",
            "en": "**What this means for the simulator.** The simulator's model does not change: a variable kept "
                  "describes the party or its leader, and would become a setting of the game only after an explicit "
                  "decision, taken after reading these results.",
            "ar": "**ما يعنيه ذلك للمحاكي.** لا يتغيّر نموذج المحاكي: فالمتغير المحتفَظ به يصف الحزب أو قائده، ولن يصبح من "
                  "إعدادات اللعبة إلا بقرار صريح يُتَّخذ بعد قراءة هذه النتائج.",
        })[lang]

        out[lang] = {
            "answer": answer, "near": near_txt, "prediction": prediction, "method": method, "testable": testable,
            "limits": limits, "recommendation": recommendation,
            "labels": [head(r["variable"]) for r in cands],
            "definitions": [LEADER_DEFS[r["variable"]][lang] for r in cands],
            "units": [LEADER_UNITS[r["unité du HR"]][lang][0] for r in cands],
        }
    return same_text_in_all_languages(out)
