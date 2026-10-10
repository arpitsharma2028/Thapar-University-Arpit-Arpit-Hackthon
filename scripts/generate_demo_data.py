"""
FinSight AI — Demo Data Generator
Generates realistic, deterministic demo data for S&P Global & CRISIL Campus Hackathon 2026.
Creates:
- data/companies.csv
- data/portfolio.csv
- data/news_events.csv
- data/social_events.csv
- data/market_data.csv
- data/stress_scenarios.json
"""

import os
import sys
import json
import random
import pandas as pd
from datetime import datetime, timedelta

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set deterministic seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 1. COMPANIES DATASET (16 Public Companies across major sectors)
COMPANIES = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "base_weight": 0.085, "beta": 1.15, "market_cap_b": 2850.0},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software & Cloud", "base_weight": 0.085, "beta": 1.10, "market_cap_b": 2980.0},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "base_weight": 0.080, "beta": 1.72, "market_cap_b": 2200.0},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "industry": "Interactive Media", "base_weight": 0.075, "beta": 1.08, "market_cap_b": 2100.0},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "industry": "E-Commerce & Cloud", "base_weight": 0.075, "beta": 1.20, "market_cap_b": 1850.0},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials", "industry": "Diversified Banking", "base_weight": 0.070, "beta": 0.95, "market_cap_b": 570.0},
    {"ticker": "BAC", "name": "Bank of America Corp", "sector": "Financials", "industry": "Commercial Banking", "base_weight": 0.055, "beta": 1.05, "market_cap_b": 290.0},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financials", "industry": "Payment Processing", "base_weight": 0.060, "beta": 0.92, "market_cap_b": 550.0},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals", "base_weight": 0.055, "beta": 0.65, "market_cap_b": 380.0},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare", "industry": "Managed Healthcare", "base_weight": 0.060, "beta": 0.70, "market_cap_b": 440.0},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Integrated Oil & Gas", "base_weight": 0.065, "beta": 0.88, "market_cap_b": 480.0},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Integrated Oil & Gas", "base_weight": 0.050, "beta": 0.85, "market_cap_b": 280.0},
    {"ticker": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples", "industry": "Household Products", "base_weight": 0.055, "beta": 0.55, "market_cap_b": 375.0},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary", "industry": "Automotive & Clean Tech", "base_weight": 0.050, "beta": 2.10, "market_cap_b": 560.0},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "industry": "Heavy Machinery", "base_weight": 0.045, "beta": 1.12, "market_cap_b": 170.0},
    {"ticker": "NEE", "name": "NextEra Energy Inc.", "sector": "Utilities", "industry": "Renewable Energy", "base_weight": 0.040, "beta": 0.60, "market_cap_b": 150.0}
]

def generate_companies_csv():
    df = pd.DataFrame(COMPANIES)
    # Ensure weights sum exactly to 1.00
    df['base_weight'] = df['base_weight'] / df['base_weight'].sum()
    df.to_csv(os.path.join(DATA_DIR, "companies.csv"), index=False)
    print("[OK] Created companies.csv")
    return df

