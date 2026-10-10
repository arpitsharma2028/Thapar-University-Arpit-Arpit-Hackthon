"""
FinSight AI — Impact Severity Scoring Engine
Predicts systemic impact severity on a calibrated 1.0 to 10.0 scale.

Architecture:
- Utilizes the trained Ridge Regression pipeline (TF-IDF + Ridge) on input text.
- Blends regression inference with structural category systemic importance,
  sentiment extremity, and verified systemic risk keyword multipliers.
- Explicitly handles missing models and prediction errors with a documented heuristic fallback.
- Strictly clamps outputs to [1.0, 10.0].

Interpretation:
- 1.0 - 3.9: Low / routine operational or localized market news.
- 4.0 - 6.9: Moderate / company-specific or sector-wide development.
- 7.0 - 8.9: High / systemic market or credit shock (triggers Module B stress test).
- 9.0 - 10.0: Critical / multi-market emergency or catastrophic disruption.
"""

import os
import re
import logging
import joblib
from typing import Dict, Any, Optional

logger = logging.getLogger("finsight.impact")

SYSTEMIC_SEVERITY_KEYWORDS = {
    # Systemic Tier 1 (adds 2.0 - 3.5)
    "crisis": 2.5, "war": 3.2, "embargo": 3.0, "sanction": 2.6, "sanctions": 2.6,
    "blockade": 3.0, "emergency": 2.4, "contagion": 3.0, "default": 2.8, "insolvency": 2.8,
    "antitrust": 2.4, "breakup": 2.8, "catastrophic": 3.2, "liquidity crunch": 2.8,
    "rate shock": 2.4, "unprecedented": 2.0, "export curb": 2.5, "export curbs": 2.5,

    # Moderate Tier 2 (adds 0.8 - 1.6)
    "surge": 1.2, "plunge": 1.6, "hike": 1.0, "misses": 1.2, "warning": 1.4,
    "restructuring": 1.2, "layoffs": 1.2, "acquisition": 1.4, "investigation": 1.4,
    "lawsuit": 1.3, "guidance cut": 1.5, "recall": 1.6, "recalls": 1.6, "defect": 1.4
}

CATEGORY_BASE_IMPORTANCE = {
    "Geopolitical": 5.5,
    "Credit": 5.2,
    "Macroeconomic": 5.0,
    "Regulatory": 4.8,
    "Market": 4.5,
    "Merger/Acquisition": 4.5,
    "Earnings": 4.2,
    "Product Launch": 4.0,
    "Other": 2.5
}

class ImpactScorer:
    def __init__(self):
        from backend.config import MODELS_DIR
        self.models_dir = MODELS_DIR
        self.model_path = os.path.join(self.models_dir, "impact_regressor.joblib")
        self.ml_pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.ml_pipeline = joblib.load(self.model_path)
                logger.info("Impact regressor ML pipeline loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load impact regressor model ({e}). Using verified heuristic model.")
                self.ml_pipeline = None

    def predict(self, text: str, sentiment_score: float = 0.0, category: str = "Other") -> float:
        """
        Predicts impact severity score on a 1.0 to 10.0 scale.
        """
        if not text or not str(text).strip():
            return 2.5

        clean_text = str(text).strip()
        text_lower = clean_text.lower()

        # 1. Structural Category Base
        base = CATEGORY_BASE_IMPORTANCE.get(category, 3.5)

        # 2. Sentiment Extremity Factor (|sentiment| * 1.8)
        sentiment_delta = abs(float(sentiment_score)) * 1.8

        # 3. Keyword Severity Signals
        keyword_boost = 0.0
        for kw, boost in SYSTEMIC_SEVERITY_KEYWORDS.items():
            if " " in kw:
                if kw in text_lower:
                    keyword_boost += boost
            else:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    keyword_boost += boost

        # 4. Numerical Percentage Cues (e.g., 20%, 150 bps)
        pct_boost = 0.0
        pct_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', clean_text)
        for p in pct_matches:
            val = float(p)
            if val > 50:
                pct_boost += 1.5
            elif val > 15:
                pct_boost += 0.8
            elif val > 5:
                pct_boost += 0.4

        heuristic_raw = base + sentiment_delta + min(keyword_boost, 3.5) + min(pct_boost, 1.5)

        # 5. Evaluate Trained ML Regressor if available
        if self.ml_pipeline is not None:
            try:
                ml_pred = float(self.ml_pipeline.predict([clean_text])[0])
                # Blend 50% trained ML regressor + 50% structured risk calibration
                blended = 0.50 * ml_pred + 0.50 * heuristic_raw
                score = max(1.0, min(10.0, blended))
                return round(score, 1)
            except Exception as e:
                logger.debug(f"Regressor inference error, falling back to heuristic: {e}")

        # Clamped heuristic score
        score = max(1.0, min(10.0, heuristic_raw))
        return round(score, 1)
