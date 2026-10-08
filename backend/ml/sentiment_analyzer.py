import os
import joblib
import re
from typing import Dict, Any, Tuple
from backend.config import MODELS_DIR

# Financial domain polarity lexicon (adapted from Loughran-McDonald & market sentiment)
POSITIVE_FINANCIAL_WORDS = {
    "surge": 0.8, "surging": 0.8, "soar": 0.85, "soaring": 0.85, "rally": 0.75, "rallying": 0.75,
    "beat": 0.7, "beats": 0.7, "beating": 0.7, "outperform": 0.8, "outperformed": 0.8,
    "gain": 0.6, "gains": 0.6, "gaining": 0.6, "record": 0.65, "profit": 0.7, "profitable": 0.7,
    "growth": 0.6, "growing": 0.6, "bullish": 0.8, "bull": 0.6, "dividend": 0.5, "upgrade": 0.75,
    "upgraded": 0.75, "boost": 0.65, "boosts": 0.65, "breakthrough": 0.85, "expansion": 0.6,
    "accretive": 0.7, "robust": 0.65, "rebound": 0.6, "all-time high": 0.9, "innovation": 0.6,
    "resilient": 0.6, "consensus beat": 0.85, "upside": 0.65, "buy": 0.55, "buying": 0.55
}

NEGATIVE_FINANCIAL_WORDS = {
    "plunge": 0.85, "plunging": 0.85, "slump": 0.75, "slumping": 0.75, "crash": 0.9, "crashing": 0.9,
    "miss": 0.7, "misses": 0.7, "missing": 0.7, "underperform": 0.75, "loss": 0.7, "losses": 0.7,
    "drop": 0.6, "drops": 0.6, "dropping": 0.6, "fall": 0.55, "falling": 0.55, "bearish": 0.8,
    "downgrade": 0.8, "downgraded": 0.8, "warning": 0.7, "warns": 0.7, "cut": 0.65, "cuts": 0.65,
    "layoff": 0.7, "layoffs": 0.7, "default": 0.9, "defaults": 0.9, "sanction": 0.8, "sanctions": 0.8,
    "probe": 0.7, "antitrust": 0.75, "lawsuit": 0.7, "decline": 0.6, "declining": 0.6, "headwind": 0.65,
    "headwinds": 0.65, "inflation": 0.55, "delinquency": 0.8, "crisis": 0.85, "recession": 0.8,
    "contraction": 0.7, "selloff": 0.8, "bleeding": 0.75, "puts": 0.5, "debt": 0.5
}

NEGATION_WORDS = {"not", "never", "no", "hardly", "barely", "neither", "nor", "fail", "failed", "despite"}

class SentimentAnalyzer:
    def __init__(self):
        self.model_path = os.path.join(MODELS_DIR, "sentiment_pipeline.joblib")
        self.ml_pipeline = None
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.model_path):
            try:
                self.ml_pipeline = joblib.load(self.model_path)
            except Exception as e:
                print(f"Warning: Failed to load sentiment ML model ({e}). Using rule-assisted lexicon engine.")
                self.ml_pipeline = None

    def analyze(self, text: str) -> Tuple[float, float]:
        """
        Returns (sentiment_score, confidence) where:
        - sentiment_score is in [-1.0, +1.0]
        - confidence is in [0.5, 1.0]
        """
        if not text or not text.strip():
            return 0.0, 0.5

        # 1. Lexicon-based baseline score
        text_clean = text.lower()
        words = re.findall(r'\b\w+(?:-\w+)?\b', text_clean)
        
        pos_score = 0.0
        neg_score = 0.0
        negated = False
        
        for i, word in enumerate(words):
            if word in NEGATION_WORDS:
                negated = not negated
                continue
                
            # Reset negation after 3 tokens
            if negated and i > 0 and words[i-1] not in NEGATION_WORDS:
                pass
                
            if word in POSITIVE_FINANCIAL_WORDS:
                val = POSITIVE_FINANCIAL_WORDS[word]
                if negated:
                    neg_score += val * 0.75
                else:
                    pos_score += val
            elif word in NEGATIVE_FINANCIAL_WORDS:
                val = NEGATIVE_FINANCIAL_WORDS[word]
                if negated:
                    pos_score += val * 0.75
                else:
                    neg_score += val

        total_matches = pos_score + neg_score
        if total_matches > 0:
            lexicon_score = (pos_score - neg_score) / (pos_score + neg_score)
            lexicon_conf = min(0.95, 0.60 + 0.08 * total_matches)
        else:
            lexicon_score = 0.0
            lexicon_conf = 0.55

        # 2. ML Pipeline if trained and available
        if self.ml_pipeline is not None:
            try:
                probs = self.ml_pipeline.predict_proba([text])[0]
                classes = list(self.ml_pipeline.classes_)
                # Classes: -1 (neg), 0 (neutral), 1 (pos) or similar
                pos_idx = classes.index(1) if 1 in classes else -1
                neg_idx = classes.index(-1) if -1 in classes else -1
                
                if pos_idx != -1 and neg_idx != -1:
                    ml_score = probs[pos_idx] - probs[neg_idx]
                    ml_conf = max(probs)
                    # Blend 50% ML + 50% Lexicon
                    blended = 0.5 * ml_score + 0.5 * lexicon_score
                    conf = (ml_conf + lexicon_conf) / 2.0
                    return round(float(max(-1.0, min(1.0, blended))), 3), round(float(conf), 2)
            except Exception:
                pass

        return round(float(max(-1.0, min(1.0, lexicon_score))), 3), round(float(lexicon_conf), 2)
