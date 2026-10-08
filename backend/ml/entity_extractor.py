import re
from typing import List, Dict, Any, Tuple

# Comprehensive mapping of tickers to companies and sectors
TICKER_MAP = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "keywords": ["apple", "iphone", "tim cook", "ios", "macbook", "app store"]},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "keywords": ["microsoft", "azure", "copilot", "satya nadella", "windows"]},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "keywords": ["nvidia", "jensen huang", "blackwell", "h100", "h200", "geforce", "gpu"]},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Communication Services", "keywords": ["google", "alphabet", "gemini", "sundar pichai", "youtube", "android"]},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "keywords": ["amazon", "aws", "andy jassy", "prime", "e-commerce"]},
    "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Financials", "keywords": ["jpmorgan", "chase", "jamie dimon", "investment bank"]},
    "BAC": {"name": "Bank of America Corp", "sector": "Financials", "keywords": ["bank of america", "bofa", "brian moynihan", "merrill lynch"]},
    "V": {"name": "Visa Inc.", "sector": "Financials", "keywords": ["visa", "credit card", "payment network", "interchange"]},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare", "keywords": ["johnson & johnson", "j&j", "medtech", "oncology", "pharma"]},
    "UNH": {"name": "UnitedHealth Group Inc.", "sector": "Healthcare", "keywords": ["unitedhealth", "optum", "managed care", "health insurer"]},
    "XOM": {"name": "Exxon Mobil Corporation", "sector": "Energy", "keywords": ["exxon", "exxonmobil", "darren woods", "permian", "crude oil"]},
    "CVX": {"name": "Chevron Corporation", "sector": "Energy", "keywords": ["chevron", "mike wirth", "lng", "refinery"]},
    "PG": {"name": "Procter & Gamble Co.", "sector": "Consumer Staples", "keywords": ["procter & gamble", "p&g", "tide", "pampers", "gillette"]},
    "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Discretionary", "keywords": ["tesla", "elon musk", "gigafactory", "cybertruck", "model y", "ev"]},
    "CAT": {"name": "Caterpillar Inc.", "sector": "Industrials", "keywords": ["caterpillar", "heavy machinery", "excavators", "mining equipment"]},
    "NEE": {"name": "NextEra Energy Inc.", "sector": "Utilities", "keywords": ["nextera", "fpl", "clean energy", "wind farm", "solar utility"]}
}

SECTOR_MAP = {
    "Technology": ["semiconductor", "chip", "cloud", "software", "ai", "hardware", "cybersecurity"],
    "Financials": ["bank", "fed", "interest rate", "loan", "yield", "credit", "treasury", "bonds"],
    "Energy": ["crude", "oil", "opec", "refinery", "petroleum", "natural gas", "pipeline"],
    "Healthcare": ["fda", "drug", "clinical", "biotech", "hospital", "pharma", "vaccine", "cancer"],
    "Consumer Discretionary": ["retail", "consumer spending", "ev", "auto", "e-commerce"],
    "Consumer Staples": ["household", "grocery", "food", "packaged goods"],
    "Industrials": ["machinery", "defense", "freight", "aerospace", "transport", "logistics"],
    "Utilities": ["power grid", "renewable", "solar", "wind", "electric utility"]
}

class EntityExtractor:
    def __init__(self):
        self.ticker_map = TICKER_MAP
        self.sector_map = SECTOR_MAP

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extracts mentioned tickers, companies, and inferred sector from text.
        """
        text_lower = text.lower()
        matched_tickers = set()
        
        # 1. Regex for explicit stock cashtags (e.g. $NVDA) or raw uppercase ticker matches
        cashtags = re.findall(r'\$([A-Z]{1,5})\b', text)
        for tag in cashtags:
            if tag in self.ticker_map:
                matched_tickers.add(tag)

        # 2. Check for ticker tokens bounded by words
        words = re.findall(r'\b[A-Z]{1,5}\b', text)
        for w in words:
            if w in self.ticker_map:
                matched_tickers.add(w)

        # 3. Check for company name and keyword matches
        for ticker, data in self.ticker_map.items():
            if ticker in matched_tickers:
                continue
            for kw in data["keywords"]:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    matched_tickers.add(ticker)
                    break

        ticker_list = sorted(list(matched_tickers))
        
        # Determine primary sector
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
            "tickers": ticker_list if ticker_list else ["SPY"],
            "companies": company_names if company_names else ["S&P 500 Index"],
            "sector": primary_sector
        }
