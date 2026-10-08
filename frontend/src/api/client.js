// FinSight AI API Client
const API_BASE = "http://127.0.0.1:8000";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/api/metrics`);
  return res.json();
}

export async function fetchPortfolio() {
  const res = await fetch(`${API_BASE}/api/portfolio`);
  return res.json();
}

export async function executeRebalance(payload) {
  const res = await fetch(`${API_BASE}/api/portfolio/rebalance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function simulateEvents(numEvents = 1, sensitivity = 0.025) {
  const res = await fetch(`${API_BASE}/api/portfolio/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_events: numEvents, sensitivity }),
  });
  return res.json();
}

export async function resetPortfolio() {
  const res = await fetch(`${API_BASE}/api/portfolio/reset`, {
    method: "POST",
  });
  return res.json();
}

export async function fetchRebalanceHistory(limit = 50) {
  const res = await fetch(`${API_BASE}/api/rebalance-history?limit=${limit}`);
  return res.json();
}

export async function fetchEvents(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") query.append(k, v);
  });
  const res = await fetch(`${API_BASE}/api/events?${query.toString()}`);
  return res.json();
}

export async function analyzeCustomText(text, headline = "", source = "Custom Input", sourceType = "News") {
  const res = await fetch(`${API_BASE}/api/events/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      headline: headline || undefined,
      source,
      source_type: sourceType,
    }),
  });
  return res.json();
}

export async function fetchStressScenarios() {
  const res = await fetch(`${API_BASE}/api/stress-tests/scenarios`);
  return res.json();
}

export async function fetchWholesalePortfolio() {
  const res = await fetch(`${API_BASE}/api/stress-tests/portfolio`);
  return res.json();
}

export async function runStressTest(payload) {
  const res = await fetch(`${API_BASE}/api/stress-tests/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchStressHistory(limit = 20) {
  const res = await fetch(`${API_BASE}/api/stress-tests?limit=${limit}`);
  return res.json();
}

export async function runDemoScenario() {
  const res = await fetch(`${API_BASE}/api/demo/scenario`, {
    method: "POST",
  });
  return res.json();
}

// ==========================================
// Market Intelligence & Forecasting APIs
// (Enhanced from stock-data-intelligence-dashboard)
// ==========================================

export async function fetchMarketCompanies() {
  const res = await fetch(`${API_BASE}/api/market/companies`);
  return res.json();
}

export async function fetchStockData(symbol, days = 30) {
  const res = await fetch(`${API_BASE}/api/market/data/${symbol}?days=${days}`);
  return res.json();
}

export async function fetchStockSummary(symbol) {
  const res = await fetch(`${API_BASE}/api/market/summary/${symbol}`);
  return res.json();
}

export async function fetchMonteCarloForecast(symbol, days = 14, sentimentGuided = true) {
  const res = await fetch(`${API_BASE}/api/market/forecast/${symbol}?days=${days}&sentiment_guided=${sentimentGuided}`);
  return res.json();
}

export async function compareStocks(symbol1, symbol2, days = 30) {
  const res = await fetch(`${API_BASE}/api/market/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`);
  return res.json();
}

export async function fetchGainersLosers() {
  const res = await fetch(`${API_BASE}/api/market/gainers-losers`);
  return res.json();
}

export async function refreshStockData(symbol) {
  const res = await fetch(`${API_BASE}/api/market/refresh/${symbol}`, {
    method: "POST"
  });
  return res.json();
}
