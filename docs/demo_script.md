# FinSight AI — Official 5-Minute Demo Video Walkthrough Script

**Platform:** FinSight AI — Market & Portfolio Risk Intelligence  
**Hackathon:** S&P Global & CRISIL Campus Hackathon 2026  
**Candidate Name:** Arpit Sharma  
**College / Campus:** Thapar Institute of Engineering and Technology (TIET)  
**Strict Video Duration Target:** **Under 5:00 Minutes** *(Mandated by DoSelect Case Study Guidelines: "A functional live demonstration of the application, not to exceed 5 minutes")*

---

## 1. The 45-Second Elevator Pitch (0:00 – 0:45)

> *"Respected Judges, in quantitative asset management and institutional credit surveillance, information latency is the single greatest driver of portfolio drawdowns. Traditional risk architectures rely heavily on lagging covariance matrices and end-of-day VaR, missing the critical window when catastrophic news, regulatory enforcement, or supply chain shocks first break in textual wire feeds.
>
> We built **FinSight AI** — a lightweight, institutional-grade financial NLP risk intelligence platform that bridges unstructured market text directly into programmatic portfolio decisions. Running 100% locally on CPU without remote cloud LLMs, FinSight AI parses news and social streams in under 35 milliseconds, extracts sentiment, classifies financial taxonomy across 9 categories, scores predictive impact severity, and drives two coordinated downstream execution engines:
> - **Module A (Tactical Index Rebalancer):** Continuously reallocates a 16-asset blue-chip index using bounded simplex projection ($w_i \in [1\%, 25\%]$, $\sum w_i \equiv 100\%$), 15% turnover cap, and equal-weight benchmark tracking.
> - **Module B (Strategic Wholesale Stress Testing):** Detects systemic shock breaches ($\text{impact} > 7.0$) and simulates multi-asset capital loss on a $50M wholesale banking book.
>
> Let us walk through the live application."*

---

## 2. Minute-by-Minute Screen Walkthrough (0:45 – 5:00)

### Segment 1: NLP Risk Intelligence & Custom Signal Sandbox (0:45 – 1:45)
- **Screen to open:** Navigate to `Risk Intelligence` tab (`/nlp`).
- **Actions to perform:**
  1. Show the **Interactive NLP Sandbox**. Click the preset button: *"Geopolitical Strait Tension"*.
  2. Notice that the publisher source is accurately displayed as *"Curated Maritime News Demo"* (not misattributed).
  3. Click **"Analyze & Extract Risk Signal"**.
  4. Point out the extracted output ribbon:
     - **Sentiment Score:** Negative (-0.72) via `ProsusAI/finbert`.
     - **Event Taxonomy:** Geopolitical.
     - **Predicted Severity:** 8.5 / 10 via the active Ridge regression pipeline.
     - **Softmax Decision Margin:** Displayed transparently from model logits.
     - **Traceability:** Persisted in SQLite event log.
  5. Show the downstream action buttons enabled: *"Apply Signal to Tactical Rebalancer"* and *"Stress Test Wholesale Portfolio (Impact > 7.0)"*.
  6. *(Optional quick check):* Enter *"Local bakery wins award for best croissant"* $\to$ Show it correctly classifies as `Other` with empty tickers `[]`, proving the engine never forces noise into `Earnings` or defaults to `SPY`.

### Segment 2: Module A — Tactical Index Rebalancer (1:45 – 2:45)
- **Screen to open:** Navigate to `Module A: Tactical Rebalancer` tab (`/module-a`).
- **Actions to perform:**
  1. Show the **Algorithmic Weight Rebalance Formula** card explaining the 3-step bounded simplex redistribution ($w_i \in [1\%, 25\%]$, $\sum w_i = 100\%$).
  2. Show the **Active Safeguards Ribbon**: Max Turnover Cap (15.0%), Transaction Fee (5 bps), Benchmark Reference (Equal-Weight 16-Stock Index).
  3. Adjust the Sensitivity slider ($\lambda = 0.035$) and click **"Simulate Next Event"**.
  4. Point out the results:
     - **Stock Allocation Bar Chart:** Clear Before vs After comparison across 16 blue chips.
     - **Safeguard Enforcement:** NVDA/Tech weights adjust dynamically while respecting the 25% upper ceiling and 1% floor.
     - **Turnover & Fee Accounting:** Shows turnover percentage within the 15% cap and realistic transaction fees deducted mark-to-market.
     - **Strategy vs Equal-Weight Benchmark:** Dynamic tracking of cumulative returns against the benchmark.

### Segment 3: Module B — Wholesale Portfolio Stress Testing (2:45 – 3:45)
- **Screen to open:** Navigate to `Module B: Wholesale Stress Testing` tab (`/module-b`).
- **Actions to perform:**
  1. Point out the baseline wholesale balance sheet: **$50.0 Million** book across Equities ($22.5M, 45%), Bonds ($15.0M, 30%), Derivatives ($7.5M, 15%), and Cash ($5.0M, 10%).
  2. Point out the systemic threshold badge: **High-Impact Trigger Threshold > 7.0**.
  3. Select **"Global Geopolitical Escalation"** (Severity 9.2) with **Severity Multiplier = 1.0x (Baseline)**. Click **"Execute Stress Test"**:
     - **Total Capital Loss:** -$4.69M (-9.38%), Post-stress value: $45.31M.
     - **Asset-Level Shock Transmission:** Equities loses -$3.71M (-16.5%), Bonds gains +$0.68M (+4.5% flight-to-safety), Derivatives loses -$1.65M (-22.0%), Cash has $0.00 loss.
  4. Now move the Severity Multiplier slider to **1.6x (Amplified Shock)** and click **"Execute Stress Test"**:
     - **Amplified Capital Loss:** Exactly -$7.50M (-15.00%), Post-stress value: $42.50M.
     - Highlight that both baseline (1.0x) and amplified (1.6x) shock settings are deterministically traceable and verified in code.

### Segment 4: Live Public Data Ingestion & Market Analytics (3:45 – 4:30)
- **Screen to open:** Navigate to `Event Explorer` tab (`/events`).
- **Actions to perform:**
  1. Show the event table populated from the local SQLite store.
  2. Click the blue **"Ingest Live RSS"** button:
     - Shows live HTTP polling of the Wall Street Journal / MarketWatch RSS feed.
     - Live market headlines are normalized into structured risk signals and appended to the table with source badge *"WSJ Markets RSS"*.
  3. Jump to `Market Intelligence` tab (`/market-intel`):
     - Show the **100-path Monte Carlo Geometric Brownian Motion (GBM)** price projection cone (P5 to P95) conditioned on NLP sentiment drift.
     - Show the Base-100 normalized cross-asset correlation matrix.

### Segment 5: QA Verification & Closing Summary (4:30 – 5:00)
- **Screen to open:** Show terminal or summarize key technical metrics.
- **Talking points:**
  - **Automated Testing:** 40 / 40 passing unit and integration tests executing on isolated temporary database fixtures.
  - **Empirical NLP Evaluation:** Evaluated on both in-domain PhraseBank (89.0% Acc, 88.7% F1) and an independent unseen dataset (69.3% Acc, 68.6% F1) without data contamination.
  - **CPU Latency:** Median warm inference of ~29 ms without requiring cloud GPUs or paid APIs.
  - **Closing Statement:** *"FinSight AI delivers a completely transparent, reproducible, and production-ready financial risk intelligence prototype. Thank you."*
