# Persistent BTC/USD Quantitative Strategy Research Program

**Mission**: Continuous, automated discovery, multi-timeframe backtesting, parameter optimization, and funded-account validation of institutional quantitative algorithms for Bitcoin (`BTCUSD#` / `BTC/USDT`).

---

## 1. Active Research State
* **Program Status**: `ACTIVE / CONTINUOUS`
* **Current Focus**: Candidate `BTC-003` (Volume-Weighted MACD & Bollinger Squeeze)
* **Status**: `STAGING - PENDING APPROVAL`
* **Next in Pipeline**: Candidate `BTC-004` (Kaufman Adaptive Moving Average Noise Filter)
* **Engines**: 
  1. **QuantDinger OS**: Strategy API V2 (`1m`, `5m`, `15m`, `1h`)
  2. **MetaTrader 5 (MT5)**: XMGlobal broker direct feed (`1m`, `5m`, `15m`, `1h`)
* **Prop Firm Standards Target**:
  - Max Trailing Drawdown: `<= 8.0%` (FTMO 10% hard cap)
  - Max Intraday Drawdown: `<= 4.0%` (FTMO 5% daily hard cap)
  - Profit Factor: `>= 1.40`
  - Win Rate: `>= 38.0%` with positive risk-to-reward asymmetry
* **Master Excel Output**: [research/excel/backtest_master_ledger.xlsx](file:///f:/multi%20agent/research/excel/backtest_master_ledger.xlsx)
* **Evidence Reports**:
  - [research/staging/BTC-001_evidence_report.md](file:///f:/multi%20agent/research/staging/BTC-001_evidence_report.md)
  - [research/staging/BTC-002_evidence_report.md](file:///f:/multi%20agent/research/staging/BTC-002_evidence_report.md)
  - [research/staging/BTC-003_evidence_report.md](file:///f:/multi%20agent/research/staging/BTC-003_evidence_report.md)
* **Performance Charts**: [research/reports/](file:///f:/multi%20agent/research/reports/) (20 Dark-Mode 3-Panel PNG Charts)

---

## 2. Research Candidate Summary

| Candidate ID | Strategy Name | Mechanism | Top Performance | Top Score | Status | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BTC-001** | Adaptive Volatility Breakout (EMA 20/50 + RSI) | Trend Following | MT5 1m (-2.74% Ret, -3.25% MaxDD) | 50.0/100 | Evaluated | **REJECTED** (Chop whipsaws) |
| **BTC-002** | Donchian Channel Breakout (Turtle Crypto) | Range Breakout | MT5 1h (+13.00% Ret, -7.35% MaxDD, PF 1.58) | 70.0/100 | Evaluated | **REJECTED BY USER** |
| **BTC-003** | Volume-Weighted MACD & Bollinger Squeeze | Volatility Squeeze | MT5 15m (+1.50% Ret, **-2.24% MaxDD**, PF 1.38) | **75.0/100** | Staging | **PENDING REVIEW** |
| **BTC-004** | Kaufman Adaptive Moving Average (KAMA) | Noise Filter Trend | Queued | Pending | Queued | Next in Queue |

---

## 3. Workflow Execution Cycle
```text
[Global Research Discovery]
         │  Scrapes and synthesizes quantitative models from literature, arXiv, SSRN, GitHub, MQL5
         ▼
[Candidate Formalization]
         │  Assigns stable Candidate ID, defines mathematical logic, entries, exits, risk rules
         ▼
[QuantDinger Multi-Timeframe Matrix]
         │  Executes backtests on 1m, 5m, 15m, 1h via Strategy API V2
         ▼
[MT5 XMGlobal Multi-Timeframe & Setting Sweeps]
         │  Executes backtests on 1m, 5m, 15m, 1h across Conservative, Aggressive, and Scalp variants
         ▼
[Funded Account Scoring & Risk Audit]
         │  Evaluates drawdown caps, Sharpe, Sortino, P/L asymmetry, and consistency
         ▼
[Master Excel Ledger & Visual Chart Generation]
         │  Appends comprehensive metrics to backtest_master_ledger.xlsx and saves 3-panel PNG charts
         ▼
[Live Dashboard Streaming & Continuous Loop Trigger]
         └──► Streams live data to http://127.0.0.1:8090 and initiates next candidate cycle
```
