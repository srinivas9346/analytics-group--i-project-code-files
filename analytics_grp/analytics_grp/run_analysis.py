"""Run EDA, modeling, and visualization exports."""

from __future__ import annotations

import json

import pandas as pd

from src.analysis import generate_key_findings, run_eda, time_series_accidents, weather_correlation
from src.config import CONFIG
from src.modeling import train_risk_model
from src.visualization import create_static_visuals


def run_analysis() -> None:
    """Execute analysis outputs from the processed integrated dataset."""
    df = pd.read_csv(f"{CONFIG.processed_data_dir}/integrated_accident_weather.csv")

    eda = run_eda(df)
    ts_df = time_series_accidents(df)
    corr_df = weather_correlation(df)
    findings = generate_key_findings(df)
    metrics = train_risk_model(df)
    fig_paths = create_static_visuals(ts_df, df, corr_df)

    eda["by_county"].to_csv(f"{CONFIG.processed_data_dir}/eda_by_county.csv", index=False)
    eda["by_hour"].to_csv(f"{CONFIG.processed_data_dir}/eda_by_hour.csv", index=False)
    corr_df.to_csv(f"{CONFIG.processed_data_dir}/correlation_matrix.csv")

    with open(f"{CONFIG.processed_data_dir}/key_findings.json", "w", encoding="utf-8") as f:
        json.dump({"findings": findings, "model_metrics": metrics, "figures": fig_paths}, f, indent=2)


if __name__ == "__main__":
    run_analysis()

