"""FastAPI inference service."""
import os
from functools import lru_cache
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.getenv("MODEL_PATH", "artifacts/model.joblib"))
app = FastAPI(title="Customer Segmentation API", version="1.0.0")


class Customer(BaseModel):
    age: float = Field(ge=18, le=100)
    annual_income: float = Field(ge=0)
    spending_score: float = Field(ge=0, le=100)
    purchase_frequency: float = Field(ge=0)
    region: str


@lru_cache
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Run the analysis pipeline first")
    return joblib.load(MODEL_PATH)


@app.get("/health")
def health():
    return {"status": "ok", "model_ready": MODEL_PATH.exists()}


@app.post("/predict")
def predict(customer: Customer):
    try:
        bundle = load_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    frame = pd.DataFrame([customer.model_dump()])
    cluster = int(bundle["model"].predict(bundle["preprocessor"].transform(frame))[0])
    return {"cluster": cluster, "persona": bundle["personas"][cluster]}
