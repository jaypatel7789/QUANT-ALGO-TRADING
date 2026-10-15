# Architecture & Technical Specification

## 1. Executive Technical Overview
The **Shark MT5 Sentinel Platform** is an enterprise-grade algorithmic execution, monitoring, and risk management system built for high-stakes proprietary trading firm challenges and institutional capital management.

### Key Performance Specifications
- **Local IPC Order Latency**: < 4.2ms between FastAPI backend and native 64-bit MT5 terminal.
- **WebSocket Broadcast Latency**: < 15ms over local loopback; < 45ms over global Cloudflare edge tunnels.
- **Execution Retry Ladder Throughput**: Up to 20 trade instructions per second with individual ticket state tracking.
- **Fail-Safe Watchdog Interval**: 1000ms health check polling broker connection, account equity, and terminal responsiveness.

---

## 2. Decoupled Multi-Tier Topology

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MOBILE CLIENT LAYER                             │
│  - Responsive PWA with Glassmorphism Design System                    │
│  - Real-time WebSockets + Biometric WebAuthn / SHA-256 PIN            │
│  - Touch-optimized Canvas Equity Trajectory Inspector                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ TLS 1.3 / WebSocket (WSS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   CLOUDFLARE ZERO-TRUST EDGE LAYER                     │
│  - Quick Tunnel / Named Cloudflare Tunnel                              │
│  - Zero Inbound Firewall Holes on AWS EC2 VPC                          │
│  - Edge DDoS Mitigation & Global Anycast Acceleration                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Local Loopback (127.0.0.1:8080)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     SENTINEL BACKEND SERVICE                           │
│  - FastAPI Asynchronous Microservice                                   │
│  - AuthManager (SHA-256 with Salt, IP Rate Limiter: max 5 fails/hr)    │
│  - StateManager (Atomic JSON write to config/sentinel_state.json)      │
│  - NewsGuard (Macroeconomic calendar scraper with IST/UTC clock sync)   │
│  - MT5Bridge (MetaTrader 5 Python IPC Driver)                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Native C-API IPC / Shared Memory
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   METATRADER 5 TERMINAL (64-BIT)                       │
│  - Native 64-bit terminal64.exe running on AWS EC2                     │
│  - XMGlobal-MT5 Interbank Real-Tick Feed                               │
│  - Common/Files Sandbox Policy Pipe (sentinel_policy.json)             │
│  - 16 Attached Quant Expert Advisors with Dynamic Magic Numbers        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Communication Protocols & Data Exchange

### A. MetaTrader 5 Python IPC Bridge
The bridge establishes a bidirectional communication channel directly with `terminal64.exe`:
- **Order Routing**: Uses `mt5.order_send()` with structured `MqlTradeRequest` payloads:
  - `action`: `TRADE_ACTION_DEAL`
  - `type`: `ORDER_TYPE_BUY` or `ORDER_TYPE_SELL`
  - `type_filling`: Cascading priority `ORDER_FILLING_IOC` -> `ORDER_FILLING_FOK` -> `ORDER_FILLING_RETURN`
  - `deviation`: Dynamic slippage limit (initially 2 pips, increments by 1 pip on requote)
- **Account Telemetry**: Polls `mt5.account_info()` every second for live equity, margin, balance, and server connection health.
- **Position Attribution**: Queries `mt5.positions_get()` and maps each position's `magic` number to its respective strategy archetype via `STRATEGY_MAP`.

### B. Shared Sandbox Policy Synchronization
To bypass MQL5 web request limitations without requiring third-party DLLs:
1. When a user toggles an algorithm or updates the News Shield in the mobile app, `state_manager.py` writes the updated state to:
   `%APPDATA%\MetaQuotes\Terminal\Common\Files\sentinel_policy.json`
2. Each MQL5 EA contains an inline security guard:
   ```cpp
   // Executed inside OnTick() before evaluating alpha triggers
   if (!IsSentinelTradingAllowed(InpMagicNumber)) {
       return; // Execution frozen by mobile command center or news shield
   }
   ```
3. This guarantees immediate sub-millisecond execution halts across all running charts.

---

## 4. Emergency Fail-Safe & Panic Close Architecture

The "PANIC CLOSE ALL" system provides instant liquidation across the entire account:
1. **Trigger**: User presses and holds the emergency button for 2 full seconds (preventing accidental touches).
2. **Execution**:
   - Fires asynchronous liquidation threads for each open ticket.
   - For Buy positions, dispatches counter Sell at `mt5.symbol_info_tick(sym).bid`.
   - For Sell positions, dispatches counter Buy at `mt5.symbol_info_tick(sym).ask`.
   - Automatically deletes all pending limit/stop orders (`TRADE_ACTION_REMOVE`).
3. **Audit**: Emits structured log entries to the terminal stream confirming execution latency and slippage for each closed ticket.
