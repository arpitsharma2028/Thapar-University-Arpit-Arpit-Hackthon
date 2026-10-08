import React, { useState, useEffect } from 'react';
import {
  History,
  TrendingUp,
  ShieldAlert,
  Calendar,
  CheckCircle2,
  DollarSign,
  ArrowRight
} from 'lucide-react';
import SentimentBadge from '../components/SentimentBadge';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';
import { fetchRebalanceHistory, fetchStressHistory } from '../api/client';

export default function SimulationHistory() {
  const [activeTab, setActiveTab] = useState("rebalance");
  const [rebalanceHistory, setRebalanceHistory] = useState([]);
  const [stressHistory, setStressHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      try {
        const reb = await fetchRebalanceHistory(50);
        setRebalanceHistory(reb || []);
        const stress = await fetchStressHistory(20);
        setStressHistory(stress || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [activeTab]);

  return (
    <div className="page-wrapper">
      <div style={{ marginBottom: '24px' }}>
        <h2 className="title-lg">Simulation History & Regulatory Audit Log</h2>
        <p className="subtitle-sm">
          Immutable audit record of all programmatic index rebalances and wholesale portfolio stress simulations executed by FinSight AI.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab("rebalance")}
          className={`btn ${activeTab === 'rebalance' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <TrendingUp size={16} />
          <span>Module A — Rebalance Decisions ({rebalanceHistory.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("stress")}
          className={`btn ${activeTab === 'stress' ? 'btn-danger' : 'btn-secondary'}`}
        >
          <ShieldAlert size={16} />
          <span>Module B — Stress Test History ({stressHistory.length})</span>
        </button>
      </div>

      {/* Rebalance History View */}
      {activeTab === 'rebalance' && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Tactical Index Rebalance Log
            </h3>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              Formula-driven executions
            </span>
          </div>

          <div className="table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Trigger Event</th>
                  <th>Sentiment</th>
                  <th>Impact</th>
                  <th>Affected Tickers</th>
                  <th>Value Shift</th>
                  <th>Post-Valuation</th>
                </tr>
              </thead>
              <tbody>
                {rebalanceHistory.length === 0 ? (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
                      No rebalance decisions recorded yet. Simulate an event from the top bar to record history.
                    </td>
                  </tr>
                ) : (
                  rebalanceHistory.map((row) => {
                    const valBefore = row.portfolio_value_before || 10000000;
                    const valAfter = row.portfolio_value_after || 10000000;
                    const delta = valAfter - valBefore;
                    const deltaPct = ((delta / valBefore) * 100).toFixed(2);
                    return (
                      <tr key={row.id}>
                        <td className="mono-text" style={{ fontSize: '0.75rem', color: '#94a3b8', whiteSpace: 'nowrap' }}>
                          {row.timestamp}
                        </td>
                        <td style={{ maxWidth: '320px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          <span className="mono-text" style={{ fontSize: '0.72rem', color: '#60a5fa', marginRight: '6px' }}>
                            [{row.trigger_event_id}]
                          </span>
                          <span style={{ fontWeight: 500 }}>{row.trigger_headline}</span>
                        </td>
                        <td>
                          <SentimentBadge score={row.trigger_sentiment} />
                        </td>
                        <td>
                          <SeverityBadge score={row.trigger_impact} />
                        </td>
                        <td>
                          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                            {(row.affected_tickers || "").split(',').map((t) => (
                              <span key={t} className="mono-text" style={{ fontSize: '0.72rem', background: '#1e293b', padding: '2px 5px', borderRadius: '4px', color: '#38bdf8' }}>
                                ${t.trim()}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="mono-text" style={{
                          fontWeight: 700,
                          color: delta >= 0 ? '#10b981' : '#ef4444'
                        }}>
                          {delta >= 0 ? '+' : ''}${Math.round(delta).toLocaleString()} ({deltaPct}%)
                        </td>
                        <td className="mono-text" style={{ fontWeight: 600, color: '#f8fafc' }}>
                          ${(valAfter / 1000000).toFixed(2)}M
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Stress Tests History View */}
      {activeTab === 'stress' && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Wholesale Portfolio Stress Test Audit Trail
            </h3>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              Simulated Catastrophic Events
            </span>
          </div>

          <div className="table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Test ID</th>
                  <th>Timestamp</th>
                  <th>Scenario</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Capital Loss ($)</th>
                  <th>Loss (%)</th>
                  <th>Post-Shock Value</th>
                </tr>
              </thead>
              <tbody>
                {stressHistory.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
                      No wholesale stress tests recorded yet. Execute a scenario from Module B to populate the audit trail.
                    </td>
                  </tr>
                ) : (
                  stressHistory.map((row) => (
                    <tr key={row.id || row.test_id}>
                      <td className="mono-text" style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        {row.test_id}
                      </td>
                      <td className="mono-text" style={{ fontSize: '0.75rem', color: '#64748b', whiteSpace: 'nowrap' }}>
                        {row.timestamp}
                      </td>
                      <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                        {row.scenario_name}
                      </td>
                      <td>
                        <EventCategoryBadge category={row.category} />
                      </td>
                      <td>
                        <SeverityBadge score={row.severity} />
                      </td>
                      <td className="mono-text" style={{ fontWeight: 700, color: '#ef4444' }}>
                        -${(row.total_loss / 1000000).toFixed(2)}M
                      </td>
                      <td className="mono-text" style={{ fontWeight: 700, color: '#f87171' }}>
                        -{row.loss_pct}%
                      </td>
                      <td className="mono-text" style={{ fontWeight: 600, color: '#38bdf8' }}>
                        ${(row.value_after / 1000000).toFixed(2)}M
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
