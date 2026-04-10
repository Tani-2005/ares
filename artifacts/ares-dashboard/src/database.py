import sqlite3
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "master_data.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS raw_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                event_date TEXT NOT NULL,
                country TEXT NOT NULL,
                zone TEXT NOT NULL CHECK(zone IN ('A', 'B')),
                event_type TEXT NOT NULL,
                sub_type TEXT,
                severity REAL,
                actor1 TEXT,
                actor2 TEXT,
                description TEXT,
                url TEXT,
                goldstein_scale REAL,
                avg_tone REAL,
                ingested_at TEXT DEFAULT (datetime('now')),
                UNIQUE(source, event_date, country, event_type, description)
            );

            CREATE TABLE IF NOT EXISTS economic_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                indicator_type TEXT NOT NULL,
                country TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER,
                value REAL,
                unit TEXT,
                ingested_at TEXT DEFAULT (datetime('now')),
                UNIQUE(source, indicator_type, country, year, month)
            );

            CREATE TABLE IF NOT EXISTS diplomatic_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                record_type TEXT NOT NULL,
                date TEXT NOT NULL,
                country1 TEXT,
                country2 TEXT,
                description TEXT,
                vote_for INTEGER,
                vote_against INTEGER,
                vote_abstain INTEGER,
                ingested_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS engineered_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                zone TEXT NOT NULL,
                feature_date TEXT NOT NULL,
                window_days INTEGER NOT NULL,
                event_count INTEGER DEFAULT 0,
                military_event_count INTEGER DEFAULT 0,
                diplomatic_event_count INTEGER DEFAULT 0,
                protest_event_count INTEGER DEFAULT 0,
                violence_event_count INTEGER DEFAULT 0,
                avg_goldstein REAL,
                avg_tone REAL,
                event_acceleration REAL,
                sentiment_volatility REAL,
                protest_violence_ratio REAL,
                diplomatic_silence_days INTEGER DEFAULT 0,
                economic_stress_score REAL,
                composite_risk_score REAL,
                risk_level TEXT CHECK(risk_level IN ('GREEN', 'AMBER', 'RED')),
                computed_at TEXT DEFAULT (datetime('now')),
                UNIQUE(country, feature_date, window_days)
            );

            CREATE TABLE IF NOT EXISTS ingestion_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                records_fetched INTEGER DEFAULT 0,
                records_stored INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TEXT DEFAULT (datetime('now')),
                completed_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_raw_events_country ON raw_events(country);
            CREATE INDEX IF NOT EXISTS idx_raw_events_date ON raw_events(event_date);
            CREATE INDEX IF NOT EXISTS idx_raw_events_zone ON raw_events(zone);
            CREATE INDEX IF NOT EXISTS idx_features_country ON engineered_features(country);
            CREATE INDEX IF NOT EXISTS idx_features_date ON engineered_features(feature_date);
        """)
        conn.commit()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Schema initialization error: {e}")
        raise
    finally:
        conn.close()


def query_df(sql: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def execute(sql: str, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def executemany(sql: str, rows: list):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(sql, rows)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_table_stats() -> dict:
    tables = ["raw_events", "economic_indicators", "diplomatic_records", "engineered_features", "ingestion_log"]
    stats = {}
    conn = get_connection()
    try:
        for table in tables:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except Exception:
                stats[table] = 0
    finally:
        conn.close()
    return stats
