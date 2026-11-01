import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts", "ares-dashboard", "src"))

from model import get_ares_model, FEATURE_COLUMNS, FEATURE_BASELINES


def test_model_initialization():
    model = get_ares_model()
    assert model is not None
    assert model.model is not None
    assert len(model.feature_importances_) == len(FEATURE_COLUMNS)
    assert model.metrics.get("cv_accuracy", 0) > 0.80


def test_model_predictions():
    model = get_ares_model()
    sample = pd.DataFrame([{
        "country": "Testland",
        "military_event_count": 50,
        "event_count": 120,
        "violence_event_count": 50,
        "avg_goldstein": -7.5,
        "avg_tone": -8.0,
        "event_acceleration": 45.0,
        "sentiment_volatility": 5.5,
        "protest_violence_ratio": 0.2,
        "diplomatic_silence_days": 30,
        "economic_stress_score": 0.85
    }])

    pred = model.predict_features(sample)
    assert not pred.empty
    score = float(pred["ml_risk_score"].iloc[0])
    tier = str(pred["ml_risk_tier"].iloc[0])
    assert 0.0 <= score <= 100.0
    assert tier == "RED"
    assert "top_factor" in pred.columns
    assert "top_factor_pct" in pred.columns


def test_waterfall_attribution():
    model = get_ares_model()
    row = pd.Series({
        "country": "Testland",
        "military_event_count": 35,
        "avg_tone": -6.0,
        "event_acceleration": 20.0,
        "sentiment_volatility": 4.0,
        "diplomatic_silence_days": 20,
        "economic_stress_score": 0.70
    })

    explanation = model.explain_prediction_waterfall(row)
    assert "baseline_score" in explanation
    assert "final_score" in explanation
    assert "contributions" in explanation
    assert len(explanation["contributions"]) > 0
    # Final score should be substantially above baseline due to hostility
    assert explanation["final_score"] > explanation["baseline_score"]

