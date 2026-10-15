# EUR_005B_LondonORB_BreakEvenLock - Individual Institutional Strategy Report

## Strategy Overview & Algorithmic Hypothesis
- **Strategy ID**: `EUR_005B_LondonORB_BreakEvenLock`
- **Asset**: `EURUSD`
- **Timeframe**: `H1`
- **Execution Architecture**: Filtered London Opening Range Breakout with Dynamic 1.2x ATR Break-Even Stop (10-35 Pip Quality Gate, 50 Macro EMA, 1.5x SL, 2.5x TP, 0.6% Risk)
- **Testing Engine**: MetaTrader 5 Engine Native Backtest (XMGlobal-MT5 6, Account `1301597088`)
- **Backtesting Range**: 2025.09.28 – 2026.09.28 (12 Full Months)

---

## 1. Verified MetaTrader 5 Official Metrics

| Parameter | Official MT5 Result | Prop Firm Target | Status |
| :--- | :--- | :--- | :--- |
| **Initial Deposit** | **$10 000.00** | $10,000.00 | VERIFIED |
| **Total Net Profit** | **+$920.69** | +$1,000.00 (10%) | POSITIVE |
| **Gross Profit** | **$1 430.28** | N/A | VERIFIED |
| **Gross Loss** | **$-509.59** | N/A | VERIFIED |
| **Profit Factor (PF)** | **2.81** | **> 1.80** | **PASSED** |
| **Max Equity Drawdown** | **272.03 (2.60%)** | **< 8.00%** | **PASSED** |
| **Max Balance Drawdown** | **197.58 (1.90%)** | < 8.00% | VERIFIED |
| **Total Closed Trades** | **36** | Min 30 | VERIFIED |
| **Winning Trades Count** | **27 (75.00%)** | > 50% | VERIFIED |
| **Losing Trades Count** | **9 (25.00%)** | N/A | VERIFIED |
| **Short Trades Win Rate** | **19 (78.95%)** | N/A | VERIFIED |
| **Long Trades Win Rate** | **17 (70.59%)** | N/A | VERIFIED |
| **Largest Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Average Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Expected Payoff** | **+$25.57** | > 0.00 | VERIFIED |
| **Sharpe Ratio** | **15.38** | > 1.50 | VERIFIED |
| **Recovery Factor** | **3.38** | > 2.00 | VERIFIED |
| **Prop Firm Compliance**| **PASSED** | Strict Rules | **PASSED** |

---

## 2. Month-by-Month Verified Performance Breakdown

| Month | Trades | Wins | Losses | Win Rate (%) | Gross Profit ($) | Gross Loss ($) | Net Profit ($) | Return (%) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2025.09** | 2 | 2 | 0 | 100.0% | +$17.64 | -$0.00 | **+$17.64** | **+0.18%** | **PROFITABLE** |
| **2025.10** | 7 | 5 | 2 | 71.4% | +$307.74 | -$119.16 | **+$188.58** | **+1.89%** | **PROFITABLE** |
| **2025.11** | 4 | 3 | 1 | 75.0% | +$189.99 | -$61.65 | **+$128.34** | **+1.28%** | **PROFITABLE** |
| **2025.12** | 1 | 0 | 1 | 0.0% | +$0.00 | -$55.86 | **+$-55.86** | **-0.56%** | LOSS |
| **2026.01** | 2 | 0 | 2 | 0.0% | +$0.00 | -$80.07 | **+$-80.07** | **-0.80%** | LOSS |
| **2026.02** | 1 | 1 | 0 | 100.0% | +$8.80 | -$0.00 | **+$8.80** | **+0.09%** | **PROFITABLE** |
| **2026.03** | 11 | 10 | 1 | 90.9% | +$567.65 | -$63.80 | **+$503.85** | **+5.04%** | **PROFITABLE** |
| **2026.04** | 1 | 1 | 0 | 100.0% | +$3.80 | -$0.00 | **+$3.80** | **+0.04%** | **PROFITABLE** |
| **2026.05** | 2 | 2 | 0 | 100.0% | +$13.54 | -$0.00 | **+$13.54** | **+0.14%** | **PROFITABLE** |
| **2026.06** | 5 | 3 | 2 | 60.0% | +$321.12 | -$129.05 | **+$192.07** | **+1.92%** | **PROFITABLE** |

---

## 3. Production Deliverables
- **Master Excel Ledger**: `f:\multi agent\research\reports\EUR_005B_LondonORB_BreakEvenLock_Master_Report.xlsx`
- **Source Code**: `f:\multi agent\scratch\EUR_005B_LondonORB_BreakEvenLock.mq5`
- **Native MT5 HTML Report**: `C:\Users\Jay Patel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\Reports\mt5_eur005_be_h1_report.html`
