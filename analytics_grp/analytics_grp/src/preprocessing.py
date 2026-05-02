"""Data cleaning, feature engineering, and integration."""

from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


def _flatten_weather_docs(weather_docs: List[dict]) -> pd.DataFrame:
    frames = []
    for doc in weather_docs:
        daily = doc.get("daily", {})
        df = pd.DataFrame(
            {
                "date": daily.get("time", []),
                "temperature_mean": daily.get("temperature_2m_mean", []),
                "precipitation_sum": daily.get("precipitation_sum", []),
                "windspeed_max": daily.get("windspeed_10m_max", []),
            }
        )
        if not df.empty:
            df["county"] = doc.get("county")
            frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["date", "temperature_mean", "precipitation_sum", "windspeed_max", "county"])
    return pd.concat(frames, ignore_index=True)


def clean_accident_data(accidents_df: pd.DataFrame) -> pd.DataFrame:
    """Clean accident CSV and derive core accident features."""
    df = accidents_df.copy()
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], errors="coerce")
    df = df.dropna(subset=["datetime", "county", "severity"]).copy()

    for col in ["latitude", "longitude", "casualties", "vehicles_involved"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["casualties"] = df["casualties"].fillna(df["casualties"].median())
    df["vehicles_involved"] = df["vehicles_involved"].fillna(df["vehicles_involved"].median())
    df["latitude"] = df["latitude"].fillna(df["latitude"].mean())
    df["longitude"] = df["longitude"].fillna(df["longitude"].mean())

    df["date"] = df["datetime"].dt.date.astype(str)
    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.day_name()
    df["month"] = df["datetime"].dt.month
    df["is_weekend"] = df["datetime"].dt.dayofweek >= 5
    df["is_rush_hour"] = df["hour"].isin([7, 8, 9, 16, 17, 18]).astype(int)

    df["severity"] = pd.to_numeric(df["severity"], errors="coerce").fillna(1).astype(int)
    df["severity"] = df["severity"].clip(1, 5)
    df["accident_severity_index"] = (
        0.55 * df["severity"] + 0.25 * df["casualties"] + 0.20 * df["vehicles_involved"]
    )

    return df


def clean_weather_data(weather_docs: List[dict]) -> pd.DataFrame:
    """Convert raw weather JSON docs into a normalized dataframe."""
    weather_df = _flatten_weather_docs(weather_docs)
    if weather_df.empty:
        LOGGER.warning("Weather dataframe is empty after flattening.")
        return weather_df

    weather_df["date"] = pd.to_datetime(weather_df["date"], errors="coerce").dt.date.astype(str)
    for c in ["temperature_mean", "precipitation_sum", "windspeed_max"]:
        weather_df[c] = pd.to_numeric(weather_df[c], errors="coerce")

    weather_df = weather_df.dropna(subset=["date", "county"]).copy()
    weather_df[["temperature_mean", "precipitation_sum", "windspeed_max"]] = weather_df[
        ["temperature_mean", "precipitation_sum", "windspeed_max"]
    ].fillna(weather_df[["temperature_mean", "precipitation_sum", "windspeed_max"]].median())
    return weather_df


def integrate_datasets(
    accidents_df: pd.DataFrame, weather_df: pd.DataFrame, traffic_panel_df: pd.DataFrame
) -> pd.DataFrame:
    """Merge accidents, weather, and county-day traffic exposure features."""
    df = accidents_df.merge(weather_df, on=["date", "county"], how="left")
    df = df.merge(traffic_panel_df, on=["date", "county"], how="left", suffixes=("", "_traffic"))

    for col in [
        "population",
        "baseline_congestion_index",
        "vehicle_km_millions",
        "goods_vehicle_share",
        "congestion_index",
        "temperature_mean",
        "precipitation_sum",
        "windspeed_max",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    df["rain_flag"] = (df["precipitation_sum"] > 1.0).astype(int)
    df["wind_flag"] = (df["windspeed_max"] > 25).astype(int)
    df["weather_impact_score"] = (
        0.45 * np.maximum(df["precipitation_sum"], 0)
        + 0.30 * np.maximum(df["windspeed_max"] / 10, 0)
        + 0.25 * np.maximum((10 - df["temperature_mean"]).clip(lower=0), 0)
    )
    # Exposure-normalised burden proxy: higher vehicle-km implies more opportunities for collisions.
    df["accidents_per_million_vehicle_km_proxy"] = df["accident_severity_index"] / (
        df["vehicle_km_millions"] + 1e-3
    )
    return df

