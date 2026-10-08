import React from 'react';
import { X, Calendar, Globe, Cpu, AlertTriangle } from 'lucide-react';
import SentimentBadge from './SentimentBadge';
import SeverityBadge from './SeverityBadge';
import EventCategoryBadge from './EventCategoryBadge';

export default function EventModal({ event, onClose, onRebalanceTrigger, onStressTrigger }) {
  if (!event) return null;

  const tickersList = event.tickers ? event.tickers.split(',').map(t => t.trim()) : [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="mono-text" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {event.event_id}
              </span>
              <EventCategoryBadge category={event.category} />
              <span className="badge" style={{ background: '#1e293b', color: '#94a3b8' }}>
                {event.source_type}
              </span>
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3 }}>
              {event.headline}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="btn btn-outline"
            style={{ padding: '6px', borderRadius: '50%' }}
          >
            <X size={18} />
          </button>
        </div>

        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '14px',
          marginBottom: '20px',
          fontSize: '0.88rem',
          color: '#cbd5e1',
          lineHeight: 1.6
        }}>
          {event.text}
        </div>

        {/* Structured Signal Metrics Grid */}
        <div className="grid-cols-2" style={{ gap: '12px', marginBottom: '20px' }}>
          <div style={{ background: 'var(--bg-input)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Sentiment Polarity
            </div>
            <SentimentBadge score={event.sentiment_score} />
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Impact Severity Score
            </div>
            <SeverityBadge score={event.impact_score} />
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Mentioned Tickers & Sector
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
              {tickersList.map((t) => (
                <span key={t} className="mono-text" style={{ background: '#2563eb25', color: '#60a5fa', border: '1px solid #3b82f640', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                  ${t}
                </span>
              ))}
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', alignSelf: 'center' }}>
                • {event.sector}
              </span>
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Signal Metadata
            </div>
            <div style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>
              Source: <strong>{event.source}</strong><br />
              Confidence: <strong>{((event.confidence || 0.9) * 100).toFixed(0)}%</strong> • {event.timestamp}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
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
