"""
ARES Geospatial Visualization Module (PRD §3.1 & SRS FR-12).
Provides:
1. Interactive Global Tactical Theater Map (Plotly Choropleth + Scattergeo Vector Overlay)
   - Country Risk Tiers (Green, Amber, Red)
   - Zone B Influence Superpowers (USA, Russia, EU, UK, Canada)
   - Strategic Tactical Flashpoints & Hotspots
   - Maritime Chokepoints (Malacca, Hormuz, Taiwan Strait, etc.)
   - Geodesic Causal Policy Vectors (Zone B -> Zone A)
2. 3D Extruded PyDeck Tactical Flashpoint Deck
   - Multi-INT Sentinel-2 optical surveillance infrastructure sites
   - South China Sea maritime militia AIS swarm trajectories
"""

import pydeck as pdk
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Any

# ISO-3 Code mapping for Indo-Pacific Zone A nations
ZONE_A_ISO_MAP = {
    "India": "IND", "Pakistan": "PAK", "China": "CHN", "Taiwan": "TWN",
    "Philippines": "PHL", "Vietnam": "VNM", "Indonesia": "IDN", "Malaysia": "MYS",
    "Myanmar": "MMR", "Bangladesh": "BGD", "Sri Lanka": "LKA", "Nepal": "NPL",
    "Thailand": "THA", "Singapore": "SGP", "South Korea": "KOR", "Japan": "JPN",
    "Cambodia": "KHM", "Laos": "LAO", "Bhutan": "BTN", "Maldives": "MDV",
    "Timor-Leste": "TLS", "Papua New Guinea": "PNG", "Fiji": "FJI",
    "Solomon Islands": "SLB", "Vanuatu": "VUT", "Australia": "AUS", "New Zealand": "NZL"
}

# ISO-3 Code mapping for Zone B Superpower Influence actors
ZONE_B_ISO_MAP = {
    "United States": "USA",
    "Russia": "RUS",
    "United Kingdom": "GBR",
    "Canada": "CAN",
    "Germany": "DEU",
    "France": "FRA"
}

ZONE_A_COUNTRIES = list(ZONE_A_ISO_MAP.keys())
ZONE_B_ACTORS = ["United States", "European Union", "United Kingdom", "Russia", "Canada"]


# Capital Coordinates for Geodesic Causal Linkages
ZONE_B_COORDS = {
    "United States": (38.89, -77.03),
    "Russia": (55.75, 37.61),
    "United Kingdom": (51.50, -0.12),
    "European Union": (50.85, 4.35),
    "Canada": (45.42, -75.69)
}

CAPITAL_COORDS = {
    "India": (28.61, 77.20),
    "Pakistan": (33.68, 73.04),
    "China": (39.90, 116.40),
    "Taiwan": (25.03, 121.56),
    "Philippines": (14.59, 120.98),
    "Vietnam": (21.02, 105.83),
    "Indonesia": (-6.20, 106.84),
    "Japan": (35.67, 139.65),
    "South Korea": (37.56, 126.97),
    "Myanmar": (19.76, 96.07),
    "Bangladesh": (23.81, 90.41),
    "Australia": (-35.28, 149.13)
}

# Causal Geodesic Linkages
CAUSAL_ARCS = [
    {"from": "United States", "to": "Taiwan", "desc": "US Taiwan Relations Act & Arms Transfers (Alpha: 0.88)"},
    {"from": "United States", "to": "Philippines", "desc": "US-Philippines EDCA Naval Basing (Alpha: 0.72)"},
    {"from": "United States", "to": "India", "desc": "QUAD Strategic Defense Partnership (Alpha: 0.65)"},
    {"from": "Russia", "to": "China", "desc": "Sino-Russian Energy & Defense Axis (Alpha: 0.82)"},
    {"from": "Russia", "to": "India", "desc": "Bilateral S-400 & Defense Hardware Accord (Alpha: 0.70)"},
    {"from": "European Union", "to": "India", "desc": "EU Indo-Pacific Maritime Cooperation (Alpha: 0.55)"}
]

