import React from 'react';
import { Play, RotateCcw, Zap, Sparkles } from 'lucide-react';

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
      padding: '20px 32px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(15, 23, 42, 0.75)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em' }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '2px' }}>
            {subtitle}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* 1-Click Demo Scenario Button */}
        <button
          onClick={onRunDemo}
          disabled={loading}
          className="btn btn-primary"
          style={{
            background: 'linear-gradient(135deg, #7c3aed, #2563eb)',
            borderColor: '#9333ea',
            boxShadow: '0 0 15px rgba(124, 58, 237, 0.4)'
          }}
          title="Executes the full Hackathon Judge Demo scenario end-to-end"
        >
          <Sparkles size={16} />
          <span>Run Demo Scenario</span>
        </button>

        {/* Simulate Single Event */}
        <button
          onClick={onSimulateEvent}
          disabled={loading}
          className="btn btn-success"
          title="Simulate next event signal from the Risk Engine"
        >
          <Zap size={16} />
          <span>Simulate Event</span>
        </button>

        {/* Reset Portfolio */}
        <button
          onClick={onResetPortfolio}
          disabled={loading}
          className="btn btn-outline"
          title="Reset portfolio to baseline weights"
        >
          <RotateCcw size={15} />
          <span>Reset</span>
        </button>
      </div>
    </header>
  );
}
