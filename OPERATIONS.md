# Operations & System Management Guide

This document outlines standard operating procedures for the **Autonomous Multi-Agent Engineering Grid**: startup, graceful shutdown, restart recovery, configuration, and troubleshooting.

---

## 1. System Requirements & Architecture Overview

- **OS**: Windows 10/11 (x64)
- **Shell**: Windows PowerShell 5.1 or PowerShell 7.x
- **Python**: Python 3.11.x (with active virtual environment at `.\venv`)
- **Node.js**: Node.js v18+ (for OmniRoute AI Gateway)
- **Default Endpoints**:
  - Multi-Agent Web Dashboard: `http://127.0.0.1:8090`
  - OmniRoute AI Gateway: `http://127.0.0.1:20128` (OpenAI API: `/v1`)

---

## 2. Startup Procedures

### One-Click Launch (Recommended)

From the project root `F:\multi agent`:

```powershell
# Using PowerShell launcher:
.\start_all.ps1

# OR using Windows Batch file:
.\start_all.bat
```

This launches the OmniRoute Gateway in a dedicated background window, starts the FastAPI Dashboard Server on loopback `127.0.0.1:8090`, and opens your default browser.

### Manual Step-by-Step Launch

If running components individually in separate terminal sessions:

```powershell
# Terminal 1: Launch OmniRoute AI Gateway
node gateway/start_gateway.js

# Terminal 2: Launch Command & Control Dashboard
.\venv\Scripts\python dashboard/server.py
```

### Verification Check

Run the comprehensive test suite to confirm operational health:

```powershell
# Run all 33 unit tests
.\venv\Scripts\python -m unittest discover tests -v

# Run the 3 end-to-end benchmarks and 5 resilience probes
.\venv\Scripts\python benchmarks/run_benchmarks.py
```

---

## 3. Graceful Shutdown Procedures

### Stopping the Dashboard & Agents

In the terminal running `dashboard/server.py`, press `Ctrl + C`.  
The server will:
1. Signal running tasks to pause or cancel.
2. Terminate any active subprocess trees in Windows.
3. Close SQLite connections cleanly in WAL mode.

### Stopping the OmniRoute Gateway

In the terminal running `gateway/start_gateway.js`, press `Ctrl + C`.

### Force Kill Stuck Process Trees (Emergency)

If a background task or script hangs on Windows:

```powershell
# Kill dangling python worker processes on port 8090
Get-NetTCPConnection -LocalPort 8090 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Kill dangling node gateway on port 20128
Get-NetTCPConnection -LocalPort 20128 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

---

## 4. Restart Recovery & Crash Handling

The platform includes automated crash recovery:

1. **State Reconciliation**: On startup, `MultiAgentOrchestrator` scans the SQLite database `tasks.sqlite3` for any tasks left in `running` or `reviewing` states.
2. **Bounded Retries**:
   - If `attempt_count < max_attempts`, the task status is automatically reset to `queued` with an audit event explaining the recovery reason.
   - If `attempt_count >= max_attempts`, the task status is set to `failed` to prevent infinite loops.
3. **Idempotency Protection**: Re-dispatching an interrupted task uses its SHA256 idempotency key, preventing duplicate operations or double-spend of tokens.

---

## 5. Configuration Reference

All settings are configured in `.env` in the project root:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DASHBOARD_HOST` | `127.0.0.1` | Binding interface for dashboard. Set to `127.0.0.1` for loopback security. |
| `AGENT_DASHBOARD_PORT` | `8090` | Port for the Web Dashboard. |
| `OMNIROUTE_BASE_URL` | `http://localhost:20128/v1` | URL of the local AI Gateway. |
| `PRIMARY_MODEL` | `gpt-5.6-luna` | Primary code synthesis model. |
| `SECONDARY_MODEL` | `grok-4.7` | Fast logic and reviewing model. |
| `FALLBACK_MODEL` | `nvidia/nemotron-3-super-120b-a12b:free` | Free deep reasoning and tool-compatible fallback. |
| `WORKSPACE_DIR` | `F:\multi agent\workspace` | Sandboxed output directory for generated code and logs. |
| `EXECUTION_TIMEOUT` | `120` | Subprocess execution timeout in seconds. |
| `AGENT_API_TOKEN` | *Auto-generated* | Optional fixed authentication token for API access. |

---

## 6. Troubleshooting Common Issues

### Issue 1: "UnicodeEncodeError: 'charmap' codec can't encode character"
- **Cause**: Windows PowerShell default cp1252 codepage cannot print emojis or unicode symbols returned by LLMs.
- **Fix**: The system automatically sets `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1` in `ExecutionBoundary`. For manual CLI scripts, include:
  ```python
  import sys
  sys.stdout.reconfigure(encoding='utf-8')
  ```

### Issue 2: "sqlite3.OperationalError: database is locked"
- **Cause**: Attempting to open concurrent nested write connections in SQLite.
- **Fix**: SQLite is configured in WAL mode (`PRAGMA journal_mode=WAL;`). In code, pass existing connection handles (`conn=conn`) to event logging functions rather than opening nested connections.

### Issue 3: "HTTP 429: Rate limit exceeded on OpenRouter"
- **Cause**: The free tier of Nemotron 120B has concurrency and requests-per-minute limits.
- **Fix**: The built-in circuit breaker in `core/models/model_registry.py` detects rate limits, temporarily avoids the endpoint for 60 seconds, and seamlessly routes requests to secondary models (`grok-4.7` or `gpt-5.6-luna`).

### Issue 4: "Path traversal access denied"
- **Cause**: An agent or script attempted to read or write a file outside the sandboxed `workspace/` folder.
- **Fix**: All file operations must specify paths relative to `workspace/` or point to approved directories.
