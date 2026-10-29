@echo off
title START COAL MINE SAFETY SYSTEM
color 0A

echo ===================================================================
echo     AI-DRIVEN DIGITAL TWIN FOR COAL MINE SAFETY GOVERNANCE
echo ===================================================================
echo.
echo [1/3] Setting up Node.js & Python environment...
set "PATH=%~dp0tools\node;C:\Users\SAIPRATAP\AppData\Local\Programs\Python\Python313;%PATH%"

echo [2/3] Launching FastAPI Backend on Port 8000...
start "Coal Mine - Backend (FastAPI)" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo [3/3] Launching React Frontend on Port 5173...
start "Coal Mine - Frontend (React)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Waiting 4 seconds for servers to initialize...
timeout /t 4 /nobreak >nul

echo.
echo ===================================================================
echo [SUCCESS] Both servers are launching!
echo.
echo Desktop Web Portal:  http://localhost:5173/
echo Mobile Field App:    http://localhost:5173/mobile
echo API Documentation:   http://localhost:8000/docs
echo ===================================================================
echo.
echo Opening system in your default browser now...
start http://localhost:5173/

echo.
echo Press any key to close this launcher window (servers will stay running).
pause >nul
