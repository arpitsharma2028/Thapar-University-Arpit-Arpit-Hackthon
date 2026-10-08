import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database.db import init_db
from backend.ml.nlp_engine import get_risk_engine
from backend.api import events_router, portfolio_router, stress_router, metrics_router, market_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB and pre-warm NLP Engine
    print("=" * 60)
    print("Starting FinSight AI — Market & Portfolio Risk Intelligence Engine")
    print("=" * 60)
    init_db()
    # Pre-warm ML models
    get_risk_engine()
    yield
    print("Shutting down FinSight AI Engine...")

app = FastAPI(
    title="FinSight AI — Market & Portfolio Risk Intelligence Platform",
    description=(
        "API for S&P Global & CRISIL Campus Hackathon 2026. "
        "Provides NLP risk event extraction, tactical index dynamic rebalancing (Module A), "
        "wholesale portfolio stress testing (Module B), and Monte Carlo quantitative forecasting."
    ),
    version="1.1.0",
    lifespan=lifespan
)

# Enable CORS for frontend Vite dev server (and any origin for hackathon evaluation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(events_router)
app.include_router(portfolio_router)
app.include_router(stress_router)
app.include_router(metrics_router)
app.include_router(market_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to FinSight AI API",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
