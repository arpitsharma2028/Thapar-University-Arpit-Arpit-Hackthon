# FinSight AI — NLP Model Evaluation & Benchmarking Report

This report documents the empirical evaluation of the FinSight AI Sentiment Analysis Engine against a naive keyword baseline on the gold-standard public **Financial PhraseBank** benchmark.

---

## 1. Dataset Provenance & Methodology
- **Dataset:** Financial PhraseBank (`Sentences_AllAgree` subset: 100% human-expert agreement).
- **Citation:** Malo, P., Sinha, A., Korhonen, P., Wallenius, J., & Takala, P. (2014). *Good debt or bad debt: Detecting semantic orientations in economic texts.* Journal of the Association for Information Science and Technology, 65(4), 782-796.
- **License:** Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0).
- **Evaluation Size:** 300 stratified examples (Seed = 42).
- **Class Distribution:** Positive (100), Neutral (100), Negative (100).
- **Train/Test Leakage Prevention:** Neither model was trained on these held-out benchmark sentences.

---

## 2. Quantitative Performance Comparison

| Model | Accuracy (%) | Macro-F1 (%) | Positive F1 | Neutral F1 | Negative F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Naive Keyword Baseline** | **50.33%** | **43.54%** | 50.8% | 62.1% | 17.7% |
| **FinSight NLP Engine** | **92.67%** | **92.59%** | **91.7%** | **90.8%** | **95.2%** |

### Per-Class Detailed Breakdown (FinSight Engine)
- **Positive:** Precision = 89.5%, Recall = 94.0%, F1 = 91.7%
- **Neutral:** Precision = 98.8%, Recall = 84.0%, F1 = 90.8%
- **Negative:** Precision = 90.9%, Recall = 100.0%, F1 = 95.2%

---

## 3. Measured Runtime & Latency Profile
- **Hardware:** Standard Laptop CPU (Windows 11, Python 3.11).
- **Cold-Start Model Initialization:** 4606.48 ms (one-time load into singleton).
- **Median Warm Inference Latency:** **30.52 ms** per headline.
- **95th Percentile (P95) Latency:** **50.15 ms** per headline.
- **Mean Latency:** 33.0 ms.

---

## 4. Observations & Limitations
1. **Generalization Over Baseline:** The FinSight NLP engine significantly outperforms naive keyword matching (Macro-F1 of 92.59% vs 43.54%) by capturing subtle financial phrasing, negations, and contrast clauses.
2. **Neutral Class Challenges:** Neutral statements in financial text often contain numbers and corporate terminology that keyword baselines mistake for positive or negative sentiment. FinBERT effectively dampens non-polarized statements.
3. **Reproducibility:** To re-run this exact evaluation benchmark, execute:
   ```bash
   python scripts/evaluate_nlp_models.py
   ```
