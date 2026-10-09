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
    <header className="glass-header">
      <div>
        <h1 style={{
          fontSize: '1.28rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          letterSpacing: '-0.028em',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{
            fontSize: '0.80rem',
            color: 'var(--text-secondary)',
            marginTop: '2px',
            letterSpacing: '-0.01em',
            maxWidth: '750px',
            lineHeight: 1.4
          }}>
            {subtitle}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '9px', flexShrink: 0 }}>
        {/* Coordinated Systemic Stress Pipeline Execution */}
        <button
          onClick={onRunDemo}
          disabled={loading}
          className="btn btn-primary"
          title="Executes an end-to-end systemic stress test pipeline across all engines"
        >
          <Play size={14} fill="currentColor" />
          <span>Execute Stress Pipeline</span>
        </button>

        {/* Process Next Ingested Event */}
        <button
          onClick={onSimulateEvent}
          disabled={loading}
          className="btn btn-outline"
          title="Ingest and process next sequential risk event signal"
        >
          <Activity size={14} />
          <span>Ingest Next Signal</span>
        </button>

        {/* Reset Portfolio to Baseline */}
        <button
          onClick={onResetPortfolio}
          disabled={loading}
          className="btn btn-secondary"
          title="Reset portfolio positions to baseline target weights"
        >
          <RotateCcw size={13} />
          <span>Reset Weights</span>
        </button>
      </div>
    </header>
  );
}
