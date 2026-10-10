"""
FinSight AI — Dependency Injection Providers (FastAPI `Depends`)
Follows Dependency Inversion Principle (DIP), decoupling route handlers from service lifecycles.
"""

from fastapi import Depends
from backend.repositories.event_repository import EventRepository
from backend.repositories.portfolio_repository import PortfolioRepository
from backend.repositories.stress_repository import StressRepository
from backend.repositories.market_repository import MarketRepository
from backend.services.event_service import EventService
from backend.services.rebalance_service import RebalanceService
from backend.services.stress_test_service import StressTestService
from backend.services.market_intelligence_service import MarketIntelligenceService
from backend.services.metrics_service import MetricsService

# Repository Providers
def get_event_repository() -> EventRepository:
    return EventRepository()

def get_portfolio_repository() -> PortfolioRepository:
    return PortfolioRepository()

def get_stress_repository() -> StressRepository:
    return StressRepository()

def get_market_repository() -> MarketRepository:
    return MarketRepository()

# Service Providers
def get_event_service(
    repo: EventRepository = Depends(get_event_repository)
) -> EventService:
    return EventService(event_repo=repo)

def get_rebalance_service(
    portfolio_repo: PortfolioRepository = Depends(get_portfolio_repository),
    event_repo: EventRepository = Depends(get_event_repository)
) -> RebalanceService:
    return RebalanceService(portfolio_repo=portfolio_repo, event_repo=event_repo)

def get_stress_service(
    stress_repo: StressRepository = Depends(get_stress_repository)
) -> StressTestService:
    return StressTestService(stress_repo=stress_repo)

def get_market_service(
    market_repo: MarketRepository = Depends(get_market_repository),
    event_repo: EventRepository = Depends(get_event_repository)
) -> MarketIntelligenceService:
    return MarketIntelligenceService(market_repo=market_repo, event_repo=event_repo)

def get_metrics_service() -> MetricsService:
    return MetricsService()

from backend.services.ingestion_service import IngestionService

def get_ingestion_service(
    repo: EventRepository = Depends(get_event_repository)
) -> IngestionService:
    return IngestionService(event_repo=repo)
