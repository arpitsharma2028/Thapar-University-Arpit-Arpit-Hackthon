import React from 'react';
import { X } from 'lucide-react';
import SentimentBadge from './SentimentBadge';
import SeverityBadge from './SeverityBadge';
import EventCategoryBadge from './EventCategoryBadge';

export default function EventModal({ event, onClose, onRebalanceTrigger, onStressTrigger }) {
  if (!event) return null;

  const tickersList = event.tickers ? event.tickers.split(',').map(t => t.trim()) : [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '18px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="mono-text" style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                {event.event_id}
              </span>
              <EventCategoryBadge category={event.category} />
              <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)' }}>
                {event.source_type}
              </span>
            </div>
            <h2 style={{ fontSize: '1.24rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3, letterSpacing: '-0.02em' }}>
              {event.headline}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{
              width: '32px',
              height: '32px',
              padding: 0,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
            title="Close"
          >
            <X size={16} />
          </button>
        </div>

        {/* Narrative text in Liquid Glass panel */}
        <div className="glass-panel" style={{
          padding: '16px',
          marginBottom: '20px',
          fontSize: '0.88rem',
          color: '#d1d1d6',
          lineHeight: 1.6,
          boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.08)'
        }}>
          {event.text}
        </div>

        {/* Structured Signal Metrics Grid */}
        <div className="grid-cols-2" style={{ gap: '12px', marginBottom: '22px' }}>
          <div className="glass-panel" style={{ padding: '14px', boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '0.70rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px', fontWeight: 600 }}>
              Sentiment Polarity
            </div>
            <SentimentBadge score={event.sentiment_score} />
          </div>

          <div className="glass-panel" style={{ padding: '14px', boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '0.70rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px', fontWeight: 600 }}>
              Impact Severity Score
            </div>
            <SeverityBadge score={event.impact_score} />
          </div>

          <div className="glass-panel" style={{ padding: '14px', boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '0.70rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px', fontWeight: 600 }}>
              Mentioned Tickers & Sector
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
              {tickersList.map((t) => (
                <span key={t} className="mono-text" style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  color: '#f5f5f7',
                  border: '1px solid rgba(255, 255, 255, 0.20)',
                  padding: '2px 8px',
                  borderRadius: '6px',
                  fontSize: '0.74rem',
                  fontWeight: 600
                }}>
                  ${t}
                </span>
              ))}
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center' }}>
                • {event.sector}
              </span>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '14px', boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '0.70rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px', fontWeight: 600 }}>
              Signal Metadata
            </div>
            <div style={{ fontSize: '0.76rem', color: '#d1d1d6', lineHeight: 1.5 }}>
              Source: <strong style={{ color: '#fff' }}>{event.source}</strong><br />
              Confidence: <strong style={{ color: '#fff' }}>{((event.confidence || 0.9) * 100).toFixed(0)}%</strong> • {event.timestamp}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', borderTop: '1px solid var(--glass-border-subtle)', paddingTop: '16px' }}>
          <button onClick={onClose} className="btn btn-secondary">
            Close
          </button>
          {onRebalanceTrigger && (
            <button
              onClick={() => { onRebalanceTrigger(event); onClose(); }}
              className="btn btn-primary"
            >
              Trigger Module A Rebalance
            </button>
          )}
          {onStressTrigger && event.impact_score >= 7.0 && (
            <button
              onClick={() => { onStressTrigger(event); onClose(); }}
              className="btn btn-danger"
            >
              Run Module B Stress Test
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
