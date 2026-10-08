import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  Flame,
  TrendingDown,
  Layers,
  DollarSign,
  Play,
  RotateCcw,
  Sliders,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie
} from 'recharts';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';
import { fetchStressScenarios, fetchWholesalePortfolio, runStressTest } from '../api/client';

export default function ModuleBStressTesting({ showToast }) {
  const [scenarios, setScenarios] = useState([]);
  const [wholesalePortfolio, setWholesalePortfolio] = useState(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [severityMultiplier, setSeverityMultiplier] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [stressResult, setStressResult] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const scens = await fetchStressScenarios();
        setScenarios(scens);
        if (scens.length > 0) setSelectedScenarioId(scens[0].id);

        const port = await fetchWholesalePortfolio();
        setWholesalePortfolio(port);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  const handleRunStress = async (scenId = selectedScenarioId) => {
    setLoading(true);
    try {
      const res = await runStressTest({
        scenario_id: scenId,
        severity_multiplier: severityMultiplier
      });
      setStressResult(res);
      if (showToast) showToast(`Executed Stress Simulation: Loss of $${(res.total_dollar_loss / 1000000).toFixed(2)}M (${res.total_loss_pct}%)`, "warning");
    } catch (err) {
      console.error(err);
      if (showToast) showToast("Failed to execute stress test.", "error");
    } finally {
      setLoading(false);
    }
  };

  const selectedScenario = scenarios.find(s => s.id === selectedScenarioId) || scenarios[0];

  // Asset impact chart data
  const assetChartData = stressResult?.asset_impacts
    ? Object.entries(stressResult.asset_impacts).map(([asset, data]) => ({
        asset,
        valueBefore: Math.round(data.value_before / 1000000 * 10) / 10,
        valueAfter: Math.round(data.value_after / 1000000 * 10) / 10,
        dollarLoss: Math.round(data.dollar_loss / 1000000 * 10) / 10,
        lossPct: data.loss_pct
      }))
    : [];

  // Sector shock chart data
  const sectorChartData = stressResult?.sector_shocks
    ? Object.entries(stressResult.sector_shocks).map(([sec, data]) => ({
        sector: sec,
        shockPct: data.shock_pct,
        dollarLoss: Math.round(data.dollar_loss / 1000)
      }))
    : [];

  return (
    <div className="page-wrapper">
      {/* Title Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge" style={{ background: '#ef444420', color: '#f87171', border: '1px solid #ef444440' }}>
            MODULE B
          </span>
          <h2 className="title-lg">Strategic Wholesale Portfolio Stress Testing</h2>
        </div>
        <p className="subtitle-sm">
          Multi-asset catastrophic risk simulation engine testing extreme shocks on wholesale banking books ($50M across Equities, Bonds, Derivatives, Cash).
        </p>
      </div>

      {/* Scenario Selection & Controls Card */}
      <div className="glass-card" style={{ marginBottom: '24px', border: '1px solid rgba(239, 68, 68, 0.35)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Flame size={20} color="#ef4444" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Stress Scenario Selector & Parameter Calibration
            </h3>
          </div>
          <span className="badge badge-severity-high">
            High-Impact Trigger Threshold &ge; 7.0
          </span>
        </div>

        {/* Scenario Buttons */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', marginBottom: '20px' }}>
          {scenarios.map((scen) => {
            const isSelected = selectedScenarioId === scen.id;
            return (
              <div
                key={scen.id}
                onClick={() => setSelectedScenarioId(scen.id)}
                style={{
                  background: isSelected ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-card)',
                  border: isSelected ? '1px solid #ef4444' : '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '14px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <EventCategoryBadge category={scen.category} />
                  <span className="mono-text" style={{ fontSize: '0.72rem', color: '#ef4444', fontWeight: 700 }}>
                    Severity {scen.severity}/10
                  </span>
                </div>
                <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                  {scen.name}
                </div>
                <div style={{ fontSize: '0.74rem', color: '#94a3b8', lineHeight: 1.4 }}>
                  {scen.description.slice(0, 85)}...
                </div>
              </div>
            );
          })}
        </div>

        {/* Parameter Adjuster & Execute Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', minWidth: '320px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#e2e8f0' }}>
              Severity Multiplier:
            </span>
            <input
              type="range"
              min="0.5"
              max="2.5"
              step="0.1"
              value={severityMultiplier}
              onChange={(e) => setSeverityMultiplier(parseFloat(e.target.value))}
              style={{ flex: 1, accentColor: '#ef4444', cursor: 'pointer' }}
            />
            <span className="mono-text" style={{ fontSize: '0.88rem', fontWeight: 700, color: '#ef4444', minWidth: '40px' }}>
              {severityMultiplier.toFixed(1)}x
            </span>
          </div>

          <button
            onClick={() => handleRunStress()}
            disabled={loading}
            className="btn btn-danger btn-lg"
            style={{ boxShadow: '0 0 16px rgba(239, 68, 68, 0.4)' }}
          >
            <Play size={18} />
            <span>{loading ? "Simulating Systemic Shock..." : "Execute Stress Test"}</span>
          </button>
        </div>
      </div>

      {/* Stress Results Display (If executed) */}
      {stressResult && (
        <div style={{ marginBottom: '28px' }}>
          {/* Top Loss KPI Row */}
          <div className="grid-cols-4" style={{ marginBottom: '20px' }}>
            <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                Pre-Stress Wholesale Value
              </div>
              <div className="mono-text" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#f8fafc', marginTop: '4px' }}>
                ${(stressResult.total_value_before / 1000000).toFixed(2)}M
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                100% Book Capital
              </div>
            </div>

            <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.6)', background: 'rgba(239, 68, 68, 0.08)' }}>
              <div style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', fontWeight: 600 }}>
                Total Simulated Capital Loss
              </div>
              <div className="mono-text" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#ef4444', marginTop: '4px' }}>
                -${(stressResult.total_dollar_loss / 1000000).toFixed(2)}M
              </div>
              <div style={{ fontSize: '0.78rem', color: '#f87171', marginTop: '4px', fontWeight: 700 }}>
                -{stressResult.total_loss_pct}% of Portfolio
              </div>
            </div>

            <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                Post-Stress Book Value
              </div>
              <div className="mono-text" style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
                ${(stressResult.total_value_after / 1000000).toFixed(2)}M
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                Residual Capital Cushion
              </div>
            </div>

            <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                Scenario Calibrated Severity
              </div>
              <div style={{ marginTop: '8px' }}>
                <SeverityBadge score={stressResult.severity} />
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '8px' }}>
                Multiplier: {stressResult.severity_multiplier}x
              </div>
            </div>
          </div>

          {/* Asset Class Impact & Equity Sector Breakdown Charts */}
          <div className="grid-cols-2" style={{ marginBottom: '24px' }}>
            {/* Asset Class Loss Bar Chart */}
            <div className="glass-card">
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                Asset Class Loss Distribution ($ Millions)
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                Wholesale banking book impact: Equities, Bonds, Derivatives, Cash
              </p>
              <div style={{ height: '240px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={assetChartData} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
                    <XAxis dataKey="asset" stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `$${val}M`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#151e32', borderColor: '#223048', borderRadius: '8px', color: '#f8fafc' }}
                      formatter={(val, name) => [`$${val}M`, name === 'dollarLoss' ? 'Loss Amount' : name]}
                    />
                    <Bar dataKey="dollarLoss" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Worst Affected Positions Card */}
            <div className="glass-card">
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                Worst Affected Sector Exposures
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                Concentrated downside vulnerabilities under scenario {stressResult.scenario.id}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {stressResult.worst_positions.map((pos, idx) => (
                  <div
                    key={pos.sector}
                    style={{
                      background: 'rgba(15, 23, 42, 0.7)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      padding: '12px 16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className="mono-text" style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700 }}>
                        #{idx + 1}
                      </span>
                      <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.9rem' }}>
                        {pos.sector} Sector
                      </span>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="mono-text" style={{ fontWeight: 700, color: '#ef4444', fontSize: '0.9rem' }}>
                        -${Math.round(pos.dollar_loss).toLocaleString()}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#fca5a5' }}>
                        {pos.loss_pct}% Shock
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Baseline Wholesale Portfolio Structure Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Baseline Wholesale Banking Asset Portfolio ($50.0M)
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Structured wholesale multi-asset balance sheet exposures (Simulated Demo Data)
            </p>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Asset Class</th>
                <th>Nominal Value</th>
                <th>Target Allocation</th>
                <th>Typical Risk Factor</th>
                <th>Primary Stress Transmission</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 700, color: '#60a5fa' }}>Equities Book</td>
                <td className="mono-text">$22,500,000</td>
                <td className="mono-text">45.0%</td>
                <td>Market Beta & Sector Earnings Multiples</td>
                <td>Direct equity drawdown & multiple compression</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 700, color: '#34d399' }}>Sovereign & Corporate Bonds</td>
                <td className="mono-text">$15,000,000</td>
                <td className="mono-text">30.0%</td>
                <td>Duration & Credit Spreads</td>
                <td>Yield curve steepening / credit default widening</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 700, color: '#f472b6' }}>Derivatives Portfolio</td>
                <td className="mono-text">$7,500,000</td>
                <td className="mono-text">15.0%</td>
                <td>Vega (Volatility) & Counterparty Exposure</td>
                <td>VIX spike, margin calls, liquidity freeze</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 700, color: '#fcd34d' }}>Cash & Equivalents</td>
                <td className="mono-text">$5,000,000</td>
                <td className="mono-text">10.0%</td>
                <td>Inflation & Real Rate Deprecation</td>
                <td>Safe haven liquidity buffer (zero principal loss)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