# Strategic Indo-Pacific Hotspots (Zone A Focus)
STRATEGIC_HOTSPOTS = [
    {"name": "Galwan Valley (LAC)", "country": "India", "lat": 34.75, "lon": 78.22, "theater": "Western Himalayas"},
    {"name": "Pangong Tso Lake", "country": "India", "lat": 33.72, "lon": 78.91, "theater": "Ladakh Sector"},
    {"name": "Doklam Plateau", "country": "India", "lat": 27.30, "lon": 89.12, "theater": "Tri-Junction"},
    {"name": "Tawang / McMahon Line", "country": "India", "lat": 27.58, "lon": 91.86, "theater": "Eastern Sector"},
    {"name": "Line of Control (Kashmir)", "country": "Pakistan", "lat": 34.15, "lon": 74.30, "theater": "Indo-Pak Border"},
    {"name": "Taiwan Strait (Median Line)", "country": "Taiwan", "lat": 24.50, "lon": 120.50, "theater": "East China Sea"},
    {"name": "Scarborough Shoal", "country": "Philippines", "lat": 15.15, "lon": 117.75, "theater": "South China Sea"},
    {"name": "Spratly Islands / Second Thomas", "country": "Philippines", "lat": 9.80, "lon": 114.50, "theater": "South China Sea"},
    {"name": "Senkaku / Diaoyu Islands", "country": "Japan", "lat": 25.75, "lon": 123.50, "theater": "Ryukyu Arc"},
    {"name": "Malacca Strait Gateway", "country": "Singapore", "lat": 2.50, "lon": 101.50, "theater": "Maritime Chokepoint"},
    {"name": "Kachin Conflict Zone", "country": "Myanmar", "lat": 25.40, "lon": 97.40, "theater": "Northern Myanmar"},
    {"name": "Strait of Hormuz Entrance", "country": "India", "lat": 26.50, "lon": 56.50, "theater": "Sea Lines of Communication"}
]

# Strategic Maritime Chokepoints
MARITIME_CHOKEPOINTS = [
    {"name": "Strait of Malacca", "lat": 2.50, "lon": 101.50, "flow": "16M bbl/day oil transit", "significance": "Primary SLOC connecting Indian Ocean to Pacific"},
    {"name": "Taiwan Strait", "lat": 24.50, "lon": 120.50, "flow": "Global container & semiconductor corridor", "significance": "Flashpoint between PRC and Taiwan"},
    {"name": "Strait of Hormuz", "lat": 26.50, "lon": 56.50, "flow": "21M bbl/day petroleum choke", "significance": "Persian Gulf gateway to Indo-Pacific"},
    {"name": "Sunda Strait", "lat": -5.90, "lon": 105.80, "flow": "Secondary naval deep-water route", "significance": "Alternative bypass to Malacca"},
    {"name": "Lombok Strait", "lat": -8.50, "lon": 115.70, "flow": "Submarine transit corridor", "significance": "Deepest trench passage in Indonesian archipelago"},
    {"name": "Bab el-Mandeb", "lat": 12.60, "lon": 43.30, "flow": "Red Sea / Suez Canal gateway", "significance": "Western flank of Indian Ocean security architecture"}
]

# Satellite Optical Surveillance Sites (Sentinel-2 Border Logistics Index)
SATELLITE_SURVEILLANCE_SITES = [
    {"name": "Galwan Logistics Depot & Helipads", "lat": 34.79, "lon": 78.30, "type": "Optical Camp Detection", "sensor": "Sentinel-2 (10m Optical)", "change_score": "High (+42% Camp Growth)"},
    {"name": "Pangong Bridge Construction Base", "lat": 33.74, "lon": 78.95, "type": "Infrastructure Expansion", "sensor": "Sentinel-2 (10m Optical)", "change_score": "Severe (Spanned Span Complete)"},
    {"name": "Fiery Cross Reef Military Runway", "lat": 9.55, "lon": 112.89, "type": "Naval Bastion Alert", "sensor": "Copernicus Multi-Spectral", "change_score": "Reinforced Hangars Active"},
    {"name": "Subi Reef Deepwater Bastion", "lat": 10.91, "lon": 114.08, "type": "Maritime Fortification", "sensor": "Copernicus Multi-Spectral", "change_score": "Coastal Radar Active"},
    {"name": "Doklam Road Extension Forward Site", "lat": 27.28, "lon": 89.15, "type": "Surface Road Cut", "sensor": "Sentinel-2 Optical", "change_score": "Track Widening Detected"}
]

