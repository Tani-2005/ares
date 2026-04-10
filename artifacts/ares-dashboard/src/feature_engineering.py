"""
Feature Engineering Module for ARES.
Computes all leading indicators from preprocessed data.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

ZONE_A_COUNTRIES = [
    "India", "Pakistan", "China", "Bangladesh", "Sri Lanka", "Nepal",
    "Myanmar", "Thailand", "Vietnam", "Philippines", "Indonesia",
    "Malaysia", "Singapore", "South Korea", "Japan", "Taiwan"
]
ZONE_B_COUNTRIES = [
    "United States", "Canada", "Germany", "France", "United Kingdom", "Russia"
]

MILITARY_KEYWORDS = {
    "Battles", "Explosions/Remote violence", "Military", "Airstrike",
    "Hostile Diplomatic", "Armed", "Violence against civilians"
}
DIPLOMATIC_KEYWORDS = {
    "Diplomatic", "Consult", "Cooperate", "Negotiate", "Summit", "Treaty",
    "Strategic developments"
}
PROTEST_KEYWORDS = {
    "Protests", "Riots", "Demonstration", "Civil unrest", "Strike"
}


def classify_event_type(event_type: str, sub_type: str = "") -> str:
    combined = f"{event_type} {sub_type}".upper()
    if any(k.upper() in combined for k in MILITARY_KEYWORDS):
        return "military"
    elif any(k.upper() in combined for k in DIPLOMATIC_KEYWORDS):
        return "diplomatic"
    elif any(k.upper() in combined for k in PROTEST_KEYWORDS):
        return "protest"
    return "other"


class FeatureEngineer:
    def __init__(self, windows: List[int] = None):
        self.windows = windows or [7, 14, 30]
        self.feature_log = []

    def _log(self, feature: str, detail: str):
        self.feature_log.append({
            "feature": feature,
            "detail": detail,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        logger.info(f"[Feature] {feature}: {detail}")

    def compute_event_features(self, events_df: pd.DataFrame, as_of_date: str = None) -> pd.DataFrame:
        """Compute event-based features per country per rolling window."""
        if events_df.empty:
            return pd.DataFrame()

        df = events_df.copy()
        df["event_date"] = pd.to_datetime(df["event_date"])

        if as_of_date is None:
            as_of_date = df["event_date"].max()
        else:
            as_of_date = pd.to_datetime(as_of_date)

        df["event_class"] = df.apply(
            lambda r: classify_event_type(
                str(r.get("event_type", "")), str(r.get("sub_type", ""))
            ), axis=1
        )

        countries_zones = (
            df[["country", "zone"]].drop_duplicates()
            .set_index("country")["zone"].to_dict()
        )

        records = []
        for country in df["country"].unique():
            zone = countries_zones.get(country, "A")
            c_df = df[df["country"] == country].copy()

            for window in self.windows:
                window_start = as_of_date - timedelta(days=window)
                w_df = c_df[(c_df["event_date"] >= window_start) & (c_df["event_date"] <= as_of_date)]

                prev_window_start = window_start - timedelta(days=window)
                p_df = c_df[(c_df["event_date"] >= prev_window_start) & (c_df["event_date"] < window_start)]

                total_events = len(w_df)
                prev_total = len(p_df)
                military_count = int((w_df["event_class"] == "military").sum())
                diplomatic_count = int((w_df["event_class"] == "diplomatic").sum())
                protest_count = int((w_df["event_class"] == "protest").sum())
                violence_count = military_count

                avg_goldstein = float(w_df["goldstein_scale"].mean()) if "goldstein_scale" in w_df.columns and len(w_df) > 0 else 0.0
                avg_tone = float(w_df["avg_tone"].mean()) if "avg_tone" in w_df.columns and len(w_df) > 0 else 0.0

                acceleration = float(total_events - prev_total) if prev_total > 0 else float(total_events)

                if len(w_df) > 1 and "avg_tone" in w_df.columns:
                    sentiment_volatility = float(w_df["avg_tone"].std())
                else:
                    sentiment_volatility = 0.0

                protest_violence_ratio = (protest_count / max(violence_count, 1)) if violence_count > 0 else 0.0

                # Diplomatic silence: days since last diplomatic event
                diplo_events = c_df[c_df["event_class"] == "diplomatic"].sort_values("event_date")
                if len(diplo_events) > 0:
                    last_diplo = diplo_events["event_date"].max()
                    diplomatic_silence = max(0, (as_of_date - last_diplo).days)
                else:
                    diplomatic_silence = window

                records.append({
                    "country": country,
                    "zone": zone,
                    "feature_date": as_of_date.strftime("%Y-%m-%d"),
                    "window_days": window,
                    "event_count": total_events,
                    "military_event_count": military_count,
                    "diplomatic_event_count": diplomatic_count,
                    "protest_event_count": protest_count,
                    "violence_event_count": violence_count,
                    "avg_goldstein": round(avg_goldstein, 4),
                    "avg_tone": round(avg_tone, 4),
                    "event_acceleration": round(acceleration, 4),
                    "sentiment_volatility": round(sentiment_volatility, 4),
                    "protest_violence_ratio": round(protest_violence_ratio, 4),
                    "diplomatic_silence_days": diplomatic_silence,
                })

        features_df = pd.DataFrame(records)
        self._log("Event Features", f"Computed {len(features_df)} records across {len(self.windows)} windows")
        return features_df

    def compute_economic_stress(self, econ_df: pd.DataFrame, features_df: pd.DataFrame) -> pd.DataFrame:
        """Add economic stress signal to features."""
        if econ_df.empty or features_df.empty:
            return features_df

        latest_year = pd.to_datetime(features_df["feature_date"].iloc[0]).year
        econ_recent = econ_df[econ_df["year"] >= latest_year - 2].copy()

        stress_scores = {}
        for country in features_df["country"].unique():
            c_econ = econ_recent[econ_recent["country"] == country]
            score = 0.0
            n = 0
            for _, row in c_econ.iterrows():
                indicator = str(row.get("indicator_type", row.get("indicator", "")))
                value = float(row.get("value", 0))
                if "GDP" in indicator or "Growth" in indicator:
                    score += max(0, (2.0 - value) / 8.0)
                    n += 1
                elif "Inflation" in indicator or "CPI" in indicator:
                    score += max(0, (value - 3.0) / 15.0)
                    n += 1
                elif "Unemployment" in indicator:
                    score += max(0, (value - 5.0) / 15.0)
                    n += 1
            stress_scores[country] = min(1.0, score / max(n, 1)) if n > 0 else 0.3

        features_df = features_df.copy()
        features_df["economic_stress_score"] = features_df["country"].map(
            lambda c: round(stress_scores.get(c, 0.3), 4)
        )
        self._log("Economic Stress", f"Computed stress scores for {len(stress_scores)} countries")
        return features_df

    def compute_composite_risk(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute composite risk score (0-100) combining all features.
        Weights aligned with ARES PRD signal hierarchy.
        """
        if features_df.empty:
            return features_df

        df = features_df.copy()

        def safe_zscore(series: pd.Series) -> pd.Series:
            mu = series.mean()
            sigma = series.std()
            if sigma == 0 or pd.isna(sigma):
                return pd.Series(np.zeros(len(series)), index=series.index)
            return (series - mu) / sigma

        def sigmoid(x: float) -> float:
            return 1 / (1 + np.exp(-x))

        weights = {
            "military_event_count": 0.30,
            "event_acceleration": 0.20,
            "sentiment_volatility": 0.15,
            "avg_tone_neg": 0.15,
            "diplomatic_silence_days": 0.10,
            "economic_stress_score": 0.10,
        }

        df["avg_tone_neg"] = -df["avg_tone"]

        risk_signal = pd.Series(np.zeros(len(df)), index=df.index)
        for feature, weight in weights.items():
            if feature in df.columns:
                z = safe_zscore(df[feature].fillna(0))
                risk_signal += weight * z

        df["composite_risk_score"] = risk_signal.apply(
            lambda x: round(sigmoid(x) * 100, 2)
        )

        def risk_level(score: float) -> str:
            if score >= 66:
                return "RED"
            elif score >= 33:
                return "AMBER"
            return "GREEN"

        df["risk_level"] = df["composite_risk_score"].apply(risk_level)
        df = df.drop(columns=["avg_tone_neg"], errors="ignore")

        self._log(
            "Composite Risk",
            f"RED: {(df['risk_level']=='RED').sum()}, "
            f"AMBER: {(df['risk_level']=='AMBER').sum()}, "
            f"GREEN: {(df['risk_level']=='GREEN').sum()}"
        )
        return df

    def compute_rolling_trends(self, events_df: pd.DataFrame, country: str, days: int = 90) -> pd.DataFrame:
        """Compute daily event count rolling trend for a country (for charts)."""
        if events_df.empty:
            return pd.DataFrame()

        df = events_df.copy()
        df["event_date"] = pd.to_datetime(df["event_date"])
        c_df = df[df["country"] == country].copy()

        if c_df.empty:
            return pd.DataFrame()

        end_date = c_df["event_date"].max()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start_date, end_date, freq="D")

        daily_counts = c_df.groupby("event_date").size().reindex(date_range, fill_value=0)
        daily_tone = c_df.groupby("event_date")["avg_tone"].mean().reindex(date_range).interpolate()
        daily_goldstein = c_df.groupby("event_date")["goldstein_scale"].mean().reindex(date_range).interpolate()

        trend_df = pd.DataFrame({
            "date": date_range,
            "event_count": daily_counts.values,
            "avg_tone": daily_tone.values,
            "avg_goldstein": daily_goldstein.values,
            "rolling_7d": pd.Series(daily_counts.values).rolling(7, min_periods=1).mean().values,
            "rolling_30d": pd.Series(daily_counts.values).rolling(30, min_periods=1).mean().values,
        })
        return trend_df

    def compute_anomaly_flags(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Flag statistical anomalies using z-score method."""
        if features_df.empty or len(features_df) < 5:
            features_df = features_df.copy()
            features_df["is_anomaly"] = False
            return features_df

        from sklearn.ensemble import IsolationForest

        numeric_cols = [
            "event_count", "military_event_count", "event_acceleration",
            "sentiment_volatility", "diplomatic_silence_days"
        ]
        available = [c for c in numeric_cols if c in features_df.columns]
        X = features_df[available].fillna(0)

        if len(X) < 5:
            features_df = features_df.copy()
            features_df["is_anomaly"] = False
            return features_df

        iso = IsolationForest(contamination=0.1, random_state=42)
        preds = iso.fit_predict(X)
        features_df = features_df.copy()
        features_df["is_anomaly"] = (preds == -1)
        n_anomalies = (preds == -1).sum()
        self._log("Anomaly Detection", f"Flagged {n_anomalies} anomalous country-window combinations")
        return features_df

    def get_feature_importance_proxy(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Compute feature importance as correlation with composite risk score."""
        feature_cols = [
            "event_count", "military_event_count", "diplomatic_event_count",
            "protest_event_count", "event_acceleration", "sentiment_volatility",
            "avg_goldstein", "avg_tone", "diplomatic_silence_days",
            "economic_stress_score"
        ]
        available = [c for c in feature_cols if c in features_df.columns and features_df[c].notna().any()]
        if "composite_risk_score" not in features_df.columns or not available:
            return pd.DataFrame()

        corrs = []
        for col in available:
            try:
                corr = features_df[col].corr(features_df["composite_risk_score"])
                corrs.append({"feature": col, "importance": abs(corr), "direction": "+" if corr > 0 else "-"})
            except Exception:
                pass

        imp_df = pd.DataFrame(corrs).sort_values("importance", ascending=False)
        return imp_df

    def get_feature_log(self) -> pd.DataFrame:
        return pd.DataFrame(self.feature_log)
