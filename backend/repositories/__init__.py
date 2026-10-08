"""
FinSight AI — Repositories Module
Exports Repository implementations for Dependency Injection.
"""

from backend.repositories.base import BaseRepository
from backend.repositories.event_repository import EventRepository
from backend.repositories.portfolio_repository import PortfolioRepository
from backend.repositories.stress_repository import StressRepository
from backend.repositories.market_repository import MarketRepository

__all__ = [
    "BaseRepository",
    "EventRepository",
    "PortfolioRepository",
    "StressRepository",
    "MarketRepository",
]
