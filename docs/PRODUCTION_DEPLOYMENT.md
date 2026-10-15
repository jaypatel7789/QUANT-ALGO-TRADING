# Cloud VPS 24/7 Production Deployment Guide

## Overview
This document outlines the exact deployment workflow for running the **Shark MT5 Sentinel** on a dedicated cloud virtual private server (AWS EC2 Windows Server 2022).

---

## 1. Prerequisites
- **AWS Account** with permissions to launch EC2 instances.
- **Recommended Instance Size**: `t3.medium` (2 vCPU, 4GB RAM) or `c6i.large`.
- **Operating System**: Windows Server 2022 Base (64-bit).
- **Trading Platform**: MetaTrader 5 Build 4400+ installed from broker (e.g. XMGlobal, SharkFunded).
- **Python**: Python 3.10 or 3.11 with `pip`.

---

## 2. Windows Environment Initialization

1. Connect to the EC2 instance via Remote Desktop Protocol (RDP).
2. Open PowerShell as Administrator and run the system optimization script:
   ```powershell
   # Disables unnecessary Windows background bloat and sets high performance power plan
   powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
   ```
3. Install Python 3.10/3.11 (ensure "Add Python to PATH" is checked).
4. Install required libraries:
   ```cmd
   pip install fastapi uvicorn websockets MetaTrader5 pydantic requests
   ```

---

## 3. Starting the Sentinel Service

### Automated 1-Click Launch
Double-click `cloud_deploy\run_sentinel_cloud_service.bat` or run:

```cmd
cd C:\QUANT-ALGO-TRADING
cloud_deploy\run_sentinel_cloud_service.bat
```

The script will:
1. Verify Python and MetaTrader 5 paths.
2. Initialize Cloudflare zero-trust quick tunnel.
3. Start the FastAPI Sentinel daemon on port `8080`.
4. Output the ephemeral secure HTTPS tunnel URL for mobile access (e.g. `https://your-unique-subdomain.trycloudflare.com`).

---

## 4. Configuring 24/7 Windows Task Scheduler Autostart

To ensure Sentinel automatically reboots if the EC2 instance restarts:
1. Open PowerShell as Administrator.
2. Register the scheduled task:
   ```powershell
   $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c C:\deploy\run_sentinel_cloud_service.bat"
   $trigger = New-ScheduledTaskTrigger -AtStartup
   $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
   Register-ScheduledTask -TaskName "SharkSentinel247" -Action $action -Trigger $trigger -Principal $principal
   ```
3. Sentinel will now launch seamlessly on system boot without requiring interactive RDP login.
