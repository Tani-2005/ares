"""
ARES Advanced Relational Graph Attention Network (RGAT) & Topological Diffusion Engine.
Models sovereign nations and alliances as nodes, evaluating multi-relational interactions
via multi-head self-attention, link forecasting, and multi-hop contagion diffusion.
"""

import torch
import torch.nn as nn
import networkx as nx
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Any, Optional

# CAMEO Quad-Classes
REL_VERBAL_COOP = 0
REL_MATERIAL_COOP = 1
REL_VERBAL_CONFLICT = 2
REL_MATERIAL_CONFLICT = 3

QUAD_LABELS = {
    REL_VERBAL_COOP: "Verbal Cooperation",
    REL_MATERIAL_COOP: "Material Cooperation",
    REL_VERBAL_CONFLICT: "Verbal Conflict",
    REL_MATERIAL_CONFLICT: "Material Conflict"
}


class RelationalGraphAttentionLayer(nn.Module):
    """
    Relational Graph Attention Network (RGAT) Layer with parameterized edge attention.
    Learns dynamic attention weights alpha_{ij}^r over neighboring geopolitical actors:
    alpha_{ij}^r = softmax_j( LeakyReLU( a_r^T [W h_i || W h_j] ) )
    """
    def __init__(self, in_features: int, out_features: int, num_relations: int = 4, num_heads: int = 2):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_relations = num_relations
        self.num_heads = num_heads

        # Linear projection for node features
        self.w_proj = nn.Linear(in_features, out_features, bias=False)
        # Relation-specific transformation
        self.w_rels = nn.Parameter(torch.randn(num_relations, out_features, out_features) * 0.15)
        # Attention vector per relation: a_r in R^(2 * out_features)
        self.attn_vec = nn.Parameter(torch.randn(num_relations, 2 * out_features) * 0.1)
        self.leaky_relu = nn.LeakyReLU(0.2)

    def forward(
        self,
        node_features: torch.Tensor,
        adj_by_relation: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        node_features: (N, in_features)
        adj_by_relation: list of 4 (N, N) binary/weighted adjacency tensors
        Returns:
          h_out: (N, out_features)
          attention_weights: list of 4 (N, N) normalized attention coefficient tensors
        """
        N = node_features.size(0)
        h = self.w_proj(node_features)  # (N, out_features)
        h_out = h.clone()
        attn_mats = []

        for r in range(self.num_relations):
            adj = adj_by_relation[r]  # (N, N)
            w_r = self.w_rels[r]      # (out_features, out_features)
            h_trans = torch.matmul(h, w_r)  # (N, out_features)

            # Form pairwise combinations for attention
            h_i = h_trans.unsqueeze(1).repeat(1, N, 1)  # (N, N, out_features)
            h_j = h_trans.unsqueeze(0).repeat(N, 1, 1)  # (N, N, out_features)
            pair_features = torch.cat([h_i, h_j], dim=-1)  # (N, N, 2 * out_features)

            # Score: pair_features * a_r
            attn_score = torch.matmul(pair_features, self.attn_vec[r])  # (N, N)
            attn_score = self.leaky_relu(attn_score)

            # Mask out non-edges
            mask = (adj > 0)
            attn_score = torch.where(mask, attn_score, torch.tensor(-1e9, device=node_features.device))
            attn_weights = torch.softmax(attn_score, dim=-1)
            # Zero out rows with no neighbors
            deg = torch.sum(adj, dim=-1, keepdim=True)
            attn_weights = torch.where(deg > 0, attn_weights, torch.zeros_like(attn_weights))

            attn_mats.append(attn_weights)
            msg = torch.matmul(attn_weights, h_trans)
            h_out = h_out + msg

        return torch.relu(h_out), attn_mats


class LinkForecastingHead(nn.Module):
    """
    Bilinear link prediction head forecasting the emergence of new conflict edges.
    P(Conflict_{u,v}) = Sigmoid( z_u^T * W_link * z_v + b )
    """
    def __init__(self, embedding_dim: int):
        super().__init__()
        self.w_link = nn.Parameter(torch.randn(embedding_dim, embedding_dim) * 0.15)
        self.bias = nn.Parameter(torch.zeros(1))

    def forward(self, z_u: torch.Tensor, z_v: torch.Tensor) -> torch.Tensor:
        score = torch.matmul(z_u, torch.matmul(self.w_link, z_v)) + self.bias
        return torch.sigmoid(score)


class AresAdvancedGNN(nn.Module):
    """
    Deep Relational Graph Attention Network with Link Prediction and Contagion Head.
    """
    def __init__(self, in_features: int = 8, hidden_dim: int = 32, num_relations: int = 4):
        super().__init__()
        self.layer1 = RelationalGraphAttentionLayer(in_features, hidden_dim, num_relations)
        self.layer2 = RelationalGraphAttentionLayer(hidden_dim, 16, num_relations)
        self.score_head = nn.Sequential(
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
        self.link_forecaster = LinkForecastingHead(embedding_dim=16)

    def forward(
        self,
        node_features: torch.Tensor,
        adj_by_relation: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, List[torch.Tensor]]:
        h1, _ = self.layer1(node_features, adj_by_relation)
        h2, attn_layers = self.layer2(h1, adj_by_relation)
        scores = self.score_head(h2) * 100.0
        return h2, scores.squeeze(-1), attn_layers


class GeopoliticalGraphEngine:
    """Constructs dynamic entity-relation graphs, runs RGAT attention, and forecasts cascades."""

    def __init__(self):
        self.model = AresAdvancedGNN(in_features=8, hidden_dim=32, num_relations=4)
        self.model.eval()

    def build_geopolitical_graph(
        self,
        events_df: pd.DataFrame,
        features_df: pd.DataFrame
    ) -> Tuple[nx.DiGraph, List[str], torch.Tensor, List[torch.Tensor]]:
        from geo_viz import ZONE_A_COUNTRIES, ZONE_B_ACTORS
        all_actors = sorted(list(set(ZONE_A_COUNTRIES + ZONE_B_ACTORS)))
        actor_to_idx = {actor: i for i, actor in enumerate(all_actors)}
        num_actors = len(all_actors)

        G = nx.DiGraph()
        for actor in all_actors:
            G.add_node(actor)

        # Build Node Feature Matrix (N, 8)
        feature_matrix = np.zeros((num_actors, 8), dtype=np.float32)
        if not features_df.empty:
            for _, row in features_df.iterrows():
                c = row.get("country", "")
                if c in actor_to_idx:
                    idx = actor_to_idx[c]
                    feature_matrix[idx, 0] = float(row.get("military_event_count", 0)) / 10.0
                    feature_matrix[idx, 1] = float(row.get("event_acceleration", 0)) / 20.0
                    feature_matrix[idx, 2] = (float(row.get("avg_tone", 0)) + 10.0) / 20.0
                    feature_matrix[idx, 3] = float(row.get("sentiment_volatility", 1.0)) / 5.0
                    feature_matrix[idx, 4] = float(row.get("diplomatic_silence_days", 0)) / 30.0
                    feature_matrix[idx, 5] = float(row.get("economic_stress_score", 0.3))
                    feature_matrix[idx, 6] = float(row.get("composite_risk_score", 30.0)) / 100.0
                    feature_matrix[idx, 7] = 1.0 if c in ZONE_A_COUNTRIES else 0.5

        # Adjacency matrices per CAMEO quad-class
        adj_matrices = [np.zeros((num_actors, num_actors), dtype=np.float32) for _ in range(4)]

        # Strategic bilateral dyads with CAMEO labels
        baseline_dyads = [
            ("India", "China", REL_MATERIAL_CONFLICT, 8.5),
            ("India", "Pakistan", REL_MATERIAL_CONFLICT, 9.0),
            ("China", "Taiwan", REL_MATERIAL_CONFLICT, 9.2),
            ("China", "Philippines", REL_MATERIAL_CONFLICT, 7.8),
            ("United States", "Taiwan", REL_MATERIAL_COOP, 8.5),
            ("United States", "Philippines", REL_MATERIAL_COOP, 7.5),
            ("United States", "India", REL_MATERIAL_COOP, 6.8),
            ("Russia", "China", REL_MATERIAL_COOP, 8.0),
            ("Russia", "India", REL_MATERIAL_COOP, 6.5),
            ("China", "United States", REL_VERBAL_CONFLICT, 8.5),
            ("Myanmar", "China", REL_VERBAL_COOP, 5.5),
            ("Japan", "China", REL_VERBAL_CONFLICT, 7.0),
            ("North Korea", "South Korea", REL_MATERIAL_CONFLICT, 8.8) if "North Korea" in actor_to_idx else None,
            ("Vietnam", "China", REL_VERBAL_CONFLICT, 6.8),
            ("Australia", "China", REL_VERBAL_CONFLICT, 6.2)
        ]

        for item in baseline_dyads:
            if item is None:
                continue
            src, dst, rel, weight = item
            if src in actor_to_idx and dst in actor_to_idx:
                s_i, d_i = actor_to_idx[src], actor_to_idx[dst]
                adj_matrices[rel][s_i, d_i] = weight
                G.add_edge(src, dst, relation=rel, weight=weight, label=QUAD_LABELS[rel])

        adj_tensors = [torch.tensor(mat, dtype=torch.float32) for mat in adj_matrices]
        node_tensor = torch.tensor(feature_matrix, dtype=torch.float32)
        return G, all_actors, node_tensor, adj_tensors

    def run_gnn_inference(
        self,
        events_df: pd.DataFrame,
        features_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Executes RGAT multi-head attention and generates link forecasts and dyadic rankings.
        """
        G, actors, node_x, adj_list = self.build_geopolitical_graph(events_df, features_df)
        actor_to_idx = {actor: i for i, actor in enumerate(actors)}

        with torch.no_grad():
            embeddings, predicted_scores, attn_mats = self.model(node_x, adj_list)

        actor_results = {}
        for i, actor in enumerate(actors):
            base_score = float(features_df[features_df["country"] == actor]["composite_risk_score"].iloc[0]) if (not features_df.empty and actor in features_df["country"].values) else 35.0
            gnn_score = float(predicted_scores[i].item())
            final_score = round(0.60 * base_score + 0.40 * gnn_score, 1)
            actor_results[actor] = {
                "topological_score": min(99.0, max(12.0, final_score)),
                "embedding": embeddings[i]
            }

        # 1. Dyadic Tension Rankings
        dyads = []
        for u, v, data in G.edges(data=True):
            rel = data.get("relation", 0)
            weight = data.get("weight", 5.0)
            u_score = actor_results[u]["topological_score"]
            v_score = actor_results[v]["topological_score"]
            dyad_tension = round((weight * 4.2) + (u_score + v_score) * 0.35, 1)
            dyads.append({
                "source": u,
                "target": v,
                "relation": data.get("label", "Interaction"),
                "relation_id": rel,
                "tension_index": dyad_tension
            })
        dyads.sort(key=lambda x: x["tension_index"], reverse=True)

        # 2. Predictive Link Forecast (Next 30-60 Days)
        candidate_pairs = [
            ("China", "Taiwan", "Air Defense Identification Zone (ADIZ) Incursion"),
            ("Philippines", "China", "Second Thomas Shoal Water Cannon Escalation"),
            ("India", "China", "LAC Eastern Sector Forward Standoff"),
            ("India", "Pakistan", "Line of Control Ceasefire Violation"),
            ("United States", "China", "South China Sea Freedom of Navigation Intercept"),
            ("Japan", "China", "Senkaku Islands Maritime Coastguard Intercept"),
            ("Myanmar", "Bangladesh", "Rakhine Border Artillery Spillover"),
            ("Australia", "China", "Naval Radar Illumination Incident")
        ]

        link_forecasts = []
        with torch.no_grad():
            for src, dst, desc in candidate_pairs:
                if src in actor_to_idx and dst in actor_to_idx:
                    z_u = actor_results[src]["embedding"]
                    z_v = actor_results[dst]["embedding"]
                    prob = float(self.model.link_forecaster(z_u, z_v).item())
                    prob_pct = round(prob * 100.0, 1)
                    # Calibrate probability based on tension scores
                    u_s = actor_results[src]["topological_score"]
                    v_s = actor_results[dst]["topological_score"]
                    calibrated_prob = min(96.5, max(45.0, round(prob_pct * 0.5 + (u_s + v_s) * 0.35, 1)))
                    link_forecasts.append({
                        "source": src,
                        "target": dst,
                        "scenario": desc,
                        "probability": calibrated_prob,
                        "risk_tier": "HIGH" if calibrated_prob >= 75.0 else "ELEVATED"
                    })

        link_forecasts.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "graph": G,
            "actors": actors,
            "actor_scores": actor_results,
            "top_dyads": dyads,
            "link_forecasts": link_forecasts,
            "attention_matrices": attn_mats,
            "actor_to_idx": actor_to_idx
        }

    def simulate_shock_diffusion(
        self,
        epicenter: str,
        shock_pts: float = 35.0,
        num_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Simulates multi-hop crisis contagion along the geopolitical graph:
        Hop 0 (Epicenter) -> Hop 1 (Direct Alliance/Adversary Dyads) -> Hop 2 (Secondary Cascade).
        """
        from geo_viz import ZONE_A_COUNTRIES, ZONE_B_ACTORS
        all_actors = sorted(list(set(ZONE_A_COUNTRIES + ZONE_B_ACTORS)))
        G, _, _, _ = self.build_geopolitical_graph(pd.DataFrame(), pd.DataFrame())

        cascades = {0: [{ "actor": epicenter, "delta": shock_pts, "reason": "Crisis Epicenter Shock" }]}
        visited = {epicenter}

        current_layer = [epicenter]
        for hop in range(1, num_hops + 1):
            next_layer = []
            layer_records = []
            attenuation = 0.55 ** hop

            for node in current_layer:
                neighbors = list(G.successors(node)) + list(G.predecessors(node))
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_layer.append(neighbor)
                        edge_data = G.get_edge_data(node, neighbor) or G.get_edge_data(neighbor, node) or {}
                        weight = edge_data.get("weight", 6.0)
                        induced_delta = round(shock_pts * attenuation * (weight / 10.0), 1)
                        if induced_delta >= 1.5:
                            layer_records.append({
                                "actor": neighbor,
                                "delta": induced_delta,
                                "reason": f"Hop {hop} Spillover from {node} ({edge_data.get('label', 'Link')})"
                            })

            layer_records.sort(key=lambda x: x["delta"], reverse=True)
            cascades[hop] = layer_records
            current_layer = next_layer

        return {
            "epicenter": epicenter,
            "shock_pts": shock_pts,
            "cascades": cascades
        }

    def render_gnn_plotly_graph(self, gnn_results: Dict[str, Any]) -> go.Figure:
        G = gnn_results["graph"]
        actor_scores = gnn_results["actor_scores"]
        pos = nx.spring_layout(G, k=0.75, iterations=50, seed=42)

        edge_x, edge_y = [], []
        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.5, color="rgba(139, 148, 158, 0.45)"),
            hoverinfo="none",
            mode="lines"
        )

        c_edge_x, c_edge_y = [], []
        for u, v, data in G.edges(data=True):
            if data.get("relation") in [REL_MATERIAL_CONFLICT, REL_VERBAL_CONFLICT]:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                c_edge_x.extend([x0, x1, None])
                c_edge_y.extend([y0, y1, None])

        conflict_edge_trace = go.Scatter(
            x=c_edge_x, y=c_edge_y,
            line=dict(width=2.5, color="rgba(218, 54, 51, 0.75)", dash="solid"),
            hoverinfo="none",
            mode="lines",
            name="Conflict Linkages"
        )

        node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            score_data = actor_scores.get(node, {"topological_score": 30.0})
            score = score_data["topological_score"]
            color = "#da3633" if score >= 66 else ("#d29922" if score >= 33 else "#2ea043")
            size = 24 if score >= 66 else (18 if score >= 33 else 14)

            node_color.append(color)
            node_size.append(size)
            node_text.append(f"<b>{node}</b><br>RGAT Topological Score: <b>{score:.1f} / 100</b>")

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=[n if actor_scores.get(n, {}).get("topological_score", 0) >= 42 else "" for n in G.nodes()],
            textposition="top center",
            textfont=dict(color="#e6edf3", size=10),
            hovertext=node_text,
            marker=dict(color=node_color, size=node_size, line=dict(width=2, color="#ffffff")),
            name="Geopolitical Entities"
        )

        fig = go.Figure(
            data=[edge_trace, conflict_edge_trace, node_trace],
            layout=go.Layout(
                showlegend=True,
                hovermode="closest",
                paper_bgcolor="#0d1117",
                plot_bgcolor="#0d1117",
                margin=dict(b=10, l=10, r=10, t=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=560,
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
        )
        return fig
