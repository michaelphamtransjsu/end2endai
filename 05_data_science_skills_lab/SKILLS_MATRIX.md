# Skills Matrix

| Skill | Implementation | Verification / user surface |
| --- | --- | --- |
| Data loading and validation | `skills_lab.data.load_dataset` uses sklearn's bundled frame interface; `validate` checks shape, target, duplicate names, and numeric types | `test_cleaning_and_validation`; dashboard “Validated data” |
| Data cleaning | `clean` drops duplicate rows and median-imputes numeric values without mutating input | Cleaning test with duplicates and a missing value |
| Exploratory data analysis | `analysis.describe` supplies count, location, spread, and quantiles | EDA dashboard tab |
| Feature engineering | `engineered_features` adds row mean and L2 norm from predictors only | Feature engineering dashboard tab and all-dataset tests |
| Statistical analysis | One-way ANOVA for classification; Pearson correlation for regression | Statistic and p-value in CLI JSON and dashboard |
| Supervised learning | Standardized logistic regression (classification) and ridge regression | Fixed train/test evaluation for all three datasets |
| Unsupervised learning | Standardized three-cluster K-means and two-component PCA | Silhouette metric and PCA visualization |
| Data visualization | Seaborn PCA scatter chart | Interactive Streamlit figure and reproducible PNGs |
| Model evaluation | Stratified classification split, accuracy; regression split, RMSE; clustering silhouette | `Results` object, JSON report, tests, dashboard metrics |
| Reproducibility and reporting | Pinned dependencies, seed 42, CLI, JSON reports, closed figures, documentation | `requirements.txt`, `reporting.py`, `FINAL_REPORT.md` |

All implementations are local. No third-party agent-skill package is referenced
or installed.
