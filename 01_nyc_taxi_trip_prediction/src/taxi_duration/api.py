"""FastAPI service and static demo UI."""
from __future__ import annotations
import os
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .features import RAW_FEATURES

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "artifacts/model.joblib"))
app = FastAPI(title="NYC Taxi Duration MVP", version="0.1.0")
_model = None

class Trip(BaseModel):
    pickup_datetime: str
    pickup_latitude: float = Field(ge=40.45, le=41.0)
    pickup_longitude: float = Field(ge=-74.3, le=-73.65)
    dropoff_latitude: float = Field(ge=40.45, le=41.0)
    dropoff_longitude: float = Field(ge=-74.3, le=-73.65)
    passenger_count: int = Field(ge=1, le=8)

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists(): raise RuntimeError("Model missing; run training first")
        _model = joblib.load(MODEL_PATH)
    return _model

@app.get("/health")
def health(): return {"status": "ok", "model_available": MODEL_PATH.exists()}

@app.post("/predict")
def predict(trip: Trip):
    try:
        seconds = max(1.0, float(get_model().predict(pd.DataFrame([trip.model_dump()])[RAW_FEATURES])[0]))
        return {"predicted_duration_seconds": round(seconds, 1), "predicted_duration_minutes": round(seconds / 60, 2)}
    except (ValueError, RuntimeError) as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/", include_in_schema=False)
def index(): return FileResponse(ROOT / "frontend/index.html")
