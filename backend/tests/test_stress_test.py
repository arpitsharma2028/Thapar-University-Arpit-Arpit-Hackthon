import pytest
from backend.services.stress_test_service import StressTestService

@pytest.fixture
def service():
    return StressTestService()

def test_stress_test_execution(service):
    result = service.run_stress_test(scenario_id="SCEN-GEO-01")
    assert result["test_id"].startswith("STRESS-")
    assert result["total_value_before"] == 50_000_000.0
    assert result["total_value_after"] < result["total_value_before"]
    assert result["total_dollar_loss"] > 0
    assert result["total_loss_pct"] > 0
    assert "Equities" in result["asset_impacts"]
    assert "Bonds" in result["asset_impacts"]
    assert len(result["worst_positions"]) > 0

def test_stress_test_high_impact_event_trigger(service):
    trigger_event = {
        "event_id": "EVT-TEST-STRESS",
        "headline": "Systemic Credit Contagion Across European Commercial Properties",
        "category": "Credit",
        "sentiment_score": -0.85,
        "impact_score": 8.8,
        "sector": "Financials"
    }
    result = service.run_stress_test(trigger_event=trigger_event)
    assert result["severity"] >= 7.0
    assert result["total_loss_pct"] > 5.0
    assert result["asset_impacts"]["Derivatives"]["dollar_loss"] > 0

def test_stress_test_history(service):
    service.run_stress_test(scenario_id="SCEN-MACRO-02")
    history = service.get_history(limit=5)
    assert len(history) >= 1
    assert "scenario_name" in history[0]
