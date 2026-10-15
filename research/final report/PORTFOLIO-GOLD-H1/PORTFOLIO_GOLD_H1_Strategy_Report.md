# Strategy #17: PORTFOLIO-GOLD-H1 (Dual-Engine Institutional Gold Portfolio)

## Executive Summary
- **Strategy ID:** PORTFOLIO-GOLD-H1
- **Asset / Symbol:** GOLD.i# (Gold Spot USD)
- **Timeframe:** H1 (1-Hour)
- **Period Tested:** 2025.09.28 – 2026.09.28 (1 Full Year)
- **Initial Deposit:** ,000.00
- **Final Net Profit:** +,783.52 (+37.84%)
- **Profit Factor:** 1.72
- **Total Closed Trades:** 144
- **Wins / Losses:** 77 Wins / 67 Losses
- **Win Rate:** 53.47%
- **Max Balance Drawdown:** 5.58% (.59)
- **Max Equity Drawdown:** 6.97% (,030.75)
- **Gross Profit:** ,012.36
- **Gross Loss:** -,228.84
- **Expected Payoff:** .27

---

## Portfolio Composition & Core Architecture
Combines two complementary institutional London session engines operating in parallel under a unified risk allocation framework on Gold (GOLD.i#) 1-Hour chart:
1. **Engine 1: GOLD-024 London Opening Range Breakout (ORB) (Magic 14024)**
   - Captures the 07:00 UTC London opening benchmark high; executes Long during the London institutional flow window (08:00 – 11:59 UTC) when price closes above the 07:00 UTC high and holds above the 50 EMA Macro Trend.
   - Sizing: 1.0% dynamic risk, 1.5x ATR Stop Loss, 2.5x ATR Take Profit.
2. **Engine 2: GOLD-CUSTOM Institutional London Session VWAP + ADX Engine (Magic 24024)**
   - Anchors VWAP to the 08:00 UTC London open; executes Long when price closes above VWAP and ADX(14) >= 22.0 confirms institutional trend strength.
   - Sizing: 1.0% dynamic risk, 2.5x ATR Stop Loss, 3.0x ATR Take Profit, with hard session close at 18:00 UTC.

---

## Tester Input Configuration
`ini
[Common]
Login=1000000000
Server=XMGlobal-MT5 6

[Tester]
Expert=multi agent all btc strategy\GOLD_COMBINED_PORTFOLIO_H1.ex5
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
Report=Reports\mt5_gold_combined_report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpE1_MagicNumber=14024
InpE1_MacroPeriod=50
InpE1_ATRStopMult=1.5
InpE1_TPMult=2.5
InpE1_UseBreakEven=false
InpE1_BETriggerATR=1.5
InpE1_RiskPercent=1.0
InpE2_MagicNumber=24024
InpE2_MacroPeriod=50
InpE2_ADXPeriod=14
InpE2_ADXThreshold=22.0
InpE2_StartHour=8
InpE2_EndHour=11
InpE2_SessionCloseHour=18
InpE2_ATRStopMult=2.5
InpE2_TPMult=3.0
InpE2_UseBreakEven=false
InpE2_BETriggerATR=1.5
InpE2_RiskPercent=1.0
`

---

## Month-by-Month Financial Ledger

| Month | Trades | Wins | Losses | Win Rate (%) | Net Profit / Loss (USD) |
|---|:---:|:---:|:---:|:---:|:---:|
| **2025.09** | 4 | 2 | 2 | 50.00% | +.38 |
| **2025.10** | 17 | 9 | 8 | 52.94% | +.36 |
| **2025.11** | 15 | 6 | 9 | 40.00% | +.28 |
| **2025.12** | 11 | 7 | 4 | 63.64% | +.23 |
| **2026.01** | 18 | 15 | 3 | 83.33% | +,438.69 |
| **2026.02** | 9 | 3 | 6 | 33.33% | -.54 |
| **2026.03** | 7 | 2 | 5 | 28.57% | -.24 |
| **2026.04** | 10 | 6 | 4 | 60.00% | +.71 |
| **2026.05** | 12 | 7 | 5 | 58.33% | +.81 |
| **2026.06** | 7 | 3 | 4 | 42.86% | -.10 |
| **2026.07** | 5 | 4 | 1 | 80.00% | +.26 |
| **2026.08** | 19 | 10 | 9 | 52.63% | +.57 |
| **2026.09** | 10 | 3 | 7 | 30.00% | -.89 |
| **TOTAL** | **144** | **77** | **67** | **53.47%** | **+,783.52** |
