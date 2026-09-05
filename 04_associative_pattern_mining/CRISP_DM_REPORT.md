# CRISP-DM Report

## 1. Business understanding

The demonstration objective is to suggest an unseen basket addition using transparent co-occurrence patterns. A useful output is a rule with observable support, confidence, and lift, not a claim that a recommendation causes purchases. Real acceptance criteria (incremental conversion, margin, availability, and customer experience) require a representative dataset and controlled evaluation and are outside this MVP.

## 2. Data understanding

`sample_transactions.json` contains 20 synthetic baskets across grocery groupings. Each row is a basket and each string is an item. The intentionally small data permits manual inspection but cannot describe a population, seasons, stores, quantities, order, customer identity, price, or time. No performance or business inference should be drawn from it.

## 3. Data preparation

The loader requires a non-empty top-level list and non-empty basket lists containing only non-blank strings. It trims whitespace, lowercases names, and converts each basket to a set, so repeated instances mean presence rather than quantity. Invalid records fail the pipeline with an indexed message instead of being silently discarded. The production decision between rejection, quarantine, or correction would need a data contract.

## 4. Modeling

Apriori starts from individual products, retains itemsets meeting minimum fractional support, joins each surviving level, and prunes candidates whose subsets were not frequent. Rules split each frequent itemset into every non-empty antecedent/consequent and retain configurable minimum confidence and lift. Defaults are support 0.15, confidence 0.50, and lift 1.0. These are demonstration settings, not optimized thresholds.

Recommendations match rules whose antecedent is a subset of the submitted basket, remove items already present, keep the strongest rule for each item, and rank by lift, confidence, support, then name. This deterministic policy is explainable but does not optimize diversity or utility.

## 5. Evaluation

Automated tests cover normalization, invalid data, known support/confidence/lift arithmetic, invalid thresholds, recommendation behavior, API errors, health, and UI delivery. Running the full pipeline verifies integration on bundled data. This is functional verification only. There is no holdout period, baseline comparison, statistical uncertainty, leakage study, online experiment, or performance benchmark.

Rule review must reject coincidental low-support patterns, popular-consequent confidence, lift near one, nested/redundant antecedents, and recommendations lacking stock or economic value. Associations do not establish causality. Before production, evaluate temporal holdouts, coverage, stability, novelty, inventory eligibility, incremental outcomes, subgroup harms, and latency using real data.

## 6. Deployment

Flask serves a local interactive page, `POST /api/recommend`, and `GET /health`. Mining occurs once at process start. Environment variables configure thresholds. This avoids paid services and persistent user data. Production work includes an application server, authentication/rate limiting as appropriate, schema/version controls, scheduled retraining, artifact lineage, observability, rollback, privacy/security review, and drift monitoring.
