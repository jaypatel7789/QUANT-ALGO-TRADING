-----# Strategy Report: BTC-009 (Multi-Timeframe Trend Coherence & Volatility Expansion)

## Executive Summary
- **Strategy ID:** `BTC-009`
- **Strategy Archetype:** Multi-Timeframe Trend Coherence & Volatility Expansion
- **Asset / Symbol:** `BTCUSD#`
- **Timeframe:** `H1` (1-Hour)
- **Evaluation Period:** `2025.09.28 - 2026.09.28` (1 Full Year)
- **Account Deposit:** $10,000.00 USD
- **Leverage:** 1:100
- **Execution Model:** 1 Minute OHLC (`Model=1`)

---

## 1. Core Quantitative Mechanism
BTC-009 captures high-probability expansion phases by demanding dual-layer trend coherence combined with volatility and volume gating:
1. **Dual Trend Hierarchy:** Requires alignment between the intermediate 50-period EMA and the macro 200-period EMA:
   $$\text{Price} > \text{EMA}_{200} \quad \text{AND} \quad \text{EMA}_{50} > \text{EMA}_{200}$$
2. **Donchian Channel Breakout:** Triggers entries when price breaks out above the highest high of the prior 20 bars.
3. **Volatility & Volume Expansion Gates:**
   - **Volatility Surge:** Real-time ATR must exceed its 30-bar simple moving average by at least $1.20\times$:
     $$\text{ATR}_{14} \ge 1.20 \times \text{SMA}(\text{ATR}, 30)$$
   - **Volume Surge:** Real-time tick volume must exceed its 20-bar simple moving average by at least $1.10\times$.
4. **Dynamic Trailing & Exhaustion Defense:** Tracks gains using a 2.5x ATR trailing stop and liquidates positions immediately if price breaks down below the 10-bar Donchian low or crosses below the 50-period intermediate EMA.

---

## 2. 1-Year Master Backtest Verification

| Strategy ID | Strategy Archetype | Trade Count | Wins / Losses | Win Rate | Profit Factor | 1-Yr Net Profit ($) | Max Drawdown (%) | Core Mechanism |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`BTC-009`** | **Multi-Timeframe Trend Coherence** | **17** | **11 / 6** | **64.71%** | **2.13** | **+$329.82 (+3.30%)** | **1.78% ($187.02)** | 200 EMA + 50 EMA Coherence + 20-bar Donchian Breakout + ATR Vol Gate ($\ge 1.2\times$) + 2.5x ATR Trailing Stop |

---

## 3. Month-by-Month Financial Ledger (`BTC-009` H1)

| Month | Trade Count | Wins | Losses | Net Profit ($) | Win Rate (%) | Cumulative Net PnL ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2025-09** | 0 | 0 | 0 | **$0.00** | 0.00% | $0.00 |
| **2025-10** | 2 | 2 | 0 | **+$48.93** | 100.00% | +$48.93 |
| **2025-11** | 0 | 0 | 0 | **$0.00** | 0.00% | +$48.93 |
| **2025-12** | 0 | 0 | 0 | **$0.00** | 0.00% | +$48.93 |
| **2026-01** | 2 | 2 | 0 | **+$190.30** | 100.00% | +$239.23 |
| **2026-02** | 0 | 0 | 0 | **$0.00** | 0.00% | +$239.23 |
| **2026-03** | 1 | 1 | 0 | **+$53.50** | 100.00% | +$292.73 |
| **2026-04** | 3 | 2 | 1 | **+$194.04** | 66.67% | +$486.77 |
| **2026-05** | 2 | 0 | 2 | **-$100.92** | 0.00% | +$385.85 |
| **2026-06** | 0 | 0 | 0 | **$0.00** | 0.00% | +$385.85 |
| **2026-07** | 2 | 1 | 1 | **+$17.19** | 50.00% | +$403.04 |
| **2026-08** | 4 | 2 | 2 | **-$85.20** | 50.00% | +$317.84 |
| **2026-09** | 1 | 1 | 0 | **+$11.98** | 100.00% | +$329.82 |
| **TOTAL** | **17** | **11** | **6** | **+$329.82** | **64.71%** | **+$329.82 (+3.30%)** |

---

## 4. MT5 Tester Settings for Reproduction

```ini
[Common]
Login=1000000000
Server=XMGlobal-MT5 6

[Tester]
Expert=multi agent all btc strategy\BTC_009_MultiTimeframe_TrendCoherence.ex5
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
Report=Reports\mt5_btc009_h1_report.html
ReplaceReport=1
ShutdownTerminal=1

[TesterInputs]
InpMacroEMA=200
InpFastEMA=50
InpDonchianPeriod=20
InpVolGateMult=1.20
InpATRMALookback=30
InpVolMAPeriod=20
InpVolSurgeMult=1.10
InpMagicNumber=11009
InpATRPeriod=14
InpATRStopMult=2.50
InpTPMult=0.00
InpUseTrailing=true
InpFixedLot=0.00
InpRiskPercent=1.00
```

---

## 5. Saved Deliverables in `F:\multi agent\research\final report\BTC-009\`
- **Source Code:** [BTC_009_MultiTimeframe_TrendCoherence.mq5](file:///F:/multi%20agent/research/final%20report/BTC-009/BTC_009_MultiTimeframe_TrendCoherence.mq5)
- **Compiled Binary:** [BTC_009_MultiTimeframe_TrendCoherence.ex5](file:///F:/multi%20agent/research/final%20report/BTC-009/BTC_009_MultiTimeframe_TrendCoherence.ex5)
- **Tester Settings:** [tester_BTC009_H1.ini](file:///F:/multi%20agent/research/final%20report/BTC-009/tester_BTC009_H1.ini)
- **Native MT5 HTML Report:** [mt5_btc009_h1_report.html](file:///F:/multi%20agent/research/final%20report/BTC-009/mt5_btc009_h1_report.html)
- **Strategy Report Markdown:** [BTC_009_Strategy_Report.md](file:///F:/multi%20agent/research/final%20report/BTC-009/BTC_009_Strategy_Report.md)
