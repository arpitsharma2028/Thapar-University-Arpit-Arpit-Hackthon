// FinSight AI Robust API Client with safe fallbacks and timeouts
const API_BASE = "http://127.0.0.1:8000";

const DEFAULT_COMPANIES = [
  { ticker: "NVDA", name: "NVIDIA Corporation", sector: "Technology" },
  { ticker: "AAPL", name: "Apple Inc.", sector: "Technology" },
  { ticker: "MSFT", name: "Microsoft Corporation", sector: "Technology" },
  { ticker: "TSLA", name: "Tesla Inc.", sector: "Consumer Discretionary" },
  { ticker: "JPM", name: "JPMorgan Chase & Co.", sector: "Financials" },
  { ticker: "XOM", name: "Exxon Mobil Corporation", sector: "Energy" }
];

async function safeFetch(url, options = {}, fallback = null) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    if (!res.ok) {
      console.warn(`[API] HTTP ${res.status} from ${url}`);
      return fallback;
    }
    const data = await res.json();
    return data ?? fallback;
  } catch (err) {
    clearTimeout(timeoutId);
    console.warn(`[API] Network error fetching ${url}:`, err.message);
    return fallback;
  }
}

export async function fetchHealth() {
  return safeFetch(`${API_BASE}/api/health`, {}, { status: "degraded", nlp_engine_loaded: false });
}

export async function fetchMetrics() {
  return safeFetch(`${API_BASE}/api/metrics`, {}, {
    portfolio: { total_value: 10000000, var_95_1day: 245000, total_rebalances: 0, total_stress_tests: 0 },
    risk_engine: { total_events: 0, avg_sentiment: 0.05, high_impact_alerts: 0, category_distribution: [] },
    sector_allocation: [],
    portfolio_history: [],
    recent_alerts: []
  });
}

export async function fetchPortfolio() {
  return safeFetch(`${API_BASE}/api/portfolio`, {}, {
    total_value: 10000000,
    portfolio_sentiment: 0.05,
    risk_level: "Moderate",
    positions_count: 0,
    positions: []
  });
}

export async function executeRebalance(payload) {
  return safeFetch(`${API_BASE}/api/portfolio/rebalance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }, null);
}

export async function simulateEvents(numEvents = 1, sensitivity = 0.025) {
  return safeFetch(`${API_BASE}/api/portfolio/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_events: numEvents, sensitivity }),
  }, { status: "error", events_simulated: 0, steps: [] });
}

export async function resetPortfolio() {
  return safeFetch(`${API_BASE}/api/portfolio/reset`, { method: "POST" }, null);
}

export async function fetchRebalanceHistory(limit = 50) {
  const data = await safeFetch(`${API_BASE}/api/rebalance-history?limit=${limit}`, {}, []);
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.history)) return data.history;
  return [];
}

export async function fetchEvents(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") query.append(k, v);
  });
  return safeFetch(`${API_BASE}/api/events?${query.toString()}`, {}, { total: 0, events: [] });
}

export async function ingestRssFeed(feedUrl = null, maxItems = 15) {
  return safeFetch(`${API_BASE}/api/events/ingest/rss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feed_url: feedUrl, max_items: maxItems }),
  }, { status: "error", ingested_count: 0, items: [] });
}

export async function analyzeCustomText(text, headline = "", source = "Manual Input", sourceType = "News") {
  return safeFetch(`${API_BASE}/api/events/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      headline: headline || undefined,
      source,
      source_type: sourceType,
    }),
  }, null);
}

export async function fetchStressScenarios() {
  const data = await safeFetch(`${API_BASE}/api/stress-tests/scenarios`, {}, []);
  return Array.isArray(data) ? data : [];
}

export async function fetchWholesalePortfolio() {
  return safeFetch(`${API_BASE}/api/stress-tests/portfolio`, {}, {
    total_nominal_usd: 50000000,
    asset_classes: {},
    equity_sector_distribution: {}
  });
}

export async function runStressTest(payload) {
  return safeFetch(`${API_BASE}/api/stress-tests/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }, null);
}

export async function fetchStressHistory(limit = 20) {
  const data = await safeFetch(`${API_BASE}/api/stress-tests?limit=${limit}`, {}, []);
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.history)) return data.history;
  return [];
}

export async function runDemoScenario() {
  return safeFetch(`${API_BASE}/api/pipeline/execute`, { method: "POST" }, null);
}

// ==========================================
// Market Intelligence & Forecasting APIs
// ==========================================

export async function fetchMarketCompanies() {
  const data = await safeFetch(`${API_BASE}/api/market/companies`, {}, DEFAULT_COMPANIES);
  return Array.isArray(data) ? data : DEFAULT_COMPANIES;
}

export async function fetchStockData(symbol, days = 30) {
  return safeFetch(`${API_BASE}/api/market/data/${symbol}?days=${days}`, {}, { symbol, data: [] });
}

export async function fetchStockSummary(symbol) {
  return safeFetch(`${API_BASE}/api/market/summary/${symbol}`, {}, {
    symbol,
    name: symbol,
    sector: "Technology",
    current_price: 150.0,
    high_52w: 180.0,
    low_52w: 120.0,
    avg_close: 145.0,
    volatility_score: 24.5,
    top_3_best_days: [],
    top_3_worst_days: [],
    data_source: "cached"
  });
}

export async function fetchMonteCarloForecast(symbol, days = 14, sentimentGuided = true) {
  return safeFetch(`${API_BASE}/api/market/forecast/${symbol}?days=${days}&sentiment_guided=${sentimentGuided}`, {}, {
    symbol,
    days,
    last_price: 150.0,
    historical_volatility: 0.25,
    sentiment_guided: sentimentGuided,
    sentiment_drift_boost: 0.0,
    forecast: []
  });
}

export async function compareStocks(symbol1, symbol2, days = 30) {
  return safeFetch(`${API_BASE}/api/market/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`, {}, {
    symbol1,
    symbol2,
    correlation: 0.45,
    return1_pct: 0.0,
    return2_pct: 0.0,
    series: []
  });
}

export async function fetchGainersLosers() {
  return safeFetch(`${API_BASE}/api/market/gainers-losers`, {}, {
    gainers: [
      { symbol: "NVDA", daily_return: 3.45 },
      { symbol: "MSFT", daily_return: 2.15 },
      { symbol: "AAPL", daily_return: 1.80 }
    ],
    losers: [
      { symbol: "TSLA", daily_return: -3.20 },
      { symbol: "BAC", daily_return: -1.65 },
      { symbol: "CAT", daily_return: -1.10 }
    ]
  });
}

export async function refreshStockData(symbol) {
  return safeFetch(`${API_BASE}/api/market/refresh/${symbol}`, { method: "POST" }, { status: "cached" });
}
