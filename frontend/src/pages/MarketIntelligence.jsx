import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  LineChart as LineChartIcon,
  GitCompare,
  Activity,
  RefreshCw,
  Sliders,
  DollarSign,
  Layers,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Area
} from 'recharts';
import StatCard from '../components/StatCard';
import SentimentBadge from '../components/SentimentBadge';
import {
  fetchMarketCompanies,
  fetchStockSummary,
  fetchMonteCarloForecast,
  compareStocks,
  fetchGainersLosers,
  refreshStockData
} from '../api/client';

export default function MarketIntelligence({ showToast }) {
  const [companies, setCompanies] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("NVDA");
  const [summary, setSummary] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [forecastDays, setForecastDays] = useState(14);
  const [sentimentGuided, setSentimentGuided] = useState(true);
  const [gainersLosers, setGainersLosers] = useState({ gainers: [], losers: [] });
  const [refreshing, setRefreshing] = useState(false);

  // Pairwise Comparison State
  const [compareSym1, setCompareSym1] = useState("NVDA");
  const [compareSym2, setCompareSym2] = useState("TSLA");
  const [compareDays, setCompareDays] = useState(30);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loadingCompare, setLoadingCompare] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const comps = await fetchMarketCompanies();
        setCompanies(comps || []);
        const gl = await fetchGainersLosers();
        setGainersLosers(gl || { gainers: [], losers: [] });
      } catch (err) {
        console.error(err);
      }
    }
    init();
  }, []);

  useEffect(() => {
    loadSymbolData(selectedSymbol);
  }, [selectedSymbol, forecastDays, sentimentGuided]);

  useEffect(() => {
    handleCompare();
  }, [compareSym1, compareSym2, compareDays]);

  const loadSymbolData = async (sym) => {
    try {
      const summ = await fetchStockSummary(sym);
      setSummary(summ);
      const fc = await fetchMonteCarloForecast(sym, forecastDays, sentimentGuided);
      setForecastData(fc);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshStockData(selectedSymbol);
      await loadSymbolData(selectedSymbol);
      if (showToast) showToast(`Refreshed live market data for $${selectedSymbol} from Yahoo Finance!`, "success");
    } catch (err) {
      console.error(err);
      if (showToast) showToast(`Fallback cache maintained for $${selectedSymbol}.`, "info");
    } finally {
      setRefreshing(false);
    }
  };

  const handleCompare = async () => {
    if (compareSym1 === compareSym2) return;
    setLoadingCompare(true);
    try {
      const res = await compareStocks(compareSym1, compareSym2, compareDays);
      setComparisonResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingCompare(false);
    }
  };

  return (
    <div className="page-wrapper">
      {/* Gainers / Losers Market Ticker */}
      <div className="glass-panel" style={{
        borderRadius: '14px',
        padding: '12px 18px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Gainers */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            TOP GAINERS:
          </span>
          {gainersLosers.gainers?.map((g) => (
            <span key={g.symbol} className="mono-text" style={{ fontSize: '0.78rem', background: '#10b98115', border: '1px solid #10b98130', padding: '2px 8px', borderRadius: '4px', color: '#34d399' }}>
              ${g.symbol} +{g.daily_return?.toFixed(2)}%
            </span>
          ))}
        </div>

        {/* Losers */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            TOP LOSERS:
          </span>
          {gainersLosers.losers?.map((l) => (
            <span key={l.symbol} className="mono-text" style={{ fontSize: '0.78rem', background: '#ef444415', border: '1px solid #ef444430', padding: '2px 8px', borderRadius: '4px', color: '#f87171' }}>
              ${l.symbol} {l.daily_return?.toFixed(2)}%
            </span>
          ))}
        </div>
      </div>

      {/* Stock Selection & Summary Header */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Select Asset:
            </label>
            <select
              className="form-select"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              style={{ width: '180px', fontWeight: 700, fontSize: '0.95rem' }}
            >
              {(Array.isArray(companies) ? companies : []).map((c) => (
                <option key={c.ticker} value={c.ticker}>
                  ${c.ticker} — {c.name}
                </option>
              ))}
            </select>

            <span className="badge badge-neutral">
              {summary?.sector || "Technology"}
            </span>

            <span className="badge" style={{ background: 'var(--apple-green-surface)', color: 'var(--apple-green)', border: '1px solid rgba(48, 209, 88, 0.35)' }}>
              Source: {summary?.data_source || "yfinance"}
            </span>
          </div>

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="btn btn-outline btn-sm"
          >
            <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
            <span>Fetch Latest via Yahoo Finance</span>
          </button>
        </div>

        {/* KPI Row */}
        {summary && (
          <div className="grid-cols-4">
            <StatCard
              title="Current Price"
              value={`$${summary.current_price?.toFixed(2)}`}
              subtitle={`Avg: $${summary.avg_close?.toFixed(2)}`}
              icon={DollarSign}
              color="#3b82f6"
            />
            <StatCard
              title="52-Week Range"
              value={`$${summary.high_52w?.toFixed(0)} / $${summary.low_52w?.toFixed(0)}`}
              subtitle="52-Week High / Low"
              icon={Activity}
              color="#f59e0b"
            />
            <StatCard
              title="Annualized Volatility"
              value={`${summary.volatility_score}%`}
              subtitle="std(returns) × √252"
              icon={TrendingUp}
              color="#ec4899"
            />
            <StatCard
              title="Tail Risk Best Day"
              value={`+${summary.top_3_best_days?.[0]?.daily_return?.toFixed(2)}%`}
              subtitle={`Worst: ${summary.top_3_worst_days?.[0]?.daily_return?.toFixed(2)}%`}
              icon={Layers}
              color="#10b981"
            />
          </div>
        )}
      </div>

      {/* Sentiment-Conditioned Monte Carlo Forecast Section */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="var(--text-primary)" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Monte Carlo Probabilistic Price Forecasting (Geometric Brownian Motion)
              </h3>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              100 simulation paths modeled via S(t+1) = S(t) × exp((&mu; - &sigma;&sup2;/2) + &sigma;&epsilon;). Shaded area indicates 5th to 95th percentile probability cone.
            </p>
          </div>

          {/* Forecast Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={sentimentGuided}
                onChange={(e) => setSentimentGuided(e.target.checked)}
                style={{ accentColor: '#a855f7' }}
              />
              <span>NLP Sentiment Drift Guide</span>
            </label>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Horizon:</span>
              <select
                className="form-select"
                value={forecastDays}
                onChange={(e) => setForecastDays(parseInt(e.target.value))}
                style={{ width: '100px', padding: '4px 8px', fontSize: '0.8rem' }}
              >
                <option value={7}>7 Days</option>
                <option value={14}>14 Days</option>
                <option value={30}>30 Days</option>
              </select>
            </div>
          </div>
        </div>

        {/* Sentiment Boost Indicator */}
        {forecastData?.sentiment_guided && (
          <div style={{
            background: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: '6px',
            padding: '8px 12px',
            marginBottom: '14px',
            fontSize: '0.78rem',
            color: '#d8b4fe',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Info size={14} color="#a855f7" />
            <span>
              Drift Parameter (&mu;) adjusted by <strong>{forecastData.sentiment_drift_boost > 0 ? '+' : ''}{forecastData.sentiment_drift_boost}%</strong> based on recent NLP Risk Engine signals for ${selectedSymbol}.
            </span>
          </div>
        )}

        {/* Monte Carlo Probability Cone Area Chart */}
        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={forecastData?.forecast || []} margin={{ top: 10, right: 15, left: -10, bottom: 5 }}>
              <defs>
                <linearGradient id="coneGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.35}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis
                domain={['auto', 'auto']}
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(val) => `$${val}`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(32, 33, 36, 0.90)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.22)', borderRadius: '10px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', color: '#f5f5f7' }}
                formatter={(val, name) => [`$${val}`, name === 'upper' ? '95th Percentile' : (name === 'median' ? 'Median (50th)' : '5th Percentile')]}
              />
              <Area type="monotone" dataKey="upper" stroke="#dce0e6" fillOpacity={1} fill="url(#coneGrad)" name="upper" />
              <Area type="monotone" dataKey="lower" stroke="#dce0e6" fillOpacity={0} name="lower" />
              <Line type="monotone" dataKey="median" stroke="#f5f5f7" strokeWidth={2.5} dot={false} name="median" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pairwise Stock Comparison & Pearson Correlation Section */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <GitCompare size={18} color="var(--text-primary)" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Multi-Stock Pairwise Comparative Analytics & Pearson Correlation
              </h3>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Normalized (Base-100) performance trajectory and daily return cross-asset correlation.
            </p>
          </div>

          {/* Selectors */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <select
              className="form-select"
              value={compareSym1}
              onChange={(e) => setCompareSym1(e.target.value)}
              style={{ width: '110px', fontSize: '0.85rem' }}
            >
              {(Array.isArray(companies) ? companies : []).map((c) => (
                <option key={c.ticker} value={c.ticker}>${c.ticker}</option>
              ))}
            </select>

            <span style={{ color: '#64748b', fontWeight: 700 }}>VS</span>

            <select
              className="form-select"
              value={compareSym2}
              onChange={(e) => setCompareSym2(e.target.value)}
              style={{ width: '110px', fontSize: '0.85rem' }}
            >
              {(Array.isArray(companies) ? companies : []).map((c) => (
                <option key={c.ticker} value={c.ticker}>${c.ticker}</option>
              ))}
            </select>

            <select
              className="form-select"
              value={compareDays}
              onChange={(e) => setCompareDays(parseInt(e.target.value))}
              style={{ width: '100px', fontSize: '0.85rem' }}
            >
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
            </select>
          </div>
        </div>

        {/* Correlation & Return Summary Bar */}
        {comparisonResult && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--glass-border)',
            borderRadius: '12px',
            padding: '12px 18px',
            marginBottom: '16px',
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <div>
              <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                Pearson Correlation (r)
              </span>
              <div className="mono-text" style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {comparisonResult.correlation}
              </div>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                ${comparisonResult.symbol1} {compareDays}D Return
              </span>
              <div className="mono-text" style={{ fontSize: '1.25rem', fontWeight: 800, color: comparisonResult.return1_pct >= 0 ? '#10b981' : '#ef4444' }}>
                {comparisonResult.return1_pct >= 0 ? '+' : ''}{comparisonResult.return1_pct}%
              </div>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                ${comparisonResult.symbol2} {compareDays}D Return
              </span>
              <div className="mono-text" style={{ fontSize: '1.25rem', fontWeight: 800, color: comparisonResult.return2_pct >= 0 ? '#10b981' : '#ef4444' }}>
                {comparisonResult.return2_pct >= 0 ? '+' : ''}{comparisonResult.return2_pct}%
              </div>
            </div>
          </div>
        )}

        {/* Base 100 Chart */}
        <div style={{ height: '280px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={comparisonResult?.series || []} margin={{ top: 10, right: 15, left: -10, bottom: 5 }}>
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={['auto', 'auto']} tickFormatter={(v) => `${v}`} />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(32, 33, 36, 0.90)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.22)', borderRadius: '10px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', color: '#f5f5f7' }}
                formatter={(val, name) => [`${val}`, name.replace('_norm', ' (Base 100)')]}
              />
              <Legend wrapperStyle={{ fontSize: '0.78rem' }} />
              <Line type="monotone" dataKey={`${compareSym1}_norm`} stroke="#3b82f6" strokeWidth={2.5} dot={false} name={`$${compareSym1} (Base 100)`} />
              <Line type="monotone" dataKey={`${compareSym2}_norm`} stroke="#ec4899" strokeWidth={2.5} dot={false} name={`$${compareSym2} (Base 100)`} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
