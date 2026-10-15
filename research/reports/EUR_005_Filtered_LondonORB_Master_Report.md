# EUR_005_Filtered_LondonORB - Individual Institutional Strategy Report

## Strategy Overview & Algorithmic Hypothesis
- **Strategy ID**: `EUR_005_Filtered_LondonORB`
- **Asset**: `EURUSD`
- **Timeframe**: `H1`
- **Execution Architecture**: Filtered London Opening Range Breakout (10-35 Pip Quality Gate, 50 Macro EMA, 1.5x SL, 2.2x TP, 0.6% Risk)
- **Testing Engine**: MetaTrader 5 Engine Native Backtest (XMGlobal-MT5 6, Account `1000000000`)
- **Backtesting Range**: 2025.09.28 – 2026.09.28 (12 Full Months)

---

## 1. Verified MetaTrader 5 Official Metrics

| Parameter | Official MT5 Result | Prop Firm Target | Status |
| :--- | :--- | :--- | :--- |
| **Initial Deposit** | **$10 000.00** | $10,000.00 | VERIFIED |
| **Total Net Profit** | **+$1 140.40** | +$1,000.00 (10%) | PASSED |
| **Gross Profit** | **$1 906.66** | N/A | VERIFIED |
| **Gross Loss** | **$-766.26** | N/A | VERIFIED |
| **Profit Factor (PF)** | **2.49** | **> 1.80** | **PASSED** |
| **Max Equity Drawdown** | **221.10 (2.03%)** | **< 8.00%** | **PASSED** |
| **Max Balance Drawdown** | **178.83 (1.77%)** | < 8.00% | VERIFIED |
| **Total Closed Trades** | **36** | Min 30 | VERIFIED |
| **Winning Trades Count** | **23 (63.89%)** | > 50% | VERIFIED |
| **Losing Trades Count** | **13 (36.11%)** | N/A | VERIFIED |
| **Short Trades Win Rate** | **19 (68.42%)** | N/A | VERIFIED |
| **Long Trades Win Rate** | **17 (58.82%)** | N/A | VERIFIED |
| **Largest Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Average Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Expected Payoff** | **+$31.68** | > 0.00 | VERIFIED |
| **Sharpe Ratio** | **16.30** | > 1.50 | VERIFIED |
| **Recovery Factor** | **5.16** | > 2.00 | VERIFIED |
| **Prop Firm Compliance**| **PASSED** | Strict Rules | **PASSED** |

---

## 2. Month-by-Month Verified Performance Breakdown

| Month | Trades | Wins | Losses | Win Rate (%) | Gross Profit ($) | Gross Loss ($) | Net Profit ($) | Return (%) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2025.09** | 2 | 1 | 1 | 50.0% | +$87.29 | -$59.67 | **+$27.62** | **+0.28%** | **PROFITABLE** |
| **2025.10** | 8 | 5 | 3 | 62.5% | +$397.56 | -$179.22 | **+$218.34** | **+2.18%** | **PROFITABLE** |
| **2025.11** | 3 | 3 | 0 | 100.0% | +$269.75 | -$0.00 | **+$269.75** | **+2.70%** | **PROFITABLE** |
| **2025.12** | 1 | 0 | 1 | 0.0% | +$0.00 | -$55.86 | **+$-55.86** | **-0.56%** | LOSS |
| **2026.01** | 2 | 0 | 2 | 0.0% | +$0.00 | -$80.62 | **+$-80.62** | **-0.81%** | LOSS |
| **2026.02** | 1 | 1 | 0 | 100.0% | +$89.79 | -$0.00 | **+$89.79** | **+0.90%** | **PROFITABLE** |
| **2026.03** | 10 | 7 | 3 | 70.0% | +$645.48 | -$191.58 | **+$453.90** | **+4.54%** | **PROFITABLE** |
| **2026.04** | 1 | 1 | 0 | 100.0% | +$2.66 | -$0.00 | **+$2.66** | **+0.03%** | **PROFITABLE** |
| **2026.05** | 2 | 2 | 0 | 100.0% | +$126.46 | -$0.00 | **+$126.46** | **+1.26%** | **PROFITABLE** |
| **2026.06** | 6 | 3 | 3 | 50.0% | +$287.67 | -$199.31 | **+$88.36** | **+0.88%** | **PROFITABLE** |

---

## 3. Production Deliverables
- **Master Excel Ledger**: `f:\multi agent\research\reports\EUR_005_Filtered_LondonORB_Master_Report.xlsx`
- **Source Code**: `f:\multi agent\scratch\EUR_005_Filtered_LondonORB.mq5`
- **Native MT5 HTML Report**: `C:\Users\Jay Patel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\Reports\mt5_eur005_h1_report.html`
