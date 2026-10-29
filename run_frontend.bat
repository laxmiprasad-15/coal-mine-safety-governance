@echo off
title Coal Mine Safety - React Frontend Server
echo ========================================================
echo Starting Coal Mine Safety React Frontend Server...
echo App will be at: http://localhost:5173/
echo ========================================================
cd /d "%~dp0frontend"
npm run dev
pause
