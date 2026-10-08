import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = "#3b82f6", trend }) {
  return (
    <div className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Subtle top indicator bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: `linear-gradient(90deg, ${color}, transparent)`
      }} />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Icon size={18} color={color} />
          </div>
        )}
      </div>

      <div style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
        {value}
      </div>

      {(subtitle || trend) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px', fontSize: '0.78rem' }}>
          {trend && (
            <span style={{
              fontWeight: 600,
              color: trend > 0 ? 'var(--accent-emerald)' : (trend < 0 ? 'var(--accent-red)' : 'var(--text-muted)')
            }}>
              {trend > 0 ? `+${trend}%` : `${trend}%`}
            </span>
          )}
          {subtitle && (
            <span style={{ color: 'var(--text-secondary)' }}>
              {subtitle}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
