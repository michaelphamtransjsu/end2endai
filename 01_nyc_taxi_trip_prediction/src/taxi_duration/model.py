"""Serializable estimator that owns preprocessing and prediction."""
from __future__ import annotations
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import HistGradientBoostingRegressor
from .features import engineer_features

class DurationPipeline(BaseEstimator, RegressorMixin):
    def __init__(self, random_state: int = 42): self.random_state = random_state
    def fit(self, X, y):
        self.model_ = HistGradientBoostingRegressor(max_iter=120, max_leaf_nodes=15, learning_rate=.07, l2_regularization=1.0, random_state=self.random_state)
        self.model_.fit(engineer_features(X), y)
        return self
    def predict(self, X): return self.model_.predict(engineer_features(X))
