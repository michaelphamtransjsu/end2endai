# Final Release Audit

Audited on 2026-09-01 in the repository container. Unless a path says otherwise, commands ran from `01_nyc_taxi_trip_prediction`.

## Release result

**Ready for pull-request review.** The verified vertical slice installs in a clean environment, retrains reproducibly, passes all tests, starts the backend, serves the frontend, and predicts through HTTP. No merge or deployment was performed.

## Critical issue found and fixed

The README previously said “Python 3.11+” and used the container-default `python`, but the default was Python 3.14.4 and the pinned pandas version had no Python 3.14 wheel; the attempted install began a source build and was stopped. This made the documented quick start unreliable. The package now declares `>=3.11,<3.14`, and the README explicitly creates its environment with `python3.11` and names supported versions 3.11–3.13. No model or application behavior changed.

## Exact verification commands and results

1. **Clean dependency installation — PASS**

   `rm -rf /tmp/taxi-release-venv /tmp/taxi-release-artifacts && PYENV_VERSION=3.11.15 python -m venv /tmp/taxi-release-venv && . /tmp/taxi-release-venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && python -m pip install -e .`

   Result: Python 3.11.15; all pinned dependencies installed; editable project wheel built and installed.

2. **Training and analysis — PASS**

   `. /tmp/taxi-release-venv/bin/activate && python -m taxi_duration.train --data data/sample_trips.csv --output /tmp/taxi-release-artifacts`

   Result: chronological split with 288 training and 72 test rows. Baseline MAE 337.806 seconds and RMSLE 0.49387; improved model MAE 46.663 seconds and RMSLE 0.11746. Training ended `2016-05-23 12:00:00`; testing began `2016-05-24 00:00:00`.

   `sha256sum artifacts/model.joblib /tmp/taxi-release-artifacts/model.joblib artifacts/metrics.json /tmp/taxi-release-artifacts/metrics.json && cmp artifacts/metrics.json /tmp/taxi-release-artifacts/metrics.json`

   Result: retrained model hashes matched (`a9dba1b8…b1fe`), metric hashes matched (`a3dd34e7…609c`), and metric files were byte-identical.

3. **Automated tests — PASS**

   `. /tmp/taxi-release-venv/bin/activate && pytest -q`

   Result: `6 passed in 3.43s`.

4. **Backend startup — PASS**

   `. /tmp/taxi-release-venv/bin/activate && uvicorn taxi_duration.api:app --host 127.0.0.1 --port 8765`

   Result: startup and shutdown completed normally; each smoke request returned HTTP 200.

5. **API smoke — PASS**

   `curl -fsS http://127.0.0.1:8765/health`

   Result: `{"status":"ok","model_available":true}`.

   `curl -fsS -X POST http://127.0.0.1:8765/predict -H 'content-type: application/json' -d '{"pickup_datetime":"2016-06-15T17:30:00","pickup_latitude":40.758,"pickup_longitude":-73.9855,"dropoff_latitude":40.7306,"dropoff_longitude":-73.9352,"passenger_count":1}'`

   Result: `{"predicted_duration_seconds":1203.4,"predicted_duration_minutes":20.06}`.

6. **Frontend build/smoke — PASS**

   The frontend is plain HTML/CSS/JavaScript and has no compilation or dependency-install step. Its deployable file is therefore the source file served by FastAPI.

   `curl -fsS http://127.0.0.1:8765/ -o /tmp/taxi-frontend.html && test -s /tmp/taxi-frontend.html && rg -q '<form id="form">' /tmp/taxi-frontend.html && rg -q "fetch\\('/predict'" /tmp/taxi-frontend.html`

   Result: served frontend was 2,191 bytes and contained both the interactive form and `/predict` request wiring.

7. **README command audit — PASS**

   The documented installation, training, test, and Uvicorn commands map directly to `requirements.txt`, the editable package, `taxi_duration.train`, pytest configuration, and `taxi_duration.api:app`. The documented health and prediction requests match the implemented routes. The optional Kaggle command was not run because it requires user credentials and competition access; the credential-free bundled demo was fully verified.

