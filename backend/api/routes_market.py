from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from backend.services.market_intelligence_service import get_market_service

router = APIRouter(prefix="/api/market", tags=["Market Intelligence & Quantitative Forecasting"])
market_service = get_market_service()

@router.get("/companies")
def list_supported_companies():
    """
    Returns list of all monitored S&P index companies with sector metadata.
    """
    return market_service.get_supported_companies()

@router.get("/data/{symbol}")
def get_stock_ohlcv(symbol: str, days: int = Query(30, ge=5, le=365)):
    """
    Returns OHLCV price series, daily returns, and 7-day Moving Average (MA7).
    """
    try:
        data = market_service.load_from_db(symbol.upper(), days=days)
        return {
            "symbol": symbol.upper(),
            "count": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{symbol}")
def get_stock_summary(symbol: str):
    """
    Returns 52-week High/Low, average close, annualized volatility score, and top gain/loss trading days.
    """
    try:
        summary = market_service.get_stock_summary(symbol.upper())
        if not summary:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/{symbol}")
def get_monte_carlo_forecast(
    symbol: str,
    days: int = Query(14, ge=7, le=30),
    sentiment_guided: bool = Query(True, description="Condition drift on NLP Risk Engine sentiment")
):
    """
    Generates 100 Geometric Brownian Motion Monte Carlo simulation paths.
    Returns 95th percentile (Upper), 50th percentile (Median), and 5th percentile (Lower) probability cone.
    """
    try:
        return market_service.get_monte_carlo_forecast(symbol.upper(), days=days, sentiment_guided=sentiment_guided)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare")
def compare_stocks(
    symbol1: str = Query(..., description="First stock symbol"),
    symbol2: str = Query(..., description="Second stock symbol"),
    days: int = Query(30, ge=7, le=365)
):
    """
    Compares two stocks: Base-100 normalized trajectories + Pearson correlation of daily returns.
    """
    try:
        return market_service.compare_stocks(symbol1, symbol2, days=days)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/gainers-losers")
def get_gainers_losers():
    """
    Returns today's top 3 gainers and top 3 losers across all tracked assets.
    """
    try:
        return market_service.get_gainers_losers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh/{symbol}")
def refresh_stock_data(symbol: str):
    """
    Forces a fresh download and cache update from Yahoo Finance.
    """
    try:
        count = market_service.fetch_and_store(symbol.upper())
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "records_updated": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
