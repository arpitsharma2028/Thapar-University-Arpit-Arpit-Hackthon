import datetime
from typing import Dict, Any, Optional
from backend.ml.feature_extraction import clean_financial_text
from backend.ml.sentiment_analyzer import SentimentAnalyzer
from backend.ml.event_classifier import EventClassifier
from backend.ml.impact_scorer import ImpactScorer
from backend.ml.entity_extractor import EntityExtractor

class UnifiedRiskEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UnifiedRiskEngine()
        return cls._instance

    def __init__(self):
        print("Initializing Unified NLP Risk Engine components...")
        self.sentiment_analyzer = SentimentAnalyzer()
        self.event_classifier = EventClassifier()
        self.impact_scorer = ImpactScorer()
        self.entity_extractor = EntityExtractor()
        print("[OK] Unified NLP Risk Engine successfully loaded.")

    def process_text(
        self,
        text: str,
        headline: Optional[str] = None,
        source: str = "Market Wire",
        source_type: str = "News"
    ) -> Dict[str, Any]:
        """
        Processes financial / social text into a structured risk signal.
        """
        full_text = f"{headline}. {text}" if headline else text
        cleaned = clean_financial_text(full_text)

        # 1. Sentiment Analysis
        sentiment_score, sentiment_conf = self.sentiment_analyzer.analyze(full_text)

        # 2. Event Classification
        category, cat_conf = self.event_classifier.classify(full_text)

        # 3. Impact Scoring
        impact_score = self.impact_scorer.predict(full_text, sentiment_score, category)

        # 4. Entity Extraction
        entities = self.entity_extractor.extract(full_text)

        # Overall confidence score
        overall_conf = round((sentiment_conf + cat_conf) / 2.0, 2)

        return {
            "headline": headline or (text[:75] + "..." if len(text) > 75 else text),
            "text": text,
            "source_type": source_type,
            "source": source,
            "category": category,
            "sentiment_score": sentiment_score,
            "impact_score": impact_score,
            "tickers": entities["tickers"],
            "companies": entities["companies"],
            "sector": entities["sector"],
            "confidence": overall_conf,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Factory convenience function
def get_risk_engine() -> UnifiedRiskEngine:
    return UnifiedRiskEngine.get_instance()
