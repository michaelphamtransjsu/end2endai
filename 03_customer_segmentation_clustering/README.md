# Project 3 — Customer Segmentation

A local, reproducible CRISP-DM vertical slice that generates non-identifying sample customers, cleans and transforms them, compares cluster solutions, creates personas and a PCA plot, and serves the selected K-Means model through FastAPI.

## Quick start

Run these commands **from this directory** (Python 3.11+):

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.pipeline --data data/customers.csv --output artifacts
.venv/bin/python -m pytest -q
.venv/bin/uvicorn src.api:app --host 127.0.0.1 --port 8000
```

The pipeline is both sample-data generation and analysis/training. It writes ignored, reproducible files to `data/` and `artifacts/`: metrics, personas, PCA PNG, metadata, and the fitted model. Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## API smoke test

With the server running:

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS -X POST http://127.0.0.1:8000/predict \
  -H 'content-type: application/json' \
  -d '{"age":35,"annual_income":60000,"spending_score":70,"purchase_frequency":10,"region":"East"}'
```

`POST /predict` validates numeric ranges and returns a cluster number and descriptive persona. Unseen regions are accepted and safely ignored by the one-hot encoder. The endpoint is descriptive decision support, not an eligibility or individual-impact decision system.

## Design and outputs

The deterministic generator uses seed 42 and three simulated behavioral populations, plus missing, duplicate, and out-of-range examples to exercise cleaning. Validation requires the feature schema; cleaning deduplicates IDs, coerces and median-imputes numeric values, bounds invalid values, and maps invalid categories to `Unknown`. Numeric inputs are standardized and region is one-hot encoded.

K-Means evaluates `k=2..6` with 20 initializations. The winner maximizes silhouette score, using lower Davies-Bouldin only as a tie-break; persona attractiveness never enters selection. Agglomerative clustering at the selected `k` is an alternative-method comparison. See [CRISP_DM_REPORT.md](CRISP_DM_REPORT.md) for methodology and [FINAL_REPORT.md](FINAL_REPORT.md) for verified run results and limitations.
