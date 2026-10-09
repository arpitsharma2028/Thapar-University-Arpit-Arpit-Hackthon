import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = "var(--text-secondary)", trend }) {
  const isPositive = trend > 0;
  const isNegative = trend < 0;

  return (
    <div className="glass-card">
      {/* Subtle top specular accent line in frosted silver-white */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, rgba(255, 255, 255, 0.45) 0%, rgba(255, 255, 255, 0.12) 60%, transparent 100%)',
        zIndex: 1
      }} />

      {/* Header Row: Label */}
      <div style={{ marginBottom: '12px' }}>
        <span style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          color: 'rgba(255, 255, 255, 0.75)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em'
        }}>
          {title}
        </span>
      </div>

      {/* Metric Value with Apple Tabular Typography */}
      <div className="tabular-nums" style={{
        fontSize: '1.92rem',
        fontWeight: 700,
        color: '#ffffff',
        letterSpacing: '-0.03em',
        lineHeight: 1.15,
        textShadow: '0 2px 10px rgba(0, 0, 0, 0.25)'
      }}>
        {value}
      </div>

      {/* Subtitle / Trend Row */}
      {(subtitle || trend !== undefined) && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '7px',
          marginTop: '10px',
          fontSize: '0.78rem'
        }}>
          {trend !== undefined && (
            <span style={{
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              padding: '2px 7px',
              borderRadius: '6px',
              fontSize: '0.74rem',
              background: isPositive ? 'rgba(50, 213, 131, 0.20)' : (isNegative ? 'rgba(255, 105, 97, 0.20)' : 'rgba(255, 255, 255, 0.12)'),
              color: isPositive ? '#32d583' : (isNegative ? '#ff6961' : 'rgba(255, 255, 255, 0.75)'),
              border: `1px solid ${isPositive ? 'rgba(50, 213, 131, 0.45)' : (isNegative ? 'rgba(255, 105, 97, 0.45)' : 'rgba(255, 255, 255, 0.25)')}`,
              boxShadow: isPositive ? '0 0 10px rgba(50, 213, 131, 0.25)' : (isNegative ? '0 0 10px rgba(255, 105, 97, 0.25)' : 'none')
            }}>
              {isPositive ? `+${trend}%` : `${trend}%`}
            </span>
          )}
          {subtitle && (
            <span style={{ color: 'rgba(245, 248, 255, 0.72)', fontSize: '0.78rem' }}>
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
