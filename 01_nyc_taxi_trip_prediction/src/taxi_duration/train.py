"""Train and evaluate models with a chronological holdout."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_log_error
from .features import RAW_FEATURES, engineer_features, validate_frame
from .model import DurationPipeline

def metrics(y, pred):
    pred = np.maximum(pred, 1)
    return {"mae_seconds": round(float(mean_absolute_error(y, pred)), 3), "rmsle": round(float(np.sqrt(mean_squared_log_error(y, pred))), 5)}

def run(data_path: Path, output_dir: Path):
    df = validate_frame(pd.read_csv(data_path), require_target=True).sort_values("pickup_datetime")
    cut = int(len(df) * .8)
    if len(df) < 50 or cut == len(df): raise ValueError("At least 50 rows are required")
    train, test = df.iloc[:cut], df.iloc[cut:]
    X_train, X_test = train[RAW_FEATURES], test[RAW_FEATURES]
    baseline = DummyRegressor(strategy="median").fit(engineer_features(X_train), train.trip_duration)
    baseline_pred = baseline.predict(engineer_features(X_test))
    model = DurationPipeline().fit(X_train, train.trip_duration)
    improved_pred = model.predict(X_test)
    result = {"split": "chronological_80_20", "train_rows": len(train), "test_rows": len(test), "train_end": str(train.pickup_datetime.max()), "test_start": str(test.pickup_datetime.min()), "baseline": metrics(test.trip_duration, baseline_pred), "improved": metrics(test.trip_duration, improved_pred)}
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_dir / "model.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--data", type=Path, default=Path("data/sample_trips.csv")); p.add_argument("--output", type=Path, default=Path("artifacts")); a=p.parse_args(); run(a.data,a.output)
if __name__ == "__main__": main()
