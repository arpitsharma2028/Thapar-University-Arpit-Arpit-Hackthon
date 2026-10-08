import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_market_companies(client):
    response = client.get("/api/market/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 16
    assert any(c["ticker"] == "NVDA" for c in companies)

def test_market_data(client):
    response = client.get("/api/market/data/NVDA?days=20")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "NVDA"
    assert len(data["data"]) > 0
    first = data["data"][0]
    assert "close" in first
    assert "daily_return" in first
    assert "ma7" in first

def test_market_summary(client):
    response = client.get("/api/market/summary/AAPL")
    assert response.status_code == 200
    summary = response.json()
    assert summary["symbol"] == "AAPL"
    assert "volatility_score" in summary
    assert summary["volatility_score"] > 0
    assert "top_3_best_days" in summary

def test_monte_carlo_forecast(client):
    response = client.get("/api/market/forecast/MSFT?days=14&sentiment_guided=true")
    assert response.status_code == 200
    forecast = response.json()
    assert forecast["symbol"] == "MSFT"
    assert len(forecast["forecast"]) == 15
    first = forecast["forecast"][0]
    assert "upper" in first
    assert "median" in first
    assert "lower" in first
    assert first["upper"] >= first["median"] >= first["lower"]

def test_compare_stocks(client):
    response = client.get("/api/market/compare?symbol1=AAPL&symbol2=MSFT&days=30")
    assert response.status_code == 200
    comp = response.json()
    assert comp["symbol1"] == "AAPL"
    assert comp["symbol2"] == "MSFT"
    assert -1.0 <= comp["correlation"] <= 1.0
    assert len(comp["series"]) > 0

def test_gainers_losers(client):
    response = client.get("/api/market/gainers-losers")
    assert response.status_code == 200
    data = response.json()
    assert "gainers" in data
    assert "losers" in data
    assert len(data["gainers"]) > 0
