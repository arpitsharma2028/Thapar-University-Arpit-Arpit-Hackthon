"""
FinSight AI — Event Classification Engine
Classifies financial text into 9 standardized categories:
- Geopolitical
- Macroeconomic
- Credit
- Merger/Acquisition
- Product Launch
- Earnings
- Regulatory
- Market
- Other (Unknown / Ambiguous / Unrelated)

Includes strict domain evidence gating to prevent unrelated consumer or general news
(e.g., local bakery croissant awards) from being misclassified as Earnings.
"""

import os
import re
import logging
import joblib
from typing import Dict, Any, Tuple, Optional

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
    "Geopolitical": [
        "sanction", "sanctions", "war", "naval", "military", "nato", "taiwan", "strait",
        "straits", "tariff", "tariffs", "treaty", "blockade", "middle east", "embargo",
        "geopolitical", "export curb", "export curbs", "export restriction", "sovereign",
        "bilateral", "conflict", "national security", "curbs on china"
    ],
    "Macroeconomic": [
        "fed", "federal reserve", "inflation", "gdp", "interest rate", "interest rates",
        "rate cut", "rate hike", "rate cuts", "rate hikes", "unemployment", "cpi",
        "central bank", "recession", "yield curve", "macroeconomic", "treasury yields",
        "monetary policy", "stagflation", "fomc", "benchmark rate"
    ],
    "Credit": [
        "bond", "bonds", "debt", "default", "defaults", "credit rating", "downgrade",
        "delinquency", "delinquencies", "refinancing", "liquidity", "credit spread",
        "credit", "insolvency", "commercial real estate", "cre", "loan default",
        "contagion", "cds", "distressed debt"
    ],
    "Merger/Acquisition": [
        "acquisition", "acquisitions", "merger", "mergers", "buyout", "takeover",
        "accretive", "deal", "consolidate", "spinoff", "spin-off", "tender offer",
        "merger agreement", "acquired", "acquires"
    ],
    "Product Launch": [
        "launch", "launches", "launched", "unveil", "unveils", "unveiled", "release",
        "releases", "released", "copilot", "gemini", "chip", "chips", "ai model",
        "device", "feature", "platform", "innovation", "patent", "product update",
        "next-gen", "architecture"
    ],
    "Earnings": [
        "quarterly", "revenue", "revenues", "eps", "net income", "margin", "margins",
        "guidance", "profit", "profits", "earnings", "beat consensus", "miss consensus",
        "fiscal quarter", "financial results", "quarter results", "q1", "q2", "q3", "q4",
        "operating income", "ebitda"
    ],
    "Regulatory": [
        "antitrust", "sec", "doj", "ftc", "cfpb", "fda", "fine", "fined", "investigation",
        "compliance", "mandate", "ruling", "lawsuit", "regulatory", "subpoena",
        "recall", "recalls", "recalled", "defect", "probe", "probes", "probed",
        "enforcement", "injunction", "violation", "sanctioned"
    ],
    "Market": [
        "rally", "rallies", "selloff", "sell-off", "volatility", "vix", "bull", "bear",
        "liquidity", "options", "hedge fund", "inflow", "outflow", "rotation",
        "intraday", "short squeeze", "market sentiment"
    ]
}

# Negative indicator words that disqualify texts from financial categories if no financial terms exist
NON_FINANCIAL_PATTERNS = re.compile(
    r'\b(?:bakery|croissant|pastry|bake-off|chef|recipe|restaurant award|cooking|gardening|local sports|weather forecast|best dessert)\b',
    re.IGNORECASE
)

class EventClassifier:
    def __init__(self):
        from backend.config import MODELS_DIR
        self.models_dir = MODELS_DIR
        self.model_path = os.path.join(self.models_dir, "event_classifier.joblib")
        self.ml_pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.ml_pipeline = joblib.load(self.model_path)
            except Exception as e:
                logger.debug(f"Event classifier model not loaded: {e}")
                self.ml_pipeline = None

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classifies input text into one of the 9 event categories with evidence gating.
        Returns: (category, confidence_score)
        """
        if not text or not str(text).strip():
            return "Other", 0.50

        text_lower = str(text).strip().lower()

        # 1. Evidence Gating: If text matches non-financial patterns with zero financial keywords
        has_non_financial = bool(NON_FINANCIAL_PATTERNS.search(text_lower))

        # Count keyword matches across categories
        keyword_scores = {}
        for cat, kws in CATEGORY_KEYWORDS.items():
            count = 0
            for kw in kws:
                if " " in kw:
                    if kw in text_lower:
                        count += 2
                else:
                    if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                        count += 1
            keyword_scores[cat] = count

        max_keyword_count = max(keyword_scores.values())
        best_kw_cat = max(keyword_scores, key=keyword_scores.get)

        # If non-financial noise detected with weak/no financial evidence, return Other
        if has_non_financial and max_keyword_count <= 1:
            return "Other", 0.85

        # 2. Check ML pipeline if trained, but validate against evidence
        if self.ml_pipeline is not None and max_keyword_count > 0:
            try:
                probs = self.ml_pipeline.predict_proba([text])[0]
                classes = list(self.ml_pipeline.classes_)
                max_prob = float(max(probs))
                predicted_class = classes[list(probs).index(max_prob)]

                # Only accept ML prediction if confidence is solid and domain evidence supports it
                if max_prob >= 0.40:
                    # Guard against misclassifying into Earnings without earnings signals
                    if predicted_class == "Earnings" and keyword_scores.get("Earnings", 0) == 0:
                        # Fallback to best keyword-supported category
                        if max_keyword_count > 0:
                            return best_kw_cat, round(min(0.92, 0.65 + 0.08 * max_keyword_count), 2)
                        return "Other", 0.55

                    # Guard against misclassifying export curbs / geopolitics into other categories
                    if keyword_scores.get("Geopolitical", 0) >= 2 and predicted_class != "Geopolitical":
                        return "Geopolitical", 0.88

                    return predicted_class, round(max_prob, 2)
            except Exception:
                pass

        # 3. Keyword-evidence based deterministic classification
        if max_keyword_count > 0:
            conf = min(0.95, 0.65 + 0.08 * max_keyword_count)
            return best_kw_cat, round(float(conf), 2)

        # 4. Unknown / Ambiguous fallback
        return "Other", 0.55
