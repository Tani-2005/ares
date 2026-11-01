"""
ARES "What-If" Counterfactual Simulation Engine (PRD §2.2 Persona B & SRS FR-14).
Enables geopolitical strategists to simulate hypothetical policy shocks,
military surges, and diplomatic breakdowns, observing real-time risk transitions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from model import get_ares_model, FEATURE_COLUMNS, FEATURE_BASELINES
from causal_matrix import CAUSAL_DEPENDENCY_MATRIX

class WhatIfSimulator:
    """Simulates counterfactual geopolitical scenarios and estimates risk deltas."""

    def __init__(self):
        self.model = get_ares_model()

    def simulate_scenario(
        self,
        base_row: pd.Series,
        military_delta: int = 0,
        tone_delta: float = 0.0,
        accel_delta: float = 0.0,
        silence_delta: int = 0,
        econ_delta: float = 0.0,
        zone_b_shock_actor: str = "None",
        zone_b_shock_pts: float = 0.0
    ) -> Dict[str, Any]:
        """
        Runs counterfactual simulation:
        1. Evaluates baseline risk score and tier.
        2. Applies simulated perturbations.
        3. Factors in Zone B -> Zone A causal spillover.
        4. Re-predicts via trained Random Forest model.
        5. Returns comparison metrics and narrative causal chain.
        """
        country = str(base_row.get("country", "Unknown"))

        # Base prediction
        base_df = pd.DataFrame([base_row]).reset_index(drop=True)
        pred_base = self.model.predict_features(base_df).iloc[0]
        base_score = float(pred_base["ml_risk_score"])
        base_tier = str(pred_base["ml_risk_tier"])
        base_top_factor = str(pred_base["top_factor"])

        # Calculate Zone B spillover if selected
        spillover_pts = 0.0
        if zone_b_shock_actor != "None" and zone_b_shock_pts > 0:
            alpha = CAUSAL_DEPENDENCY_MATRIX.get(zone_b_shock_actor, {}).get(country, 0.15)
            spillover_pts = zone_b_shock_pts * alpha * 0.40

        # Create counterfactual row
        sim_row = base_row.copy()
        sim_row["military_event_count"] = max(0, int(sim_row.get("military_event_count", 2) + military_delta))
        sim_row["event_count"] = max(1, int(sim_row.get("event_count", 20) + military_delta))
        sim_row["violence_event_count"] = sim_row["military_event_count"]
        sim_row["avg_tone"] = float(np.clip(sim_row.get("avg_tone", 0.0) + tone_delta, -15.0, 15.0))
        sim_row["avg_goldstein"] = float(np.clip(sim_row.get("avg_goldstein", 0.0) + (tone_delta * 0.6), -10.0, 10.0))
        sim_row["event_acceleration"] = float(sim_row.get("event_acceleration", 0.0) + accel_delta)
        sim_row["sentiment_volatility"] = max(0.2, float(sim_row.get("sentiment_volatility", 1.2) + abs(tone_delta) * 0.25))
        sim_row["diplomatic_silence_days"] = max(0, int(sim_row.get("diplomatic_silence_days", 5) + silence_delta))
        sim_row["economic_stress_score"] = float(np.clip(sim_row.get("economic_stress_score", 0.25) + econ_delta + (spillover_pts / 100.0), 0.0, 1.0))

        # Re-predict
        sim_df = pd.DataFrame([sim_row]).reset_index(drop=True)
        pred_sim = self.model.predict_features(sim_df).iloc[0]
        sim_score = float(pred_sim["ml_risk_score"])

        # Add spillover directly if substantial
        final_sim_score = min(99.0, round(sim_score + spillover_pts, 1))
        sim_tier = "RED" if final_sim_score >= 66.0 else ("AMBER" if final_sim_score >= 33.0 else "GREEN")
        sim_top_factor = str(pred_sim["top_factor"])

        score_delta = round(final_sim_score - base_score, 1)

        # Build analyst narrative chain
        drivers = []
        if military_delta > 0:
            drivers.append(f"+{military_delta} kinetic military incidents")
        if tone_delta < 0:
            drivers.append(f"{tone_delta:.1f} tone collapse in media coverage")
        if accel_delta > 0:
            drivers.append(f"+{accel_delta:.0f} WoW event acceleration")
        if silence_delta > 0:
            drivers.append(f"+{silence_delta} days diplomatic freeze")
        if econ_delta > 0:
            drivers.append(f"+{econ_delta:.2f} macroeconomic stress index")
        if spillover_pts > 0:
            drivers.append(f"+{spillover_pts:.1f} pts {zone_b_shock_actor} policy spillover")

        drivers_text = ", ".join(drivers) if drivers else "baseline stability"
        narrative = (
            f"Simulated posture shifts risk from {base_score:.1f} [{base_tier}] to {final_sim_score:.1f} [{sim_tier}] "
            f"({'+' if score_delta>=0 else ''}{score_delta} pts). Driven primarily by: {drivers_text}."
        )

        return {
            "country": country,
            "base_score": base_score,
            "base_tier": base_tier,
            "base_top_factor": base_top_factor,
            "sim_score": final_sim_score,
            "sim_tier": sim_tier,
            "sim_top_factor": sim_top_factor,
            "score_delta": score_delta,
            "spillover_pts": round(spillover_pts, 1),
            "narrative_chain": narrative,
            "simulated_row": sim_row
        }

