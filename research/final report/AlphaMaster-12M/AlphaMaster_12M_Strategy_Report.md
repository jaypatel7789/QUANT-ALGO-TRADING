# Strategy #18: AlphaMaster-12M (Institutional 4-Engine Multi-Asset Portfolio on Gold Engine)

## Executive Summary
- **Strategy ID:** AlphaMaster-12M
- **Asset / Symbol:** GOLD.i# (Gold Spot USD)
- **Timeframe:** H1 (1-Hour)
- **Period Tested:** 2025.09.28 – 2026.09.28 (1 Full Year)
- **Initial Deposit:** ,000.00
- **Final Net Profit:** +.22 (+7.64%)
- **Profit Factor:** 1.47
- **Total Closed Trades:** 95
- **Wins / Losses:** 45 Wins / 50 Losses
- **Win Rate:** 47.37%
- **Max Balance Drawdown:** 5.06% (.39)
- **Max Equity Drawdown:** 5.81% (.17)
- **Gross Profit:** ,376.42
- **Gross Loss:** -,612.20
- **Expected Payoff:** .04

---

## Portfolio Architecture & Core Engines
An institutional 4-engine portfolio designed to maintain high Sharpe and smooth calendar performance:
1. **Engine 1: XAU-024 London ORB Expansion (Magic 9991212)**
   - London opening range breakout with Asian cap filter (2.5x ATR max), targeting 2.5x ATR with 2.5x ATR Stop Loss, session close 16:00 UTC.
2. **Engine 2: XAU-030 Connors Mean Reversion**
   - RSI(3) oversold mean-reversion snapback (RSI < 14), filtered by low ADX (ADX < 24), taking quick profit at 0.45x ATR with 2.0x ATR SL.
3. **Engine 3: XAU-026 London Breakout Retest**
   - Executes on retest of Asian session high during London open with 2.5x ATR TP and 1.5x ATR SL.
4. **Engine 4: BTC-003 Squeeze Momentum (BTC Mode)**
   - Deploys Bollinger Band / Keltner Channel squeeze expansion on Bitcoin when attached to BTC pairs.

---

## Tester Input Configuration
`ini
[Common]
Login=1000000000
Server=XMGlobal-MT5 6

[Tester]
Expert=multi agent all btc strategy\AlphaMaster_12Month_Portfolio.ex5
Symbol=GOLD.i#
Period=H1
Deposit=10000
Currency=USD
Leverage=100
Model=1
ExecutionMode=0
Optimization=0
FromDate=2025.09.28
ToDate=2026.09.28
Report=Reports\mt5_alphamaster_gold_report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpTimeframe=0
InpFixedLot=0.0
InpRiskPercent=1.0
InpMaxDailyLossPct=4.5
InpMaxTotalDrawdown=8.0
InpMagicNumber=9991212
InpDebugMode=false
InpEnableXAU024=true
InpXAU024_AsianCap=2.5
InpXAU024_TPMult=2.5
InpXAU024_SLMult=2.5
InpXAU024_StartHour=7
InpXAU024_EndHour=11
InpXAU024_CloseHour=16
InpEnableXAU030=true
InpXAU030_RSILimit=14.0
InpXAU030_MaxADX=24.0
InpXAU030_TPMult=0.45
InpXAU030_SLMult=2.0
InpXAU030_StartHour=8
InpXAU030_EndHour=18
InpEnableXAU026=true
InpXAU026_RetestZone=0.5
InpXAU026_TPMult=2.5
InpXAU026_SLMult=1.5
InpEnableBTC003=true
InpBTC003_BBMult=2.0
InpBTC003_KCMult=1.5
InpBTC003_SlopeMult=1.001
InpBTC003_TPMult=2.0
InpBTC003_SLMult=2.5
`

---

## Month-by-Month Financial Ledger

| Month | Trades | Wins | Losses | Win Rate (%) | Net Profit / Loss (USD) |
|---|:---:|:---:|:---:|:---:|:---:|
| **2025.09** | 1 | 1 | 0 | 100.00% | +.26 |
| **2025.10** | 11 | 7 | 4 | 63.64% | +.29 |
| **2025.11** | 9 | 4 | 5 | 44.44% | +.02 |
| **2025.12** | 12 | 7 | 5 | 58.33% | +.40 |
| **2026.01** | 6 | 0 | 6 | 0.00% | -.42 |
| **2026.02** | 10 | 6 | 4 | 60.00% | +.85 |
| **2026.03** | 6 | 1 | 5 | 16.67% | -.27 |
| **2026.04** | 10 | 3 | 7 | 30.00% | +.19 |
| **2026.05** | 5 | 3 | 2 | 60.00% | +.19 |
| **2026.06** | 6 | 4 | 2 | 66.67% | +.41 |
| **2026.07** | 4 | 2 | 2 | 50.00% | +.61 |
| **2026.08** | 9 | 5 | 4 | 55.56% | +.96 |
| **2026.09** | 6 | 2 | 4 | 33.33% | -.27 |
| **TOTAL** | **95** | **45** | **50** | **47.37%** | **+.22** |
