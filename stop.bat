@echo off
title FinSight AI — Platform Stopper
color 0C

echo ===============================================================================
echo                FinSight AI — Stopping Platform Services
echo ===============================================================================
echo.

echo [*] Stopping Python / Uvicorn server processes...
taskkill /F /IM python.exe /T 2>nul

echo [*] Stopping Node / Vite dev server processes...
taskkill /F /IM node.exe /T 2>nul

echo.
echo [OK] All FinSight AI processes stopped cleanly.
echo.
pause