# Maritime AIS Militia & Dark Fleet Vectors (Global Fishing Watch Feed)
MARITIME_AIS_TRACKS = [
    {
        "name": "Second Thomas Shoal Militia Blockade Vector",
        "path": [[115.5, 9.8], [115.2, 9.85], [114.8, 9.88], [114.5, 9.8]],
        "vessel_count": 28,
        "color": [218, 54, 51, 200]
    },
    {
        "name": "Scarborough Shoal Swarm Perimeter",
        "path": [[117.6, 15.0], [117.8, 15.15], [117.9, 15.3], [117.7, 15.2]],
        "vessel_count": 19,
        "color": [210, 153, 34, 200]
    },
    {
        "name": "Taiwan Strait Median Line Incursion Path",
        "path": [[119.8, 23.5], [120.2, 24.2], [120.6, 24.8], [121.0, 25.4]],
        "vessel_count": 34,
        "color": [218, 54, 51, 220]
    }
]


def create_world_theater_map(
    features_df: pd.DataFrame,
    selected_country: Optional[str] = None,
    show_hotspots: bool = True,
    show_chokepoints: bool = True,
    show_causal_arcs: bool = True,
    show_zone_b: bool = True
) -> go.Figure:
    """
    Renders an interactive, dark military-themed Global Theater Choropleth Map:
    - Zone A countries shaded by Escalation Risk (Green -> Amber -> Red)
    - Zone B countries highlighted as Superpower Influence Nodes
    - Strategic Hotspot Radar Pings
    - Maritime Chokepoint Transit Badges
    - Geodesic Causal Policy Arcs from Zone B to Zone A
    """
    fig = go.Figure()

    # Build Country Risk Lookup
    country_risk = {}
    if not features_df.empty:
        for _, row in features_df.iterrows():
            c = str(row.get("country", ""))
            score = float(row.get("ml_risk_score", row.get("composite_risk_score", 30.0)) or 30.0)
            tier = str(row.get("ml_risk_tier", row.get("risk_level", "AMBER")))
            factor = str(row.get("top_factor", "Baseline"))
            country_risk[c] = (score, tier, factor)

    # 1. Zone A Choropleth Layer
    zone_a_locs = []
    zone_a_scores = []
    zone_a_texts = []
    zone_a_countries = []

    for c, iso in ZONE_A_ISO_MAP.items():
        score, tier, factor = country_risk.get(c, (24.0, "GREEN", "Stable Baseline"))
        zone_a_locs.append(iso)
        zone_a_scores.append(score)
        zone_a_countries.append(c)
        zone_a_texts.append(
            f"<b>{c} ({iso})</b><br>"
            f"Risk Score: <b>{score:.1f} / 100</b> ({tier})<br>"
            f"Dominant Factor: {factor}<br>"
            f"Theater: Zone A (Indo-Pacific)"
        )

    # Custom Tactical Heatmap Colorscale: Green (0) -> Amber (33-65) -> Red (66-100)
    risk_colorscale = [
        [0.0, "#2ea043"],
        [0.32, "#2ea043"],
        [0.33, "#d29922"],
        [0.65, "#d29922"],
        [0.66, "#da3633"],
        [1.0, "#b62324"]
    ]

    fig.add_trace(go.Choropleth(
        locations=zone_a_locs,
        z=zone_a_scores,
        text=zone_a_texts,
        hoverinfo="text",
        colorscale=risk_colorscale,
        zmin=0,
        zmax=100,
        colorbar=dict(
            title=dict(text="Escalation Risk", font=dict(color="#e6edf3", size=11)),
            tickfont=dict(color="#8b949e", size=10),
            thickness=12,
            len=0.6,
            y=0.5,
            x=1.01
        ),
        marker_line_color="#30363d",
        marker_line_width=1.0,
        name="Zone A Risk Theater"
    ))

    # 2. Zone B Superpower Influence Spheres (Tactical Blue)
    if show_zone_b:
        zb_locs = list(ZONE_B_ISO_MAP.values())
        zb_texts = [
            f"<b>{c} ({iso})</b><br>Role: <b>Zone B Global Influence Sphere</b><br>Signal: Sanctions, Arms Deals, Leadership Rhetoric"
            for c, iso in ZONE_B_ISO_MAP.items()
        ]
        fig.add_trace(go.Choropleth(
            locations=zb_locs,
            z=[50.0] * len(zb_locs),
            text=zb_texts,
            hoverinfo="text",
            colorscale=[[0, "#1f6feb"], [1, "#1f6feb"]],
            showscale=False,
            marker_line_color="#58a6ff",
            marker_line_width=1.2,
            name="Zone B Influence Sphere"
        ))

    # 3. Geodesic Causal Policy Arcs (Zone B -> Zone A)
    if show_causal_arcs:
        for arc in CAUSAL_ARCS:
            from_actor = arc["from"]
            to_country = arc["to"]
            from_coord = ZONE_B_COORDS.get(from_actor)
            to_coord = CAPITAL_COORDS.get(to_country)

            if from_coord and to_coord:
                fig.add_trace(go.Scattergeo(
                    lon=[from_coord[1], to_coord[1]],
                    lat=[from_coord[0], to_coord[0]],
                    mode="lines",
                    line=dict(width=1.8, color="rgba(88, 166, 255, 0.65)", dash="dash"),
                    hoverinfo="text",
                    text=f"<b>Causal Spillover Vector:</b><br>{from_actor} ➔ {to_country}<br>{arc['desc']}",
                    showlegend=False
                ))

    # 4. Strategic Tactical Hotspots (Radar Markers)
    if show_hotspots:
        hs_lons = [h["lon"] for h in STRATEGIC_HOTSPOTS]
        hs_lats = [h["lat"] for h in STRATEGIC_HOTSPOTS]
        hs_texts = []
        hs_colors = []
        hs_sizes = []

        for h in STRATEGIC_HOTSPOTS:
            c = h["country"]
            score, tier, factor = country_risk.get(c, (45.0, "AMBER", "Border Skirmish"))
            color = "#da3633" if (score >= 66 or tier == "RED") else ("#d29922" if score >= 33 else "#2ea043")
            size = 14 if (score >= 66 or tier == "RED") else (11 if score >= 33 else 9)
            hs_colors.append(color)
            hs_sizes.append(size)
            hs_texts.append(
                f"<b>📍 FLASHPOINT: {h['name']}</b><br>"
                f"Country: {h['country']} | Theater: {h['theater']}<br>"
                f"Risk Level: <b>{score:.1f} / 100 ({tier})</b><br>"
                f"Driver: {factor}"
            )

        fig.add_trace(go.Scattergeo(
            lon=hs_lons,
            lat=hs_lats,
            mode="markers+text",
            text=[h["name"].split(" ")[0] for h in STRATEGIC_HOTSPOTS],
            textposition="top center",
            textfont=dict(color="#c9d1d9", size=9),
            hovertext=hs_texts,
            hoverinfo="text",
            marker=dict(
                size=hs_sizes,
                color=hs_colors,
                symbol="diamond",
                line=dict(width=1.5, color="#ffffff")
            ),
            name="Tactical Flashpoints"
        ))

    # 5. Strategic Maritime Chokepoints
    if show_chokepoints:
        ck_lons = [c["lon"] for c in MARITIME_CHOKEPOINTS]
        ck_lats = [c["lat"] for c in MARITIME_CHOKEPOINTS]
        ck_texts = [
            f"<b>⚓ CHOKEPOINT: {c['name']}</b><br>Traffic: {c['flow']}<br>Significance: {c['significance']}"
            for c in MARITIME_CHOKEPOINTS
        ]

        fig.add_trace(go.Scattergeo(
            lon=ck_lons,
            lat=ck_lats,
            mode="markers",
            hovertext=ck_texts,
            hoverinfo="text",
            marker=dict(
                size=12,
                color="#58a6ff",
                symbol="square",
                line=dict(width=1.5, color="#ffffff")
            ),
            name="Maritime Chokepoints"
        ))

    # Highlight Selected Country if specified
    if selected_country and selected_country in CAPITAL_COORDS:
        sel_lat, sel_lon = CAPITAL_COORDS[selected_country]
        fig.add_trace(go.Scattergeo(
            lon=[sel_lon],
            lat=[sel_lat],
            mode="markers",
            marker=dict(size=22, color="rgba(255, 255, 255, 0)", line=dict(width=3, color="#f0883e")),
            hoverinfo="text",
            text=f"Selected Entity: {selected_country}",
            name="Selected Country Focus"
        ))

    # Dark Command Center Layout
    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showcoastlines=True,
            coastlinecolor="#30363d",
            showland=True,
            landcolor="#0d1117",
            showocean=True,
            oceancolor="#090d13",
            showcountries=True,
            countrycolor="#21262d",
            showlakes=True,
            lakecolor="#090d13",
            bgcolor="#090d13",
            lataxis=dict(range=[-35, 65]),
            lonaxis=dict(range=[-100, 160])
        ),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        margin=dict(l=0, r=0, t=20, b=10),
        height=580,
        legend=dict(
            font=dict(color="#8b949e", size=10),
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(22, 27, 34, 0.8)",
            bordercolor="#30363d",
            borderwidth=1
        )
    )

    return fig


