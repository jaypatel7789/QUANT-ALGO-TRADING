<#
.SYNOPSIS
    Comprehensive Windows Optimization Script for MetaTrader 5 (Algo-Trading, 24/7 Stability, Low Latency)
.DESCRIPTION
    Applies critical Windows settings:
    - High Performance power plan without sleep/hibernation
    - Windows Defender exclusions for MT5 binaries and data directories
    - Windows Firewall inbound/outbound rules for MT5 terminal and tester
    - TCP network latency optimizations
#>

# Auto-elevate to Administrator if needed
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Yellow
    Start-Process powershell.exe -ArgumentList ("-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"") -Verb RunAs
    exit
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  MetaTrader 5 Windows Optimization - Jay Patel          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Power & Sleep Configuration (24/7 Trading & Backtesting)
Write-Host "`n[1/5] Configuring Power & Sleep Policies..." -ForegroundColor Green
try {
    # Check or create High Performance scheme
    $highPerfGuid = "dd0a951e-e546-4159-abf5-a3b5f0a792f5"
    powercfg /setactive $highPerfGuid 2>$null
    if ($LASTEXITCODE -ne 0) {
        $out = powercfg /duplicatescheme 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
        if ($out -match "([a-f0-9\-]{36})") {
            $highPerfGuid = $matches[1]
            powercfg /setactive $highPerfGuid
        }
    }
    # Disable Sleep, Hibernation, and Disk Idle on AC
    powercfg /change standby-timeout-ac 0
    powercfg /change hibernate-timeout-ac 0
    powercfg /change disk-timeout-ac 0
    # Set USB selective suspend disabled
    powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba4d5a0 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    powercfg /SETACTIVE SCHEME_CURRENT
    Write-Host "  -> Power scheme set to High Performance (Sleep & Hibernation DISABLED on AC)." -ForegroundColor White
} catch {
    Write-Host "  -> Warning configuring power scheme: $_" -ForegroundColor Yellow
}

# 2. Windows Defender Antivirus Exclusions
Write-Host "`n[2/5] Configuring Windows Defender Exclusions..." -ForegroundColor Green
$mt5Paths = @(
    "C:\Program Files\MetaTrader 5",
    "C:\Users\Jay Patel\AppData\Roaming\MetaQuotes",
    "F:\multi agent"
)
foreach ($path in $mt5Paths) {
    if (Test-Path $path) {
        Add-MpPreference -ExclusionPath $path -ErrorAction SilentlyContinue
        Write-Host "  -> Added Folder Exclusion: $path" -ForegroundColor White
    }
}

$mt5Processes = @(
    "terminal64.exe",
    "metatester64.exe",
    "metaeditor64.exe"
)
foreach ($proc in $mt5Processes) {
    Add-MpPreference -ExclusionProcess $proc -ErrorAction SilentlyContinue
    Write-Host "  -> Added Process Exclusion: $proc" -ForegroundColor White
}

# 3. Windows Firewall Rules for MetaTrader 5
Write-Host "`n[3/5] Configuring Windows Firewall Rules..." -ForegroundColor Green
$terminalExe = "C:\Program Files\MetaTrader 5\terminal64.exe"
$testerExe = "C:\Program Files\MetaTrader 5\metatester64.exe"

if (Test-Path $terminalExe) {
    Remove-NetFirewallRule -DisplayName "MetaTrader 5 Terminal Inbound" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "MetaTrader 5 Terminal Outbound" -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "MetaTrader 5 Terminal Inbound" -Direction Inbound -Program $terminalExe -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null
    New-NetFirewallRule -DisplayName "MetaTrader 5 Terminal Outbound" -Direction Outbound -Program $terminalExe -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null
    Write-Host "  -> Allowed Terminal64 through Windows Firewall (Inbound & Outbound)." -ForegroundColor White
}

if (Test-Path $testerExe) {
    Remove-NetFirewallRule -DisplayName "MetaTrader 5 Tester Inbound" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "MetaTrader 5 Tester Outbound" -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "MetaTrader 5 Tester Inbound" -Direction Inbound -Program $testerExe -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null
    New-NetFirewallRule -DisplayName "MetaTrader 5 Tester Outbound" -Direction Outbound -Program $testerExe -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null
    Write-Host "  -> Allowed MetaTester64 through Windows Firewall (Inbound & Outbound)." -ForegroundColor White
}

# 4. Network and Latency Tuning
Write-Host "`n[4/5] Tuning Network Stack for Low Latency..." -ForegroundColor Green
try {
    netsh int tcp set global autotuninglevel=normal 2>$null | Out-Null
    netsh int tcp set global rss=enabled 2>$null | Out-Null
    Write-Host "  -> TCP Autotuning & Receive Side Scaling (RSS) verified." -ForegroundColor White
} catch {
    Write-Host "  -> Network tuning notice: $_" -ForegroundColor Yellow
}

# 5. Elevated Process Priority for running terminal64 instances
Write-Host "`n[5/5] Checking Running MetaTrader Instances..." -ForegroundColor Green
$procs = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($procs) {
    foreach ($p in $procs) {
        $p.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::AboveNormal
        Write-Host "  -> Elevated terminal64 (PID $($p.Id)) priority to AboveNormal." -ForegroundColor White
    }
} else {
    Write-Host "  -> No terminal64 process currently running." -ForegroundColor White
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  Optimization Complete! Windows is configured for MT5.   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Start-Sleep -Seconds 3
