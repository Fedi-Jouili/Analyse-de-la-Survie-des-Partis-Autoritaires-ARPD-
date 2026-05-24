# Analyse de la Survie des Partis Autoritaires (ARPD)

This repository contains the Jupyter notebook `final.ipynb`, an applied survival analysis of authoritarian ruling parties using the Autocratic Ruling Parties Dataset (Miller, 2020).

**Authors:** Fedi Jouili — Eya Chaabouni

---

**Purpose**: Reproduce the survival analysis pipeline used to investigate structural and institutional determinants of party longevity in non‑democratic regimes. The notebook performs data loading, cleaning, exploratory analysis, Kaplan–Meier estimation, Cox proportional hazards modeling (including penalized, stratified, interaction terms), diagnostics, a Weibull AFT comparison, and bootstrap inference.

**Notebook structure (high level)**
- Configuration & imports
- Introduction, definitions & literature review
- Data loading and exclusion of `Party = "N"` (juntas)
- Exploratory data analysis (pre-/post-cleaning)
- Cleaning & preprocessing (type fixes, binary reconstruction, encoding)
- Kaplan–Meier estimation & log‑rank tests
- Cox model fitting and comparisons
- Diagnostics (Schoenfeld, residuals, VIF)
- Bootstrap and Weibull AFT as robustness checks
- Interpretation, limitations, references

---

**Requirements**
- Python 3.8+ recommended
- Key Python packages used (installed by the notebook if missing):
  - `lifelines`
  - `matplotlib`
  - `seaborn`
  - `statsmodels`
  - `scipy`
  - `pandas`, `numpy`, `scikit-learn`

You can install the core dependencies with:

```bash
pip install lifelines matplotlib seaborn statsmodels scipy pandas numpy scikit-learn
```

**Data**
- The notebook expects the ARPD CSV file at `ARP_dataset_cleaned.csv` in the notebook directory or the path provided via the environment variable `ARP_DATA_PATH`.
- The notebook writes intermediate outputs to:
  - `ARP_dataset_filled.csv`
  - `ARP_dataset_clean.csv`
  - `ARP_dataset_model.csv`

**How to run**
1. Open `final.ipynb` in JupyterLab / Jupyter Notebook / VS Code.
2. (Optional) Set `ARP_DATA_PATH` to the dataset location if not placed next to the notebook.

On Windows (PowerShell):

```powershell
$env:ARP_DATA_PATH = "C:\path\to\ARP_dataset_cleaned.csv"
jupyter lab
```

3. Run cells top to bottom. The notebook includes automatic checks and a small routine to install missing packages (uses `pip`).

**Outputs & artifacts**
- Figures: EDA plots, KM curves, forest plots, residuals diagnostics
- Tables: model summaries, bootstrap CI tables, model comparison table
- CSVs: cleaned and model datasets (listed above)

**Notes & reproducibility**
- The notebook sets `RANDOM_STATE = 42` for reproducibility where applicable.
- The analysis excludes observations with `Party = "N"` (juntas); this is documented in the notebook and discussed in the limitations section.
- Some rules for reconstructing binary variables (e.g., `Military`, `Monarchy`, `Violence`, `Occupation`) are heuristic and rely on deterministic mappings documented in the notebook.

**Citation**
If you use this work, please cite Miller (2020) for the dataset and include this notebook authorship:

M.K. Miller (2020). The Autocratic Ruling Parties Dataset. Journal of Conflict Resolution.

**License**
Use and redistribution: please ask the authors (listed above) for permission before redistribution.

---

