import React, { useState } from 'react';
import {
  TrendingUp,
  RotateCcw,
  Zap,
  Sliders,
  Layers,
  ArrowUp,
  ArrowDown,
  Info,
  CheckCircle2,
  DollarSign
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell
} from 'recharts';
import SentimentBadge from '../components/SentimentBadge';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';

export default function ModuleARebalancer({
  portfolio,
  onSimulateEvent,
  onSimulateBatch,
  onResetPortfolio,
  lastRebalanceResult,
  loading
}) {
  const [sensitivity, setSensitivity] = useState(0.025);

  const positions = portfolio?.positions || [];
  const totalVal = portfolio?.total_value || 10000000;
  const portfolioSentiment = portfolio?.portfolio_sentiment ?? 0.0;

  // Comparison data for Recharts (Before vs After)
  const comparisonData = positions.map((p) => {
    // If we have lastRebalanceResult with updated_positions, map old vs new
    let oldW = p.target_weight * 100;
    let newW = p.current_weight * 100;

    if (lastRebalanceResult?.updated_positions) {
      const match = lastRebalanceResult.updated_positions.find(x => x.ticker === p.ticker);
      if (match) {
        oldW = match.old_weight * 100;
        newW = match.new_weight * 100;
      }
    }

    return {
      ticker: p.ticker,
      oldWeight: parseFloat(oldW.toFixed(2)),
      newWeight: parseFloat(newW.toFixed(2)),
      delta: parseFloat((newW - oldW).toFixed(2))
    };
  });

  return (
    <div className="page-wrapper">
      {/* Header & Controls Bar */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-neutral">
              MODULE A
            </span>
            <h2 className="title-lg">Tactical High-Frequency Index Rebalancer</h2>
          </div>
          <p className="subtitle-sm">
            Continuous dynamic rebalancing engine responding to real-time sentiment signals with bounded sensitivity and weight normalization.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => onSimulateEvent(sensitivity)}
            disabled={loading}
            className="btn btn-primary"
          >
            <Zap size={16} />
            <span>Simulate Next Event</span>
          </button>

          <button
            onClick={() => onSimulateBatch(5, sensitivity)}
            disabled={loading}
            className="btn btn-secondary"
          >
            <span>Batch Simulate (5 Events)</span>
          </button>

          <button
            onClick={onResetPortfolio}
            disabled={loading}
            className="btn btn-outline"
            title="Reset to baseline weights"
          >
            <RotateCcw size={15} />
            <span>Reset Baseline</span>
          </button>
        </div>
      </div>

      {/* Rebalance Algorithm & Sensitivity Control Banner */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div className="grid-cols-12" style={{ alignItems: 'center' }}>
          {/* Formula Explanation */}
          <div style={{ gridColumn: 'span 8' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <Info size={16} color="var(--text-primary)" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Algorithmic Weight Rebalance Formula
              </span>
            </div>
            <div className="mono-text glass-panel" style={{
              padding: '10px 14px',
              fontSize: '0.84rem',
              color: 'var(--text-primary)',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--glass-border)',
              boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.1)'
            }}>
              new_weight<sub>i</sub> = clamp(old_weight<sub>i</sub> + &lambda; &times; sentiment &times; (impact / 10), min=1.0%, max=25.0%)<br />
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.78rem' }}>
                &rarr; Normalized: weight<sub>i</sub> = new_weight<sub>i</sub> / &sum; new_weight &nbsp;|&nbsp; Guarantees &sum; w<sub>i</sub> &equiv; 100.0%, w<sub>i</sub> &ge; 1.0%
              </span>
            </div>
          </div>

          {/* Sensitivity Slider Control */}
          <div style={{ gridColumn: 'span 4', borderLeft: '1px solid var(--border-color)', paddingLeft: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#e2e8f0' }}>
                Sensitivity Parameter (&lambda;)
              </span>
              <span className="mono-text" style={{ fontSize: '0.85rem', fontWeight: 700, color: '#3b82f6' }}>
                {sensitivity.toFixed(3)}
              </span>
            </div>
            <input
              type="range"
              min="0.010"
              max="0.060"
              step="0.005"
              value={sensitivity}
              onChange={(e) => setSensitivity(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#3b82f6', cursor: 'pointer' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#64748b', marginTop: '4px' }}>
              <span>Conservative (0.010)</span>
              <span>Aggressive (0.060)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Last Trigger Event Banner (If available) */}
      {lastRebalanceResult?.trigger_event && (
        <div className="glass-panel" style={{
          background: 'linear-gradient(90deg, rgba(255, 255, 255, 0.09) 0%, rgba(255, 255, 255, 0.03) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.20)',
          borderRadius: '14px',
          padding: '14px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          boxShadow: 'var(--shadow-sm), inset 0 1px 1px rgba(255, 255, 255, 0.12)'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <CheckCircle2 size={16} color="#10b981" />
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f5f5f7', textTransform: 'uppercase' }}>
                Latest Rebalance Trigger Event
              </span>
              <EventCategoryBadge category={lastRebalanceResult.trigger_event.category} />
              <span className="mono-text" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                {lastRebalanceResult.trigger_event.event_id}
              </span>
            </div>
            <div style={{ fontSize: '0.9rem', color: '#f1f5f9', fontWeight: 500 }}>
              {lastRebalanceResult.trigger_event.headline}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <SentimentBadge score={lastRebalanceResult.trigger_event.sentiment_score} />
            <SeverityBadge score={lastRebalanceResult.trigger_event.impact_score} />
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Portfolio Value Shift</div>
              <div className="mono-text" style={{
                fontSize: '0.9rem',
                fontWeight: 700,
                color: (lastRebalanceResult.value_change || 0) >= 0 ? '#10b981' : '#ef4444'
              }}>
                {(lastRebalanceResult.value_change || 0) >= 0 ? '+' : ''}${Number(lastRebalanceResult.value_change || 0).toLocaleString()} ({lastRebalanceResult.value_change_pct}%)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Before vs After Allocation Chart */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Stock Allocation Weight Changes (Before vs After)
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Comparison of baseline vs active dynamically adjusted weights across 16 public tickers (%)
            </p>
          </div>
          <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', background: '#475569', borderRadius: '2px' }}></span>
              Before Rebalance
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '10px', height: '10px', background: '#3b82f6', borderRadius: '2px' }}></span>
              After Rebalance
            </span>
          </div>
        </div>

        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
              <XAxis dataKey="ticker" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `${val}%`} />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(32, 33, 36, 0.90)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: '1px solid rgba(255, 255, 255, 0.22)', borderRadius: '10px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)', color: '#f5f5f7' }}
                formatter={(val, name) => [`${val}%`, name === 'oldWeight' ? 'Before Rebalance' : 'After Rebalance']}
              />
              <Bar dataKey="oldWeight" fill="#475569" radius={[3, 3, 0, 0]} />
              <Bar dataKey="newWeight" fill="#3b82f6" radius={[3, 3, 0, 0]}>
                {comparisonData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.delta > 0.1 ? '#10b981' : (entry.delta < -0.1 ? '#ef4444' : '#3b82f6')}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stock Portfolio Allocation Table */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              16-Asset Portfolio Positions & Sentiment Status
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Total Index Value: <strong>${(totalVal / 1000000).toFixed(2)}M</strong> • Portfolio Sentiment: <strong>{portfolioSentiment.toFixed(2)}</strong>
            </p>
          </div>
          <span className="mono-text" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Weights Total: <strong>{(positions.reduce((acc, p) => acc + p.current_weight, 0) * 100).toFixed(1)}%</strong>
          </span>
        </div>

        <div className="table-wrapper">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Ticker & Name</th>
                <th>Sector</th>
                <th>Current Weight</th>
                <th>Target Weight</th>
                <th>Weight Delta</th>
                <th>Position Value</th>
                <th>Share Price</th>
                <th>Local Sentiment</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p) => {
                const delta = (p.current_weight - p.target_weight) * 100;
                const deltaBps = Math.round(delta * 100);
                return (
                  <tr key={p.ticker}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>
                        ${p.ticker}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        {p.name}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>
                        {p.sector}
                      </span>
                    </td>
                    <td className="mono-text" style={{ fontWeight: 700, color: '#60a5fa' }}>
                      {(p.current_weight * 100).toFixed(2)}%
                    </td>
                    <td className="mono-text" style={{ color: '#94a3b8' }}>
                      {(p.target_weight * 100).toFixed(2)}%
                    </td>
                    <td>
                      <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: delta > 0.05 ? '#10b981' : (delta < -0.05 ? '#ef4444' : '#94a3b8'),
                        fontWeight: 600,
                        fontSize: '0.78rem'
                      }}>
                        {delta > 0.05 ? <ArrowUp size={12} /> : (delta < -0.05 ? <ArrowDown size={12} /> : null)}
                        {delta > 0 ? `+${delta.toFixed(2)}%` : `${delta.toFixed(2)}%`} ({deltaBps > 0 ? `+${deltaBps}` : deltaBps} bps)
                      </div>
                    </td>
                    <td className="mono-text" style={{ fontWeight: 600 }}>
                      ${Math.round(p.position_value).toLocaleString()}
                    </td>
                    <td className="mono-text" style={{ color: '#94a3b8' }}>
                      ${p.current_price?.toFixed(2)}
                    </td>
                    <td>
                      <SentimentBadge score={p.sentiment ?? 0.0} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
