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

# --- Negation & Contrast Regression Test Suite ---

def test_negation_strong_growth(engine):
    text = "The company reported strong revenue growth."
    signal = engine.process_text(text)
    assert signal["sentiment_score"] > 0.3

def test_negation_did_not_achieve(engine):
    text = "The company did not achieve its revenue target."
    signal = engine.process_text(text)
    assert signal["sentiment_score"] < 0.0

def test_negation_not_facing_crisis(engine):
    text = "The company is not facing a credit crisis."
    signal = engine.process_text(text)
    # Negated crisis should mitigate negative severity to neutral/mild
    assert signal["sentiment_score"] >= -0.15

def test_negation_contrast_clause(engine):
    text = "Revenue increased, but the future outlook weakened."
    signal = engine.process_text(text)
    # The post-contrast clause dominates
    assert signal["sentiment_score"] < 0.0

def test_negation_no_improvement(engine):
    text = "The company reported no improvement in demand."
    signal = engine.process_text(text)
    assert signal["sentiment_score"] < 0.0

# --- Event Classification & Evidence Gating ---

def test_event_classification_geopolitical(engine):
    text = "Middle East shipping tensions escalate as naval patrols reroute tankers away from key straits."
    signal = engine.process_text(text)
    assert signal["category"] == "Geopolitical"

def test_event_classification_regulatory(engine):
    text = "Department of Justice antitrust ruling mandates major cloud service interoperability and data portability."
    signal = engine.process_text(text)
    assert signal["category"] == "Regulatory"

def test_event_classification_macro_fed(engine):
    text = "Fed holds rates steady, signals cuts in upcoming FOMC policy meeting."
    signal = engine.process_text(text)
    assert signal["category"] == "Macroeconomic"

def test_event_classification_croissant_bakery_gating(engine):
    text = "Local bakery wins award for best croissant."
    signal = engine.process_text(text)
    # Must NOT be classified as Earnings or assign ticker SPY
    assert signal["category"] == "Other"
    assert signal["tickers"] == []
    assert signal["companies"] == []

def test_event_classification_tesla_recall_not_earnings(engine):
    text = "Tesla recalls 2M vehicles over defect."
    signal = engine.process_text(text)
    assert signal["category"] != "Earnings"
    assert "TSLA" in signal["tickers"]

def test_impact_score_range(engine):
    text = "Catastrophic global supply chain embargo declared amid unprecedented maritime blockade."
    signal = engine.process_text(text)
    assert 1.0 <= signal["impact_score"] <= 10.0
    assert signal["impact_score"] >= 7.0

def test_entity_extraction(engine):
    text = "Microsoft unveils enterprise Copilot update while Apple prepares iOS spatial computing release."
    signal = engine.process_text(text)
    assert "MSFT" in signal["tickers"] or "AAPL" in signal["tickers"]
    assert signal["sector"] == "Technology"

def test_empty_and_malformed_text(engine):
    signal_empty = engine.process_text("")
    assert signal_empty["sentiment_score"] == 0.0
    assert signal_empty["category"] == "Other"
    assert signal_empty["tickers"] == []
