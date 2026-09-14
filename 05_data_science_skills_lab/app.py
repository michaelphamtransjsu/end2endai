"""Interactive Streamlit explorer for the lab."""

from dataclasses import asdict

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from skills_lab import DATASETS, load_dataset
from skills_lab.analysis import describe, engineered_features, pca_projection, run_analysis

st.set_page_config(page_title="Data Science Skills Mastery Lab", layout="wide")
st.title("Data Science Skills Mastery Lab")
st.caption("Reproducible exploration of small datasets bundled with scikit-learn")
name = st.sidebar.selectbox("Dataset", DATASETS)
dataset = load_dataset(name)
st.subheader("Validated data")
st.write(f"Task: **{dataset.task}** · Rows: **{len(dataset.frame)}** · Target: **{dataset.target}**")
st.dataframe(dataset.frame.head(20), use_container_width=True)

eda, features, models = st.tabs(["EDA & visualization", "Feature engineering", "Models & statistics"])
with eda:
    st.dataframe(describe(dataset), use_container_width=True)
    projection = pca_projection(dataset)
    fig, ax = plt.subplots()
    sns.scatterplot(data=projection, x="PC1", y="PC2", hue="target", palette="viridis", ax=ax)
    st.pyplot(fig)
with features:
    st.write("Two interpretable aggregate features derived from predictors only.")
    st.dataframe(engineered_features(dataset).head(20), use_container_width=True)
with models:
    results = asdict(run_analysis(dataset))
    c1, c2 = st.columns(2)
    c1.metric(results["supervised_metric"].replace("_", " ").title(), f'{results["supervised_value"]:.4f}')
    c2.metric("Clustering silhouette", f'{results["silhouette"]:.4f}')
    st.write({"test": results["statistical_test"], "statistic": results["statistic"], "p_value": results["p_value"]})
    st.caption("Metrics are computed live from a fixed random split (seed 42); they are demonstrations, not benchmarks.")