def generate_portfolio_csv(companies_df):
    total_portfolio_value = 10_000_000.0  # $10 Million Portfolio
    records = []
    
    # Prices roughly calibrated
    base_prices = {
        "AAPL": 182.50, "MSFT": 415.20, "NVDA": 875.00, "GOOGL": 155.40,
        "AMZN": 178.90, "JPM": 198.30, "BAC": 37.50, "V": 278.40,
        "JNJ": 152.10, "UNH": 482.00, "XOM": 118.60, "CVX": 156.20,
        "PG": 162.80, "TSLA": 175.40, "CAT": 345.00, "NEE": 68.20
    }
    
    for _, row in companies_df.iterrows():
        ticker = row['ticker']
        weight = row['base_weight']
        allocated_val = total_portfolio_value * weight
        price = base_prices.get(ticker, 100.0)
        shares = round(allocated_val / price)
        actual_val = shares * price
        records.append({
            "ticker": ticker,
            "name": row['name'],
            "sector": row['sector'],
            "target_weight": round(weight, 4),
            "current_weight": round(weight, 4),
            "shares": shares,
            "current_price": price,
            "position_value": round(actual_val, 2),
            "last_rebalanced": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    df = pd.DataFrame(records)
    # Recalculate exact current_weight from position_value
    tot = df['position_value'].sum()
    df['current_weight'] = (df['position_value'] / tot).round(4)
    df.to_csv(os.path.join(DATA_DIR, "portfolio.csv"), index=False)
    print("[OK] Created portfolio.csv")
    return df

# 2. RAW NEWS EVENTS (Financial News Ingestion Source)
NEWS_TEMPLATES = [
    # Geopolitical
    ("Middle East shipping tensions escalate as naval patrols reroute tankers away from key straits; crude supply disruptions loom.", "Geopolitical", -0.72, 8.5, ["XOM", "CVX"], "Energy", "Reuters"),
    ("US-China bilateral trade negotiations reach surprise preliminary consensus on critical green technology tariffs.", "Geopolitical", 0.65, 7.2, ["TSLA", "NEE", "CAT"], "Industrials", "Bloomberg"),
    ("NATO allies increase defense infrastructure commitments; cybersecurity procurement fast-tracked for major tech vendors.", "Geopolitical", 0.58, 6.8, ["MSFT", "GOOGL"], "Technology", "Financial Times"),
    ("Export restrictions tightened on advanced AI semiconductor packaging equipment targeting foreign foundries.", "Geopolitical", -0.68, 8.8, ["NVDA", "AAPL"], "Technology", "Wall Street Journal"),

    # Macroeconomic
    ("Federal Reserve signals prolonged benchmark rate plateau as sticky core inflation defies central bank forecasts.", "Macroeconomic", -0.55, 7.5, ["JPM", "BAC", "V"], "Financials", "Bloomberg"),
    ("US GDP annualized growth expands at an unexpected 3.1% driven by resilient consumer spending and corporate productivity.", "Macroeconomic", 0.78, 6.9, ["AMZN", "PG", "CAT"], "Consumer Discretionary", "CNBC"),
    ("Treasury yield curve steepens sharply as bond auction demand softens amid elevated sovereign debt issuance.", "Macroeconomic", -0.48, 6.5, ["JPM", "BAC", "NEE"], "Financials", "Reuters"),
    ("Global supply chain index normalizes to 5-year low, dramatically reducing freight and inventory handling costs.", "Macroeconomic", 0.62, 5.8, ["AAPL", "AMZN", "CAT"], "Technology", "Barron's"),

    # Credit & Debt
    ("Major corporate debt refinancing costs drop 35 bps as investment grade credit spreads narrow to cyclical lows.", "Credit", 0.64, 6.0, ["JPM", "BAC"], "Financials", "Moody's Analytics"),
    ("Commercial real estate loan delinquency rates tick higher in downtown metro portfolios, pressuring regional credit reserves.", "Credit", -0.71, 7.8, ["BAC", "JPM"], "Financials", "S&P Global Market Intelligence"),
    ("Municipal bond issuer upgrades outpace downgrades 3-to-1, boosting municipal infrastructure utility financing.", "Credit", 0.52, 4.8, ["NEE"], "Utilities", "Crisil Market Wire"),

    # Earnings & Financial Performance
    ("NVIDIA smashes quarterly revenue expectations with 260% data center revenue surge; raises next-quarter margin guidance.", "Earnings", 0.94, 9.2, ["NVDA"], "Technology", "Dow Jones"),
    ("Apple reports record Services revenue exceeding $24B, offsetting minor iPhone hardware saturation headwinds in Asia.", "Earnings", 0.68, 7.1, ["AAPL"], "Technology", "Bloomberg"),
    ("Tesla automotive gross margins contract below 16% due to aggressive EV discounting amid heightened competition.", "Earnings", -0.75, 7.9, ["TSLA"], "Consumer Discretionary", "Wall Street Journal"),
    ("JPMorgan posts record net interest income and raises full-year guidance on commercial loan growth.", "Earnings", 0.81, 7.4, ["JPM"], "Financials", "Financial Times"),
    ("Exxon Mobil delivers robust free cash flow and boosts quarterly dividend following productive Permian basin integration.", "Earnings", 0.72, 6.5, ["XOM"], "Energy", "Reuters"),
    ("Johnson & Johnson beats consensus EPS on solid oncology pharmaceutical sales and MedTech robotic device traction.", "Earnings", 0.61, 5.9, ["JNJ"], "Healthcare", "CNBC"),

    # Regulatory & Antitrust
    ("Department of Justice antitrust ruling mandates major cloud service interoperability and data portability compliance.", "Regulatory", -0.62, 8.1, ["GOOGL", "MSFT", "AMZN"], "Technology", "Politico Pro"),
    ("FDA grants accelerated breakthrough therapy designation for breakthrough monoclonal antibody in lung cancer trial.", "Regulatory", 0.85, 7.8, ["JNJ", "UNH"], "Healthcare", "BioPharma Dive"),
    ("Consumer Financial Protection Bureau issues cap on credit card late fees, denting unsecured consumer lending profitability.", "Regulatory", -0.58, 6.9, ["BAC", "JPM", "V"], "Financials", "American Banker"),
    ("EPA announces sweeping tax incentives and expedited permits for large-scale utility battery storage installations.", "Regulatory", 0.74, 6.7, ["NEE"], "Utilities", "Energy Daily"),

    # Product Launch & Innovation
    ("Microsoft unveils next-generation enterprise Copilot agents with automated reasoning and autonomous workflow execution.", "Product Launch", 0.88, 8.4, ["MSFT"], "Technology", "TechCrunch"),
    ("Alphabet reveals Gemini Ultra multimodal model leading competitive benchmarks in quantitative and coding evaluations.", "Product Launch", 0.82, 8.0, ["GOOGL"], "Technology", "VentureBeat"),
    ("Amazon Web Services launches custom AI acceleration silicon chips claiming 40% cost reduction vs competitors.", "Product Launch", 0.79, 7.6, ["AMZN"], "Technology", "AWS Press"),
    ("Apple announces Vision spatial computing commercial expansion into medical diagnostics and aviation training.", "Product Launch", 0.64, 6.2, ["AAPL"], "Technology", "The Verge"),

    # Market Dynamics & Volatility
    ("Tech sector experiences heavy intraday rotational selling as hedge funds de-gross mega-cap long exposure.", "Market", -0.60, 7.2, ["NVDA", "MSFT", "AAPL", "GOOGL"], "Technology", "MarketWatch"),
    ("Safe haven flight accelerates; utility and healthcare defensive dividend yields attract multi-billion institutional inflows.", "Market", 0.55, 6.1, ["PG", "JNJ", "NEE"], "Defensive", "Institutional Investor"),
    ("Energy sector rallies as Brent crude crosses $92/barrel driven by surprise OPEC+ output quota extension.", "Market", 0.76, 7.3, ["XOM", "CVX"], "Energy", "OilPrice.com"),

    # Mergers & Acquisitions
    ("Caterpillar announces accretive strategic acquisition of autonomous mining robotics pioneer for $2.4B.", "Merger/Acquisition", 0.71, 7.0, ["CAT"], "Industrials", "DealReporter"),
    ("Regulatory scrutiny intensifies over proposed health insurance tech consolidation, clouding deal closure certainty.", "Merger/Acquisition", -0.54, 6.6, ["UNH"], "Healthcare", "Modern Healthcare")
]

# 3. SOCIAL MEDIA EVENTS (Retail & Sentiment Momentum Ingestion Source)
SOCIAL_TEMPLATES = [
    ("🚨 $NVDA orders for H200 and Blackwell chips are backed up 18 months. Absolute money printer. Buying more calls at open! 🚀🔥", "Earnings", 0.92, 7.9, ["NVDA"], "Technology", "X / StockTwits"),
    ("Massive layoffs rumored at legacy retail fintech division. $BAC sentiment turning very sour among engineering teams. 📉", "Other", -0.65, 5.8, ["BAC"], "Financials", "Blind / Reddit"),
    ("$TSLA deliveries missed consensus again in Europe. German Gigafactory shutdown extended. Puts are going to print! 💥", "Earnings", -0.84, 8.2, ["TSLA"], "Consumer Discretionary", "X / Twitter"),
    ("$AAPL App Store antitrust lawsuit could cut service revenue by 20%. Market is completely sleeping on this downside risk. ⚠️", "Regulatory", -0.73, 7.5, ["AAPL"], "Technology", "X / Twitter"),
    ("Holy volume on $XOM! Crude breaking resistance and energy stocks are printing massive buy signals on the daily chart. 🛢️💰", "Market", 0.75, 6.4, ["XOM"], "Energy", "StockTwits"),
    ("Healthcare stocks $UNH $JNJ looking like an incredible bargain right now with dividend reinvestment compounding. Deep value play. 💎", "Market", 0.68, 5.1, ["UNH", "JNJ"], "Healthcare", "Reddit r/investing"),
    ("$MSFT enterprise Azure cloud migration numbers look totally unstoppable this quarter. IT budgets are moving straight to AI.", "Product Launch", 0.86, 7.3, ["MSFT"], "Technology", "X / Twitter"),
    ("Fed chair speaking soon. Bond yields spike 12 bps in 30 minutes! High beta tech taking a severe beating today. 🩸", "Macroeconomic", -0.70, 7.8, ["NVDA", "TSLA", "AMZN"], "Technology", "X / Financial News Feed"),
    ("Just deployed the new Claude & Gemini models inside our enterprise org. The productivity gains are real. Bullish $GOOGL.", "Product Launch", 0.71, 5.6, ["GOOGL"], "Technology", "Hacker News"),
    ("Middle East tanker warning issued by UK maritime authorities! Crude oil spike imminent. Inflation hedge is ON. ⚡", "Geopolitical", -0.65, 8.0, ["XOM", "CVX"], "Energy", "X / OpenSource Intel")
]

def generate_events_csv():
    base_time = datetime.now() - timedelta(days=5)
    news_rows = []
    
    # Generate 50 news events by repeating and subtly varying templates
    for i in range(50):
        tmpl = NEWS_TEMPLATES[i % len(NEWS_TEMPLATES)]
        t_delta = timedelta(hours=i * 2.4, minutes=random.randint(5, 55))
        evt_time = base_time + t_delta
        
        # Add slight natural jitter to sentiment and impact
        sentiment = max(-1.0, min(1.0, round(tmpl[2] + random.uniform(-0.08, 0.08), 3)))
        impact = max(1.0, min(10.0, round(tmpl[3] + random.uniform(-0.4, 0.4), 1)))
        conf = round(random.uniform(0.85, 0.98), 2)
        
        news_rows.append({
            "event_id": f"NEWS-{1000 + i}",
            "headline": tmpl[0],
            "text": f"{tmpl[0]} Analysts note that this development carries significant implications for sector benchmarks, valuation multiples, and immediate portfolio allocation adjustments.",
            "source_type": "News",
            "source": tmpl[6],
            "category": tmpl[1],
            "sentiment_score": sentiment,
            "impact_score": impact,
            "tickers": ",".join(tmpl[4]),
            "sector": tmpl[5],
            "confidence": conf,
            "timestamp": evt_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    news_df = pd.DataFrame(news_rows)
    news_df.to_csv(os.path.join(DATA_DIR, "news_events.csv"), index=False)
    print(f"[OK] Created news_events.csv ({len(news_df)} records)")
    
    # Generate 40 social events
    social_rows = []
    for i in range(40):
        tmpl = SOCIAL_TEMPLATES[i % len(SOCIAL_TEMPLATES)]
        t_delta = timedelta(hours=i * 3.1, minutes=random.randint(3, 50))
        evt_time = base_time + t_delta
        
        sentiment = max(-1.0, min(1.0, round(tmpl[2] + random.uniform(-0.1, 0.1), 3)))
        impact = max(1.0, min(10.0, round(tmpl[3] + random.uniform(-0.5, 0.5), 1)))
        conf = round(random.uniform(0.78, 0.95), 2)
        
        social_rows.append({
            "event_id": f"SOC-{2000 + i}",
            "headline": tmpl[0][:60] + "...",
            "text": tmpl[0],
            "source_type": "Social",
            "source": tmpl[6],
            "category": tmpl[1],
            "sentiment_score": sentiment,
            "impact_score": impact,
            "tickers": ",".join(tmpl[4]),
            "sector": tmpl[5],
            "confidence": conf,
            "timestamp": evt_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    social_df = pd.DataFrame(social_rows)
    social_df.to_csv(os.path.join(DATA_DIR, "social_events.csv"), index=False)
    print(f"[OK] Created social_events.csv ({len(social_df)} records)")
    return news_df, social_df

# 4. MARKET DATA (Historical / Simulated Baseline Prices & Betas)
CALIBRATED_BASE_PRICES = {
    "AAPL": 182.50, "MSFT": 415.20, "NVDA": 875.00, "GOOGL": 155.40,
    "AMZN": 178.90, "JPM": 198.30, "BAC": 37.50, "V": 278.40,
    "JNJ": 152.10, "UNH": 482.00, "XOM": 118.60, "CVX": 156.20,
    "PG": 162.80, "TSLA": 175.40, "CAT": 345.00, "NEE": 68.20
}

def generate_market_data_csv(companies_df):
    records = []
    base_date = datetime.now() - timedelta(days=30)
    
    for _, comp in companies_df.iterrows():
        ticker = comp['ticker']
        curr_price = CALIBRATED_BASE_PRICES.get(ticker, 150.0)
        
        for d in range(30):
            date_str = (base_date + timedelta(days=d)).strftime("%Y-%m-%d")
            # Calibrated random walk around true base price
            pct_change = random.gauss(0.0005, 0.015 * comp['beta'])
            curr_price = round(curr_price * (1 + pct_change), 2)
            vol = int(random.uniform(2_000_000, 15_000_000))
            records.append({
                "date": date_str,
                "ticker": ticker,
                "close_price": curr_price,
                "volume": vol,
                "beta": comp['beta']
            })
            
    mkt_df = pd.DataFrame(records)
    mkt_df.to_csv(os.path.join(DATA_DIR, "market_data.csv"), index=False)
    print(f"[OK] Created market_data.csv ({len(mkt_df)} records with calibrated base prices)")
    return mkt_df

# 5. STRESS SCENARIOS JSON (Wholesale Banking Multi-Asset Stress Scenarios)
def generate_stress_scenarios_json():
    scenarios = [
        {
            "id": "SCEN-GEO-01",
            "name": "Global Geopolitical Escalation & Supply Chain Severance",
            "category": "Geopolitical",
            "severity": 9.2,
            "description": "Simulated multi-theater maritime blockade disrupting 30% of global semiconductor trade and shipping lanes, triggering emergency commodity rationing.",
            "impact_factors": {
                "Equities": -0.165,
                "Bonds": 0.045,
                "Derivatives": -0.220,
                "Cash": 0.000,
                "Commodities": 0.280
            },
            "sector_shocks": {
                "Technology": -0.225,
                "Consumer Discretionary": -0.180,
                "Financials": -0.140,
                "Healthcare": -0.050,
                "Energy": 0.190,
                "Utilities": -0.040,
                "Industrials": -0.150
            },
            "wholesale_portfolio": {
                "total_nominal_usd": 50_000_000.0,
                "asset_classes": {
                    "Equities": {"value": 22_500_000.0, "share": 0.45},
                    "Bonds": {"value": 15_000_000.0, "share": 0.30},
                    "Derivatives": {"value": 7_500_000.0, "share": 0.15},
                    "Cash": {"value": 5_000_000.0, "share": 0.10}
                }
            }
        },
        {
            "id": "SCEN-MACRO-02",
            "name": "Sudden 150 bps Stagflationary Rate Shock",
            "category": "Macroeconomic",
            "severity": 8.5,
            "description": "Unanticipated central bank emergency monetary tightening of 150 bps to combat sticky energy inflation, depressing fixed income valuations and corporate credit spreads.",
            "impact_factors": {
                "Equities": -0.135,
                "Bonds": -0.088,
                "Derivatives": -0.160,
                "Cash": 0.015,
                "Commodities": -0.070
            },
            "sector_shocks": {
                "Technology": -0.190,
                "Consumer Discretionary": -0.160,
                "Financials": 0.040,
                "Healthcare": -0.060,
                "Energy": -0.030,
                "Utilities": -0.120,
                "Industrials": -0.110
            },
            "wholesale_portfolio": {
                "total_nominal_usd": 50_000_000.0,
                "asset_classes": {
                    "Equities": {"value": 22_500_000.0, "share": 0.45},
                    "Bonds": {"value": 15_000_000.0, "share": 0.30},
                    "Derivatives": {"value": 7_500_000.0, "share": 0.15},
                    "Cash": {"value": 5_000_000.0, "share": 0.10}
                }
            }
        },
        {
            "id": "SCEN-CREDIT-03",
            "name": "Systemic Credit Contagion & Commercial Real Estate Default Cascade",
            "category": "Credit",
            "severity": 8.9,
            "description": "Liquidity crisis triggered by multi-billion debt default across major European/US commercial property syndicates, spiking credit default swap spreads.",
            "impact_factors": {
                "Equities": -0.175,
                "Bonds": -0.065,
                "Derivatives": -0.280,
                "Cash": 0.005,
                "Commodities": -0.120
            },
            "sector_shocks": {
                "Technology": -0.110,
                "Consumer Discretionary": -0.145,
                "Financials": -0.260,
                "Healthcare": -0.040,
                "Energy": -0.090,
                "Utilities": -0.050,
                "Industrials": -0.130
            },
            "wholesale_portfolio": {
                "total_nominal_usd": 50_000_000.0,
                "asset_classes": {
                    "Equities": {"value": 22_500_000.0, "share": 0.45},
                    "Bonds": {"value": 15_000_000.0, "share": 0.30},
                    "Derivatives": {"value": 7_500_000.0, "share": 0.15},
                    "Cash": {"value": 5_000_000.0, "share": 0.10}
                }
            }
        },
        {
            "id": "SCEN-TECH-04",
            "name": "Global Tech Monopoly Breakup & AI Compute Sanctions",
            "category": "Regulatory",
            "severity": 8.1,
            "description": "Coordinated international antitrust rulings requiring break-up of cloud ecosystems alongside heavy computing export embargoes.",
            "impact_factors": {
                "Equities": -0.140,
                "Bonds": 0.020,
                "Derivatives": -0.190,
                "Cash": 0.000,
                "Commodities": -0.040
            },
            "sector_shocks": {
                "Technology": -0.270,
                "Consumer Discretionary": -0.130,
                "Financials": -0.050,
                "Healthcare": 0.020,
                "Energy": 0.010,
                "Utilities": 0.030,
                "Industrials": -0.080
            },
            "wholesale_portfolio": {
                "total_nominal_usd": 50_000_000.0,
                "asset_classes": {
                    "Equities": {"value": 22_500_000.0, "share": 0.45},
                    "Bonds": {"value": 15_000_000.0, "share": 0.30},
                    "Derivatives": {"value": 7_500_000.0, "share": 0.15},
                    "Cash": {"value": 5_000_000.0, "share": 0.10}
                }
            }
        },
        {
            "id": "SCEN-COMM-05",
            "name": "Global Energy Embargo & Commodity Super-Cycle Spike",
            "category": "Market",
            "severity": 7.8,
            "description": "Strait closure and production cutbacks pushing Brent crude to $140/bbl and European natural gas up 85%, compressing industrial margins.",
            "impact_factors": {
                "Equities": -0.115,
                "Bonds": -0.045,
                "Derivatives": -0.150,
                "Cash": 0.010,
                "Commodities": 0.350
            },
            "sector_shocks": {
                "Technology": -0.120,
                "Consumer Discretionary": -0.170,
                "Financials": -0.080,
                "Healthcare": -0.040,
                "Energy": 0.310,
                "Utilities": -0.090,
                "Industrials": -0.160
            },
            "wholesale_portfolio": {
                "total_nominal_usd": 50_000_000.0,
                "asset_classes": {
                    "Equities": {"value": 22_500_000.0, "share": 0.45},
                    "Bonds": {"value": 15_000_000.0, "share": 0.30},
                    "Derivatives": {"value": 7_500_000.0, "share": 0.15},
                    "Cash": {"value": 5_000_000.0, "share": 0.10}
                }
            }
        }
    ]
    
    with open(os.path.join(DATA_DIR, "stress_scenarios.json"), "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)
    print("[OK] Created stress_scenarios.json")

def main():
    print("Generating FinSight AI Demo Datasets...")
    comp_df = generate_companies_csv()
    generate_portfolio_csv(comp_df)
    generate_events_csv()
    generate_market_data_csv(comp_df)
    generate_stress_scenarios_json()
    print("All demo data generated successfully in /data directory!")

if __name__ == "__main__":
    main()
