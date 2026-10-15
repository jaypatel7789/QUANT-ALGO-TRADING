# ================================================================
# Launching AG2 Multi-Agent Brain Interactive Terminal
# ================================================================

Set-Location -Path $PSScriptRoot

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Launching AG2 Multi-Agent Brain Interactive Terminal" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

.\venv\Scripts\python cli.py
