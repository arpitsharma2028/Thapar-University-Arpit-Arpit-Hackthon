@echo off
title FinSight AI — Platform Services
setlocal enabledelayedexpansion

echo ===============================================================================
echo         FinSight AI — Quantitative Market ^& Portfolio Risk Intelligence
echo ===============================================================================
echo.

:: Ensure working directory is the repository root
cd /d "%~dp0"

:: 1. Verify / Configure Python Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [*] Initializing virtual environment in %~dp0venv ...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python 3.10+ required. Unable to create virtual environment.
        pause
        exit /b 1
    )
    echo [*] Installing dependencies from requirements.txt ...
    venv\Scripts\pip install -r requirements.txt
    echo [*] Initializing baseline datasets and model weights ...
    venv\Scripts\python scripts\generate_demo_data.py
    venv\Scripts\python scripts\train_models.py
    venv\Scripts\python scripts\seed_database.py
)

:: 2. Verify Frontend Dependencies
if not exist "frontend\node_modules\" (
    echo [*] Installing frontend dependencies ...
    cd frontend
    call npm install
    cd ..
)

echo [*] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "FinSight AI — Backend Server" cmd /k "title FinSight AI Backend && cd /d "%~dp0" && call venv\Scripts\activate.bat && uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo [*] Starting Vite Frontend on http://localhost:5173 ...
start "FinSight AI — Frontend Client" cmd /k "title FinSight AI Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo [*] Waiting for services to initialize ...
timeout /t 3 /nobreak >nul

echo [*] Launching dashboard at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ===============================================================================
echo Services operational:
echo   - Web Interface : http://localhost:5173
echo   - API Schema    : http://127.0.0.1:8000/docs
echo   - Health Check  : http://127.0.0.1:8000/api/health
echo.
echo To terminate services, close the backend and frontend terminal windows.
echo ===============================================================================
echo.
pause
