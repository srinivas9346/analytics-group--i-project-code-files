"""Predictive modeling for accident risk."""

from __future__ import annotations

import json
import logging
from typing import Dict

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from src.config import CONFIG
from src.utils import ensure_directories

LOGGER = logging.getLogger(__name__)


def train_risk_model(df: pd.DataFrame) -> Dict[str, float]:
    """
    Train a simple regression model to forecast accident severity index.
    """
    features = [
        "hour",
        "is_weekend",
        "is_rush_hour",
        "temperature_mean",
        "precipitation_sum",
        "windspeed_max",
        "population",
        "baseline_congestion_index",
        "vehicle_km_millions",
        "goods_vehicle_share",
        "congestion_index",
    ]
    target = "accident_severity_index"

    X = df[features].copy()
    X["is_weekend"] = X["is_weekend"].astype(int)
    y = df[target].copy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    metrics = {
        "r2": float(r2_score(y_test, preds)),
        "mae": float(mean_absolute_error(y_test, preds)),
    }

    ensure_directories(CONFIG.models_dir)
    pd.DataFrame({"feature": features, "coefficient": model.coef_}).to_csv(
        f"{CONFIG.models_dir}/linear_model_coefficients.csv", index=False
    )
    with open(f"{CONFIG.models_dir}/linear_model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    LOGGER.info("Model training completed. R2=%.3f MAE=%.3f", metrics["r2"], metrics["mae"])
    return metrics

