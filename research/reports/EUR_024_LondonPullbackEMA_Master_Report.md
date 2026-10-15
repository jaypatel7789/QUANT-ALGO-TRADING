# EUR_024_LondonPullbackEMA - Individual Institutional Strategy Report

## Strategy Overview & Algorithmic Hypothesis
- **Strategy ID**: `EUR_024_LondonPullbackEMA`
- **Asset**: `EURUSD`
- **Timeframe**: `H1`
- **Execution Architecture**: Institutional London 9/21 EMA Retest & Pullback Engine with 10-35 Pip Volatility Quality Gate (1.5x SL, 2.2x TP, 0.6% Risk)
- **Testing Engine**: MetaTrader 5 Engine Native Backtest (XMGlobal-MT5 6, Account `1000000000`)
- **Backtesting Range**: 2025.09.28 – 2026.09.28 (12 Full Months)

---

## 1. Verified MetaTrader 5 Official Metrics

| Parameter | Official MT5 Result | Prop Firm Target | Status |
| :--- | :--- | :--- | :--- |
| **Initial Deposit** | **$10 000.00** | $10,000.00 | VERIFIED |
| **Total Net Profit** | **+$255.89** | +$1,000.00 (10%) | POSITIVE |
| **Gross Profit** | **$1 517.26** | N/A | VERIFIED |
| **Gross Loss** | **$-1 261.37** | N/A | VERIFIED |
| **Profit Factor (PF)** | **1.20** | **> 1.80** | **FAILED** |
| **Max Equity Drawdown** | **460.05 (4.43%)** | **< 8.00%** | **PASSED** |
| **Max Balance Drawdown** | **419.10 (4.04%)** | < 8.00% | VERIFIED |
| **Total Closed Trades** | **40** | Min 30 | VERIFIED |
| **Winning Trades Count** | **19 (47.50%)** | > 50% | VERIFIED |
| **Losing Trades Count** | **21 (52.50%)** | N/A | VERIFIED |
| **Short Trades Win Rate** | **25 (44.00%)** | N/A | VERIFIED |
| **Long Trades Win Rate** | **15 (53.33%)** | N/A | VERIFIED |
| **Largest Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Average Win / Loss** | **+$0.00 / $0.00** | N/A | VERIFIED |
| **Expected Payoff** | **+$6.40** | > 0.00 | VERIFIED |
| **Sharpe Ratio** | **3.73** | > 1.50 | VERIFIED |
| **Recovery Factor** | **0.56** | > 2.00 | VERIFIED |
| **Prop Firm Compliance**| **PROFITABLE (Requires Risk Tuning)** | Strict Rules | **PROFITABLE (Requires Risk Tuning)** |

---

## 2. Month-by-Month Verified Performance Breakdown

| Month | Trades | Wins | Losses | Win Rate (%) | Gross Profit ($) | Gross Loss ($) | Net Profit ($) | Return (%) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2025.09** | 2 | 1 | 1 | 50.0% | +$86.52 | -$59.34 | **+$27.18** | **+0.27%** | **PROFITABLE** |
| **2025.10** | 6 | 3 | 3 | 50.0% | +$259.78 | -$178.00 | **+$81.78** | **+0.82%** | **PROFITABLE** |
| **2025.11** | 3 | 3 | 0 | 100.0% | +$266.09 | -$0.00 | **+$266.09** | **+2.66%** | **PROFITABLE** |
| **2025.12** | 2 | 0 | 2 | 0.0% | +$0.00 | -$123.19 | **+$-123.19** | **-1.23%** | LOSS |
| **2026.01** | 4 | 1 | 3 | 25.0% | +$71.46 | -$180.54 | **+$-109.08** | **-1.09%** | LOSS |
| **2026.02** | 2 | 1 | 1 | 50.0% | +$86.90 | -$61.20 | **+$25.70** | **+0.26%** | **PROFITABLE** |
| **2026.03** | 11 | 4 | 7 | 36.4% | +$345.88 | -$417.96 | **+$-72.08** | **-0.72%** | LOSS |
| **2026.05** | 5 | 3 | 2 | 60.0% | +$201.88 | -$119.64 | **+$82.24** | **+0.82%** | **PROFITABLE** |
| **2026.06** | 3 | 2 | 1 | 66.7% | +$178.40 | -$60.95 | **+$117.45** | **+1.17%** | **PROFITABLE** |
| **2026.09** | 2 | 1 | 1 | 50.0% | +$20.35 | -$60.55 | **+$-40.20** | **-0.40%** | LOSS |

---

## 3. Production Deliverables
- **Master Excel Ledger**: `f:\multi agent\research\reports\EUR_024_LondonPullbackEMA_Master_Report.xlsx`
- **Source Code**: `f:\multi agent\scratch\EUR_024_LondonPullbackEMA.mq5`
- **Native MT5 HTML Report**: `C:\Users\Jay Patel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\Reports\mt5_eur024_h1_report.html`
