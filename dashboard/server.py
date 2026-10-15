"""
FastAPI Command & Control Dashboard Server
Provides REST APIs and WebSocket real-time event streaming for the AG2 agent team,
OmniRoute gateway health, Graphify indexing, and Windows system terminal execution.
"""
import os
import sys
import json
import asyncio
import requests
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.security.auth import (
    require_auth,
    verify_ws_auth,
    SESSION_TOKEN,
    is_loopback_client
)
from core.config import (
    OMNIROUTE_BASE_URL,
    OMNIROUTE_HOST,
    OMNIROUTE_PORT,
    WORKSPACE_DIR,
    PRIMARY_MODEL,
    SECONDARY_MODEL,
    FALLBACK_MODEL
)
from core.orchestrator import MultiAgentOrchestrator
from core.executor import register_execution_listener
from core.skills.system_skill import SystemSkill

app = FastAPI(title="AG2 + OmniRoute Multi-Agent Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Orchestrator & Skills Singleton
orchestrator = MultiAgentOrchestrator()
sys_skill = SystemSkill(str(WORKSPACE_DIR))

# Active WebSocket connections
connected_websockets: List[WebSocket] = []

async def broadcast_event(event: dict):
    """Sends event data to all connected clients."""
    disconnected = []
    for ws in connected_websockets:
        try:
            await ws.send_text(json.dumps(event))
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in connected_websockets:
            connected_websockets.remove(ws)

import threading

# Wire Python event listeners to async WebSocket broadcaster
def handle_orchestrator_event(event: dict):
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        if loop and loop.is_running():
            if threading.current_thread() != threading.main_thread():
                asyncio.run_coroutine_threadsafe(broadcast_event(event), loop)
            else:
                asyncio.create_task(broadcast_event(event))
    except Exception:
        pass

def handle_execution_event(event: dict):
    handle_orchestrator_event({"source": "system_executor", **event})

orchestrator.subscribe(handle_orchestrator_event)
register_execution_listener(handle_execution_event)

# Request Models
class TaskRequest(BaseModel):
    prompt: str
    max_rounds: int = 20

class CommandRequest(BaseModel):
    command: str
    shell: str = "powershell"

class IndexRequest(BaseModel):
    path: str = ""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if not verify_ws_auth(websocket):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        # Send initial status packet with session token indicator
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "workspace": str(WORKSPACE_DIR),
            "primary_model": PRIMARY_MODEL,
            "omniroute_url": OMNIROUTE_BASE_URL
        }))
        while True:
            # Keep alive and listen for client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

@app.get("/api/status")
def get_system_status():
    """Returns telemetry, OmniRoute status, and agent team configuration."""
    omniroute_healthy = False
    try:
        # Check OmniRoute port
        base_host = f"http://{OMNIROUTE_HOST}:{OMNIROUTE_PORT}"
        r = requests.get(f"{base_host}/v1/models", timeout=1.5)
        omniroute_healthy = r.status_code == 200
    except Exception:
        omniroute_healthy = False

    telemetry = sys_skill.get_system_telemetry()

    return {
        "status": "online",
        "omniroute": {
            "url": OMNIROUTE_BASE_URL,
            "is_healthy": omniroute_healthy,
            "primary_model": PRIMARY_MODEL,
            "secondary_model": SECONDARY_MODEL,
            "fallback_model": FALLBACK_MODEL
        },
        "agents": [
            {"name": "Architect", "role": "Lead Architect", "rules": "Ponytail Philosophy", "status": "idle" if not orchestrator.is_running else "active"},
            {"name": "NemotronSuper", "role": "120B Super Reasoning", "skills": ["Deep Logic", "Strawberry/Math Reasoning", "Token Streaming"], "status": "idle" if not orchestrator.is_running else "active"},
            {"name": "Engineer", "role": "Senior Engineer", "skills": ["Graphify AST", "Code Generator"], "status": "idle" if not orchestrator.is_running else "active"},
            {"name": "QuantTrader", "role": "Algo & Backtesting", "skills": ["Backtesting.py", "CCXT", "Indicators"], "status": "idle" if not orchestrator.is_running else "active"},
            {"name": "FullStackDev", "role": "Web & Software", "skills": ["FastAPI", "Glassmorphic UI", "WebSockets"], "status": "idle" if not orchestrator.is_running else "active"},
            {"name": "Reviewer", "role": "QA & Security Auditor", "skills": ["Ponytail Bloat Audit"], "status": "idle" if not orchestrator.is_running else "active"},
            {"name": "SystemExecutor", "role": "OS & Terminal Controller", "capabilities": ["PowerShell", "Git", "Pip"], "status": "idle" if not orchestrator.is_running else "active"}
        ],
        "system": telemetry,
        "is_task_running": orchestrator.is_running,
        "active_task": orchestrator.active_task
    }

