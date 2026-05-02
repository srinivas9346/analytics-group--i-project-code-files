"""Configuration helpers for project settings."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Project-level settings loaded from environment variables."""

    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    mongo_db: str = os.getenv("MONGO_DB", "traffic_risk_ireland")
    mongo_collection_weather: str = os.getenv("MONGO_COLLECTION_WEATHER", "raw_weather")
    postgres_uri: str = os.getenv(
        "POSTGRES_URI",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/traffic_risk_ireland",
    )
    start_date: str = os.getenv("START_DATE", "2023-01-01")
    end_date: str = os.getenv("END_DATE", "2024-12-31")

    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    figures_dir: str = "outputs/figures"
    models_dir: str = "outputs/models"


CONFIG = Config()

