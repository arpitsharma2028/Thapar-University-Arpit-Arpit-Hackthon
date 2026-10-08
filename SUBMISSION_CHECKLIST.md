# S&P Global & CRISIL Campus Hackathon 2026 — Submission Checklist

Use this checklist to verify all submission deliverables before submitting your entry.

---

## 1. Repository & Source Code Readiness
- [x] **Zero-Placeholder Implementation:** All features are fully functional; no dummy/fake buttons or mockup endpoints.
- [x] **Backend Services:** FastAPI application running with modular architecture (`backend/api`, `backend/services`, `backend/ml`, `backend/database`).
- [x] **Frontend Application:** React + Vite dashboard built with Recharts, custom dark terminal styling, and 7 active pages (including Market Intelligence & Monte Carlo).
- [x] **Local Execution:** Tested and verified on Windows 11 CPU without requiring external APIs or GPUs.
- [x] **Automated Test Suite:** 26/26 Pytest tests passing cleanly in `backend/tests/`.
- [x] **Package Configurations:** `requirements.txt` and `frontend/package.json` verified and locked.

---

## 2. Deliverables & Documentation
- [x] **`README.md`:** Follows official submission format with Problem Statement, Mermaid Diagram, Quickstart, API Docs, Module A, Module B, and Domain Impact.
- [x] **`LICENSE`:** Open-source MIT License included.
- [x] **Architecture Diagram:** Saved at `docs/architecture.png` (high-resolution PNG).
- [x] **Presentation Deck:** Saved at `docs/presentation.pdf` (7 slides matching official prompt structure).
- [x] **Demo Walkthrough Script:** Saved at `docs/demo_script.md` (includes 60-second elevator pitch and 7–10 minute minute-by-minute judge walkthrough).
- [x] **Datasets in `/data`:**
  - `data/news_events.csv` (50 records)
  - `data/social_events.csv` (40 records)
  - `data/companies.csv` (16 tickers)
  - `data/portfolio.csv` ($10M baseline)
  - `data/market_data.csv` (480 records)
  - `data/stress_scenarios.json` (5 wholesale stress scenarios)

---

## 3. Compliance & Ethics
- [x] **Confidentiality:** Zero confidential or proprietary S&P Global / CRISIL internal data used.
- [x] **Data Provenance:** All datasets explicitly labeled as synthetic or public reference market data.
- [x] **Safety & Governance:** No live trading or uncontrolled financial execution; all outputs are advisory risk signals.

---

## 4. Personal Action Items for You (Before Final Form Submission)
- [ ] **Push to Public GitHub Repository:**
  ```bash
  git init
  git add .
  git commit -m "FinSight AI - S&P Global & CRISIL Campus Hackathon 2026 Submission"
  git branch -M main
  git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
  git push -u origin main
  ```
  *(Ensure repository visibility is set to **Public**)*.
- [ ] **Fill Placeholders in `README.md`:**
  - Replace `[MY NAME]` with your full name.
  - Replace `[MY COLLEGE EMAIL]` with your college email.
  - Update `Demo Video Link` after recording.
  - Update `Slide Deck Link` (e.g., Google Drive or GitHub link).
- [ ] **Record 7–10 Minute Demo Video:**
  - Follow the exact sequence in `docs/demo_script.md`.
  - Record full screen showing both the terminal backend running and the browser dashboard at `http://localhost:5173`.
  - Upload to YouTube (Unlisted) or Google Drive (Public access).
- [ ] **Submit Official Hackathon Portal Form:**
  - Paste GitHub Repository URL.
  - Paste Demo Video URL.
  - Upload `docs/presentation.pdf`.
