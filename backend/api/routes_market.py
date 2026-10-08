"""
FinSight AI — Market Intelligence & Quantitative Forecasting API Router
Provides technical indicators, Monte Carlo stochastic projections, and Pearson correlation matrices with Dependency Injection.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, Path, Depends
from backend.services.market_intelligence_service import MarketIntelligenceService
from backend.api.deps import get_market_service

router = APIRouter(prefix="/api/market", tags=["Market Intelligence & Quantitative Forecasting"])

@router.get("/companies")
def list_supported_companies(
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Returns list of monitored S&P index companies with sector metadata.
    """
    return market_service.get_supported_companies()

@router.get("/data/{symbol}")
def get_stock_ohlcv(
    symbol: str = Path(..., pattern=r"^[A-Za-z0-9\.\^]{1,10}$", description="Stock ticker symbol"),
    days: int = Query(30, ge=5, le=365),
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Returns OHLCV price series, daily returns, and 7-day Moving Average (MA7).
    """
    data = market_service.load_from_db(symbol.upper(), days=days)
    return {
        "symbol": symbol.upper(),
        "count": len(data),
        "data": data
    }

@router.get("/summary/{symbol}")
def get_stock_summary(
    symbol: str = Path(..., pattern=r"^[A-Za-z0-9\.\^]{1,10}$", description="Stock ticker symbol"),
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Returns 52-week High/Low, average close, annualized volatility score, and tail-risk trading days.
    """
    return market_service.get_stock_summary(symbol.upper())

@router.get("/forecast/{symbol}")
def get_monte_carlo_forecast(
    symbol: str = Path(..., pattern=r"^[A-Za-z0-9\.\^]{1,10}$", description="Stock ticker symbol"),
    days: int = Query(14, ge=7, le=30),
    sentiment_guided: bool = Query(True, description="Condition drift on NLP Risk Engine sentiment"),
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Generates 100 Geometric Brownian Motion Monte Carlo simulation paths.
    Returns 95th percentile (Upper), 50th percentile (Median), and 5th percentile (Lower) probability cone.
    """
    return market_service.get_monte_carlo_forecast(symbol.upper(), days=days, sentiment_guided=sentiment_guided)

@router.get("/compare")
def compare_stocks(
    symbol1: str = Query(..., pattern=r"^[A-Za-z0-9\.\^]{1,10}$", description="First stock symbol"),
    symbol2: str = Query(..., pattern=r"^[A-Za-z0-9\.\^]{1,10}$", description="Second stock symbol"),
    days: int = Query(30, ge=7, le=365),
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Compares two stocks: Base-100 normalized trajectories + Pearson correlation of daily returns.
    """
    return market_service.compare_stocks(symbol1, symbol2, days=days)

@router.get("/gainers-losers")
def get_gainers_losers(
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Returns today's top 3 gainers and top 3 losers across tracked assets.
    """
    return market_service.get_gainers_losers()

@router.post("/refresh/{symbol}")
def refresh_stock_data(
    symbol: str = Path(..., pattern=r"^[A-Za-z0-9\.\^]{1,10}$", description="Stock ticker symbol"),
    market_service: MarketIntelligenceService = Depends(get_market_service)
):
    """
    Forces a fresh download and cache update from Yahoo Finance.
    """
    count = market_service.fetch_and_store(symbol.upper())
    return {
        "status": "success",
        "symbol": symbol.upper(),
        "records_updated": count
    }
