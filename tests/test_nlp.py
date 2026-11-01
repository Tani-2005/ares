import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts", "ares-dashboard", "src"))

from nlp_engine import NarrativeEngine


def test_source_credibility_tiering():
    engine = NarrativeEngine()
    tier1, weight1 = engine.get_source_tier("https://www.reuters.com/world/asia-pacific/border-clash")
    assert tier1 == 1
    assert weight1 == 1.0

    tier2, weight2 = engine.get_source_tier("https://www.globaltimes.cn/page/peace-talks.shtml")
    assert tier2 == 2
    assert weight2 == 0.4


def test_rhetorical_analysis():
    engine = NarrativeEngine()
    hostile_text = "Military troops mobilize after unprovoked border incursion and missile launch."
    res = engine.analyze_text(hostile_text)
    assert res["hostile_score"] > 0
    assert res["net_tension"] > 0
    assert res["hostile_matches"] >= 2

    peace_text = "Leaders sign historic ceasefire and peace agreement during bilateral summit."
    res_peace = engine.analyze_text(peace_text)
    assert res_peace["de_escalation_score"] > 0
    assert res_peace["net_tension"] < 0


def test_narrative_divergence():
    engine = NarrativeEngine()
    df = pd.DataFrame([
        {"country": "TestNation", "url": "reuters.com/news", "description": "Violent incursion and military mobilization along border."},
        {"country": "TestNation", "url": "apnews.com/news", "description": "Artillery shelling and retaliatory strike reported."},
        {"country": "TestNation", "url": "globaltimes.cn/news", "description": "Border situation completely calm, peaceful trade dialogue thriving."},
        {"country": "TestNation", "url": "xinhuanet.com/news", "description": "Cooperation and goodwill agreements celebrated."}
    ])

    div = engine.detect_narrative_divergence(df, "TestNation")
    assert div["divergence_detected"] is True
    assert div["divergence_score"] > 25.0

