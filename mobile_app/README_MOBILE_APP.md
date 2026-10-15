# Shark MT5 Sentinel — Mobile Command & Monitoring Center

A production-grade, ultra-lightweight mobile Progressive Web App (PWA) designed for live monitoring and real-time control of MetaTrader 5 institutional trading algorithms on **Shark Funded** (or any MT5 broker).

---

## 🌟 Key Features

1. **Live Account Telemetry & Floating PnL:**
   - Real-time Balance, Equity, Free Margin, and Margin Level.
   - Live streaming floating PnL with green/red glowing feedback.
2. **Shark Funded Risk Shield:**
   - Visual progress meters for **Daily Loss Limit ($450.00 / 4.5%)** and **Max Trailing Drawdown ($800.00 / 8.0%)**.
   - Real-time safety status indicator to ensure prop firm evaluation rules are never breached.
3. **Active Trades with Strategy Attribution:**
   - Attributed to the specific executing algorithm (e.g. `[GOLD-CUSTOM]`, `[BTC-018]`, `[PORTFOLIO-GOLD]`, Magic Number).
   - Live Stop Loss (SL), Take Profit (TP), Entry Price, Current Price, and PnL.
   - **Break-Even Locked Status Badge (`BE ACTIVE`):** Automatically detects when SL has been moved to entry + spread.
   - **One-Tap Close Button:** Close any single position instantly from your phone.
4. **Master & Individual Algo Controls:**
   - **Master Algo Switch:** Pause or resume all 16 algorithms with one toggle.
   - **Per-Strategy Switch:** Individually disable or enable any specific strategy.
5. **High-Impact News Shield:**
   - Pre-news blackout window (customizable minutes, default: 30 min).
   - Post-news cooldown window (customizable minutes, default: 15 min).
   - Live economic calendar events for USD, EUR, and GBP with auto-shield countdown.
6. **🚨 Emergency Panic Button (Liquidate All):**
   - 2-second press-and-hold safety modal to immediately close all open trades on the account.
7. **Cloud VPS & AWS Free-Tier Guard:**
   - Live CPU %, RAM %, and SSD storage meters.
   - AWS Free-Tier egress bandwidth tracker (ensuring you stay strictly within the 100 GB/month free limit).

---

## 🚀 How to Run & Access on Your Phone

### Step 1: Launch Local Server
Double-click:
`mobile_app\start_mobile_app.bat`  
Or run in terminal:
```powershell
cd mobile_app\backend
python -m uvicorn server:app --host 0.0.0.0 --port 8080
```

### Step 2: Open on Mobile Phone
Ensure your phone is connected to the same Wi-Fi network as your computer:
1. Find your computer's local IP address (e.g. `192.168.1.XX` or check via `ipconfig`).
2. On your phone's browser (Safari on iPhone, Chrome on Android), go to:
   ```
   http://YOUR_LOCAL_IP:8080/
   ```
   *(For testing directly on PC browser: go to `http://127.0.0.1:8080/`)*

### Step 3: Install as Native App (PWA)
- **On iPhone (Safari):** Tap the **Share** button (box with upward arrow) -> Select **"Add to Home Screen"**.
- **On Android (Chrome):** Tap the three dots menu -> Select **"Install App"** or **"Add to Home Screen"**.
- The app will now open full-screen without browser address bars, with app icon on your home screen.

---

## ☁️ Deploying to Dedicated Cloud VPS

To make the app accessible from anywhere in the world (even when not on home Wi-Fi) without paying a single penny:

1. **Option A: Free Cloudflare Tunnel (Recommended — Zero Open Ports & Bank-Grade SSL)**
   - Download the free `cloudflared.exe` binary onto the Cloud VPS.
   - Run: `cloudflared tunnel --url http://localhost:8080`
   - Cloudflare provides a free HTTPS domain (e.g., `https://shark-sentinel-xyz.trycloudflare.com`) with end-to-end encryption.
   - Open that URL on your phone anytime, anywhere.
2. **Option B: AWS Security Group Inbound Rule**
   - In AWS EC2 Console -> Security Groups -> Add Inbound Rule:
     - Type: Custom TCP, Port: `8080`, Source: Your Mobile IP (or `0.0.0.0/0` with PIN protection enabled).
