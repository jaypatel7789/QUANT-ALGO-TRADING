# ================================================================
# Starting AG2 Multi-Agent Platform + OmniRoute Gateway
# ================================================================

Set-Location -Path $PSScriptRoot

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Starting AG2 Multi-Agent Platform + OmniRoute Gateway" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

# 1. Check & Start OmniRoute Gateway (:20128)
$omniHealthy = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:20128/v1/models" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($res) { $omniHealthy = $true }
} catch { $omniHealthy = $false }

if ($omniHealthy) {
    Write-Host "[1/2] OmniRoute Gateway is ALREADY running and healthy on http://127.0.0.1:20128" -ForegroundColor Green
} else {
    Write-Host "[1/2] Launching OmniRoute Gateway on http://127.0.0.1:20128..." -ForegroundColor Yellow
    Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList "-NoExit", "-Command", "node gateway\start_gateway.js"
    Start-Sleep -Seconds 2
}

# 2. Check & Start Multi-Agent Dashboard (:8090)
$dashHealthy = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:8090/api/status" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($res -and $res.status -eq "online") { $dashHealthy = $true }
} catch { $dashHealthy = $false }

if ($dashHealthy) {
    Write-Host "[2/2] Multi-Agent Dashboard is ALREADY running and healthy on http://127.0.0.1:8090" -ForegroundColor Green
} else {
    Write-Host "[2/2] Launching Multi-Agent Dashboard on http://127.0.0.1:8090..." -ForegroundColor Yellow
    Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\python dashboard\server.py"
    Start-Sleep -Seconds 2
}

Write-Host "`nOpening Dashboard in Browser..." -ForegroundColor Cyan
Start-Process "http://localhost:8090"

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host " System is Active & Connected!" -ForegroundColor Green
Write-Host " Dashboard: http://localhost:8090" -ForegroundColor Cyan
Write-Host " OmniRoute: http://localhost:20128" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Green

