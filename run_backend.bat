@echo off
title Coal Mine Safety - Backend API Server
echo ========================================================
echo Starting Coal Mine Safety FastAPI Backend Server...
echo API Docs will be at: http://localhost:8000/docs
echo ========================================================
cd /d "%~dp0backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
