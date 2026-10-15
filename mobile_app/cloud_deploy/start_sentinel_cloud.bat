@echo off
title Shark MT5 Sentinel - Cloud VPS Service Runner
color 0b
echo =====================================================================
echo       SHARK MT5 SENTINEL - CLOUD VPS 24/7 SERVICE RUNNER
echo =====================================================================
echo.

:: 1. Search for Python in all known install paths
set "PY="
if exist "C:\Program Files\Python311\python.exe" set "PY=C:\Program Files\Python311\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PY if exist "C:\Program Files\Python312\python.exe" set "PY=C:\Program Files\Python312\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "C:\Python311\python.exe" set "PY=C:\Python311\python.exe"
if not defined PY if exist "C:\Python312\python.exe" set "PY=C:\Python312\python.exe"

:: 2. Check PATH as fallback
if not defined PY (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 set "PY=python"
)

:: 3. If STILL not found, auto-download and install Python 3.11 silently
if not defined PY (
    echo [1/4] Python not found on VPS. Auto-installing Python 3.11 (30s)...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '$env:TEMP\py_setup.exe'; Start-Process '$env:TEMP\py_setup.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1' -Wait; Remove-Item '$env:TEMP\py_setup.exe' -Force"
    if exist "C:\Program Files\Python311\python.exe" set "PY=C:\Program Files\Python311\python.exe"
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

if not defined PY (
    echo [ERROR] Could not locate or install Python. Please check internet connection.
    pause
    exit /b 1
)

echo [ACTIVE] Python Engine Detected: "%PY%"
echo.

:: 4. Verify & Install Python Dependencies
echo [2/4] Verifying Python Dependencies (fastapi, uvicorn, psutil, MetaTrader5)...
"%PY%" -m pip install --quiet fastapi uvicorn psutil requests websockets MetaTrader5

:: 5. Check Cloudflare Tunnel Client
echo [3/4] Checking Cloudflare Tunnel Executable...
if not exist "%~dp0cloudflared.exe" (
    echo Downloading lightweight zero-config cloudflared tunnel client...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%~dp0cloudflared.exe'"
)

:: 6. Launch Backend Server
echo [4/4] Starting FastAPI Sentinel Backend on Port 8080...
cd /d "%~dp0..\backend"
start /min "SharkSentinelBackend" "%PY%" -m uvicorn server:app --host 127.0.0.1 --port 8080

echo.
echo =====================================================================
echo Starting Cloudflare Secure HTTPS Tunnel for Mobile Access...
echo Once started, look for the 'https://*.trycloudflare.com' link below!
echo Open that link on your smartphone to monitor and control your algos.
echo =====================================================================
echo.

cd /d "%~dp0"
"%~dp0cloudflared.exe" tunnel --url http://127.0.0.1:8080
pause
