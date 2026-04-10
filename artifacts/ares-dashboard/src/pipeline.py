"""
Main pipeline orchestrator for ARES.
Runs ingestion → preprocessing → feature engineering → storage.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Optional, Callable

from database import initialize_schema, executemany, execute, get_table_stats
from ingestion import (
    fetch_gdelt_live, ingest_acled, ingest_icews, ingest_sipri,
    ingest_un_sanctions, ingest_un_voting, ingest_world_bank,
    ingest_exchange_rate, ingest_weo,
    INSERT_EVENT_SQL, INSERT_ECON_SQL, INSERT_DIPLO_SQL
)
from preprocessing import DataPreprocessor
from feature_engineering import FeatureEngineer
from static_data_generator import load_all_static_datasets
from live_data import (
    fetch_all_world_bank_live, fetch_ucdp_ged, fetch_reliefweb,
    fetch_all_imf_live, fetch_gdelt_gkg_themes
)

logger = logging.getLogger(__name__)


def _safe_event_rows(df: pd.DataFrame, source_override: str = None) -> list:
    """Convert any event DataFrame to INSERT_EVENT_SQL rows safely."""
    rows = []
    if df.empty:
        return rows
    for _, row in df.iterrows():
        rows.append((
            source_override or str(row.get("source", "Live")),
            str(row.get("event_date", ""))[:10],
            str(row.get("country", "Unknown")),
            str(row.get("zone", "A")),
            str(row.get("event_type", "Event")),
            str(row.get("sub_type", ""))[:200],
            float(row.get("severity", 0.5) or 0.5),
            str(row.get("actor1", ""))[:200],
            str(row.get("actor2", ""))[:200],
            str(row.get("description", ""))[:500],
            str(row.get("url", ""))[:500],
            float(row.get("goldstein_scale", 0) or 0),
            float(row.get("avg_tone", 0) or 0),
        ))
    return rows


def _safe_econ_rows(df: pd.DataFrame) -> list:
    """Convert economic DataFrame to INSERT_ECON_SQL rows safely."""
    rows = []
    if df.empty:
        return rows
    for _, row in df.iterrows():
        rows.append((
            str(row.get("source", "Live")),
            str(row.get("indicator_type", "")),
            str(row.get("country", "")),
            int(row.get("year", 2020)),
            None,
            float(row.get("value", 0) or 0),
            str(row.get("unit", "%")),
        ))
    return rows


class ARESPipeline:
    def __init__(self, config: dict = None, progress_callback: Optional[Callable] = None):
        self.config = config or {}
        self.progress_callback = progress_callback
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer(
            windows=self.config.get("feature_engineering", {}).get("rolling_windows", [7, 14, 30])
        )
        self.run_log = []
        self.stats = {}

    def _progress(self, step: str, pct: float, detail: str = ""):
        if self.progress_callback:
            self.progress_callback(step, pct, detail)
        logger.info(f"[{pct:.0%}] {step} — {detail}")

    def _log_run(self, source: str, status: str, fetched: int, stored: int, error: str = None):
        self.run_log.append({
            "source": source, "status": status,
            "fetched": fetched, "stored": stored,
            "error": error, "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    def run_full_pipeline(self) -> Dict:
        result = {
            "success": False,
            "stages": {},
            "error": None,
            "started_at": datetime.now().isoformat()
        }

        try:
            # ── Schema ──────────────────────────────────────────────────────
            self._progress("Schema Init", 0.02, "Initializing database schema")
            initialize_schema()
            result["stages"]["schema"] = "OK"

            # ── Static datasets ─────────────────────────────────────────────
            self._progress("Loading Static Data", 0.05, "Generating static baseline datasets")
            static_data = load_all_static_datasets()
            result["stages"]["static_load"] = {src: len(df) for src, df in static_data.items()}

            # ACLED
            self._progress("Ingesting ACLED", 0.09, f"{len(static_data['acled'])} raw records")
            acled_rows = ingest_acled(static_data["acled"])
            n = executemany(INSERT_EVENT_SQL, acled_rows)
            self._log_run("ACLED (Static)", "OK", len(acled_rows), n)
            result["stages"]["acled"] = n

            # ICEWS
            self._progress("Ingesting ICEWS", 0.14, f"{len(static_data['icews'])} raw records")
            icews_rows = ingest_icews(static_data["icews"])
            n = executemany(INSERT_EVENT_SQL, icews_rows)
            self._log_run("ICEWS (Static)", "OK", len(icews_rows), n)
            result["stages"]["icews"] = n

            # SIPRI
            self._progress("Ingesting SIPRI", 0.18, "Arms transfers")
            sipri_rows = ingest_sipri(static_data["sipri"])
            n = executemany(INSERT_DIPLO_SQL, sipri_rows)
            self._log_run("SIPRI (Static)", "OK", len(sipri_rows), n)
            result["stages"]["sipri"] = n

            # World Bank static
            self._progress("Ingesting World Bank Static", 0.21, "GDP + Inflation (historical)")
            gdp_rows = ingest_world_bank(static_data["world_bank_gdp"], "GDP Growth (%)")
            inf_rows = ingest_world_bank(static_data["world_bank_inflation"], "Inflation CPI (%)")
            n1 = executemany(INSERT_ECON_SQL, gdp_rows)
            n2 = executemany(INSERT_ECON_SQL, inf_rows)
            self._log_run("World Bank GDP (Static)", "OK", len(gdp_rows), n1)
            self._log_run("World Bank Inflation (Static)", "OK", len(inf_rows), n2)
            result["stages"]["world_bank_static"] = n1 + n2

            # WEO, exchange rates, UN, GSDB
            self._progress("Ingesting WEO + FX + Diplomatic", 0.25, "IMF WEO, exchange rates, UN records")
            weo_rows = ingest_weo(static_data["weo"])
            fx_rows = ingest_exchange_rate(static_data["exchange_rate"])
            san_rows = ingest_un_sanctions(static_data["un_sanctions"])
            vote_rows = ingest_un_voting(static_data["un_voting"])
            gsdb_rows = ingest_un_sanctions(static_data["gsdb"])
            n_weo = executemany(INSERT_ECON_SQL, weo_rows)
            n_fx = executemany(INSERT_ECON_SQL, fx_rows)
            n_san = executemany(INSERT_DIPLO_SQL, san_rows)
            n_vote = executemany(INSERT_DIPLO_SQL, vote_rows)
            n_gsdb = executemany(INSERT_DIPLO_SQL, gsdb_rows)
            for src, ni in [("IMF WEO", n_weo), ("Exchange Rates", n_fx),
                             ("UN Sanctions", n_san), ("UN Voting", n_vote), ("GSDB", n_gsdb)]:
                self._log_run(f"{src} (Static)", "OK", ni, ni)
            result["stages"]["diplomatic_static"] = n_san + n_vote + n_gsdb

            # ── GDELT Live ───────────────────────────────────────────────────
            self._progress("Fetching GDELT Live", 0.30, "Querying GDELT real-time news feed...")
            gdelt_config = self.config.get("gdelt", {})
            gdelt_df = fetch_gdelt_live(
                keywords=gdelt_config.get("keywords", ["Indo-Pacific", "China India"]),
                timespan=gdelt_config.get("timespan", "7d"),
                max_records=gdelt_config.get("max_records", 200)
            )
            gdelt_rows = _safe_event_rows(gdelt_df, "GDELT_LIVE")
            n = executemany(INSERT_EVENT_SQL, gdelt_rows)
            self._log_run("GDELT (Live)", "OK", len(gdelt_rows), n)
            result["stages"]["gdelt_live"] = n

            # ── GDELT GKG Live ───────────────────────────────────────────────
            self._progress("Fetching GDELT GKG Live", 0.36, "Conflict theme volume signals...")
            try:
                gkg_df = fetch_gdelt_gkg_themes(days_back=7)
                gkg_rows = _safe_event_rows(gkg_df)
                n = executemany(INSERT_EVENT_SQL, gkg_rows) if gkg_rows else 0
                self._log_run("GDELT GKG (Live)", "OK", len(gkg_rows), n)
                result["stages"]["gdelt_gkg_live"] = n
            except Exception as e:
                self._log_run("GDELT GKG (Live)", "WARN", 0, 0, str(e))
                result["stages"]["gdelt_gkg_live"] = 0

            # ── UCDP GED Live ────────────────────────────────────────────────
            self._progress("Fetching UCDP GED Live", 0.42, "Uppsala verified conflict events...")
            try:
                ucdp_df = fetch_ucdp_ged(start_year=2020)
                ucdp_rows = _safe_event_rows(ucdp_df)
                n = executemany(INSERT_EVENT_SQL, ucdp_rows) if ucdp_rows else 0
                self._log_run("UCDP GED (Live)", "OK", len(ucdp_rows), n)
                result["stages"]["ucdp_live"] = n
            except Exception as e:
                self._log_run("UCDP GED (Live)", "WARN", 0, 0, str(e))
                result["stages"]["ucdp_live"] = 0

            # ── ReliefWeb Live ───────────────────────────────────────────────
            self._progress("Fetching ReliefWeb Live", 0.48, "UN humanitarian crisis reports...")
            try:
                rw_df = fetch_reliefweb(days_back=60, limit=150)
                rw_rows = _safe_event_rows(rw_df)
                n = executemany(INSERT_EVENT_SQL, rw_rows) if rw_rows else 0
                self._log_run("ReliefWeb (Live)", "OK", len(rw_rows), n)
                result["stages"]["reliefweb_live"] = n
            except Exception as e:
                self._log_run("ReliefWeb (Live)", "WARN", 0, 0, str(e))
                result["stages"]["reliefweb_live"] = 0

            # ── World Bank Live API ──────────────────────────────────────────
            self._progress("Fetching World Bank Live API", 0.54, "Live GDP, inflation, military expenditure...")
            try:
                wb_live_df = fetch_all_world_bank_live()
                wb_live_rows = _safe_econ_rows(wb_live_df)
                n = executemany(INSERT_ECON_SQL, wb_live_rows) if wb_live_rows else 0
                self._log_run("World Bank (Live API)", "OK", len(wb_live_rows), n)
                result["stages"]["world_bank_live"] = n
            except Exception as e:
                self._log_run("World Bank (Live API)", "WARN", 0, 0, str(e))
                result["stages"]["world_bank_live"] = 0

            # ── IMF Live API ─────────────────────────────────────────────────
            self._progress("Fetching IMF Live API", 0.60, "Live WEO projections...")
            try:
                imf_live_df = fetch_all_imf_live()
                imf_live_rows = _safe_econ_rows(imf_live_df)
                n = executemany(INSERT_ECON_SQL, imf_live_rows) if imf_live_rows else 0
                self._log_run("IMF (Live API)", "OK", len(imf_live_rows), n)
                result["stages"]["imf_live"] = n
            except Exception as e:
                self._log_run("IMF (Live API)", "WARN", 0, 0, str(e))
                result["stages"]["imf_live"] = 0

            # ── Preprocessing ────────────────────────────────────────────────
            self._progress("Data Preprocessing", 0.70, "Cleaning and normalising all ingested data")
            from database import query_df
            events_df = query_df("SELECT * FROM raw_events")
            econ_df = query_df("SELECT * FROM economic_indicators")

            clean_events, missing_report = self.preprocessor.preprocess_events(events_df)
            clean_econ, _ = self.preprocessor.preprocess_economic(econ_df)
            result["stages"]["preprocessing"] = {
                "events_cleaned": len(clean_events),
                "econ_cleaned": len(clean_econ),
                "quality_score": self.preprocessor.compute_data_quality_score(clean_events)
            }

            # ── Feature Engineering ───────────────────────────────────────────
            self._progress("Feature Engineering", 0.82, "Computing leading indicators")
            features_df = self.feature_engineer.compute_event_features(clean_events)

            if not econ_df.empty and not features_df.empty:
                features_df = self.feature_engineer.compute_economic_stress(econ_df, features_df)
            if not features_df.empty:
                features_df = self.feature_engineer.compute_composite_risk(features_df)
                features_df = self.feature_engineer.compute_anomaly_flags(features_df)

            result["stages"]["features"] = {
                "total": len(features_df),
                "countries": features_df["country"].nunique() if not features_df.empty else 0,
                "risk_distribution": features_df["risk_level"].value_counts().to_dict() if not features_df.empty and "risk_level" in features_df.columns else {}
            }

            # ── Store features ────────────────────────────────────────────────
            self._progress("Storing Features", 0.92, "Persisting engineered features to SQLite")
            if not features_df.empty:
                feature_cols = [
                    "country", "zone", "feature_date", "window_days",
                    "event_count", "military_event_count", "diplomatic_event_count",
                    "protest_event_count", "violence_event_count",
                    "avg_goldstein", "avg_tone", "event_acceleration",
                    "sentiment_volatility", "protest_violence_ratio",
                    "diplomatic_silence_days", "economic_stress_score",
                    "composite_risk_score", "risk_level"
                ]
                available_cols = [c for c in feature_cols if c in features_df.columns]
                feat_rows = [
                    tuple(row[c] for c in available_cols)
                    for _, row in features_df[available_cols].iterrows()
                ]
                placeholders = ", ".join(["?"] * len(available_cols))
                cols_str = ", ".join(available_cols)
                insert_sql = f"INSERT OR REPLACE INTO engineered_features ({cols_str}) VALUES ({placeholders})"
                n = executemany(insert_sql, feat_rows)
                result["stages"]["features_stored"] = n

            self._progress("Pipeline Complete", 1.0, "All stages completed successfully")
            result["success"] = True
            result["completed_at"] = datetime.now().isoformat()
            result["table_stats"] = get_table_stats()
            result["run_log"] = self.run_log
            result["feature_df"] = features_df if not features_df.empty else pd.DataFrame()

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            result["error"] = str(e)
            result["run_log"] = self.run_log

        return result
