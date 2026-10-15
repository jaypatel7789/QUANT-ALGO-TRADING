@echo off
:: Run MetaTrader 5 Windows Optimization as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator permissions...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================================
echo Running MetaTrader 5 Windows Optimizations...
echo ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_mt5_windows_optimizations.ps1"
pause
