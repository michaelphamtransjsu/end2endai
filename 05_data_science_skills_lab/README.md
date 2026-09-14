# Data Science Skills Mastery Lab

A compact, offline end-to-end lab using the Iris, Breast Cancer Wisconsin
(Diagnostic), and Diabetes datasets bundled with scikit-learn. It demonstrates
classification, regression, clustering, statistics, PCA visualization, and
reproducible reporting. No dataset download or paid service is required.

## Setup

From `05_data_science_skills_lab` (Python 3.11 recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Run the analysis / generate saved artifacts

```bash
python3 run_analysis.py --output-dir outputs
```

This creates one PCA PNG and one metrics JSON file per dataset. `outputs/` is
deliberately gitignored because every artifact is reproducible. The console
also prints the actual paths and metrics. The fixed split and estimator seed is
42; package versions are pinned in `requirements.txt`.

## Tests

```bash
python3 -m pytest -q
```

The tests include all-dataset end-to-end analysis and report-generation smoke
tests.

## Dashboard

```bash
python3 -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). Use
the sidebar to select a dataset, then inspect the data, descriptive statistics,
PCA chart, engineered features, supervised evaluation, clustering evaluation,
and statistical test. For a non-interactive startup smoke test:

```bash
timeout 15s python -m streamlit run app.py --server.headless true --server.port 8501
```

## Project layout

- `skills_lab/data.py`: loading contract, validation, and cleaning.
- `skills_lab/analysis.py`: EDA, feature engineering, statistical inference,
  train/test modelling, evaluation, clustering, and PCA.
- `skills_lab/reporting.py`: deterministic chart and JSON report artifacts.
- `run_analysis.py`: command-line orchestration across all datasets.
- `app.py`: Streamlit interactive presentation.
- `tests/`: automated unit, integration, and smoke tests.

## Interpretation cautions

The datasets are small educational examples. A single fixed train/test split is
easy to reproduce but does not quantify variation across splits. Statistical
p-values demonstrate APIs rather than establish causal claims; assumptions such
as independence and distribution shape require domain review. PCA and K-means
are scale-sensitive, so predictors are standardized. Dataset targets are never
included among clustering inputs or engineered predictors.
