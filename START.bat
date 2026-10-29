@echo off
title COAL MINE SAFETY GOVERNANCE SYSTEM
cd /d "%~dp0"
set "PATH=%~dp0tools\node;C:\Users\SAIPRATAP\AppData\Local\Programs\Python\Python313;%PATH%"
python run.py
pause
