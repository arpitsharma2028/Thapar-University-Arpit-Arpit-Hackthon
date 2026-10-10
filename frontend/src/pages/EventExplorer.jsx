import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  RefreshCw,
  Eye,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  Globe
} from 'lucide-react';
import SentimentBadge from '../components/SentimentBadge';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';
import EventModal from '../components/EventModal';
import { fetchEvents, ingestRssFeed } from '../api/client';

export default function EventExplorer({ onRebalanceTrigger, onStressTrigger }) {
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [ingestingRss, setIngestingRss] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Filters
  const [sourceType, setSourceType] = useState("");
  const [category, setCategory] = useState("");
  const [minImpact, setMinImpact] = useState("");
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const loadEvents = async () => {
    setLoading(true);
    try {
      const data = await fetchEvents({
        source_type: sourceType || undefined,
        category: category || undefined,
        min_impact: minImpact ? parseFloat(minImpact) : undefined,
        search: search || undefined,
        limit,
        offset
      });
      setEvents(data.events || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, [sourceType, category, minImpact, offset]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setOffset(0);
    loadEvents();
  };

  const handleIngestRss = async () => {
    setIngestingRss(true);
    try {
      const res = await ingestRssFeed();
      if (res && res.ingested_count > 0) {
        setOffset(0);
        await loadEvents();
      }
    } catch (err) {
      console.error("Failed to ingest RSS:", err);
    } finally {
      setIngestingRss(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div style={{ marginBottom: '24px' }}>
        <h2 className="title-lg">Event Explorer & Signal Registry</h2>
        <p className="subtitle-sm">
          Browse, filter, and inspect verified financial news and social momentum signals processed by the NLP Risk Engine.
        </p>
      </div>

      {/* Filter and Search Bar Card */}
      <div className="glass-card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {/* Search Input */}
          <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
            <input
              type="text"
              className="form-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search headline, text body, or ticker (e.g., NVDA, rate, tariff)..."
              style={{ paddingLeft: '36px' }}
            />
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          </div>

          {/* Source Type Filter */}
          <select
            className="form-select"
            value={sourceType}
            onChange={(e) => { setSourceType(e.target.value); setOffset(0); }}
            style={{ width: '140px' }}
          >
            <option value="">All Sources</option>
            <option value="News">Financial News</option>
            <option value="Social">Social Media</option>
          </select>

          {/* Category Filter */}
          <select
            className="form-select"
            value={category}
            onChange={(e) => { setCategory(e.target.value); setOffset(0); }}
            style={{ width: '160px' }}
          >
            <option value="">All Categories</option>
            <option value="Geopolitical">Geopolitical</option>
            <option value="Macroeconomic">Macroeconomic</option>
            <option value="Credit">Credit</option>
            <option value="Earnings">Earnings</option>
            <option value="Regulatory">Regulatory</option>
            <option value="Product Launch">Product Launch</option>
            <option value="Merger/Acquisition">Merger/Acq</option>
            <option value="Market">Market</option>
          </select>

          {/* Min Impact Filter */}
          <select
            className="form-select"
            value={minImpact}
            onChange={(e) => { setMinImpact(e.target.value); setOffset(0); }}
            style={{ width: '150px' }}
          >
            <option value="">All Severities</option>
            <option value="7.0">High Risk (&ge; 7.0)</option>
            <option value="5.0">Moderate (&ge; 5.0)</option>
          </select>

          <button type="submit" className="btn btn-primary">
            <span>Apply</span>
          </button>
        </form>
      </div>

      {/* Events Table Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Showing <strong>{events.length}</strong> of <strong>{total}</strong> filtered events
          </span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={handleIngestRss}
              disabled={ingestingRss}
              className="btn btn-sm btn-primary"
              title="Fetch live public financial headlines from WSJ Markets RSS Feed"
            >
              <Globe size={13} className={ingestingRss ? "animate-spin" : ""} />
              <span>{ingestingRss ? "Ingesting RSS..." : "Ingest Live RSS"}</span>
            </button>
            <button onClick={loadEvents} className="btn btn-sm btn-outline">
              <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="custom-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Source</th>
                <th>Category</th>
                <th>Headline</th>
                <th>Tickers</th>
                <th>Sentiment</th>
                <th>Impact</th>
                <th>Confidence</th>
                <th>Timestamp</th>
                <th>View</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => (
                <tr key={ev.id || ev.event_id} style={{ cursor: 'pointer' }} onClick={() => setSelectedEvent(ev)}>
                  <td className="mono-text" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {ev.event_id}
                  </td>
                  <td>
                    <span className="badge" style={{ background: 'var(--glass-control)', color: 'var(--text-secondary)', border: '1px solid var(--glass-border)' }}>
                      {ev.source_type}
                    </span>
                  </td>
                  <td>
                    <EventCategoryBadge category={ev.category} />
                  </td>
                  <td style={{ maxWidth: '350px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 500 }}>
                    {ev.headline}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {(ev.tickers || "").split(',').slice(0, 2).map((t) => (
                        <span key={t} className="mono-text" style={{ fontSize: '0.72rem', background: 'var(--glass-control)', color: 'var(--text-primary)', border: '1px solid var(--glass-border)', padding: '2px 6px', borderRadius: '5px', fontWeight: 600 }}>
                          ${t.trim()}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <SentimentBadge score={ev.sentiment_score} />
                  </td>
                  <td>
                    <SeverityBadge score={ev.impact_score} />
                  </td>
                  <td className="mono-text" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {((ev.confidence || 0.9) * 100).toFixed(0)}%
                  </td>
                  <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                    {ev.timestamp?.split(' ')[0]}
                  </td>
                  <td>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedEvent(ev);
                      }}
                      className="btn btn-sm btn-outline"
                      style={{ padding: '4px 8px' }}
                    >
                      <Eye size={13} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--glass-border)' }}>
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="btn btn-sm btn-outline"
          >
            <ChevronLeft size={14} />
            <span>Previous</span>
          </button>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit) || 1}
          </span>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={offset + limit >= total}
            className="btn btn-sm btn-outline"
          >
            <span>Next</span>
            <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedEvent && (
        <EventModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onRebalanceTrigger={onRebalanceTrigger}
          onStressTrigger={onStressTrigger}
        />
      )}
    </div>
  );
}
