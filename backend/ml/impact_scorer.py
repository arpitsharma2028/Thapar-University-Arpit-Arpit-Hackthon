import os
import re
import joblib
import logging
from typing import Dict, Any
from backend.config import MODELS_DIR

logger = logging.getLogger("finsight.impact")

SEVERITY_KEYWORDS = {
    # High severity (adds 2.0 - 3.5)
    "crisis": 3.0, "war": 3.5, "embargo": 3.2, "sanction": 2.8, "sanctions": 2.8,
    "blockade": 3.0, "emergency": 2.5, "contagion": 3.2, "default": 2.8, "insolvency": 3.0,
    "antitrust": 2.5, "breakup": 3.0, "record": 1.8, "historic": 2.0, "catastrophic": 3.5,
    "liquidity crunch": 3.0, "rate shock": 2.5, "unprecedented": 2.2,

    # Medium severity (adds 1.0 - 1.8)
    "surge": 1.5, "plunge": 1.8, "hike": 1.2, "misses": 1.4, "warning": 1.6,
    "restructuring": 1.5, "layoffs": 1.4, "acquisition": 1.6, "billion": 1.2,
    "investigation": 1.6, "lawsuit": 1.5, "guidance cut": 1.8
}

class ImpactScorer:
    def __init__(self):
        self.model_path = os.path.join(MODELS_DIR, "impact_regressor.joblib")
        self.ml_pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.ml_pipeline = joblib.load(self.model_path)
            except Exception as e:
                logger.warning(f"Could not load impact regressor model ({e}). Using heuristic model.")
                self.ml_pipeline = None

    def predict(self, text: str, sentiment_score: float, category: str) -> float:
        """
        Predicts an impact severity score on a 1.0 to 10.0 scale.
        """
        if not text:
            return 3.0

        # Baseline score depends on category systemic importance
        category_weights = {
            "Geopolitical": 5.5,
            "Macroeconomic": 5.0,
            "Credit": 5.2,
            "Regulatory": 4.8,
            "Earnings": 4.2,
            "Merger/Acquisition": 4.5,
            "Product Launch": 4.0,
            "Market": 4.5,
            "Other": 3.0
        }

        base = category_weights.get(category, 4.0)

        # Extremity of sentiment adds impact: |sentiment| * 2.5
        sentiment_delta = abs(sentiment_score) * 2.5

        # Keyword severity boosts
        text_lower = text.lower()
        keyword_boost = 0.0
        for kw, boost in SEVERITY_KEYWORDS.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                keyword_boost += boost

        # Numerical percentage cues (e.g. 20%, 150 bps)
        pct_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        pct_boost = 0.0
        for p in pct_matches:
            val = float(p)
            if val > 50:
                pct_boost += 1.5
            elif val > 15:
                pct_boost += 0.8
            elif val > 5:
                pct_boost += 0.4

        # Combine
        raw_score = base + sentiment_delta + min(keyword_boost, 3.5) + min(pct_boost, 1.5)
        
        # Clamp between 1.0 and 10.0
        score = max(1.0, min(10.0, raw_score))
        return round(score, 1)
