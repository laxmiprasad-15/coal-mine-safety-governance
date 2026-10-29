@echo off
title Coal Mine Safety System Launcher
echo ========================================================
echo Launching Coal Mine Safety Governance Application...
echo 1. Backend (FastAPI on Port 8000)
echo 2. Frontend (React Vite on Port 5173)
echo ========================================================
start "Coal Mine Backend" cmd /k "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "Coal Mine Frontend" cmd /k "%~dp0run_frontend.bat"
echo.
echo Both servers are launching!
echo Frontend: http://localhost:5173/
echo API Docs: http://localhost:8000/docs

