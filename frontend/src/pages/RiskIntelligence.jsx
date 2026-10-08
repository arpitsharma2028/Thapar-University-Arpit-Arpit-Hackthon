import React, { useState } from 'react';
import {
  Cpu,
  Send,
  Zap,
  Tag,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Globe,
  MessageSquare
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell
} from 'recharts';
import SentimentBadge from '../components/SentimentBadge';
import SeverityBadge from '../components/SeverityBadge';
import EventCategoryBadge from '../components/EventCategoryBadge';
import { analyzeCustomText } from '../api/client';

const SAMPLE_PROMPTS = [
  {
    title: "Geopolitical Strait Tension",
    text: "Naval escort operations initiated in Red Sea after commercial tanker attacks; oil insurance premiums spike 45% and container rerouting adds 14 days transit.",
    type: "News"
  },
  {
    title: "NVIDIA Mega Earnings Beat",
    text: "NVIDIA quarterly data center revenue skyrockets 260% to record $22.6B on insatiable Blackwell GPU compute demand; raises guidance by $2B.",
    type: "News"
  },
  {
    title: "DOJ Antitrust Mandate",
    text: "DOJ announces sweeping antitrust lawsuit against mega-cap cloud providers demanding forced unbundling of enterprise software and AI copilot suites.",
    type: "News"
  },
  {
    title: "Fintech Retail Social Sentiment",
    text: "🚨 Rumors circulating that $BAC fintech division seeing massive headcount cuts and loan book write-downs. Puts are going to print! 📉💥",
    type: "Social"
  }
];

export default function RiskIntelligence({
  metrics,
  onRebalanceTrigger,
  onStressTrigger,
  showToast
}) {
  const [inputText, setInputText] = useState(SAMPLE_PROMPTS[0].text);
  const [inputSource, setInputSource] = useState("Reuters Live Feed");
  const [sourceType, setSourceType] = useState("News");
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzedSignal, setAnalyzedSignal] = useState(null);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await analyzeCustomText(inputText, "", inputSource, sourceType);
      setAnalyzedSignal(res);
      if (showToast) showToast(`Successfully parsed risk signal for ${res.category}!`);
    } catch (err) {
      console.error(err);
      if (showToast) showToast("Failed to analyze text. Please check backend connection.", "error");
    } finally {
      setAnalyzing(false);
    }
  };

  const categoryChartData = (metrics?.risk_engine?.category_distribution || []).map(item => ({
    name: item.category,
    count: item.count
  }));

  return (
    <div className="page-wrapper">
      {/* Page Title & Mission */}
      <div style={{ marginBottom: '24px' }}>
        <h2 className="title-lg">Unified AI / NLP Risk Intelligence Engine</h2>
        <p className="subtitle-sm">
          Real-time financial NLP architecture extracting sentiment polarity, event taxonomy, entity mentions, and predictive severity impacts.
        </p>
      </div>

      {/* Main Interactive Analyzer Sandbox */}
      <div className="glass-card" style={{ marginBottom: '28px', border: '1px solid rgba(59, 130, 246, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: '#3b82f620', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Cpu size={16} color="#3b82f6" />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Interactive NLP Risk Signal Sandbox
            </h3>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            scikit-learn Pipeline + Financial Lexicon Calibrated
          </span>
        </div>

        {/* Preset Sample Buttons */}
        <div style={{ marginBottom: '14px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginRight: '8px', fontWeight: 600 }}>
            Pre-Calibrated Test Signals:
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '6px' }}>
            {SAMPLE_PROMPTS.map((p, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInputText(p.text);
                  setSourceType(p.type);
                }}
                className="btn btn-sm btn-outline"
              >
                {p.title}
              </button>
            ))}
          </div>
        </div>

        {/* Input Text Area */}
        <div style={{ marginBottom: '16px' }}>
          <textarea
            className="form-textarea"
            rows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type or paste any financial headline, news excerpt, or social media commentary..."
            style={{ fontSize: '0.92rem', lineHeight: 1.5 }}
          />
        </div>

        {/* Configuration Row & Trigger Button */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
              Source Type:
              <select
                className="form-select"
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                style={{ width: '130px', padding: '6px 10px', fontSize: '0.8rem' }}
              >
                <option value="News">News Article</option>
                <option value="Social">Social / Forum</option>
              </select>
            </label>

            <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
              Publisher:
              <input
                className="form-input"
                type="text"
                value={inputSource}
                onChange={(e) => setInputSource(e.target.value)}
                style={{ width: '180px', padding: '6px 10px', fontSize: '0.8rem' }}
              />
            </label>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="btn btn-primary"
            style={{ padding: '9px 20px' }}
          >
            <Send size={15} />
            <span>{analyzing ? "Extracting Risk Signal..." : "Analyze & Extract Risk Signal"}</span>
          </button>
        </div>

        {/* Visualized Output Card */}
        {analyzedSignal && (
          <div style={{
            marginTop: '20px',
            background: 'rgba(15, 23, 42, 0.9)',
            border: '1px solid #3b82f6',
            borderRadius: '10px',
            padding: '18px',
            animation: 'fadeIn 0.3s ease'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.78rem', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Extracted Risk Signal Output
                </span>
                <span className="mono-text" style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                  ID: {analyzedSignal.event_id}
                </span>
              </div>
              <span className="badge" style={{ background: '#10b98125', color: '#34d399', border: '1px solid #10b98150' }}>
                Model Confidence: {((analyzedSignal.confidence || 0.9) * 100).toFixed(0)}%
              </span>
            </div>

            {/* Grid of Extracted Features */}
            <div className="grid-cols-4" style={{ gap: '12px', marginBottom: '16px' }}>
              <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Sentiment Score
                </div>
                <div style={{ marginTop: '4px' }}>
                  <SentimentBadge score={analyzedSignal.sentiment_score} />
                </div>
              </div>

              <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Event Taxonomy
                </div>
                <div style={{ marginTop: '4px' }}>
                  <EventCategoryBadge category={analyzedSignal.category} />
                </div>
              </div>

              <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Predicted Severity
                </div>
                <div style={{ marginTop: '4px' }}>
                  <SeverityBadge score={analyzedSignal.impact_score} />
                </div>
              </div>

              <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Identified Entity & Sector
                </div>
                <div style={{ marginTop: '4px', fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                  {analyzedSignal.tickers?.join(', ') || 'SPY'} ({analyzedSignal.sector})
                </div>
              </div>
            </div>

            {/* Downstream Actions */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '10px', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
              <button
                onClick={() => onRebalanceTrigger(analyzedSignal)}
                className="btn btn-primary"
              >
                <TrendingUp size={15} />
                <span>Apply Signal to Tactical Rebalancer</span>
              </button>

              {analyzedSignal.impact_score >= 7.0 && (
                <button
                  onClick={() => onStressTrigger(analyzedSignal)}
                  className="btn btn-danger"
                >
                  <AlertTriangle size={15} />
                  <span>Stress Test Wholesale Portfolio</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Category Distribution Chart */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Risk Engine Classification Taxonomy Distribution
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Total parsed events across mandatory 9 financial categories
            </p>
          </div>
        </div>

        <div style={{ height: '240px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={10} angle={-25} textAnchor="end" />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#151e32', borderColor: '#223048', borderRadius: '8px', color: '#f8fafc' }} />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                {categoryChartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.name === 'Geopolitical' ? '#ef4444' : (entry.name === 'Earnings' ? '#10b981' : '#3b82f6')}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
