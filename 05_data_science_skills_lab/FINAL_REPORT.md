# Final Report

## Delivered scope

The project implements a verified vertical slice over three datasets bundled
with scikit-learn. Reusable modules cover ingestion through reporting, a CLI
generates saved visual and JSON artifacts, and a Streamlit dashboard presents
the same analyses. The skills mapping and CRISP-DM report document traceability.

## Reproducibility

- Python dependencies are pinned in `requirements.txt`.
- The train/test split and K-means initialization use seed 42.
- Source data ship with scikit-learn and require no network request at runtime.
- Generated `outputs/`, caches, and virtual environments are ignored and are not
  repository deliverables.

## Verification record (2026-09-01 UTC)

The following commands were run from `05_data_science_skills_lab`. Results below
must reflect the final working tree and are completed immediately before commit.

| Command | Result |
| --- | --- |
| `python -m pip install -r requirements.txt` | Passed; all eight pinned direct dependencies installed/satisfied (pip emitted its standard root-user warning in this disposable environment) |
| `python run_analysis.py --output-dir outputs` | Passed; created six ignored artifacts (PNG and JSON for each of three datasets) and printed computed metrics |
| `python -m pytest -q` | Passed; 6 tests passed in 7.67 seconds |
| `python -m streamlit run app.py --server.headless true --server.port 8501` plus `curl -fsS http://127.0.0.1:8501/_stcore/health` and page request | Passed; health returned `ok`, index HTML returned, then server was stopped cleanly |

## Assumptions and limitations

- Python 3.11 or a compatible recent Python is available.
- All predictors in the selected bundled datasets are numeric.
- A single 25% holdout provides a concise deterministic example, not robust
  performance estimation. No metric is presented as a production benchmark.
- Statistical tests are demonstrations; their assumptions and multiple-testing
  implications are not exhaustively diagnosed, and no causal conclusion follows.
- K-means uses three clusters consistently for pedagogy rather than claiming
  that three is optimal for every dataset.
- The dashboard is smoke-tested for server startup; browser interaction and
  screenshot-based visual regression are outside the automated suite.
- No external agent-skill package or installation instructions were used.
