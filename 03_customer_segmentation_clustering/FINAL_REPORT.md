# Final Report

## Delivered vertical slice

- Deterministic synthetic-data generator (240 unique records; no PII or external services).
- Validation, deduplication, imputation, bounds cleaning, categorical encoding, and numeric scaling.
- K-Means sweep over `k=2..6`, agglomerative comparison, silhouette and Davies-Bouldin metrics.
- PCA visualization, cluster summaries, human-readable post-hoc personas, persisted model, and FastAPI inference.
- Automated cleaning, pipeline, artifact, health, and prediction smoke tests.

## Exact verification record (2026-09-01 UTC)

All commands were run from `03_customer_segmentation_clustering` in the provided environment using Python 3.14. The first exact-version install attempt was cancelled when pandas 2.3.1 lacked a wheel for Python 3.14; dependency ranges were then adjusted to compatible major versions.

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.pipeline --data data/customers.csv --output artifacts
.venv/bin/python -m pytest -q
```

The successful install resolved FastAPI 0.141.1, pandas 3.0.5, scikit-learn 1.9.0, and their dependencies. Pipeline result: 241 raw rows, 240 cleaned rows, selected `k=3`; PCA explained variance ratios were `0.581932` and `0.211656`. Tests: **2 passed in 3.72s**, with one environment/dependency deprecation warning from FastAPI's `TestClient` compatibility layer.

### Verified metrics

| Method | k | Silhouette | Davies-Bouldin |
|---|---:|---:|---:|
| K-Means | 2 | 0.452062 | 0.862229 |
| K-Means | 3 | **0.515841** | **0.788176** |
| K-Means | 4 | 0.430508 | 1.125551 |
| K-Means | 5 | 0.351056 | 1.274375 |
| K-Means | 6 | 0.254567 | 1.394476 |
| Agglomerative | 3 | 0.515841 | 0.788176 |

The selected groups contained 79, 80, and 81 customers. Their summaries correspond to mature/budget/lower-engagement; younger/budget/frequent-high-spend; and mature/higher-income/lower-engagement personas. These labels simplify continuous averages and must not be treated as facts about individuals.

## API smoke test

The automated test used FastAPI `TestClient`, verified `/health` reported `model_ready=true`, and submitted a valid example to `/predict`, which returned HTTP 200 with exactly `cluster` and `persona`. A separate live smoke test ran `.venv/bin/uvicorn src.api:app --host 127.0.0.1 --port 8765`, then the README-equivalent curl requests: health returned `{"status":"ok","model_ready":true}` and prediction returned `{"cluster":1,"persona":"younger budget frequent, high-spend customers"}` with HTTP 200 in the server log.

Final hygiene checks used `git status --short`, `find . -path './.venv' -prune -o -path './artifacts' -prune -o -path './data' -prune -o -type f -printf '%s %p\n' | sort -nr | head`, and `git diff --check`. They showed changes exclusively in this project, no tracked/generated large files or secrets, and no whitespace errors. The virtual environment, generated sample, artifacts, bytecode, and pytest cache are excluded by `.gitignore`.

## Assumptions and limitations

- Synthetic populations and seeded defects validate engineering behavior, not market validity or business ROI.
- Euclidean clusters favor roughly convex groups and may be sensitive to outliers, feature choices, weighting, seed, and changing customer behavior.
- Region one-hot columns influence distance; its business relevance and potential proxy effects require review.
- Silhouette and Davies-Bouldin are internal criteria. External validation, temporal holdouts, bootstrap stability, fairness review, and campaign experiments remain necessary.
- The global maximum silhouette in the tested range determines `k`; the range itself is a modeling assumption. The apparent business interpretability of three segments did not determine selection.
- Persona text is rule-based from cluster means relative to overall means. It intentionally avoids prescriptive or sensitive targeting claims.
- Generated data, plots, metrics, and model files are ignored to avoid committing reproducible artifacts and build output.

## Final release audit (2026-09-01 UTC)

The release audit began from a clean Git working tree. No critical end-to-end defect was found, so no application behavior or major feature was changed. The README commands were checked against the module names, CLI arguments, paths, and endpoints in the implementation and then executed from the project directory.

### Commands and results

1. `python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt` — passed. Installation resolved FastAPI 0.141.1, pandas 3.0.5, NumPy 2.5.2, scikit-learn 1.9.0, and the remaining declared dependencies.
2. `rm -rf data artifacts .pytest_cache src/__pycache__ tests/__pycache__` — passed; this removed reproducible outputs before verification.
3. `.venv/bin/python -m src.pipeline --data data/customers.csv --output artifacts` — passed. It regenerated the sample and all artifacts, processed 241 raw/240 clean rows, selected `k=3`, and reported PCA variance ratios `0.5819315078300529` and `0.21165577627134707`.
4. `.venv/bin/python -m pytest -q` — passed: **2 passed in 4.26s**. One non-failing `StarletteDeprecationWarning` reports that FastAPI's current `TestClient` compatibility import uses `httpx`; it does not affect the tested API behavior.
5. `.venv/bin/uvicorn src.api:app --host 127.0.0.1 --port 8765` — passed. Uvicorn completed startup and graceful shutdown.
6. `curl -fsS http://127.0.0.1:8765/health` — passed with `{"status":"ok","model_ready":true}`.
7. `curl -fsS -X POST http://127.0.0.1:8765/predict -H 'content-type: application/json' -d '{"age":35,"annual_income":60000,"spending_score":70,"purchase_frequency":10,"region":"East"}'` — passed with `{"cluster":1,"persona":"younger budget frequent, high-spend customers"}`.
8. `find . -path './.venv' -prune -o -type f \( -name package.json -o -name vite.config.js -o -name vite.config.ts \) -print` — returned no files. A frontend build is **not applicable**: this MVP intentionally exposes FastAPI plus its generated interactive `/docs` UI and contains no separately built frontend.
9. `git check-ignore -v .venv data/customers.csv artifacts/model.joblib .pytest_cache src/__pycache__` — passed; every generated/cache path was ignored.
10. `git ls-files -z . | xargs -0 -r stat -c '%s %n' | sort -nr` — passed; the largest tracked project file was about 4 KB, with no large dataset or generated artifact.
11. `rg -n --hidden -g '!.venv/**' -g '!artifacts/**' -g '!data/**' -g '!*.pyc' '(api[_-]?key|secret|token|password)\s*[:=]' .` — found no suspected secret assignments.
12. `git ls-files . | rg '(^|/)(artifacts|data|\.venv|\.pytest_cache|__pycache__|node_modules|dist|build)(/|$)|\.pyc$'` — found no tracked generated output or cache.
13. `git diff --check` — passed with no whitespace errors.

### Failures, fixes, and remaining limitations

There were no command failures in this final audit and therefore no critical code fix was required. The earlier dependency-resolution failure and its compatible-version-range fix remain documented above rather than being concealed. Remaining release limitations are the synthetic-data and internal-validation limitations listed in the preceding section, the non-failing test-client deprecation warning, absence of a standalone frontend by design, and dependency ranges that permit compatible updates instead of providing a fully locked transitive environment.
