"""Analytical computations for the project."""

from __future__ import annotations

import logging
from typing import Dict

import pandas as pd

LOGGER = logging.getLogger(__name__)


def run_eda(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generate key summary tables for reporting."""
    by_county = (
        df.groupby("county", as_index=False)
        .agg(
            accidents=("accident_id", "count"),
            avg_severity=("severity", "mean"),
            avg_weather_impact=("weather_impact_score", "mean"),
        )
        .sort_values("accidents", ascending=False)
    )
    by_hour = df.groupby("hour", as_index=False).agg(accidents=("accident_id", "count"))
    by_day = df.groupby("day_of_week", as_index=False).agg(accidents=("accident_id", "count"))
    return {"by_county": by_county, "by_hour": by_hour, "by_day": by_day}


def time_series_accidents(df: pd.DataFrame) -> pd.DataFrame:
    """Daily accident counts for time-series visualizations."""
    ts = df.groupby("date", as_index=False).agg(accidents=("accident_id", "count"))
    ts["date"] = pd.to_datetime(ts["date"], errors="coerce")
    return ts.sort_values("date")


def weather_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix between accidents and weather-related factors."""
    corr_cols = [
        "severity",
        "casualties",
        "vehicles_involved",
        "temperature_mean",
        "precipitation_sum",
        "windspeed_max",
        "weather_impact_score",
    ]
    return df[corr_cols].corr(numeric_only=True)


def hotspot_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """County-level hotspot table."""
    hotspots = (
        df.groupby("county", as_index=False)
        .agg(
            accidents=("accident_id", "count"),
            mean_lat=("latitude", "mean"),
            mean_lon=("longitude", "mean"),
            severe_share=("severity", lambda s: float((s >= 4).mean())),
        )
        .sort_values("accidents", ascending=False)
    )
    return hotspots


def generate_key_findings(df: pd.DataFrame) -> Dict[str, str]:
    """Create plain-English insights for reporting."""
    peak_hour = int(df.groupby("hour")["accident_id"].count().idxmax())
    top_county = str(df.groupby("county")["accident_id"].count().idxmax())
    rain_severity = df.groupby("rain_flag")["severity"].mean().to_dict()
    rainy = float(rain_severity.get(1, 0.0))
    dry = float(rain_severity.get(0, 0.0))

    findings = {
        "peak_time": f"Peak accident hour is {peak_hour}:00, indicating higher risk around commuting periods.",
        "high_risk_county": f"{top_county} has the highest recorded accident count in the analysis window.",
        "weather_effect": (
            f"Average severity during rainy conditions is {rainy:.2f} compared with {dry:.2f} in drier conditions."
        ),
        "recommendation": (
            "Target peak-hour enforcement, dynamic weather warnings, and county-specific traffic calming in hotspot areas."
        ),
    }
    return findings

