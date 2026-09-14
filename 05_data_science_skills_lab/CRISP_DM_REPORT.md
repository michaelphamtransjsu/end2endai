# CRISP-DM Report

## 1. Business understanding

The lab's objective is educational: make ten common data-science capabilities
inspectable in one small, locally runnable project. Success means a learner can
select known data, trace preprocessing, run supervised and unsupervised methods,
inspect honest evaluation outputs, and regenerate reports without paid services.
The outputs are demonstrations and must not be treated as clinical predictions.

## 2. Data understanding

Three scikit-learn datasets exercise distinct shapes and tasks: Iris is a
three-class flower dataset; Breast Cancer Wisconsin (Diagnostic) is a binary
classification dataset; Diabetes is a continuous-target regression dataset.
Loading uses sklearn's `as_frame=True`, preserving documented feature names.
The dashboard and descriptive statistics expose row counts, ranges, quartiles,
and targets. These curated data are small and mostly clean, so the cleaning API
is additionally tested with synthetic missing and duplicate rows.

## 3. Data preparation

The contract rejects empty frames, missing targets, duplicate names, and
non-numeric columns. Cleaning removes exact duplicates and median-imputes numeric
missing values. Modelling separates the target before processing. Pipelines fit
imputation and standardization on training data, preventing test-set leakage.
The educational feature step adds predictor-only row mean and L2 norm. PCA and
K-means use standardized predictor values.

## 4. Modelling

Classification uses logistic regression; regression uses ridge regression.
Both use a 75/25 fixed train/test split, with classification stratified by the
target. K-means demonstrates unsupervised learning with three clusters and a
fixed initialization seed. PCA creates a two-dimensional visualization but is
not fed into the supervised estimators.

## 5. Evaluation

Classification reports held-out accuracy, regression reports held-out root mean
squared error, and clustering reports silhouette coefficient. Classification
datasets receive a one-way ANOVA demonstration on the first predictor across
target groups; the regression dataset receives a Pearson correlation test with
the target. Automated tests require finite results and exercise every dataset.
These metrics are not cross-validated benchmarks, and no performance threshold
is claimed. Labels make classification metrics interpretable; regression RMSE
remains in the target's units.

## 6. Deployment

Deployment is local and educational: a CLI regenerates version-ignored PNG/JSON
artifacts, while Streamlit recomputes and displays analyses interactively.
Dependencies are pinned, randomness is fixed, and exact operations are in the
README. Monitoring, authentication, persistence, and production model serving
are intentionally out of scope. Future work could add repeated cross-validation,
confidence intervals, accessibility checks, and dataset-specific cluster-count
selection.
