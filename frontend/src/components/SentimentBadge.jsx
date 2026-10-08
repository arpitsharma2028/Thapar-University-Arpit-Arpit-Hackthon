import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function SentimentBadge({ score }) {
  const val = typeof score === 'number' ? score : parseFloat(score) || 0.0;
  
  if (val > 0.15) {
    return (
      <span className="badge badge-bullish">
        <TrendingUp size={13} />
        +{val.toFixed(2)} (Bullish)
      </span>
    );
  } else if (val < -0.15) {
    return (
      <span className="badge badge-bearish">
        <TrendingDown size={13} />
        {val.toFixed(2)} (Bearish)
      </span>
    );
  } else {
    return (
      <span className="badge badge-neutral">
        <Minus size={13} />
        {val.toFixed(2)} (Neutral)
      </span>
    );
  }
}
