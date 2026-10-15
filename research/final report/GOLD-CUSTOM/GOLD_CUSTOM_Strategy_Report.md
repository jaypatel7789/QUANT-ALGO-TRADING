# Strategy #12: GOLD-CUSTOM (Institutional London VWAP + ADX Regime Flow)

## Executive Summary
- **Strategy ID:** GOLD-CUSTOM
- **Asset / Symbol:** GOLD.i# (Gold Spot USD)
- **Timeframe:** H1 (1-Hour)
- **Period Tested:** 2025.09.28 – 2026.09.28 (1 Full Year)
- **Initial Deposit:** ,000.00
- **Final Net Profit:** +,145.75 (+11.46%)
- **Profit Factor:** 2.19
- **Total Closed Trades:** 62
- **Wins / Losses:** 40 Wins / 22 Losses
- **Win Rate:** 64.52%
- **Max Balance Drawdown:** 2.10% (.67)
- **Max Equity Drawdown:** 3.49% (.16)
- **Gross Profit:** ,112.02
- **Gross Loss:** -.27
- **Expected Payoff:** .48

---

## Strategy Logic & Archetype
- **Archetype:** Institutional Session VWAP + Opening Range + ADX Trend Strength Filter
- **Session Architecture:** Anchors an institutional Volume-Weighted Average Price (VWAP) to the start of the London trading session (08:00 UTC). Monitors London opening flow (08:00 – 11:00 UTC) with an ADX(14) trend strength filter (threshold >= 22.0) and a 50 EMA Macro Trend baseline. When price closes above VWAP and confirms institutional volume accumulation, an institutional Long is triggered.
- **Risk Management:** 1.0% dynamic risk sizing, 2.5x ATR dynamic Stop Loss, 3.0x ATR Take Profit (1:1.2 R:R), with a hard session close at 18:00 UTC.

---

## Tester Input Configuration
`ini
[Common]
Login=1000000000
Server=XMGlobal-MT5 6

[Tester]
Expert=multi agent all btc strategy\GOLD_CUSTOM_INSTITUTIONAL_ALPHA.ex5
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
Report=Reports\mt5_gold_custom_alpha_h1_report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpMacroPeriod=50
InpADXPeriod=14
InpADXThreshold=22.0
InpStartHour=8
InpEndHour=11
InpSessionCloseHour=18
InpMagicNumber=24024
InpATRStopMult=2.5
InpTPMult=3.0
InpUseBreakEven=false
InpBETriggerATR=1.5
InpFixedLot=0.0
InpRiskPercent=1.0
`

---

## Month-by-Month Financial Ledger

| Month | Trades | Wins | Losses | Win Rate (%) | Net Profit / Loss (USD) |
|---|:---:|:---:|:---:|:---:|:---:|
| **2025.09** | 2 | 1 | 1 | 50.00% | -.53 |
| **2025.10** | 8 | 5 | 3 | 62.50% | +.09 |
| **2025.11** | 6 | 2 | 4 | 33.33% | +.37 |
| **2025.12** | 5 | 3 | 2 | 60.00% | +.93 |
| **2026.01** | 8 | 7 | 1 | 87.50% | +.06 |
| **2026.02** | 3 | 1 | 2 | 33.33% | -.56 |
| **2026.03** | 3 | 1 | 2 | 33.33% | -.78 |
| **2026.04** | 5 | 4 | 1 | 80.00% | +.22 |
| **2026.05** | 6 | 4 | 2 | 66.67% | +.56 |
| **2026.06** | 3 | 2 | 1 | 66.67% | +.78 |
| **2026.07** | 1 | 1 | 0 | 100.00% | +.98 |
| **2026.08** | 8 | 6 | 2 | 75.00% | +.40 |
| **2026.09** | 4 | 3 | 1 | 75.00% | +.23 |
| **TOTAL** | **62** | **40** | **22** | **64.52%** | **+,145.75** |
