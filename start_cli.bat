@echo off
chcp 65001 >nul
title AG2 Multi-Agent Brain Terminal
cd /d "%~dp0"

echo ================================================================
echo  Launching AG2 Multi-Agent Brain Interactive Terminal...
echo ================================================================

.\venv\Scripts\python cli.py
pause
