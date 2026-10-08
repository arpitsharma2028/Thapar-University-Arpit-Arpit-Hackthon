from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.services.rebalance_service import RebalanceService
from backend.services.event_service import EventService
from backend.models.schemas import RebalanceRequest, BatchSimulateRequest

router = APIRouter(tags=["Portfolio & Tactical Rebalancer"])
rebalance_service = RebalanceService()
event_service = EventService()

@router.get("/api/portfolio")
def get_portfolio():
    """
    Returns current index portfolio positions, weights, and aggregate sentiment.
    """
    try:
        return rebalance_service.get_current_portfolio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/portfolio/rebalance")
def execute_rebalance(req: RebalanceRequest):
    """
    MODULE A: Dynamically rebalances portfolio weights based on a risk signal.
    """
    trigger_event = {
        "event_id": req.event_id or "MANUAL-TRIGGER",
        "headline": req.headline or "Manual Risk Signal",
        "tickers": req.tickers or "",
        "sector": req.sector or "Broad Market",
        "sentiment_score": req.sentiment_score,
        "impact_score": req.impact_score
    }
    try:
        return rebalance_service.rebalance(trigger_event, req.sensitivity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/portfolio/simulate")
def simulate_events(req: Optional[BatchSimulateRequest] = None):
    """
    Simulates rebalancing against either 1 next event or a batch of N events.
    """
    count = req.num_events if req else 1
    sens = req.sensitivity if req else 0.025
    results = []

    for _ in range(count):
        evt = event_service.get_next_simulation_event()
        if not evt:
            break
        reb_res = rebalance_service.rebalance(evt, sensitivity=sens)
        results.append({
            "event_id": evt.get("event_id"),
            "headline": evt.get("headline"),
            "sentiment": evt.get("sentiment_score"),
            "impact": evt.get("impact_score"),
            "value_change": reb_res.get("value_change"),
            "portfolio_value_after": reb_res.get("portfolio_value_after")
        })

    current_portfolio = rebalance_service.get_current_portfolio()
    return {
        "status": "success",
        "events_simulated": len(results),
        "steps": results,
        "current_portfolio": current_portfolio
    }

@router.get("/api/rebalance-history")
def get_rebalance_history(limit: int = Query(50, ge=1, le=100)):
    """
    Returns complete chronological audit log of portfolio rebalancing decisions.
    """
    return rebalance_service.get_history(limit=limit)

@router.post("/api/portfolio/reset")
def reset_portfolio():
    """
    Resets portfolio allocations back to initial baseline target weights.
    """
    return rebalance_service.reset_portfolio()
