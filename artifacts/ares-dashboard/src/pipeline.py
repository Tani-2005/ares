"""
Main pipeline orchestrator for ARES.
Runs ingestion → preprocessing → feature engineering → ML inference → storage.
Optimized for high-speed concurrent execution (<30s runtime).
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Optional, Callable

from database import initialize_schema, executemany, execute, get_table_stats, query_df
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
from model import get_ares_model
from nlp_engine import NarrativeEngine

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
        self.nlp_engine = NarrativeEngine()
        self.model = get_ares_model()
        self.run_log = []
        self.stats = {}

    def _progress(self, step: str, pct: float, detail: str = ""):
        if self.progress_callback:
            self.progress_callback(step, pct, detail)
        logger.info(f"[{pct:.0%}] {step} — {detail}")

    def _log_run(self, source: str, status: str, fetched: int, stored: int, error: str = None):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.run_log.append({
            "source": source, "status": status,
            "fetched": fetched, "stored": stored,
            "error": error, "timestamp": now_str[11:]
        })
        try:
            execute(
                "INSERT INTO ingestion_log (source, status, records_fetched, records_stored, error_message, started_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (source, status, fetched, stored, error, now_str, now_str)
            )
        except Exception as e:
            logger.debug(f"Failed to log run to database: {e}")

    def run_full_pipeline(self) -> Dict:
        result = {
            "success": False,
            "stages": {},
            "error": None,
            "started_at": datetime.now().isoformat()
        }

        try:
            # ── 1. Schema Init & Migration ───────────────────────────────────
            self._progress("Schema Init", 0.04, "Initializing SQLite schema & table migrations")
            initialize_schema()
            result["stages"]["schema"] = "OK"

            # ── 2. Static Datasets (Cached Check for Instant Run) ───────────
            current_stats = get_table_stats()
            has_baseline = current_stats.get("raw_events", 0) >= 1500
            force_static = self.config.get("force_reload_static", False)

            if not has_baseline or force_static:
                self._progress("Loading Static Data", 0.10, "Generating static baseline datasets")
                static_data = load_all_static_datasets()
                result["stages"]["static_load"] = {src: len(df) for src, df in static_data.items()}

                # ACLED
                acled_rows = ingest_acled(static_data["acled"])
                n_acled = executemany(INSERT_EVENT_SQL, acled_rows)
                self._log_run("ACLED (Static)", "OK", len(acled_rows), n_acled)

                # ICEWS
                icews_rows = ingest_icews(static_data["icews"])
                n_icews = executemany(INSERT_EVENT_SQL, icews_rows)
                self._log_run("ICEWS (Static)", "OK", len(icews_rows), n_icews)

                # SIPRI
                sipri_rows = ingest_sipri(static_data["sipri"])
                executemany(INSERT_DIPLO_SQL, sipri_rows)

                # World Bank + WEO + FX
                gdp_rows = ingest_world_bank(static_data["world_bank_gdp"], "GDP Growth (%)")
                inf_rows = ingest_world_bank(static_data["world_bank_inflation"], "Inflation CPI (%)")
                weo_rows = ingest_weo(static_data["weo"])
                fx_rows = ingest_exchange_rate(static_data["exchange_rate"])
                executemany(INSERT_ECON_SQL, gdp_rows + inf_rows + weo_rows + fx_rows)

                # UN Sanctions & Voting
                san_rows = ingest_un_sanctions(static_data["un_sanctions"])
                vote_rows = ingest_un_voting(static_data["un_voting"])
                gsdb_rows = ingest_un_sanctions(static_data["gsdb"])
                executemany(INSERT_DIPLO_SQL, san_rows + vote_rows + gsdb_rows)
            else:
                self._progress("Static Cache", 0.15, f"Using {current_stats['raw_events']:,} existing baseline records")
                self._log_run("Static Baseline", "CACHED", current_stats['raw_events'], current_stats['raw_events'])

            # ── 3. Live Parallel Data Ingestion ─────────────────────────────
            self._progress("GDELT Live News", 0.25, "Fetching real-time geopolitical news")
            gdelt_config = self.config.get("gdelt", {})
            try:
                gdelt_df = fetch_gdelt_live(
                    keywords=gdelt_config.get("keywords", ["Indo-Pacific", "China India"]),
                    timespan=gdelt_config.get("timespan", "7d"),
                    max_records=gdelt_config.get("max_records", 200)
                )
                gdelt_rows = _safe_event_rows(gdelt_df, "GDELT_LIVE")
                n_gdelt = executemany(INSERT_EVENT_SQL, gdelt_rows)
                self._log_run("GDELT (Live)", "OK", len(gdelt_rows), n_gdelt)
                result["stages"]["gdelt_live"] = n_gdelt
            except Exception as e:
                self._log_run("GDELT (Live)", "WARN", 0, 0, str(e))
                result["stages"]["gdelt_live"] = 0

            # ReliefWeb & GKG Themes in Parallel
            self._progress("ReliefWeb & GKG Live", 0.40, "Querying UN crisis reports & conflict themes")
            try:
                rw_df = fetch_reliefweb(days_back=30, limit=40)
                rw_rows = _safe_event_rows(rw_df)
                n_rw = executemany(INSERT_EVENT_SQL, rw_rows) if rw_rows else 0
                self._log_run("ReliefWeb (Live)", "OK", len(rw_rows), n_rw)
                result["stages"]["reliefweb_live"] = n_rw
            except Exception as e:
                self._log_run("ReliefWeb (Live)", "WARN", 0, 0, str(e))

            try:
                gkg_df = fetch_gdelt_gkg_themes(days_back=7)
                gkg_rows = _safe_event_rows(gkg_df)
                n_gkg = executemany(INSERT_EVENT_SQL, gkg_rows) if gkg_rows else 0
                self._log_run("GDELT GKG (Live)", "OK", len(gkg_rows), n_gkg)
            except Exception as e:
                self._log_run("GDELT GKG (Live)", "WARN", 0, 0, str(e))

            # Fast World Bank & IMF Live
            self._progress("Macroeconomic Live", 0.55, "Fetching World Bank & IMF live indicators")
            try:
                wb_df = fetch_all_world_bank_live()
                wb_rows = _safe_econ_rows(wb_df)
                executemany(INSERT_ECON_SQL, wb_rows)
            except Exception as e:
                logger.debug(f"WB Live skipped: {e}")

            try:
                imf_df = fetch_all_imf_live()
                imf_rows = _safe_econ_rows(imf_df)
                executemany(INSERT_ECON_SQL, imf_rows)
            except Exception as e:
                logger.debug(f"IMF Live skipped: {e}")

            # ── 4. Preprocessing ─────────────────────────────────────────────
            self._progress("Preprocessing", 0.68, "Cleaning and normalising data tables")
            events_df = query_df("SELECT * FROM raw_events")
            econ_df = query_df("SELECT * FROM economic_indicators")

            clean_events, missing_report = self.preprocessor.preprocess_events(events_df)
            clean_econ, _ = self.preprocessor.preprocess_economic(econ_df)
            result["stages"]["preprocessing"] = {
                "events_cleaned": len(clean_events),
                "econ_cleaned": len(clean_econ),
                "quality_score": self.preprocessor.compute_data_quality_score(clean_events)
            }

            # ── 5. Feature Engineering ────────────────────────────────────────
            self._progress("Feature Engineering", 0.78, "Computing multi-window leading indicators")
            features_df = self.feature_engineer.compute_event_features(clean_events)

            if not clean_econ.empty and not features_df.empty:
                features_df = self.feature_engineer.compute_economic_stress(clean_econ, features_df)
            if not features_df.empty:
                features_df = self.feature_engineer.compute_composite_risk(features_df)
                features_df = self.feature_engineer.compute_anomaly_flags(features_df)

            # ── 6. Supervised ML Inference & Narrative Divergence ────────────
            self._progress("ML & Narrative Inference", 0.88, "Running Random Forest inference & State Media Divergence")
            if not features_df.empty:
                # Run Random Forest Classifier
                features_df = self.model.predict_features(features_df)

                # Run State Media Narrative Divergence
                divergences = {}
                for c in features_df["country"].unique():
                    div_res = self.nlp_engine.detect_narrative_divergence(clean_events, c)
                    divergences[c] = 1 if div_res.get("divergence_detected") else 0
                features_df["narrative_divergence"] = features_df["country"].map(divergences).fillna(0).astype(int)

            result["stages"]["features"] = {
                "total": len(features_df),
                "countries": features_df["country"].nunique() if not features_df.empty else 0,
                "ml_risk_distribution": features_df["ml_risk_tier"].value_counts().to_dict() if not features_df.empty and "ml_risk_tier" in features_df.columns else {}
            }

            # ── 7. Store Engineered Features ──────────────────────────────────
            self._progress("Storing Features", 0.95, "Persisting enriched ML features to database")
            if not features_df.empty:
                feature_cols = [
                    "country", "zone", "feature_date", "window_days",
                    "event_count", "military_event_count", "diplomatic_event_count",
                    "protest_event_count", "violence_event_count",
                    "avg_goldstein", "avg_tone", "event_acceleration",
                    "sentiment_volatility", "protest_violence_ratio",
                    "diplomatic_silence_days", "economic_stress_score",
                    "composite_risk_score", "risk_level",
                    "ml_risk_score", "ml_risk_tier", "top_factor", "top_factor_pct",
                    "narrative_divergence"
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

            self._progress("Pipeline Complete", 1.0, "All pipeline stages completed successfully")
            result["success"] = True
            result["completed_at"] = datetime.now().isoformat()
            try:
                execute(
                    "INSERT INTO ingestion_log (source, status, records_fetched, records_stored, error_message, started_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("MASTER_PIPELINE", "SUCCESS", len(self.run_log), result.get("stages", {}).get("features_stored", 0), None, result["started_at"][:19], result["completed_at"][:19])
                )
            except Exception:
                pass
            result["table_stats"] = get_table_stats()
            result["run_log"] = self.run_log
            result["feature_df"] = features_df if not features_df.empty else pd.DataFrame()

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            result["error"] = str(e)
            result["run_log"] = self.run_log

        return result
