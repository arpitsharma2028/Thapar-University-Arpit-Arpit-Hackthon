import React from 'react';
import { AlertCircle, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function SeverityBadge({ score }) {
  const val = typeof score === 'number' ? score : parseFloat(score) || 5.0;

  if (val >= 7.0) {
    return (
      <span className="badge badge-severity-high" title="High Severity — Triggers Stress Testing">
        <AlertTriangle size={13} />
        {val.toFixed(1)} / 10 (High Risk)
      </span>
    );
  } else if (val >= 4.5) {
    return (
      <span className="badge badge-severity-med">
        <AlertCircle size={13} />
        {val.toFixed(1)} / 10 (Moderate)
      </span>
    );
  } else {
    return (
      <span className="badge badge-severity-low">
        <ShieldCheck size={13} />
        {val.toFixed(1)} / 10 (Low Risk)
      </span>
    );
  }
}
