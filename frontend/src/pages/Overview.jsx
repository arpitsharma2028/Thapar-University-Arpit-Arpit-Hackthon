import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  ShieldAlert,
  Activity,
  ArrowUpRight,
  Layers,
  BarChart2,
  ArrowRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
  ComposedChart,
  Area
} from 'recharts';
import StatCard from '../components/StatCard';
import SentimentBadge from '../components/SentimentBadge';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';
import EventModal from '../components/EventModal';
import {
  fetchGainersLosers,
  fetchStockSummary,
  fetchMonteCarloForecast
} from '../api/client';

const SECTOR_COLORS = [
  '#0a84ff', '#30d158', '#ffd60a', '#ff375f', '#bf5af2', '#64d2ff', '#8e8e93', '#ff453a'
];

const PREVIEW_TICKERS = ["NVDA", "AAPL", "MSFT", "TSLA", "JPM", "XOM"];

export default function Overview({
  metrics,
  portfolio,
  onRunDemo,
  onSimulateEvent,
  onRebalanceTrigger,
  onStressTrigger,
  onNavigateTab,
  loading
}) {
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Market Intelligence preview states (from reference quantitative engine)
  const [gainersLosers, setGainersLosers] = useState({ gainers: [], losers: [] });
  const [marketSymbol, setMarketSymbol] = useState("NVDA");
  const [marketSummary, setMarketSummary] = useState(null);
  const [marketForecast, setMarketForecast] = useState(null);
  const [loadingMarket, setLoadingMarket] = useState(false);

  const totalValue = portfolio?.total_value || metrics?.portfolio?.total_value || 10000000;
  const portfolioSentiment = portfolio?.portfolio_sentiment ?? 0.05;
  const riskLevel = portfolio?.risk_level || "Moderate";
  const var95 = metrics?.portfolio?.var_95_1day || 245000;
  const rebalanceCount = metrics?.portfolio?.total_rebalances || 0;
  const stressCount = metrics?.portfolio?.total_stress_tests || 0;

  useEffect(() => {
    async function loadMarketStats() {
      try {
        const gl = await fetchGainersLosers();
        if (gl) setGainersLosers(gl);
      } catch (e) {
        console.error("Failed to load gainers/losers:", e);
      }
    }
    loadMarketStats();
  }, []);

  useEffect(() => {
    async function loadSymbolStats() {
      setLoadingMarket(true);
      try {
        const [sum, fc] = await Promise.all([
          fetchStockSummary(marketSymbol),
          fetchMonteCarloForecast(marketSymbol, 14, true)
        ]);
        setMarketSummary(sum);
        setMarketForecast(fc);
      } catch (e) {
        console.error(`Failed to load market metrics for ${marketSymbol}:`, e);
      } finally {
        setLoadingMarket(false);
      }
    }
    loadSymbolStats();
  }, [marketSymbol]);

  // Valuation History data for Recharts
  const historyData = (metrics?.portfolio_history && metrics.portfolio_history.length > 0)
    ? metrics.portfolio_history.map(item => ({
        time: item.timestamp.split(' ')[1] || item.timestamp,
        value: Math.round(item.total_value),
        sentiment: item.portfolio_sentiment
      }))
    : [
        { time: '10:00', value: 10000000 },
        { time: '11:00', value: 10045000 },
        { time: '12:00', value: 10020000 },
        { time: '13:00', value: 10080000 },
        { time: '14:00', value: totalValue }
      ];

  // Sector allocation data for PieChart
  const sectorData = (metrics?.sector_allocation && metrics.sector_allocation.length > 0)
    ? metrics.sector_allocation.map(s => ({
        name: s.sector,
        value: Math.round(s.weight * 100)
      }))
    : (portfolio?.positions || []).reduce((acc, p) => {
        const existing = acc.find(x => x.name === p.sector);
        if (existing) existing.value += Math.round(p.current_weight * 100);
        else acc.push({ name: p.sector, value: Math.round(p.current_weight * 100) });
        return acc;
      }, []);

  return (
    <div className="page-wrapper">
      {/* Live Alert Ticker */}
      <div className="glass-panel" style={{
        background: 'linear-gradient(90deg, rgba(255, 255, 255, 0.09) 0%, rgba(255, 255, 255, 0.03) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.20)',
        borderRadius: '14px',
        padding: '12px 18px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        boxShadow: 'var(--shadow-sm), inset 0 1px 1px rgba(255, 255, 255, 0.15)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{
            background: 'var(--apple-red-surface)',
            color: 'var(--apple-red)',
            border: '1px solid rgba(255, 69, 58, 0.4)',
            fontSize: '0.68rem',
            fontWeight: 700,
            padding: '3px 8px',
            borderRadius: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px'
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--apple-red)', boxShadow: '0 0 6px var(--apple-red)' }} />
            LIVE FEED
          </span>
          <span style={{ fontSize: '0.84rem', color: '#f5f5f7', fontWeight: 500 }}>
            {metrics?.recent_alerts?.[0]?.headline || "AI Risk Engine actively parsing live News & Social signals across 16 Index Assets."}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onSimulateEvent}
            disabled={loading}
            className="btn btn-sm btn-secondary"
          >
            <Activity size={13} color="var(--text-primary)" />
            <span>Process Next Signal</span>
          </button>
        </div>
      </div>

      {/* Top Gainers & Losers Market Strip */}
      <div className="glass-panel" style={{
        borderRadius: '14px',
        padding: '10px 16px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Gainers */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--apple-green)', letterSpacing: '0.06em' }}>
            MARKET GAINERS:
          </span>
          {(gainersLosers.gainers || []).slice(0, 3).map((g) => (
            <span
              key={g.symbol}
              onClick={() => setMarketSymbol(g.symbol)}
              className="mono-text"
              style={{
                fontSize: '0.76rem',
                fontWeight: 600,
                background: 'var(--apple-green-surface)',
                border: '1px solid rgba(48, 209, 88, 0.32)',
                padding: '2px 8px',
                borderRadius: '6px',
                color: 'var(--apple-green)',
                cursor: 'pointer'
              }}
              title="Click to inspect Monte Carlo forecast"
            >
              ${g.symbol} +{g.daily_return?.toFixed(2)}%
            </span>
          ))}
        </div>

        {/* Losers */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--apple-red)', letterSpacing: '0.06em' }}>
            MARKET LOSERS:
          </span>
          {(gainersLosers.losers || []).slice(0, 3).map((l) => (
            <span
              key={l.symbol}
              onClick={() => setMarketSymbol(l.symbol)}
              className="mono-text"
              style={{
                fontSize: '0.76rem',
                fontWeight: 600,
                background: 'var(--apple-red-surface)',
                border: '1px solid rgba(255, 69, 58, 0.32)',
                padding: '2px 8px',
                borderRadius: '6px',
                color: 'var(--apple-red)',
                cursor: 'pointer'
              }}
              title="Click to inspect Monte Carlo forecast"
            >
              ${l.symbol} {l.daily_return?.toFixed(2)}%
            </span>
          ))}
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-cols-4" style={{ marginBottom: '24px' }}>
        <StatCard
          title="Portfolio Valuation"
          value={`$${(totalValue / 1000000).toFixed(2)}M`}
          subtitle={`Baseline $10.00M`}
          icon={DollarSign}
          color="var(--apple-green)"
          trend={+(((totalValue - 10000000) / 10000000) * 100).toFixed(2)}
        />
        <StatCard
          title="Portfolio Sentiment"
          value={portfolioSentiment > 0 ? `+${portfolioSentiment.toFixed(2)}` : portfolioSentiment.toFixed(2)}
          subtitle={`Risk Level: ${riskLevel}`}
          icon={TrendingUp}
          color={portfolioSentiment >= 0 ? "var(--apple-green)" : "var(--apple-red)"}
        />
        <StatCard
          title="1-Day VaR (95%)"
          value={`$${(var95 / 1000).toFixed(1)}K`}
          subtitle="Simulated Parametric Value-at-Risk"
          icon={ShieldAlert}
          color="var(--apple-amber)"
        />
        <StatCard
          title="Engine Decisions"
          value={`${rebalanceCount} / ${stressCount}`}
          subtitle="Rebalances / Stress Tests Logged"
          icon={Activity}
          color="var(--glass-border-strong)"
        />
      </div>

      {/* Section 1: Valuation Trend + Sector Allocation */}
      <div className="grid-cols-12" style={{ marginBottom: '24px' }}>
        {/* Left: Valuation Trend */}
        <div className="glass-card" style={{ gridColumn: 'span 7' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Portfolio Valuation Dynamic Trajectory
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Mark-to-market performance driven by sentiment shocks and algorithmic rebalances
              </p>
            </div>
            <span className="badge badge-bullish">
              Adaptive Index
            </span>
          </div>
          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis
                  domain={['auto', 'auto']}
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000000).toFixed(2)}M`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(32, 33, 36, 0.90)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.22)', borderRadius: '10px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', color: '#f5f5f7' }}
                  formatter={(val) => [`$${Number(val).toLocaleString()}`, 'Portfolio Value']}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#f5f5f7"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#f5f5f7' }}
                  activeDot={{ r: 6, fill: '#ffffff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Sector Allocation Breakdown */}
        <div className="glass-card" style={{ gridColumn: 'span 5' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Index Sector Diversification
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Target vs current sector weights (%)
              </p>
            </div>
            <Layers size={18} color="#94a3b8" />
          </div>
          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={95}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {sectorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SECTOR_COLORS[index % SECTOR_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(32, 33, 36, 0.90)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.22)', borderRadius: '10px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', color: '#f5f5f7' }}
                  formatter={(val, name) => [`${val}%`, name]}
                />
                <Legend
                  wrapperStyle={{ fontSize: '0.72rem', color: '#94a3b8' }}
                  layout="horizontal"
                  verticalAlign="bottom"
                  align="center"
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Section 2: Stochastic Monte Carlo Forecasting Panel (Direct from reference repo quantitative algorithms) */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={18} color="var(--text-primary)" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Stochastic Price Forecasting (Geometric Brownian Motion)
              </h3>
              <span className="badge badge-neutral">
                100 Paths • P5 to P95 Cone
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              14-Day Monte Carlo price projection conditioned on historical volatility and FinSight NLP risk sentiment drift
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ display: 'flex', gap: '6px' }}>
              {PREVIEW_TICKERS.map((sym) => (
                <button
                  key={sym}
                  onClick={() => setMarketSymbol(sym)}
                  className={`btn btn-sm ${marketSymbol === sym ? 'btn-primary' : 'btn-outline'}`}
                  style={{ padding: '3px 9px', fontSize: '0.75rem' }}
                >
                  ${sym}
                </button>
              ))}
            </div>

            {onNavigateTab && (
              <button
                onClick={() => onNavigateTab('market-intel')}
                className="btn btn-sm btn-outline"
                style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
                title="Open full interactive market analytics and correlation matrix"
              >
                <span>Full Analytics</span>
                <ArrowRight size={13} />
              </button>
            )}
          </div>
        </div>

        {/* Summary Metric Ribbon */}
        {marketSummary && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '10px',
            marginBottom: '16px',
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '12px',
            borderRadius: '12px',
            border: '1px solid var(--glass-border)'
          }}>
            <div>
              <span style={{ fontSize: '0.70rem', color: '#94a3b8', textTransform: 'uppercase' }}>Current Price</span>
              <div className="mono-text" style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
                ${marketSummary.current_price?.toFixed(2)}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.70rem', color: '#94a3b8', textTransform: 'uppercase' }}>52-Week Range</span>
              <div className="mono-text" style={{ fontSize: '0.90rem', color: '#cbd5e1' }}>
                ${marketSummary.low_52w?.toFixed(0)} — ${marketSummary.high_52w?.toFixed(0)}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.70rem', color: '#94a3b8', textTransform: 'uppercase' }}>Ann. Volatility</span>
              <div className="mono-text" style={{ fontSize: '0.90rem', color: '#f59e0b' }}>
                {marketSummary.volatility_score}%
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.70rem', color: '#94a3b8', textTransform: 'uppercase' }}>Sentiment Drift Boost</span>
              <div className="mono-text" style={{ fontSize: '0.90rem', color: marketForecast?.sentiment_drift_boost >= 0 ? '#10b981' : '#ef4444' }}>
                {marketForecast?.sentiment_drift_boost > 0 ? '+' : ''}{marketForecast?.sentiment_drift_boost}%
              </div>
            </div>
          </div>
        )}

        {/* 14-Day Monte Carlo Area Chart */}
        <div style={{ height: '260px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={marketForecast?.forecast || []} margin={{ top: 10, right: 15, left: -10, bottom: 5 }}>
              <defs>
                <linearGradient id="overviewConeGrad" x1="0" y1="0" x2="0" y2="1">
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
              <Area type="monotone" dataKey="upper" stroke="#dce0e6" fillOpacity={1} fill="url(#overviewConeGrad)" name="upper" />
              <Area type="monotone" dataKey="lower" stroke="#dce0e6" fillOpacity={0} name="lower" />
              <Line type="monotone" dataKey="median" stroke="#f5f5f7" strokeWidth={2.5} dot={false} name="median" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Section 3: Recent Risk Engine Events Feed Table */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Latest NLP Risk Signals
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Inbound financial news & social media text transformed into structured risk intelligence
            </p>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Showing 5 most recent signals
          </span>
        </div>

        <div className="table-wrapper">
          <table className="custom-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Category</th>
                <th>Headline</th>
                <th>Mentioned Tickers</th>
                <th>Sentiment</th>
                <th>Impact</th>
                <th>Confidence</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {(metrics?.recent_alerts || []).map((ev) => (
                <tr key={ev.id || ev.event_id} style={{ cursor: 'pointer' }} onClick={() => setSelectedEvent(ev)}>
                  <td className="mono-text" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    {ev.event_id}
                  </td>
                  <td>
                    <EventCategoryBadge category={ev.category} />
                  </td>
                  <td style={{ maxWidth: '380px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 500 }}>
                    {ev.headline}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {(ev.tickers || "").split(',').slice(0, 2).map((t) => (
                        <span key={t} className="mono-text" style={{ fontSize: '0.72rem', background: 'rgba(255, 255, 255, 0.08)', border: '1px solid rgba(255, 255, 255, 0.16)', padding: '2px 6px', borderRadius: '4px', color: '#f5f5f7' }}>
                          ${t.trim()}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <SentimentBadge score={ev.sentiment_score} />
                  </td>
                  <td>
                    <SeverityBadge score={ev.impact_score} />
                  </td>
                  <td className="mono-text" style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    {((ev.confidence || 0.9) * 100).toFixed(0)}%
                  </td>
                  <td>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRebalanceTrigger(ev);
                      }}
                      className="btn btn-sm btn-outline"
                      title="Apply signal to rebalance portfolio"
                    >
                      <ArrowUpRight size={13} />
                      <span>Rebalance</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Event Details Modal */}
      {selectedEvent && (
        <EventModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onRebalanceTrigger={onRebalanceTrigger}
          onStressTrigger={onStressTrigger}
        />
      )}
    </div>
  );
}
