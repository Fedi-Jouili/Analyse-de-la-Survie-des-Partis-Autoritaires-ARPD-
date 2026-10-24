# Analyse de la Survie des Partis Autoritaires (ARPD)

An applied survival analysis of authoritarian ruling parties using the Autocratic Ruling Parties Dataset (Miller, 2020), enriched with country-year data from V-Dem, Polity5, Archigos, REIGN, UCDP/PRIO, the World Bank and the Maddison Project Database 2023 (GDP per capita since the 19th century; Bolt & van Zanden, 2024, https://doi.org/10.34894/INZBF2, CC-BY-4.0).

**Author:** Fedi Jouili

---

**Purpose**: Investigate the structural, institutional and time-varying (economy, conflict, democracy level) determinants of party longevity in non‑democratic regimes, using Kaplan–Meier estimation and Cox proportional hazards models.

**Repository layout**

`data/` is not in the repository (`.gitignore`): `data/raw/` holds the sources (downloaded as the tables below explain, or by the notebooks themselves) and the notebooks write `data/processed/`. The website does not need it: everything it shows is in `frontend/data/`.
```
data/                 (not in the repository)
  raw/          source datasets (ARPD, V-Dem, Polity5, Archigos, REIGN, UCDP, World Bank, Maddison; for
                04_demographics.ipynb: UN WPP 2024, World Bank WDI (demography; labour and education), EPR 2021, QoG,
                logged in demo_sources.json; for 05_shocks.ipynb: EM-DAT archive, NOAA significant earthquakes,
                PRIO and UCDP battle deaths, WPF famines, FAOSTAT production indices, logged in shocks_sources.json;
                for 06_party_leaders.ipynb: arpd_leaders_archigos.csv, the leader who brought each party to power,
                reviewed by hand, and lead/ (LEAD, not in the repository), logged in party_leader_sources.json;
                for the Atlas card: atlas_party_wikipedia.csv, the Wikipedia article of each ARPD party checked by hand,
                and wikimedia_atlas.json, the flags, logos, portraits and extracts collected by build_media.py)
  processed/    arpd_panel_merged.csv (party-year panel) + its data dictionary;
                ml_static.csv, ml_timevarying.csv, ml_metadata.json (modelling datasets exported for the ML notebook);
                ml_folds.csv (cross-validation fold assignments);
                ml_static_demo.csv, ml_timevarying_demo.csv, demo_*.csv, site_results_demo.json (04_demographics.ipynb);
                shocks_country_year.csv, ml_timevarying_shocks.csv, shocks_cv_taskB.csv, site_results_shocks.json
                (05_shocks.ipynb);
                ml_static_leaders.csv, ml_timevarying_leaders.csv (not in the repository), leaders_cv_taskA.csv,
                leaders_cv_taskB.csv, site_results_leaders.json (06_party_leaders.ipynb)
graph/          EDA figures: per source (01_data_merging.ipynb) and of the merged panel (panel_*.png, 02_eda_and_data_processing.ipynb)
notebooks/
  01_data_merging.ipynb             EDA of each source + merge into the party-year panel
  02_eda_and_data_processing.ipynb  exploratory analysis of the merged panel (before the models)
  final.ipynb                       spell-level analysis (one row per party)
  final_panel.ipynb                 panel analysis — main notebook
  03_ml_survival.ipynb              machine-learning benchmark of the Cox models
  04_demographics.ipynb             country characteristics (demography, public services, ethnicity, religion,
                                    employment, education, academic freedom) tested against the existing models
  05_shocks.ipynb                   shocks of the previous year (natural disasters, earthquakes, battle deaths, wars
                                    between states, famines, food production, recessions) tested against the
                                    time-varying model
  06_party_leaders.ipynb            characteristics of the ruling party and of its leader (party age, leader's age,
                                    irregular entry, military service, rebel past, university, political experience)
                                    tested against both existing models
requirements.txt        pinned package versions (see Requirements)
render.yaml             Render Blueprint: publishes frontend/ as a static website (see Website)
src/
  panel_model.py          early/late Cox helpers + survival prediction
  cph_static_model.pkl    exported Cox model (lifelines object, written by final_panel.ipynb Section 7.1)
  model_features.pkl      expected covariates, corrected covariates, time cut, Origin levels
  cox_static_model.json   portable export of the same model for the API (final_panel.ipynb Section 7.4)
  site_export.py          helpers used by the notebooks to export their results for the website (JSON)
  site_text.py            the notebooks' generated texts rewritten in French, English and Arabic for the website
  download_party_leader_data.py  downloads LEAD for 06_party_leaders.ipynb (fixed commit of peacesciencer) and
                          records the sources in data/raw/party_leader_sources.json
api/
  predictor.py            survival prediction from the JSON export (numpy only, no lifelines, no pickle)
  main.py                 FastAPI application
  requirements.txt        run-time dependencies of the API only
tests/                    pytest tests of the predictor, the API, the website (data, predictor, pages) and of
                          the outputs of 04_demographics.ipynb, 05_shocks.ipynb and 06_party_leaders.ipynb
docs/
  glossary.md             terms of the website in French, English and Arabic
frontend/                 static website in three languages (HTML, CSS, JavaScript; see Website)
  index.html  atlas.html  analyse.html  simulation.html  about.html
  assets/                 css/, js/ and i18n/ (dictionaries fr.js, en.js, ar.js)
  data/                   data files built by build_data.py (JavaScript, so the site also opens from disk)
  vendor/                 globe.gl (3D globe library, MIT licence)
  build_data.py           builds frontend/data/ from the panel, V-Dem, Natural Earth and the notebook exports
  build_media.py          collects the flags, party logos, portraits and Wikipedia extracts of the Atlas card
                          (Wikidata, Wikimedia Commons, Wikipedia) into data/raw/wikimedia_atlas.json
```

**Notebooks**

`final_panel.ipynb` (main analysis, edit it directly)
- Loads `data/processed/arpd_panel_merged.csv`, excludes juntas (`Party = "N"`), checks data integrity
- Event definition: `event = 1 − Censored` (`Censored = 1` ⇔ party still in power at the end of the data)
- Static Cox model (covariates measured at entry into power, standard errors clustered by country)
- Time-varying Cox model (GDP, Polity2 and conflict lagged by one year, time measured from accession, late entry handled)
- Robustness check (Section 5.4): V-Dem's electoral democracy index instead of Polity2 (Polity5 stops in 2018)
- Proportional-hazards diagnostics and correction: early/late effects (cut at 10 years) for the covariates flagged by the Schoenfeld test, with a joint Wald test, sensitivity to the cut, and a Cox time-interaction test
- Export of the corrected model to `src/` for the web app; interpretation, limitations, conclusion and references generated from the results

`final.ipynb` (spell-level analysis)
- Data loading and exclusion of juntas, EDA before/after cleaning, reconstruction of binary variables
- Kaplan–Meier + log‑rank, Cox models (penalized, stratified, interaction), diagnostics (Schoenfeld, residuals, VIF)
- Standard errors clustered by country (robust sandwich estimator, Lin & Wei 1989) for the Cox models, and a bootstrap that resamples whole countries; the Weibull AFT model is not clustered (not supported by lifelines for AFT models) and only its global metrics are used
- Bootstrap and Weibull AFT robustness checks, interpretation, limitations, references

`01_data_merging.ipynb`
- EDA of each source dataset (figures saved to `graph/`) and merge into `data/processed/arpd_panel_merged.csv`

`02_eda_and_data_processing.ipynb`
- Exploratory analysis of the merged panel with the definitions of the models (named parties, `event = 1 − Censored`), per spell or per party-year
- Kaplan–Meier median survival by origin, governance strategy and era (log-rank tests; for the strategy, the test compares the three coded strategies, without the parties whose strategy is not coded), coverage of the merged sources over time, macro variables in the years before a fall
- Checks behind the modelling choices (origin/ideology overlap, Polity2–V-Dem correlation, governance coding rate, missing data) and a generated synthesis for the models; figures saved as `graph/panel_*.png`

`03_ml_survival.ipynb`
- Predictive benchmark of the Cox models with machine learning; the Cox models remain the inference tool
- Uses exactly the datasets of `final_panel.ipynb` (exported in its Section 7.3), with data-integrity and leakage checks
- Evaluation: 5-fold cross-validation grouped by country (all spells of a country in the same fold), stratified on the event, repeated 10 times; fold assignments saved so every model uses the same splits
- Task A (one row per spell): Kaplan-Meier, Cox, random survival forest, gradient-boosted survival (Harrell and Uno C-index, integrated Brier score, time-dependent AUC)
- Task B (one row per party-year, discrete-time hazard): duration only, time-varying Cox, logistic regression, LightGBM (ROC-AUC, PR-AUC, Brier, log loss, calibration)
- Comparison with the corrected resampled t-test (Nadeau & Bengio, 2003); interpretation with permutation importance, partial dependence and SHAP values; generated limitations and conclusion

`04_demographics.ipynb` (country characteristics; see *Country characteristics* below)
- Three blocks of country variables, measured at entry into power (task A) and in the previous year (task B):
  - A, demography and public services: age structure, life expectancy, urbanisation, state capacity and public services from V-Dem;
  - B, ethnicity and religion: exclusion from power in EPR, V-Dem indicators of power by social group and of the state's treatment of religion;
  - C, employment, education and academic freedom: unemployment, schooling, university graduates and academic freedom (the place of "intellectuals").
- Decision rules written before any result; same protocol as `03_ml_survival.ipynb` (same folds, corrected resampled t-test), with every comparison made on the common sample of the models compared
- Models: the existing static Cox model refitted on each sample (M0), each block alone (D1, E1, S1), the existing model plus one variable (D2, E2, S2), a blend of M0 and the block model whose weight is chosen inside each training fold (D3, E3, S3), E2 with region indicators (E2r) and S2 with GDP per capita (S2p)
- Read-only for everything that exists: writes new files only, and the website's model does not change

`05_shocks.ipynb` (shocks of the previous year; see *Shocks* below)
- Seven shocks, measured in the year before each party-year (task B only: a shock is a dated event, not a characteristic at entry into power): deaths in sudden-onset natural disasters, major earthquakes, battle deaths, wars between states, famines, falls in food production, severe recessions
- Decision rules written and approved before any result; same protocol as `04_demographics.ipynb` (same folds, corrected resampled t-test, common sample), with standard errors clustered by country also in task B
- Models: the existing time-varying Cox model refitted on the common sample (M0), the shocks alone (K1), the existing model plus one shock (K2), K2 plus the calendar year (K2t, period control) and a blend of M0 and K1 (K3)
- Read-only for everything that exists: writes new files only, and the website's model does not change

`06_party_leaders.ipynb` (characteristics of the ruling party and of its leader; see *Parties and leaders* below)
- Seven variables describing the party or its leader, not the country, in both tasks: the value at entry into power (task A) and the leader of the previous year (task B)
- Decision rules written and approved before any result; same protocol as `04_demographics.ipynb` and `05_shocks.ipynb` (same folds, corrected resampled t-test, Holm correction, common sample, standard errors clustered by country in both tasks)
- Models: the existing models refitted on the common samples (M0), the variables alone (P1), the existing model plus one variable (P2), P2 plus the controls (P2c: decade of entry and GDP per capita at entry in task A, calendar year in task B) and a blend of M0 and P1 (P3)
- Read-only for everything that exists: writes new files only, and neither the website's model nor the simulation changes

---

**Requirements**
- Python 3.14 (tested on Windows)
- Packages: pinned in `requirements.txt`. Install in two steps:

```bash
python -m pip install -r requirements.txt
python -m pip install --no-deps scikit-survival==0.27.0
```

`scikit-survival` is installed without its dependencies because it requires `ecos`, which has no pre-built package for Python 3.14 and needs a C++ compiler to build. `ecos` is only used by scikit-survival's survival SVMs, which this project does not use; `pip check` will report it as missing.

**How to run**

Open any notebook and run the cells top to bottom. Each notebook locates the project root itself (`PROJECT_ROOT`), so it works whether Jupyter is launched from the project root or from `notebooks/`. No path needs to be edited.

| Notebook | Reads | Writes |
|---|---|---|
| `01_data_merging.ipynb` | `data/raw/*.csv` | `data/processed/arpd_panel_merged.csv`, `data/processed/arpd_panel_data_dictionary.csv`, figures in `graph/` |
| `02_eda_and_data_processing.ipynb` | `data/processed/arpd_panel_merged.csv` | figures `graph/panel_*.png`, `data/processed/site_results_eda.json` |
| `final.ipynb` | `data/raw/ARP_dataset_cleaned.csv` (or `ARP_DATA_PATH` if set) | `data/processed/ARP_dataset_filled.csv`, `ARP_dataset_clean.csv`, `ARP_dataset_model.csv` |
| `final_panel.ipynb` | `data/processed/arpd_panel_merged.csv`, `ml_results_taskA.csv` (Section 7.4) | `src/cph_static_model.pkl`, `src/model_features.pkl`, `src/cox_static_model.json`, `data/processed/ml_static.csv`, `ml_timevarying.csv`, `ml_metadata.json`, `site_results_panel.json` |
| `03_ml_survival.ipynb` | `data/processed/ml_static.csv`, `ml_timevarying.csv`, `ml_metadata.json`, `arpd_panel_merged.csv` | `data/processed/ml_folds.csv`, `ml_results_taskA.csv`, `ml_results_taskB.csv`, `ml_oof_taskB.csv`, `site_results_ml.json` |
| `04_demographics.ipynb` | `data/processed/ml_static.csv`, `ml_timevarying.csv`, `ml_metadata.json`, `ml_folds.csv`, `ml_results_taskA.csv`, `ml_results_taskB.csv`, `arpd_panel_merged.csv`; `data/raw/V-Dem-CY-Full+Others-v16.csv`, `worldbank.csv`; downloads the UN, World Bank, EPR and QoG files into `data/raw/` if they are missing | `data/processed/ml_static_demo.csv`, `ml_timevarying_demo.csv`, `demo_country_year.csv`, `demo_epr_mapping.csv`, `demo_cv_taskA.csv`, `demo_cv_taskB.csv`, `site_results_demo.json`; `data/raw/demo_sources.json` |
| `05_shocks.ipynb` | `data/processed/ml_timevarying.csv`, `ml_metadata.json`, `ml_folds.csv`, `ml_results_taskB.csv`, `arpd_panel_merged.csv`; `data/raw/V-Dem-CY-Core-v16.csv`, `UcdpPrioConflict_v26_1.csv`, `mpd2023_web.xlsx`, the UN WPP file; downloads the EM-DAT, NOAA, PRIO, UCDP, World Peace Foundation and FAOSTAT files into `data/raw/` if they are missing | `data/processed/shocks_country_year.csv`, `ml_timevarying_shocks.csv`, `shocks_cv_taskB.csv`, `site_results_shocks.json`; `data/raw/shocks_sources.json` |
| `06_party_leaders.ipynb` | `data/processed/ml_static.csv`, `ml_timevarying.csv`, `ml_metadata.json`, `ml_folds.csv`, `ml_results_taskA.csv`, `ml_results_taskB.csv`, `arpd_panel_merged.csv`; `data/raw/arpd_leaders_archigos.csv`, `arch_annual.csv`, `party_leader_sources.json` and `lead/LEAD.csv` (runs `src/download_party_leader_data.py` if LEAD is missing) | `data/processed/ml_static_leaders.csv`, `ml_timevarying_leaders.csv`, `leaders_cv_taskA.csv`, `leaders_cv_taskB.csv`, `site_results_leaders.json` |

Run order: `01_data_merging.ipynb` → `02_eda_and_data_processing.ipynb` → `final_panel.ipynb` → `03_ml_survival.ipynb` → `04_demographics.ipynb` → `05_shocks.ipynb` → `06_party_leaders.ipynb` (`final.ipynb` is independent: it reads the raw ARPD file). Section 7.4 of `final_panel.ipynb` reads the cross-validated C-index from `03_ml_survival.ipynb`'s results (`ml_results_taskA.csv`): after re-running the ML notebook, re-run `final_panel.ipynb` to refresh `src/cox_static_model.json`, then run the tests.

**Country characteristics**

`04_demographics.ipynb` tests whether characteristics of the country add information to the existing models. It has three blocks:
- block A covers demography and public services;
- block B covers ethnicity and religion;
- block C covers employment, education and academic freedom.

Block C was added after blocks A and B had been analysed; its rules were written before any estimate on its variables.

A candidate first needs enough data: at least 120 falls in each task, and enough falls in its block's common sample for its models to keep 10 falls per parameter. A variable is then kept only if:
- its Holm-adjusted p-value over all candidates of the three blocks is below 0.05, with errors clustered by country;
- its effect has the same direction in tasks A and B;
- the existing model plus this variable beats the existing model's cross-validated C-index (corrected p < 0.05);
- for blocks B and C, the effect survives region indicators (B) or GDP per capita (C).

Results of the current run:
- **No variable is kept**, so the final model is not fitted.
- Academic freedom comes closest: its effect is significant after correction and survives the GDP control, but it does not significantly improve the cross-validated C-index.
- Unemployment cannot be tested: the harmonised ILO series start in 1991, and leave fewer than 80 falls.
- Average years of schooling, tertiary enrolment and the share of graduates have too little data. They get descriptive estimates only.

These variables describe countries, not choices of a party: none of them is an input of the simulation, and the website's model does not change. The results describe associations, not causes. No variable identifies a country's majority religion or a specific ethnic or religious group. The notebook uses only measures of diversity, of exclusion from power and of the state's treatment of religion. The results are shown in the three languages on the Analyse page (card 04, "Does the country matter?", with the full tables under "Show details") and summed up on the home page.

| Source | Version | File in `data/raw/` | Citation | Terms of use |
|---|---|---|---|---|
| United Nations, World Population Prospects, population by 5-year age group, medium variant (https://population.un.org/wpp/) | 2024; estimates 1950–2023 (projections not used) | `WPP2024_PopulationByAge5GroupSex_Medium.csv.gz` (30 MB) | United Nations, Department of Economic and Social Affairs, Population Division (2024). *World Population Prospects 2024* | CC BY 3.0 IGO |
| World Bank, World Development Indicators, public API (https://api.worldbank.org/v2/): `SP.DYN.LE00.IN`, `SE.SEC.ENRR`, `SP.URB.TOTL.IN.ZS` | downloaded 2026-10-14 (data updated 2026-10-08) | `worldbank_wdi_demography.csv`; the Gini index (`SI.POV.GINI`) comes from the existing `worldbank.csv` | World Bank (2026). *World Development Indicators* | CC BY 4.0 |
| World Bank, World Development Indicators, public API: unemployment, total and ages 15-24 (`SL.UEM.TOTL.ZS`, `SL.UEM.1524.ZS`, ILO modelled estimates, from 1991), unemployment with advanced education (`SL.UEM.ADVN.ZS`), tertiary enrolment (`SE.TER.ENRR`), share of adults 25+ with at least a bachelor's degree (`SE.TER.CUAT.BA.ZS`) | downloaded 2026-10-15 | `worldbank_wdi_labour_education.csv` | World Bank (2026). *World Development Indicators*; International Labour Organization, ILOSTAT, *ILO modelled estimates* | CC BY 4.0 |
| V-Dem Country-Year Full+Others: `v2stfisccap`, `v2clrspct`, `v2peedueq`, `v2pehealth`, `v2pepwrsoc`, `v2clrelig`, `v2csrlgrep`, `v2xca_academ` (Academic Freedom Index), `e_peaveduc` (average years of education of people aged 15+, from Clio-Infra; V-Dem interpolates missing years and the series stops in 2010) | v16 | `V-Dem-CY-Full+Others-v16.csv` (not in the repository, see Website) | Coppedge et al. (2026), https://doi.org/10.23696/vdemds26; Spannagel & Kinzelbach (2022), *Quality & Quantity*; Clio-Infra (2018), http://www.clio-infra.eu/ | CC BY-SA 4.0 (V-Dem); the Clio-Infra series is cited as V-Dem asks |
| ETH Zurich, Ethnic Power Relations, EPR Core (https://icr.ethz.ch/data/epr/core/) | 2021 (1946–2021) | `EPR-2021.csv` (not in the repository) | Vogt, M., Bormann, N.-C., Rüegger, S., Cederman, L.-E., Hunziker, P., & Girardin, L. (2015). Integrating Data on Ethnicity, Geography, and Conflict: The Ethnic Power Relations Data Set Family. *Journal of Conflict Resolution*, 59(7), 1327–1342. https://doi.org/10.1177/0022002715591215 | free download, citation requested; no explicit licence on the download page |
| Quality of Government Standard Dataset, cross-section (https://www.gu.se/en/quality-government), for the fractionalization indexes of Alesina et al. (2003), `al_ethnic2000` and `al_religion2000`, used for comparison only | Jan26 | `qog_std_cs_jan26.csv` (not in the repository) | Teorell et al. (2026), *The Quality of Government Standard Dataset*, version Jan26, https://doi.org/10.18157/qogstdjan26; Alesina, A., Devleeschauwer, A., Easterly, W., Kurlat, S., & Wacziarg, R. (2003). Fractionalization. *Journal of Economic Growth*, 8(2), 155–194 | academic, non-commercial use; redistribution not allowed; the data remain the property of their original source |

*Downloads.* None of the files needs a registration or a form. The notebook downloads them once and records each file's URL, date, size and SHA-256 hash in `data/raw/demo_sources.json`. A later run checks the files on disk against these hashes. The EPR and QoG files are excluded by `.gitignore` because their terms do not allow redistribution; the notebook downloads them again when they are missing, and warns if the new copy no longer matches the recorded hash. The files `demo_country_year.csv`, `ml_static_demo.csv` and `ml_timevarying_demo.csv` in `data/processed/` contain the Alesina et al. values taken from QoG (columns `al_ethnic2000*`, `al_religion2000*`) and measures computed from EPR: they are excluded by `.gitignore` too, and the notebook writes them again. The website copies only result tables and texts from `site_results_demo.json` (`frontend/build_data.py`, `demo_results`), never these country-year values.

*Country codes.* Values are merged on COW code and year, measured at entry into power (task A) and in the previous year (task B), with no imputation; task B carries the last known value forward within a spell, as in `final_panel.ipynb`.
- ARPD's Polity codes are translated as in `01_data_merging.ipynb`, plus 769 → 770 (Pakistan, three party-years from 1947 to 1949).
- ISO3 codes (United Nations, World Bank, QoG) are mapped to COW through V-Dem.
- EPR's Gleditsch-Ward codes differ from COW for three states: Germany (260, then 255 from 1991), Yemen (678, then 679 from 1991) and Serbia (GW 340 from 2006 is COW 345).
- Series at today's borders are not used for the USSR and Yugoslavia (until 1991), Pakistan before 1972 and North Vietnam (until 1975).

*How to rerun.*
1. Make sure the V-Dem Full+Others file is in `data/raw/`. The first run also needs internet access, for about 40 MB of downloads.
2. Open `notebooks/04_demographics.ipynb` and run all cells top to bottom (`RANDOM_STATE = 42`; from 5 to 20 minutes depending on the machine, mostly for the cross-validation). Alternatively, run `python -m nbconvert --to notebook --execute --inplace notebooks/04_demographics.ipynb`.
3. Rebuild the website's data with `python frontend/build_data.py`: card 04 of the Analyse page and the home page read `site_results_demo.json`.
4. Run `python -m pytest tests/test_demographics.py tests/test_frontend_build.py`.

*Tests.* `tests/test_demographics.py` is skipped until the notebook has run. It checks:
- the merge keys and country-years are unique;
- the columns of `ml_static.csv` and `ml_timevarying.csv` are unchanged in the new files;
- each value is the one at entry or in the previous year;
- every ARPD country is in the EPR mapping, and every ARPD country-year that EPR covers has a value (except years of state collapse);
- shares and indexes lie in their range, there is one fractionalization value per country, and the unemployment and education series start and stop where their sources do;
- no new column beyond the expected ones, and regions follow the COW ranges;
- the coverage table, samples and decision table match the files, including the GDP control of block C;
- a variable removed from its block would indeed leave too few falls per parameter;
- every compared model is evaluated on the same spells;
- the reference model reproduces `03_ml_survival.ipynb`;
- the events-per-parameter rule holds, including for the descriptive models of the untestable variables;
- the exported texts in French, English and Arabic are current and contain no dataset code;
- no candidate appears in the website's model;
- the downloads match their recorded hashes, and the files with QoG or EPR values are listed in `.gitignore`.

**Shocks**

`05_shocks.ipynb` tests whether a shock in the previous year changes the risk that an authoritarian party loses power the following year. It uses task B only (a shock is a dated event, not a characteristic at entry into power), and its Holm correction is a family separate from that of `04_demographics.ipynb`, whose results do not change. The definitions and the rules were written and approved on 2026-10-16, before any estimate.

| | Shock (value of the previous year) | Source |
|---|---|---|
| D1 | deaths in sudden-onset natural disasters (earthquakes, volcanoes, landslides, storms, extreme temperatures, floods, wildfires; droughts and epidemics excluded) per million people, log(1 + x) | EM-DAT |
| D2 | earthquake of magnitude 7.5 or more in the country (NOAA lists every such earthquake, with or without damage) | NOAA NCEI |
| D3 | battle deaths in armed conflicts located in the country, per million people, log(1 + x) | PRIO (1946–1988), then UCDP, if the two series agree |
| D4 | the country is one of the two main sides of an armed conflict between states (at least 25 battle deaths in the year) | UCDP/PRIO |
| D5 | famine killing at least 100,000 people under way in the country | World Peace Foundation (via Our World in Data) |
| D6 | fall of at least 10% in one year in the gross food production index per person | FAOSTAT |
| D7 | fall of at least 5% in one year in GDP per capita | Maddison |

Rules:
- A shock needs at least 120 falls, and the common sample must keep 10 falls per parameter for the largest planned model (the 13 covariates of the existing time-varying model, the shock and the calendar year: 15 parameters); otherwise the least covered shock leaves the block.
- A shock is kept only if: (1) its Holm-adjusted p-value is below 0.05 in the existing time-varying model plus the shock, with errors clustered by country; (2) it improves the cross-validated ROC-AUC of the existing model (corrected p < 0.05); (3) its effect survives the period control (calendar year): same direction and p < 0.05.
- Differences with notebook 04: the condition "same direction in tasks A and B" disappears (task B only); the GDP control is not needed, since GDP per capita of the previous year is already in the existing model, and is replaced by the period control (disasters are better and better recorded, and the risk of falling changed after the Cold War). Hazard ratios come from the time-varying model fitted with delayed entry, which gives the same coefficients as the project's model (largest gap 1e-5) with errors clustered by country.
- Event datasets give 0 in the years they cover; a series without a value stays missing; no value is carried forward. An event counts for the state that existed at its date (an earthquake in Turkmenistan in 1946 for the USSR, the famine in today's South Sudan in 1988–1998 for Sudan); in a divided country (Vietnam 1954–1975, Germany 1949–1990), an event with deaths and no precise location makes the value missing for both states; dependent territories count for no party. Population: UN WPP from 1950 to 2023, the sum of today's territories for dissolved states, Maddison before 1950.

Results of the current run:
- **No shock is kept**: none meets the three conditions, and none has p < 0.05 even before correction.
- Closest: sudden-onset natural disasters, HR 1.33 for ten times as many deaths per million people (95% CI 0.96–1.83; p = 0.083 with errors clustered by country, 0.060 without clustering as in `final_panel.ipynb`), with no ROC-AUC gain (+0.002, corrected p = 0.56) and p = 0.080 with the period control.
- Major earthquake HR 0.72 (p = 0.52), war between states 1.07 (p = 0.85), famine 0.88 (p = 0.84), severe recession 1.34 (p = 0.19).
- The shocks alone predict worse than the existing model (ROC-AUC 0.599 against 0.676); blended with it, there is no clear difference.
- Battle deaths cannot be tested: PRIO and UCDP agree with a correlation of 0.79 conflict by conflict over 1989–2008, below the threshold of 0.8 set before the results, so the series starts in 1989 and covers only 95 falls.
- The food production shock cannot be tested: FAOSTAT publishes its indexes only for today's countries, from their creation; with it, the common sample would keep 148 falls, 9.9 per parameter.
- Common sample: 3,563 party-years from 1947 to 2023, with 190 of the 194 falls.

Shocks describe what happens to a country, not choices of a party: none is an input of the simulation, and the website's model does not change. The results are shown in the three languages on the Analyse page (card 05, "Do shocks bring parties down?", with the full tables under "Show details") and summed up on the home page.

| Source | Version | File in `data/raw/` | Citation | Terms of use |
|---|---|---|---|---|
| EM-DAT, validated archive of the database (CRED, UCLouvain; https://doi.org/10.14428/DVN/I0LTPH) | v2, published 2026-04-30 (events 1900–2024) | `260430_emdat_archive.xlsx` (not in the repository) | Delforge et al. (2025), *International Journal of Disaster Risk Reduction*; CRED / UCLouvain | CC BY-NC-ND 4.0: non-commercial use, no distribution of adapted data |
| NOAA NCEI, Global Significant Earthquake Database, HazEL API (https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes) | downloaded 2026-10-16 (1940–2025) | `noaa_significant_earthquakes.csv` | NCEI/WDS, https://doi.org/10.7289/V5TD9V7K | no licence stated; U.S. government data; citation requested |
| PRIO Battle Deaths Dataset (https://www.prio.org/data/1) | 3.1 (1946–2008) | `PRIO_BattleDeaths_v3.1.xls` (not in the repository) | Lacina & Gleditsch (2005), *European Journal of Population*, 21(2–3) | no licence stated |
| UCDP Battle-Related Deaths Dataset (conflict level) and UCDP's table of old and new conflict identifiers (https://ucdp.uu.se/downloads/) | 26.1 (1989–2025) | `ucdp-brd-conf-261-csv.zip`, `ucdp_translate_conf.csv` | Davies, Pettersson & Öberg (2026), *Journal of Peace Research*, 63(4) | CC BY 4.0 |
| World Peace Foundation, *Historic Famines* (100,000 deaths or more), via Our World in Data (https://ourworldindata.org/grapher/famines-and-the-deaths-in-them) | WPF 2025 (Our World in Data update of 2025-01-17) | `owid_famines.csv`, `owid_famines.metadata.json` (not in the repository) | World Peace Foundation (2025), processed by Our World in Data | Our World in Data: CC BY 4.0; WPF: no licence stated, citation requested |
| FAOSTAT, Production Indices (https://www.fao.org/faostat/) | update of 2026-05-11 (1961–2024) | `Production_Indices_E_All_Data_(Normalized).zip` | FAO (2026) | CC BY 4.0 |
| UCDP/PRIO Armed Conflict Dataset; Maddison Project Database; UN WPP (files already in `data/raw/`) | 26.1; 2023; 2024 | | | CC BY 4.0; CC BY 4.0; CC BY 3.0 IGO |

*Downloads.* None of the files needs a registration or a form: the EM-DAT archive is a public file of UCLouvain's repository, and the notebook stops if a server returns anything other than the expected file. The notebook downloads the files once and records each file's URL, date, size and SHA-256 hash in `data/raw/shocks_sources.json`. The EM-DAT, PRIO and WPF files, and the two processed tables that contain values derived from EM-DAT (`shocks_country_year.csv`, `ml_timevarying_shocks.csv`), are excluded by `.gitignore`; the notebook downloads the sources again when they are missing. The website copies only result tables (`frontend/build_data.py`, `shocks_results`). Reading the PRIO file needs `xlrd` (in `requirements.txt`).

*How to rerun.*
1. Make sure `data/raw/V-Dem-CY-Core-v16.csv` is present. The first run also needs internet access, for about 25 MB of downloads.
2. Run `notebooks/05_shocks.ipynb` top to bottom (a few minutes), or `python -m nbconvert --to notebook --execute --inplace notebooks/05_shocks.ipynb`.
3. Rebuild the website's data with `python frontend/build_data.py`: card 05 of the Analyse page and the home page read `site_results_shocks.json`.
4. Run `python -m pytest tests/test_shocks.py tests/test_frontend_build.py`.

*Tests.* `tests/test_shocks.py` is skipped until the notebook has run. It checks:
- the columns of `ml_timevarying.csv` are unchanged in the new file;
- each party-year gets the shock of the previous year only: never a later value, never a value carried forward;
- binary shocks are 0 or 1, death rates are non-negative, and each source covers exactly its years;
- well-known events are attributed to the state of their date (Kamchatka 1952, the Sahel famine, East Timor, today's South Sudan, East Pakistan 1970);
- the coverage table, the screening, the common sample and the splice rule match the files;
- every compared model is evaluated on the same party-years, and the decision table follows the three rules;
- the export contains no country-year table;
- the exported texts in French, English and Arabic are current and contain no dataset code;
- no shock appears in the website's model;
- the downloads match their recorded hashes, and the files that must not be redistributed are listed in `.gitignore`.

**Parties and leaders**

`06_party_leaders.ipynb` tests whether seven characteristics of the ruling party and of its leader add information beyond the existing models, in both tasks: the value at entry into power (task A, static model) and the leader of the previous year (task B, time-varying model). Its Holm correction is a family separate from those of notebooks 04 and 05. The variables, their measurement and the rules were written on 2026-10-21 (control step) and approved on 2026-10-23, before any estimate.

| Variable | Definition | Source | Hazard ratio for |
|---|---|---|---|
| `party_age` | age of the party when it comes to power (entry year − founding year); the same value in task B, since on the time-in-power scale the age of the previous year gives the same coefficient | ARPD | 10 more years |
| `leader_age` | age of the leader | Archigos | 10 more years |
| `leader_irregular` | the leader came to power irregularly (coup, revolt, assassination…: Archigos entry "Irregular"; "Regular" and "Foreign Imposition" count as 0) | Archigos | yes rather than no |
| `leader_military` | military service before taking power | LEAD | yes rather than no |
| `leader_rebel` | member of a rebel group before taking power | LEAD | yes rather than no |
| `leader_university` | university education (LEAD `leveledu` ≥ 2) | LEAD | yes rather than no |
| `leader_experience` | years of political experience before taking power | LEAD | 10 more years |

*Which leader.*
- Task A: the leader who brought the party to power, in `data/raw/arpd_leaders_archigos.csv` (one row per party of the static model: 224). The automatic link is the Archigos effective leader in office on 31 December of the entry year (ARPD country codes translated to COW, then to Archigos, which keeps 678 for unified Yemen). Every row was reviewed by hand on 2026-10-23, with Archigos and Wikipedia. The link goes to (1) the party's own leader, if he is an Archigos leader in the entry year or the next one; otherwise (2) the ruler who created the party or made it the ruling party, or the leader of the coup that installed it; otherwise (3) no link. The automatic link is confirmed for 209 parties (93%) and replaced by another leader for 9: for example Bourguiba instead of Lamine Bey for the Neo-Destour in 1956, Gottwald instead of Beneš for the Czechoslovak communists in 1947, and Chiang Kai-shek instead of Li Zongren for the Kuomintang in Taiwan in 1949. It is removed for 6 parties whose effective leaders belonged to another camp or to none: ARENA in 1981, the Latvian and Lithuanian communists in 1991, the NDP of Suriname in 1990, the Republican Party of Armenia in 1999 and the PAIGC in 2004. Each row gives its reason (`review`, `note`).
- Task B: the Archigos effective leader on 31 December of the previous year. Before the arrival of the leader of the table (the party's first year), that leader is used, not the predecessor from the former regime (52 party-years). The 6 parties without a link have no leader values (40 party-years, 4 falls), and neither do the years after 2015, when Archigos ends (285 party-years, 15 falls). Nothing is carried forward from one leader to another. The 22 parties of task B only (in power before 1946, or absent from the static model) take the Archigos leader of their entry year.

Rules:
- Each variable needs at least 120 falls in each task. The common sample needs at least 10 falls per parameter for the largest planned model (15 parameters in each task: the existing covariates, the variable and the controls), i.e. 150 falls; otherwise the least covered variable leaves the block.
- A variable is kept only if: (1) its Holm-adjusted p-value is below 0.05 in the existing static model plus the variable (task A, errors clustered by country); (2) its effect has the same direction in task B (time-varying model with delayed entry, errors clustered by country); (3) it improves the cross-validated Harrell's C of the existing model (corrected p < 0.05); (4) its effect survives the controls: same direction and p < 0.05 in task A with the decade of entry and the log GDP per capita at entry, same direction in task B with the calendar year.
- If no variable is kept, the conclusion was written in advance: no characteristic of the party or of the leader tested adds information beyond the existing model, and neither the website's model nor the simulation changes. A kept variable would become a choice of the simulation only if this were explicitly accepted after reading the results.

Results of the current run:
- **No variable is kept**: none meets the four conditions, and none has p < 0.05 even before correction (Holm-adjusted p = 1.000 for all seven).
- Closest: military service of the leader, HR 0.82 (95% CI 0.56–1.21; p = 0.32) in task A and 0.89 (p = 0.58) in task B.
- The others, in task A: party age 0.96 per 10 years (p = 0.61), leader's age 1.02 (p = 0.79), irregular entry 1.08 (p = 0.63; 0.98 in task B, the opposite direction), rebel past 0.89 (p = 0.45), university 1.06 (p = 0.79), political experience 1.02 per 10 years (p = 0.81).
- No variable improves the existing model's C-index (largest gain +0.003, corrected p = 0.63). The variables alone predict less well than the existing model (Harrell's C 0.545 against 0.613 in task A; ROC-AUC 0.585 against 0.649 in task B); blended with it, there is no clear difference.
- All seven are testable: common samples of 175 parties (152 falls) in task A and 3,064 party-years (159 falls) in task B. No variable violates the proportional-hazards assumption.

None of these characteristics is an input of the simulation, and the website's model does not change. The results are shown in the three languages on the Analyse page (card 06, "Do the party and its leader matter?", with the full tables under "Show details"); their texts are written by `src/site_text.py` (`leaders_texts`), called by Section 10 of the notebook.

| Source | Version | File | Citation | Terms of use |
|---|---|---|---|---|
| LEAD, *Leader Experience and Attribute Descriptions*: the 11 variables of the authors' replication file, one row per Archigos leader, as distributed by the R package peacesciencer (https://github.com/svmiller/peacesciencer) | LEAD v1 (1875–2004); `data/LEAD.rda` at commit `2bb3321` (2023-03-22) | `data/raw/lead/LEAD.rda`, `LEAD.csv` (not in the repository) | Ellis, Horowitz & Stam (2015), *International Interactions*, 41(4); Miller (2022), *Conflict Management and Peace Science*, 39(6) | no licence stated for the data (the package is GPL-2): not redistributed |
| Archigos (https://www.rochester.edu/college/faculty/hgoemans/data.htm) | 4.1 (until 2015-12-31), annual version | `data/raw/arch_annual.csv` (already present; the origin of this CSV version is not documented in the repository) | Goemans, Gleditsch & Chiozza (2009), *Journal of Peace Research*, 46(2) | no licence stated; citation requested |

*Sources not used.* They were checked at the control step and recorded in `party_leader_sources.json`. V-Party v2 (download behind a form asking for an e-mail address; at most 106 falls at entry into power, even perfectly linked), DPI 2023 (CC BY 4.0, direct links; at most 99) and PLAD v7 (CC0, Harvard Dataverse; at most 68) cannot reach the 120 falls required at entry.

*Downloads.* `python src/download_party_leader_data.py` downloads `LEAD.rda` from the GitHub repository of peacesciencer at a fixed commit, converts it to CSV with `pyreadr` (in `requirements.txt`) and records the URL, date, version, licence, size and SHA-256 of each file in `data/raw/party_leader_sources.json`. It reads the host's `robots.txt` first, sends one request at a time (at least one second apart), waits as long as `Retry-After` asks on 429 or 503, names the project in its User-Agent without personal data and fills no form. A link that answers with an HTML page instead of the file stops it, and so does a file whose SHA-256 differs from the one recorded. `data/raw/lead/` and the two tables with LEAD values (`ml_static_leaders.csv`, `ml_timevarying_leaders.csv`) are excluded by `.gitignore`. The export `site_results_leaders.json` contains result tables and the website's texts only: no country-year, party-year, leader or LEAD value. The website copies the tables it shows from it (`frontend/build_data.py`, `leaders_results`).

*How to rerun.*
1. `python src/download_party_leader_data.py` (the notebook also runs it if LEAD is missing).
2. Run `notebooks/06_party_leaders.ipynb` top to bottom (about two minutes), or `python -m nbconvert --to notebook --execute --inplace notebooks/06_party_leaders.ipynb`.
3. Rebuild the website's data with `python frontend/build_data.py`: card 06 of the Analyse page reads `site_results_leaders.json`.
4. Run `python -m pytest tests/test_party_leaders.py`.

*Tests.* `tests/test_party_leaders.py` checks:
- the table of leaders: one reviewed row per party of the static model (224), every link an Archigos leader of the same country in office in the entry year or the next one, and the known cases read in Archigos itself (Castro for Cuba 1959, Bourguiba for Tunisia 1956, Saleh for Yemen 1993);
- the downloads: a fixed commit, sizes and hashes as recorded, the sources not used with their reason, no personal data in the User-Agent, the files with LEAD values listed in `.gitignore`;
- the notebook's outputs (skipped until it has run): the columns of `ml_static.csv` and `ml_timevarying.csv` unchanged; the leader of each task follows the rules (the leader of the table in task A; the Archigos leader on 31 December of the previous year in task B, nothing after 2015, nothing carried forward); LEAD values copied without recoding; coverage, screening and common samples; every compared model evaluated on the same rows; the decision table follows the four rules;
- the export contains no country-year, party-year, leader or LEAD value, and none of the variables appears in the website's model;
- the website's texts in the three languages are those that `src/site_text.py` rebuilds from the export, with no variable code, no leader's name, no Archigos identifier, and Latin digits in Arabic.

**API**

The API serves the corrected static Cox model of `final_panel.ipynb` (Section 6.3) from `src/cox_static_model.json`. It needs only `api/requirements.txt` (numpy, FastAPI, uvicorn, pydantic): it never loads lifelines or a pickle. Start it from the project root:

```bash
python -m uvicorn api.main:app --reload
```

Optional environment variables: `ARPD_MODEL_PATH` (path of the JSON export, default `src/cox_static_model.json`) and `ARPD_CORS_ORIGINS` (comma-separated allowed origins; CORS is disabled by default). Interactive documentation: http://127.0.0.1:8000/docs.

| Endpoint | Returns |
|---|---|
| `GET /health` | status, schema version, export date |
| `GET /model` | form definition (origin and governance levels, Polity2 range, horizon), default profile, support counts (training spells per choice), sample size, C-index values, limits of the model (in French) |
| `POST /predict` | survival curve at 0..horizon years, 95% band (country bootstrap, 500 replicates), median survival, notes and warnings |

Example request (all fields required except `horizon`, default 30; strict types, unknown fields rejected with 422):

```json
{"origin": "Communist", "governance": "Repressive", "marxist": true,
 "conflict_entry": false, "polity2_entry": -7, "horizon": 30}
```

Response (abridged):

```json
{"times": [0, 1, "...", 30], "survival": [1.0, "...", 0.51],
 "band": {"level": 0.95, "lower": [1.0, "...", 0.319], "upper": [1.0, "...", 0.696], "replicates": 500},
 "median": {"years": null, "reached": false,
            "text": "Médiane non atteinte : plus de la moitié des partis comparables sont encore au pouvoir après 30 ans."},
 "horizon_requested": 30, "horizon_used": 30, "notes": [], "warnings": []}
```

The governance strategy is one of `Policy-Based`, `Repressive`, `Clientelist`: the "Non code" category of the data is never offered (it is not a strategy) and is fixed to 0. Warnings flag choices backed by fewer than 20 training spells (e.g. `Clientelist`), origin × strategy combinations absent from the data, and Polity2 values outside the 5th–95th percentile.

To regenerate the export, re-run `final_panel.ipynb` (Section 7.4 checks that the JSON reproduces the lifelines model). Tests: `python -m pytest tests` (they compare the API predictor with the lifelines model on 100 random profiles).

**Website**

A static website (HTML, CSS and JavaScript, no framework and no server-side code) in **French, English and Arabic** presents the project in five pages:

| Page | Content |
|---|---|
| `index.html` · Home | The entry page, written for readers new to the topic: the question in one sentence, a short introduction, five key figures (median time in power, parties, countries, share that lost power, parties still in power), the summary of the results in five small charts (how long parties last, what protects and what weakens, whether the fall can be predicted, whether the country matters, whether shocks matter), each linked to its card on the Analyse page, links to the three tools, and the data sources. Every figure and sentence is built from the notebooks' exports, like the Analyse page. |
| `atlas.html` · Atlas | 3D globe (drag to rotate, scroll to zoom) with a year slider from 1946 to 2024. Countries are coloured by regime type: party regime, military regime, monarchy (ARPD), other autocracy (V-Dem, e.g. personal rule or autocracies after 2015), democracy, non-sovereign territory. Two other readings colour countries by the age of the regime or by V-Dem's electoral democracy index; "relief" raises each autocracy by its time in power. The ARPD tracks parties only: all the years of a country without a ruling party form a single row (`Party = "N"`), which can cover several regimes (Libya: Idris's monarchy, Qaddafi's personalist regime, civil war). The globe splits these periods by the regimes of Geddes, Wright & Frantz (`gwf_casename` in the panel): the type is GWF's when it translates (monarchy, personalist, military, civil war, occupation, transition), otherwise the panel's precise type (theocracy, failed state…), otherwise "unclassified"; after GWF's last year the previous regime continues. No accession or end mode is shown for these periods, since the raw ARPD gives none. These periods are excluded from every analysis. Two periods that the ARPD (which stops in 2015) leaves open are closed in `build_data.py` (`NO_PARTY_EXCEPTIONS`, with sources): Sri Lanka's personalist period ends in 2015 (Rajapaksa's defeat), after which V-Dem takes over, and the Taliban form a new period, a theocracy, from 2021. Borders follow the UN position: Crimea is part of Ukraine in every year, and Western Sahara is one territory, distinct from Morocco: a Spanish colony until 1975, then a non-self-governing territory, as its card says. For annexations that were not recognised (Estonia, Latvia and Lithuania 1946–1991, East Timor 1976–1999), the card says "annexed by the USSR (annexation not recognised)" or "annexed by Indonesia (annexation not recognised)" instead of "part of". Clicking a country opens a card: the flag of the state in that year, the logo of the ruling party or else the portrait of the main leader, a short generated text on the regime, party, dates, origin, ideology, the first sentences of the Wikipedia article on the ruling party or the ruler (in the language of the page), the leaders (V-Dem, with their portraits), its regimes from 1946 to 2024 and its democracy index (see *Atlas card: flags, logos, portraits and Wikipedia* below). The **List** view shows the same information as a sortable table of the states of the selected year (keyboard: arrow keys move between rows, Enter opens the card). Keyboard: ← → change the year, Space plays the timeline, Esc closes the card or the list; the year is announced to screen readers. Links: `atlas.html#pays=CUB&annee=1975` opens a country in a given year, `#vue=liste` opens the list (older links to `index.html#pays=…` are redirected to the Atlas). The panels, the timeline and the list are drawn first and work while the globe loads; without WebGL the List view opens by itself, with a message. On a computer, the globe stops above the timeline, which no longer hides its lower part; the **Hide chart** button above the timeline folds the chart of autocracies per year, and **Show chart** brings it back (the choice is kept in the browser). On a phone (≤ 860 px) the "World situation" panel is a card above the timeline, closed by default, whose summary gives the year and the number of autocracies. The globe renders at most 1.5 pixels per CSS pixel; if it shows fewer than 30 frames per second in its first seconds, it switches to 1. With the system setting "reduce motion", the globe does not rotate by itself and draws no rings. |
| `analyse.html` · Analysis | A dashboard of the results, generated from the notebooks' exports: five key figures, then one card per question, each with a one-sentence answer built from the exported numbers (e.g. "half of the parties lose power within 11 years") and a chart. **01** How long do they stay in power? (Kaplan-Meier curve, for all parties or by origin, strategy or era, with the longest and the shortest group highlighted; the parties whose strategy is not coded are neither drawn nor compared, and stay greyed in the table; the log-rank test of this view compares the three coded strategies.) **02** What makes them last? (Effect of each factor of the static Cox model as a multiplier of the risk of falling: blue protects, red weakens, grey has no clear effect.) **03** Can their fall be predicted? (C-index and ROC-AUC of the Cox models and of the machine-learning models, on a scale from 0.5 = chance to 1 = perfect.) **04** Does the country matter? (C-index of the existing model and with the best country characteristic of each block, from `04_demographics.ipynb`.) **05** Do shocks bring parties down? (Effect of each shock of the previous year on the risk of falling, as a multiplier, grey when there is no clear effect after the Holm correction, from `05_shocks.ipynb`.) **06** Do the party and its leader matter? (Effect of the party's age and of six characteristics of its leader at entry into power, as a multiplier of the risk of falling, grey when there is no clear effect after the Holm correction, from `06_party_leaders.ipynb`.) **07** What data? (From all authoritarian regimes to the parties of the model.) Each card folds its details under **Show details**: the full tables, the four Cox models (forest plot), the proportional-hazards tests and the early/late correction, the V-Dem robustness check, the benchmark, the country test, the shock test and the party and leader test in full, and "How to read this chart" boxes. **Going further** gathers the detailed conclusion, the research questions, the limitations, the sources and a glossary (hazard ratio, censoring, median survival, C-index, p-value, confidence interval, Holm correction). A link to a card or a term (`analyse.html#facteurs`, `#gl-hr`) opens the folded part that holds it. |
| `simulation.html` · Simulation | A game with two modes. **Free**: the player chooses the characteristics of a party when it takes power (origin, governance strategy, Marxist-Leninist ideology, armed conflict, Polity2 score) and the corrected static Cox model predicts how long it stays in power: median duration with its 95% band, probability of still being in power after 5, 10, 20 and 30 years, survival curve, effect of each choice on the risk of falling, historical rank, closest real parties, warnings when a choice rests on few parties, and a log to compare strategies. Next to the median, the **confidence** of the prediction (high, medium or low, with an icon and its reasons) is read from those warnings: high without warning; medium with a single warning, either a choice made by 10 to 19 parties or a Polity2 score outside the range of 90% of parties; low for an origin × strategy combination never observed, a choice made by fewer than 10 parties (the clientelist strategy: 8), or two warnings or more. **Challenges**: five scenarios set one or more parameters (e.g. "your party came from a military coup: stay 10 years"); the challenge is won if the predicted probability of still being in power at the target duration is at least 50%, with 1 to 3 stars by that probability, **capped by the confidence** (2 stars at most when it is medium, 1 when it is low; the result says so, e.g. "3 stars possible, limited to 1: the clientelist strategy rests on 8 parties"), the rank among real parties, and the best (capped) score of each challenge kept in the browser. The thresholds follow a rule applied to the 1,764 profiles a player can build (`frontend/assets/js/game.js`): 50% for one star, and for three stars the best probability reached by a profile of the best confidence the challenge allows, so that every challenge can be won with three stars by a well-documented profile; the coup challenge gives two stars at most, because every military-founded party profile rests on 17 parties. When no profile reaches 52% at the planned duration, the duration is shortened by 5 years: on the current model, the president challenge targets 10 years, the coup 10, the opening 15, the war 30 and independence 25. **Copy link** copies the address, which holds the profile, the challenge and the language (`simulation.html#o=Communist&g=Repressive&m=1&c=0&p=-7&h=30&lang=en`). The prediction runs in the browser (`frontend/assets/js/survival.js`, a port of `api/predictor.py`); the API is not needed. |
| `about.html` · About | Authors, what the site shows, the method in six lines, the data sources with their citations (including those of the country characteristics test, of the shock test and of the party and leader test), credits and licences. |

Build the data, then open the site:

```bash
python frontend/build_data.py            # from the project root; writes frontend/data/*.js
cd frontend && python -m http.server 8000  # then open http://127.0.0.1:8000
```

The pages can also be opened directly from disk (double-click `frontend/index.html`). Fonts are loaded from Google Fonts; without internet access the pages fall back to system fonts.

*Online (Render).* The site is static, so it can be published as it is. `render.yaml` (a Render Blueprint) publishes `frontend/` with no build step on Render; `frontend/data/*.js` must therefore be rebuilt locally (`python frontend/build_data.py`) and committed. First time: on https://render.com, sign in, choose **New → Blueprint**, connect this GitHub repository and confirm; Render reads `render.yaml` and gives the site an address such as `https://observatoire-regimes-autoritaires.onrender.com`. Each push to `main` then deploys the site again.

*Languages.* The switcher FR · EN · العربية in the command bar changes the language in place (the year, the selected country and the simulation profile are kept). The language comes from `?lang=` (or `lang=` in the `#`), else the last choice (saved in the browser), else the browser's language, else French. Interface texts live in `frontend/assets/i18n/{fr,en,ar}.js` (one key tree, JSON after the `=`); dataset codes are translated there too (`labels`). The texts generated from the results (conclusion, research questions, limitations, syntheses) are rewritten in the three languages by `src/site_text.py`, called by the export sections of the notebooks, so every language states the same numbers; the notebooks keep displaying their own French texts. Terms follow `docs/glossary.md`, which marks the Arabic terms to be reviewed by a native speaker. In Arabic the layout is mirrored (right to left), numbers use Latin digits (`0.47`, `4,233`) like the charts, formulas and signed numbers are kept left to right (`HR = 0.47`, `p < 0.001`, `−3`), and the charts, the timeline and the sliders keep a left-to-right axis. Arabic text uses Amiri and IBM Plex Sans Arabic. In French, `assets/js/i18n.js` puts a narrow no-break space before ? ! ; : » and after « (in the dictionaries and, through `assets/js/core.js`, in the generated texts), so that these signs never wrap alone to the next line; the files themselves keep ordinary spaces.

`build_data.py` reads `data/processed/arpd_panel_merged.csv`, `ml_static.csv`, the six `site_results_*.json` exports, `src/cox_static_model.json`, the Natural Earth 1:50m country borders and names (`data/raw/ne_50m_admin_0_countries.geojson`, names in French, English and Arabic), the Natural Earth 1:50m disputed areas (`data/raw/ne_50m_admin_0_breakaway_disputed_areas.geojson`, public domain, downloaded without registration from https://github.com/nvkelso/natural-earth-vector; it gives the outlines of Crimea and Western Sahara, which `build_data.py` moves from Russia to Ukraine and from Morocco to Western Sahara) and V-Dem. With `data/raw/V-Dem-CY-Full+Others-v16.csv` (406 MB, not in the repository: download "Country-Year: V-Dem Full+Others v16" in CSV format from https://v-dem.net/data/the-v-dem-dataset/) the cards show the names of the leaders; without it, the script falls back to the Core file and omits them. It checks that every ARPD country-year from 1946 to 2024 is drawn on the globe. Borders are today's, according to the UN position (see the Atlas row above): territories of dissolved unions (USSR, Yugoslavia, Czechoslovakia) take the colour of the state they belonged to, and divided states (East Germany, North and South Vietnam, North and South Yemen) are listed in the card of today's country. A polygon shows one regime per year: in the three years where two parties of the same state share a year (Yemen 1990, Serbia 1991, Sudan 2011), the globe shows one of them and the other appears in that year's events. Re-run `build_data.py` after re-running a notebook.

*Atlas card: flags, logos, portraits and Wikipedia.* The country card shows, for the year chosen, the flag of the state, the logo of the ruling party (or else the portrait of the main leader) next to the generated text, the first sentences of the Wikipedia article on the ruling party (or, in an autocracy without a party, on the main leader), and small portraits next to the leaders' names. `frontend/build_media.py` collects them once and writes `data/raw/wikimedia_atlas.json`; `build_data.py` turns it into tables of `atlas.js` and into `frontend/data/wiki_{fr,en,ar}.js` (the extracts, loaded when a card opens).
- Sources, none of which needs a registration: Wikidata (CC0) for the dated flags (P41, and P163 for the adoption date of the current flag), the items and logos of the parties (P154) and the links to the articles; Wikipedia in French, English and Arabic (CC BY-SA 4.0) for the articles on the leaders and the extracts; Wikimedia Commons for the image files, each under its own free licence. The requests identify the project in their User-Agent, without personal data.
- Flags: the flag in force at the end of the year, as dated in Wikidata (or in the file name, or by the adoption date of the current flag); no flag when no dated flag covers the year (no flag rather than a wrong one), and none for non-sovereign territories (colonies, Western Sahara). The flag is the one of the state shown: the USSR for Ukraine in 1980, West Germany from 1949, none for Germany under Allied occupation.
- Parties: each ARPD party is linked to the English Wikipedia article checked by hand in `data/raw/atlas_party_wikipedia.csv` (automatic matches reviewed one by one, 26 corrected, 8 parties without an article); a party renamed with one article per name has one row per period (Tunisia: Neo Destour, Socialist Destourian Party, Democratic Constitutional Rally). The logo is the latest logo recorded in Wikidata; for a party that still exists, the card says "current logo", and a logo with a start date is not shown before it.
- Leaders: a V-Dem name is linked to an English Wikipedia article only if the article is about a person alive in the years concerned (categories of birth and death), whose name is close to V-Dem's and who is linked to the country (its name or demonym in the description or the categories); first by trying the name and shorter forms as titles, then by a search. Main leaders of autocracies that this cannot find (typing errors in V-Dem, distant transliterations, titles such as "Faruq I") are linked by hand in `LEADER_TITLES` (`build_media.py`), still checked against the article's dates; "Georgios Andreou Papandreou" is left without a link, because V-Dem gives this name both to Georgios Papandreou (1964) and to his grandson George Papandreou (2009–2010). The portrait is the free lead image of the article. The main leader is the head of government when V-Dem says that he or she has more power over the cabinet than the head of state (`v2ex_hosw` < 0.5), otherwise the head of state.
- Extracts: the first sentences of the article in the language of the page (up to about 320 characters), without pronunciations (phonetic alphabet, "listen"), names in other languages or scripts, and asides longer than 90 characters. Extracts are collected for the ruling parties and for the main leaders of autocracies only.
- Coverage (collection of 21 October 2026): 241 of the 253 Wikidata states have at least one dated flag; all 634 flag files are free Commons images. The states without a dated flag are North Yemen (until 1989), Palestine, Western Sahara, New Caledonia, Antarctica and seven small territories. 256 of the 264 ARPD parties have an article and 116 have a logo. 3,236 of the 3,767 V-Dem leaders (name and country) are linked to an article, and 2,856 have a portrait. 1,034 of the 1,052 main leaders of autocracies are linked; the 18 others are 14 "collective bodies" (juntas, councils), Georgios Andreou Papandreou, and three people for whom no English article was found (Vladimir Sviridov, Hungary 1946; Akim A. Gibril, Sierra Leone 1995–1996; George Mooring, Zanzibar 1963). Extracts: 1,202 in French, 1,269 in English, 1,018 in Arabic.
- Credits: each card lists, under "Image and text credits", the author and the licence of every image, with a link to its Commons page, and the licence of the Wikipedia text. The author is the one given on the file page, without wiki boilerplate ("User:", "see file history below", "Unknown author" written twice); when the page names no author (108 of the 3,497 files), the card gives the licence and the link only; the About page cites Wikidata, Wikimedia Commons and Wikipedia. The images are loaded from Wikimedia's servers when a card opens (the visitor's browser then contacts Wikimedia); offline, the card simply shows no image.
- Rerun: `python frontend/build_media.py` (internet; about 2 hours 30 the first time, at one request per second because Wikimedia limits anonymous clients, plus the pauses it asks for; when a server answers "429 Too Many Requests", the script waits as long as its `Retry-After` header asks, and at least 15 seconds doubled at each new attempt; the answers are cached in `data/raw/wikimedia_cache/`, not in the repository, so a rerun without new names takes under a minute), then `python frontend/build_data.py`. Without `wikimedia_atlas.json`, the site works and shows no image and no extract.

*Tests.* `python -m pytest tests` also checks the website:
- `tests/test_frontend_build.py`: schemas of the four data files, every dictionary key used by a page (no key left over), the log-rank test of the strategy view computed without the parties whose strategy is not coded, every ARPD party-year drawn, the three languages present for every generated text and every name, the same keys and placeholders in the three dictionaries, every key used by the pages defined, no text left untranslated in the HTML, only result tables (no country-year values) copied from `site_results_demo.json`, `site_results_shocks.json` and `site_results_leaders.json` (no leader or LEAD value either), every key that the Analyse page builds at run time (table columns, verdicts, "How to read" boxes) defined, the borders (Crimea in Ukraine, Western Sahara distinct from Morocco, areas of Ukraine and Western Sahara within 2.5% of 603,500 and 266,000 km²), the unrecognised annexations, Western Sahara's status, the two periods without a party closed after 2015, the absence of `Monarchy` from the exported model and from the simulation, and the media of the Atlas card (every image a free Commons file with its licence, every extract in the right language, flags by period on known cases such as Libya and the USSR, no flag for non-sovereign territories, leaders linked to the right people on known cases such as Fidel Castro and Augusto Pinochet, parties linked to their articles by period);
- `tests/test_frontend_model.py`: `frontend/data/model.js` contains the current `src/cox_static_model.json`, and the JavaScript predictor gives the same curves, bands, medians, warnings and coded warnings as `api/predictor.py` on 80 random profiles (requires Node.js; skipped otherwise);
- `tests/test_frontend_game.py`: the game rules of `frontend/assets/js/game.js`, run with Node: the confidence rule on hand-written cases and on the 1,764 possible profiles (against the warnings of `api/predictor.py`), the star cap, and the challenges, whose targets and thresholds must follow the calibration rule on the current model, with every challenge reaching its maximum number of stars (requires Node.js; skipped otherwise);
- `tests/test_frontend_typography.py`: in French, every text of the dictionaries and every generated text gets a narrow no-break space before ? ! ; : » and after «, while English and Arabic are unchanged (requires Node.js; skipped otherwise);
- `tests/test_site_text_branches.py`: the texts of `src/site_text.py` for notebooks 04, 05 and 06 in the cases the current results never reach (a variable kept, a variable almost kept for each condition, variables that cannot be tested), rebuilt from altered copies of the exports: no error, and a failed condition is never presented as met;
- `tests/test_frontend_smoke.py`: every page in every language, 1600 px and 390 px wide, in a headless Chromium browser: no console error, `lang`/`dir` set, no horizontal overflow, no untranslated key, no ordinary space before French punctuation; the home page draws its five charts and the Analyse dashboard its seven; on the Atlas at 1600 px, the globe ends above the timeline and the chart button hides and shows the chart; at 390 px, the "World situation" card is closed by default and covers neither the timeline, nor the controls, nor a country card; and in a browser without WebGL, the Atlas opens its List view with a message. It needs Node.js, the npm package `puppeteer-core` (found by Node, or in the `node_modules` folder given by `ARPD_NODE_PATH`) and Edge or Chrome (or `ARPD_BROWSER`); it is skipped otherwise, and with `ARPD_SKIP_BROWSER=1`. It takes 15 to 25 minutes on a computer without a graphics card, mostly for the 3D globe in software rendering; there, an Atlas page opened right after another can wait several minutes for the browser's graphics process, still busy with the previous globe, and may exceed the 5-minute limit of a page load.

*Licences and credits.* Country borders from Natural Earth (public domain); globe rendered with globe.gl (MIT licence, © Vasco Asturiano) and three.js (MIT); fonts Cormorant Garamond, Inter, JetBrains Mono, Amiri and IBM Plex Sans Arabic (SIL Open Font License 1.1). V-Dem data: Coppedge et al. (2026), V-Dem Country-Year Dataset v16, https://doi.org/10.23696/vdemds26. According to V-Dem's dataset page, the V-Dem Dataset is published under a Creative Commons Attribution-ShareAlike (CC BY-SA) 4.0 licence, which allows use and redistribution with attribution, and requires derivative products to be distributed under the same licence: this applies to the V-Dem values contained in `frontend/data/atlas.js` (regime classes, democracy index, leaders' names) and in `data/processed/arpd_panel_merged.csv`.

**Notes & reproducibility**
- `01_data_merging.ipynb` (v1.3, October 2026): `tenure_years` is the total tenure of the leader of each country-year (first start date to last end date of the Archigos spell, `obsid`); it used to be the time in office within one row of the annual Archigos file (at most one year). The time within the year is kept as `years_in_row` and still chooses the leader of a country-year, so the merged leaders do not change. The Archigos figures read exit modes and post-tenure fates on the last year of each tenure, where the annual file records them (they used to leave out 77% of the tenures), and are saved again in `graph/` (`arch_entry_exit.png`, `arch_fate.png`, `arch_tenure.png`, `arch_corr.png`); the Polity5 figures use Polity's three categories (autocracy −10 to −6, anocracy −5 to +5, democracy +6 to +10). No model uses these columns. The other figures of `graph/` named after a source (`arch_birth_year.png`, `vdem_*`, `polity5_*`, `reign_missing.png`…) come from an earlier version of the notebook, which no longer saves them.
- Four country names (`Haiti `, `Romania `, `Russia `, `Vietnam `) and three party names of the raw ARPD keep stray spaces (a trailing space, or a double space in "All People's Congress  (APC)"). They are left as they are, because they are part of the join keys (`spell_id`, `Country`) of every table; the pages do not show them.
- Limits of the data worth keeping in mind: 70% of the parties of the static model (156 of 224) have no coded governance strategy, and the reference strategy (`Policy-Based`) counts only 27 parties; 170 party-years of named parties (in 30 countries, e.g. Namibia, Malaysia) have a Polity2 score of 6 or more, democratic by Polity's standard, although the ARPD codes them as authoritarian.
- `RANDOM_STATE = 42` wherever randomness is involved.
- Juntas (`Party = "N"`) are excluded from both analyses; this is documented in the notebooks and discussed in the limitations.
- Some rules for reconstructing binary variables (e.g., `Military`, `Violence`, `Occupation`) in `final.ipynb` are heuristic and rely on deterministic mappings documented in the notebook.
- In the ARPD, `Military`, `Violence` and `Occupation` describe only regimes without a party (juntas); they are not used as covariates for named parties in `final.ipynb`. `Governance Strategy` is coded by Miller (2020) for about a third of the parties and is not imputed: uncoded parties form an explicit "Non code" category.
- `Monarchy` is our own coding, year by year (table `GOVERNING_MONARCHY`, identical in `01_data_merging.ipynb` and `final.ipynb`, with dated sources): 1 when a monarch, or a royal regent of a minor king, actually holds executive power on 31 December (absolute or semi-absolute monarchy); constitutional monarchies whose government does not depend on the monarch are 0 (Japan, Thailand, Laos 1959–1975, Lesotho, Malaysia). Only three named parties are governing monarchies when they come to power (Iran 1963 and 1975, Swaziland 1968; 21 party-years), too few to estimate an effect: the variable stays in the panel as a descriptive column and is in no model (`final_panel.ipynb`, `final.ipynb`, `03`–`05`), no export and no choice of the simulation. The previous version coded every year of a list of countries, including years after the monarchy (Iran after 1979, Libya after 1969).
- Post-2015 extension (`01_data_merging.ipynb`, Section 9, and `final.ipynb`, Section 4.0, same table): falls coded by hand, each with its source. Added: FLN (Algeria) 2019, Dawa (Iraq) 2018; corrected: PPRD (DR Congo) 2019 instead of 2018 (last calendar year in power, as for the Gambia in 2017). Not a fall: Uzbekistan (Mirziyoyev succeeds Karimov in 2016 without a change of regime), Chad (Mahamat Déby succeeds his father in 2021 with the support of the MPS: continuity), Kazakhstan (Nur Otan renamed Amanat), Togo. The falls of the EPRDF (Ethiopia, 2019) and of the RDR (Côte d'Ivoire, 2018) are kept, but their successor parties (Prosperity Party, RHDP) are not added as new spells. The end mode of these falls is left empty: it is never filled in without a source.
- The ARPD uses Polity country codes for five states (USSR 364, Vietnam 818, Ethiopia 529, Serbia 347, Sudan-North 624). `01_data_merging.ipynb` translates them to standard COW codes when merging V-Dem, Archigos, REIGN, UCDP, the World Bank and Maddison; `04_demographics.ipynb` and `05_shocks.ipynb` also translate 769 (Pakistan, 1947–1949) to 770.
- UCDP starts in 1946: conflict variables are missing (not 0) before 1946.

**Citation**
If you use this work, please cite Miller (2020) for the dataset and include this notebook authorship:

M.K. Miller (2020). The Autocratic Ruling Parties Dataset. Journal of Conflict Resolution.

**License**
Use and redistribution: please ask the author (above) for permission before redistribution.
