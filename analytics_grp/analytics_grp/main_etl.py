"""Run extraction, transformation, and load stages."""

from __future__ import annotations

import logging

import pandas as pd

from src.config import CONFIG
from src.db import optimize_indexes, store_raw_weather_in_mongo, write_df_to_postgres
from src.ingestion import extract_all_sources
from src.preprocessing import clean_accident_data, clean_weather_data, integrate_datasets
from src.utils import ensure_directories, setup_logging

LOGGER = logging.getLogger(__name__)


def run_etl() -> pd.DataFrame:
    """Execute the full ETL workflow."""
    setup_logging()
    ensure_directories(CONFIG.raw_data_dir, CONFIG.processed_data_dir)

    LOGGER.info("Starting extraction...")
    weather_docs = extract_all_sources()
    store_raw_weather_in_mongo(weather_docs)

    LOGGER.info("Starting transformation...")
    accidents_df = pd.read_csv(f"{CONFIG.raw_data_dir}/accidents_ireland.csv")
    traffic_panel_df = pd.read_csv(f"{CONFIG.raw_data_dir}/county_traffic_exposure_daily.csv")
    weather_df = clean_weather_data(weather_docs)
    accidents_clean = clean_accident_data(accidents_df)
    integrated = integrate_datasets(accidents_clean, weather_df, traffic_panel_df)

    integrated.to_csv(f"{CONFIG.processed_data_dir}/integrated_accident_weather.csv", index=False)
    LOGGER.info("Processed dataset stored in CSV.")

    LOGGER.info("Starting load into PostgreSQL...")
    write_df_to_postgres(accidents_clean, "accidents_clean")
    write_df_to_postgres(weather_df, "weather_daily")
    write_df_to_postgres(traffic_panel_df, "county_traffic_exposure_daily")
    write_df_to_postgres(integrated, "accident_risk_integrated")
    optimize_indexes(
        [
            "CREATE INDEX IF NOT EXISTS idx_accident_date_county ON accident_risk_integrated (date, county);",
            "CREATE INDEX IF NOT EXISTS idx_accident_severity ON accident_risk_integrated (severity);",
        ]
    )
    LOGGER.info("ETL completed successfully.")
    return integrated


if __name__ == "__main__":
    run_etl()

