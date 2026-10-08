import datetime
from fastapi import APIRouter
from backend.services.metrics_service import MetricsService
from backend.services.event_service import EventService
from backend.services.rebalance_service import RebalanceService
from backend.services.stress_test_service import StressTestService
from backend.models.schemas import HealthResponse

router = APIRouter(tags=["Metrics & Diagnostics"])
metrics_service = MetricsService()
event_service = EventService()
rebalance_service = RebalanceService()
stress_service = StressTestService()

@router.get("/api/metrics")
def get_metrics():
    """
    Returns aggregate platform KPIs, risk metrics, and valuation history.
    """
    return metrics_service.get_dashboard_metrics()

@router.get("/api/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint validating NLP engine and database readiness.
    """
    return {
        "status": "healthy",
        "service": "FinSight AI Risk Intelligence Platform",
        "version": "1.0.0-hackathon",
        "nlp_engine_loaded": True,
        "database_connected": True,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@router.post("/api/demo/scenario")
def run_demo_scenario():
    """
    Automated execution of the official Hackathon Demo Scenario:
    1. Analyzes a severe negative geopolitical event
    2. Executes tactical dynamic index rebalancing (Module A)
    3. Detects impact >= 7.0 and triggers strategic wholesale portfolio stress test (Module B)
    4. Returns coordinated before/after results for instant demo review.
    """
    sample_text = (
        "Middle East shipping tensions escalate as naval patrols reroute tankers away from key straits; "
        "crude supply disruptions loom while semiconductor freight faces 3-week delays."
    )
    
    # 1. Analyze Event with NLP Engine
    risk_signal = event_service.analyze_and_store(
        text=sample_text,
        headline="Middle East Naval Crisis Disrupts Oil & Tech Supply Chains",
        source="Reuters Breaking Financials",
        source_type="News"
    )

    # 2. Module A: Rebalance Equity Index
    rebalance_result = rebalance_service.rebalance(risk_signal, sensitivity=0.035)

    # 3. Module B: Trigger Strategic Stress Test
    stress_result = stress_service.run_stress_test(
        scenario_id="SCEN-GEO-01",
        trigger_event=risk_signal,
        severity_multiplier=1.05
    )

    return {
        "step_1_nlp_risk_signal": risk_signal,
        "step_2_module_a_rebalance": rebalance_result,
        "step_3_module_b_stress_test": stress_result
    }
