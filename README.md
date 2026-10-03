# Analyse de la Survie des Partis Autoritaires (ARPD)

An applied survival analysis of authoritarian ruling parties using the Autocratic Ruling Parties Dataset (Miller, 2020), enriched with country-year data from V-Dem, Polity5, Archigos, REIGN, UCDP/PRIO, the World Bank and the Maddison Project Database 2023 (GDP per capita since the 19th century; Bolt & van Zanden, 2024, https://doi.org/10.34894/INZBF2, CC-BY-4.0).

**Authors:** Fedi Jouili — Eya Chaabouni

---

**Purpose**: Investigate the structural, institutional and time-varying (economy, conflict, democracy level) determinants of party longevity in non‑democratic regimes, using Kaplan–Meier estimation and Cox proportional hazards models.

**Repository layout**
```
data/
  raw/          source datasets (ARPD, V-Dem, Polity5, Archigos, REIGN, UCDP, World Bank, Maddison)
  processed/    arpd_panel_merged.csv (party-year panel) + its data dictionary;
                ml_static.csv, ml_timevarying.csv, ml_metadata.json (modelling datasets exported for the ML notebook);
                ml_folds.csv (cross-validation fold assignments)
graph/          EDA figures: per source (01_data_merging.ipynb) and of the merged panel (panel_*.png, 02_eda_and_data_processing.ipynb)
notebooks/
  01_data_merging.ipynb             EDA of each source + merge into the party-year panel
  02_eda_and_data_processing.ipynb  exploratory analysis of the merged panel (before the models)
  final.ipynb                       spell-level analysis (one row per party)
  final_panel.ipynb                 panel analysis — main notebook
  03_ml_survival.ipynb              machine-learning benchmark of the Cox models
requirements.txt        pinned package versions (see Requirements)
src/
  panel_model.py        early/late Cox helpers + survival prediction (shared with the web app)
  cph_static_model.pkl  exported Cox model (written by final_panel.ipynb)
  model_features.pkl    expected covariates, corrected covariates, time cut, Origin levels
api/, frontend/         web app (not started)
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
- Kaplan–Meier median survival by origin, governance strategy and era (log-rank tests), coverage of the merged sources over time, macro variables in the years before a fall
- Checks behind the modelling choices (origin/ideology overlap, Polity2–V-Dem correlation, governance coding rate, missing data) and a generated synthesis for the models; figures saved as `graph/panel_*.png`

`03_ml_survival.ipynb`
- Predictive benchmark of the Cox models with machine learning; the Cox models remain the inference tool
- Uses exactly the datasets of `final_panel.ipynb` (exported in its Section 7.3), with data-integrity and leakage checks
- Evaluation: 5-fold cross-validation grouped by country (all spells of a country in the same fold), stratified on the event, repeated 10 times; fold assignments saved so every model uses the same splits
- Task A (one row per spell): Kaplan-Meier, Cox, random survival forest, gradient-boosted survival (Harrell and Uno C-index, integrated Brier score, time-dependent AUC)
- Task B (one row per party-year, discrete-time hazard): duration only, time-varying Cox, logistic regression, LightGBM (ROC-AUC, PR-AUC, Brier, log loss, calibration)
- Comparison with the corrected resampled t-test (Nadeau & Bengio, 2003); interpretation with permutation importance, partial dependence and SHAP values; generated limitations and conclusion

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
| `02_eda_and_data_processing.ipynb` | `data/processed/arpd_panel_merged.csv` | figures `graph/panel_*.png` |
| `final.ipynb` | `data/raw/ARP_dataset_cleaned.csv` (or `ARP_DATA_PATH` if set) | `data/processed/ARP_dataset_filled.csv`, `ARP_dataset_clean.csv`, `ARP_dataset_model.csv` |
| `final_panel.ipynb` | `data/processed/arpd_panel_merged.csv` | `src/cph_static_model.pkl`, `src/model_features.pkl`, `data/processed/ml_static.csv`, `ml_timevarying.csv`, `ml_metadata.json` |
| `03_ml_survival.ipynb` | `data/processed/ml_static.csv`, `ml_timevarying.csv`, `ml_metadata.json`, `arpd_panel_merged.csv` | `data/processed/ml_folds.csv`, `ml_results_taskA.csv`, `ml_results_taskB.csv`, `ml_oof_taskB.csv` |

Run order: `01_data_merging.ipynb` → `02_eda_and_data_processing.ipynb` → `final_panel.ipynb` → `03_ml_survival.ipynb` (`final.ipynb` is independent: it reads the raw ARPD file).

**Notes & reproducibility**
- `RANDOM_STATE = 42` wherever randomness is involved.
- Juntas (`Party = "N"`) are excluded from both analyses; this is documented in the notebooks and discussed in the limitations.
- Some rules for reconstructing binary variables (e.g., `Military`, `Monarchy`, `Violence`, `Occupation`) in `final.ipynb` are heuristic and rely on deterministic mappings documented in the notebook.
- In the ARPD, `Military`, `Violence` and `Occupation` describe only regimes without a party (juntas); they are not used as covariates for named parties in `final.ipynb`. `Monarchy` is our own coding (verified list of monarchies). `Governance Strategy` is coded by Miller (2020) for about a third of the parties and is not imputed: uncoded parties form an explicit "Non code" category.
- The ARPD uses Polity country codes for five states (USSR 364, Vietnam 818, Ethiopia 529, Serbia 347, Sudan-North 624). `01_data_merging.ipynb` translates them to standard COW codes when merging V-Dem, Archigos, REIGN, UCDP, the World Bank and Maddison.
- UCDP starts in 1946: conflict variables are missing (not 0) before 1946.

**Citation**
If you use this work, please cite Miller (2020) for the dataset and include this notebook authorship:

M.K. Miller (2020). The Autocratic Ruling Parties Dataset. Journal of Conflict Resolution.

**License**
Use and redistribution: please ask the authors (listed above) for permission before redistribution.
