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

logger = logging.getLogger(__name__)


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
        """Run the complete ARES data pipeline end-to-end."""
        result = {
            "success": False,
            "stages": {},
            "error": None,
            "started_at": datetime.now().isoformat()
        }

        try:
            self._progress("Schema Init", 0.02, "Initializing database schema")
            initialize_schema()
            result["stages"]["schema"] = "OK"

            self._progress("Loading Static Data", 0.05, "Loading all static datasets")
            static_data = load_all_static_datasets()
            result["stages"]["static_load"] = {
                src: len(df) for src, df in static_data.items()
            }

            self._progress("Ingesting ACLED", 0.12, f"{len(static_data['acled'])} raw records")
            acled_rows = ingest_acled(static_data["acled"])
            n = executemany(INSERT_EVENT_SQL, acled_rows)
            self._log_run("ACLED", "OK", len(acled_rows), n)
            result["stages"]["acled"] = n

            self._progress("Ingesting ICEWS", 0.20, f"{len(static_data['icews'])} raw records")
            icews_rows = ingest_icews(static_data["icews"])
            n = executemany(INSERT_EVENT_SQL, icews_rows)
            self._log_run("ICEWS", "OK", len(icews_rows), n)
            result["stages"]["icews"] = n

            self._progress("Ingesting SIPRI", 0.27, "Arms transfers data")
            sipri_rows = ingest_sipri(static_data["sipri"])
            n = executemany(INSERT_DIPLO_SQL, sipri_rows)
            self._log_run("SIPRI", "OK", len(sipri_rows), n)
            result["stages"]["sipri"] = n

            self._progress("Ingesting World Bank GDP", 0.33, "Economic growth indicators")
            gdp_rows = ingest_world_bank(static_data["world_bank_gdp"], "GDP Growth (%)")
            n = executemany(INSERT_ECON_SQL, gdp_rows)
            self._log_run("World Bank GDP", "OK", len(gdp_rows), n)
            result["stages"]["world_bank_gdp"] = n

            self._progress("Ingesting World Bank Inflation", 0.38, "Inflation CPI data")
            inf_rows = ingest_world_bank(static_data["world_bank_inflation"], "Inflation CPI (%)")
            n = executemany(INSERT_ECON_SQL, inf_rows)
            self._log_run("World Bank Inflation", "OK", len(inf_rows), n)
            result["stages"]["world_bank_inflation"] = n

            self._progress("Ingesting WEO", 0.43, "IMF World Economic Outlook")
            weo_rows = ingest_weo(static_data["weo"])
            n = executemany(INSERT_ECON_SQL, weo_rows)
            self._log_run("IMF WEO", "OK", len(weo_rows), n)
            result["stages"]["weo"] = n

            self._progress("Ingesting Exchange Rates", 0.48, "Currency exchange rates")
            fx_rows = ingest_exchange_rate(static_data["exchange_rate"])
            n = executemany(INSERT_ECON_SQL, fx_rows)
            self._log_run("Exchange Rate", "OK", len(fx_rows), n)
            result["stages"]["exchange_rate"] = n

            self._progress("Ingesting UN Sanctions", 0.53, "Diplomatic sanctions records")
            san_rows = ingest_un_sanctions(static_data["un_sanctions"])
            n = executemany(INSERT_DIPLO_SQL, san_rows)
            self._log_run("UN Sanctions", "OK", len(san_rows), n)
            result["stages"]["un_sanctions"] = n

            self._progress("Ingesting UN Voting", 0.57, "UNGA voting records")
            vote_rows = ingest_un_voting(static_data["un_voting"])
            n = executemany(INSERT_DIPLO_SQL, vote_rows)
            self._log_run("UN Voting", "OK", len(vote_rows), n)
            result["stages"]["un_voting"] = n

            self._progress("Ingesting GSDB", 0.60, "Global Sanctions Database")
            gsdb_rows = ingest_un_sanctions(static_data["gsdb"])
            n = executemany(INSERT_DIPLO_SQL, gsdb_rows)
            self._log_run("GSDB", "OK", len(gsdb_rows), n)
            result["stages"]["gsdb"] = n

            self._progress("Fetching GDELT Live", 0.63, "Querying GDELT real-time feed...")
            gdelt_config = self.config.get("gdelt", {})
            gdelt_df = fetch_gdelt_live(
                keywords=gdelt_config.get("keywords", ["Indo-Pacific", "China India"]),
                timespan=gdelt_config.get("timespan", "7d"),
                max_records=gdelt_config.get("max_records", 200)
            )

            gdelt_rows = []
            for _, row in gdelt_df.iterrows():
                gdelt_rows.append((
                    "GDELT_LIVE",
                    str(row.get("event_date", ""))[:10],
                    str(row.get("country", "Unknown")),
                    str(row.get("zone", "B")),
                    str(row.get("event_type", "News Event")),
                    str(row.get("sub_type", "")),
                    float(row.get("severity", 0.5)),
                    "", "", str(row.get("description", ""))[:500],
                    str(row.get("url", "")),
                    float(row.get("goldstein_scale", 0)),
                    float(row.get("avg_tone", 0))
                ))
            n = executemany(INSERT_EVENT_SQL, gdelt_rows)
            self._log_run("GDELT_LIVE", "OK", len(gdelt_rows), n)
            result["stages"]["gdelt_live"] = n

            self._progress("Data Preprocessing", 0.70, "Cleaning and normalizing all data")
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

            self._progress("Storing Features", 0.92, "Persisting engineered features")
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
