import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["nlp_engine_loaded"] is True

def test_api_events_list(client):
    response = client.get("/api/events?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert len(data["events"]) > 0

def test_api_analyze_custom_text(client):
    payload = {
        "text": "Alphabet announces breakthrough quantum acceleration chip for Gemini cloud datacenters.",
        "source": "AI Tech Wire",
        "source_type": "News"
    }
    response = client.post("/api/events/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment_score"] > 0
    assert "GOOGL" in data["tickers"] or "Alphabet Inc." in data["companies"]
    assert 1.0 <= data["impact_score"] <= 10.0

def test_api_portfolio_endpoint(client):
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert "total_value" in data
    assert "positions" in data
    assert len(data["positions"]) == 16

def test_api_rebalance_endpoint(client):
    payload = {
        "event_id": "API-TEST-01",
        "headline": "Apple Services revenue hits all-time record high",
        "tickers": "AAPL",
        "sector": "Technology",
        "sentiment_score": 0.75,
        "impact_score": 7.5,
        "sensitivity": 0.025
    }
    response = client.post("/api/portfolio/rebalance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "updated_positions" in data

def test_api_stress_test_run(client):
    payload = {
        "scenario_id": "SCEN-GEO-01",
        "severity_multiplier": 1.0
    }
    response = client.post("/api/stress-tests/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_dollar_loss" in data
    assert data["total_dollar_loss"] > 0

def test_api_metrics_endpoint(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "portfolio" in data
    assert "risk_engine" in data
    assert "sector_allocation" in data

def test_api_rss_ingestion_endpoint(client):
    response = client.post("/api/events/ingest/rss?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("success", "offline", "empty")

def test_api_stress_test_boundary_below_threshold(client):
    # Event with impact <= 7.0 should NOT trigger wholesale stress test (threshold is > 7.0)
    low_event = {
        "event_id": "EVT-LOW-IMPACT",
        "headline": "Minor retail store renovations announced",
        "impact_score": 7.0,
        "sentiment_score": 0.1,
        "category": "Other"
    }
    from backend.services.stress_test_service import StressTestService
    service = StressTestService()
    mapped = service.map_event_to_scenario(low_event)
    assert mapped is None  # Exact 7.0 must not breach > 7.0 threshold
