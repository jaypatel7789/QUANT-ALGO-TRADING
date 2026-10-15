@echo off
title Shark MT5 Sentinel - Mobile Command Center
color 0b
echo ========================================================
echo   SHARK MT5 SENTINEL - MOBILE COMMAND CENTER
echo ========================================================
echo.
echo Starting FastAPI & WebSocket Server on http://0.0.0.0:8080 ...
echo.
cd /d "%~dp0backend"
python -m uvicorn server:app --host 0.0.0.0 --port 8080
pause
