"""Visualization utilities for static and interactive figures."""

from __future__ import annotations

import logging
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

from src.config import CONFIG
from src.utils import ensure_directories

LOGGER = logging.getLogger(__name__)

sns.set_theme(style="whitegrid")


def create_static_visuals(ts_df: pd.DataFrame, df: pd.DataFrame, corr_df: pd.DataFrame) -> Dict[str, str]:
    """Generate matplotlib/seaborn plots and save to disk."""
    ensure_directories(CONFIG.figures_dir)
    paths = {}

    # Time series
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(ts_df["date"], ts_df["accidents"], color="#1f77b4", linewidth=1.8)
    ax.set_title("Daily Accidents Over Time (Ireland)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Accident Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    p = f"{CONFIG.figures_dir}/time_series_accidents.png"
    plt.savefig(p, dpi=220)
    plt.close(fig)
    paths["time_series"] = p

    # Bar chart by severity
    sev = df.groupby("severity", as_index=False).agg(accidents=("accident_id", "count"))
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=sev, x="severity", y="accidents", hue="severity", ax=ax, palette="viridis", dodge=False)
    if ax.legend_ is not None:
        ax.legend_.remove()
    ax.set_title("Accidents by Severity")
    ax.set_xlabel("Severity Level")
    ax.set_ylabel("Accident Count")
    plt.tight_layout()
    p = f"{CONFIG.figures_dir}/accidents_by_severity.png"
    plt.savefig(p, dpi=220)
    plt.close(fig)
    paths["severity_bar"] = p

    # Correlation heatmap
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix: Accidents and Weather Factors")
    plt.tight_layout()
    p = f"{CONFIG.figures_dir}/correlation_heatmap.png"
    plt.savefig(p, dpi=220)
    plt.close(fig)
    paths["correlation"] = p

    return paths


def create_plotly_hotspot_map(df: pd.DataFrame):
    """Create a geospatial scatter map of accident locations."""
    map_df = df[["latitude", "longitude", "severity", "county", "weather_impact_score"]].copy()
    fig = px.scatter_mapbox(
        map_df,
        lat="latitude",
        lon="longitude",
        color="severity",
        size="weather_impact_score",
        hover_name="county",
        zoom=5.5,
        height=600,
        title="Accident Hotspots and Weather Impact (Ireland)",
        color_continuous_scale="YlOrRd",
    )
    fig.update_layout(mapbox_style="carto-positron", margin=dict(r=0, t=40, l=0, b=0))
    return fig

