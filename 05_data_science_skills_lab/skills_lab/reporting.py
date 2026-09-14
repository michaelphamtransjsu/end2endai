"""Reproducible chart and machine-readable report generation."""

import json
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from .analysis import pca_projection, run_analysis
from .data import load_dataset


def create_outputs(dataset_name: str, output_dir: str | Path) -> dict:
    dataset = load_dataset(dataset_name)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    results = asdict(run_analysis(dataset))
    projection = pca_projection(dataset)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=projection, x="PC1", y="PC2", hue="target", palette="viridis", ax=ax)
    ax.set_title(f"{dataset_name.replace('_', ' ').title()} PCA projection")
    fig.tight_layout()
    chart = output / f"{dataset_name}_pca.png"
    fig.savefig(chart, dpi=140)
    plt.close(fig)
    report = output / f"{dataset_name}_metrics.json"
    report.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"chart": str(chart), "report": str(report), **results}
