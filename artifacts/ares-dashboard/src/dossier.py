"""
ARES Intelligence Dossier Export Generator (PRD §4.2 & SRS FR-16).
Produces standardized, command-level National Security Early-Warning Dossiers
in HTML and Markdown formats with full SHAP attribution and multi-INT correlation.
"""

import datetime
import pandas as pd
from typing import Dict, Any, Optional

def generate_intelligence_dossier(
    country: str,
    feature_row: pd.Series,
    waterfall_data: Optional[Dict[str, Any]] = None,
    confidence_data: Optional[Dict[str, Any]] = None,
    divergence_data: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Generates an official Command-Level Intelligence Briefing Dossier.
    Returns:
      {
        "html": "...full styled standalone HTML report...",
        "markdown": "...markdown formatted briefing..."
      }
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    report_id = f"ARES-DOSSIER-{country.upper()[:3]}-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
    
    score = float(feature_row.get("ml_risk_score", feature_row.get("composite_risk_score", 45.0)) or 45.0)
    tier = str(feature_row.get("ml_risk_tier", feature_row.get("risk_level", "AMBER")))
    top_factor = str(feature_row.get("top_factor", "Event Acceleration"))
    window_days = int(feature_row.get("window_days", 14))
    
    if tier == "RED" or score >= 66:
        tier_color = "#da3633"
        tier_title = "CRITICAL ESCALATION (RED)"
        posture = "DEFENSE LEVEL 1 // IMMEDIATE DIPLOMATIC & SATELLITE SURVEILLANCE PRIORITY"
        rec_summary = (
            "Initiate immediate bilateral de-escalation hotlines, task high-resolution satellite reconnaissance "
            "(Copernicus / Sentinel-2) over forward logistics corridors, and deploy multilateral crisis mediation mechanisms."
        )
    elif tier == "AMBER" or score >= 33:
        tier_color = "#d29922"
        tier_title = "ELEVATED TENSION (AMBER)"
        posture = "DEFENSE LEVEL 2 // HEIGHTENED REGIONAL VIGILANCE"
        rec_summary = (
            "Heighten SIGINT and open-source narrative monitoring, verify border logistics activity, "
            "and engage regional security partners to preempt kinetic escalation triggers."
        )
    else:
        tier_color = "#2ea043"
        tier_title = "STABLE / MONITORED (GREEN)"
        posture = "DEFENSE LEVEL 3 // ROUTINE HORIZON MONITORING"
        rec_summary = (
            "Maintain standard automated multi-source data ingestion and regular macroeconomic baseline monitoring."
        )

    conf_score = confidence_data.get("confidence_score", 85.0) if confidence_data else 85.0
    conf_tier = confidence_data.get("confidence_tier", "HIGH") if confidence_data else "HIGH"

    # SHAP Waterfall rows
    waterfall_rows_html = ""
    waterfall_rows_md = ""
    if waterfall_data and "contributions" in waterfall_data:
        for item in waterfall_data["contributions"]:
            delta = item["delta"]
            sign = "+" if delta > 0 else ""
            color = "#da3633" if delta > 0 else "#2ea043"
            waterfall_rows_html += f"""
            <tr>
                <td style="padding:8px 12px; border-bottom:1px solid #30363d; font-weight:600;">{item['feature']}</td>
                <td style="padding:8px 12px; border-bottom:1px solid #30363d; text-align:right;">{item['actual_value']}</td>
                <td style="padding:8px 12px; border-bottom:1px solid #30363d; text-align:right; color:{color}; font-weight:700;">{sign}{delta} pts</td>
            </tr>
            """
            waterfall_rows_md += f"| {item['feature']} | {item['actual_value']} | {sign}{delta} pts |\n"
    else:
        waterfall_rows_html = """<tr><td colspan="3" style="padding:10px; text-align:center; color:#8b949e;">No attribution data</td></tr>"""
        waterfall_rows_md = "| Baseline Feature Attributions | Default | +0.0 pts |\n"

    # Narrative divergence info
    div_status = "DETECTED (State Media Deviation)" if (divergence_data and divergence_data.get("divergence_detected")) else "NOMINAL (Aligned Narrative)"
    div_color = "#da3633" if (divergence_data and divergence_data.get("divergence_detected")) else "#2ea043"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{report_id} — ARES Intelligence Dossier</title>
    <style>
        body {{
            background-color: #0d1117;
            color: #e6edf3;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 40px;
            line-height: 1.5;
        }}
        .header {{
            border-bottom: 2px solid #30363d;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .title {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 1px;
            color: #58a6ff;
            margin: 0;
        }}
        .subtitle {{
            font-size: 13px;
            color: #8b949e;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge {{
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .card {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        .card-title {{
            font-size: 15px;
            font-weight: 700;
            color: #58a6ff;
            margin-top: 0;
            margin-bottom: 14px;
            border-bottom: 1px solid #21262d;
            padding-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #8b949e;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 20px;
            font-weight: 700;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            background-color: #21262d;
            color: #8b949e;
            text-align: left;
            padding: 10px 12px;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .footer {{
            border-top: 1px solid #30363d;
            padding-top: 20px;
            margin-top: 40px;
            font-size: 11px;
            color: #8b949e;
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{ background-color: #ffffff; color: #000000; padding: 20px; }}
            .card {{ border: 1px solid #cccccc; background-color: #f9f9f9; }}
            th {{ background-color: #eaeaea; color: #333333; }}
            .title {{ color: #003366; }}
            .badge {{ border: 1px solid #333333; }}
        }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <div class="title">🛡️ ARES STRATEGIC RISK ASSESSMENT DOSSIER</div>
            <div class="subtitle">Autonomous Reconnaissance & Escalation System // Multi-INT Early Warning</div>
            <div style="font-size:12px; color:#c9d1d9; margin-top:8px;">
                <b>Target Entity:</b> {country} &nbsp;|&nbsp; 
                <b>Assessment Window:</b> {window_days}-Day Rolling Horizon &nbsp;|&nbsp; 
                <b>Generated:</b> {now_str}
            </div>
        </div>
        <div style="text-align:right;">
            <div class="badge" style="background-color:{tier_color}; color:#ffffff;">{tier_title}</div>
            <div style="font-size:11px; color:#8b949e; margin-top:6px;">DOSSIER ID: {report_id}</div>
        </div>
    </div>

    <!-- 1. EXECUTIVE POSTURE SUMMARY -->
    <div class="card">
        <div class="card-title">1. Executive Posture & Threat Level</div>
        <div class="grid">
            <div>
                <div class="metric-label">Composite ML Risk Score</div>
                <div class="metric-value" style="color:{tier_color};">{score:.1f} / 100</div>
            </div>
            <div>
                <div class="metric-label">Primary Escalation Driver</div>
                <div class="metric-value" style="font-size:16px;">{top_factor}</div>
            </div>
            <div>
                <div class="metric-label">Epistemic Data Confidence</div>
                <div class="metric-value" style="color:#58a6ff;">{conf_score:.1f}% ({conf_tier})</div>
            </div>
            <div>
                <div class="metric-label">Narrative Divergence</div>
                <div class="metric-value" style="font-size:15px; color:{div_color};">{div_status}</div>
            </div>
        </div>
        <div style="margin-top:16px; padding:12px; background-color:#21262d; border-radius:4px; font-size:13px;">
            <b>Operational Posture:</b> <span style="color:#58a6ff;">{posture}</span>
        </div>
    </div>

    <!-- 2. SHAP FACTOR ATTRIBUTION -->
    <div class="card">
        <div class="card-title">2. Explainable Factor Attribution (SHAP-Style Waterfall)</div>
        <div style="font-size:12px; color:#8b949e; margin-bottom:12px;">
            Exact point contributions evaluated against the Indo-Pacific regional baseline (22.0 pts):
        </div>
        <table>
            <thead>
                <tr>
                    <th>Observed Leading Indicator</th>
                    <th style="text-align:right;">Observed Value</th>
                    <th style="text-align:right;">Risk Attribution Impact</th>
                </tr>
            </thead>
            <tbody>
                {waterfall_rows_html}
            </tbody>
        </table>
    </div>

    <!-- 3. STRATEGIC POLICY RECOMMENDATIONS -->
    <div class="card">
        <div class="card-title">3. Recommended De-escalation & Surveillance Protocols</div>
        <div style="font-size:13px; line-height:1.6;">
            {rec_summary}
        </div>
        <ul style="font-size:12px; color:#c9d1d9; margin-top:12px; padding-left:20px;">
            <li><b>Diplomatic Channel:</b> Audit bilateral high-level engagements and reverse diplomatic silence spikes.</li>
            <li><b>Information Operations:</b> Filter and counter coordinated narrative divergence originating from state-controlled proxies.</li>
            <li><b>Geospatial Surveillance:</b> Correlate optical satellite changes with commercial AIS dark-fleet positions across chokepoints.</li>
        </ul>
    </div>

    <div class="footer">
        <div>CLASSIFICATION: UNCLASSIFIED // DECISION-SUPPORT DECISION ONLY</div>
        <div>DEPARTMENT OF INFORMATION SCIENCE & ENGINEERING // BMSIT&M</div>
    </div>

</body>
</html>
"""

    md_content = f"""# 🛡️ ARES STRATEGIC RISK ASSESSMENT DOSSIER
**Document ID:** `{report_id}`  
**Target Entity:** {country} | **Horizon:** {window_days} Days | **Generated:** {now_str}  
**Classification:** UNCLASSIFIED // DEFENSE DECISION-SUPPORT  

---

### 1. Executive Threat Posture
- **ML Escalation Score:** **{score:.1f} / 100** (`{tier_title}`)
- **Primary Escalation Driver:** {top_factor}
- **Epistemic Data Confidence:** {conf_score:.1f}% ({conf_tier})
- **State Media Narrative Divergence:** {div_status}
- **Operational Posture:** `{posture}`

---

### 2. Explainable Factor Attribution (SHAP Waterfall)
| Observed Leading Indicator | Observed Value | Risk Attribution Impact |
| :--- | :---: | :---: |
{waterfall_rows_md}

---

### 3. Recommended De-escalation & Surveillance Protocols
{rec_summary}

- **Diplomatic Channel:** Audit bilateral high-level engagements and reverse diplomatic silence spikes.
- **Information Operations:** Filter and counter coordinated narrative divergence originating from state-controlled proxies.
- **Geospatial Surveillance:** Correlate optical satellite changes with commercial AIS dark-fleet positions across chokepoints.

---
*Generated by ARES Early-Warning System (BMSIT&M ISE)*
"""

    return {
        "html": html_content,
        "markdown": md_content,
        "report_id": report_id
    }

