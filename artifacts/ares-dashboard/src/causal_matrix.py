"""
ARES Zone B → Zone A Causal Cross-Impact Engine (PRD §1.0 & §1.2).
Models how distal superpower policies, sanctions, and rhetoric (Zone B)
propagate downstream into Indo-Pacific conflict theater stability (Zone A).
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List

ZONE_B_ACTORS = ["United States", "European Union", "Russia", "United Kingdom"]
ZONE_A_THEATERS = [
    "China", "India", "Taiwan", "Philippines", "Pakistan",
    "Vietnam", "Myanmar", "South Korea", "Japan"
]

# Strategic Bilateral Causal Dependency Matrix (Alpha Coefficients: 0.0 to 1.0)
# Represents downstream sensitivity of Zone A nations to Zone B policy shocks
CAUSAL_DEPENDENCY_MATRIX = {
    "United States": {
        "Taiwan": 0.75,      # High sensitivity to US defense policy & arms sales
        "China": 0.68,       # Trade sanctions, export controls, tech embargoes
        "Philippines": 0.58, # EDCA base access, mutual defense treaty
        "Japan": 0.52,       # Security alliance, missile defense
        "South Korea": 0.48, # Extended deterrence, joint drills
        "India": 0.35,       # Quad coordination, tech transfers
        "Pakistan": 0.30,    # IMF loans, counter-terror diplomacy
        "Vietnam": 0.28,     # Comprehensive strategic partnership
        "Myanmar": 0.25      # Target sanctions on junta
    },
    "European Union": {
        "China": 0.55,       # Carbon tariffs, EV duties, trade disputes
        "Taiwan": 0.42,      # Parliamentary delegations, semiconductor ties
        "India": 0.32,       # Free trade negotiations, green energy
        "Russia": 0.80,      # Sanctions package, oil price cap
        "Myanmar": 0.35,     # Arms embargoes, asset freezes
        "Pakistan": 0.25,    # GSP+ trade status
        "Vietnam": 0.22      # EVFTA enforcement
    },
    "Russia": {
        "India": 0.58,       # Crude oil discounting, S-400 defense logistics
        "China": 0.65,       # 'No limits' partnership, joint naval patrols
        "Myanmar": 0.42,     # Arms supply to military regime
        "North Korea": 0.70, # Comprehensive strategic partnership
        "Pakistan": 0.24     # Energy corridor negotiations
    },
    "United Kingdom": {
        "China": 0.40,       # Hong Kong treaty disputes, naval carrier transits
        "Taiwan": 0.35,      # Informal defense dialogue
        "India": 0.30,       # FTA negotiations, historical diaspora
        "Pakistan": 0.28     # Commonwealth diplomacy
    }
}


def compute_causal_spillover(zone_b_shocks: Dict[str, float]) -> pd.DataFrame:
    """
    Computes downstream risk spillover on Zone A countries given Zone B policy shocks.
    zone_b_shocks: dict of {country: shock_magnitude (0 to 100)}
    e.g. {'United States': 40.0 (Sanction), 'European Union': 25.0 (Tariff)}
    """
    rows = []
    for za in ZONE_A_THEATERS:
        total_induced_risk = 0.0
        contributions = {}
        for zb, shock in zone_b_shocks.items():
            alpha = CAUSAL_DEPENDENCY_MATRIX.get(zb, {}).get(za, 0.10)
            induced = shock * alpha * 0.45  # Scaled impact
            total_induced_risk += induced
            contributions[zb] = round(induced, 1)

        rows.append({
            "target_country": za,
            "induced_risk_pts": round(total_induced_risk, 1),
            "primary_driver": max(contributions, key=contributions.get) if contributions else "None",
            "us_shock_impact": contributions.get("United States", 0.0),
            "eu_shock_impact": contributions.get("European Union", 0.0),
            "russia_shock_impact": contributions.get("Russia", 0.0)
        })

    df = pd.DataFrame(rows).sort_values("induced_risk_pts", ascending=False)
    return df


def get_causal_heatmap_fig() -> go.Figure:
    """Generate an interactive correlation heatmap of Zone B -> Zone A causal dependencies."""
    z_data = []
    for zb in ZONE_B_ACTORS:
        row = [CAUSAL_DEPENDENCY_MATRIX.get(zb, {}).get(za, 0.0) for za in ZONE_A_THEATERS]
        z_data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=ZONE_A_THEATERS,
        y=ZONE_B_ACTORS,
        colorscale="Viridis",
        hoverongaps=False,
        colorbar=dict(title="Causal Coupling (α)")
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        title="Zone B (Global Input) → Zone A (Theater Outcome) Causal Coupling Matrix",
        height=320,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(title="Zone A Conflict Theaters", gridcolor="#21262d"),
        yaxis=dict(title="Zone B Strategic Actors", gridcolor="#21262d")
    )
    return fig

