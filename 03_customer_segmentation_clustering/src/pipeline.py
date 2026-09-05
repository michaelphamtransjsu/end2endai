"""Train, evaluate, explain, and persist clustering models."""
import argparse
import json
from pathlib import Path
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .data import generate_sample, validate_and_clean

NUMERIC = ["age", "annual_income", "spending_score", "purchase_frequency"]
CATEGORICAL = ["region"]


def preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC),
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
    ])


def persona(row: pd.Series, overall: pd.Series) -> str:
    age = "younger" if row.age < overall.age else "mature"
    income = "higher-income" if row.annual_income >= overall.annual_income else "budget"
    engagement = "frequent, high-spend" if row.spending_score >= overall.spending_score and row.purchase_frequency >= overall.purchase_frequency else "lower-engagement"
    return f"{age} {income} {engagement} customers"


def run(data_path: Path, output: Path, seed: int = 42) -> dict:
    if not data_path.exists():
        generate_sample(data_path, seed=seed)
    raw = pd.read_csv(data_path)
    df = validate_and_clean(raw)
    prep = preprocessor()
    x = prep.fit_transform(df[NUMERIC + CATEGORICAL])
    experiments = []
    fitted = {}
    for k in range(2, 7):
        model = KMeans(n_clusters=k, random_state=seed, n_init=20)
        labels = model.fit_predict(x)
        experiments.append({"method": "kmeans", "k": k, "silhouette": float(silhouette_score(x, labels)), "davies_bouldin": float(davies_bouldin_score(x, labels))})
        fitted[k] = (model, labels)
    # Statistical selection is explicit and deterministic; personas are not an input.
    winner = max(experiments, key=lambda item: (item["silhouette"], -item["davies_bouldin"]))
    k = winner["k"]
    model, labels = fitted[k]
    alt_labels = AgglomerativeClustering(n_clusters=k).fit_predict(x)
    experiments.append({"method": "agglomerative", "k": k, "silhouette": float(silhouette_score(x, alt_labels)), "davies_bouldin": float(davies_bouldin_score(x, alt_labels))})
    df["cluster"] = labels
    summary = df.groupby("cluster")[NUMERIC].mean().round(2)
    summary["size"] = df.groupby("cluster").size()
    overall = df[NUMERIC].mean()
    summary["persona"] = summary.apply(lambda row: persona(row, overall), axis=1)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(experiments).to_csv(output / "metrics.csv", index=False)
    summary.to_csv(output / "personas.csv")
    pca = PCA(n_components=2, random_state=seed)
    points = pca.fit_transform(x)
    plt.figure(figsize=(7, 5))
    plt.scatter(points[:, 0], points[:, 1], c=labels, cmap="tab10", s=22)
    plt.xlabel("PCA component 1"); plt.ylabel("PCA component 2"); plt.title(f"Customer segments (k={k})")
    plt.tight_layout(); plt.savefig(output / "pca_segments.png", dpi=140); plt.close()
    bundle = {"preprocessor": prep, "model": model, "personas": summary["persona"].to_dict(), "features": NUMERIC + CATEGORICAL}
    joblib.dump(bundle, output / "model.joblib")
    metadata = {"selected_k": k, "selection_rule": "maximum silhouette; Davies-Bouldin tie-break", "rows_raw": len(raw), "rows_clean": len(df), "pca_explained_variance": pca.explained_variance_ratio_.tolist()}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2))
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/customers.csv"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    print(json.dumps(run(args.data, args.output), indent=2))
