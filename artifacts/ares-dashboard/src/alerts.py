"""
ARES Active Tactical Alerts & Notification Center (SRS FR-13).
Scans live intelligence for critical thresholds, manages alert queues,
and logs automated notification dispatches to defense command centers.
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict

class AlertManager:
    """Manages active tactical escalation alerts and analyst acknowledgments."""

    def __init__(self):
        self.dispatched_logs = []

    def scan_for_alerts(self, features_df: pd.DataFrame) -> List[Dict]:
        """Scans engineered features for critical conflict triggers."""
        alerts = []
        if features_df.empty:
            return alerts

        w14 = features_df[features_df["window_days"] == 14] if "window_days" in features_df.columns else features_df

        for idx, row in w14.iterrows():
            country = str(row.get("country", "Unknown"))
            score = float(row.get("ml_risk_score", row.get("composite_risk_score", 0.0)) or 0.0)
            accel = float(row.get("event_acceleration", 0.0) or 0.0)
            divergence = int(row.get("narrative_divergence", 0) or 0)
            anomaly = bool(row.get("is_anomaly", False))
            top_factor = str(row.get("top_factor", "Military Acceleration"))

            # Trigger 1: Critical Red Escalation
            if score >= 66.0:
                alerts.append({
                    "id": f"ALT-{country[:3].upper()}-01",
                    "country": country,
                    "severity": "CRITICAL",
                    "score": round(score, 1),
                    "badge_color": "#da3633",
                    "trigger_title": "Critical Conflict Escalation Breach",
                    "trigger_desc": f"14-day risk score reached {score:.1f}/100. Dominant leading factor: {top_factor}.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommended_action": "Notify J2 Strategic Watchkeeper; initiate tactical reconnaissance."
                })

            # Trigger 2: High Event Acceleration Surge
            elif accel >= 25.0:
                alerts.append({
                    "id": f"ALT-{country[:3].upper()}-02",
                    "country": country,
                    "severity": "HIGH",
                    "score": round(score, 1),
                    "badge_color": "#d29922",
                    "trigger_title": "Sharp Event Acceleration Surge",
                    "trigger_desc": f"Week-over-week kinetic clash acceleration exceeded +{accel:.0f} events above baseline.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommended_action": "Cross-reference border NOTAMs and naval AIS movement."
                })

            # Trigger 3: State Media Narrative Divergence
            elif divergence == 1:
                alerts.append({
                    "id": f"ALT-{country[:3].upper()}-03",
                    "country": country,
                    "severity": "MEDIUM",
                    "score": round(score, 1),
                    "badge_color": "#a371f7",
                    "trigger_title": "State Propaganda Narrative Divergence",
                    "trigger_desc": "State media output contradicts independent reporting of troop buildup and hostility.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommended_action": "Flag adversary information warfare stream; discount Tier 2 sentiment scores."
                })

        return alerts

    def dispatch_notification(self, alert_id: str, recipient: str = "Defense Strategic Command") -> Dict:
        """Simulates automated webhook or encrypted dispatch of tactical alert."""
        record = {
            "alert_id": alert_id,
            "recipient": recipient,
            "dispatched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "DELIVERED",
            "protocol": "HTTPS Webhook / REST",
            "payload_hash": f"SHA256:{abs(hash(alert_id + recipient)) % 10000000:07d}"
        }
        self.dispatched_logs.append(record)
        return record

