import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts", "ares-dashboard", "src"))

from simulation import WhatIfSimulator
from alerts import AlertManager
from causal_matrix import compute_causal_spillover


def test_what_if_simulation_sensitivity():
    sim = WhatIfSimulator()
    base_row = pd.Series({
        "country": "India",
        "military_event_count": 5,
        "event_count": 25,
        "violence_event_count": 5,
        "avg_goldstein": 1.0,
        "avg_tone": 1.0,
        "event_acceleration": 0.0,
        "sentiment_volatility": 1.5,
        "protest_violence_ratio": 2.0,
        "diplomatic_silence_days": 5,
        "economic_stress_score": 0.30
    })

    # Scenario: Heavy military spike and negative tone drop
    res = sim.simulate_scenario(
        base_row,
        military_delta=40,
        tone_delta=-8.0,
        accel_delta=35.0,
        silence_delta=20,
        zone_b_shock_actor="United States",
        zone_b_shock_pts=45.0
    )

    assert res["sim_score"] > res["base_score"]
    assert res["score_delta"] > 20.0
    assert "narrative_chain" in res
    assert res["spillover_pts"] > 0


def test_causal_spillover():
    shocks = {"United States": 50.0, "European Union": 30.0}
    df = compute_causal_spillover(shocks)
    assert not df.empty
    assert "target_country" in df.columns
    assert "induced_risk_pts" in df.columns
    # Taiwan/China should be top affected by US shock
    top_country = df.iloc[0]["target_country"]
    assert top_country in ["Taiwan", "China", "Philippines"]


def test_alert_manager():
    mgr = AlertManager()
    features = pd.DataFrame([
        {"country": "CountryA", "window_days": 14, "ml_risk_score": 78.5, "event_acceleration": 10.0, "narrative_divergence": 0},
        {"country": "CountryB", "window_days": 14, "ml_risk_score": 45.0, "event_acceleration": 35.0, "narrative_divergence": 0},
        {"country": "CountryC", "window_days": 14, "ml_risk_score": 30.0, "event_acceleration": 2.0, "narrative_divergence": 1},
        {"country": "CountryD", "window_days": 14, "ml_risk_score": 15.0, "event_acceleration": 0.0, "narrative_divergence": 0}
    ])

    alerts = mgr.scan_for_alerts(features)
    assert len(alerts) == 3  # CountryA (RED), CountryB (Accel), CountryC (Divergence)
    severities = [a["severity"] for a in alerts]
    assert "CRITICAL" in severities
    assert "HIGH" in severities
    assert "MEDIUM" in severities

    dispatch = mgr.dispatch_notification(alerts[0]["id"])
    assert dispatch["status"] == "DELIVERED"


def test_what_if_non_zero_index_series():
    """Verify that a Series with non-zero index label (e.g. index 21) does not raise IndexError."""
    sim = WhatIfSimulator()
    df = pd.DataFrame([{
        "country": "Pakistan",
        "military_event_count": 8,
        "event_count": 30,
        "avg_goldstein": -2.0,
        "avg_tone": -3.0,
        "event_acceleration": 15.0,
        "sentiment_volatility": 2.0,
        "diplomatic_silence_days": 12,
        "economic_stress_score": 0.45
    }], index=[21])

    c_row = df.loc[21]
    res = sim.simulate_scenario(c_row, military_delta=10, tone_delta=-2.0)
    assert res is not None
    assert "sim_score" in res
    assert res["base_score"] > 0


