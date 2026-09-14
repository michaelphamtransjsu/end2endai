"""Dataset loading, validation, and deterministic cleaning."""

from dataclasses import dataclass

import pandas as pd
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris


@dataclass(frozen=True)
class Dataset:
    name: str
    frame: pd.DataFrame
    target: str
    task: str


DATASETS = ("iris", "breast_cancer", "diabetes")
_LOADERS = {
    "iris": (load_iris, "classification"),
    "breast_cancer": (load_breast_cancer, "classification"),
    "diabetes": (load_diabetes, "regression"),
}


def validate(frame: pd.DataFrame, target: str) -> None:
    """Raise a useful error when the basic tabular contract is violated."""
    if frame.empty or target not in frame:
        raise ValueError("dataset must be non-empty and contain its target")
    if frame.columns.duplicated().any():
        raise ValueError("duplicate column names are not supported")
    if not all(pd.api.types.is_numeric_dtype(frame[c]) for c in frame):
        raise TypeError("all bundled dataset columns must be numeric")


def clean(frame: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows and median-impute numeric missing values."""
    result = frame.drop_duplicates().copy()
    numeric = result.select_dtypes("number").columns
    result[numeric] = result[numeric].fillna(result[numeric].median())
    return result


def load_dataset(name: str) -> Dataset:
    """Load a bundled sklearn dataset as a validated, clean DataFrame."""
    if name not in _LOADERS:
        raise KeyError(f"unknown dataset {name!r}; choose from {DATASETS}")
    loader, task = _LOADERS[name]
    bunch = loader(as_frame=True)
    target = bunch.target.name or "target"
    frame = clean(bunch.frame)
    validate(frame, target)
    return Dataset(name, frame, target, task)
