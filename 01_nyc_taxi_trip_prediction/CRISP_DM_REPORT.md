# CRISP-DM Report

## 1. Business understanding

Goal: demonstrate a low-latency estimate of NYC taxi trip duration from information available at pickup. Success for this MVP means an end-to-end, reproducible local path and an improved model beating a median baseline on both MAE and RMSLE—not readiness for dispatch, fares, or safety decisions.

## 2. Data understanding

The bundled 360-row synthetic sample spans January–June 2016 at 12-hour intervals. Coordinates are sampled within a Manhattan-area rectangle; durations combine approximate geographic distance, rush/weekend effects, and seeded noise. It is intentionally small and contains no personal data. It does not reproduce weather, traffic, roads, airport queues, or real sampling bias.

## 3. Data preparation

`validate_frame` requires the schema, parses timestamps and numerics, rejects missing/non-finite values, checks NYC coordinate bounds, passenger counts 1–8, and training targets 30–10,800 seconds. Feature engineering computes haversine distance and pickup hour, weekday, weekend, rush-hour, passenger count, and endpoint coordinates. The serialized estimator calls the same feature function during inference.

## 4. Modeling

The baseline predicts the training median. The improved estimator is histogram gradient boosting with fixed seed and bounded complexity. Rows are ordered by pickup time; the first 80% train and newest 20% test. This mimics forecasting later trips and prevents later observations entering training, although overlapping real-world drivers or locations are not represented by synthetic data.

## 5. Evaluation

MAE is interpretable in seconds; RMSLE emphasizes relative error and reduces domination by long trips. The generated `artifacts/metrics.json` is the source of exact measured results. Passing the baseline is only an internal synthetic-data check, not evidence of real NYC performance.

## 6. Deployment

FastAPI loads the joblib artifact lazily, validates JSON using Pydantic, and serves a static interactive form. `/health` reports artifact availability and `/predict` returns seconds and minutes. Monitor input ranges, temporal drift, residuals by geography/time, latency, and errors before any real use. Retrain only from versioned validated data, then rerun chronological evaluation and tests.
