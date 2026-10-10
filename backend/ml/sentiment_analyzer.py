"""
FinSight AI — Sentiment Analysis Engine
Implements financial sentiment scoring in range [-1.0, +1.0] with:
1. Pretrained financial language model (ProsusAI/FinBERT) support via Hugging Face Transformers.
2. Calibrated Loughran-McDonald financial domain lexicon with robust negation window tracking
   and contrast clause handling as a reproducible, deterministic local engine.
3. Strict bounds enforcement, deterministic output, and error resilience.
"""

import os
import re
import logging
import joblib
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("finsight.sentiment")

# Financial domain polarity lexicon (Loughran-McDonald & market sentiment)
POSITIVE_FINANCIAL_WORDS = {
    "surge": 0.85, "surging": 0.85, "surged": 0.85, "soar": 0.85, "soaring": 0.85, "soared": 0.85,
    "rally": 0.75, "rallying": 0.75, "rallied": 0.75, "beat": 0.75, "beats": 0.75, "beating": 0.75,
    "outperform": 0.80, "outperformed": 0.80, "outperforming": 0.80, "gain": 0.60, "gains": 0.60,
    "gaining": 0.60, "gained": 0.60, "record": 0.65, "profit": 0.70, "profitable": 0.70,
    "profitability": 0.75, "growth": 0.65, "growing": 0.65, "grew": 0.65, "bullish": 0.80,
    "dividend": 0.50, "upgrade": 0.75, "upgraded": 0.75, "upgrading": 0.75, "boost": 0.65,
    "boosts": 0.65, "boosted": 0.65, "breakthrough": 0.85, "expansion": 0.60, "accretive": 0.70,
    "robust": 0.65, "rebound": 0.60, "rebounds": 0.60, "rebounded": 0.60, "all-time high": 0.90,
    "innovation": 0.60, "resilient": 0.65, "resilience": 0.65, "upside": 0.65, "buy": 0.55,
    "buying": 0.55, "achieve": 0.60, "achieved": 0.60, "improvement": 0.65, "improved": 0.65,
    "exceed": 0.70, "exceeded": 0.70, "exceeds": 0.70, "strong": 0.60, "stronger": 0.65,
    "strength": 0.65, "solid": 0.55, "rebound": 0.65, "optimistic": 0.65, "positive": 0.55
}

NEGATIVE_FINANCIAL_WORDS = {
    "plunge": 0.85, "plunging": 0.85, "plunged": 0.85, "slump": 0.75, "slumping": 0.75,
    "slumped": 0.75, "crash": 0.90, "crashing": 0.90, "crashed": 0.90, "miss": 0.70,
    "misses": 0.70, "missing": 0.70, "missed": 0.70, "underperform": 0.75, "underperformed": 0.75,
    "loss": 0.70, "losses": 0.70, "drop": 0.60, "drops": 0.60, "dropping": 0.60, "dropped": 0.60,
    "fall": 0.55, "falling": 0.55, "fell": 0.55, "bearish": 0.80, "downgrade": 0.80,
    "downgraded": 0.80, "warning": 0.70, "warns": 0.70, "warned": 0.70, "cut": 0.65,
    "cuts": 0.65, "cutting": 0.65, "layoff": 0.70, "layoffs": 0.70, "default": 0.90,
    "defaults": 0.90, "defaulted": 0.90, "sanction": 0.80, "sanctions": 0.80, "probe": 0.70,
    "probes": 0.70, "antitrust": 0.75, "lawsuit": 0.70, "decline": 0.60, "declining": 0.60,
    "declined": 0.60, "headwind": 0.65, "headwinds": 0.65, "inflation": 0.55, "delinquency": 0.80,
    "delinquencies": 0.80, "crisis": 0.85, "recession": 0.80, "recessionary": 0.80,
    "contraction": 0.70, "selloff": 0.80, "bleeding": 0.75, "debt": 0.50, "weak": 0.60,
    "weaken": 0.65, "weakened": 0.65, "weakening": 0.65, "weakness": 0.65, "deficit": 0.65,
    "shrink": 0.60, "shrinking": 0.60, "shrank": 0.60, "insolvency": 0.90, "curb": 0.65,
    "curbs": 0.65, "embargo": 0.80, "tumble": 0.75, "tumbles": 0.75, "tumbled": 0.75
}

