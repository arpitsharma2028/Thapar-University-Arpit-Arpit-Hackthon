@echo off
title FinSight AI — Platform Launcher
color 0B

echo ===============================================================================
echo                FinSight AI — Market ^& Portfolio Risk Intelligence
echo            S^&P Global ^& CRISIL Campus Hackathon 2026 Submission
echo ===============================================================================
echo.

:: Ensure working directory is the script's root folder
cd /d "%~dp0"

:: 1. Check Python Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found in %~dp0venv
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python not found or failed to create venv. Please install Python 3.10+.
        pause
        exit /b 1
    )
    echo [*] Installing dependencies from requirements.txt...
    venv\Scripts\pip install -r requirements.txt
    echo [*] Seeding database and training NLP models...
    venv\Scripts\python scripts\generate_demo_data.py
    venv\Scripts\python scripts\train_models.py
    venv\Scripts\python scripts\seed_database.py
)

:: 2. Check Frontend node_modules
if not exist "frontend\node_modules\" (
    echo [*] Installing frontend npm dependencies...
    cd frontend
    call npm install
    cd ..
)

echo [*] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "FinSight AI — Backend Server" cmd /k "title FinSight AI Backend && cd /d "%~dp0" && call venv\Scripts\activate.bat && uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [*] Launching Vite Frontend on http://localhost:5173 ...
start "FinSight AI — Frontend Client" cmd /k "title FinSight AI Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo [*] Waiting 4 seconds for services to initialize...
timeout /t 4 /nobreak >nul

echo [*] Opening FinSight AI Dashboard in your default browser...
start http://localhost:5173

echo.
echo ===============================================================================
echo [SUCCESS] FinSight AI is running!
echo.
echo  - Frontend Dashboard : http://localhost:5173
echo  - Backend API Docs   : http://127.0.0.1:8000/docs
echo  - Backend Health     : http://127.0.0.1:8000/api/health
echo.
echo To stop the application, simply close the two opened terminal windows.
echo ===============================================================================
echo.
pause