8. **Repository hygiene — PASS**

   From the repository root: `git diff --check && git status --short && find 01_nyc_taxi_trip_prediction -type f -not -path '*/.venv/*' -printf '%s %p\n' | sort -nr | head -20 && rg -n -i '(api[_-]?key|secret|password|token|BEGIN [A-Z ]*PRIVATE KEY)' 01_nyc_taxi_trip_prediction --glob '!.venv/**'`

   Result: no whitespace errors; no virtual environment, cache, `node_modules`, full Kaggle data, or build directory was staged. No credential or private-key material was found (documentation references to credentials/secrets and this audit pattern are non-secret). The generated 178,738-byte joblib model was reproducible but has been removed from Git tracking for pull-request compatibility; training recreates it locally. The largest retained project data file is the 28,645-byte bundled sample CSV. Metrics remain as a text JSON summary. Temporary verification outputs remained under `/tmp`.

## Remaining limitations

The sample is synthetic and structurally simple, so these scores do not establish real NYC accuracy. It omits routing, live traffic, weather, road closures, airport behavior, borough balance, and fairness-relevant operating conditions. The chronological holdout has only 72 rows; there is no external validation or hyperparameter search. The frontend received static and route-level smoke coverage, not a multi-browser end-to-end test. The Kaggle download path remains optional and unverified in this audit. Only trusted joblib artifacts should be loaded because deserialization can execute code.

## Pull-request binary repair audit — 2026-09-14

The branch-versus-base binary inventory initially contained exactly one file: `artifacts/model.joblib`, a 178,738-byte joblib/pickle binary. No tracked `NYC.csv`, ZIP, `.pkl`, SQLite/database, packaged project ZIP, PNG chart, or PDF transcript was present, so there was nothing in those categories to remove or convert. The 28,645-byte synthetic `data/sample_trips.csv`, text `artifacts/metrics.json`, source, tests, configuration, frontend, scripts, and Markdown documentation were retained.

The joblib file was removed from Git tracking. `.gitignore` now excludes the user-owned `data/NYC.csv`, full-data directory, ZIP archives, joblib/pickle artifacts, SQLite/database files, and Python package artifacts. The README identifies the Kaggle download page and exact local destination. Because API tests formerly relied on the tracked model, a session fixture now trains a temporary model outside the repository; this preserves standalone `pytest` behavior without committing generated binaries.

An initial verification attempt failed before tests because `/tmp/taxi-release-venv` no longer existed after the environment reset; the shell then fell through to Python 3.14, where dependencies and the editable package were absent. Fix: a fresh Python 3.11.15 environment was created at `/tmp/taxi-binary-audit-venv`, and dependencies plus the editable package were installed successfully with `PYENV_VERSION=3.11.15 python -m venv /tmp/taxi-binary-audit-venv && . /tmp/taxi-binary-audit-venv/bin/activate && python -m pip install -r requirements.txt -e .`.

Verification after the fix:

- `. /tmp/taxi-binary-audit-venv/bin/activate && rm -f artifacts/model.joblib && pytest -q` — 6 passed in 0.61 seconds, with one third-party Starlette/AnyIO deprecation warning.
- `python -m taxi_duration.train --data data/sample_trips.csv --output /tmp/taxi-binary-repair-artifacts` — passed with the same 288/72 chronological split and recorded metrics.
- `MODEL_PATH=/tmp/taxi-binary-repair-artifacts/model.joblib uvicorn taxi_duration.api:app --host 127.0.0.1 --port 8765` — started and shut down normally.
- Health, prediction, and frontend `curl` smoke checks all returned HTTP 200; prediction remained 1203.4 seconds / 20.06 minutes.

Remaining limitations are unchanged: the data is synthetic, external Kaggle training was not exercised, and the UI has route/static smoke coverage rather than multi-browser automation. The local model must be trained before manually starting the API, exactly as ordered in the README.

Pull-request creation was attempted with `gh pr create --title "Add NYC taxi trip-duration MVP without generated binaries" ...` after the repair commit. It could not create the PR because this checkout has no Git remote and GitHub CLI has no authentication (`gh auth login` / `GH_TOKEN` required). No credentials were requested or stored, and no repository settings were changed. The branch is clean and technically ready to push and open once the caller provides its remote/authenticated PR environment.
