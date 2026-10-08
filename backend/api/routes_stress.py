"""
FinSight AI — Strategic Stress Testing API Router
Provides wholesale banking multi-asset portfolio stress simulation endpoints (Module B) with Dependency Injection.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, Depends
from backend.services.stress_test_service import StressTestService
from backend.services.event_service import EventService
from backend.models.schemas import StressTestRequest
from backend.api.deps import get_stress_service, get_event_service

router = APIRouter(prefix="/api/stress-tests", tags=["Strategic Stress Testing"])

@router.get("")
def get_stress_history(
    limit: int = Query(20, ge=1, le=50),
    stress_service: StressTestService = Depends(get_stress_service)
):
    """
    Returns history of wholesale portfolio stress tests.
    """
    return stress_service.get_history(limit=limit)

@router.get("/scenarios")
def get_stress_scenarios(
    stress_service: StressTestService = Depends(get_stress_service)
):
    """
    Returns available wholesale banking stress test scenarios.
    """
    return stress_service.get_scenarios()

@router.get("/portfolio")
def get_wholesale_portfolio(
    stress_service: StressTestService = Depends(get_stress_service)
):
    """
    Returns the baseline wholesale multi-asset portfolio breakdown ($50M).
    """
    return stress_service.get_wholesale_portfolio()

@router.post("/run")
def run_stress_test(
    req: StressTestRequest,
    stress_service: StressTestService = Depends(get_stress_service),
    event_service: EventService = Depends(get_event_service)
):
    """
    MODULE B: Executes strategic multi-asset portfolio stress simulation.
    """
    trigger_event = None
    if req.trigger_event_id:
        conn_res = event_service.get_events(search=req.trigger_event_id, limit=1)
        if conn_res["events"]:
            trigger_event = conn_res["events"][0]

    return stress_service.run_stress_test(
        scenario_id=req.scenario_id,
        custom_scenario=req.custom_scenario,
        trigger_event=trigger_event,
        severity_multiplier=req.severity_multiplier or 1.0
    )
