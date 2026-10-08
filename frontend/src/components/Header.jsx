import React from 'react';
import { Play, RotateCcw, Activity } from 'lucide-react';

export default function Header({
  title,
  subtitle,
  onRunDemo,
  onSimulateEvent,
  onResetPortfolio,
  loading
}) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '18px 32px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div>
        <h1 style={{ fontSize: '1.35rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em' }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{ fontSize: '0.80rem', color: '#94a3b8', marginTop: '2px' }}>
            {subtitle}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Coordinated Systemic Stress Pipeline Execution */}
        <button
          onClick={onRunDemo}
          disabled={loading}
          className="btn btn-primary"
          style={{
            background: '#2563eb',
            borderColor: '#3b82f6',
            color: '#ffffff'
          }}
          title="Executes an end-to-end systemic stress test pipeline across all engines"
        >
          <Play size={15} />
          <span>Execute Stress Pipeline</span>
        </button>

        {/* Process Next Ingested Event */}
        <button
          onClick={onSimulateEvent}
          disabled={loading}
          className="btn btn-outline"
          style={{
            borderColor: 'rgba(56, 189, 248, 0.4)',
            color: '#38bdf8'
          }}
          title="Ingest and process next sequential risk event signal"
        >
          <Activity size={15} />
          <span>Ingest Next Signal</span>
        </button>

        {/* Reset Portfolio to Baseline */}
        <button
          onClick={onResetPortfolio}
          disabled={loading}
          className="btn btn-outline"
          title="Reset portfolio positions to baseline target weights"
        >
          <RotateCcw size={14} />
          <span>Reset Weights</span>
        </button>
      </div>
    </header>
  );
}
