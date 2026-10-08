from backend.api.routes_events import router as events_router
from backend.api.routes_portfolio import router as portfolio_router
from backend.api.routes_stress import router as stress_router
from backend.api.routes_metrics import router as metrics_router
from backend.api.routes_market import router as market_router

__all__ = ["events_router", "portfolio_router", "stress_router", "metrics_router", "market_router"]
