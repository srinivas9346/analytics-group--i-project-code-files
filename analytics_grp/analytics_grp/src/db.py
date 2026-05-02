"""Database connectivity and load helpers."""

from __future__ import annotations

import logging
import re
from typing import Iterable, List

import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url

from src.config import CONFIG

LOGGER = logging.getLogger(__name__)


def get_mongo_client() -> MongoClient:
    """Return configured MongoDB client."""
    return MongoClient(CONFIG.mongo_uri)


def store_raw_weather_in_mongo(weather_docs: List[dict]) -> int:
    """Insert weather JSON docs into MongoDB."""
    if not weather_docs:
        LOGGER.warning("No weather documents to insert into MongoDB.")
        return 0

    with get_mongo_client() as client:
        coll = client[CONFIG.mongo_db][CONFIG.mongo_collection_weather]
        coll.delete_many({})
        result = coll.insert_many(weather_docs)
        inserted = len(result.inserted_ids)
        LOGGER.info("Inserted %d weather documents into MongoDB.", inserted)
        return inserted


def read_weather_from_mongo() -> List[dict]:
    """Read weather JSON docs from MongoDB."""
    with get_mongo_client() as client:
        coll = client[CONFIG.mongo_db][CONFIG.mongo_collection_weather]
        docs = list(coll.find({}, {"_id": 0}))
    return docs


def get_postgres_engine() -> Engine:
    """Create PostgreSQL SQLAlchemy engine."""
    ensure_postgres_database_exists(CONFIG.postgres_uri)
    return create_engine(CONFIG.postgres_uri, pool_pre_ping=True)


def ensure_postgres_database_exists(postgres_uri: str) -> None:
    """
    Ensure target PostgreSQL database exists before writing tables.

    This prevents ETL failure when server is running but DB is not created yet.
    """
    url = make_url(postgres_uri)
    target_db = url.database
    if not target_db:
        raise ValueError("POSTGRES_URI must include a database name.")

    # Basic safety check because database name is interpolated in CREATE DATABASE.
    if not re.fullmatch(r"[A-Za-z0-9_]+", target_db):
        raise ValueError("Database name contains unsupported characters.")

    admin_url = url.set(database="postgres")
    admin_engine = create_engine(admin_url, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :db_name"), {"db_name": target_db}).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{target_db}"'))
            LOGGER.info("Created PostgreSQL database: %s", target_db)


def write_df_to_postgres(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> None:
    """Write a dataframe to PostgreSQL."""
    engine = get_postgres_engine()
    with engine.begin() as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False, method="multi", chunksize=1000)
    LOGGER.info("Table written to PostgreSQL: %s (%d rows)", table_name, len(df))


def optimize_indexes(index_sql: Iterable[str]) -> None:
    """Run index creation SQL statements."""
    engine = get_postgres_engine()
    with engine.begin() as conn:
        for stmt in index_sql:
            conn.execute(text(stmt))
            LOGGER.info("Index statement executed.")

