"""
FinSight AI — Market Intelligence Service (Business Logic Layer)
Fetches and caches market quotes via MarketRepository, runs Monte Carlo GBM forecasts, and computes Pearson correlations.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import yfinance as yf
from backend.repositories.market_repository import MarketRepository
from backend.repositories.event_repository import EventRepository
from backend.ml.entity_extractor import TICKER_MAP
from backend.core.security import validate_and_sanitize_ticker
from backend.core.exceptions import EntityNotFoundException, DomainValidationError

logger = logging.getLogger("finsight.market")

class MarketIntelligenceService:
    def __init__(
        self,
        market_repo: Optional[MarketRepository] = None,
        event_repo: Optional[EventRepository] = None
    ):
        self.market_repo = market_repo or MarketRepository()
        self.event_repo = event_repo or EventRepository()
        self.tickers = list(TICKER_MAP.keys())
        self.mock_symbols = set()

    def get_supported_companies(self) -> List[Dict[str, Any]]:
        return [
            {
                "ticker": sym,
                "name": data["name"],
                "sector": data["sector"]
            }
            for sym, data in TICKER_MAP.items()
        ]

    def fetch_and_store(self, symbol: str, period: str = "1y") -> int:
        """
        Downloads historical stock data via yfinance, computes returns + MA7, and caches via MarketRepository.
        Gracefully falls back to realistic deterministic synthetic generation if offline or rate-limited.
        """
        clean_symbol = validate_and_sanitize_ticker(symbol)
        df = pd.DataFrame()

        try:
            ticker_obj = yf.Ticker(clean_symbol)
            df = ticker_obj.history(period=period)
        except Exception as e:
            logger.warning(f"Market data fetch warning for {clean_symbol}: {e}")
            df = pd.DataFrame()

        data_source = "yfinance"

        if df.empty or len(df) < 5:
            data_source = "synthetic_cache"
            self.mock_symbols.add(clean_symbol)
            
            base_prices = {
                "AAPL": 182.50, "MSFT": 415.20, "NVDA": 875.00, "GOOGL": 155.40,
                "AMZN": 178.90, "JPM": 198.30, "BAC": 37.50, "V": 278.40,
                "JNJ": 152.10, "UNH": 482.00, "XOM": 118.60, "CVX": 156.20,
                "PG": 162.80, "TSLA": 175.40, "CAT": 345.00, "NEE": 68.20
            }
            seed_price = base_prices.get(clean_symbol, 150.0)
            np.random.seed(abs(hash(clean_symbol)) % 10000)

            dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
            prices = [seed_price]
            for _ in range(len(dates) - 1):
                pct = np.random.normal(0.0005, 0.018)
                prices.append(prices[-1] * (1 + pct))

            df = pd.DataFrame({
                "Date": dates,
                "Open": [p * (1 - np.random.uniform(-0.005, 0.005)) for p in prices],
                "High": [p * (1 + np.random.uniform(0.005, 0.025)) for p in prices],
                "Low": [p * (1 - np.random.uniform(0.005, 0.025)) for p in prices],
                "Close": prices,
                "Volume": np.random.randint(1_500_000, 25_000_000, len(dates))
            })

        df = df.reset_index()
        col_map = {c: c.lower() for c in df.columns}
        df.rename(columns=col_map, inplace=True)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        df = df[["date", "open", "high", "low", "close", "volume"]].copy()
        df.dropna(subset=["close"], inplace=True)

        df["daily_return"] = ((df["close"] - df["open"]) / df["open"] * 100).round(4)
        df["ma7"] = df["close"].rolling(window=7, min_periods=1).mean().round(2)
        df["symbol"] = clean_symbol
        df["data_source"] = data_source

        return self.market_repo.save_ohlcv_dataframe(df, clean_symbol, data_source)

    def load_from_db(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        clean_symbol = validate_and_sanitize_ticker(symbol)
        count = self.market_repo.count_records_for_symbol(clean_symbol)
        if count == 0:
            self.fetch_and_store(clean_symbol)

        return self.market_repo.get_ohlcv(clean_symbol, days=days)

    def get_stock_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Calculates 52-week High/Low, average price, annualized volatility score, and top gain/loss days.
        """
        clean_symbol = validate_and_sanitize_ticker(symbol)
        rows = self.load_from_db(clean_symbol, days=365)
        if not rows:
            raise EntityNotFoundException(f"No pricing history available for {clean_symbol}", entity_type="Stock", entity_id=clean_symbol)

        df = pd.DataFrame(rows)
        volatility = round(float(df["daily_return"].std() * np.sqrt(252)), 2) if len(df) > 1 else 0.0

        top3_best = df.nlargest(3, "daily_return")[["date", "close", "daily_return"]].to_dict("records")
        top3_worst = df.nsmallest(3, "daily_return")[["date", "close", "daily_return"]].to_dict("records")

        company_info = TICKER_MAP.get(clean_symbol, {"name": clean_symbol, "sector": "Broad Market"})

        return {
            "symbol": clean_symbol,
            "name": company_info["name"],
            "sector": company_info["sector"],
            "current_price": round(float(df["close"].iloc[-1]), 2),
            "high_52w": round(float(df["high"].max()), 2),
            "low_52w": round(float(df["low"].min()), 2),
            "avg_close": round(float(df["close"].mean()), 2),
            "volatility_score": volatility,
            "top_3_best_days": top3_best,
            "top_3_worst_days": top3_worst,
            "data_source": df["data_source"].iloc[-1] if "data_source" in df.columns else "yfinance"
        }

    def get_monte_carlo_forecast(
        self,
        symbol: str,
        days: int = 14,
        sentiment_guided: bool = True
    ) -> Dict[str, Any]:
        """
        Simulates 100 Geometric Brownian Motion paths:
        S(t+1) = S(t) * exp((mu - sigma^2 / 2) + sigma * epsilon)
        Optionally conditions the drift mu on the NLP Risk Engine sentiment score.
        """
        clean_symbol = validate_and_sanitize_ticker(symbol)
        if days < 7 or days > 30:
            raise DomainValidationError("Forecast horizon must be between 7 and 30 days.", field="days")

        rows = self.load_from_db(clean_symbol, days=60)
        if len(rows) < 10:
            raise DomainValidationError(f"Insufficient historical pricing data for {clean_symbol} to simulate paths.")

        df = pd.DataFrame(rows)
        closes = df["close"].values
        returns = np.diff(closes) / closes[:-1]

        mu = float(np.mean(returns))
        sigma = float(np.std(returns))

        sentiment_shift = 0.0
        if sentiment_guided:
            ev_rows = self.event_repo.get_recent_events_for_ticker(clean_symbol, limit=5)
            if ev_rows:
                avg_sent = sum(r["sentiment_score"] for r in ev_rows) / len(ev_rows)
                avg_imp = sum(r["impact_score"] for r in ev_rows) / len(ev_rows)
                sentiment_shift = avg_sent * (avg_imp / 10.0) * 0.003
                mu += sentiment_shift

        last_price = float(closes[-1])
        last_date = pd.to_datetime(df["date"].iloc[-1])

        num_simulations = 100
        np.random.seed(42)
        simulations = []

        for _ in range(num_simulations):
            prices = [last_price]
            for _ in range(days):
                eps = np.random.normal(0, 1)
                p = prices[-1] * np.exp((mu - (sigma**2) / 2) + sigma * eps)
                prices.append(float(p))
            simulations.append(prices)

        sim_array = np.array(simulations)
        upper_bound = np.percentile(sim_array, 95, axis=0)
        median_path = np.percentile(sim_array, 50, axis=0)
        lower_bound = np.percentile(sim_array, 5, axis=0)

        future_dates = [last_date.strftime("%Y-%m-%d")]
        curr_dt = last_date + pd.Timedelta(days=1)
        while len(future_dates) < days + 1:
            if curr_dt.weekday() < 5:
                future_dates.append(curr_dt.strftime("%Y-%m-%d"))
            curr_dt += pd.Timedelta(days=1)

        forecast_points = []
        for i, dt in enumerate(future_dates):
            forecast_points.append({
                "date": dt,
                "upper": round(float(upper_bound[i]), 2),
                "median": round(float(median_path[i]), 2),
                "lower": round(float(lower_bound[i]), 2)
            })

        return {
            "symbol": clean_symbol,
            "days": days,
            "last_price": round(float(last_price), 2),
            "historical_volatility": round(float(sigma * np.sqrt(252)), 4),
            "sentiment_guided": sentiment_guided,
            "sentiment_drift_boost": round(float(sentiment_shift * 100), 4),
            "forecast": forecast_points
        }

    def compare_stocks(self, symbol1: str, symbol2: str, days: int = 30) -> Dict[str, Any]:
        """
        Compares two stocks: Base-100 normalized trajectories + Pearson correlation of daily returns.
        """
        s1 = validate_and_sanitize_ticker(symbol1)
        s2 = validate_and_sanitize_ticker(symbol2)
        if s1 == s2:
            raise DomainValidationError("Cannot compare stock against itself. Select distinct symbols.", field="symbol2")

        d1 = pd.DataFrame(self.load_from_db(s1, days=days)).set_index("date")
        d2 = pd.DataFrame(self.load_from_db(s2, days=days)).set_index("date")

        if d1.empty or d2.empty:
            raise EntityNotFoundException("Insufficient pricing data to compare selected symbols.")

        common_dates = sorted(list(set(d1.index) & set(d2.index)))
        if not common_dates:
            raise DomainValidationError("No overlapping trading dates found between selected symbols.")

        d1_common = d1.loc[common_dates]
        d2_common = d2.loc[common_dates]

        corr = round(float(d1_common["daily_return"].corr(d2_common["daily_return"])), 4)

        base1 = d1_common["close"].iloc[0]
        base2 = d2_common["close"].iloc[0]

        comparison_series = []
        for dt in common_dates:
            p1 = d1_common.loc[dt, "close"]
            p2 = d2_common.loc[dt, "close"]
            comparison_series.append({
                "date": dt,
                f"{s1}_norm": round(float(p1 / base1 * 100), 2),
                f"{s2}_norm": round(float(p2 / base2 * 100), 2),
                f"{s1}_price": round(float(p1), 2),
                f"{s2}_price": round(float(p2), 2)
            })

        ret1 = round(float((d1_common["close"].iloc[-1] / base1 - 1) * 100), 2)
        ret2 = round(float((d2_common["close"].iloc[-1] / base2 - 1) * 100), 2)

        return {
            "symbol1": s1,
            "symbol2": s2,
            "days": days,
            "correlation": corr,
            "return1_pct": ret1,
            "return2_pct": ret2,
            "series": comparison_series
        }

    def get_gainers_losers(self) -> Dict[str, Any]:
        """
        Returns top 3 gainers and top 3 losers based on latest recorded daily return.
        """
        summaries = []
        for sym in self.tickers:
            rows = self.load_from_db(sym, days=5)
            if rows:
                latest = rows[-1]
                summaries.append({
                    "symbol": sym,
                    "name": TICKER_MAP[sym]["name"],
                    "sector": TICKER_MAP[sym]["sector"],
                    "close": latest["close"],
                    "daily_return": latest["daily_return"]
                })

        if not summaries:
            return {"gainers": [], "losers": []}

        df = pd.DataFrame(summaries)
        gainers = df.nlargest(3, "daily_return").to_dict("records")
        losers = df.nsmallest(3, "daily_return").to_dict("records")

        return {
            "gainers": gainers,
            "losers": losers
        }

# Factory function for Dependency Injection
def get_market_service() -> MarketIntelligenceService:
    return MarketIntelligenceService()
