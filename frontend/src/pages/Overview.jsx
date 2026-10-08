import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  ShieldAlert,
  Zap,
  Activity,
  ArrowUpRight,
  Layers,
  Sparkles
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
  Legend
} from 'recharts';
import StatCard from '../components/StatCard';
import SentimentBadge from '../components/SentimentBadge';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';
import EventModal from '../components/EventModal';

const SECTOR_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#64748b', '#ef4444'
];

export default function Overview({
  metrics,
  portfolio,
  onRunDemo,
  onSimulateEvent,
  onRebalanceTrigger,
  onStressTrigger,
  loading
}) {
  const [selectedEvent, setSelectedEvent] = useState(null);

  const totalValue = portfolio?.total_value || metrics?.portfolio?.total_value || 10000000;
  const portfolioSentiment = portfolio?.portfolio_sentiment ?? 0.05;
  const riskLevel = portfolio?.risk_level || "Moderate";
  const var95 = metrics?.portfolio?.var_95_1day || 245000;
  const rebalanceCount = metrics?.portfolio?.total_rebalances || 0;
  const stressCount = metrics?.portfolio?.total_stress_tests || 0;

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
      <div style={{
        background: 'linear-gradient(90deg, rgba(37, 99, 235, 0.15), rgba(15, 23, 42, 0.8))',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '10px',
        padding: '12px 18px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{
            background: '#ef4444',
            color: '#fff',
            fontSize: '0.68rem',
            fontWeight: 800,
            padding: '3px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            animation: 'pulse 2s infinite'
          }}>
            LIVE FEED
          </span>
          <span style={{ fontSize: '0.85rem', color: '#e2e8f0', fontWeight: 500 }}>
            {metrics?.recent_alerts?.[0]?.headline || "AI Risk Engine actively parsing live News & Social signals across 16 Index Assets."}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onSimulateEvent}
            disabled={loading}
            className="btn btn-sm btn-secondary"
          >
            <Zap size={14} color="#f59e0b" />
            <span>Process Next Signal</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-cols-4" style={{ marginBottom: '24px' }}>
        <StatCard
          title="Portfolio Valuation"
          value={`$${(totalValue / 1000000).toFixed(2)}M`}
          subtitle={`Baseline $10.00M`}
          icon={DollarSign}
          color="#10b981"
          trend={+(((totalValue - 10000000) / 10000000) * 100).toFixed(2)}
        />
        <StatCard
          title="Portfolio Sentiment"
          value={portfolioSentiment > 0 ? `+${portfolioSentiment.toFixed(2)}` : portfolioSentiment.toFixed(2)}
          subtitle={`Risk Level: ${riskLevel}`}
          icon={TrendingUp}
          color={portfolioSentiment >= 0 ? "#10b981" : "#ef4444"}
        />
        <StatCard
          title="1-Day VaR (95%)"
          value={`$${(var95 / 1000).toFixed(1)}K`}
          subtitle="Simulated Parametric Value-at-Risk"
          icon={ShieldAlert}
          color="#f59e0b"
        />
        <StatCard
          title="Engine Decisions"
          value={`${rebalanceCount} / ${stressCount}`}
          subtitle="Rebalances / Stress Tests Logged"
          icon={Activity}
          color="#3b82f6"
        />
      </div>

      {/* Charts Section */}
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
                  contentStyle={{ backgroundColor: '#151e32', borderColor: '#223048', borderRadius: '8px', color: '#f8fafc' }}
                  formatter={(val) => [`$${Number(val).toLocaleString()}`, 'Portfolio Value']}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#3b82f6' }}
                  activeDot={{ r: 7, fill: '#60a5fa' }}
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
                  contentStyle={{ backgroundColor: '#151e32', borderColor: '#223048', borderRadius: '8px', color: '#f8fafc' }}
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

      {/* Recent Risk Engine Events Feed Table */}
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
                        <span key={t} className="mono-text" style={{ fontSize: '0.72rem', background: '#1e293b', padding: '2px 6px', borderRadius: '4px', color: '#38bdf8' }}>
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
