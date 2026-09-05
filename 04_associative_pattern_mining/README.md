# Project 4: Associative Pattern Mining

A small, local market-basket MVP: validated JSON transactions flow through a dependency-free Apriori implementation into association rules and a Flask recommendation API/UI. This is a demonstration, not evidence of commercial value.

## Quick start

Run every command from `04_associative_pattern_mining`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m market_basket.pipeline --output outputs/mining_results.json
python -m pytest
flask --app market_basket.app run --debug
```

Open <http://127.0.0.1:5000>. Smoke-test the running API:

```bash
curl -sS -X POST http://127.0.0.1:5000/api/recommend \
  -H 'Content-Type: application/json' -d '{"items":["chips"]}'
```

The output directory is intentionally ignored because mined results are reproducible.

## Configuration and mining

The CLI accepts `--data`, `--min-support`, `--min-confidence`, `--min-lift`, and optional `--output`. Fractions must be in `(0, 1]`; lift must be non-negative. Example:

```bash
python -m market_basket.pipeline --data sample_transactions.json \
  --min-support 0.15 --min-confidence 0.6 --min-lift 1.1 \
  --output outputs/mining_results.json
```

The web app uses environment variables `MIN_SUPPORT`, `MIN_CONFIDENCE`, and `MIN_LIFT` (defaults: `0.15`, `0.5`, and `1.0`). Restart after changing them. To test only the pipeline:

```bash
python -m pytest tests/test_mining.py
```

There is no training step in association-rule mining. The exact equivalent requested “training” command is the pipeline command above, which fits thresholds to the bundled transactions and emits itemsets/rules.

## API

`POST /api/recommend` accepts `{"items":["chips"]}`. Items are trimmed, lowercased, deduplicated, and checked against the catalog. Each result includes the recommended item, triggering rule, support, confidence, and lift. Rules are ranked by lift, confidence, then support; only the strongest rule per item is returned. `GET /health` is the health check.

## Interpreting rules responsibly

* **Support** is the fraction of all baskets containing both sides. Low-support rules can be coincidences, even with high confidence.
* **Confidence** is the fraction of antecedent baskets also containing the consequent. A popular consequent can make confidence look impressive.
* **Lift** compares confidence with the consequent's baseline frequency. Lift near 1 indicates little association; lift below 1 indicates negative association. Lift is not causation.
* **Redundant rules** may add an antecedent item without materially changing confidence/lift, or yield the same recommendation. The endpoint collapses multiple rules to one strongest explanation per item, but analysts should still compare nested antecedents.
* **Misleading rules** can reflect promotions, product placement, seasonality, duplicated customers, data collection, or tiny counts. The sample is synthetic and deliberately small.
* **Low-value rules** may recommend items already present, obvious substitutes, unavailable items, or products whose operational cost outweighs benefit. The endpoint removes already-present items, but has no inventory, margin, user, or time context.

## Scope

The bundled 20-basket synthetic dataset makes behavior inspectable and fast. It is not representative customer data. The in-memory exhaustive candidate generation is appropriate only for this demo; larger data needs sparse structures, FP-Growth/distributed mining, holdout evaluation, monitoring, privacy review, and business constraints. See [CRISP_DM_REPORT.md](CRISP_DM_REPORT.md) and [FINAL_REPORT.md](FINAL_REPORT.md).
