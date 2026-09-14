import json

import numpy as np
import pandas as pd
import pytest

from skills_lab.analysis import engineered_features, pca_projection, run_analysis
from skills_lab.data import DATASETS, clean, load_dataset, validate
from skills_lab.reporting import create_outputs


@pytest.mark.parametrize("name", DATASETS)
def test_end_to_end_analysis(name):
    dataset = load_dataset(name)
    results = run_analysis(dataset)
    assert len(dataset.frame) > 100
    assert results.test_rows > 0
    assert np.isfinite([results.supervised_value, results.silhouette, results.p_value]).all()
    assert pca_projection(dataset).shape == (len(dataset.frame), 3)
    assert len(engineered_features(dataset).columns) == len(dataset.frame.columns) + 1


def test_cleaning_and_validation():
    dirty = pd.DataFrame({"x": [1.0, np.nan, 1.0], "target": [0, 1, 0]})
    cleaned = clean(dirty)
    validate(cleaned, "target")
    assert cleaned.shape == (2, 2)
    assert not cleaned.isna().any().any()


def test_unknown_dataset():
    with pytest.raises(KeyError):
        load_dataset("unknown")


def test_reporting_smoke(tmp_path):
    result = create_outputs("iris", tmp_path)
    assert (tmp_path / "iris_pca.png").stat().st_size > 0
    payload = json.loads((tmp_path / "iris_metrics.json").read_text())
    assert payload["supervised_metric"] == result["supervised_metric"]
