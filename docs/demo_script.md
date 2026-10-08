# FinSight AI — Demo Script & Hackathon Presentation Walkthrough
**Platform:** Market & Portfolio Risk Intelligence Platform  
**Hackathon:** S&P Global & CRISIL Campus Hackathon 2026  
**Candidate Name:** Lead Engineer  
**College / Campus:** Thapar Institute of Engineering and Technology (TIET)  
**Total Target Walkthrough Duration:** 7–10 Minutes  

---

## 1. The 60-Second Elevator Pitch

> *"Respected Judges, in quantitative asset management and wholesale banking, information latency is the single greatest catalyst for severe portfolio drawdowns. Traditional risk systems look at backward-looking historical volatility matrices, missing the critical window when catastrophic news, regulatory enforcement, or social momentum first breaks.*
>
> *We built **FinSight AI** — a high-speed, lightweight, unified NLP Risk Intelligence platform that bridges unstructured market text directly into programmatic portfolio decisions. Running entirely on a standard CPU without requiring GPUs, FinSight AI parses news articles and social media feeds in under 20 milliseconds, extracts sentiment polarity, assigns structured risk categories, calculates predictive impact severity, and drives two core downstream engines:*
>
> 1. ***Module A (Tactical Index Rebalancer):*** *Dynamically rebalances stock index weights using a bounded sensitivity formula with strict 100% normalization.*
> 2. ***Module B (Strategic Stress Testing):*** *Automatically detects high-impact shocks (severity &ge; 7.0) and simulates catastrophic capital loss across a $50M wholesale banking book of Equities, Bonds, Derivatives, and Cash.*
>
> *Let us now walk you through the live, interactive system."*

---

## 2. Minute-by-Minute Live Demo Walkthrough (7–10 Minutes)

### Minute 0:00 – 1:30 | Screen 1: Executive Overview Dashboard
* **What screen to open:** Open `http://localhost:5173/` (Nav: **Overview**).
* **What to point out:**
  1. **Top Bar Live Ticker:** Shows continuous risk feed ingestion from the SQLite store.
  2. **Top KPI Cards:**
     - Portfolio Valuation: `$10.00M` baseline.
     - Portfolio Sentiment: `+0.05` (Neutral to Moderately Bullish).
     - 1-Day VaR (95%): `$245K` parametric loss estimate.
     - Engine Decisions: Rebalances & Stress tests logged.
  3. **Interactive Recharts:**
     - Point to the **Valuation Dynamic Trajectory** line chart (mark-to-market performance).
     - Point to the **Index Sector Diversification** donut chart (Technology, Financials, Energy, etc.).
  4. **Latest NLP Risk Signals Table:** Point out the color-coded **Category Badges** (Geopolitical, Macro, Credit, Earnings), **Sentiment Badges**, and **Severity Badges** (1.0 to 10.0 scale).

* **What to explain to judges:**
  > *"Notice how cleanly our design integrates high-density institutional metrics without clutter. Every number here is computed dynamically from real database records, not hardcoded mockups."*

---

### Minute 1:30 – 3:30 | Screen 2: Unified NLP Risk Engine Explorer
* **What screen to open:** Click on **Risk Intelligence** in the left sidebar.
* **What to explain:**
  > *"Here is our core NLP engine. Instead of calling expensive third-party APIs that can fail during a demo or require confidential data, we implemented a CPU-optimized, scikit-learn pipeline combined with Loughran-McDonald financial sentiment lexicons."*
* **What action to take (Live Demo Step):**
  1. Under **"Load Demo Prompt"**, click the button: **`Geopolitical Strait Tension`**.
  2. Show that the textarea populates with:
     > *"Naval escort operations initiated in Red Sea after commercial tanker attacks; oil insurance premiums spike 45% and container rerouting adds 14 days transit."*
  3. Click the blue button: **`Analyze & Extract Risk Signal`**.
* **What output appears:**
  - Instantly (< 25 ms), the **Extracted Risk Signal Output** box renders:
    - **Sentiment Polarity:** `Negative / Bearish (-0.68 to -0.75)`
    - **Event Taxonomy:** `Geopolitical`
    - **Predicted Severity:** `8.5 / 10 (High Risk)`
    - **Identified Entities & Sector:** `Energy (XOM, CVX)`
    - **Model Confidence:** `91%`
* **What to explain to judges:**
  > *"Notice how the model caught the numerical intensity (+45% insurance spike) and severity terms ('tanker attacks', 'rerouting') to assign an 8.5 impact score, classifying it as Geopolitical. We can immediately route this structured signal downstream."*

---

### Minute 3:30 – 5:30 | Screen 3: Module A — Tactical Index Rebalancer
* **What screen to open:** Click on **Module A — Rebalancer** in the left sidebar.
* **What to explain:**
  > *"Module A addresses tactical high-frequency rebalancing for a 16-asset blue-chip index. Every stock starts with an initial target allocation summing exactly to 100%."*
* **What action to take (Live Demo Step):**
  1. Highlight the **Algorithmic Weight Rebalance Formula** card:
     $$\text{new\_weight}_i = \text{clamp}(\text{old\_weight}_i + \lambda \times \text{sentiment} \times (\text{impact}/10), 1.0\%, 25.0\%)$$
     followed by strict normalization $\sum w_i = 100.0\%$.
  2. Adjust the **Sensitivity Slider ($\lambda$)** to `0.035`.
  3. Click **`Simulate Next Event`** (or click **`Batch Simulate (5 Events)`**).
