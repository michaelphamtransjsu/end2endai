"""Test fixtures that build generated artifacts outside the repository."""
from pathlib import Path

import pytest

from taxi_duration import api
from taxi_duration.train import run


@pytest.fixture(scope="session", autouse=True)
def trained_test_model(tmp_path_factory: pytest.TempPathFactory):
    """Train the API model in a temporary directory so tests need no binary artifact."""
    project_root = Path(__file__).resolve().parents[1]
    artifact_dir = tmp_path_factory.mktemp("artifacts")
    run(project_root / "data/sample_trips.csv", artifact_dir)
    api.MODEL_PATH = artifact_dir / "model.joblib"
    api._model = None
    yield
    api._model = None
