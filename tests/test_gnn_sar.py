import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts", "ares-dashboard", "src"))

from gnn_engine import GeopoliticalGraphEngine
from sar_engine import SarReconnaissanceEngine, SAR_HOTSPOT_REGISTRY


def test_gnn_graph_construction_and_inference():
    gnn = GeopoliticalGraphEngine()
    features_df = pd.DataFrame([
        {"country": "India", "composite_risk_score": 68.0, "military_event_count": 8, "event_acceleration": 14.0},
        {"country": "China", "composite_risk_score": 72.0, "military_event_count": 10, "event_acceleration": 18.0},
        {"country": "Taiwan", "composite_risk_score": 65.0, "military_event_count": 6, "event_acceleration": 10.0}
    ])
    events_df = pd.DataFrame()

    res = gnn.run_gnn_inference(events_df, features_df)
    assert res is not None
    assert "actors" in res
    assert len(res["actors"]) >= 27
    assert "India" in res["actor_scores"]
    assert "topological_score" in res["actor_scores"]["India"]
    assert len(res["top_dyads"]) > 0

    # Verify high-tension dyad ordering
    top_sources = [d["source"] for d in res["top_dyads"][:5]]
    assert any(c in top_sources for c in ["India", "China", "United States"])


def test_gnn_plotly_visualization():
    gnn = GeopoliticalGraphEngine()
    features_df = pd.DataFrame([{"country": "India", "composite_risk_score": 60.0}])
    res = gnn.run_gnn_inference(pd.DataFrame(), features_df)
    fig = gnn.render_gnn_plotly_graph(res)
    assert fig is not None
    assert len(fig.data) >= 3  # edges, conflict_edges, nodes


def test_sar_hotspot_report_and_metrics():
    sar = SarReconnaissanceEngine()
    report = sar.get_hotspot_sar_report("Galwan Valley (LAC)")

    assert report is not None
    assert report["hotspot"] == "Galwan Valley (LAC)"
    assert report["delta_sigma_db"] > 0
    assert "Sentinel-1" in report["sensor"]
    assert report["severity"] in ["CRITICAL SURGE", "ELEVATED ACTIVITY", "BASELINE NOMINAL"]
    assert report["sar_confidence"] >= 80.0


def test_sar_backscatter_heatmap_generation():
    sar = SarReconnaissanceEngine()
    fig = sar.generate_radar_backscatter_heatmap("Pangong Tso Lake")
    assert fig is not None
    assert len(fig.data) == 1
    assert fig.data[0].type == "heatmap"
    assert fig.data[0].z.shape == (30, 30)

