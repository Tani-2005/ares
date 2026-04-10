"""
Data Preprocessing Module for ARES.
Handles cleaning, normalization, and alignment of multi-source data.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Tuple

logger = logging.getLogger(__name__)

ZONE_A_COUNTRIES = [
    "India", "Pakistan", "China", "Bangladesh", "Sri Lanka", "Nepal",
    "Myanmar", "Thailand", "Vietnam", "Philippines", "Indonesia",
    "Malaysia", "Singapore", "South Korea", "Japan", "Taiwan"
]
ZONE_B_COUNTRIES = [
    "United States", "Canada", "Germany", "France", "United Kingdom",
    "Russia", "European Union"
]
ALL_MONITORED = set(ZONE_A_COUNTRIES + ZONE_B_COUNTRIES)


class DataPreprocessor:
    def __init__(self):
        self.processing_log = []

    def _log(self, step: str, detail: str, records_in: int = 0, records_out: int = 0):
        entry = {
            "step": step,
            "detail": detail,
            "records_in": records_in,
            "records_out": records_out,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.processing_log.append(entry)
        logger.info(f"[{step}] {detail} ({records_in} → {records_out})")

    def normalize_dates(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        before = len(df)
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
        after = len(df)
        dropped = before - after
        if dropped > 0:
            self._log("Date Normalization", f"Dropped {dropped} rows with unparseable dates", before, after)
        df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        before = len(df)
        report = {}
        df = df.copy()
        for col in df.columns:
            n_missing = df[col].isna().sum()
            if n_missing > 0:
                pct = n_missing / len(df) * 100
                report[col] = {"missing": int(n_missing), "pct": round(pct, 2)}
                if df[col].dtype in [np.float64, np.int64]:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna("Unknown")
        after = len(df)
        self._log("Missing Value Handling", f"Imputed {sum(r['missing'] for r in report.values())} cells across {len(report)} columns", before, after)
        return df, report

    def standardize_country_names(self, df: pd.DataFrame, country_col: str) -> pd.DataFrame:
        before = df[country_col].nunique()
        variants = {
            "US": "United States", "USA": "United States", "U.S.": "United States",
            "U.S.A.": "United States", "United States of America": "United States",
            "UK": "United Kingdom", "U.K.": "United Kingdom", "Britain": "United Kingdom",
            "Great Britain": "United Kingdom", "England": "United Kingdom",
            "EU": "European Union", "Europe": "European Union",
            "PRC": "China", "People's Republic of China": "China",
            "Mainland China": "China",
            "ROK": "South Korea", "Republic of Korea": "South Korea",
            "DPRK": "North Korea",
            "Burma": "Myanmar",
            "Viet Nam": "Vietnam",
            "The Philippines": "Philippines",
            "UAE": "United Arab Emirates",
        }
        df = df.copy()
        df[country_col] = df[country_col].map(lambda x: variants.get(str(x).strip(), str(x).strip()) if pd.notna(x) else "Unknown")
        after = df[country_col].nunique()
        self._log("Country Standardization", f"Consolidated country names: {before} → {after} unique values", before, after)
        return df

    def filter_relevant_countries(self, df: pd.DataFrame, country_col: str, keep_unknown: bool = False) -> pd.DataFrame:
        before = len(df)
        if keep_unknown:
            mask = df[country_col].isin(ALL_MONITORED) | (df[country_col] == "Unknown")
        else:
            mask = df[country_col].isin(ALL_MONITORED)
        df = df[mask].copy()
        after = len(df)
        self._log("Country Filter", f"Kept {after} rows from monitored countries (dropped {before - after})", before, after)
        return df

    def remove_duplicates(self, df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates(subset=subset).copy() if subset else df.drop_duplicates().copy()
        after = len(df)
        if before > after:
            self._log("Deduplication", f"Removed {before - after} duplicate rows", before, after)
        return df

    def normalize_severity(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        df = df.copy()
        if col in df.columns and df[col].notna().any():
            series = df[col].astype(float)
            mn, mx = series.min(), series.max()
            if mx > mn:
                df[col] = (series - mn) / (mx - mn)
            else:
                df[col] = 0.5
        return df

    def clip_outliers(self, df: pd.DataFrame, col: str, method: str = "iqr") -> pd.DataFrame:
        df = df.copy()
        if col not in df.columns:
            return df
        series = df[col].astype(float)
        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 3 * iqr
            upper = q3 + 3 * iqr
        else:
            mu = series.mean()
            sigma = series.std()
            lower = mu - 3 * sigma
            upper = mu + 3 * sigma
        clipped = series.clip(lower=lower, upper=upper)
        n_clipped = (series != clipped).sum()
        if n_clipped > 0:
            self._log("Outlier Clipping", f"Clipped {n_clipped} values in '{col}' (IQR method)", len(df), len(df))
        df[col] = clipped
        return df

    def preprocess_events(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """Full preprocessing pipeline for event data."""
        self._log("Pipeline Start", f"Input: {len(df)} raw event records", len(df), len(df))

        df = self.normalize_dates(df, "event_date")
        df = self.standardize_country_names(df, "country")
        df = self.filter_relevant_countries(df, "country")
        df, missing_report = self.handle_missing_values(df)
        df = self.remove_duplicates(df)

        if "goldstein_scale" in df.columns:
            df = self.clip_outliers(df, "goldstein_scale")
        if "avg_tone" in df.columns:
            df = self.clip_outliers(df, "avg_tone")
        if "severity" in df.columns:
            df = self.normalize_severity(df, "severity")

        self._log("Pipeline Complete", f"Output: {len(df)} clean records", len(df), len(df))
        return df, missing_report

    def preprocess_economic(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        df = self.standardize_country_names(df, "country")
        df, missing_report = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        if "value" in df.columns:
            df = self.clip_outliers(df, "value")
        return df, missing_report

    def get_processing_report(self) -> pd.DataFrame:
        return pd.DataFrame(self.processing_log)

    def compute_data_quality_score(self, df: pd.DataFrame) -> dict:
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0

        scores = {
            "completeness": round(completeness * 100, 1),
            "total_records": len(df),
            "total_cells": total_cells,
            "missing_cells": int(missing_cells),
            "duplicate_rows": int(df.duplicated().sum()),
        }
        return scores
