"""
ARES NLP & Narrative Analysis Engine.
Analyzes news headlines, text streams, narrative tension,
source credibility weighting, and state media narrative divergence.
"""

import re
import logging
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Tier 1: Independent / High-Credibility International & Regional Media (Weight = 1.0)
TIER_1_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "thehindu.com", "hindustantimes.com",
    "nikkei.com", "aljazeera.com", "bloomberg.com", "ft.com", "scmp.com",
    "straitstimes.com", "japantimes.co.jp", "dawn.com", "afp.com"
}

# Tier 2: State-Controlled / Official Propaganda Outlets (Weight = 0.4)
TIER_2_DOMAINS = {
    "globaltimes.cn", "xinhuanet.com", "chinadaily.com.cn", "tass.com",
    "rt.com", "ptv.com.pk", "radio.gov.pk", "kcna.kp", "cgtn.com",
    "peoplesdaily.com.cn"
}

# Geopolitical Rhetorical Keywords
HOSTILE_RHETORIC = [
    r"\b(retaliat\w*|strike back|punitive)\b",
    r"\b(incursion|violation|encroach\w*)\b",
    r"\b(sovereignty|territorial integrity|red line)\b",
    r"\b(provocation|unprovoked|belligeren\w*)\b",
    r"\b(mobiliz\w*|troops mass\w*|reinforce\w*|drill\w*)\b",
    r"\b(blockade|intercept\w*|missile launch)\b",
    r"\b(unforgivable|grave consequences|war\b|clash\w*)\b",
    r"\b(sanction\w*|embargo|blacklist\w*)\b"
]

DE_ESCALATION_RHETORIC = [
    r"\b(ceasefire|truce|peace agreement)\b",
    r"\b(diplomatic talks|bilateral summit|cooperat\w*)\b",
    r"\b(de-escalat\w*|disengage\w*|buffer zone)\b",
    r"\b(joint statement|dialogue|peaceful resolution)\b",
    r"\b(trade deal|economic corridor|goodwill)\b"
]

COMPILED_HOSTILE = [re.compile(p, re.IGNORECASE) for p in HOSTILE_RHETORIC]
COMPILED_DE_ESCALATION = [re.compile(p, re.IGNORECASE) for p in DE_ESCALATION_RHETORIC]


class NarrativeEngine:
    """Processes geopolitical text streams, computes rhetoric intensity, and flags narrative divergence."""

    def __init__(self):
        self._transformer_model = None
        self._has_transformers = False
        try:
            import transformers
            self._has_transformers = True
            logger.info("HuggingFace Transformers detected.")
        except Exception:
            logger.info("Using optimized geopolitical lexicon and regex sentiment engine.")

    def get_source_tier(self, url_or_domain: str) -> Tuple[int, float]:
        """Return (tier, weight) for a given source domain or URL."""
        if not url_or_domain:
            return 1, 0.8
        target = url_or_domain.lower()
        for d in TIER_2_DOMAINS:
            if d in target:
                return 2, 0.4
        for d in TIER_1_DOMAINS:
            if d in target:
                return 1, 1.0
        return 1, 0.8

    def analyze_text(self, text: str, source_domain: str = "") -> Dict:
        """
        Analyze a headline or article snippet for:
        - Hostile Rhetoric Score (0 to 100)
        - De-escalation Marker Score (0 to 100)
        - Net Narrative Tension (-100 to +100)
        - Source Credibility Weight
        """
        if not text or not isinstance(text, str):
            return {
                "hostile_score": 0.0,
                "de_escalation_score": 0.0,
                "net_tension": 0.0,
                "tier": 1,
                "credibility_weight": 1.0,
                "hostile_matches": 0,
                "de_escalation_matches": 0
            }

        tier, weight = self.get_source_tier(source_domain)

        h_matches = sum(len(pattern.findall(text)) for pattern in COMPILED_HOSTILE)
        d_matches = sum(len(pattern.findall(text)) for pattern in COMPILED_DE_ESCALATION)

        # Base scores scaled by matches
        hostile_score = min(100.0, h_matches * 30.0)
        de_escalation_score = min(100.0, d_matches * 25.0)

        # Net narrative tension (-100 to +100)
        net_tension = (hostile_score - de_escalation_score) * weight

        return {
            "hostile_score": round(hostile_score, 2),
            "de_escalation_score": round(de_escalation_score, 2),
            "net_tension": round(net_tension, 2),
            "tier": tier,
            "credibility_weight": weight,
            "hostile_matches": h_matches,
            "de_escalation_matches": d_matches
        }

    def detect_narrative_divergence(self, articles_df: pd.DataFrame, country: str) -> Dict:
        """
        PRD §7.1: Detect when Tier 2 state-controlled media narrative contradicts
        Tier 1 independent international coverage (e.g. State media claims peace while
        independent outlets document border skirmishes and aggressive posturing).
        """
        if articles_df.empty or "description" not in articles_df.columns:
            return {"divergence_detected": False, "divergence_score": 0.0, "details": "No articles"}

        c_df = articles_df[articles_df["country"] == country].copy() if "country" in articles_df.columns else articles_df.copy()
        if c_df.empty:
            return {"divergence_detected": False, "divergence_score": 0.0, "details": "No country articles"}

        t1_tensions = []
        t2_tensions = []

        for _, row in c_df.iterrows():
            text = str(row.get("description", ""))
            url = str(row.get("url", ""))
            res = self.analyze_text(text, url)
            if res["tier"] == 2:
                t2_tensions.append(res["net_tension"])
            else:
                t1_tensions.append(res["net_tension"])

        if not t1_tensions or not t2_tensions:
            # Not enough dual-tier reporting to prove divergence
            return {
                "divergence_detected": False,
                "divergence_score": 0.0,
                "tier1_avg_tension": round(np.mean(t1_tensions), 2) if t1_tensions else 0.0,
                "tier2_avg_tension": round(np.mean(t2_tensions), 2) if t2_tensions else 0.0,
                "details": "Insufficient multi-tier coverage for divergence confirmation"
            }

        t1_mean = np.mean(t1_tensions)
        t2_mean = np.mean(t2_tensions)

        # Divergence occurs when Independent media shows high tension, while state media paints an overly benign picture
        divergence = t1_mean - t2_mean
        is_divergent = divergence > 25.0

        return {
            "divergence_detected": bool(is_divergent),
            "divergence_score": round(max(0.0, divergence), 2),
            "tier1_avg_tension": round(t1_mean, 2),
            "tier2_avg_tension": round(t2_mean, 2),
            "details": f"Tier 1 (Independent) Net Tension: {t1_mean:.1f} vs Tier 2 (State Media): {t2_mean:.1f}"
        }

