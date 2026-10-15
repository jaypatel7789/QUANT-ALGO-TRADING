# Strategy #16: PORTFOLIO-BTC-H1 (Dual-Engine Institutional Bitcoin Portfolio)

## Executive Summary
- **Strategy ID:** PORTFOLIO-BTC-H1
- **Asset / Symbol:** BTCUSD# (Bitcoin Spot USD)
- **Timeframe:** H1 (1-Hour)
- **Period Tested:** 2025.09.28 – 2026.09.28 (1 Full Year)
- **Initial Deposit:** ,000.00
- **Final Net Profit:** +,750.31 (+27.50%)
- **Profit Factor:** 1.56
- **Total Closed Trades:** 103
- **Wins / Losses:** 55 Wins / 48 Losses
- **Win Rate:** 53.40%
- **Max Balance Drawdown:** 11.22% (,294.12)
- **Max Equity Drawdown:** 13.75% (,600.39)
- **Gross Profit:** ,698.82
- **Gross Loss:** -,948.51
- **Expected Payoff:** .70

---

## Portfolio Composition & Core Architecture
Combines two independent, uncorrelated quantitative engines operating in parallel under a unified risk allocation framework on Bitcoin (BTCUSD#) 1-Hour chart:
1. **Engine 1: BTC-018 Markov Regime-Switching Volatility Breakout (Magic 11018)**
   - Captures high-conviction volatility transition breakouts when the fast/slow volatility ratio expands (Ratio >= 1.30) with ADX trend confirmation.
   - Sizing: 1.0% dynamic risk, 2.0x ATR Stop Loss, 2.5x ATR Take Profit.
2. **Engine 2: BTC-CUSTOM Institutional Volatility Ratio + ADX Regime Flow (Magic 21018)**
   - Detects 20-period swing breakouts during volatility expansion, holding an asymmetric 3.0x ATR profit target.
   - Sizing: 1.0% dynamic risk, 2.0x ATR Stop Loss, 3.0x ATR Take Profit.

---

## Tester Input Configuration
`ini
[Common]
Login=1000000000
Server=XMGlobal-MT5 6

[Tester]
Expert=multi agent all btc strategy\BTC_COMBINED_PORTFOLIO_H1.ex5
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
Report=Reports\mt5_btc_combined_report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpE1_MagicNumber=11018
InpE1_VolFastWindow=10
InpE1_VolSlowWindow=30
InpE1_VolRatioThresh=1.30
InpE1_MacroPeriod=50
InpE1_BreakoutLookback=20
InpE1_ADXPeriod=14
InpE1_ADXThreshold=22.0
InpE1_ATRStopMult=2.0
InpE1_TPMult=2.5
InpE1_RiskPercent=1.0
InpE2_MagicNumber=21018
InpE2_VolFastWindow=10
InpE2_VolSlowWindow=30
InpE2_VolRatioThresh=1.30
InpE2_BreakoutLookback=20
InpE2_MacroPeriod=50
InpE2_ADXPeriod=14
InpE2_ADXThreshold=22.0
InpE2_ATRStopMult=2.0
InpE2_TPMult=3.0
InpE2_UseBreakEven=false
InpE2_BETriggerATR=1.5
InpE2_RiskPercent=1.0
`

---

## Month-by-Month Financial Ledger

| Month | Trades | Wins | Losses | Win Rate (%) | Net Profit / Loss (USD) |
|---|:---:|:---:|:---:|:---:|:---:|
| **2025.09** | 4 | 2 | 2 | 50.00% | +.51 |
| **2025.10** | 18 | 8 | 10 | 44.44% | +.24 |
| **2025.11** | 6 | 4 | 2 | 66.67% | +.35 |
| **2025.12** | 9 | 4 | 5 | 44.44% | +.29 |
| **2026.01** | 9 | 4 | 5 | 44.44% | -.87 |
| **2026.02** | 2 | 2 | 0 | 100.00% | +.65 |
| **2026.03** | 8 | 4 | 4 | 50.00% | +.13 |
| **2026.04** | 7 | 4 | 3 | 57.14% | +.24 |
| **2026.05** | 6 | 0 | 6 | 0.00% | -.36 |
| **2026.06** | 2 | 2 | 0 | 100.00% | +.84 |
| **2026.07** | 4 | 0 | 4 | 0.00% | -.32 |
| **2026.08** | 20 | 14 | 6 | 70.00% | +,327.89 |
| **2026.09** | 8 | 7 | 1 | 87.50% | +.72 |
| **TOTAL** | **103** | **55** | **48** | **53.40%** | **+,750.31** |