@app.post("/api/dispatch", dependencies=[Depends(require_auth)])
async def dispatch_task(request: TaskRequest):
    """Dispatches a task to the multi-agent team."""
    if orchestrator.is_running:
        return JSONResponse(status_code=400, content={"error": "A task is already actively running."})

    task = orchestrator.store.create_task(
        prompt=request.prompt,
        workspace_dir=str(orchestrator.workspace)
    )
    task_id = task["id"]

    # Native async task on the main event loop
    asyncio.create_task(orchestrator.dispatch_task_async(
        task_prompt=request.prompt,
        max_turns=request.max_rounds,
        task_id=task_id
    ))
    return {"status": "dispatched", "task_id": task_id, "prompt": request.prompt}

@app.post("/api/execute", dependencies=[Depends(require_auth)])
def execute_shell_command(request: CommandRequest):
    """Direct execution of a command via the sandboxed system executor."""
    result = orchestrator.team.executor.execute_command(request.command, shell_type=request.shell)
    return result

@app.post("/api/graphify/index", dependencies=[Depends(require_auth)])
def index_with_graphify(request: IndexRequest):
    """Triggers Graphify codebase AST indexing."""
    target = request.path if request.path.strip() else None
    result = orchestrator.team.graphify.index_codebase(target)
    return result

@app.get("/api/events")
def get_persisted_events(since: int = 0, limit: int = 100, task_id: Optional[str] = None):
    """
    Enables reconnecting clients to replay ordered events missed during disconnection.
    """
    return orchestrator.store.get_events(task_id=task_id, since_event_id=since, limit=limit)

@app.get("/api/tasks")
def list_tasks(limit: int = 50):
    """Returns durable list of tasks from SQLite with status and metrics."""
    persisted = orchestrator.store.list_tasks(limit=limit)
    if persisted:
        return persisted
    return orchestrator.history

@app.post("/api/tasks/{task_id}/cancel", dependencies=[Depends(require_auth)])
def cancel_task_endpoint(task_id: str):
    """Cancels a running task and kills its process tree."""
    success = orchestrator.cancel_task(task_id)
    return {"task_id": task_id, "cancelled": success}

@app.get("/api/history")
def get_task_history():
    """Returns past task and command executions from durable store."""
    tasks = orchestrator.store.list_tasks(limit=50)
    cmd_history = getattr(orchestrator.team.executor, "execution_history", [])[-30:]
    return {
        "task_history": tasks,
        "command_history": cmd_history
    }

@app.delete("/api/history", dependencies=[Depends(require_auth)])
def clear_history_endpoint():
    """Clears all durable task history and command execution logs."""
    orchestrator.clear_history()
    return {"status": "cleared", "message": "History cleared successfully."}

@app.get("/api/tasks/{task_id}/events")
def get_task_events(task_id: str, since: int = 0, limit: int = 250):
    """Returns chronological events for a specific task to replay or rehydrate dialogue."""
    events = orchestrator.store.get_events(task_id=task_id, since_event_id=since, limit=limit)
    return {"task_id": task_id, "events": events}


@app.get("/api/brain/status")
def get_brain_status():
    """Returns Meta-Brain inventory of models, skills, and repositories."""
    return orchestrator.brain.get_system_inventory()

@app.get("/api/workspace/files")
def get_workspace_files():
    """Lists files generated in the sandboxed workspace."""
    results = []
    ws = orchestrator.workspace
    if ws.exists():
        for item in sorted(ws.rglob("*")):
            if item.is_file():
                rel = str(item.relative_to(ws))
                results.append({
                    "name": item.name,
                    "rel_path": rel,
                    "size_bytes": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                    "is_code": item.suffix in [".py", ".js", ".html", ".css", ".json", ".md", ".txt", ".yml", ".yaml"]
                })
    return {"workspace": str(ws), "files": results}

