"""Validation and deterministic feature engineering."""
from __future__ import annotations
import numpy as np
import pandas as pd

RAW_FEATURES = ["pickup_datetime", "pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude", "passenger_count"]
NYC_BOUNDS = {"latitude": (40.45, 41.0), "longitude": (-74.3, -73.65)}

def validate_frame(frame: pd.DataFrame, require_target: bool = False) -> pd.DataFrame:
    required = RAW_FEATURES + (["trip_duration"] if require_target else [])
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    out = frame.copy()
    out["pickup_datetime"] = pd.to_datetime(out["pickup_datetime"], errors="raise")
    numeric = required[1:]
    out[numeric] = out[numeric].apply(pd.to_numeric, errors="raise")
    if not out[numeric].replace([np.inf, -np.inf], np.nan).notna().all().all():
        raise ValueError("Numeric values must be finite and non-null")
    for col in ("pickup_latitude", "dropoff_latitude"):
        if not out[col].between(*NYC_BOUNDS["latitude"]).all(): raise ValueError(f"{col} outside NYC bounds")
    for col in ("pickup_longitude", "dropoff_longitude"):
        if not out[col].between(*NYC_BOUNDS["longitude"]).all(): raise ValueError(f"{col} outside NYC bounds")
    if not out["passenger_count"].between(1, 8).all(): raise ValueError("passenger_count must be 1..8")
    if require_target and not out["trip_duration"].between(30, 10800).all(): raise ValueError("trip_duration must be 30..10800 seconds")
    return out

def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = validate_frame(frame)
    lat1, lat2 = np.radians(df.pickup_latitude), np.radians(df.dropoff_latitude)
    dlat = lat2 - lat1
    dlon = np.radians(df.dropoff_longitude - df.pickup_longitude)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    dt = df.pickup_datetime
    return pd.DataFrame({
        "distance_km": 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))),
        "hour": dt.dt.hour, "day_of_week": dt.dt.dayofweek,
        "is_weekend": (dt.dt.dayofweek >= 5).astype(int),
        "is_rush_hour": dt.dt.hour.isin([7, 8, 9, 16, 17, 18]).astype(int),
        "passenger_count": df.passenger_count.astype(float),
        "pickup_latitude": df.pickup_latitude, "pickup_longitude": df.pickup_longitude,
        "dropoff_latitude": df.dropoff_latitude, "dropoff_longitude": df.dropoff_longitude,
    }, index=df.index)
