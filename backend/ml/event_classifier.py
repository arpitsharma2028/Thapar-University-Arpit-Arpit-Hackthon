import os
import joblib
import re
import logging
from typing import Dict, Any, Tuple
from backend.config import MODELS_DIR

logger = logging.getLogger("finsight.classifier")

EVENT_CATEGORIES = [
    "Geopolitical",
    "Macroeconomic",
    "Credit",
    "Merger/Acquisition",
    "Product Launch",
    "Earnings",
    "Regulatory",
    "Market",
    "Other"
]

CATEGORY_KEYWORDS = {
    "Geopolitical": ["sanction", "war", "naval", "military", "nato", "taiwan", "strait", "tariff", "treaty", "blockade", "middle east", "embargo", "geopolitical"],
    "Macroeconomic": ["fed", "inflation", "gdp", "interest rate", "unemployment", "cpi", "central bank", "recession", "yield curve", "macroeconomic", "treasury yields"],
    "Credit": ["bond", "debt", "default", "rating", "downgrade", "delinquency", "refinancing", "liquidity", "spread", "credit", "insolvency", "commercial real estate"],
    "Merger/Acquisition": ["acquisition", "merger", "buyout", "takeover", "accretive", "deal", "consolidate", "spinoff", "tender offer"],
    "Product Launch": ["launch", "unveil", "release", "copilot", "gemini", "chip", "ai model", "device", "feature", "platform", "innovation", "patent"],
    "Earnings": ["quarterly", "revenue", "eps", "net income", "margin", "guidance", "profit", "earnings", "beat consensus", "miss consensus", "fiscal quarter"],
    "Regulatory": ["antitrust", "sec", "doj", "ftc", "cfpb", "fda", "fine", "investigation", "compliance", "mandate", "ruling", "lawsuit", "regulatory"],
    "Market": ["rally", "selloff", "volatility", "vix", "bull", "bear", "liquidity", "options", "hedge fund", "inflow", "outflow", "rotation", "market"]
}

class EventClassifier:
    def __init__(self):
        self.model_path = os.path.join(MODELS_DIR, "event_classifier.joblib")
        self.ml_pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.ml_pipeline = joblib.load(self.model_path)
            except Exception as e:
                logger.warning(f"Could not load event classifier model ({e}). Using feature matcher.")
                self.ml_pipeline = None

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classifies input text into one of the 9 event categories.
        Returns: (category, confidence_score)
        """
        if not text or not text.strip():
            return "Other", 0.50

        # ML Model prediction if present
        if self.ml_pipeline is not None:
            try:
                probs = self.ml_pipeline.predict_proba([text])[0]
                classes = list(self.ml_pipeline.classes_)
                max_prob = max(probs)
                best_class = classes[list(probs).index(max_prob)]
                return best_class, round(float(max_prob), 2)
            except Exception:
                pass

        # Robust domain feature keyword matching
        text_lower = text.lower()
        scores = {}
        for cat, kws in CATEGORY_KEYWORDS.items():
            count = sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower)) for kw in kws)
            scores[cat] = count

        best_cat = max(scores, key=scores.get)
        best_count = scores[best_cat]

        if best_count == 0:
            return "Other", 0.55

        conf = min(0.95, 0.65 + 0.08 * best_count)
        return best_cat, round(float(conf), 2)