@app.get("/api/workspace/file")
def read_workspace_file_content(path: str):
    """Safely reads a workspace file for the dashboard code previewer."""
    try:
        content = orchestrator.boundary.safe_read_file(path, max_chars=100000)
        return {"path": path, "content": content, "success": True}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e), "success": False})

@app.get("/api/brain/skills")
def get_brain_skills():
    """Returns catalog of engineering skills available to agents."""
    return orchestrator.brain.skill_hub.list_available_skills()

@app.get("/api/quant/overview")
def get_quant_overview():
    """Returns all candidates, research sources, master ledger rows, and research state."""
    research_dir = BASE_DIR / "research"
    candidates_file = research_dir / "CANDIDATES.csv"
    sources_file = research_dir / "SOURCES.csv"
    state_file = research_dir / "RESEARCH_STATE.md"
    excel_file = research_dir / "excel" / "backtest_master_ledger.xlsx"
    live_excel = research_dir / "excel" / "backtest_master_ledger_live.xlsx"
    if live_excel.exists() and (not excel_file.exists() or live_excel.stat().st_mtime > excel_file.stat().st_mtime):
        excel_file = live_excel

    candidates = []
    if candidates_file.exists():
        try:
            import csv
            with open(candidates_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                candidates = list(reader)
        except Exception:
            pass

    sources = []
    if sources_file.exists():
        try:
            import csv
            with open(sources_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                sources = list(reader)
        except Exception:
            pass

    state_text = ""
    if state_file.exists():
        try:
            state_text = state_file.read_text(encoding="utf-8")
        except Exception:
            pass

    ledger_rows = []
    if excel_file.exists():
        try:
            import pandas as pd
            df = pd.read_excel(excel_file)
            df = df.fillna("")
            ledger_rows = df.to_dict(orient="records")
        except Exception:
            pass

    return {
        "status": "online",
        "excel_path": str(excel_file),
        "candidates": candidates,
        "sources": sources,
        "research_state": state_text,
        "ledger_rows": ledger_rows,
        "summary": {
            "total_candidates": len(candidates),
            "total_sources": len(sources),
            "total_backtest_runs": len(ledger_rows)
        }
    }

@app.get("/api/quant/download-excel")
def download_excel_ledger():
    """Provides direct download for the master backtest Excel ledger."""
    excel_file = BASE_DIR / "research" / "excel" / "backtest_master_ledger.xlsx"
    live_excel = BASE_DIR / "research" / "excel" / "backtest_master_ledger_live.xlsx"
    if live_excel.exists() and (not excel_file.exists() or live_excel.stat().st_mtime > excel_file.stat().st_mtime):
        excel_file = live_excel

    if excel_file.exists():
        return FileResponse(
            excel_file,
            filename="backtest_master_ledger.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return JSONResponse(status_code=404, content={"error": "Excel ledger not found"})

@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Serve static dashboard frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_dashboard(response: Response):
    """Serves the dashboard and attaches session cookie for seamless local browser usage."""
    res = FileResponse(
        STATIC_DIR / "index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
    res.set_cookie(
        key="session_token",
        value=SESSION_TOKEN,
        httponly=True,
        samesite="lax"
    )
    return res

if __name__ == "__main__":
    import socket
    import webbrowser

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    import uvicorn
    port = int(os.getenv("AGENT_DASHBOARD_PORT") or os.getenv("DASHBOARD_PORT") or "8090")
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")

    # Gracefully check if port is already occupied by a running server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_port_in_use = False
    try:
        sock.bind((host, port))
        sock.close()
    except OSError:
        is_port_in_use = True

    if is_port_in_use:
        print(f"\n=======================================================")
        print(f"[+] Multi-Agent Dashboard is ALREADY running on http://{host}:{port}!")
        print(f"[*] Serving live agents and WebSocket mesh cleanly.")
        print(f"=======================================================\n")
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
        sys.exit(0)

    print(f"\n=======================================================")
    print(f"[+] Multi-Agent Command & Control Dashboard starting!")
    print(f"[*] Binding to: http://{host}:{port}")
    print(f"[*] Protected with local loopback & session authentication.")
    print(f"=======================================================\n")
    uvicorn.run("dashboard.server:app", host=host, port=port, reload=False)
