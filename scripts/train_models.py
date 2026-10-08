"""
FinSight AI — Model Training Script
Trains scikit-learn NLP models on financial datasets and saves pipelines under backend/ml/saved_models/
- Event Classification Pipeline (TF-IDF + Logistic Regression)
- Sentiment Polarity Pipeline (TF-IDF + Ridge Classifier)
- Impact Severity Regressor (TF-IDF + Ridge)
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, RidgeClassifier, Ridge
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "ml", "saved_models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_event_classifier(train_df):
    print("\n[1/3] Training Event Classifier (Multi-class)...")
    X = train_df['text'].tolist()
    y = train_df['category'].tolist()

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=2500, stop_words='english')),
        ('clf', LogisticRegression(C=2.5, class_weight='balanced', max_iter=1000, random_state=42))
    ])

    pipeline.fit(X, y)
    out_path = os.path.join(MODELS_DIR, "event_classifier.joblib")
    joblib.dump(pipeline, out_path)
    print(f"[OK] Event Classifier trained on {len(X)} samples & saved to {out_path}")
    return pipeline

def train_sentiment_model(train_df):
    print("\n[2/3] Training Sentiment Classifier...")
    # Discretize continuous sentiment into 3 classes: -1 (negative), 0 (neutral), 1 (positive)
    X = train_df['text'].tolist()
    y = []
    for s in train_df['sentiment_score']:
        if s > 0.15:
            y.append(1)
        elif s < -0.15:
            y.append(-1)
        else:
            y.append(0)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=2000, stop_words='english')),
        ('clf', LogisticRegression(C=1.5, max_iter=1000, random_state=42))
    ])

    pipeline.fit(X, y)
    out_path = os.path.join(MODELS_DIR, "sentiment_pipeline.joblib")
    joblib.dump(pipeline, out_path)
    print(f"[OK] Sentiment Classifier trained on {len(X)} samples & saved to {out_path}")
    return pipeline

def train_impact_regressor(train_df):
    print("\n[3/3] Training Impact Severity Regressor...")
    X = train_df['text'].tolist()
    y = train_df['impact_score'].tolist()

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1500, stop_words='english')),
        ('reg', Ridge(alpha=1.0, random_state=42))
    ])

    pipeline.fit(X, y)
    out_path = os.path.join(MODELS_DIR, "impact_regressor.joblib")
    joblib.dump(pipeline, out_path)
    print(f"[OK] Impact Regressor trained on {len(X)} samples & saved to {out_path}")
    return pipeline

def main():
    news_csv = os.path.join(DATA_DIR, "news_events.csv")
    social_csv = os.path.join(DATA_DIR, "social_events.csv")

    if not os.path.exists(news_csv) or not os.path.exists(social_csv):
        print("Data files not found. Running generate_demo_data.py first...")
        from scripts.generate_demo_data import main as gen_data
        gen_data()

    news_df = pd.read_csv(news_csv)
    social_df = pd.read_csv(social_csv)
    combined_df = pd.concat([news_df, social_df], ignore_index=True)

    print(f"Combined Training Corpus: {len(combined_df)} records across {len(combined_df['category'].unique())} categories.")
    
    train_event_classifier(combined_df)
    train_sentiment_model(combined_df)
    train_impact_regressor(combined_df)
    print("\n[OK] All NLP/ML models successfully trained and stored in backend/ml/saved_models/")

if __name__ == "__main__":
    main()
