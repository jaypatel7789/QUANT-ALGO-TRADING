# Strategy Report: BTC-018 Adaptive Markov Volatility Regime-Switching

- **Strategy ID:** `BTC-018`
- **Strategy Archetype:** Adaptive Markov Volatility Regime-Switching Trend Expansion
- **Asset:** Bitcoin (`BTCUSD#` on `XMGlobal-MT5 6`)
- **Timeframe:** `H1` (1-Hour strictly)
- **Backtest Period:** `2025.09.28` to `2026.09.28` (Full 1 Year)
- **Model:** 1 Minute OHLC (Real tick data simulation)
- **Initial Deposit:** $10,000.00 USD
- **Final Balance:** $11,282.45 USD

---

## 1. Executive Performance Metrics

| Metric | Verified MT5 Value | Evaluation / Status |
| :--- | :---: | :--- |
| **Strategy ID** | `BTC-018` | Standardized ID |
| **Strategy Archetype** | Markov Volatility Regime Breakout | Volatility Gated Momentum |
| **Total Trades** | **54 Trades** | Low Churn / Zero Overtrading |
| **Wins / Losses** | **30 Wins / 24 Losses** | Positive Distribution |
| **Win Rate (%)** | **55.56%** | Solid Trend Win Rate |
| **Profit Factor** | **1.54** | Institutional Quality (>1.50) |
| **1-Yr Net Profit ($)** | <mark>**+$1,282.45**</mark> | **+12.82% Return on Deposit** |
| **Gross Profit** | +$3,656.78 | 30 Winning Trades |
| **Gross Loss** | -$2,374.33 | 24 Capped Losses |
| **Expected Payoff** | +$23.75 per trade | Positive Statistical Edge |
| **Max Drawdown ($)** | **$682.79** | Well within funded safety limits |
| **Max Drawdown (%)** | <mark>**6.40%**</mark> | Under 8.0% Prop Firm Limit |
| **Average Win** | +$121.89 | Asymmetric Payoff |
| **Average Loss** | -$98.93 | Strict Risk Discipline |
| **Largest Win** | +$149.98 | Big Momentum Expansion |
| **Largest Loss** | -$102.47 | Capped Stop Loss |

---

## 2. Core Quantitative Mechanism

`BTC-018` employs an institutional **two-state regime transition filter**:
1. **Volatility Regime Filter:** Compares rolling Fast Volatility Window (10-bar ATR) against Slow Volatility Window (30-bar ATR). It requires `Fast ATR / Slow ATR >= 1.30` (volatility expansion regime).
2. **Directional Momentum Gate:** Enters only when `ADX(14) >= 22.0`, ensuring market is entering a strong trending state rather than noisy consolidation.
3. **Macro Anchor Filter:** Price must align with the 50-period Exponential Moving Average (`Close > 50 EMA` for Longs).
4. **Risk & Profit Booking:**
   - Stop Loss: `2.0x ATR` below entry.
   - Take Profit: `2.5x ATR` above entry (Hard TP target, locking profits before momentum exhaustion).
   - Dynamic Risk: `1.0%` of account equity per trade.

---

## 3. Month-by-Month Verified Financial Ledger

| Month | Trades | Wins | Losses | Net Profit ($) | Monthly Return (%) | Win Rate (%) | Performance Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2025-09** | 2 | 1 | 1 | +$21.77 | +0.22% | 50.00% | Profitable |
| **2025-10** | 9 | 4 | 5 | -$13.41 | -0.13% | 44.44% | Minor Chop |
| **2025-11** | 3 | 2 | 1 | +$138.22 | +1.38% | 66.67% | Profitable |
| **2025-12** | 5 | 2 | 3 | -$50.14 | -0.50% | 40.00% | Consolidation |
| **2026-01** | 5 | 3 | 2 | +$159.37 | +1.59% | 60.00% | Profitable |
| **2026-02** | 1 | 1 | 0 | +$114.40 | +1.14% | 100.00% | Profitable |
| **2026-03** | 4 | 2 | 2 | +$48.59 | +0.49% | 50.00% | Profitable |
| **2026-04** | 4 | 2 | 2 | +$39.51 | +0.40% | 50.00% | Profitable |
| **2026-05** | 3 | 0 | 3 | -$296.96 | -2.97% | 0.00% | Drawdown |
| **2026-06** | 1 | 1 | 0 | +$126.29 | +1.26% | 100.00% | Profitable |
| **2026-07** | 2 | 0 | 2 | -$204.03 | -2.04% | 0.00% | Drawdown |
| **2026-08** | 11 | 8 | 3 | +$676.75 | +6.77% | 72.73% | Massive Bull Expansion |
| **2026-09** | 4 | 4 | 0 | +$522.09 | +5.22% | 100.00% | Perfect Month |
| **TOTAL** | **54** | **30** | **24** | <mark>**+$1,282.45**</mark> | <mark>**+12.82%**</mark> | **55.56%** | **PASS / APPROVED** |

---

## 4. MT5 Strategy Tester Exact Parameters

To replicate this exact backtest in your MetaTrader 5 terminal:

- **Expert:** `multi agent all btc strategy\BTC_018_Markov_RegimeSwitching.ex5`
- **Symbol:** `BTCUSD#`
- **Period:** `H1`
- **Date:** `2025.09.28` to `2026.09.28`
- **Deposit:** `10000` USD
- **Execution Mode:** `Normal`
- **Model:** `1 minute OHLC` (or `Every tick based on real ticks`)

### Input Parameters (`[TesterInputs]`):
```ini
InpWindow=10
InpSlowWindow=30
InpVolRatioThresh=1.30
InpMacroPeriod=50
InpBreakoutLookback=20
InpADXPeriod=14
InpADXThreshold=22.0
InpATRStopMult=2.0
InpTPMult=2.5
InpFixedLot=0.0
InpRiskPercent=1.0
InpMagicNumber=11018
```

---

## 5. Artifacts and Generated Files

- **Source Code:** [F:\multi agent\research\final report\BTC-018\BTC_018_Markov_RegimeSwitching.mq5](file:///f:/multi%20agent/research/final%20report/BTC-018/BTC_018_Markov_RegimeSwitching.mq5)
- **Compiled Binary:** [F:\multi agent\research\final report\BTC-018\BTC_018_Markov_RegimeSwitching.ex5](file:///f:/multi%20agent/research/final%20report/BTC-018/BTC_018_Markov_RegimeSwitching.ex5)
- **Tester Settings:** [F:\multi agent\research\final report\BTC-018\tester_BTC018_H1.ini](file:///f:/multi%20agent/research/final%20report/BTC-018/tester_BTC018_H1.ini)
- **Native MT5 HTML Report:** [F:\multi agent\research\final report\BTC-018\mt5_btc018_h1_report.html](file:///f:/multi%20agent/research/final%20report/BTC-018/mt5_btc018_h1_report.html)
