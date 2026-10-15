import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from state_manager import state_mgr, logger
from auth_manager import AuthManager, require_auth
from mt5_bridge import MT5Bridge
from news_guard import NewsGuard
from system_monitor import SystemMonitor
from logs_provider import logs_provider

app = FastAPI(title="Shark MT5 Sentinel Command Center", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
mt5_bridge = MT5Bridge()
news_guard = NewsGuard(mt5_bridge=mt5_bridge)
system_mon = SystemMonitor()

# Request Models
class LoginRequest(BaseModel):
    pin: str

class ChangePinRequest(BaseModel):
    old_pin: str
    new_pin: str

class AlgoToggleRequest(BaseModel):
    magic: int
    enabled: bool

class MasterToggleRequest(BaseModel):
    enabled: bool

class CloseSingleRequest(BaseModel):
    ticket: int

class NewsSettingsRequest(BaseModel):
    enabled: bool
    block_before_min: int
    block_after_min: int

class NewsToggleRequest(BaseModel):
    enabled: bool

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================
@app.post("/api/auth/login")
def login(req: LoginRequest, request: Request):
    ip = AuthManager.get_client_ip(request)
    return AuthManager.authenticate_pin(req.pin, ip)

@app.post("/api/auth/change-pin")
def change_pin(req: ChangePinRequest, token: str = Depends(require_auth)):
    if len(req.new_pin.strip()) != 4 or not req.new_pin.strip().isdigit():
        raise HTTPException(status_code=400, detail="New PIN must be exactly 4 digits.")
    if state_mgr.update_pin(req.old_pin, req.new_pin):
        return {"status": "SUCCESS", "message": "Security PIN updated successfully."}
    raise HTTPException(status_code=401, detail="Old Security PIN is incorrect.")

# ==========================================
# PUBLIC READ TELEMETRY (For Dashboard Readouts)
# ==========================================
@app.get("/api/account")
def get_account():
    return mt5_bridge.get_account_summary()

@app.get("/api/positions")
def get_positions():
    return mt5_bridge.get_open_positions()

@app.get("/api/algos")
def get_algos():
    return mt5_bridge.get_algo_status()

@app.get("/api/chart")
def get_chart():
    return mt5_bridge.get_equity_curve()

@app.get("/api/news")
def get_news():
    return news_guard.check_shield_status()

@app.get("/api/system")
def get_system():
    return system_mon.get_telemetry()

@app.get("/api/history")
def get_history():
    return mt5_bridge.get_trade_history()

@app.get("/api/logs")
def get_logs(category: str = "all", limit: int = 150, q: str = ""):
    return logs_provider.get_logs(category=category, limit=min(limit, 500), search=q)

# ==========================================
# PROTECTED MUTATION ENDPOINTS (Requires Session Token)
# ==========================================
@app.post("/api/algos/toggle")
def toggle_algo(req: AlgoToggleRequest, token: str = Depends(require_auth)):
    return mt5_bridge.toggle_algo(req.magic, req.enabled)

@app.post("/api/algos/master-toggle")
def toggle_master(req: MasterToggleRequest, token: str = Depends(require_auth)):
    return mt5_bridge.set_master_trading(req.enabled)

@app.post("/api/trades/close-all")
def close_all(token: str = Depends(require_auth)):
    return mt5_bridge.close_all_positions()

@app.post("/api/trades/close-single")
def close_single(req: CloseSingleRequest, token: str = Depends(require_auth)):
    return mt5_bridge.close_single_position(req.ticket)

@app.post("/api/news/settings")
def update_news_settings(req: NewsSettingsRequest):
    logger.info(f"Policy: News Shield updated via API: Enabled={req.enabled}, Before={req.block_before_min}m, After={req.block_after_min}m")
    return news_guard.update_settings(req.enabled, req.block_before_min, req.block_after_min)

@app.post("/api/news/toggle")
def toggle_news_shield(req: NewsToggleRequest):
    settings = state_mgr.get_news_settings()
    logger.info(f"Policy: News Shield toggled via API to: {'ENABLED' if req.enabled else 'DISABLED'}")
    return news_guard.update_settings(
        req.enabled,
        settings.get("block_before_min", 30),
        settings.get("block_after_min", 15)
    )

# ==========================================
# WEBSOCKET MANAGER FOR REAL-TIME PUSH
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            payload = {
                "account": mt5_bridge.get_account_summary(),
                "positions": mt5_bridge.get_open_positions(),
                "algos": mt5_bridge.get_algo_status(),
                "news": news_guard.check_shield_status(),
                "system": system_mon.get_telemetry(),
                "chart": mt5_bridge.get_equity_curve()
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Mount frontend PWA
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Production Shark MT5 Sentinel on http://0.0.0.0:8080 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=False, log_level="info")
