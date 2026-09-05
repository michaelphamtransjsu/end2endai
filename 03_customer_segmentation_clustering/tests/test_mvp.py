from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from src.data import generate_sample, validate_and_clean
from src.pipeline import run


def test_cleaning_removes_duplicate_and_bounds(tmp_path):
    raw = generate_sample(tmp_path / "sample.csv", rows=30)
    clean = validate_and_clean(raw)
    assert len(clean) == 30
    assert not clean.isna().any().any()
    assert clean.spending_score.between(0, 100).all()


def test_pipeline_and_api(tmp_path, monkeypatch):
    output = tmp_path / "artifacts"
    metadata = run(tmp_path / "customers.csv", output)
    assert 2 <= metadata["selected_k"] <= 6
    assert {"model.joblib", "metrics.csv", "personas.csv", "pca_segments.png"} <= {p.name for p in output.iterdir()}
    metrics = pd.read_csv(output / "metrics.csv")
    assert len(metrics) == 6
    import src.api as api
    monkeypatch.setattr(api, "MODEL_PATH", output / "model.joblib")
    api.load_model.cache_clear()
    client = TestClient(api.app)
    assert client.get("/health").json()["model_ready"] is True
    response = client.post("/predict", json={"age": 35, "annual_income": 60000, "spending_score": 70, "purchase_frequency": 10, "region": "East"})
    assert response.status_code == 200
    assert set(response.json()) == {"cluster", "persona"}