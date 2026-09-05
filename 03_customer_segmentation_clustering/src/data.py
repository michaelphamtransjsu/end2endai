"""Deterministic sample data generation and validation."""
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = {"age", "annual_income", "spending_score", "purchase_frequency", "region"}
REGIONS = ("North", "South", "East", "West")


def generate_sample(path: Path, rows: int = 240, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic, non-identifying customers with intentionally imperfect rows."""
    if rows < 30:
        raise ValueError("rows must be at least 30")
    rng = np.random.default_rng(seed)
    profiles = [(28, 42_000, 82, 16), (46, 105_000, 68, 9), (60, 58_000, 30, 4)]
    records = []
    for i in range(rows):
        age, income, score, frequency = profiles[i % len(profiles)]
        records.append({
            "customer_id": f"C{i + 1:04d}",
            "age": round(rng.normal(age, 5), 0),
            "annual_income": round(rng.normal(income, income * .12), 2),
            "spending_score": round(rng.normal(score, 8), 1),
            "purchase_frequency": round(rng.normal(frequency, 2), 1),
            "region": rng.choice(REGIONS),
        })
    df = pd.DataFrame(records)
    # Reproducible defects exercise cleaning without hiding the raw-data contract.
    df.loc[0, "annual_income"] = np.nan
    df.loc[1, "region"] = None
    df.loc[2, "spending_score"] = 130
    df = pd.concat([df, df.iloc[[3]]], ignore_index=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    clean = df.drop_duplicates(subset="customer_id").copy()
    numeric = ["age", "annual_income", "spending_score", "purchase_frequency"]
    for col in numeric:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
        clean[col] = clean[col].fillna(clean[col].median())
    clean["age"] = clean["age"].clip(18, 100)
    clean["annual_income"] = clean["annual_income"].clip(lower=0)
    clean["spending_score"] = clean["spending_score"].clip(0, 100)
    clean["purchase_frequency"] = clean["purchase_frequency"].clip(lower=0)
    clean["region"] = clean["region"].where(clean["region"].isin(REGIONS), "Unknown")
    return clean
