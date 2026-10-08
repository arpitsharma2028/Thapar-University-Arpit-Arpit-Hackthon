import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("finsight.main")

from backend.database.db import init_db
from backend.ml.nlp_engine import get_risk_engine
from backend.api import events_router, portfolio_router, stress_router, metrics_router, market_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing FinSight AI Market & Portfolio Risk Intelligence Engine...")
    init_db()
    get_risk_engine()
    logger.info("Core engine services and statistical models operational.")
    yield
    logger.info("Shutting down FinSight AI Engine...")

app = FastAPI(
    title="FinSight AI — Quantitative Risk Intelligence Platform",
    description=(
        "Institutional platform for high-frequency unstructured financial text processing, "
        "tactical index dynamic rebalancing (Module A), wholesale multi-asset portfolio stress testing (Module B), "
        "and stochastic Monte Carlo price forecasting."
    ),
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(portfolio_router)
app.include_router(stress_router)
app.include_router(metrics_router)
app.include_router(market_router)

@app.get("/")
def root():
    return {
        "service": "FinSight AI Quantitative Risk Intelligence Platform",
        "version": "1.1.0",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
