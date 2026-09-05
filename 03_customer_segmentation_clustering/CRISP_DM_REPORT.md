# CRISP-DM Report

## 1. Business understanding

The MVP explores whether customers can be grouped into understandable behavioral cohorts for aggregate campaign planning. Success means a reproducible solution with reasonable internal cohesion/separation, stable operational preprocessing, and summaries a stakeholder can review. Clusters are hypotheses—not ground truth—and must not drive credit, pricing, access, or other high-impact individual decisions.

## 2. Data understanding

No external or personal data is used. A seeded generator creates 240 fictional customers from three deliberately overlapping profiles. Features are age, annual income, spending score, purchase frequency, and region. It inserts one duplicate, two missing values, and one out-of-range score, making 241 raw records and allowing the cleaning path to be tested. Because the generating process contains three profiles, results will look cleaner than real customer data and are not evidence of production value.

## 3. Data preparation

The pipeline checks required columns, deduplicates by `customer_id`, converts numerics, median-imputes missing numerics, clips values to documented feasible ranges, and replaces absent/unrecognized regions with `Unknown`. It standardizes numeric values so income cannot dominate Euclidean distance, and one-hot encodes region with unknown-category tolerance. The fitted transformer is saved with the model, preventing training/serving skew.

## 4. Modeling

K-Means is fitted for `k=2,3,4,5,6` with seed 42 and `n_init=20`. Agglomerative clustering is evaluated at the selected K-Means `k` to test another inductive bias. K-Means remains the deployed method because it naturally supports prediction for new rows; hierarchical clustering does not offer an equivalent native out-of-sample prediction.

## 5. Evaluation

Selection maximizes silhouette (higher is better), with Davies-Bouldin (lower is better) as a deterministic tie-break. In the verified sample run, `k=3` won (silhouette `0.515841`, Davies-Bouldin `0.788176`). Although this aligns with three useful personas, names and perceived business attractiveness were created only afterward and played no role in selection.

Tradeoffs matter: `k=2` is simpler to operationalize but merges meaningful structure and scored worse (`0.452062` silhouette, `0.862229` Davies-Bouldin). Values `k=4..6` offer finer targeting but produced progressively weaker cohesion/separation in this run. Internal indices do not prove business lift, stability, fairness, or causal response. PCA's first two components explain about `79.36%` combined variance and are useful for visualization, not model selection.

## 6. Deployment

FastAPI exposes health and prediction endpoints. The bundle includes preprocessing, K-Means, and post-hoc persona labels. Deployment monitoring should cover schema/range failures, feature and cluster-size drift, periodic stability across seeds/time windows, and outcome/fairness review. Retraining should be versioned and require human approval. The current artifact is local and reproducible rather than committed.
