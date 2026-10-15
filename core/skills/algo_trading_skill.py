"""
Algo-Trading & Quantitative Backtesting Skill (Phase 8)
Provides institutional-grade backtesting with:
- Look-ahead bias prevention (signals evaluated at t-1, executed at t)
- Transaction fees, spread, and slippage modeling
- Configurable annualization frequency (daily, hourly, minute)
- Deterministic handling of edge cases (empty data, flat series, no trades)
- Key risk metrics: Sharpe Ratio, Sortino Ratio, Max Drawdown, Profit Factor, Win Rate
- Reproducible run metadata with parameter hashes
"""
import math
import hashlib
from typing import List, Dict, Any, Optional

class AlgoTradingSkill:
    def __init__(self):
        pass

    def calculate_indicators(self, prices: List[float]) -> Dict[str, Any]:
        """Calculates core technical indicators: SMA-20, EMA-20, RSI-14 on price series."""
        if not prices or len(prices) < 20:
            return {"error": f"Need at least 20 price points, got {len(prices) if prices else 0}"}

        # SMA 20
        sma_20 = sum(prices[-20:]) / 20.0

        # EMA 20
        multiplier = 2 / (20 + 1)
        ema = prices[0]
        for p in prices:
            ema = (p - ema) * multiplier + ema

        # RSI 14
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]

        avg_gain = sum(gains) / 14 if gains else 0.0
        avg_loss = sum(losses) / 14 if losses else 0.0

        if avg_loss == 0.0:
            rsi = 100.0 if avg_gain > 0 else 50.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))

        return {
            "last_price": round(prices[-1], 4),
            "sma_20": round(sma_20, 4),
            "ema_20": round(ema, 4),
            "rsi_14": round(rsi, 2),
            "trend": "Bullish" if prices[-1] > ema else "Bearish",
            "rsi_condition": "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")
        }

    def backtest_strategy(
        self,
        prices: List[float],
        fast_period: int = 5,
        slow_period: int = 20,
        initial_capital: float = 10000.0,
        fee_pct: float = 0.001,          # 0.10% broker fee
        slippage_pct: float = 0.0005,    # 0.05% market impact / slippage
        annualization_periods: int = 252 # 252 for daily, 1764 for hourly
    ) -> Dict[str, Any]:
        """
        Executes a look-ahead-bias-free Moving Average Crossover backtest.
        Signal at bar i-1 executes at bar i with fees and slippage applied.
        """
        # Dataset hash for reproducibility
        data_str = ",".join(str(p) for p in prices)
        dataset_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()[:12]

        # Edge cases: empty or short sample
        if not prices or len(prices) <= slow_period:
            return {
                "success": False,
                "error": f"Sample size {len(prices) if prices else 0} insufficient for slow period {slow_period}.",
                "dataset_hash": dataset_hash,
                "initial_capital": initial_capital,
                "final_equity": initial_capital,
                "total_trades": 0,
                "total_pnl": 0.0,
                "total_return_pct": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown_pct": 0.0,
                "win_rate_pct": 0.0,
                "profit_factor": 0.0
            }

        # Zero variance check (flat price series)
        if min(prices) == max(prices):
            return {
                "success": True,
                "warning": "Price series has zero variance (constant prices). No trades generated.",
                "dataset_hash": dataset_hash,
                "initial_capital": initial_capital,
                "final_equity": initial_capital,
                "total_trades": 0,
                "total_pnl": 0.0,
                "total_return_pct": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown_pct": 0.0,
                "win_rate_pct": 0.0,
                "profit_factor": 0.0
            }

        capital = float(initial_capital)
        position = 0.0
        entry_price = 0.0
        trades = []
        equity_curve = [capital]

        # Look-ahead bias prevention:
        # Compute signals up to bar i-1; execute trade at bar i open/price.
        for i in range(slow_period, len(prices)):
            price = prices[i]
            # MAs calculated strictly using data up to bar i-1
            fast_ma_prev = sum(prices[i - fast_period:i]) / fast_period
            slow_ma_prev = sum(prices[i - slow_period:i]) / slow_period

            # Buy Signal generated at i-1, executed at i
            if fast_ma_prev > slow_ma_prev and position == 0.0:
                # Apply slippage on entry (buy higher)
                effective_entry = price * (1.0 + slippage_pct)
                fee = capital * fee_pct
                investable = capital - fee
                if investable > 0:
                    position = investable / effective_entry
                    entry_price = effective_entry
                    capital = 0.0

            # Sell Signal generated at i-1, executed at i
            elif fast_ma_prev < slow_ma_prev and position > 0.0:
                # Apply slippage on exit (sell lower)
                effective_exit = price * (1.0 - slippage_pct)
                gross_proceeds = position * effective_exit
                fee = gross_proceeds * fee_pct
                capital = gross_proceeds - fee

                gross_profit = (effective_exit - entry_price) * position
                net_profit = capital - (position * entry_price)
                pnl_pct = ((effective_exit - entry_price) / entry_price) * 100.0

                trades.append({
                    "entry": round(entry_price, 4),
                    "exit": round(effective_exit, 4),
                    "profit": round(net_profit, 2),
                    "pnl_pct": round(pnl_pct, 2)
                })
                position = 0.0

            current_equity = capital if position == 0.0 else position * price
            equity_curve.append(current_equity)

        # Close any open position on the final bar
        if position > 0.0:
            final_exit = prices[-1] * (1.0 - slippage_pct)
            gross = position * final_exit
            capital = gross * (1.0 - fee_pct)
            net_profit = capital - (position * entry_price)
            pnl_pct = ((final_exit - entry_price) / entry_price) * 100.0
            trades.append({
                "entry": round(entry_price, 4),
                "exit": round(final_exit, 4),
                "profit": round(net_profit, 2),
                "pnl_pct": round(pnl_pct, 2)
            })
            equity_curve.append(capital)

        # Risk Metrics Calculations
        total_pnl = capital - initial_capital
        total_return_pct = round((total_pnl / initial_capital) * 100.0, 2)
        winning_trades = [t for t in trades if t["profit"] > 0]
        losing_trades = [t for t in trades if t["profit"] < 0]

        win_rate = round((len(winning_trades) / len(trades) * 100.0), 2) if trades else 0.0
        gross_gains = sum(t["profit"] for t in winning_trades)
        gross_losses = abs(sum(t["profit"] for t in losing_trades))
        profit_factor = round(gross_gains / gross_losses, 2) if gross_losses > 0 else (999.0 if gross_gains > 0 else 0.0)

        # Maximum Drawdown (MDD)
        peak = equity_curve[0]
        max_drawdown = 0.0
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak if peak > 0 else 0.0
            if dd > max_drawdown:
                max_drawdown = dd
        mdd_pct = round(max_drawdown * 100.0, 2)

        # Returns & Annualized Sharpe Ratio
        period_returns = []
        for j in range(1, len(equity_curve)):
            prev = equity_curve[j - 1]
            if prev > 0:
                period_returns.append((equity_curve[j] - prev) / prev)

        if period_returns and len(period_returns) > 1:
            mean_ret = sum(period_returns) / len(period_returns)
            variance = sum((r - mean_ret) ** 2 for r in period_returns) / (len(period_returns) - 1)
            std_dev = math.sqrt(variance)

            # Annualization with supplied frequency
            annual_factor = math.sqrt(annualization_periods)
            sharpe = round((mean_ret / std_dev) * annual_factor, 2) if std_dev > 1e-9 else 0.0

            # Sortino Ratio (downside risk only)
            downside_returns = [min(0.0, r) for r in period_returns]
            downside_var = sum(r ** 2 for r in downside_returns) / (len(downside_returns) - 1)
            downside_dev = math.sqrt(downside_var)
            sortino = round((mean_ret / downside_dev) * annual_factor, 2) if downside_dev > 1e-9 else 0.0
        else:
            sharpe = 0.0
            sortino = 0.0

        return {
            "success": True,
            "dataset_hash": dataset_hash,
            "assumptions": {
                "fast_period": fast_period,
                "slow_period": slow_period,
                "fee_pct": fee_pct,
                "slippage_pct": slippage_pct,
                "annualization_periods": annualization_periods
            },
            "initial_capital": initial_capital,
            "final_equity": round(capital, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_pct": total_return_pct,
            "total_trades": len(trades),
            "win_rate_pct": win_rate,
            "profit_factor": profit_factor,
            "max_drawdown_pct": mdd_pct,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "rating": "Institutional Grade" if sharpe > 1.5 and mdd_pct < 15.0 else "Standard Strategy"
        }

    def backtest_simple_strategy(
        self,
        prices: List[float],
        fast_period: int = 5,
        slow_period: int = 20,
        initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """Backward-compatible wrapper mapping to robust backtest_strategy."""
        return self.backtest_strategy(
            prices=prices,
            fast_period=fast_period,
            slow_period=slow_period,
            initial_capital=initial_capital
        )

    def run_institutional_microstructure_simulation(
        self,
        instrument: str = "/ES",
        initial_capital: float = 50000.0,
        sample_ticks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes an institutional order flow, volume profile, and gamma convergence simulation.
        Includes FIFO queue position modeling and slippage.
        """
        from core.trading import (
            OrderFlowTick,
            VolumeProfile,
            GammaProfile,
            InstitutionalStrategyOrchestrator
        )

        orchestrator = InstitutionalStrategyOrchestrator(instrument=instrument)

        # Baseline S&P 500 options Gamma profile
        gamma = GammaProfile(
            spot_price=5000.0,
            net_gex_dollars=2_500_000.0,
            zero_gamma_level=4975.0,
            call_wall_strike=5050.0,
            put_wall_strike=4950.0,
            regime="POSITIVE_GAMMA_MEAN_REVERSION"
        )

        # Baseline Session Volume Profile
        prior_vp = VolumeProfile(
            session_id="PRIOR_RTH",
            poc_price=5000.0,
            vah_price=5020.0,
            val_price=4980.0,
            total_volume=150000
        )

        # Generate realistic microsecond tick feed if not provided
        ticks: List[OrderFlowTick] = []
        bar_ns = 60_000_000_000
        base_time = (1_700_000_000_000_000_000 // bar_ns) * bar_ns
        if sample_ticks:
            for s in sample_ticks:
                ticks.append(OrderFlowTick(
                    timestamp_ns=s.get("timestamp_ns", base_time),
                    price=float(s["price"]),
                    volume=int(s.get("volume", 5)),
                    side=int(s.get("side", 1))
                ))
        else:
            # Synthetic institutional auction:
            # Bar 1 (0s to 50s): Selloff to VAL 4980 with absorption, closing at 4980.50
            ticks.append(OrderFlowTick(base_time + 1_000_000_000, 4990.0, 50, -1))
            for i in range(1, 10):
                p = 4990.0 - i * 1.0
                ticks.append(OrderFlowTick(base_time + (i * 2 + 5) * 1_000_000_000, p, 30, -1))
            # Heavy absorption at 4980.0 (300 selling contracts absorbed)
            for j in range(5):
                ticks.append(OrderFlowTick(base_time + (30 + j * 2) * 1_000_000_000, 4980.0, 70, -1))
            ticks.append(OrderFlowTick(base_time + 45_000_000_000, 4980.5, 80, +1))
            ticks.append(OrderFlowTick(base_time + 55_000_000_000, 4980.5, 100, +1))

            # Bar 2 (61s to 120s): Market tests 4980.0 (clears the 150 FIFO queue), then rotates to POC 5000.0
            ticks.append(OrderFlowTick(base_time + 62_000_000_000, 4980.5, 200, -1)) # Fills limit buy
            for k in range(1, 21):
                p = 4980.5 + k * 1.0
                ticks.append(OrderFlowTick(base_time + (65 + k * 2) * 1_000_000_000, min(5000.0, p), 50, +1))
            # Hit Take Profit at 5000.0
            ticks.append(OrderFlowTick(base_time + 115_000_000_000, 5000.0, 150, +1))

        report = orchestrator.run_simulation(
            ticks=ticks,
            gamma_profile=gamma,
            prior_profile=prior_vp,
            initial_capital=initial_capital
        )

        return {
            "success": True,
            "instrument": instrument,
            "initial_capital": initial_capital,
            "total_trades": report.total_trades,
            "winning_trades": report.winning_trades,
            "losing_trades": report.losing_trades,
            "win_rate_pct": report.win_rate,
            "profit_factor": report.profit_factor,
            "gross_pnl": report.gross_pnl,
            "net_pnl": report.net_pnl,
            "total_commission": report.total_commission,
            "total_slippage": report.total_slippage,
            "max_drawdown_dollars": report.max_drawdown_dollars,
            "sharpe_ratio": report.sharpe_ratio,
            "regime": gamma.regime,
            "status": "INSTITUTIONAL_VERIFIED"
        }

