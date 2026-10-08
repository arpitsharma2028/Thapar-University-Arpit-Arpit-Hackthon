import pytest
from backend.ml.nlp_engine import get_risk_engine

@pytest.fixture(scope="module")
def engine():
    return get_risk_engine()

def test_sentiment_positive_earnings(engine):
    text = "NVIDIA smashes quarterly revenue expectations with 260% surge; raises margin guidance to all-time high."
    signal = engine.process_text(text)
    assert -1.0 <= signal["sentiment_score"] <= 1.0
    assert signal["sentiment_score"] > 0.3
    assert signal["confidence"] >= 0.5

def test_sentiment_negative_crisis(engine):
    text = "Commercial real estate delinquency spikes as multi-billion default cascades through regional banks."
    signal = engine.process_text(text)
    assert -1.0 <= signal["sentiment_score"] <= 1.0
    assert signal["sentiment_score"] < -0.2

def test_event_classification_geopolitical(engine):
    text = "Middle East shipping tensions escalate as naval patrols reroute tankers away from key straits."
    signal = engine.process_text(text)
    assert signal["category"] == "Geopolitical"

def test_event_classification_regulatory(engine):
    text = "Department of Justice antitrust ruling mandates major cloud service interoperability and data portability."
    signal = engine.process_text(text)
    assert signal["category"] == "Regulatory"

def test_impact_score_range(engine):
    text = "Catastrophic global supply chain embargo declared amid unprecedented maritime blockade."
    signal = engine.process_text(text)
    assert 1.0 <= signal["impact_score"] <= 10.0
    # High impact should exceed 7.0
    assert signal["impact_score"] >= 7.0

def test_entity_extraction(engine):
    text = "Microsoft unveils enterprise Copilot update while Apple prepares iOS spatial computing release."
    signal = engine.process_text(text)
    assert "MSFT" in signal["tickers"] or "AAPL" in signal["tickers"]
    assert signal["sector"] == "Technology"
