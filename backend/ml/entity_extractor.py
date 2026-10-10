"""
FinSight AI — Evidence-Based Entity & Ticker Extractor
Identifies mentioned public companies, stock tickers, and economic sectors.
Guarantees:
- Evidence-based identification only: never defaults arbitrary text to SPY.
- Cashtags ($NVDA) take highest precedence.
- High-precision filtering to avoid false positives on short words (e.g. 'V', 'A', 'IT').
- Clean empty outputs when no entities are present.
"""

import re
from typing import List, Dict, Any, Tuple

TICKER_MAP = {
    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Technology",
        "keywords": ["apple", "iphone", "tim cook", "ios", "macbook", "app store", "ipad"]
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "keywords": ["microsoft", "azure", "copilot", "satya nadella", "windows"]
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "keywords": ["nvidia", "jensen huang", "blackwell", "h100", "h200", "geforce", "gpu", "cuda"]
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "keywords": ["google", "alphabet", "gemini", "sundar pichai", "youtube", "android", "waymo"]
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "sector": "Consumer Discretionary",
        "keywords": ["amazon", "aws", "andy jassy", "prime", "e-commerce"]
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "sector": "Financials",
        "keywords": ["jpmorgan", "chase", "jamie dimon", "investment bank", "j.p. morgan"]
    },
    "BAC": {
        "name": "Bank of America Corp",
        "sector": "Financials",
        "keywords": ["bank of america", "bofa", "brian moynihan", "merrill lynch"]
    },
    "V": {
        "name": "Visa Inc.",
        "sector": "Financials",
        "keywords": ["visa inc", "visa payment", "visa card", "visa network"]
    },
    "JNJ": {
        "name": "Johnson & Johnson",
        "sector": "Healthcare",
        "keywords": ["johnson & johnson", "j&j", "medtech", "oncology", "pharma"]
    },
    "UNH": {
        "name": "UnitedHealth Group Inc.",
        "sector": "Healthcare",
        "keywords": ["unitedhealth", "optum", "managed care", "health insurer"]
    },
    "XOM": {
        "name": "Exxon Mobil Corporation",
        "sector": "Energy",
        "keywords": ["exxon", "exxonmobil", "darren woods", "permian", "crude oil"]
    },
    "CVX": {
        "name": "Chevron Corporation",
        "sector": "Energy",
        "keywords": ["chevron", "mike wirth", "lng", "refinery"]
    },
    "PG": {
        "name": "Procter & Gamble Co.",
        "sector": "Consumer Staples",
        "keywords": ["procter & gamble", "p&g", "tide", "pampers", "gillette"]
    },
    "TSLA": {
        "name": "Tesla Inc.",
        "sector": "Consumer Discretionary",
        "keywords": ["tesla", "elon musk", "gigafactory", "cybertruck", "model y", "model 3", "ev maker"]
    },
    "CAT": {
        "name": "Caterpillar Inc.",
        "sector": "Industrials",
        "keywords": ["caterpillar inc", "caterpillar machinery", "excavators", "mining equipment"]
    },
    "NEE": {
        "name": "NextEra Energy Inc.",
        "sector": "Utilities",
        "keywords": ["nextera", "fpl", "clean energy", "wind farm", "solar utility"]
    }
}

SECTOR_MAP = {
    "Technology": ["semiconductor", "chip", "chips", "cloud", "software", "ai", "hardware", "cybersecurity"],
    "Financials": ["bank", "fed", "federal reserve", "interest rate", "loan", "yield", "credit", "treasury", "bonds"],
    "Energy": ["crude", "oil", "opec", "refinery", "petroleum", "natural gas", "pipeline", "brent"],
    "Healthcare": ["fda", "drug", "clinical", "biotech", "hospital", "pharma", "vaccine", "cancer"],
    "Consumer Discretionary": ["retail", "consumer spending", "ev", "auto", "e-commerce", "vehicles", "vehicle"],
    "Consumer Staples": ["household", "grocery", "food", "packaged goods"],
    "Industrials": ["machinery", "defense", "freight", "aerospace", "transport", "logistics"],
    "Utilities": ["power grid", "renewable", "solar", "wind", "electric utility"]
}

# Tickers that are short (<=3 chars) or common English words that should ONLY be matched
# via cashtags ($) or verified company context, never raw uppercase text
AMBIGUOUS_TICKERS = {"V", "CAT"}

class EntityExtractor:
    def __init__(self):
        self.ticker_map = TICKER_MAP
        self.sector_map = SECTOR_MAP

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extracts verified tickers, companies, and inferred sector from text.
        Returns empty lists when no entity evidence is present.
        """
        if not text or not str(text).strip():
            return {"tickers": [], "companies": [], "sector": "Broad Market"}

        text_str = str(text).strip()
        text_lower = text_str.lower()
        matched_tickers = set()

        # 1. Regex for explicit stock cashtags (e.g. $NVDA, $AAPL, $V)
        cashtags = re.findall(r'\$([A-Z]{1,5})\b', text_str)
        for tag in cashtags:
            if tag in self.ticker_map:
                matched_tickers.add(tag)

        # 2. Check for company name and explicit keywords (case-insensitive)
        for ticker, data in self.ticker_map.items():
            if ticker in matched_tickers:
                continue
            for kw in data["keywords"]:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    matched_tickers.add(ticker)
                    break

        # 3. Check for standalone uppercase ticker words (excluding ambiguous short words)
        words = re.findall(r'\b[A-Z]{2,5}\b', text_str)
        for w in words:
            if w in self.ticker_map and w not in AMBIGUOUS_TICKERS:
                matched_tickers.add(w)

        ticker_list = sorted(list(matched_tickers))

        # 4. Determine primary sector
        primary_sector = "Broad Market"
        if ticker_list:
            primary_sector = self.ticker_map[ticker_list[0]]["sector"]
        else:
            # Fallback to sector keywords
            for sector, kws in self.sector_map.items():
                if any(re.search(r'\b' + re.escape(k) + r'\b', text_lower) for k in kws):
                    primary_sector = sector
                    break

        company_names = [self.ticker_map[t]["name"] for t in ticker_list]

        return {
            "tickers": ticker_list,
            "companies": company_names,
            "sector": primary_sector
        }
