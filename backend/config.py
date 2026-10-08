import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "ml", "saved_models")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "finsight.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Rebalancing Parameters
DEFAULT_SENSITIVITY = 0.025  # Sensitivity coefficient in weight adjustment
MIN_STOCK_WEIGHT = 0.010    # 1.0% minimum weight floor (avoids zero/negative weights)
MAX_STOCK_WEIGHT = 0.250    # 25.0% maximum single-stock concentration cap
HIGH_IMPACT_THRESHOLD = 7.0 # Triggers stress testing consideration
INITIAL_PORTFOLIO_VALUE = 10_000_000.0  # $10M baseline wholesale/index portfolio
