@echo off
title STOP COAL MINE SAFETY SYSTEM
color 0C
echo ===================================================================
echo     STOPPING ALL COAL MINE SAFETY SYSTEM PROCESSES...
echo ===================================================================
echo.
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
echo.
echo [DONE] All servers stopped and ports 8000 & 5173 freed.
timeout /t 2 >nul
