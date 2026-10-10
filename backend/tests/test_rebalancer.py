import pytest
from backend.services.rebalance_service import RebalanceService

@pytest.fixture
def service():
    serv = RebalanceService()
    serv.reset_portfolio()
    return serv

def test_portfolio_initial_state(service):
    portfolio = service.get_current_portfolio()
    assert portfolio["positions_count"] == 16
    assert abs(portfolio["total_value"] - 10_000_000.0) < 50_000.0
    total_wt = sum(p["current_weight"] for p in portfolio["positions"])
    assert abs(total_wt - 1.0) < 0.001

def test_rebalance_positive_sentiment(service):
    # Positive sentiment for NVDA should increase NVDA weight
    initial_p = service.get_current_portfolio()
    nvda_old = next(p for p in initial_p["positions"] if p["ticker"] == "NVDA")["current_weight"]

    event = {
        "event_id": "TEST-POS-01",
        "headline": "NVDA sets record revenue with incredible AI chip surge",
        "tickers": "NVDA",
        "sector": "Technology",
        "sentiment_score": 0.85,
        "impact_score": 9.0
    }
    result = service.rebalance(event, sensitivity=0.03)

    assert result["status"] == "success"
    nvda_up = next(p for p in result["updated_positions"] if p["ticker"] == "NVDA")
    assert nvda_up["new_weight"] > nvda_old
    assert nvda_up["weight_delta"] > 0

    # Ensure total weights normalize to 1.0000
    total_wt = sum(p["new_weight"] for p in result["updated_positions"])
    assert abs(total_wt - 1.0) < 0.0005

def test_rebalance_negative_sentiment(service):
    # Negative sentiment for TSLA should decrease TSLA weight
    initial_p = service.get_current_portfolio()
    tsla_old = next(p for p in initial_p["positions"] if p["ticker"] == "TSLA")["current_weight"]

    event = {
        "event_id": "TEST-NEG-01",
        "headline": "Tesla margins plunge on steep discounting and German factory stoppage",
        "tickers": "TSLA",
        "sector": "Consumer Discretionary",
        "sentiment_score": -0.80,
        "impact_score": 8.0
    }
    result = service.rebalance(event, sensitivity=0.03)

    tsla_up = next(p for p in result["updated_positions"] if p["ticker"] == "TSLA")
    assert tsla_up["new_weight"] < tsla_old
    assert tsla_up["weight_delta"] < 0
    assert tsla_up["new_weight"] >= service.min_weight  # Clamped to min weight floor

def test_no_negative_weights(service):
    # Extreme negative event should not cause weight to go below min_weight floor (0.01)
    event = {
        "event_id": "TEST-EXTREME-NEG",
        "headline": "Catastrophic collapse in ticker AAPL",
        "tickers": "AAPL",
        "sector": "Technology",
        "sentiment_score": -1.0,
        "impact_score": 10.0
    }
    # Run multiple times with high sensitivity
    for _ in range(5):
        service.rebalance(event, sensitivity=0.10)

    portfolio = service.get_current_portfolio()
    for pos in portfolio["positions"]:
        assert pos["current_weight"] >= service.min_weight
        assert pos["current_weight"] <= service.max_weight

def test_bounded_simplex_extreme_invariants(service):
    # Test extreme bullish event with maximal sensitivity
    bullish_event = {
        "event_id": "TEST-EXTREME-BULL",
        "headline": "Historic trillion dollar revenue explosion in NVDA",
        "tickers": "NVDA",
        "sector": "Technology",
        "sentiment_score": 1.0,
        "impact_score": 10.0
    }
    result = service.rebalance(bullish_event, sensitivity=0.20, max_turnover=0.15, transaction_cost_bps=5.0)
    
    # 1. Weights strictly within [1%, 25%]
    for p in result["updated_positions"]:
        assert p["new_weight"] >= 0.01, f"Weight {p['new_weight']} below 1.0% floor for {p['ticker']}"
        assert p["new_weight"] <= 0.25, f"Weight {p['new_weight']} above 25.0% cap for {p['ticker']}"
    
    # 2. Strict exact normalization sum == 1.0000
    total_w = sum(p["new_weight"] for p in result["updated_positions"])
    assert abs(total_w - 1.0) < 0.0001, f"Total weight sum {total_w} deviates from 1.0"
    
    # 3. Turnover respects cap
    assert result["turnover_pct"] <= 15.01
    
    # 4. Transaction cost calculated correctly
    assert result["transaction_cost_usd"] > 0
    
    # 5. Benchmark comparison present
    assert "strategy_cum_return_pct" in result
    assert "benchmark_cum_return_pct" in result
