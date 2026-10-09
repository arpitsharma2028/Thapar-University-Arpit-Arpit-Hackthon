import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = "var(--text-secondary)", trend }) {
  const isPositive = trend > 0;
  const isNegative = trend < 0;

  return (
    <div className="glass-card">
      {/* Subtle delicate top edge luminance */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.03) 50%, transparent 100%)',
        zIndex: 1
      }} />

      {/* Header Row: Label */}
      <div style={{ marginBottom: '12px' }}>
        <span style={{
          fontSize: '0.72rem',
          fontWeight: 600,
          color: 'var(--text-muted)',
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
        color: 'var(--text-primary)',
        letterSpacing: '-0.03em',
        lineHeight: 1.15
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
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              padding: '2px 7px',
              borderRadius: '6px',
              fontSize: '0.74rem',
              background: isPositive ? 'rgba(50, 213, 131, 0.14)' : (isNegative ? 'rgba(255, 105, 97, 0.14)' : 'var(--glass-control)'),
              color: isPositive ? 'var(--accent-positive)' : (isNegative ? 'var(--accent-negative)' : 'var(--text-secondary)'),
              border: `1px solid ${isPositive ? 'rgba(50, 213, 131, 0.28)' : (isNegative ? 'rgba(255, 105, 97, 0.28)' : 'var(--glass-border)')}`
            }}>
              {isPositive ? `+${trend}%` : `${trend}%`}
            </span>
          )}
          {subtitle && (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