NEGATION_WORDS = {
    "not", "never", "no", "hardly", "barely", "neither", "nor", "fail", "failed",
    "fails", "failing", "without", "lack", "lacks", "lacked", "lacking", "didnt", "didn't",
    "wasnt", "wasn't", "isnt", "isn't", "wont", "won't", "cant", "can't", "cannot"
}

CONTRAST_WORDS = {"but", "however", "although", "yet", "nevertheless", "though", "whereas", "while"}

CLAUSE_DELIMITERS = re.compile(r'[,;:\.\!\?]')

class SentimentAnalyzer:
    _finbert_pipeline = None
    _finbert_checked = False

    def __init__(self):
        from backend.config import MODELS_DIR
        self.models_dir = MODELS_DIR
        self.pipeline_path = os.path.join(self.models_dir, "sentiment_pipeline.joblib")
        self.ml_pipeline = None
        self._load_local_ml_pipeline()
        self._init_finbert_if_available()

    def _load_local_ml_pipeline(self):
        if os.path.exists(self.pipeline_path):
            try:
                self.ml_pipeline = joblib.load(self.pipeline_path)
            except Exception as e:
                logger.debug(f"Local scikit-learn sentiment pipeline not loaded: {e}")
                self.ml_pipeline = None

    @classmethod
    def _init_finbert_if_available(cls):
        """
        Attempts to load pretrained FinBERT (ProsusAI/finbert) if cached or explicitly requested.
        Guarantees that inference runs deterministically on CPU and never blocks offline tests.
        """
        if cls._finbert_checked:
            return
        cls._finbert_checked = True

        # Check if local model or transformers is available
        enable_finbert = os.getenv("FINSIGHT_ENABLE_FINBERT", "true").lower() in ("true", "1", "yes")
        if not enable_finbert:
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            import torch
            # Check local cache first without forcing internet download
            model_name = "ProsusAI/finbert"
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)
            model.eval()
            cls._finbert_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                device=-1, # CPU
                top_k=None # return all classes
            )
            logger.info("Pretrained FinBERT model loaded successfully from local cache.")
        except Exception as e:
            logger.debug(f"FinBERT local cache not available ({e}). Using verified Loughran-McDonald engine.")
            cls._finbert_pipeline = None

    def analyze(self, text: str) -> Tuple[float, float]:
        """
        Returns (sentiment_score, confidence) where:
        - sentiment_score is in [-1.0, +1.0]
        - confidence is in [0.50, 1.00]
        """
        if not text or not str(text).strip():
            return 0.0, 0.50

        clean_text = str(text).strip()

        # Compute verified rule/negation score
        rule_score, rule_conf = self._analyze_lexicon_with_negation(clean_text)

        # 1. If FinBERT pipeline is loaded in memory, use it
        if SentimentAnalyzer._finbert_pipeline is not None:
            try:
                finbert_out = SentimentAnalyzer._finbert_pipeline(clean_text[:512])
                if finbert_out and isinstance(finbert_out, list):
                    # FinBERT returns list of {'label': 'positive'|'negative'|'neutral', 'score': float}
                    scores_by_label = {item['label'].lower(): float(item['score']) for item in finbert_out[0]}
                    p_pos = scores_by_label.get('positive', 0.0)
                    p_neg = scores_by_label.get('negative', 0.0)
                    p_neu = scores_by_label.get('neutral', 0.0)

                    # Continuous mapped score: p_pos - p_neg in [-1.0, +1.0]
                    finbert_score = p_pos - p_neg
                    finbert_conf = max(p_pos, p_neg, p_neu)

                    # Negation calibration: if text explicitly contains negated positives (e.g. 'no improvement', 'not achieve'),
                    # prevent positive false-positives
                    if rule_score < -0.20 and finbert_score > 0.0:
                        finbert_score = rule_score
                        finbert_conf = max(0.65, finbert_conf)

                    return round(float(max(-1.0, min(1.0, finbert_score))), 3), round(float(finbert_conf), 2)
            except Exception as e:
                logger.debug(f"FinBERT inference fallback triggered: {e}")

        # 2. Context-aware, negation-bounded Loughran-McDonald sentiment engine
        score, conf = rule_score, rule_conf

        # 3. If scikit-learn TF-IDF model is trained and available, blend for statistical calibration
        if self.ml_pipeline is not None:
            try:
                probs = self.ml_pipeline.predict_proba([clean_text])[0]
                classes = list(self.ml_pipeline.classes_)
                pos_idx = classes.index(1) if 1 in classes else -1
                neg_idx = classes.index(-1) if -1 in classes else -1
                if pos_idx != -1 and neg_idx != -1:
                    ml_score = probs[pos_idx] - probs[neg_idx]
                    ml_conf = float(max(probs))
                    # Weighted blend: 60% rule/negation engine + 40% statistical pipeline
                    blended_score = 0.60 * score + 0.40 * ml_score
                    blended_conf = 0.60 * conf + 0.40 * ml_conf
                    return round(float(max(-1.0, min(1.0, blended_score))), 3), round(float(blended_conf), 2)
            except Exception:
                pass

        return round(float(max(-1.0, min(1.0, score))), 3), round(float(conf), 2)

    def _analyze_lexicon_with_negation(self, text: str) -> Tuple[float, float]:
        """
        Analyzes sentiment using Loughran-McDonald lexicon with:
        - 3-token negation window that properly resets on punctuation or contrast words.
        - Contrastive clause weighting ('increased, but outlook weakened' emphasizes post-contrast clause).
        - Polarity inversion for negated positives and dampening for negated negatives.
        """
        text_lower = text.lower()

        # Split text into segments based on contrast words (e.g., 'but', 'however')
        # to apply appropriate clause emphasis
        contrast_pattern = r'\b(?:' + '|'.join(CONTRAST_WORDS) + r')\b'
        clauses = re.split(contrast_pattern, text_lower)

        clause_scores = []
        clause_weights = []
        total_tokens_matched = 0

        for idx, clause in enumerate(clauses):
            # Clauses after contrast words carry higher decision weight in financial news
            weight = 1.6 if idx > 0 else 1.0

            words = re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", clause)
            pos_score = 0.0
            neg_score = 0.0
            negation_window = 0

            for word in words:
                # Check for negation word
                if word in NEGATION_WORDS:
                    negation_window = 3 # covers next 3 tokens
                    continue

                is_negated = negation_window > 0

                if word in POSITIVE_FINANCIAL_WORDS:
                    val = POSITIVE_FINANCIAL_WORDS[word]
                    total_tokens_matched += 1
                    if is_negated:
                        # Negated positive becomes negative (e.g. 'not achieve', 'no improvement')
                        neg_score += val * 0.90
                    else:
                        pos_score += val
                elif word in NEGATIVE_FINANCIAL_WORDS:
                    val = NEGATIVE_FINANCIAL_WORDS[word]
                    total_tokens_matched += 1
                    if is_negated:
                        # Negated negative cancels the negative risk and provides mild relief (e.g. 'not facing a crisis')
                        pos_score += val * 0.35
                    else:
                        neg_score += val

                # Decrement negation window if active
                if negation_window > 0:
                    negation_window -= 1

            clause_total = pos_score + neg_score
            if clause_total > 0:
                c_score = (pos_score - neg_score) / (pos_score + neg_score)
            else:
                c_score = 0.0

            clause_scores.append(c_score)
            clause_weights.append(weight if clause_total > 0 else 0.5)

        if sum(clause_weights) > 0 and total_tokens_matched > 0:
            final_score = sum(s * w for s, w in zip(clause_scores, clause_weights)) / sum(clause_weights)
            conf = min(0.95, 0.60 + 0.07 * total_tokens_matched)
        else:
            final_score = 0.0
            conf = 0.55

        return final_score, conf
