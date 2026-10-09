import React from 'react';

const CATEGORY_COLORS = {
  "Geopolitical": { bg: "rgba(220, 38, 38, 0.15)", text: "#fca5a5", border: "rgba(220, 38, 38, 0.4)" },
  "Macroeconomic": { bg: "rgba(217, 119, 6, 0.15)", text: "#fcd34d", border: "rgba(217, 119, 6, 0.4)" },
  "Credit": { bg: "rgba(168, 85, 247, 0.15)", text: "#d8b4fe", border: "rgba(168, 85, 247, 0.4)" },
  "Earnings": { bg: "rgba(16, 185, 129, 0.15)", text: "#6ee7b7", border: "rgba(16, 185, 129, 0.4)" },
  "Regulatory": { bg: "rgba(6, 182, 212, 0.15)", text: "#67e8f9", border: "rgba(6, 182, 212, 0.4)" },
  "Product Launch": { bg: "rgba(59, 130, 246, 0.15)", text: "#93c5fd", border: "rgba(59, 130, 246, 0.4)" },
  "Merger/Acquisition": { bg: "rgba(236, 72, 153, 0.15)", text: "#f472b6", border: "rgba(236, 72, 153, 0.4)" },
  "Market": { bg: "rgba(245, 158, 11, 0.15)", text: "#fde68a", border: "rgba(245, 158, 11, 0.4)" },
  "Other": { bg: "rgba(100, 116, 139, 0.15)", text: "#cbd5e1", border: "rgba(100, 116, 139, 0.4)" },
};

export default function EventCategoryBadge({ category }) {
  const style = CATEGORY_COLORS[category] || CATEGORY_COLORS["Other"];
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: '3px 8px',
      borderRadius: '6px',
      fontSize: '0.72rem',
      fontWeight: 600,
      background: style.bg,
      color: style.text,
      border: `1px solid ${style.border}`,
      backdropFilter: 'blur(8px)',
      WebkitBackdropFilter: 'blur(8px)',
      boxShadow: '0 2px 6px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.15)',
      whiteSpace: 'nowrap'
    }}>
      {category}
    </span>
  );
}
