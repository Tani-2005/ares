import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts", "ares-dashboard", "src"))

from geo_viz import create_world_theater_map, create_3d_hotspot_deck, STRATEGIC_HOTSPOTS, MARITIME_CHOKEPOINTS
from confidence import compute_data_confidence
from dossier import generate_intelligence_dossier
from daemon import start_background_daemon, stop_background_daemon, get_daemon_status


def test_world_theater_map_generation():
    df = pd.DataFrame([
        {"country": "India", "ml_risk_score": 68.5, "ml_risk_tier": "RED", "top_factor": "Event Acceleration"},
        {"country": "Pakistan", "ml_risk_score": 75.0, "ml_risk_tier": "RED", "top_factor": "Military Surge"},
        {"country": "Taiwan", "ml_risk_score": 62.0, "ml_risk_tier": "AMBER", "top_factor": "Negative Tone"}
    ])

    fig = create_world_theater_map(df, selected_country="India", show_hotspots=True, show_chokepoints=True, show_causal_arcs=True)
    assert fig is not None
    # Traces: Zone A choropleth, Zone B choropleth, Causal Arcs (6), Hotspots, Chokepoints, Selected Country = 11 traces
    assert len(fig.data) >= 5
    trace_types = [t.type for t in fig.data]
    assert "choropleth" in trace_types
    assert "scattergeo" in trace_types


def test_3d_hotspot_deck_generation():
    df = pd.DataFrame([
        {"country": "India", "composite_risk_score": 70.0, "risk_level": "RED", "top_factor": "Event Acceleration"}
    ])
    deck = create_3d_hotspot_deck(df, show_satellite=True, show_maritime_ais=True)
    assert deck is not None
    assert len(deck.layers) == 4  # Column, Scatter rings, Satellite, AIS


def test_data_confidence_computation():
    events_df = pd.DataFrame([
        {"country": "India", "source": "ACLED"},
        {"country": "India", "source": "GDELT"},
        {"country": "India", "source": "ReliefWeb"},
        {"country": "Maldives", "source": "GDELT"}
    ] * 50)

    c_row = pd.Series({
        "country": "India",
        "military_event_count": 10,
        "avg_tone": -2.0,
        "event_acceleration": 12.0,
        "sentiment_volatility": 1.8,
        "diplomatic_silence_days": 5,
        "economic_stress_score": 0.3
    })

    conf_india = compute_data_confidence("India", events_df, c_row)
    assert conf_india["confidence_score"] >= 70.0
    assert conf_india["confidence_tier"] in ["HIGH", "MODERATE"]

    conf_sparse = compute_data_confidence("Bhutan", pd.DataFrame())
    assert conf_sparse["confidence_score"] <= 50.0
    assert conf_sparse["confidence_tier"] == "LOW DENSITY"


def test_intelligence_dossier_generation():
    feature_row = pd.Series({
        "country": "Taiwan",
        "ml_risk_score": 78.4,
        "ml_risk_tier": "RED",
        "top_factor": "Hostile Narrative Divergence",
        "window_days": 14
    })

    waterfall = {
        "baseline_score": 22.0,
        "final_score": 78.4,
        "contributions": [
            {"feature": "Negative Media Tone", "delta": 24.5, "actual_value": -6.2},
            {"feature": "Event Acceleration", "delta": 18.0, "actual_value": 35.0}
        ]
    }

    confidence = {"confidence_score": 91.2, "confidence_tier": "HIGH"}

    dossier = generate_intelligence_dossier("Taiwan", feature_row, waterfall, confidence)
    assert "html" in dossier
    assert "markdown" in dossier
    assert "report_id" in dossier
    assert "ARES-DOSSIER-TAI" in dossier["report_id"]
    assert "CRITICAL ESCALATION (RED)" in dossier["html"]
    assert "Negative Media Tone" in dossier["html"]
    assert "Taiwan" in dossier["markdown"]


def test_daemon_lifecycle():
    stat_init = get_daemon_status()
    assert isinstance(stat_init, dict)
    assert "is_running" in stat_init

    # Stop check
    stop_background_daemon()
    stat_stopped = get_daemon_status()
    assert stat_stopped["is_running"] is False

