/* English dictionary of the site. Terms: docs/glossary.md.
   The content after "=" is valid JSON (read as such by tests/test_frontend_build.py).
   Plurals: {one, other} chosen by {count}; {count} is formatted for the language. */
window.I18N_DICT = window.I18N_DICT || {};
window.I18N_DICT.en = {
 "brand": {"title": "Regime Observatory", "sub": "Authoritarian parties · 1946–2024"},
 "nav": {"home": "Home", "label": "Pages", "atlas": "Atlas", "analyse": "Analysis", "simulation": "Simulation", "about": "About"},
 "status": {"data": "Data", "clock": "Clock", "model": "Model", "ok": "System operational"},
 "common": {
  "language": "Site language", "yes": "yes", "no": "no", "colon": ": ", "listSep": "; ", "period": ".",
  "skipToContent": "Skip to content", "skipToTimeline": "Skip to the timeline"
 },
 "units": {
  "years": {"one": "{count} year", "other": "{count} years"},
  "yearsWord": {"one": "year", "other": "years"},
  "parties": {"one": "{count} party", "other": "{count} parties"},
  "falls": {"one": "{count} fall", "other": "{count} falls"},
  "countries": {"one": "{count} country", "other": "{count} countries"},
  "partyYears": {"one": "{count} party-year", "other": "{count} party-years"},
  "regimes": {"one": "{count} regime", "other": "{count} regimes"},
  "factors": {"one": "{count} factor", "other": "{count} factors"}
 },
 "labels": {
  "category": {
   "nodata": "No data", "party": "Party regime", "military": "Military regime",
   "monarchy": "Authoritarian monarchy", "other_arpd": "Other autocracy", "other_vdem": "Other autocracy",
   "democracy": "Democracy", "dependent": "Non-sovereign territory"
  },
  "regimeType": {
   "party": "party regime", "military": "military regime", "military_monarchy": "military-monarchical regime",
   "monarchy": "authoritarian monarchy", "personal": "personalist regime", "occupation": "foreign occupation",
   "transitional": "transitional government", "failed_state": "failed state", "civil_war": "civil war",
   "theocracy": "theocracy", "unclassified": "unclassified autocracy without a party"
  },
  "origin": {
   "Dictator-Created": "created by a dictator", "Elite Coalition": "elite coalition",
   "Revolution": "born of a revolution", "Independence": "born of the independence struggle",
   "Communist": "communist party", "Military": "founded by the military", "Merger": "merger of parties",
   "Split": "split from a party", "Dictator-Created/Merger": "created by a dictator (merger)",
   "Dictator-Created/Split": "created by a dictator (split)", "Merger/Split": "merger or split"
  },
  "originShort": {
   "Communist": "Communist", "Dictator-Created": "Dictator-created", "Elite Coalition": "Elite coalition",
   "Independence": "Independence", "Merger/Split": "Merger / split", "Military": "Military", "Revolution": "Revolution"
  },
  "gained": {
   "Election": "election", "Dictator-Created": "created by the incumbent ruler", "Coup": "coup",
   "Revolution": "revolution", "Military": "military takeover", "Dictator-Supported": "backed by the incumbent ruler",
   "Communist-Imposed": "imposed by a communist power", "Foreign-Imposed": "imposed by a foreign power",
   "Dictator-Supported/Revolution": "revolution backed by the incumbent ruler", "Communist": "communist takeover",
   "Dictator-Supported/Election": "election backed by the incumbent ruler",
   "Foreign-Imposed/Election": "election imposed from abroad", "Revolution/Election": "revolution, then election"
  },
  "ended": {
   "Coup": "coup", "Election": "electoral defeat", "Continued": "continued under another regime",
   "Revolution": "revolution", "Dictator-Supported": "the ruler's decision", "Protests/Election": "protests, then elections",
   "Occupation": "foreign occupation", "Merger": "merger with another party", "Protests": "protests",
   "Civil War": "civil war", "Split": "split", "Protests/Coup": "protests, then a coup",
   "Country Merger": "merger of states", "Revolution/Election": "revolution, then elections"
  },
  "governance": {
   "Policy-Based": "policy-based", "Policy-Based/Repressive": "policy-based and repressive",
   "Repressive": "repressive", "Clientelist/Policy-Based": "clientelist and policy-based",
   "Clientelist": "clientelist", "Clientelist/Repressive": "clientelist and repressive"
  },
  "governanceShort": {"Policy-Based": "Policy-based", "Repressive": "Repressive", "Clientelist": "Clientelist", "Non codé": "Not coded"},
  "vdemRegime": ["closed autocracy", "electoral autocracy", "electoral democracy", "liberal democracy"],
  "vdemRegimeInSentence": ["a closed autocracy", "an electoral autocracy", "an electoral democracy", "a liberal democracy"],
  "covariate": {
   "Marxist?": "Marxist-Leninist ideology", "Gov_Repressive": "Repressive strategy",
   "Gov_Clientelist": "Clientelist strategy", "Gov_Non code": "Strategy not coded",
   "polity2_entry": "Polity2 at entry (per point)", "polity2_lag1": "Polity2, previous year (per point)",
   "vdem_entry": "V-Dem at entry (per 0.1)", "vdem_lag1": "V-Dem, previous year (per 0.1)",
   "conflict_entry": "Armed conflict at entry", "conflict_active_lag1": "Armed conflict, previous year",
   "log_gdppc_entry": "log GDP per capita at entry", "log_gdppc_lag1": "log GDP per capita, previous year",
   "Origin_Communist": "Communist origin", "Origin_Elite Coalition": "Origin: elite coalition",
   "Origin_Independence": "Origin: independence", "Origin_Merger/Split": "Origin: merger / split",
   "Origin_Military": "Military origin", "Origin_Revolution": "Revolutionary origin",
   "Origin_Communist_x_late": "Communist origin, after 10 years", "Origin_Military_x_late": "Military origin, after 10 years",
   "conflict_entry_x_late": "Conflict at entry, after 10 years", "niveau démocratique": "Democracy level",
   "Origin": "Origin", "Gouvernance": "Governance strategy", "start": "Time in power"
  },
  "covariateShort": {
   "polity2_entry": "Polity2 (per point)", "conflict_entry": "Armed conflict", "log_gdppc_entry": "log GDP per capita",
   "Marxist?": "Marxist-Leninist ideology", "Origin_Communist": "Communist origin"
  },
  "factor": {
   "Origin": "Origin", "Gouvernance": "Governance", "polity2_entry": "Polity2", "polity2_lag1": "Polity2",
   "Marxist?": "Ideology", "conflict_entry": "Conflict", "conflict_active_lag1": "Conflict",
   "log_gdppc_lag1": "GDP", "log_gdppc_entry": "GDP"
  },
  "model": {
   "KM": "Kaplan-Meier (no covariate)", "Cox": "Cox", "RSF": "Random survival forest", "GBSA": "Gradient-boosted survival",
   "Temps seul": "Duration only", "Cox time-varying": "Time-varying Cox", "Logistique": "Logistic regression", "LightGBM": "LightGBM"
  },
  "source": {
   "V-Dem (v2x_polyarchy)": "V-Dem", "Polity5 (polity2)": "Polity5", "Maddison (PIB par habitant)": "Maddison (GDP)",
   "UCDP (conflit)": "UCDP (conflicts)", "REIGN (type de régime)": "REIGN", "Archigos (dirigeant)": "Archigos"
  },
  "era": {"avant 1945": "before 1945", "1945-1989": "1945–1989", "depuis 1990": "since 1990"},
  "verdict": {
   "référence": "reference", "meilleur que Cox": "better than Cox", "moins bon que Cox": "worse than Cox",
   "pas de différence nette": "no clear difference", "sans covariable : moins bon que Cox": "no covariate: worse than Cox",
   "sans covariable : pas de différence nette": "no covariate: no clear difference"
  }
 },
 "atlas": {
  "historyTitle": "Autocracies in the world, year by year",
  "graphShow": "Show chart",
  "graphHide": "Hide chart",
  "pageTitle": "Atlas of authoritarian regimes",
  "pageDescription": "Interactive globe of authoritarian regimes from 1946 to 2024 (ARPD, V-Dem).",
  "globeAria": "Globe of regimes: drag to rotate, scroll to zoom, click a country. The List view gives the same information as a table.",
  "loading": "Loading the 3D globe…",
  "loadingNote": "The timeline, the panels and the List view already work.",
  "noWebgl": "The 3D globe needs WebGL, which this browser does not provide: each year's data are shown here as a list.",
  "world": "World situation",
  "kpiLabel": "sovereign autocracies",
  "kpiShare": "{pct} of the {states} on record",
  "sovereignStates": {"one": "{count} sovereign state", "other": "{count} sovereign states"},
  "legendAria": "Legend and count by regime type",
  "legendToggle": "Click to hide or show",
  "legendNoteType": "Other autocracy: personalist rule, occupation, transition, or an autocracy according to V-Dem that is not in the ARPD.",
  "legendNoteAge": "Years in power of the ruling regime (regimes recorded in the ARPD). Other countries stay dark.",
  "legendNoteVdem": "V-Dem's electoral democracy index (0 to 1), for every country covered.",
  "events": "Events of the year",
  "noEvents": "No regime change on record.",
  "fallAfter": "Fell after {years}",
  "accession": "Came to power",
  "oldest": "Longest in power",
  "inPower": "{years} in power",
  "controlsAria": "Display controls",
  "viewLabel": "View", "viewGlobe": "Globe", "viewList": "List",
  "modeLabel": "Reading", "modeAria": "Colour mode", "modeType": "Type", "modeAge": "Longevity", "modeVdem": "Democracy",
  "relief": "Relief: time in power", "reliefTitle": "Raises each autocracy according to its time in power",
  "rotate": "Auto-rotate",
  "searchLabel": "Find a country", "searchPlaceholder": "e.g. China, Chile, Soviet Union…",
  "historicalNames": [["Soviet Union", "RUS"], ["USSR", "RUS"], ["Yugoslavia", "SRB"], ["Czechoslovakia", "CZE"],
                      ["East Germany (GDR)", "DEU"], ["GDR", "DEU"], ["West Germany (FRG)", "DEU"],
                      ["North Vietnam", "VNM"], ["South Vietnam", "VNM"], ["North Yemen", "YEM"],
                      ["South Yemen", "YEM"], ["Zanzibar", "TZA"]],
  "list": {
   "title": "States in {year}", "count": {"one": "{count} state", "other": "{count} states"},
   "close": "Close the list", "open": "Open the card: {name}",
   "col": {"name": "Country", "type": "Regime type", "party": "Ruling party", "years": "Years in power"}
  },
  "dossier": "Country card", "dossierClose": "Close the card",
  "territory": "Territory: {name}",
  "media": {
   "flagAlt": "Flag: {state}, {year}",
   "logoAlt": "Logo: {party}",
   "logoCaption": "Party logo",
   "logoCurrent": "Current party logo",
   "portraitAlt": "Portrait: {name}",
   "wikiSource": "Wikipedia, “{title}”",
   "credits": "Image and text credits",
   "creditFlag": "Flag",
   "creditFlagOf": "Flag of {state}",
   "creditLogo": "Party logo",
   "creditPortrait": "Portrait of {name}",
   "creditNote": "Images: Wikimedia Commons, each under its own licence (see the link). Links between the data and the articles: Wikidata. Text: Wikipedia, CC BY-SA 4.0 licence. The images are loaded from Wikimedia's servers."
  },
  "status": {
   "annexedUSSR": "The territory is then annexed by the USSR (annexation not recognised).",
   "annexedIndonesia": "The territory is then annexed by Indonesia (annexation not recognised).",
   "crimea": "Crimea, annexed by Russia in 2014, is shown here as part of Ukraine: the annexation is not recognised (UN General Assembly resolution 68/262).",
   "spanishSahara": "The territory is then a Spanish colony, Spanish Sahara (until 1975).",
   "westernSahara": "A non-self-governing territory according to the UN, whose status is unresolved: Morocco has administered most of it since 1975; the Polisario Front, which proclaimed the Sahrawi Arab Democratic Republic in 1976, claims its independence."
  },
  "narr": {
   "inherited": "The territory of {territory} is then part of <strong>{state}</strong>.",
   "noData": "No data for this territory in {year}.",
   "dependent": "In {year}, this territory is not a sovereign state: V-Dem codes it as a colony or dependent territory.",
   "party": "<strong>Party regime.</strong> The <em>{party}</em> has held power since {start} — its {ord} year in {year}.",
   "noParty": "<strong>{type}</strong> without a ruling party, in place since {start} — its {ord} year in {year}.",
   "traitOrigin": "origin: {value}", "traitGained": "came to power through: {value}", "traitMarxist": "Marxist-Leninist ideology",
   "governance": "Governance strategy: {value}.",
   "gained": "Came to power through: {value}.",
   "how": " ({value})",
   "ongoing": "Still in power in {last}, the last year observed.",
   "willEnd": "This regime will leave power in {end}{how}.",
   "lastYear": "This is its last year in power{how}.",
   "otherVdem": "<strong>Autocracy outside the ARPD.</strong> V-Dem classifies this country as {regime} in {year}, with no party regime or junta recorded in the ARPD for that year.",
   "democracy": "<strong>Democracy.</strong> V-Dem classifies this country as {regime} in {year}."
  },
  "detail": {
   "regime": "Regime", "party": "Party", "inPower": "In power", "span": "{start} → {end}", "spanOngoing": "{start} → ongoing", "founded": "Founded",
   "origin": "Origin", "gained": "Came to power", "strategy": "Strategy", "notCoded": "not coded in the ARPD",
   "marxist": "Marxist-Leninist", "independence": "Independence", "sinceIndependence": "in power since independence",
   "renamed": "Renamed", "end": "End", "polyarchy": "Electoral democracy"
  },
  "headOfState": "Head of state", "headOfStateAndGov": "Head of state and government", "headOfGov": "Head of government",
  "leaders": "Leaders on 31 December {year} (V-Dem)",
  "trajectory": "Path of the territory, {range}",
  "stripAria": "Regime type by year, {range}",
  "polyarchyTitle": "Electoral democracy (V-Dem, 0 to 1)",
  "sparkAria": "V-Dem electoral democracy index, {range}",
  "secondaryTitle": "Historical state on this territory",
  "secondaryOut": "Outside this state's period in {year}.",
  "dossierSources": "Sources: ARPD (Miller, 2020) and a post-2015 extension coded by hand; V-Dem v16 (classification, index, leaders on 31 December); flags, logos, portraits and extracts: Wikidata, Wikimedia Commons and Wikipedia.",
  "timelineAria": "Timeline", "year": "Year", "prevYear": "Previous year", "nextYear": "Next year",
  "play": "Play the years", "pause": "Pause the animation",
  "historyAria": "Number of sovereign autocracies by type, {range}",
  "autocracies": {"one": "{count} autocracy", "other": "{count} autocracies"},
  "announce": {"one": "Year {year}: {count} sovereign autocracy.", "other": "Year {year}: {count} sovereign autocracies."},
  "credits": "Present-day borders (Natural Earth); the territories of dissolved unions (Soviet Union, Yugoslavia…) take the colour of the state they belonged to. Data: ARPD (Miller, 2020), V-Dem v16 (CC BY-SA 4.0)."
 },
 "analyse": {
  "pageTitle": "Survival of authoritarian parties: the analysis",
  "pageDescription": "Results of the notebooks: survival, Cox models, robustness and predictive benchmark.",
  "km": {
   "aria": "Kaplan-Meier survival curves", "median": "median: {years}", "all": "All parties",
   "tipHead": "{years} in power", "tipLine": "{label}: {pct} still in power",
   "axisY": "share still in power", "axisX": "years in power"
  },
  "model": {"static": "Static", "staticGdp": "Static + GDP", "corrected": "Corrected", "timevarying": "Time-varying"},
  "factorName": {
   "Origin_Communist": "communist origin", "Origin_Elite Coalition": "elite-coalition origin",
   "Origin_Independence": "independence-movement origin", "Origin_Merger/Split": "merger-or-split origin",
   "Origin_Military": "military origin", "Origin_Revolution": "revolutionary origin",
   "Marxist?": "Marxist-Leninist ideology",
   "Gov_Repressive": "a repressive strategy", "Gov_Clientelist": "a clientelist strategy",
   "conflict_entry": "armed conflict at entry into power", "polity2": "the Polity2 score", "conflict": "armed conflict",
   "gdp": "GDP per capita"
  },
  "howto": {
   "glossary": "See the glossary:",
   "km": {
    "title": "How to read these curves",
    "items": [
     "Each curve starts at 100% (all parties in power) and steps down at each fall: its height at a given duration is the share of parties still in power, for example {pct} after {years}.",
     "The dotted line marks the median, the time by which half of the parties had fallen: {median}.",
     "The grey band around the curve is the 95% confidence interval: the wider it is, the less precise the estimate.",
     "The {censored} parties still in power in {year} count until their last observed year, with no invented date of fall: this is censoring.",
     "In the “By group” chart, pick a grouping, then hover over a row of the table to highlight its curve; the log-rank test tells whether the curves differ more than chance would explain."
    ]
   },
   "forest": {
    "title": "How to read this chart",
    "items": [
     "Each row is a factor and each column a Cox model; the dot gives the hazard ratio, the line its 95% confidence interval.",
     "The vertical line (1) means the same risk as the reference group: to the left, the party falls more slowly; to the right, faster.",
     "Filled dot: significant effect at the 5% level (the interval does not cross 1). Hollow dot: the difference may be due to chance.",
     "The scale is logarithmic: 0.5 (risk halved) and 2 (risk doubled) are the same distance from 1.",
     "The models differ in their sample and in how variables are measured: an effect found in every column is more solid."
    ],
    "example": "Example: {name}, {formula} in the static model, i.e. a risk of falling {k} times lower."
   },
   "robust": {
    "title": "How to read these tables",
    "items": [
     "Schoenfeld test: a p-value below 0.05 flags an effect that changes over time. Here {factors} are concerned: they get one effect before {cut} in power and another after.",
     "Before / after: hazard ratio and 95% confidence interval for each period.",
     "Sensitivity to the cut-off: the Wald test compares the two periods for several cut-offs; a high p-value means that the effects before and after do not clearly differ.",
     "V-Dem: “same conclusion” when the effect keeps the same direction and the same verdict, significant or not, with both measures of the democracy level."
    ],
    "example": "Example: {name} goes from {before} to {after}."
   },
   "bench": {
    "title": "How to read this comparison",
    "items": [
     "Each model learns on part of the countries and is evaluated on the others ({folds} folds × {repeats} repetitions, i.e. {evaluations} evaluations): this measures how well it predicts countries it has never seen.",
     "Harrell's C and ROC-AUC: 0.5 means chance and 1 a perfect prediction; the higher, the better. Integrated Brier score and log loss (↓): the lower, the better.",
     "The dot gives the mean of the {evaluations} evaluations and the line ± one standard deviation: widely overlapping lines mean equivalent models.",
     "Verdict: comparison with the Cox model by the corrected resampled t-test; “no clear difference” means the gap may be due to chance."
    ]
   },
   "country": {
    "title": "How to read this test",
    "items": [
     "Each variable is added alone to the existing model: its hazard ratio shows how the risk of falling changes when it increases by the unit shown (above 1, the risk rises).",
     "With {tested} variables tested at once, some look significant by chance: the Holm correction raises the bar accordingly.",
     "The C-index measures how well the model predicts countries it has not seen; the existing model reaches {c} over all parties.",
     "A variable that is not kept may still be linked to how long parties last: the test only shows that it adds no measurable information to the factors already in the model."
    ]
   },
   "shocks": {
    "title": "How to read this test",
    "items": [
     "Each row compares the year after a shock with a year without one, for parties that are otherwise comparable: to the right of ×1, the risk of falling is higher; to the left, lower.",
     "For disasters and battle deaths, the effect corresponds to ten times as many deaths per million people.",
     "Since several shocks are tested at once, some look significant by chance: the Holm correction raises the threshold accordingly.",
     "A shock that is not kept may still play a role: the test only shows that it does not measurably change the risk of falling, beyond the factors already in the model."
    ]
   },
   "leaders": {
    "title": "How to read this test",
    "items": [
     "Each row compares parties that are otherwise comparable but differ by one characteristic, measured when they came to power: to the right of ×1, the risk of falling is higher; to the left, lower.",
     "For the party's age, the leader's age and political experience, the effect corresponds to 10 more years; for the other variables, to “yes” rather than “no”.",
     "Since the {tested} variables are tested at once, some look significant by chance: the Holm correction raises the threshold accordingly.",
     "A variable that is not kept may still play a role: the test only shows that it adds no measurable information to the factors already in the model."
    ]
   }
  },
  "gl": {
   "title": "Glossary",
   "plain": {"one": "The notion that comes up throughout the report, illustrated with a figure from the analysis.", "other": "The {count} notions that come up throughout the report, each illustrated with a figure from the analysis."},
   "hr": {
    "term": "Hazard ratio (HR)",
    "def": "Ratio between the risks of falling of two groups, at any moment. HR = 1: same risk; HR = 0.5: risk halved; HR = 2: risk doubled.",
    "example": "Example: {name}, {formula} in the static model, i.e. a risk {k} times lower than in the reference group."
   },
   "censoring": {
    "term": "Censoring",
    "def": "A party still in power at the end of the observation period is censored: we know it lasted at least until then, not when it will fall. This applies to {censored} of the {total} in {year}; survival methods count them without inventing a date of fall."
   },
   "median": {
    "term": "Median survival",
    "def": "Time by which half of the parties have lost power, estimated while taking censoring into account: {median} for all named parties (95% confidence interval: {range} years)."
   },
   "cindex": {
    "term": "C-index (concordance index)",
    "def": "Share of pairs of parties that the model puts in the right order: the first to fall has the higher predicted risk. 0.5 means chance and 1 a perfect prediction; the Cox model reaches {c} in cross-validation grouped by country."
   },
   "pvalue": {
    "term": "p-value",
    "def": "Probability of observing a difference at least as large if the factor actually had no effect. Below 0.05, the effect is called significant; it is neither the probability that the effect exists nor a measure of its size.",
    "example": "Example: {name}, {p} in the static model."
   },
   "ci": {
    "term": "Confidence interval (95% CI)",
    "def": "Range of values compatible with the data. For a hazard ratio, an interval that contains 1 means the effect is not significant at the 5% level.",
    "example": "Example: {name}, 95% confidence interval of the hazard ratio: {range}, which does not contain 1."
   },
   "holm": {
    "term": "Holm correction",
    "def": "When many variables are tested, some cross the 0.05 threshold by chance. The Holm (1979) correction raises the threshold of each test according to their number; a variable is judged significant only if it remains so after correction."
   }
  },
  "s00": {
   "kpiPartiesSub": "came to power between {from} and {to}, followed until {end}"
  },
  "s01": {
   "title": "Data and sample",
   "lead": "From the ARPD dataset to the samples of the models: each step removes observations for a documented reason.",
   "plain": "The analysis starts from the {regimes} of the ARPD and keeps the {named} with a name, leaving juntas aside; the main model uses {used} of them, for lack of complete data on the others. The governance strategy is known for only {coded} of them.",
   "flowAll": "ARPD regimes (parties and juntas)",
   "flowNamed": {"one": "named parties · {count} junta without a party excluded", "other": "named parties · {count} juntas without a party excluded"},
   "flowFalls": "falls among named parties",
   "flowStatic": "static model · {falls}",
   "flowTv": "time-varying model · {falls}, {rows}",
   "coverage": "Coverage of the merged sources", "coverageLabel": "per party-year, {range}",
   "coverageAria": "Coverage of {source} by year", "coverageTip": "{pct} of party-years covered",
   "checkMarxist": "Communist parties coded Marxist", "checkMarxistSub": "against {pct} of other parties",
   "checkCorr": "Polity2 / V-Dem correlation", "checkCorrSub": {"one": "over {count} party-year", "other": "over {count} party-years"},
   "checkGov": "Governance strategy coded", "checkGovSub": "of parties; the rest form the “not coded” category",
   "checkMacro": "Complete macro variables", "checkMacroSub": "of party-years (Polity2, GDP, conflict)",
   "synthesis": "What the data impose on the models", "synthesisSource": "02_eda · synthesis"
  },
  "s02": {
   "title": "Survival in power",
   "lead": "Kaplan-Meier estimator: the probability that a party is still in power after t years, taking into account the parties still in place.",
   "plain": "Half of the parties lose power within {median} of taking it, and {pct} are still in power after {years}. Depending on the party's origin, this median ranges from {low} ({lowGroup}) to {high} ({highGroup}).",
   "groupAria": "Grouping",
   "group": {"origin": "Origin", "governance": "Strategy", "era": "Era"},
   "col": {"group": "Group", "parties": "Parties", "falls": "Falls", "median": "Median", "ci": "95% CI"},
   "notReached": "not reached",
   "logrank": "Log-rank test: {chi}, {p} — {verdict}",
   "differ": "the curves differ significantly.", "noDiffer": "no significant difference at the 5% level.",
   "notCodedNote": "“Not coded” is not a strategy: these are the parties whose strategy Miller (2020) does not code. This group is therefore neither drawn nor compared (longest and shortest durations, log-rank test, which covers the three coded strategies); it stays greyed out in the table."
  },
  "s03": {
   "title": "What makes a party last",
   "lead": "Hazard ratios of the Cox models (log scale): left of 1, the factor protects the party; right of 1, it speeds up its fall. Filled dot: significant at the 5% level.",
   "plainBest": "In the static model, the most protective factor is {name}: at any moment, the parties concerned have a risk of falling {k} times lower than the reference group ({formula}).",
   "plainWorst": "The most harmful is {name}, with a risk {k} times higher ({formula}).",
   "plainNone": "No factor is significant at the 5% level in the static model.",
   "covariate": "Covariate",
   "noteStatic": "values at entry", "noteStaticGdp": "variant", "noteCorrected": "effects before / after {cut} years",
   "noteTv": "previous-year values", "colSample": "{note} · {parties}, {falls}",
   "groupOrigin": "Origin (reference: dictator-created)",
   "groupGov": "Governance strategy (reference: policy-based)",
   "groupInst": "Ideology", "groupContext": "Context",
   "notCoded": "Not coded (not a strategy)",
   "beforeCut": " · before {cut} years",
   "lateGroup": "Effects after {cut} years in power (corrected model)",
   "lateRow": "{label}, after {cut} years",
   "axis": "Hazard ratio", "ci95": "95% CI",
   "note": "Polity2: effect per point of the scale (−10 to +10). GDP: per log unit (GDP multiplied by e ≈ 2.7). Corrected model: for the covariates whose effect changes over time, the first row gives the effect before the cut-off. Standard errors clustered by country (static and corrected models)."
  },
  "s04": {
   "title": "Assumptions and robustness",
   "lead": "The Cox model assumes effects that are constant over time; we test this, correct it, then replace Polity2 with V-Dem.",
   "plainAll": "The Schoenfeld test finds {factors} whose effect changes over time: the corrected model gives them one effect before {cut} in power and another after. Replacing Polity2 with V-Dem changes none of the {count} significant conclusions of the static model.",
   "plainSome": "The Schoenfeld test finds {factors} whose effect changes over time: the corrected model gives them one effect before {cut} in power and another after. Replacing Polity2 with V-Dem leaves {same} of the {count} significant conclusions of the static model unchanged.",
   "schoenfeld": "Schoenfeld test (static model)", "schoenfeldLabel": "proportional hazards",
   "col": {"covariate": "Covariate", "stat": "Statistic", "corrected": "Corrected", "before": "Before", "after": "After",
           "cut": "Cut-off", "pJoint": "joint p", "hrPolity": "HR Polity2", "hrVdem": "HR V-Dem", "robust": "Robust"},
   "schoenfeldNote": "Covariates with p < 0.05 get a separate effect before and after {cut} years in power.",
   "earlyLate": "Effects before and after the cut-off",
   "wald": "Sensitivity to the cut-off", "waldLabel": "joint Wald test",
   "waldNote": "At the chosen cut-off ({cut}): {p}. Violations left after correction (Cox test): {remaining}.",
   "none": "none",
   "vdem": "Polity2 replaced by V-Dem",
   "vdemLabel": {"one": "correlation {r} over {count} party-year", "other": "correlation {r} over {count} party-years"},
   "vdemScale": "V-Dem HR per 0.1 point of the electoral democracy index; Polity2 HR per point.",
   "modelAria": "Model", "same": "same conclusion", "different": "different conclusion"
  },
  "s05": {
   "title": "Cox against machine learning",
   "lead": "Cross-validation grouped by country ({folds} folds × {repeats} repetitions); differences tested with the corrected resampled t-test (Nadeau & Bengio, 2003).",
   "plainNone": "More flexible methods, such as random forests or boosting, do not predict better than the Cox model: none of the {count} models compared does better. All predictions remain modest: the Cox model's Harrell's C is {c}, where 0.5 means chance and 1 a perfect prediction.",
   "plainBetter": "According to the rules set in advance, at least one of the {count} models compared predicts better than the Cox model: {models}. Predictions remain modest: the Cox model's Harrell's C is {c}, where 0.5 means chance and 1 a perfect prediction.",
   "taskA": "Task A: survival per spell in power", "taskB": "Task B: yearly hazard",
   "taskLabel": "{parties} · {falls}",
   "col": {"model": "Model", "meanSd": "{metric} (mean ± SD)", "verdict": "Verdict", "variable": "Variable",
           "r2": "Linear R²", "shape": "Shape", "covariate": "Covariate", "hrCox": "Cox HR", "sameSign": "Same direction"},
   "metric": {"harrell": "Harrell's C", "ibs": "Integrated Brier ↓", "rocAuc": "ROC-AUC", "logLoss": "Log loss ↓"},
   "task": "task {task}",
   "perm": "What the models learned: permutation importance", "permLabel": "● significant in the Cox model",
   "permTipRank": "{factor}: rank {rank}", "permTipImportance": "importance {value} (SD {sd})",
   "permTipP": "p in the Cox model: {p}",
   "linear": "Are the effects linear?", "linearLabel": "partial dependence",
   "shap": "Does LightGBM point the same way as Cox?", "shapLabel": "SHAP values"
  },
  "country": {
   "title": "Do country characteristics make a difference?",
   "lead": "Notebook 04_demographics. Same protocol as the benchmark: cross-validation grouped by country ({folds} folds × {repeats} repetitions), the same parties for every model compared, decision rules set before the results.",
   "plainNone": "We added {tested} country characteristics to the model, one at a time: none improves its predictions, and the simulator's model does not change. There is not enough data to test {untestable} others: {list}.",
   "plainKept": "According to the rules set in advance, these country characteristics improve the model: {list}. They describe countries, not choices made by a party: the simulator does not offer them as settings.",
   "tested": "Variables tested",
   "testedLabel": "task A · hazard ratio for the unit shown",
   "col": {
    "block": "Block",
    "variable": "Variable",
    "unit": "Unit",
    "hr": "HR [95% CI]",
    "holm": "p (Holm)",
    "c1": "1. Holm",
    "c2": "2. Direction",
    "c3": "3. C-index",
    "c4": "4. Control",
    "kept": "Kept",
    "model": "Model",
    "cA": "C-index, task A",
    "aucB": "ROC-AUC, task B",
    "verdict": "Verdict (task A)",
    "falls": "Falls (A / B)",
    "since": "Data since",
    "reduced": "HR, reduced model (task B)", "reading": "Reading"
   },
   "testedNote": "A variable is kept only if all four conditions hold: 1. a significant effect after the Holm correction; 2. the same direction in task A (value at entry) and task B (value in the previous year); 3. a C-index gain in cross-validation (corrected p < 0.05); 4. for blocks B and C, an effect that survives the region or GDP-per-capita control. A dash marks a condition that does not apply to the block.",
   "prediction": "Prediction: the existing model and the country variables",
   "predictionLabel": "same parties within each block",
   "m0": "existing model (M0)",
   "alone": "block variables alone",
   "best": "M0 + {name} (best addition)",
   "blend": "blend of M0 and the block",
   "verdict": {
    "ref": "reference",
    "better": "better than M0",
    "worse": "worse than M0",
    "none": "no clear difference"
   },
   "untestable": "Variables without enough data",
   "untestableLabel": "outside the rules · descriptive",
   "tooFew": "too few falls",
   "link": {"none": "no clear link", "lower": "lower risk of falling", "higher": "higher risk of falling"},
   "limits": "Limits of this test"
  },
  "shocks": {
   "title": "Do shocks bring parties down?",
   "lead": "Notebook 05_shocks. Each shock of the previous year is added on its own to the existing time-varying model (task B), with errors clustered by country; cross-validation grouped by country ({folds} folds × {repeats} repetitions); decision rules set before the results.",
   "decision": "Decision for each shock",
   "decisionLabel": "task B · hazard ratio for the unit shown",
   "decisionNote": "A shock is kept only if the three conditions are met: 1. a significant effect after the Holm correction; 2. a ROC-AUC gain in cross-validation (corrected p < 0.05); 3. an effect that survives the period control (calendar year): same direction and p < 0.05.",
   "coverage": "The shocks and their data",
   "coverageLabel": "value of the previous year",
   "prediction": "Prediction: the existing model and the shocks",
   "predictionLabel": "same party-years for every model",
   "limits": "Limitations of this test",
   "col": {
    "shock": "Shock",
    "unit": "Unit",
    "hr": "HR [95% CI]",
    "p": "p",
    "holm": "p (Holm)",
    "c1": "1. Holm",
    "auc": "ROC-AUC: difference (p)",
    "c2": "2. Prediction",
    "period": "HR with the period (p)",
    "c3": "3. Period",
    "kept": "Kept",
    "definition": "Definition",
    "obs": "Party-years",
    "falls": "Falls",
    "withShock": "After a shock",
    "tested": "Tested",
    "model": "Model",
    "rocAuc": "ROC-AUC",
    "diff": "Difference with M0 (p)",
    "verdict": "Verdict"
   },
   "model": {
    "m0": "existing model (M0)",
    "alone": "shocks alone",
    "plus": "M0 + {name}",
    "blend": "blend of M0 and the shocks"
   },
   "verdict": {
    "ref": "reference",
    "better": "better than M0",
    "worse": "worse than M0",
    "none": "no clear difference"
   }
  },
  "leaders": {
   "title": "Do the party and its leader matter?",
   "lead": "Notebook 06_party_leaders. Each characteristic is added on its own to the existing model, on arrival in power (task A, static model) and in the previous year (task B, time-varying model), with errors clustered by country; cross-validation grouped by country ({folds} folds × {repeats} repetitions); decision rules set before the results.",
   "decision": "Decision for each variable",
   "decisionLabel": "hazard ratio for the unit shown",
   "decisionNote": "A variable is kept only if the four conditions are met: 1. a significant effect in task A after the Holm correction; 2. the same direction in task B; 3. a C-index gain in cross-validation (corrected p < 0.05); 4. an effect that survives the period and GDP controls: same direction and p < 0.05 in task A, same direction in task B.",
   "coverage": "The variables and their data",
   "coverageLabel": "task A: on arrival in power · task B: the previous year",
   "leader": "Which leader?",
   "leaderLabel": "Archigos · table reviewed by hand",
   "prediction": "Prediction: the existing model and the variables",
   "predictionLabel": "same parties and party-years for every model",
   "limits": "Limitations of this test",
   "col": {
    "variable": "Variable",
    "hrA": "HR (A) [95% CI]",
    "p": "p (A)",
    "c1": "1. Holm (p)",
    "c2": "2. Same sign: HR (B)",
    "c3": "3. C-index: difference (p)",
    "c4": "4. Controls: HR (A)",
    "kept": "Kept",
    "definition": "Definition",
    "partiesA": "Parties (A)",
    "fallsA": "Falls (A)",
    "obsB": "Party-years (B)",
    "fallsB": "Falls (B)",
    "tested": "Tested",
    "rule": "Leader of each party-year (task B)",
    "obs": "Party-years",
    "falls": "Falls",
    "model": "Model",
    "cA": "C-index (task A)",
    "diffA": "Difference with M0 (p)",
    "verdictA": "Verdict (A)",
    "aucB": "ROC-AUC (task B)",
    "diffB": "Difference with M0 (p)",
    "verdictB": "Verdict (B)"
   },
   "rule": {
    "archigos": "Archigos's effective leader on 31 December of the previous year",
    "first": "party's first year: leader of the table",
    "noLink": "party without a link: no leader values",
    "after": "after {year} (end of Archigos): no leader values"
   },
   "model": {
    "m0": "existing model (M0)",
    "alone": "variables alone",
    "plus": "M0 + {name}",
    "blend": "blend of M0 and the variables"
   },
   "verdict": {
    "ref": "reference",
    "better": "better than M0",
    "worse": "worse than M0",
    "none": "no clear difference"
   }
  },
  "s06": {
   "lead": "Each factor compared across the three Cox models (static, corrected, time-varying); an effect is robust if it is significant in all three.",
   "plain": {"one": "An effect is called robust only if it is significant in all three Cox models, which are built differently. This holds for a single factor: {list}.", "other": "An effect is called robust only if it is significant in all three Cox models, which are built differently. This holds for {count} factors: {list}."},
   "plainNone": "An effect is called robust only if it is significant in all three Cox models, which are built differently; no factor is."
  },
  "s07": {
   "plain": "These results describe observed associations, not causes. They rest on only {parties}, {censored} of them still in power in {year}, and some categories contain very few (clientelist strategy: {clientelist} in the static model).",
   "ml": "Limitations of the predictive benchmark"
  },
  "s08": {
   "plain": "All sources are public and cited below in their original language; the figures on this page were recomputed by the notebooks on {date}.",
   "note": "Results exported by notebooks/02_eda_and_data_processing.ipynb, final_panel.ipynb, 03_ml_survival.ipynb, 04_demographics.ipynb, 05_shocks.ipynb and 06_party_leaders.ipynb; site data built on {date}."
  }
 },
 "sim": {
  "pageTitle": "Regime simulation",
  "pageDescription": "Build an authoritarian regime, or take on a challenge: the Cox model predicts how long it stays in power.",
  "kicker": "Simulation · corrected Cox model",
  "title": "How long will your regime last?",
  "lead": "Cox model estimated on {parties} (named authoritarian parties) from {countries} ({falls}; accessions to power between {from} and {to}). Choose the features of your party when it takes power: each choice changes its risk of falling.",
  "modelInfo": {"one": "Cox · {count} replicate", "other": "Cox · {count} replicates"},
  "params": "Regime settings",
  "modeAria": "Game mode", "modeFree": "Free", "modeChallenge": "Challenges",
  "field": {
   "origin": "01 · Origin of the party", "governance": "02 · Governance strategy",
   "entry": "03 · Features at entry into power", "polity": "04 · Democracy level at entry (Polity2)",
   "horizon": "05 · Forecast horizon"
  },
  "refTag": "ref.",
  "lockedAria": "set by the challenge", "lockedNote": "Set by the challenge.",
  "switch": {"marxist": "Marxist-Leninist ideology", "conflict_entry": "Armed conflict at entry into power"},
  "switchMeta": "{parties} · risk {effect}",
  "afterCut": "(after {cut})",
  "polityLow": "−10 · closed autocracy", "polityHigh": "+10 · open regime",
  "polityHelp": "Shaded band: 90% of the parties in the sample ({range}). Each extra point multiplies the risk of falling by {effect}.",
  "run": "Run the simulation", "submit": "Submit my strategy", "reset": "Reference profile",
  "share": "Copy link",
  "shareCopied": "Link copied: it opens this profile in this language.",
  "shareFailed": "Could not copy: copy the page address instead.",
  "short": {"marxist": "Marxist", "conflict": "conflict"},
  "paramRef": "reference profile",
  "paramActive": {"one": "{count} active lever", "other": "{count} active levers"},
  "results": "Results",
  "medianLabel": "Predicted median duration",
  "medianReached": "Half of comparable parties had left power after {years}.",
  "medianNotReached": "Median not reached: more than half of comparable parties are still in power after {years}.",
  "bandBeyond": "95% band: beyond {years}.",
  "bandOpen": "95% band: from {low} to more than {years}.",
  "bandRange": "95% band: {range} {unit}.",
  "atYears": "At {years}",
  "chartTitle": "Probability of still being in power",
  "chart": {
   "aria": "Predicted survival curve over {years}", "cut": "{years}: late effects", "median": "median: {years}",
   "target": "target: {years}", "tipHead": "After {years}", "tipYours": "Your regime: {pct} ({range})",
   "tipRef": "Reference profile: {pct}", "tipHistory": "History (all parties): {pct}"
  },
  "legend": {
   "yours": "Your regime", "band": "95% band", "ref": "Reference profile",
   "history": "History (Kaplan-Meier, {count} parties)", "target": "Challenge target"
  },
  "leversTitle": "Levers: effect of each choice on the risk of falling",
  "lever": {
   "origin": "Origin: {value}", "governance": "Strategy: {value}",
   "vs": "compared with: {value}", "vsNo": "compared with: no", "vsNoConflict": "compared with: no conflict",
   "vsMedian": "compared with the median {value}", "late": "≥ {cut}: {value}",
   "refNote": "Reference profile: a dictator-created party with a policy-based strategy, no Marxist ideology and no conflict, Polity2 at the median. Change a setting to see its effect on the risk of falling.",
   "combined": "Combined risk compared with the reference profile: {early} during the first {cut} years, {late} afterwards. Left of the line, the choice protects the regime; right of it, it speeds up its fall."
  },
  "rankTitle": "Historical rank",
  "rank": {
   "label": "Historical parties already fallen by this time",
   "reached": "According to the historical curve (Kaplan-Meier, {count} parties), {pct} of parties had left power after {years}, the predicted median duration of your regime.",
   "notReached": "Your regime has a better than even chance of lasting beyond {years}; {pct} of historical parties had already fallen by then.",
   "plotAria": "Observed durations of the parties in the sample",
   "yourMedian": "your median: {years}",
   "note": "Each dot: a party of the sample and its observed duration (hollow circle: still in power in {year})."
  },
  "warningsTitle": "Reliability of the prediction",
  "warn": {
   "smallGroup": "Only {n} parties in the estimation sample have {what} (alert threshold: {threshold}): the prediction is imprecise for this choice.",
   "whatOrigin": "the origin “{value}”", "whatGov": "the strategy “{value}”",
   "what": {
    "marxist": {"yes": "a Marxist-Leninist ideology", "no": "no Marxist-Leninist ideology"},
    "conflict_entry": {"yes": "an armed conflict at entry into power", "no": "no armed conflict at entry into power"}
   },
   "unseen": "No party in the sample combines the origin “{origin}” with the strategy “{governance}” (among the {coded} parties whose strategy is coded): the prediction is an extrapolation.",
   "polity": "The chosen Polity2 score ({value}) is outside the range of 90% of the parties in the sample ({range}).",
   "horizon": "Horizon reduced from {requested} to {used}, the longest duration observed in the data."
  },
  "analogsTitle": "Closest real regimes",
  "analog": {
   "count": {"one": "{count} party compared", "other": "{count} parties compared"},
   "atlas": "see on the atlas", "notCoded": "strategy not coded", "fell": "fell in {year}", "still": "still in power",
   "note": "Real parties whose features at entry into power are closest to yours (origin, strategy, ideology, conflict, Polity2)."
  },
  "logTitle": "Simulation log", "logClear": "Clear the log",
  "log": {"empty": "Run a simulation to add it to the log and compare your strategies.", "reload": "Reload this profile"},
  "disclaimer": "Prediction from the corrected static Cox model (final_panel.ipynb, Section 6.3), computed in the browser from src/cox_static_model.json; 95% band: {replicates} replicates of a country bootstrap. The results describe associations observed between {from} and {to}, not causal effects; discrimination is modest (C-index {cindex} in cross-validation). The ARPD's “not coded” strategy is not offered: it is not a strategy.",
  "ch": {
   "intro": "Each challenge sets one or more parameters and a duration to reach. Build the rest of the regime, then submit: you win if the probability of still being in power at that duration reaches 50%.",
   "target": "{years}",
   "notPlayed": "not played yet",
   "bestAria": {"one": "Best result: {count} star", "other": "Best result: {count} stars"},
   "lockOrigin": "origin set: {value}", "lockGov": "strategy set: {value}", "lockPolity": "Polity2 set: {value}",
   "cardLabel": "Current challenge",
   "starsRule": "★ {a} · ★★ {b} · ★★★ {c}",
   "goal": "Goal: still be in power after {years}, with a probability of at least 50%.",
   "howTo": "Build your regime with the free settings, then click “Submit my strategy”.",
   "won": {"one": "Challenge won: {count} star", "other": "Challenge won: {count} stars"},
   "lost": "Challenge lost",
   "prob": "Probability of still being in power after {years}: {p} (95% band: {range}).",
   "history": "Among real parties, {pct} were still in power after {years}.",
   "medianRank": "Predicted median duration: {median}; by then, {pct} of real parties had already fallen.",
   "hint": "Hint: look for the levers that protect the regime (bars left of the line). Some rest on few parties: check the reliability of the prediction.",
   "hintMore": "For more stars, combine more protective levers.",
   "hintCapped": "For more stars, rely on better-documented choices: the reliability of the prediction shows which ones rest on few parties."
  },
  "conf": {
   "label": "Confidence: {level}",
   "level": {"high": "high", "medium": "medium", "low": "low"},
   "stars": {"one": "{count} star", "other": "{count} stars"},
   "tipHigh": "Each choice rests on at least {parties} of the sample, this combination of origin and strategy has been observed, and the Polity2 score is within the range of 90% of parties ({range}).",
   "tipLimit": "In a challenge: {stars} at most.",
   "reason": {
    "origin": "the “{value}” origin rests on {parties}",
    "governance": "the {value} strategy rests on {parties}",
    "switch": "“{value}” applies to only {parties}",
    "unseen": "no party combines the “{origin}” origin with the “{governance}” strategy",
    "polity": "Polity2 {value} is outside the range of 90% of parties ({range})"
   },
   "possible": {"one": "{count} star possible", "other": "{count} stars possible"},
   "limit": {"one": "{count}", "other": "{count}"},
   "capped": "{possible}, limited to {limit}: {reasons}.",
   "rule": "Stars also depend on the confidence of the prediction: {medium} at most when it is medium, {low} when it is low (choices made by few parties, a combination never observed).",
   "challengeMax": "This challenge gives {stars} at most: {reasons}.",
   "challengeMaxShort": "{stars} at most"
  },
  "challenges": {
   "president": {"title": "The president's party", "brief": "Your party was created by the ruler in place and governs through public policy, like the reference profile of the model. Both choices are set: play with the rest."},
   "coup": {"title": "The coup", "brief": "Your party was born of a military takeover: its origin is set. In the corrected model, its risk of falling is higher after 10 years in power than at the start."},
   "opening": {"title": "The opening", "brief": "You come to power in a fairly open regime: Polity2 is set to +6. The model links openness to a higher risk of falling."},
   "war": {"title": "Born in war", "brief": "Your party takes power during an armed conflict. In the model, this conflict has no clear effect on the risk of falling: everything depends on your other choices."},
   "independence": {"title": "Heir to independence", "brief": "Your party comes from the independence struggle, an origin linked to long survival. Aim high."}
  }
 },
 "home": {
  "pageTitle": "Authoritarian parties: why some last longer",
  "pageDescription": "Why do some authoritarian parties stay in power longer than others? Introduction, key results in charts and data sources.",
  "kicker": "Statistics project · survival analysis",
  "title": "Why do some authoritarian parties stay in power longer than others?",
  "lead": "We follow ruling parties in authoritarian regimes from the moment they take power until they fall. This site shows how long they last and what makes them last; it also lets you explore every country, year by year, and simulate a party.",
  "ctaAtlas": "Explore the globe",
  "ctaAnalyse": "See the results",
  "kpiTitle": "Key figures",
  "kpi": {
   "median": "Median time in power",
   "medianSub": "half of the parties fall sooner",
   "parties": "Parties studied",
   "countries": "Countries",
   "countriesSub": "on every continent",
   "fallen": "Lost power",
   "inPower": "Still in power",
   "inPowerSub": "in {year}"
  },
  "summaryTitle": "Key findings",
  "seeAnalysis": "See in the analysis",
  "f": {
   "survival": {
    "title": "How long?",
    "text": "Half of the parties lose power within {median}."
   },
   "factors": {
    "title": "What protects, what weakens",
    "text": "{best} divides the risk of falling by {k1}; {worst} multiplies it by {k2}.",
    "none": "No factor has a clear effect on time in power."
   },
   "prediction": {
    "title": "Can the fall be predicted?",
    "text": "Only in part: {c} on a scale from 0.5 (chance) to 1 (perfect prediction). Machine learning does not do clearly better than the Cox model.",
    "textBetter": "In part: {c} on a scale from 0.5 (chance) to 1 (perfect prediction); machine learning does slightly better."
   },
   "country": {
    "title": "Does the country matter?",
    "text": "Not measurably: none of the {tested} country characteristics tested (demography, ethnicity, religion, education…) improves the prediction.",
    "textKept": "Yes for {list}: these country characteristics improve the prediction."
   },
   "shocks": {
    "title": "Do shocks matter?",
    "text": "Not measurably: neither disasters, nor wars, nor famines, nor recessions clearly change the risk of falling the following year ({tested} shocks tested).",
    "textKept": "Yes for {list}: after this shock, the risk of falling clearly changes the following year."
   }
  },
  "exploreTitle": "Explore",
  "tools": {
   "atlas": "The globe of regimes, year by year from 1946 to 2024, with a card for every country.",
   "analyse": "The results dashboard: time in power, factors, quality of the predictions.",
   "simulation": "Build a party and see how long it would stay in power according to the model."
  },
  "sourcesTitle": "Data sources",
  "sourcesMore": "All references and licences"
 },
 "dash": {
  "kicker": "Analysis",
  "title": "The results at a glance",
  "sub": "Each card answers one question with a sentence and a chart. Full figures and methods are folded under “Show details”.",
  "more": "Show details",
  "kpi": {
   "median": "Median time in power",
   "medianSub": "95% CI: {range} years",
   "parties": "Parties studied",
   "fallen": "Lost power",
   "countries": "Countries",
   "cindex": "Quality of the predictions",
   "cindexSub": "C-index: 0.5 = chance, 1 = perfect"
  },
  "survival": {
   "title": "How long do they stay in power?",
   "answer": "Half of the parties lose power within {median}, and {pct} are still in power after {years}.",
   "all": "All",
   "longest": "longest: {group}",
   "shortest": "shortest: {group}",
   "others": "other groups"
  },
  "factors": {
   "title": "What makes them last?",
   "answer": "{best} divides the risk of falling by {k1}; {worst} multiplies it by {k2}.",
   "answerNone": "No factor has a clear effect on time in power.",
   "protect": "protects: lower risk",
   "harm": "weakens: higher risk",
   "none": "no clear effect",
   "note": "Other factors being equal. Origins are compared with “{origin}” parties, strategies with “{strategy}”."
  },
  "prediction": {
   "title": "Can their fall be predicted?",
   "answer": "Only in part: the Cox model reaches {c} on a scale from 0.5 (chance) to 1 (perfect prediction), and no machine-learning method does clearly better.",
   "answerBetter": "In part: the Cox model reaches {c} on a scale from 0.5 (chance) to 1 (perfect prediction); {models} do slightly better.",
   "groupA": "How long will the party stay? (C-index)",
   "groupB": "Will it fall within the year? (ROC-AUC)",
   "chance": "0.5 chance",
   "perfect": "1 perfect"
  },
  "country": {
   "title": "Does the country matter?",
   "answer": "No: none of the {tested} country characteristics tested improves the prediction (demography, ethnicity, religion, employment, education).",
   "answerKept": "Yes for {list}: these country characteristics improve the prediction.",
   "m0": "existing model",
   "best": "with the block's best variable",
   "tip": "{variable}: C-index {pair}, {p} (corrected test)",
   "noteNone": "The small gains shown here are not significant: they stay within the margin of chance."
  },
  "shocks": {
   "title": "Do shocks bring parties down?",
   "answer": "No: none of the {tested} shocks tested (disasters, earthquakes, wars, famines, recessions) clearly changes the risk of falling the following year.",
   "answerKept": "Yes for {list}: after this shock, the risk of falling clearly changes the following year.",
   "note": "Risk of falling in the year after the shock, other factors being equal. For disasters, the effect corresponds to ten times as many deaths per million people. Grey: no clear effect after the correction for multiple tests (Holm).",
   "pHolm": "{p} after the Holm correction"
  },
  "leaders": {
   "title": "Do the party and its leader matter?",
   "answer": "No: none of the {tested} characteristics tested (the party's age; the leader's age, background and way into power) clearly changes the risk of falling.",
   "answerKept": "Yes for {list}: other factors being equal, the risk of falling clearly changes.",
   "note": "Risk of falling according to the value on arrival in power, other factors being equal. Ages and experience: effect of 10 more years; other variables: “yes” rather than “no”. Grey: no clear effect after the correction for multiple tests (Holm).",
   "pHolm": "{p} after the Holm correction"
  },
  "data": {
   "title": "What data?",
   "answer": "{parties} in {countries}, followed until {year}.",
   "steps": {
    "all": "authoritarian regimes recorded",
    "named": "led by a party (military juntas left aside)",
    "model": "with complete data for the model",
    "falls": "of which lost power"
   }
  },
  "moreTitle": "Going further",
  "acc": {
   "conclusion": "Detailed conclusion",
   "questions": "Research questions",
   "limits": "Limitations",
   "sources": "Sources and methods",
   "glossary": "Glossary"
  }
 },
 "about": {
  "pageTitle": "About the Observatory",
  "pageDescription": "Authors, method, sources and licences of the site on the survival of authoritarian parties.",
  "kicker": "About",
  "title": "How long do authoritarian parties last, and why?",
  "lead": "This site presents a survival analysis of ruling parties in authoritarian regimes from 1946 to 2024, based on Michael K. Miller's Autocratic Ruling Parties Dataset (ARPD), complemented by V-Dem, Polity5, Archigos, REIGN, UCDP/PRIO and the Maddison database.",
  "authors": "Author",
  "pagesTitle": "What the site shows",
  "pages": {
   "atlas": "A 3D globe: the regime type of every country, every year from 1946 to 2024, with a card for each country and a list view.",
   "analyse": "The results of the notebooks: survival curves, Cox models, tests of the assumptions, robustness and a comparison with machine learning.",
   "simulation": "A game: build a regime, or take on a challenge, and the model predicts how long it would stay in power."
  },
  "methodTitle": "The method in five lines",
  "method": [
   "Unit of analysis: the period in power of a named authoritarian party of the ARPD, from its accession to its fall or to the end of the observation period; juntas without a party are excluded.",
   "Survival in power described with the Kaplan-Meier estimator; groups compared with the log-rank test.",
   "Three Cox models: static (situation at entry into power), corrected (different effects before and after 10 years in power) and time-varying (situation in the previous year); standard errors clustered by country.",
   "Tests of the assumptions (Schoenfeld test), a robustness check with V-Dem instead of Polity2, and a predictive comparison with machine learning in cross-validation grouped by country.",
   "Three further tests, with rules set before the results, add to the existing model characteristics of the countries (demography, ethnicity, religion, employment, education), shocks of the previous year (disasters, wars, famines, recessions) and characteristics of the party and its leader (cards 04 to 06 of the Analyse page).",
   "The simulation uses the corrected static Cox model, with a 95% band from a country bootstrap. The results describe associations, not causal effects."
  ],
  "sourcesTitle": "Data sources",
  "sources": {
   "arpd": "Authoritarian parties: origin, accession to power, fall (ARPD)",
   "vdem": "Regime classification, electoral democracy index, leaders' names",
   "polity": "Polity2 score",
   "archigos": "Leaders (data merge; party and leader test)",
   "reign": "Regime types (data merge)",
   "ucdp": "Armed conflicts; battle deaths since 1989 (shock test)",
   "maddison": "GDP per capita; recessions (shock test)",
   "naturalearth": "Country borders and names",
   "wpp": "Age structure of the population (country characteristics test)",
   "wdi": "Life expectancy, urbanisation, schooling, unemployment (country characteristics test)",
   "epr": "Ethnic exclusion from power (country characteristics test)",
   "qog": "Ethnic and religious fractionalization, for comparison (country characteristics test)",
   "clio": "Average years of schooling (country characteristics test)",
   "afi": "Academic freedom (country characteristics test)",
   "emdat": "Natural disasters and their victims (shock test)",
   "noaa": "Major earthquakes (shock test)",
   "prio": "Battle deaths before 1989 (shock test)",
   "famine": "Famines killing at least 100,000 people (shock test)",
   "faostat": "Food production per person (shock test)",
   "lead": "Leaders' background before taking power: military service, rebel past, education, political experience (party and leader test)",
   "wikidata": "Dated flags, party logos, people and links to Wikipedia (Atlas country card)",
   "commons": "Images of the flags, logos and portraits (Atlas country card)",
   "wikipedia": "First sentences of the articles on the parties and the leaders (Atlas country card)"
  },
  "creditsTitle": "Credits and licences",
  "credits": {
   "globe": "3D globe rendering",
   "three": "3D engine used by globe.gl",
   "naturalearth": "Country borders",
   "vdem": "Electoral democracy index, regime classes and leaders' names shown on the site",
   "fonts": "Typefaces of the site",
   "wikidata": "Links between the site's data and the articles, dates of the flags",
   "commons": "Flags, logos and portraits; author and licence given for each image in the country card",
   "wikipedia": "Extracts of the articles shown in the country card, with a link to the article"
  },
  "licence": "Licence", "publicDomain": "Public domain", "licencePerFile": "Each file under its own licence",
  "languagesTitle": "Languages",
  "languages": "The site is available in French, English and Arabic. The texts generated from the results are rewritten in each language with the same figures; in Arabic, numbers use Latin digits and charts read from left to right. The Arabic terminology still needs a review by a native speaker.",
  "built": "Site data built on {date}."
 }
};
