# S&P Global & CRISIL Campus Hackathon 2026 — Submission Checklist

This document tracks the verification status of all deliverables and technical requirements for the **FinSight AI** platform submission.

---

## 1. Candidate & Submission Metadata
- **Candidate Name:** Arpit Sharma
- **College Email ID:** asharma32_be22@thapar.edu
- **College / Campus:** Thapar Institute of Engineering and Technology (TIET)
- **GitHub Repository:** [https://github.com/arpitsharma2028/Thapar-University-Arpit-Arpit-Hackthon](https://github.com/arpitsharma2028/Thapar-University-Arpit-Arpit-Hackthon)
- **Demo Video Link:** `[PENDING USER ACTION]` *(Record and upload 7–10 min demo video; add link to README)*
- **Slide Deck Link:** `[PENDING USER ACTION]` *(Upload presentation or share drive link; local PDF generated at `docs/presentation.pdf`)*

---

## 2. Technical Implementation Status

| Component | Status | Verification Notes |
| :--- | :--- | :--- |
| **Backend Services (FastAPI)** | Completed | Clean Architecture with routers, domain repositories, defensive middleware (CORS, rate limiting, request validation), and structured exception handling. |
| **Unified NLP Risk Engine** | Completed | Financial sentiment analysis (ProsusAI/FinBERT with calibrated offline fallback), robust negation handling, evidence-based event classification (no arbitrary default tickers), and regression-based impact scoring. |
| **Module A (Tactical Index Rebalancer)** | Completed | Mark-to-market portfolio accounting, bounded sensitivity delta with strict simplex normalization, turnover and transaction cost controls, equal-weight benchmark comparison. |
| **Module B (Wholesale Stress Testing)** | Completed | Deterministic wholesale banking multi-asset stress simulation ($50M portfolio across Equities, Bonds, Derivatives, Cash); explicit $\ge 7.0$ impact threshold mapping; verified -$4.69M (-9.38%) geopolitical loss. |
| **Market Data Intelligence** | Completed | Unified OHLCV data contract across Overview and Market Analytics; explicit data-source metadata (`yfinance` vs `synthetic_fallback`); 100-path Monte Carlo Geometric Brownian Motion forecasts. |
| **Public Data Ingestion Path** | Completed | Public low-friction financial RSS ingestion service alongside deterministic synthetic data replay; full offline compatibility. |
| **Frontend Application (React + Vite)** | Completed | Liquid Glass dark aesthetic, responsive layouts, 7 functional pages, interactive custom text analysis sandbox, Recharts visualizations. Production build verified. |

---

## 3. Automated Testing & Quality Assurance

| Test Suite / Metric | Status | Verified Result |
| :--- | :--- | :--- |
| **Pytest Suite (`backend/tests/`)** | Completed | Automated test suite passes cleanly on isolated temporary SQLite fixtures without requiring pre-seeded database. |
| **Code Coverage** | Not Verified | Not claiming 100% test coverage without an automated coverage report tool; all core API endpoints, NLP features, rebalancer invariants, and stress scenarios are tested. |
| **Frontend Production Build** | Completed | `npm run build` succeeds cleanly with zero compiler errors. |
| **Clean Clone Setup** | Completed | Setup instructions verified with isolated virtual environment and dependency installation. |

---

## 4. Deliverables & Documentation

- [x] **`README.md`:** Updated with clone instructions, verified runtime specs, architecture diagram embed, API examples, evaluation results, and honest dependency disclosures. Video and slide deck placeholders preserved for manual addition.
- [x] **`LICENSE`:** MIT License assigned to `Copyright (c) 2026 Arpit Sharma`.
- [x] **Architecture Diagram:** Saved at `docs/architecture.png` and embedded directly in README.
- [x] **Presentation Deck:** Generated at `docs/presentation.pdf` (7 slides matching hackathon criteria, `CONFIDENTIAL & PROPRIETARY` footer removed, numerical claims aligned with code).
- [x] **Demo Walkthrough Script:** Available at `docs/demo_script.md` for recording guidance.
- [x] **Synthetic & Baseline Data:** In `/data` (`news_events.csv`, `social_events.csv`, `companies.csv`, `portfolio.csv`, `market_data.csv`, `stress_scenarios.json`).

---

## 5. Pending Manual Actions for Final Submission

- [ ] **Record 7–10 Minute Demo Video:**
  - Follow the walkthrough sequence in `docs/demo_script.md`.
  - Capture both the running backend terminal and the live dashboard at `http://localhost:5173`.
  - Upload to YouTube (Unlisted) or Google Drive (Public view).
- [ ] **Add Demo Video URL & Slide Deck URL to `README.md`:**
  - Replace `[TO BE ADDED]` in `README.md` with your actual video and deck links.
- [ ] **Submit Official Hackathon Portal Form:**
  - Paste GitHub Repository URL: `https://github.com/arpitsharma2028/Thapar-University-Arpit-Arpit-Hackthon`
  - Paste Demo Video URL.
  - Upload `docs/presentation.pdf`.
