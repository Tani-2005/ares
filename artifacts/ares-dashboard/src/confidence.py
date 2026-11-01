"""
ARES Epistemic Uncertainty & Data Density Bounding Engine (PRD §5.2 & SRS NFR-08).
Evaluates open-source reporting density, source diversity, and feature completeness
to bound model confidence and prevent false positive alarms in data-sparse regions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

# Baseline source diversity threshold
RECOMMENDED_SOURCES = ["ACLED", "GDELT", "ReliefWeb", "World Bank"]

def compute_data_confidence(
    country: str,
    events_df: pd.DataFrame,
    feature_row: pd.Series = None
) -> Dict[str, Any]:
    """
    Computes a 0-100% Data Density & Epistemic Confidence Score for a given country.
    
    Formula:
      Score = (Coverage Weight * 45%) + (Source Diversity * 35%) + (Completeness * 20%)
    
    Tiers:
      - HIGH (>= 75%): Robust reporting density, high analytic confidence.
      - MODERATE (45% - 74%): Sufficient baseline coverage, standard vigilance.
      - LOW_DENSITY (< 45%): Sparse reporting; flagged with epistemic uncertainty boundary.
    """
    c_events = events_df[events_df["country"] == country] if not events_df.empty and "country" in events_df.columns else pd.DataFrame()
    event_count = len(c_events)
    
    # 1. Event reporting volume (0 to 45 pts)
    # 150+ events is considered full volume for an Indo-Pacific theater state
    coverage_ratio = min(1.0, event_count / 150.0)
    coverage_pts = coverage_ratio * 45.0
    
    # 2. Source diversity (0 to 35 pts)
    # 3+ distinct sources (e.g., GDELT + ACLED + ReliefWeb) gives full score
    n_sources = c_events["source"].nunique() if not c_events.empty and "source" in c_events.columns else 1
    diversity_ratio = min(1.0, n_sources / 3.0)
    diversity_pts = diversity_ratio * 35.0
    
    # 3. Feature completeness (0 to 20 pts)
    completeness_pts = 20.0
    if feature_row is not None and isinstance(feature_row, (pd.Series, dict)):
        zero_or_null = 0
        total_checked = 0
        for col in ["military_event_count", "avg_tone", "event_acceleration", "sentiment_volatility", "diplomatic_silence_days", "economic_stress_score"]:
            if col in feature_row:
                total_checked += 1
                val = feature_row.get(col, None)
                if val is None or pd.isna(val) or val == 0:
                    zero_or_null += 1
        if total_checked > 0:
            completeness_pts = max(5.0, (1.0 - (zero_or_null / total_checked)) * 20.0)
            
    confidence_score = round(coverage_pts + diversity_pts + completeness_pts, 1)
    confidence_score = max(10.0, min(99.0, confidence_score))
    
    if confidence_score >= 75.0:
        tier = "HIGH"
        badge_color = "#2ea043"
        desc = "High reporting density with multi-source validation."
    elif confidence_score >= 45.0:
        tier = "MODERATE"
        badge_color = "#d29922"
        desc = "Adequate reporting density; minor epistemic latency."
    else:
        tier = "LOW DENSITY"
        badge_color = "#8b949e"
        desc = "Sparse open-source data density; risk alerts bounded by uncertainty buffer."
        
    return {
        "country": country,
        "confidence_score": confidence_score,
        "confidence_tier": tier,
        "badge_color": badge_color,
        "event_count": event_count,
        "source_count": n_sources,
        "description": desc
    }