def create_3d_hotspot_deck(
    features_df: pd.DataFrame,
    show_satellite: bool = True,
    show_maritime_ais: bool = True
) -> pdk.Deck:
    """
    Generate an interactive 3D PyDeck multi-INT visualization:
    - 3D Extruded Escalation Columns
    - Satellite Optical Infrastructure Sites (Sentinel-2)
    - Maritime AIS Militia Swarm Vectors
    """
    hotspot_data = []
    country_risk_map = {}

    if not features_df.empty:
        for _, row in features_df.iterrows():
            c = str(row.get("country", ""))
            score = float(row.get("composite_risk_score", row.get("ml_risk_score", 40.0)) or 40.0)
            level = str(row.get("risk_level", row.get("ml_risk_tier", "AMBER")))
            factor = str(row.get("top_factor", "Event Acceleration"))
            country_risk_map[c] = (score, level, factor)

    for spot in STRATEGIC_HOTSPOTS:
        c = spot["country"]
        score, level, factor = country_risk_map.get(c, (np.random.uniform(45, 75), "AMBER", "Border Skirmish Acceleration"))

        if score >= 66 or level == "RED":
            color = [218, 54, 51, 230]  # RED
            status = "CRITICAL ESCALATION"
        elif score >= 33 or level == "AMBER":
            color = [210, 153, 34, 210]  # AMBER
            status = "ELEVATED TENSION"
        else:
            color = [46, 160, 67, 190]   # GREEN
            status = "STABLE / MONITORED"

        hotspot_data.append({
            "name": spot["name"],
            "country": spot["country"],
            "theater": spot["theater"],
            "lat": spot["lat"],
            "lon": spot["lon"],
            "risk_score": round(score, 1),
            "status": status,
            "top_factor": factor,
            "elevation": score * 1600,
            "color": color
        })

    df = pd.DataFrame(hotspot_data)
    layers = []

    # 1. 3D Column Layer
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=40000,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )
    layers.append(column_layer)

    # 2. Scatter Rings
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_radius=55000,
        get_fill_color=[255, 255, 255, 40],
        stroked=True,
        get_line_color="color",
        get_line_width=3000,
    )
    layers.append(scatter_layer)

    # 3. Satellite Optical Infrastructure Sites (Sentinel-2)
    if show_satellite:
        sat_df = pd.DataFrame(SATELLITE_SURVEILLANCE_SITES)
        sat_layer = pdk.Layer(
            "ScatterplotLayer",
            data=sat_df,
            get_position=["lon", "lat"],
            get_radius=30000,
            get_fill_color=[56, 139, 253, 220],
            stroked=True,
            get_line_color=[255, 255, 255, 255],
            get_line_width=2000,
            pickable=True
        )
        layers.append(sat_layer)

    # 4. Maritime AIS Militia Paths
    if show_maritime_ais:
        ais_df = pd.DataFrame(MARITIME_AIS_TRACKS)
        ais_layer = pdk.Layer(
            "PathLayer",
            data=ais_df,
            get_path="path",
            get_color="color",
            width_min_pixels=3,
            pickable=True
        )
        layers.append(ais_layer)

    view_state = pdk.ViewState(
        latitude=21.0,
        longitude=95.0,
        zoom=3.6,
        pitch=48,
        bearing=12
    )

    tooltip = {
        "html": """
        <div style="background-color:#161b22; color:#e6edf3; padding:10px; border-radius:6px; font-family:sans-serif; border:1px solid #30363d;">
            <div style="font-weight:700; font-size:13px; color:#58a6ff;">{name}</div>
            <div style="font-size:11px; color:#8b949e; margin-top:2px;"><b>Theater/Type:</b> {theater}{type}</div>
            <div style="font-size:12px; margin-top:4px;"><b>Signal:</b> {risk_score}{change_score}{vessel_count}</div>
        </div>
        """,
        "style": {"color": "white"}
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="dark",
        tooltip=tooltip
    )
    return deck
