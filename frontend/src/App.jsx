import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Overview from './pages/Overview';
import RiskIntelligence from './pages/RiskIntelligence';
import ModuleARebalancer from './pages/ModuleARebalancer';
import ModuleBStressTesting from './pages/ModuleBStressTesting';
import MarketIntelligence from './pages/MarketIntelligence';
import EventExplorer from './pages/EventExplorer';
import SimulationHistory from './pages/SimulationHistory';
import {
  fetchMetrics,
  fetchPortfolio,
  simulateEvents,
  resetPortfolio,
  executeRebalance,
  runDemoScenario
} from './api/client';
import { CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [lastRebalanceResult, setLastRebalanceResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadPlatformData = async () => {
    try {
      const [m, p] = await Promise.all([fetchMetrics(), fetchPortfolio()]);
      setMetrics(m);
      setPortfolio(p);
    } catch (err) {
      console.error("Failed to load initial data:", err);
    }
  };

  useEffect(() => {
    loadPlatformData();
    const interval = setInterval(loadPlatformData, 10000); // 10s polling
    return () => clearInterval(interval);
  }, []);

  // End-to-end Systemic Risk Pipeline Simulation
  const handleRunDemoScenario = async () => {
    setLoading(true);
    showToast("Executing systemic risk pipeline simulation...", "info");
    try {
      const result = await runDemoScenario();
      setLastRebalanceResult(result.step_2_module_a_rebalance);
      await loadPlatformData();
      showToast(
        `Systemic shock processed: Geopolitical event parsed -> Index rebalanced -> Wholesale stress loss: -$${(result.step_3_module_b_stress_test.total_dollar_loss / 1000000).toFixed(2)}M`,
        "success"
      );
      setActiveTab('overview');
    } catch (err) {
      console.error(err);
      showToast("Failed to execute stress pipeline. Verify backend service is online.", "error");
    } finally {
      setLoading(false);
    }
  };

  // Simulate Next Single Event
  const handleSimulateEvent = async (sensitivity = 0.025) => {
    setLoading(true);
    try {
      const res = await simulateEvents(1, sensitivity);
      if (res.steps && res.steps.length > 0) {
        const step = res.steps[0];
        setLastRebalanceResult({
          trigger_event: {
            event_id: step.event_id,
            headline: step.headline,
            sentiment_score: step.sentiment,
            impact_score: step.impact,
            category: "Market"
          },
          value_change: step.value_change,
          value_change_pct: ((step.value_change / (step.portfolio_value_after - step.value_change)) * 100).toFixed(2)
        });
        await loadPlatformData();
        showToast(`Processed signal ${step.event_id}: Portfolio shifted by $${Math.round(step.value_change).toLocaleString()}`, "success");
      }
    } catch (err) {
      console.error(err);
      showToast("Error simulating event.", "error");
    } finally {
      setLoading(false);
    }
  };

  // Simulate Batch of 5 Events
  const handleSimulateBatch = async (count = 5, sensitivity = 0.025) => {
    setLoading(true);
    showToast(`Simulating batch of ${count} real-time event signals...`, "info");
    try {
      const res = await simulateEvents(count, sensitivity);
      await loadPlatformData();
      showToast(`Batch completed: ${res.events_simulated} events processed dynamically!`, "success");
    } catch (err) {
      console.error(err);
      showToast("Batch simulation error.", "error");
    } finally {
      setLoading(false);
    }
  };

  // Reset Portfolio to Baseline
  const handleResetPortfolio = async () => {
    setLoading(true);
    try {
      await resetPortfolio();
      setLastRebalanceResult(null);
      await loadPlatformData();
      showToast("Portfolio successfully reset to baseline target allocations.", "info");
    } catch (err) {
      console.error(err);
      showToast("Reset failed.", "error");
    } finally {
      setLoading(false);
    }
  };

  // Trigger Rebalance from an event
  const handleRebalanceTrigger = async (event) => {
    setLoading(true);
    try {
      const res = await executeRebalance({
        event_id: event.event_id,
        headline: event.headline,
        tickers: event.tickers,
        sector: event.sector,
        sentiment_score: event.sentiment_score,
        impact_score: event.impact_score
      });
      setLastRebalanceResult(res);
      await loadPlatformData();
      setActiveTab('module-a');
      showToast(`Applied ${event.event_id} to Tactical Rebalancer. Weight adjustments logged.`, "success");
    } catch (err) {
      console.error(err);
      showToast("Rebalance execution failed.", "error");
    } finally {
      setLoading(false);
    }
  };

  // Trigger Stress Test from high-impact event
  const handleStressTrigger = (event) => {
    setActiveTab('module-b');
    showToast(`Forwarded high-severity event (${event.impact_score}/10) to Wholesale Stress Testing engine.`, "warning");
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case 'overview': return { title: 'Executive Overview', subtitle: 'Integrated market risk signals, index health, and multi-asset wholesale portfolio surveillance' };
      case 'risk-engine': return { title: 'Unified AI / NLP Risk Intelligence', subtitle: 'Real-time NLP entity extraction, continuous sentiment polarity, and predictive severity scoring' };
      case 'module-a': return { title: 'Module A — Tactical Index Rebalancer', subtitle: 'Dynamic weight optimization responding to sentiment signals with bounded sensitivity' };
      case 'module-b': return { title: 'Module B — Strategic Stress Testing', subtitle: 'Multi-asset wholesale banking stress simulation for catastrophic events' };
      case 'market-intel': return { title: 'Market Analytics & Monte Carlo Forecasting', subtitle: 'Geometric Brownian Motion probability cone (GBM), Yahoo Finance data, and multi-stock Pearson correlation' };
      case 'events': return { title: 'Event Explorer & Signal Registry', subtitle: 'Filterable database of parsed financial news articles and social media sentiment feeds' };
      case 'history': return { title: 'Simulation History & Audit Trail', subtitle: 'Chronological ledger of programmatic rebalance decisions and stress test executions' };
      default: return { title: 'FinSight AI', subtitle: 'Market & Portfolio Risk Intelligence' };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="main-content">
        <Header
          title={title}
          subtitle={subtitle}
          onRunDemo={handleRunDemoScenario}
          onSimulateEvent={() => handleSimulateEvent(0.025)}
          onResetPortfolio={handleResetPortfolio}
          loading={loading}
        />

        <main style={{ flex: 1 }}>
          {activeTab === 'overview' && (
            <Overview
              metrics={metrics}
              portfolio={portfolio}
              onRunDemo={handleRunDemoScenario}
              onSimulateEvent={() => handleSimulateEvent(0.025)}
              onRebalanceTrigger={handleRebalanceTrigger}
              onStressTrigger={handleStressTrigger}
              onNavigateTab={setActiveTab}
              loading={loading}
            />
          )}

          {activeTab === 'risk-engine' && (
            <RiskIntelligence
              metrics={metrics}
              onRebalanceTrigger={handleRebalanceTrigger}
              onStressTrigger={handleStressTrigger}
              showToast={showToast}
            />
          )}

          {activeTab === 'module-a' && (
            <ModuleARebalancer
              portfolio={portfolio}
              onSimulateEvent={handleSimulateEvent}
              onSimulateBatch={handleSimulateBatch}
              onResetPortfolio={handleResetPortfolio}
              lastRebalanceResult={lastRebalanceResult}
              loading={loading}
            />
          )}

          {activeTab === 'module-b' && (
            <ModuleBStressTesting
              showToast={showToast}
            />
          )}

          {activeTab === 'market-intel' && (
            <MarketIntelligence
              showToast={showToast}
            />
          )}

          {activeTab === 'events' && (
            <EventExplorer
              onRebalanceTrigger={handleRebalanceTrigger}
              onStressTrigger={handleStressTrigger}
            />
          )}

          {activeTab === 'history' && (
            <SimulationHistory />
          )}
        </main>
      </div>

      {/* Toast Notification Banner */}
      {toast && (
        <div className="toast-banner">
          {toast.type === 'success' && <CheckCircle2 size={18} color="#10b981" />}
          {toast.type === 'warning' && <AlertTriangle size={18} color="#f59e0b" />}
          {toast.type === 'error' && <AlertTriangle size={18} color="#ef4444" />}
          {toast.type === 'info' && <Info size={18} color="#3b82f6" />}
          <span style={{ fontSize: '0.86rem', color: '#f8fafc', fontWeight: 500 }}>
            {toast.message}
          </span>
        </div>
      )}
    </div>
  );
}
