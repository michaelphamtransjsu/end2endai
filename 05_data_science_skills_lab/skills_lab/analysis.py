"""EDA, feature engineering, statistics, modelling, and evaluation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import f_oneway, pearsonr
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (accuracy_score, mean_squared_error,
                             silhouette_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data import Dataset


RANDOM_STATE = 42


@dataclass(frozen=True)
class Results:
    supervised_metric: str
    supervised_value: float
    silhouette: float
    statistical_test: str
    statistic: float
    p_value: float
    test_rows: int


def split_xy(dataset: Dataset):
    return dataset.frame.drop(columns=dataset.target), dataset.frame[dataset.target]


def describe(dataset: Dataset) -> pd.DataFrame:
    """Return standard descriptive statistics without changing the data."""
    return dataset.frame.describe().T


def engineered_features(dataset: Dataset) -> pd.DataFrame:
    """Add transparent row-level magnitude and mean features."""
    x, _ = split_xy(dataset)
    result = x.copy()
    result["feature_mean"] = x.mean(axis=1)
    result["feature_l2_norm"] = np.sqrt((x**2).sum(axis=1))
    return result


def _supervised(dataset: Dataset) -> tuple[str, float, int]:
    x, y = split_xy(dataset)
    stratify = y if dataset.task == "classification" else None
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=.25, random_state=RANDOM_STATE, stratify=stratify
    )
    estimator = LogisticRegression(max_iter=1000) if dataset.task == "classification" else Ridge()
    model = Pipeline([("imputer", SimpleImputer()), ("scale", StandardScaler()), ("model", estimator)])
    model.fit(x_train, y_train)
    prediction = model.predict(x_test)
    if dataset.task == "classification":
        return "accuracy", float(accuracy_score(y_test, prediction)), len(y_test)
    return "root_mean_squared_error", float(mean_squared_error(y_test, prediction) ** .5), len(y_test)


def _statistics(dataset: Dataset) -> tuple[str, float, float]:
    x, y = split_xy(dataset)
    if dataset.task == "classification":
        groups = [x.loc[y == label, x.columns[0]] for label in sorted(y.unique())]
        stat, p = f_oneway(*groups)
        return f"one-way ANOVA: {x.columns[0]} by target", float(stat), float(p)
    stat, p = pearsonr(x.iloc[:, 0], y)
    return f"Pearson correlation: {x.columns[0]} and target", float(stat), float(p)


def run_analysis(dataset: Dataset) -> Results:
    """Run deterministic supervised, clustering, and statistical examples."""
    metric, value, rows = _supervised(dataset)
    x, _ = split_xy(dataset)
    scaled = StandardScaler().fit_transform(SimpleImputer().fit_transform(x))
    labels = KMeans(n_clusters=3, random_state=RANDOM_STATE, n_init=10).fit_predict(scaled)
    silhouette = float(silhouette_score(scaled, labels))
    test, statistic, p = _statistics(dataset)
    return Results(metric, value, silhouette, test, statistic, p, rows)


def pca_projection(dataset: Dataset) -> pd.DataFrame:
    """Create a standardized two-dimensional PCA projection for plotting."""
    x, y = split_xy(dataset)
    scaled = StandardScaler().fit_transform(x)
    points = PCA(n_components=2).fit_transform(scaled)
    return pd.DataFrame({"PC1": points[:, 0], "PC2": points[:, 1], "target": y.to_numpy()})
