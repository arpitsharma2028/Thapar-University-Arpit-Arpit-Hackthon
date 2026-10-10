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

def test_stress_test_boundary_exact_score_7_vs_8(service):
    from backend.core.exceptions import DomainValidationError
    
    # Impact score exactly 7.0 MUST NOT trigger wholesale stress test (threshold is > 7.0)
    event_score_7 = {
        "event_id": "EVT-SCORE-7",
        "headline": "Moderate supply friction reported",
        "category": "Geopolitical",
        "sentiment_score": -0.4,
        "impact_score": 7.0
    }
    assert service.map_event_to_scenario(event_score_7) is None
    with pytest.raises(DomainValidationError) as exc:
        service.run_stress_test(trigger_event=event_score_7)
    assert "does not exceed systemic threshold (> 7.0)" in str(exc.value)

    # Impact score 8.0 MUST trigger wholesale stress test
    event_score_8 = {
        "event_id": "EVT-SCORE-8",
        "headline": "Severe naval blockade declared in Strait of Hormuz",
        "category": "Geopolitical",
        "sentiment_score": -0.8,
        "impact_score": 8.0
    }
    assert service.map_event_to_scenario(event_score_8) is not None
    res = service.run_stress_test(trigger_event=event_score_8)
    assert res["scenario_id"] == "SCEN-GEO-01"

def test_stress_test_reconciled_multipliers(service):
    # Baseline 1.0x multiplier: -$4.6875M (-9.38%) on $50M book
    base_res = service.run_stress_test(scenario_id="SCEN-GEO-01", severity_multiplier=1.0)
    assert base_res["total_dollar_loss"] == 4_687_500.0
    assert base_res["total_loss_pct"] == 9.38
    assert base_res["total_value_after"] == 45_312_500.0

    # Amplified 1.6x multiplier: -$7.500M (-15.00%) on $50M book, ending at $42.50M
    amp_res = service.run_stress_test(scenario_id="SCEN-GEO-01", severity_multiplier=1.6)
    assert amp_res["total_dollar_loss"] == 7_500_000.0
    assert amp_res["total_loss_pct"] == 15.0
    assert amp_res["total_value_after"] == 42_500_000.0