* **What output appears:**
  1. The **Latest Rebalance Trigger Event** banner updates with the triggering headline, sentiment, and portfolio value delta.
  2. The **Stock Allocation Weight Changes (Before vs After)** grouped bar chart animates:
     - Positive sentiment stocks (e.g., $NVDA on earnings beat) visibly grow in green.
     - Negative sentiment stocks (e.g., $TSLA on margin contraction) visibly shrink in red.
  3. The **16-Asset Portfolio Table** shows updated current weights, share counts, mark-to-market prices, and basis-point deltas.
* **What to explain to judges:**
  > *"Notice how the algorithm strictly prevents negative weights and enforces the 1% floor and 25% concentration ceiling, while total portfolio weight always normalizes to exactly 100.00%."*

---

### Minute 5:30 – 7:30 | Screen 4: Module B — Wholesale Portfolio Stress Testing
* **What screen to open:** Click on **Module B — Stress Testing** in the left sidebar.
* **What to explain:**
  > *"While Module A manages tactical single-stock weights, Module B evaluates strategic solvency for a wholesale banking institution managing a $50 Million multi-asset portfolio (Equities, Bonds, Derivatives, and Cash)."*
* **What action to take (Live Demo Step):**
  1. Select the scenario card: **`Global Geopolitical Escalation & Supply Chain Severance`** (Severity `9.2/10`).
  2. Point out the Severity Multiplier slider (`1.0x`).
  3. Click the red button: **`Execute Stress Test`**.
* **What output appears:**
  1. **Pre-Stress Wholesale Value:** `$50.00M`.
  2. **Total Simulated Capital Loss:** `-$8.25M (-16.50%)`.
  3. **Post-Stress Book Value:** `$41.75M`.
  4. **Asset Class Loss Distribution Chart:**
     - Equities: `-$3.71M (-16.5%)`
     - Derivatives: `-$1.65M (-22.0%)`
     - Bonds: `+$0.68M (+4.5% safe haven flight)`
     - Cash: `$0.00M (Capital preserved)`
  5. **Worst Affected Positions:** Technology (`-$1.77M`), Industrials, and Financials.
* **What to explain to judges:**
  > *"Notice how our stress engine doesn't just apply a blanket shock. Bonds act as a flight-to-safety buffer, derivatives face amplified non-linear volatility losses, and energy rallies while tech suffers from semiconductor embargoes."*

---

### Minute 7:30 – 8:30 | Screen 5 & 6: Event Explorer & Regulatory Audit Trail
* **What screen to open:**
  1. Click on **Event Explorer**: Show judges the multi-dimensional filters (Filter by News vs Social, Category, Severity &ge; 7.0, Search). Click on any event to open the detailed **Event Modal**.
  2. Click on **Simulation History**: Show the immutable audit trail of all rebalance decisions and stress test runs with exact timestamps and dollar shifts.

---

### Minute 8:30 – 9:30 | 1-Click Master Scenario & Conclusion
* **What action to take:**
  - From anywhere in the application, click the purple button in the top header: **`Run Demo Scenario`**.
* **What happens:**
  - In one unified execution, the platform:
    1. Injects a high-severity geopolitical event into the NLP engine.
    2. Runs Module A tactical rebalancing.
    3. Detects severity &ge; 7.0 and triggers Module B wholesale stress testing.
    4. Displays a confirmation toast with loss figures and redirects to the refreshed Overview.
* **Closing Remarks to Judges:**
  > *"FinSight AI represents a comprehensive, fully functional, mathematically sound implementation of market text risk intelligence. The entire system is running right here locally on this laptop, backed by automated tests, clean REST APIs, and an institutional dashboard. Thank you, and we welcome your questions."*

---

## 3. Potential Judge Questions & Suggested Answers

**Q1: Is this using real LLMs like GPT-4 or OpenAI?**  
*Answer:* *"We deliberately designed this system using a lightweight, CPU-optimized scikit-learn pipeline combined with Loughran-McDonald financial lexicons and calibrated regressors. This guarantees deterministic sub-20ms inference, runs entirely offline on standard hardware without GPU or API key dependencies, and eliminates prompt injection vulnerabilities in automated rebalancing."*

**Q2: How do you prevent negative weights or runaway concentration in Module A?**  
*Answer:* *"Our formula applies a three-stage mathematical safeguard: first, weight deltas are proportional to sentiment and impact severity; second, we clamp every stock to a configured floor (min 1.0%) and ceiling (max 25.0%); third, we apply a vector normalization step dividing each weight by the sum of weights, ensuring the portfolio always sums strictly to 100.00%."*

**Q3: How would you connect this to real S&P Global and CRISIL data in production?**  
*Answer:* *"Our ingestion layer is fully decoupled behind the `EventService` interface. Connecting to the S&P Capital IQ API, S&P Global Market Intelligence News Wire, or CRISIL credit rating bulletins simply requires implementing a lightweight WebSocket/REST adapter that serializes inbound JSON into our existing Pydantic schema."*
