# S&P Global & CRISIL Campus Hackathon 2026 — Submission Checklist

This document tracks the verification status of all deliverables and technical requirements for the **FinSight AI** platform submission.

---

## 1. Candidate & Submission Metadata
- **Candidate Name:** Arpit Sharma
- **College Email ID:** asharma32_be22@thapar.edu
- **College / Campus:** Thapar Institute of Engineering and Technology (TIET)
- **GitHub Repository:** [https://github.com/arpitsharma2028/Thapar-University-Arpit-Arpit-Hackthon](https://github.com/arpitsharma2028/Thapar-University-Arpit-Arpit-Hackthon)
- **Demo Video Link:** `[PENDING USER ACTION]` *(Record and upload &le; 5 min demo video; add link to README)*
- **Slide Deck Link:** `[PENDING USER ACTION]` *(Upload presentation or share drive link; local PDF generated at `docs/presentation.pdf`)*

---

## 2. Technical Implementation Status

| Component | Status | Verification Notes |
| :--- | :--- | :--- |
| **Backend Services (FastAPI)** | Completed | Clean Architecture with routers, domain repositories, defensive middleware (CORS, rate limiting, request validation), and structured exception handling. |
| **Unified NLP Risk Engine** | Completed | Financial sentiment analysis (`ProsusAI/finbert` with calibrated offline fallback), robust 3-token negation window reset, evidence-based event classification across 9 financial categories (no arbitrary default tickers), active Ridge regression impact scoring. Evaluated on dual benchmarks: In-domain PhraseBank (89.0% Acc, 88.7% Macro-F1) and independent unseen news (69.3% Acc, 68.6% Macro-F1). |
| **Module A (Tactical Index Rebalancer)** | Completed | Mark-to-market portfolio accounting, bounded simplex reallocation ensuring $w_i \in [1.0\%, 25.0\%]$ and $\sum w_i \equiv 100.00\%$, 15% turnover cap, 5 bps transaction fees, equal-weight benchmark comparison. |
| **Module B (Wholesale Stress Testing)** | Completed | Deterministic wholesale banking multi-asset stress simulation ($50M portfolio across Equities, Bonds, Derivatives, Cash); explicit $> 7.0$ impact threshold mapping; verified -$4.6875M (-9.38%) geopolitical loss at 1.0x baseline and -$7.50M (-15.00%) at 1.6x amplified shock. |
| **Market Data Intelligence** | Completed | Unified OHLCV data contract across Overview and Market Analytics; explicit data-source metadata (`yfinance` vs `synthetic_fallback` anchored to NVDA @ $875.0); 100-path Monte Carlo Geometric Brownian Motion forecasts. |
| **Public Data Ingestion Path** | Completed | Live unauthenticated WSJ Markets / MarketWatch RSS ingestion service with SHA-256 deduplication alongside deterministic synthetic data replay; full offline compatibility. |
| **Frontend Application (React + Vite)** | Completed | Liquid Glass dark aesthetic, responsive layouts, 7 functional pages, interactive custom text analysis sandbox with manual/demo source attribution, Recharts visualizations. Production build verified. |

---

## 3. Automated Testing & Quality Assurance

| Test Suite / Metric | Status | Verified Result |
| :--- | :--- | :--- |
| **Pytest Suite (`backend/tests/`)** | Completed | **40 passed out of 40 in 10.61s** on isolated temporary SQLite fixtures without requiring pre-seeded database. |
| **Code Coverage** | Not Verified | Not claiming 100% test coverage without an automated coverage report tool; all core API endpoints, NLP features, boundary thresholds (> 7.0 vs 7.0), rebalancer invariants, and stress scenarios are tested. |
| **Frontend Production Build** | Completed | `npm run build` succeeds cleanly with zero compiler errors (2,488 modules bundled in 624ms). |
| **Clean Clone Setup** | Completed | Setup instructions verified with isolated virtual environment and dependency installation. |

---

## 4. Deliverables & Documentation

- [x] **`README.md`:** Updated with clone instructions, verified runtime specs, architecture diagram embed, API examples, dual evaluation results, reconciled stress testing settings, and honest dependency disclosures. Video and slide deck placeholders preserved for manual addition.
- [x] **`LICENSE`:** MIT License assigned to `Copyright (c) 2026 Arpit Sharma`.
- [x] **Architecture Diagram:** Saved at `docs/architecture.png` and embedded directly in README.
- [x] **Presentation Deck:** Generated at `docs/presentation.pdf` (7 slides matching hackathon criteria, `CONFIDENTIAL & PROPRIETARY` footer removed, numerical claims aligned with code).
- [x] **Demo Walkthrough Script:** Available at `docs/demo_script.md` formatted strictly for &le; 5 minutes video walkthrough.
- [x] **Synthetic & Baseline Data:** In `/data` (`news_events.csv`, `social_events.csv`, `companies.csv`, `portfolio.csv`, `market_data.csv`, `stress_scenarios.json`, `independent_financial_news_test.csv`).

---

## 5. Pending Manual Actions for Final Submission

- [ ] **Record &le; 5-Minute Demo Video:**
  - Follow the walkthrough sequence in `docs/demo_script.md` (DoSelect official maximum: 5 minutes).
  - Capture both the running backend terminal and the live dashboard at `http://localhost:5173`.
  - Upload to YouTube (Unlisted) or Google Drive (Public view).
- [ ] **Add Demo Video URL & Slide Deck URL to `README.md`:**
  - Replace `[TO BE ADDED]` in `README.md` with your actual video and deck links.
- [ ] **Submit Official Hackathon Portal Form:**
  - Paste GitHub Repository URL: `https://github.com/arpitsharma2028/Thapar-University-Arpit-Arpit-Hackthon`
  - Paste Demo Video URL.
  - Upload `docs/presentation.pdf`.
