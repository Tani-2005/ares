"""
ARES — Advanced Reconnaissance & Escalation System
Dashboard for Data Collection, Preprocessing & Feature Engineering
Version 1.0 | UNCLASSIFIED // ACADEMIC USE ONLY
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import time
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("ares")

st.set_page_config(
    page_title="ARES — Escalation Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "bg": "#0d1117",
    "card": "#161b22",
    "border": "#21262d",
    "green": "#2ea043",
    "amber": "#d29922",
    "red": "#da3633",
    "blue": "#388bfd",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "accent": "#1f6feb",
}

st.markdown(f"""
<style>
    .stApp {{ background-color: {COLORS['bg']}; color: {COLORS['text']}; }}
    .main .block-container {{ padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: {COLORS['card']}; border-right: 1px solid {COLORS['border']}; }}
    [data-testid="stSidebar"] * {{ color: {COLORS['text']} !important; }}

    /* Cards */
    .ares-card {{
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }}
    .ares-card-title {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {COLORS['muted']};
        margin-bottom: 0.4rem;
    }}
    .ares-metric {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {COLORS['text']};
        line-height: 1;
    }}
    .ares-metric-sub {{
        font-size: 0.8rem;
        color: {COLORS['muted']};
        margin-top: 0.25rem;
    }}

    /* Risk badges */
    .badge-red {{ background:#3d1414; color:#f85149; border:1px solid #f85149; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}
    .badge-amber {{ background:#2d2010; color:#e3b341; border:1px solid #d29922; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}
    .badge-green {{ background:#0d2318; color:#3fb950; border:1px solid #2ea043; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}
    .badge-blue {{ background:#0d1e38; color:#79c0ff; border:1px solid #388bfd; border-radius:4px; padding:2px 8px; font-size:0.75rem; font-weight:600; }}

    /* Section headers */
    .section-header {{
        display: flex; align-items: center; gap: 8px;
        font-size: 1rem; font-weight: 700; color: {COLORS['text']};
        border-bottom: 1px solid {COLORS['border']};
        padding-bottom: 0.5rem; margin-bottom: 1rem;
    }}
    .section-badge {{
        font-size: 0.7rem; background: {COLORS['accent']};
        color: white; border-radius: 3px; padding: 1px 6px; font-weight: 600;
    }}

    /* Pipeline step */
    .pipeline-step {{
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-left: 3px solid {COLORS['accent']};
        border-radius: 0 6px 6px 0;
        padding: 0.6rem 1rem;
        margin-bottom: 0.4rem;
        display: flex; justify-content: space-between; align-items: center;
    }}
    .step-ok {{ border-left-color: {COLORS['green']} !important; }}
    .step-warn {{ border-left-color: {COLORS['amber']} !important; }}
    .step-err {{ border-left-color: {COLORS['red']} !important; }}

    /* Tables */
    .dataframe {{ background: {COLORS['card']} !important; color: {COLORS['text']} !important; }}

    /* Top header */
    .ares-header {{
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 1.2rem;
    }}
    .ares-title {{ font-size: 1.6rem; font-weight: 800; color: {COLORS['text']}; }}
    .ares-subtitle {{ font-size: 0.8rem; color: {COLORS['muted']}; margin-top: 2px; }}
    .ares-classification {{
        font-family: monospace; font-size: 0.7rem; font-weight: 600;
        color: #e3b341; letter-spacing: 0.1em;
    }}

    /* Plotly charts dark */
    .js-plotly-plot .plotly {{ background: transparent !important; }}

    /* Streamlit element overrides */
    .stSelectbox > div > div {{ background: {COLORS['card']}; border-color: {COLORS['border']}; color: {COLORS['text']}; }}
    .stButton > button {{ background: {COLORS['accent']}; color: white; border: none; border-radius: 6px; font-weight: 600; }}
    .stButton > button:hover {{ background: #1a56c4; }}
    div[data-testid="stExpander"] {{ background: {COLORS['card']}; border: 1px solid {COLORS['border']}; border-radius: 8px; }}

    hr {{ border-color: {COLORS['border']}; }}
</style>
""", unsafe_allow_html=True)

CHART_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e6edf3", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
)


def get_pipeline():
    """Import pipeline module from src/."""
    try:
        from pipeline import ARESPipeline
        return ARESPipeline
    except ImportError as e:
        st.error(f"Import error: {e}")
        return None


def risk_badge(level: str) -> str:
    badges = {"RED": "badge-red", "AMBER": "badge-amber", "GREEN": "badge-green"}
    cls = badges.get(level, "badge-blue")
    return f'<span class="{cls}">{level}</span>'


def render_header():
    now = datetime.now()
    st.markdown(f"""
    <div class="ares-header">
        <div>
            <div class="ares-title">🛡️ ARES</div>
            <div class="ares-subtitle">Advanced Reconnaissance & Escalation System &nbsp;|&nbsp; Indo-Pacific Theater</div>
            <div class="ares-classification">⚑ UNCLASSIFIED // ACADEMIC USE ONLY</div>
        </div>
        <div style="text-align:right">
            <div style="color:#8b949e; font-size:0.8rem">Pipeline Status</div>
            <div style="font-size:1rem; font-weight:700; color:#e6edf3;">{now.strftime("%Y-%m-%d %H:%M")} UTC</div>
            <div style="font-size:0.75rem; color:#8b949e;">Phases 0–2 Active</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ ARES Control Panel")
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["🏠 Overview", "📡 Data Sources", "🔬 Preprocessing", "⚡ Feature Engineering", "🌍 Country Analysis"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown("**Data Filters**")
        zone_filter = st.selectbox("Zone", ["All", "Zone A (Conflict)", "Zone B (Influence)"])
        window_filter = st.selectbox("Feature Window", [7, 14, 30], index=1)
        st.markdown("---")
        st.markdown("**Pipeline Control**")
        run_pipeline = st.button("▶ Run Full Pipeline", use_container_width=True)
        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.7rem; color:#8b949e; line-height:1.7;">
        <span style="color:#3fb950; font-weight:700">● LIVE</span><br>
        GDELT News • GDELT GKG Themes<br>
        UCDP GED Events • ReliefWeb Reports<br>
        World Bank API • IMF Datamapper<br><br>
        <span style="color:#388bfd; font-weight:700">● STATIC</span><br>
        ACLED • ICEWS (Harvard) • SIPRI<br>
        UN Sanctions • UN Voting • GSDB<br>
        World Bank Historical • IMF WEO<br>
        Exchange Rates<br><br>
        <span style="color:#79c0ff; font-weight:700">⚡ FEATURES</span><br>
        Event Counts • Acceleration<br>
        Sentiment Volatility • Diplo. Silence<br>
        Economic Stress • Composite Risk
        </div>
        """, unsafe_allow_html=True)
    return page, zone_filter, window_filter, run_pipeline


def run_pipeline_with_progress(config: dict) -> dict:
    ARESPipeline = get_pipeline()
    if not ARESPipeline:
        return {"success": False, "error": "Pipeline module not found"}

    progress_bar = st.progress(0.0)
    status_text = st.empty()
    log_container = st.container()
    log_lines = []

    def update_progress(step: str, pct: float, detail: str = ""):
        progress_bar.progress(min(pct, 1.0))
        status_text.markdown(f"**{step}** — {detail}")
        log_lines.append(f"`{datetime.now().strftime('%H:%M:%S')}` **{step}**: {detail}")

    pipeline = ARESPipeline(config=config, progress_callback=update_progress)

    with st.spinner("Running ARES pipeline..."):
        result = pipeline.run_full_pipeline()

    progress_bar.progress(1.0)
    if result.get("success"):
        status_text.markdown("✅ **Pipeline completed successfully**")
    else:
        status_text.markdown(f"❌ **Pipeline failed**: {result.get('error', 'Unknown error')}")

    with log_container.expander("📋 Pipeline Log", expanded=False):
        for line in log_lines:
            st.markdown(line)

    if hasattr(pipeline.preprocessor, "processing_log"):
        st.session_state["processing_log"] = pipeline.preprocessor.get_processing_report()
    if hasattr(pipeline.feature_engineer, "feature_log"):
        st.session_state["feature_log"] = pipeline.feature_engineer.get_feature_log()

    return result


def load_db_data():
    try:
        from database import query_df, get_table_stats, initialize_schema
        initialize_schema()
        stats = get_table_stats()
        return stats, query_df
    except Exception as e:
        st.warning(f"Database not ready: {e}")
        return {}, None


def render_overview(stats: dict, query_df, config: dict, result: dict = None):
    st.markdown('<div class="section-header"><span>📊 Mission Status</span><span class="section-badge">LIVE</span></div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    cards = [
        ("Event Records", stats.get("raw_events", 0), "raw_events", "blue"),
        ("Economic Indicators", stats.get("economic_indicators", 0), "economic_indicators", "blue"),
        ("Diplomatic Records", stats.get("diplomatic_records", 0), "diplomatic_records", "blue"),
        ("Engineered Features", stats.get("engineered_features", 0), "engineered_features", "blue"),
        ("Pipeline Runs", stats.get("ingestion_log", 0), "ingestion_log", "blue"),
    ]
    for col, (title, val, _, color) in zip([col1, col2, col3, col4, col5], cards):
        with col:
            st.markdown(f"""
            <div class="ares-card">
                <div class="ares-card-title">{title}</div>
                <div class="ares-metric">{val:,}</div>
            </div>
            """, unsafe_allow_html=True)

    render_risk_explanation()

    if result and result.get("success") and not result.get("feature_df", pd.DataFrame()).empty:
        feats = result["feature_df"]
        if "risk_level" in feats.columns:
            st.markdown('<div class="section-header" style="margin-top:1.5rem"><span>🚦 Current Risk Distribution</span></div>', unsafe_allow_html=True)
            risk_counts = feats[feats["window_days"] == 14].groupby("risk_level").size().reset_index(name="count")
            col1, col2, col3 = st.columns(3)
            for col, level, badge_cls in [
                (col1, "RED", "badge-red"), (col2, "AMBER", "badge-amber"), (col3, "GREEN", "badge-green")
            ]:
                n = risk_counts[risk_counts["risk_level"] == level]["count"].sum() if level in risk_counts["risk_level"].values else 0
                with col:
                    st.markdown(f"""
                    <div class="ares-card">
                        <div class="ares-card-title">Countries at {level} Risk</div>
                        <div class="ares-metric">{n}</div>
                        <div style="margin-top:0.4rem"><span class="{badge_cls}">{level}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:1rem"><span>🗺️ Risk Map — Zone A Countries (14-day window)</span></div>', unsafe_allow_html=True)
        w14 = feats[(feats["window_days"] == 14) & (feats["zone"] == "A")].sort_values("composite_risk_score", ascending=False)
        if not w14.empty:
            color_map = {"RED": "#da3633", "AMBER": "#d29922", "GREEN": "#2ea043"}
            fig = px.bar(
                w14, x="composite_risk_score", y="country", orientation="h",
                color="risk_level", color_discrete_map=color_map,
                labels={"composite_risk_score": "Composite Risk Score (0–100)", "country": "Country", "risk_level": "Risk Level"},
                title="Zone A Country Risk Scores (14-day window)",
            )
            fig.update_layout(**CHART_THEME, height=420, showlegend=True)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    elif query_df:
        events = query_df("SELECT * FROM raw_events LIMIT 5000")
        if not events.empty:
            events["event_date"] = pd.to_datetime(events["event_date"])
            daily = events.groupby("event_date").size().reset_index(name="count")
            daily = daily.sort_values("event_date").tail(90)
            if not daily.empty:
                fig = px.area(daily, x="event_date", y="count",
                              title="Event Volume — Last 90 Days (all sources)",
                              labels={"event_date": "Date", "count": "Events"},
                              color_discrete_sequence=["#388bfd"])
                fig.update_layout(**CHART_THEME, height=300)
                st.plotly_chart(fig, use_container_width=True)

    if result and result.get("success"):
        stages = result.get("stages", {})
        st.markdown('<div class="section-header" style="margin-top:1rem"><span>✅ Pipeline Stage Results</span></div>', unsafe_allow_html=True)
        for source, val in stages.items():
            if isinstance(val, int):
                label = source.replace("_", " ").upper()
                st.markdown(f"""
                <div class="pipeline-step step-ok">
                    <span>📥 {label}</span>
                    <span class="badge-green">{val:,} records</span>
                </div>
                """, unsafe_allow_html=True)


def render_data_sources(query_df, result: dict = None):
    st.markdown('<div class="section-header"><span>📡 Data Sources & Ingestion Status</span></div>', unsafe_allow_html=True)

    source_info = {
        # ── Live Sources ─────────────────────────────────
        "GDELT (Live)": ("Global Database of Events — News Feed", "Live (last 7 days)", "News & Tone", "All Zones"),
        "GDELT GKG (Live)": ("GDELT Global Knowledge Graph — Theme Volume", "Live (last 7 days)", "Conflict Themes", "Zone A"),
        "UCDP GED (Live)": ("Uppsala Conflict Data Program — Verified Events", "Live (2020–present)", "Verified Conflict", "Zone A"),
        "ReliefWeb (Live)": ("UN Humanitarian Situation Reports", "Live (last 60 days)", "Crisis Reports", "Zone A"),
        "World Bank API (Live)": ("World Bank Open Data API — 6 indicators", "Live (annual)", "GDP, Military Exp., Debt", "All Zones"),
        "IMF API (Live)": ("IMF Datamapper — WEO projections", "Live (annual)", "Macro Projections", "All Zones"),
        # ── Static Sources ───────────────────────────────
        "ACLED": ("Armed Conflict Location & Event Data", "Static (2018–2024)", "Conflict Events", "Zone A"),
        "ICEWS (Harvard)": ("Harvard Integrated Crisis Early Warning", "Static (2015–2024)", "Diplomatic Events", "All Zones"),
        "SIPRI": ("Stockholm Int'l Peace Research Institute", "Static (2010–2024)", "Arms Transfers", "All Zones"),
        "UN Sanctions": ("UN Security Council Sanctions", "Static (2000–2024)", "Diplomatic", "Global"),
        "UN Voting": ("UN General Assembly Voting", "Static (2000–2024)", "Diplomatic", "Global"),
        "GSDB": ("Global Sanctions Database", "Static (1990–2024)", "Sanctions", "Global"),
        "World Bank (Static)": ("World Bank Historical GDP & Inflation", "Static (2010–2024)", "Economic Baseline", "All Zones"),
        "IMF WEO (Static)": ("IMF World Economic Outlook Historical", "Static (2010–2024)", "Macro Indicators", "All Zones"),
        "Exchange Rate": ("Exchange Rate Data", "Static (2015–2024)", "Economic", "Zone A/B"),
    }

    col1, col2 = st.columns(2)
    source_items = list(source_info.items())
    for i, (src, (desc, coverage, dtype, zone)) in enumerate(source_items):
        col = col1 if i % 2 == 0 else col2
        with col:
            is_live = "Live" in coverage
            badge = '<span class="badge-green">LIVE</span>' if is_live else '<span class="badge-blue">STATIC</span>'
            st.markdown(f"""
            <div class="ares-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start">
                    <div>
                        <div style="font-weight:700; font-size:0.9rem; color:#e6edf3">{src}</div>
                        <div style="font-size:0.78rem; color:#8b949e; margin-top:2px">{desc}</div>
                    </div>
                    <div>{badge}</div>
                </div>
                <div style="margin-top:0.6rem; display:flex; gap:8px; flex-wrap:wrap">
                    <span class="badge-blue">{dtype}</span>
                    <span style="font-size:0.75rem; color:#8b949e">📅 {coverage}</span>
                    <span style="font-size:0.75rem; color:#8b949e">🗺️ {zone}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if query_df:
        st.markdown('<div class="section-header" style="margin-top:1rem"><span>📋 Recent Ingested Events</span></div>', unsafe_allow_html=True)
        events = query_df("""
            SELECT source, event_date, country, zone, event_type, sub_type, severity, description
            FROM raw_events ORDER BY event_date DESC LIMIT 200
        """)
        if not events.empty:
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                src_sel = st.multiselect("Filter by Source", options=events["source"].unique().tolist(), default=[])
            with col_filter2:
                country_sel = st.multiselect("Filter by Country", options=sorted(events["country"].unique().tolist()), default=[])

            filtered = events.copy()
            if src_sel:
                filtered = filtered[filtered["source"].isin(src_sel)]
            if country_sel:
                filtered = filtered[filtered["country"].isin(country_sel)]

            display_df = filtered[["source", "event_date", "country", "zone", "event_type", "description"]].copy()
            display_df.columns = ["Source", "Date", "Country", "Zone", "Type", "Description"]
            display_df["Description"] = display_df["Description"].str[:80] + "..."

            st.dataframe(
                display_df,
                use_container_width=True,
                height=350,
                hide_index=True,
            )

            col_a, col_b = st.columns(2)
            with col_a:
                src_counts = events["source"].value_counts().reset_index()
                src_counts.columns = ["Source", "Records"]
                fig = px.pie(src_counts, values="Records", names="Source",
                             title="Records by Data Source",
                             color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(**CHART_THEME, height=320)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                zone_counts = events.groupby(["source", "zone"]).size().reset_index(name="count")
                fig = px.bar(zone_counts, x="source", y="count", color="zone",
                             title="Records by Source & Zone",
                             barmode="stack",
                             color_discrete_map={"A": "#388bfd", "B": "#d29922"})
                fig.update_layout(**CHART_THEME, height=320)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No event data in database yet. Run the pipeline first.")


def render_preprocessing(query_df, result: dict = None):
    st.markdown('<div class="section-header"><span>🔬 Data Preprocessing</span><span class="section-badge">PANDAS + NUMPY</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ares-card">
        <div class="ares-card-title">Preprocessing Pipeline Steps</div>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.5rem; margin-top:0.5rem">
            <div style="background:#0d2318; border:1px solid #2ea043; border-radius:6px; padding:0.5rem 0.75rem">
                <div style="color:#3fb950; font-size:0.75rem; font-weight:700">1. Date Normalization</div>
                <div style="color:#8b949e; font-size:0.7rem">Parse multi-format dates, drop unparseable rows</div>
            </div>
            <div style="background:#0d2318; border:1px solid #2ea043; border-radius:6px; padding:0.5rem 0.75rem">
                <div style="color:#3fb950; font-size:0.75rem; font-weight:700">2. Country Standardization</div>
                <div style="color:#8b949e; font-size:0.7rem">Unify country name variants (US→United States, etc.)</div>
            </div>
            <div style="background:#0d2318; border:1px solid #2ea043; border-radius:6px; padding:0.5rem 0.75rem">
                <div style="color:#3fb950; font-size:0.75rem; font-weight:700">3. Zone Filtering</div>
                <div style="color:#8b949e; font-size:0.7rem">Assign Zone A / Zone B per PRD architecture</div>
            </div>
            <div style="background:#0d2318; border:1px solid #2ea043; border-radius:6px; padding:0.5rem 0.75rem">
                <div style="color:#3fb950; font-size:0.75rem; font-weight:700">4. Missing Value Imputation</div>
                <div style="color:#8b949e; font-size:0.7rem">Median fill for numeric, 'Unknown' for categorical</div>
            </div>
            <div style="background:#0d2318; border:1px solid #2ea043; border-radius:6px; padding:0.5rem 0.75rem">
                <div style="color:#3fb950; font-size:0.75rem; font-weight:700">5. Outlier Clipping (IQR)</div>
                <div style="color:#8b949e; font-size:0.7rem">Clip Goldstein scale & tone beyond 3×IQR</div>
            </div>
            <div style="background:#0d2318; border:1px solid #2ea043; border-radius:6px; padding:0.5rem 0.75rem">
                <div style="color:#3fb950; font-size:0.75rem; font-weight:700">6. Severity Normalization</div>
                <div style="color:#8b949e; font-size:0.7rem">Min-max scale severity [0, 1] across all sources</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if query_df:
        events = query_df("SELECT * FROM raw_events LIMIT 5000")
        if not events.empty:
            from preprocessing import DataPreprocessor
            proc = DataPreprocessor()
            clean_events, missing_report = proc.preprocess_events(events)
            quality = proc.compute_data_quality_score(events)

            st.markdown('<div class="section-header" style="margin-top:1rem"><span>📊 Data Quality Metrics</span></div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Completeness</div>
                    <div class="ares-metric">{quality['completeness']}%</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Total Records</div>
                    <div class="ares-metric">{quality['total_records']:,}</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Missing Cells</div>
                    <div class="ares-metric">{quality['missing_cells']:,}</div>
                </div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Duplicates Found</div>
                    <div class="ares-metric">{quality['duplicate_rows']:,}</div>
                </div>""", unsafe_allow_html=True)

            proc_log = proc.get_processing_report()
            if not proc_log.empty:
                st.markdown('<div class="section-header" style="margin-top:1rem"><span>🗒️ Processing Log</span></div>', unsafe_allow_html=True)
                for _, row in proc_log.iterrows():
                    ri, ro = int(row.get("records_in", 0)), int(row.get("records_out", 0))
                    dropped = ri - ro
                    st.markdown(f"""
                    <div class="pipeline-step step-ok">
                        <span>🔧 <b>{row['step']}</b> — {row['detail']}</span>
                        <span style="color:#8b949e; font-size:0.8rem">
                            {ri:,} → {ro:,} {"↓ " + str(dropped) if dropped > 0 else ""}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            if missing_report:
                st.markdown('<div class="section-header" style="margin-top:1rem"><span>🔍 Missing Value Analysis</span></div>', unsafe_allow_html=True)
                miss_df = pd.DataFrame([
                    {"Column": col, "Missing": v["missing"], "% Missing": v["pct"]}
                    for col, v in missing_report.items()
                ]).sort_values("Missing", ascending=False)
                if not miss_df.empty:
                    fig = px.bar(miss_df, x="Column", y="% Missing",
                                 title="Missing Values by Column",
                                 color="% Missing",
                                 color_continuous_scale=["#2ea043", "#d29922", "#da3633"])
                    fig.update_layout(**CHART_THEME, height=300)
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header" style="margin-top:1rem"><span>📈 Country Coverage After Preprocessing</span></div>', unsafe_allow_html=True)
            country_counts = clean_events.groupby(["country", "zone"]).size().reset_index(name="Event Count")
            country_counts = country_counts.sort_values("Event Count", ascending=False).head(20)
            fig = px.bar(country_counts, x="country", y="Event Count", color="zone",
                         title="Event Coverage by Country (after preprocessing)",
                         color_discrete_map={"A": "#388bfd", "B": "#d29922"},
                         labels={"zone": "Zone", "country": "Country"})
            fig.update_layout(**CHART_THEME, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run the pipeline first to see preprocessing results.")


def render_feature_engineering(query_df, result: dict = None, window: int = 14):
    st.markdown('<div class="section-header"><span>⚡ Feature Engineering</span><span class="section-badge">SCIKIT-LEARN + PANDAS</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ares-card">
        <div class="ares-card-title">Engineered Features — Leading Indicators</div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:0.5rem; margin-top:0.5rem">
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Event Count</div>
                <div style="color:#8b949e; font-size:0.7rem">Total events per country per window</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Military Events</div>
                <div style="color:#8b949e; font-size:0.7rem">Battles, airstrikes, naval incidents</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Event Acceleration</div>
                <div style="color:#8b949e; font-size:0.7rem">Δ events vs prior window (escalation)</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Sentiment Volatility</div>
                <div style="color:#8b949e; font-size:0.7rem">StdDev of GDELT tone scores</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Diplomatic Silence</div>
                <div style="color:#8b949e; font-size:0.7rem">Days since last diplomatic event</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Protest/Violence Ratio</div>
                <div style="color:#8b949e; font-size:0.7rem">Civil unrest vs kinetic events</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Economic Stress</div>
                <div style="color:#8b949e; font-size:0.7rem">GDP + inflation + unemployment signal</div>
            </div>
            <div style="background:#0d1e38; border:1px solid #388bfd; border-radius:6px; padding:0.5rem">
                <div style="color:#79c0ff; font-size:0.75rem; font-weight:700">Composite Risk (0–100)</div>
                <div style="color:#8b949e; font-size:0.7rem">Weighted signal fusion → GREEN/AMBER/RED</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    feats = pd.DataFrame()
    if result and result.get("feature_df") is not None and not result["feature_df"].empty:
        feats = result["feature_df"]
    elif query_df:
        feats = query_df("SELECT * FROM engineered_features")

    if feats.empty:
        st.info("Run the pipeline to generate engineered features.")
        return

    w_df = feats[feats["window_days"] == window].copy()
    if w_df.empty:
        w_df = feats.copy()

    st.markdown(f'<div class="section-header" style="margin-top:1rem"><span>📋 Feature Matrix — {window}-Day Window</span></div>', unsafe_allow_html=True)

    display_cols = [
        "country", "zone", "risk_level", "composite_risk_score",
        "event_count", "military_event_count", "event_acceleration",
        "sentiment_volatility", "diplomatic_silence_days", "economic_stress_score"
    ]
    available = [c for c in display_cols if c in w_df.columns]
    disp = w_df[available].copy()

    if "composite_risk_score" in disp.columns:
        disp = disp.sort_values("composite_risk_score", ascending=False)

    rename_map = {
        "country": "Country", "zone": "Zone", "risk_level": "Risk",
        "composite_risk_score": "Risk Score", "event_count": "Events",
        "military_event_count": "Military", "event_acceleration": "Acceleration",
        "sentiment_volatility": "Sentiment Vol.", "diplomatic_silence_days": "Diplo. Silence (days)",
        "economic_stress_score": "Econ. Stress"
    }
    disp = disp.rename(columns=rename_map)

    numeric_cols = ["Risk Score", "Acceleration", "Sentiment Vol.", "Econ. Stress"]
    for col in numeric_cols:
        if col in disp.columns:
            disp[col] = disp[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")

    st.dataframe(disp, use_container_width=True, height=400, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        feature_cols = [
            "event_count", "military_event_count", "event_acceleration",
            "sentiment_volatility", "diplomatic_silence_days", "economic_stress_score"
        ]
        available_feat = [c for c in feature_cols if c in w_df.columns]
        if "composite_risk_score" in w_df.columns and available_feat:
            from feature_engineering import FeatureEngineer
            fe = FeatureEngineer()
            imp_df = fe.get_feature_importance_proxy(w_df)
            if not imp_df.empty:
                imp_df["feature"] = imp_df["feature"].str.replace("_", " ").str.title()
                fig = px.bar(imp_df, x="importance", y="feature", orientation="h",
                             title="Feature Importance (Correlation with Risk Score)",
                             color="importance",
                             color_continuous_scale=["#388bfd", "#da3633"])
                fig.update_layout(**CHART_THEME, height=340)
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "composite_risk_score" in w_df.columns and "country" in w_df.columns:
            zone_a = w_df[w_df["zone"] == "A"].sort_values("composite_risk_score", ascending=False).head(10)
            color_map = {"RED": "#da3633", "AMBER": "#d29922", "GREEN": "#2ea043"}
            fig = px.bar(zone_a, x="composite_risk_score", y="country",
                         orientation="h", color="risk_level", color_discrete_map=color_map,
                         title="Top 10 Zone A Countries by Risk Score",
                         labels={"composite_risk_score": "Risk Score", "country": "Country", "risk_level": "Risk Level"})
            fig.update_layout(**CHART_THEME, height=340)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header" style="margin-top:1rem"><span>📊 Rolling Window Comparison</span></div>', unsafe_allow_html=True)
    window_compare = feats.groupby(["window_days", "risk_level"]).size().reset_index(name="count")
    fig = px.bar(window_compare, x="window_days", y="count", color="risk_level",
                 barmode="group",
                 color_discrete_map={"RED": "#da3633", "AMBER": "#d29922", "GREEN": "#2ea043"},
                 title="Risk Level Distribution Across Rolling Windows (7 / 14 / 30 days)",
                 labels={"window_days": "Window (days)", "count": "Country Count", "risk_level": "Risk Level"})
    fig.update_layout(**CHART_THEME, height=320)
    st.plotly_chart(fig, use_container_width=True)

    if "is_anomaly" in w_df.columns and w_df["is_anomaly"].any():
        anomalies = w_df[w_df["is_anomaly"] == True]
        st.markdown('<div class="section-header" style="margin-top:0.5rem"><span>⚠️ Anomaly Detection Flags (IsolationForest)</span></div>', unsafe_allow_html=True)
        st.warning(f"**{len(anomalies)} anomalous country-window combinations detected** using IsolationForest (contamination=10%)")
        anom_display = anomalies[["country", "zone", "risk_level", "composite_risk_score", "event_count", "military_event_count"]].copy()
        st.dataframe(anom_display, use_container_width=True, hide_index=True)


def render_country_analysis(query_df, result: dict = None):
    st.markdown('<div class="section-header"><span>🌍 Country Deep-Dive Analysis</span></div>', unsafe_allow_html=True)

    ZONE_A_COUNTRIES = [
        "India", "Pakistan", "China", "Bangladesh", "Sri Lanka", "Nepal",
        "Myanmar", "Thailand", "Vietnam", "Philippines", "Indonesia",
        "Malaysia", "Singapore", "South Korea", "Japan", "Taiwan"
    ]

    selected_country = st.selectbox("Select Country", options=ZONE_A_COUNTRIES, index=0)

    events = pd.DataFrame()
    feats = pd.DataFrame()
    if query_df:
        events = query_df(f"""
            SELECT * FROM raw_events WHERE country = '{selected_country}'
            ORDER BY event_date DESC
        """)
        feats = query_df(f"""
            SELECT * FROM engineered_features WHERE country = '{selected_country}'
            ORDER BY window_days
        """)

    if events.empty and (result is None or result.get("feature_df", pd.DataFrame()).empty):
        st.info("Run the pipeline first to generate country-level data.")
        return

    if result and not result.get("feature_df", pd.DataFrame()).empty:
        all_feats = result["feature_df"]
        c_feats = all_feats[all_feats["country"] == selected_country]
    else:
        c_feats = feats

    if not c_feats.empty:
        best_row = c_feats.sort_values("window_days").iloc[0] if len(c_feats) > 0 else None
        if best_row is not None:
            risk_l = str(best_row.get("risk_level", "GREEN"))
            risk_s = float(best_row.get("composite_risk_score", 50.0))
            col1, col2, col3, col4 = st.columns(4)
            badge_classes = {"RED": "badge-red", "AMBER": "badge-amber", "GREEN": "badge-green"}
            with col1:
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Risk Level</div>
                    <div class="ares-metric"><span class="{badge_classes.get(risk_l, 'badge-blue')}">{risk_l}</span></div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Risk Score (14d)</div>
                    <div class="ares-metric">{risk_s:.1f}</div>
                    <div class="ares-metric-sub">out of 100</div>
                </div>""", unsafe_allow_html=True)
            with col3:
                n_events = int(best_row.get("event_count", 0))
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Events (7d)</div>
                    <div class="ares-metric">{n_events}</div>
                </div>""", unsafe_allow_html=True)
            with col4:
                mil = int(best_row.get("military_event_count", 0))
                st.markdown(f"""<div class="ares-card">
                    <div class="ares-card-title">Military Events</div>
                    <div class="ares-metric">{mil}</div>
                </div>""", unsafe_allow_html=True)

    if not events.empty:
        events["event_date"] = pd.to_datetime(events["event_date"])
        events = events.sort_values("event_date")

        col1, col2 = st.columns(2)
        with col1:
            from feature_engineering import FeatureEngineer
            fe = FeatureEngineer()
            trend = fe.compute_rolling_trends(events, selected_country, days=90)
            if not trend.empty:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                    subplot_titles=["Daily Event Count", "Average GDELT Tone"])
                fig.add_trace(go.Bar(x=trend["date"], y=trend["event_count"],
                                     name="Daily Events", marker_color="#388bfd", opacity=0.6), row=1, col=1)
                fig.add_trace(go.Scatter(x=trend["date"], y=trend["rolling_7d"],
                                         name="7-day MA", line=dict(color="#d29922", width=2)), row=1, col=1)
                fig.add_trace(go.Scatter(x=trend["date"], y=trend["avg_tone"],
                                         name="GDELT Tone", line=dict(color="#2ea043", width=1.5),
                                         fill="tozeroy", fillcolor="rgba(46,160,67,0.15)"), row=2, col=1)
                fig.update_layout(**CHART_THEME, height=400, title_text=f"{selected_country} — 90-day Event Timeline")
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            event_type_counts = events["event_type"].value_counts().head(10).reset_index()
            event_type_counts.columns = ["Event Type", "Count"]
            fig = px.pie(event_type_counts, values="Count", names="Event Type",
                         title=f"{selected_country} — Event Type Distribution",
                         color_discrete_sequence=px.colors.qualitative.Dark24)
            fig.update_layout(**CHART_THEME, height=400)
            st.plotly_chart(fig, use_container_width=True)

        if not c_feats.empty and "composite_risk_score" in c_feats.columns:
            st.markdown('<div class="section-header" style="margin-top:0.5rem"><span>📊 Feature Comparison Across Windows</span></div>', unsafe_allow_html=True)
            feat_compare = c_feats[["window_days", "event_count", "military_event_count",
                                     "event_acceleration", "sentiment_volatility",
                                     "diplomatic_silence_days", "composite_risk_score"]].copy()
            feat_compare = feat_compare.rename(columns={
                "window_days": "Window", "event_count": "Events",
                "military_event_count": "Military", "event_acceleration": "Acceleration",
                "sentiment_volatility": "Sentiment Vol.",
                "diplomatic_silence_days": "Diplo. Silence",
                "composite_risk_score": "Risk Score"
            })
            st.dataframe(feat_compare, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-header" style="margin-top:0.5rem"><span>📋 Recent Events</span></div>', unsafe_allow_html=True)
        recent = events.tail(30)[["event_date", "source", "event_type", "sub_type", "description"]].copy()
        recent = recent.sort_values("event_date", ascending=False)
        recent["description"] = recent["description"].str[:100] + "..."
        st.dataframe(recent, use_container_width=True, height=300, hide_index=True)


def render_risk_explanation():
    """Render a clear explanation of what risk levels mean in ARES context."""
    st.markdown('<div class="section-header" style="margin-top:1.5rem"><span>🚦 Understanding Risk Levels</span><span class="section-badge">METHODOLOGY</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ares-card" style="border-left: 3px solid #388bfd">
        <div style="font-size:0.85rem; color:#8b949e; margin-bottom:1rem; line-height:1.6">
            The ARES <b style="color:#e6edf3">Composite Risk Score</b> (0–100) is a
            weighted fusion of <b style="color:#e6edf3">8 leading indicators</b> derived from
            multi-source geopolitical, conflict, and economic data.
            It is designed to provide a <b style="color:#e6edf3">14–28 day strategic early warning</b>
            before physical escalation occurs — detecting the <em>intent</em> and <em>preparation</em> phases,
            not just the kinetic event itself.
        </div>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1rem">

            <div style="background:#1a0d0d; border:1.5px solid #da3633; border-radius:8px; padding:1rem">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.6rem">
                    <div style="width:14px; height:14px; border-radius:50%; background:#da3633; flex-shrink:0"></div>
                    <div style="font-size:1rem; font-weight:800; color:#f85149">RED — Escalation</div>
                </div>
                <div style="font-size:0.78rem; color:#e6edf3; font-weight:600; margin-bottom:0.4rem">Score: 66–100</div>
                <div style="font-size:0.75rem; color:#8b949e; line-height:1.7">
                    Conflict Phase 2–4 signals detected.<br>
                    <span style="color:#f85149">●</span> Military event frequency above baseline<br>
                    <span style="color:#f85149">●</span> Rapid tone deterioration in media<br>
                    <span style="color:#f85149">●</span> Extended diplomatic silence (&gt;14 days)<br>
                    <span style="color:#f85149">●</span> Anomalous event acceleration<br>
                    <b style="color:#e6edf3">Action:</b> Elevate to senior command. Verify with HUMINT.
                </div>
            </div>

            <div style="background:#1a1500; border:1.5px solid #d29922; border-radius:8px; padding:1rem">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.6rem">
                    <div style="width:14px; height:14px; border-radius:50%; background:#d29922; flex-shrink:0"></div>
                    <div style="font-size:1rem; font-weight:800; color:#e3b341">AMBER — Tension</div>
                </div>
                <div style="font-size:0.78rem; color:#e6edf3; font-weight:600; margin-bottom:0.4rem">Score: 33–65</div>
                <div style="font-size:0.75rem; color:#8b949e; line-height:1.7">
                    Conflict Phase 1 signals present.<br>
                    <span style="color:#e3b341">●</span> Narrative shift in state media detected<br>
                    <span style="color:#e3b341">●</span> GDELT tone declining below baseline<br>
                    <span style="color:#e3b341">●</span> Economic stress indicators elevated<br>
                    <span style="color:#e3b341">●</span> Protest/civil unrest uptick<br>
                    <b style="color:#e6edf3">Action:</b> Increase monitoring cadence. Watch for Phase 2 triggers.
                </div>
            </div>

            <div style="background:#0a1a0d; border:1.5px solid #2ea043; border-radius:8px; padding:1rem">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.6rem">
                    <div style="width:14px; height:14px; border-radius:50%; background:#2ea043; flex-shrink:0"></div>
                    <div style="font-size:1rem; font-weight:800; color:#3fb950">GREEN — Stable</div>
                </div>
                <div style="font-size:0.78rem; color:#e6edf3; font-weight:600; margin-bottom:0.4rem">Score: 0–32</div>
                <div style="font-size:0.75rem; color:#8b949e; line-height:1.7">
                    Conflict Phase 0 — normal baseline.<br>
                    <span style="color:#3fb950">●</span> Event frequency within 1σ of baseline<br>
                    <span style="color:#3fb950">●</span> Active diplomatic channels<br>
                    <span style="color:#3fb950">●</span> Stable economic indicators<br>
                    <span style="color:#3fb950">●</span> Neutral/positive media tone<br>
                    <b style="color:#e6edf3">Action:</b> Routine monitoring. No alert required.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📐 How the Score is Calculated", expanded=False):
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("""
            <div style="font-size:0.82rem; color:#e6edf3; line-height:1.8">
            <b style="color:#79c0ff">Step 1 — Signal Extraction</b><br>
            For each country and rolling window (7/14/30 days), ARES computes raw signals
            from ingested event data across all sources (GDELT, ACLED, UCDP, ICEWS, ReliefWeb).<br><br>
            <b style="color:#79c0ff">Step 2 — Z-score Standardisation</b><br>
            Each feature is z-score normalised across all countries so a country with
            10 military events is judged relative to the regional baseline, not in absolute terms.<br><br>
            <b style="color:#79c0ff">Step 3 — Weighted Fusion</b><br>
            Features are combined using a weighted sum aligned with PRD signal hierarchy,
            then passed through a sigmoid function to produce a 0–100 score.<br><br>
            <b style="color:#79c0ff">Step 4 — Threshold Classification</b><br>
            Score ≥ 66 → RED &nbsp;&nbsp;|&nbsp;&nbsp; Score ≥ 33 → AMBER &nbsp;&nbsp;|&nbsp;&nbsp; Score &lt; 33 → GREEN
            </div>
            """, unsafe_allow_html=True)
        with col2:
            weights_data = {
                "Feature": [
                    "Military Event Count", "Event Acceleration",
                    "Sentiment Volatility", "Avg GDELT Tone (neg.)",
                    "Diplomatic Silence", "Economic Stress"
                ],
                "Weight": [0.30, 0.20, 0.15, 0.15, 0.10, 0.10]
            }
            wdf = pd.DataFrame(weights_data)
            fig = px.bar(wdf, x="Weight", y="Feature", orientation="h",
                         color="Weight",
                         color_continuous_scale=["#388bfd", "#d29922", "#da3633"],
                         title="Signal Weights in Risk Model",
                         labels={"Weight": "Weight", "Feature": ""})
            fig.update_layout(**CHART_THEME, height=290, showlegend=False,
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)


def main():
    render_header()
    page, zone_filter, window_filter, run_pipeline = render_sidebar()

    if "pipeline_result" not in st.session_state:
        st.session_state["pipeline_result"] = None

    try:
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception:
        config = {}

    if run_pipeline:
        with st.container():
            st.markdown("---")
            result = run_pipeline_with_progress(config)
            st.session_state["pipeline_result"] = result
            if result.get("success"):
                st.success(f"Pipeline complete. {result.get('table_stats', {}).get('raw_events', 0):,} events, {result.get('table_stats', {}).get('engineered_features', 0):,} features stored.")
            else:
                st.error(f"Pipeline error: {result.get('error', 'Unknown')}")
            st.markdown("---")

    stats, query_df_fn = load_db_data()
    result = st.session_state.get("pipeline_result")

    page_key = page.split(" ", 1)[1] if " " in page else page

    if page_key == "Overview":
        render_overview(stats, query_df_fn, config, result)
    elif page_key == "Data Sources":
        render_data_sources(query_df_fn, result)
    elif page_key == "Preprocessing":
        render_preprocessing(query_df_fn, result)
    elif page_key == "Feature Engineering":
        render_feature_engineering(query_df_fn, result, window=window_filter)
    elif page_key == "Country Analysis":
        render_country_analysis(query_df_fn, result)


if __name__ == "__main__":
    main()
