from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.services.stress_test_service import StressTestService
from backend.services.event_service import EventService
from backend.models.schemas import StressTestRequest

router = APIRouter(prefix="/api/stress-tests", tags=["Strategic Stress Testing"])
stress_service = StressTestService()
event_service = EventService()

@router.get("")
def get_stress_history(limit: int = Query(20, ge=1, le=50)):
    """
    Returns history of wholesale portfolio stress tests.
    """
    return stress_service.get_history(limit=limit)

@router.get("/scenarios")
def get_stress_scenarios():
    """
    Returns available wholesale banking stress test scenarios.
    """
    return stress_service.get_scenarios()

@router.get("/portfolio")
def get_wholesale_portfolio():
    """
    Returns the baseline wholesale multi-asset portfolio breakdown.
    """
    return stress_service.get_wholesale_portfolio()

@router.post("/run")
def run_stress_test(req: StressTestRequest):
    """
    MODULE B: Executes strategic multi-asset portfolio stress simulation.
    """
    trigger_event = None
    if req.trigger_event_id:
        conn_res = event_service.get_events(search=req.trigger_event_id, limit=1)
        if conn_res["events"]:
            trigger_event = conn_res["events"][0]

    try:
        result = stress_service.run_stress_test(
            scenario_id=req.scenario_id,
            custom_scenario=req.custom_scenario,
            trigger_event=trigger_event,
            severity_multiplier=req.severity_multiplier or 1.0
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
