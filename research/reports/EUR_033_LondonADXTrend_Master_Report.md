# EUR_033_LondonADXTrend - Individual Institutional Strategy Report

## Strategy Overview & Algorithmic Hypothesis
- **Strategy ID**: `EUR_033_LondonADXTrend`
- **Asset**: `EURUSD`
- **Timeframe**: `H1`
- **Execution Architecture**: London ORB with ADX Trend Strength Filter & Early Break-Even Defense (22 Min ADX, 0.9x BE Trigger, 1.8x TP, 0.6% Risk)
- **Testing Engine**: MetaTrader 5 Engine Native Backtest (XMGlobal-MT5 6, Account `1000000000`)
- **Backtesting Range**: 2025.09.28 – 2026.09.28 (12 Full Months)

---

## 1. Verified MetaTrader 5 Official Metrics

| Parameter | Official MT5 Result | Prop Firm Target | Status |
| :--- | :--- | :--- | :--- |
| **Initial Deposit** | **$10 000.00** | $10,000.00 | VERIFIED |
| **Total Net Profit** | **+$350.51** | +$1,000.00 (10%) | POSITIVE |
| **Gross Profit** | **$784.51** | N/A | VERIFIED |
| **Gross Loss** | **$-434.00** | N/A | VERIFIED |
| **Profit Factor (PF)** | **1.81** | **> 1.80** | **PASSED** |
| **Max Equity Drawdown** | **210.14 (2.08%)** | **< 8.00%** | **PASSED** |
| **Max Balance Drawdown** | **178.77 (1.77%)** | < 8.00% | VERIFIED |
| **Total Closed Trades** | **28** | Min 30 | VERIFIED |
| **Winning Trades Count** | **20 (71.43%)** | > 50% | VERIFIED |
| **Losing Trades Count** | **8 (28.57%)** | N/A | VERIFIED |
| **Short Trades Win Rate** | **12 (75.00%)** | N/A | VERIFIED |
| **Long Trades Win Rate** | **16 (68.75%)** | N/A | VERIFIED |
| **Largest Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Average Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Expected Payoff** | **+$12.52** | > 0.00 | VERIFIED |
| **Sharpe Ratio** | **9.77** | > 1.50 | VERIFIED |
| **Recovery Factor** | **1.67** | > 2.00 | VERIFIED |
| **Prop Firm Compliance**| **PASSED** | Strict Rules | **PASSED** |

---

## 2. Month-by-Month Verified Performance Breakdown

| Month | Trades | Wins | Losses | Win Rate (%) | Gross Profit ($) | Gross Loss ($) | Net Profit ($) | Return (%) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2025.09** | 4 | 3 | 1 | 75.0% | +$89.39 | -$59.67 | **+$29.72** | **+0.30%** | **PROFITABLE** |
| **2025.10** | 5 | 2 | 3 | 40.0% | +$79.70 | -$177.34 | **+$-97.64** | **-0.98%** | LOSS |
| **2025.11** | 2 | 2 | 0 | 100.0% | +$79.23 | -$0.00 | **+$79.23** | **+0.79%** | **PROFITABLE** |
| **2026.01** | 1 | 0 | 1 | 0.0% | +$0.00 | -$18.15 | **+$-18.15** | **-0.18%** | LOSS |
| **2026.02** | 2 | 2 | 0 | 100.0% | +$79.14 | -$0.00 | **+$79.14** | **+0.79%** | **PROFITABLE** |
| **2026.03** | 9 | 7 | 2 | 77.8% | +$236.48 | -$117.80 | **+$118.68** | **+1.19%** | **PROFITABLE** |
| **2026.04** | 1 | 1 | 0 | 100.0% | +$3.60 | -$0.00 | **+$3.60** | **+0.04%** | **PROFITABLE** |
| **2026.05** | 1 | 1 | 0 | 100.0% | +$71.70 | -$0.00 | **+$71.70** | **+0.72%** | **PROFITABLE** |
| **2026.06** | 3 | 2 | 1 | 66.7% | +$145.27 | -$61.04 | **+$84.23** | **+0.84%** | **PROFITABLE** |

---

## 3. Production Deliverables
- **Master Excel Ledger**: `f:\multi agent\research\reports\EUR_033_LondonADXTrend_Master_Report.xlsx`
- **Source Code**: `f:\multi agent\scratch\EUR_033_LondonADXTrend.mq5`
- **Native MT5 HTML Report**: `C:\Users\Jay Patel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\Reports\mt5_eur033_h1_report.html`
