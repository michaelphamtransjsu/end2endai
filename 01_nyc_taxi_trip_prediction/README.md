# NYC Taxi Trip-Duration Prediction MVP

A compact, local end-to-end CRISP-DM demonstration: validated tabular input, geographic/time feature engineering, chronological evaluation, a saved estimator, FastAPI, and a responsive browser UI. **This is an educational model, not an operational travel-time service.**

## Data

`data/sample_trips.csv` contains 360 deterministic synthetic trips in plausible NYC coordinate ranges. It was generated for this repository; no Kaggle account is needed for the demo. Durations reflect a documented distance/rush-hour formula plus seeded noise, so results on it do not establish real-world accuracy.

Optional full data: download the [NYC Taxi Trip Duration competition data from Kaggle](https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data). Keep the raw file local and place it at exactly `01_nyc_taxi_trip_prediction/data/NYC.csv` (that path is git-ignored). From this project directory, train against it with `python -m taxi_duration.train --data data/NYC.csv --output artifacts`. The Kaggle CLI helper, `./scripts/download_kaggle.sh`, is optional and requires your own credentials and acceptance of the competition rules; rename its extracted `train.csv` to `data/NYC.csv`. The Kaggle schema has compatible core columns, but production use should add dataset-specific cleaning and validation.

## Exact local commands

Run from this directory (Python 3.11, 3.12, or 3.13; the pinned scientific stack is not released for Python 3.14):

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m taxi_duration.train --data data/sample_trips.csv --output artifacts
pytest -q
uvicorn taxi_duration.api:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. API smoke test in another shell:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/predict -H 'content-type: application/json' -d '{"pickup_datetime":"2016-06-15T17:30:00","pickup_latitude":40.758,"pickup_longitude":-73.9855,"dropoff_latitude":40.7306,"dropoff_longitude":-73.9352,"passenger_count":1}'
```

## Design

The newest 20% of rows is held out, avoiding random temporal leakage. The median-duration `DummyRegressor` is the baseline. A fixed-seed histogram gradient boosting regressor is the improved model. `DurationPipeline` performs feature engineering inside its serialized prediction path. Features include haversine distance, hour, weekday, weekend/rush indicators, passenger count, and coordinates. Training writes `artifacts/model.joblib` and `artifacts/metrics.json`.

See `CRISP_DM_REPORT.md` for lifecycle decisions, `MODEL_CARD.md` for intended use and risk, and `FINAL_REPORT.md` for verified commands and results.
