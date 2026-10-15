# Strategy #13: BTC-CUSTOM (Institutional Volatility Ratio + ADX Trend Strength)

## Executive Summary
- **Strategy ID:** BTC-CUSTOM
- **Asset / Symbol:** BTCUSD# (Bitcoin Spot USD)
- **Timeframe:** H1 (1-Hour)
- **Period Tested:** 2025.09.28 – 2026.09.28 (1 Full Year)
- **Initial Deposit:** ,000.00
- **Final Net Profit:** +,289.16 (+12.89%)
- **Profit Factor:** 1.54
- **Total Closed Trades:** 49
- **Wins / Losses:** 25 Wins / 24 Losses
- **Win Rate:** 51.02%
- **Max Balance Drawdown:** 5.23% (.55)
- **Max Equity Drawdown:** 6.26% (.75)
- **Gross Profit:** ,690.70
- **Gross Loss:** -,401.54
- **Expected Payoff:** .31

---

## Strategy Logic & Archetype
- **Archetype:** Institutional Volatility Ratio Transition + 20-Bar Channel Breakout + ADX Strength
- **Algorithm Architecture:** Measures dynamic volatility expansion via the ratio of Fast Volatility (10-bar ATR) over Slow Volatility (30-bar ATR). When the ratio crosses the expansion threshold (Ratio >= 1.30), price breaks above the 20-period highest high, trend strength is confirmed by ADX(14) >= 22.0, and price is above the 50 EMA Macro Trend anchor, an institutional Long is executed.
- **Risk Management:** 1.0% dynamic risk sizing, 2.0x ATR Stop Loss, 3.0x ATR Take Profit (1:1.5 asymmetric risk-reward ratio).

---

## Tester Input Configuration
`ini
[Common]
Login=1000000000
Server=XMGlobal-MT5 6

[Tester]
Expert=multi agent all btc strategy\BTC_CUSTOM_INSTITUTIONAL_ALPHA.ex5
Symbol=BTCUSD#
Period=H1
Deposit=10000
Currency=USD
Leverage=100
Model=1
ExecutionMode=0
Optimization=0
FromDate=2025.09.28
ToDate=2026.09.28
Report=Reports\mt5_btc_custom_alpha_h1_report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpVolFastWindow=10
InpVolSlowWindow=30
InpVolRatioThresh=1.30
InpBreakoutLookback=20
InpMacroPeriod=50
InpADXPeriod=14
InpADXThreshold=22.0
InpMagicNumber=21018
InpATRStopMult=2.0
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
| **2025.09** | 2 | 1 | 1 | 50.00% | +.74 |
| **2025.10** | 9 | 4 | 5 | 44.44% | +.65 |
| **2025.11** | 3 | 2 | 1 | 66.67% | +.70 |
| **2025.12** | 4 | 2 | 2 | 50.00% | +.78 |
| **2026.01** | 4 | 1 | 3 | 25.00% | -.54 |
| **2026.02** | 1 | 1 | 0 | 100.00% | +.28 |
| **2026.03** | 4 | 2 | 2 | 50.00% | +.76 |
| **2026.04** | 3 | 2 | 1 | 66.67% | +.81 |
| **2026.05** | 3 | 0 | 3 | 0.00% | -.18 |
| **2026.06** | 1 | 1 | 0 | 100.00% | +.55 |
| **2026.07** | 2 | 0 | 2 | 0.00% | -.03 |
| **2026.08** | 9 | 6 | 3 | 66.67% | +.86 |
| **2026.09** | 4 | 3 | 1 | 75.00% | +.78 |
| **TOTAL** | **49** | **25** | **24** | **51.02%** | **+,289.16** |
