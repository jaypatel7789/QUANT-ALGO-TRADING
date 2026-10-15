"""
Institutional Tick-by-Tick Backtesting Engine with FIFO Queue Modeling (Phase 4)
Features:
- CME Globex FIFO limit order queue position simulation (realistic fill modeling)
- Adverse execution slippage on market and stop orders
- Institutional fee structure (CME exchange fee, NFA fee, clearing)
- Instrument sizing for /ES ($50/pt, $12.50/tick) and /MES ($5/pt, $1.25/tick)
- Performance metrics: Win Rate, Profit Factor, Expectancy, Sharpe Ratio, Max Drawdown
"""
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class SimulatedOrder:
    order_id: str
    direction: str  # "BUY" or "SELL"
    order_type: str  # "LIMIT" or "MARKET" or "STOP"
    price: float
    size: int
    queue_ahead_volume: int = 0
    submitted_time_ns: int = 0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    tag: str = ""

@dataclass
class SimulatedTrade:
    trade_id: str
    direction: str
    entry_price: float
    exit_price: float
    size: int
    entry_time_ns: int
    exit_time_ns: int
    gross_pnl: float
    net_pnl: float
    commission: float
    slippage_cost: float
    exit_reason: str
    tag: str = ""

@dataclass
class BacktestReport:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    gross_pnl: float
    net_pnl: float
    total_commission: float
    total_slippage: float
    max_drawdown_dollars: float
    max_drawdown_pct: float
    sharpe_ratio: float
    trades: List[SimulatedTrade] = field(default_factory=list)

class InstitutionalBacktester:
    """
    High-fidelity event-driven backtesting engine for futures order books.
    """
    def __init__(
        self,
        instrument: str = "/ES",
        initial_capital: float = 50000.0,
        commission_per_contract: float = 1.85,  # per side ($3.70 round turn)
        slippage_ticks: int = 1,                 # 1 tick adverse slippage on market/stop orders
        tick_size: float = 0.25
    ):
        self.instrument = instrument
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission_per_contract = commission_per_contract
        self.slippage_ticks = slippage_ticks
        self.tick_size = tick_size

        # Instrument point multiplier: /ES is $50/pt ($12.50/tick); /MES is $5/pt ($1.25/tick)
        self.point_value = 5.0 if instrument.upper() == "/MES" else 50.0
        self.tick_value = self.point_value * self.tick_size

        self.pending_orders: List[SimulatedOrder] = []
        self.open_position: Optional[Dict[str, Any]] = None
        self.closed_trades: List[SimulatedTrade] = []
        self.equity_curve: List[float] = [initial_capital]

    def round_to_tick(self, price: float) -> float:
        return round(round(price / self.tick_size) * self.tick_size, 4)

    def submit_limit_order(
        self,
        direction: str,
        price: float,
        size: int = 1,
        resting_depth_estimate: int = 250,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        tag: str = "",
        timestamp_ns: int = 0
    ) -> SimulatedOrder:
        """
        Submits a limit order into the simulated CME Globex FIFO queue.
        Requires resting_depth_estimate volume to trade at this price before getting filled.
        """
        order = SimulatedOrder(
            order_id=f"ord-{len(self.pending_orders) + len(self.closed_trades) + 1}",
            direction=direction.upper(),
            order_type="LIMIT",
            price=self.round_to_tick(price),
            size=size,
            queue_ahead_volume=resting_depth_estimate,
            submitted_time_ns=timestamp_ns,
            stop_loss=self.round_to_tick(stop_loss) if stop_loss else None,
            take_profit=self.round_to_tick(take_profit) if take_profit else None,
            tag=tag
        )
        self.pending_orders.append(order)
        return order

    def process_tick(
        self,
        timestamp_ns: int,
        price: float,
        volume: int,
        side: int  # +1 for aggressive buy, -1 for aggressive sell
    ):
        """Processes an incoming market trade tick against open orders and positions."""
        p_rounded = self.round_to_tick(price)

        # 1. Check stop-loss and take-profit on open positions first
        if self.open_position:
            pos = self.open_position
            direction = pos["direction"]
            sl = pos["stop_loss"]
            tp = pos["take_profit"]

            # Long position checks
            if direction == "BUY":
                if sl is not None and p_rounded <= sl:
                    # Slippage on stop loss
                    exec_price = self.round_to_tick(sl - self.slippage_ticks * self.tick_size)
                    self._close_position(exec_price, timestamp_ns, "STOP_LOSS", slippage_applied=True)
                    return
                elif tp is not None and p_rounded >= tp:
                    self._close_position(tp, timestamp_ns, "TAKE_PROFIT", slippage_applied=False)
                    return

            # Short position checks
            elif direction == "SELL":
                if sl is not None and p_rounded >= sl:
                    exec_price = self.round_to_tick(sl + self.slippage_ticks * self.tick_size)
                    self._close_position(exec_price, timestamp_ns, "STOP_LOSS", slippage_applied=True)
                    return
                elif tp is not None and p_rounded <= tp:
                    self._close_position(tp, timestamp_ns, "TAKE_PROFIT", slippage_applied=False)
                    return

        # 2. Update FIFO queue positions for pending limit orders
        unfilled_orders: List[SimulatedOrder] = []
        for ord in self.pending_orders:
            # We already have an open position; do not over-fill
            if self.open_position:
                unfilled_orders.append(ord)
                continue

            if ord.direction == "BUY":
                # Limit Buy is filled when trades occur at or below order price
                if p_rounded < ord.price:
                    # Market traded through our price: filled immediately
                    self._open_position(ord, ord.price, timestamp_ns)
                elif p_rounded == ord.price and side < 0:
                    # Aggressive sellers hitting bid: reduce queue ahead volume
                    ord.queue_ahead_volume -= volume
                    if ord.queue_ahead_volume <= 0:
                        self._open_position(ord, ord.price, timestamp_ns)
                    else:
                        unfilled_orders.append(ord)
                else:
                    unfilled_orders.append(ord)

            elif ord.direction == "SELL":
                # Limit Sell is filled when trades occur at or above order price
                if p_rounded > ord.price:
                    self._open_position(ord, ord.price, timestamp_ns)
                elif p_rounded == ord.price and side > 0:
                    # Aggressive buyers hitting ask: reduce queue ahead volume
                    ord.queue_ahead_volume -= volume
                    if ord.queue_ahead_volume <= 0:
                        self._open_position(ord, ord.price, timestamp_ns)
                    else:
                        unfilled_orders.append(ord)
                else:
                    unfilled_orders.append(ord)

        self.pending_orders = unfilled_orders

    def _open_position(self, order: SimulatedOrder, exec_price: float, timestamp_ns: int):
        """Fills an order and opens an active position."""
        self.open_position = {
            "order_id": order.order_id,
            "direction": order.direction,
            "entry_price": exec_price,
            "size": order.size,
            "entry_time_ns": timestamp_ns,
            "stop_loss": order.stop_loss,
            "take_profit": order.take_profit,
            "tag": order.tag
        }

    def _close_position(
        self,
        exec_price: float,
        timestamp_ns: int,
        reason: str,
        slippage_applied: bool = False
    ):
        """Closes the current position, computes net PnL, commissions and slippage."""
        pos = self.open_position
        if not pos:
            return

        direction = pos["direction"]
        entry_price = pos["entry_price"]
        size = pos["size"]

        # Points captured
        pts = (exec_price - entry_price) if direction == "BUY" else (entry_price - exec_price)
        gross_pnl = pts * self.point_value * size

        # Round turn commission: $1.85 entry + $1.85 exit = $3.70 per contract
        commissions = self.commission_per_contract * 2 * size

        # Slippage cost in dollars
        slippage_cost = (self.slippage_ticks * self.tick_value * size) if slippage_applied else 0.0

        net_pnl = gross_pnl - commissions - slippage_cost
        self.capital += net_pnl
        self.equity_curve.append(self.capital)

        trade = SimulatedTrade(
            trade_id=f"trd-{len(self.closed_trades) + 1}",
            direction=direction,
            entry_price=entry_price,
            exit_price=exec_price,
            size=size,
            entry_time_ns=pos["entry_time_ns"],
            exit_time_ns=timestamp_ns,
            gross_pnl=round(gross_pnl, 2),
            net_pnl=round(net_pnl, 2),
            commission=round(commissions, 2),
            slippage_cost=round(slippage_cost, 2),
            exit_reason=reason,
            tag=pos["tag"]
        )

        self.closed_trades.append(trade)
        self.open_position = None

    def generate_report(self) -> BacktestReport:
        """Generates comprehensive institutional backtest report with Sharpe, Drawdown, and Win Rate."""
        total_trades = len(self.closed_trades)
        if total_trades == 0:
            return BacktestReport(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                gross_pnl=0.0,
                net_pnl=0.0,
                total_commission=0.0,
                total_slippage=0.0,
                max_drawdown_dollars=0.0,
                max_drawdown_pct=0.0,
                sharpe_ratio=0.0,
                trades=[]
            )

        wins = [t for t in self.closed_trades if t.net_pnl > 0]
        losses = [t for t in self.closed_trades if t.net_pnl <= 0]

        win_rate = round(len(wins) / total_trades * 100, 2)

        gross_wins = sum(t.net_pnl for t in wins)
        gross_losses = abs(sum(t.net_pnl for t in losses))
        profit_factor = round(gross_wins / gross_losses, 2) if gross_losses > 0 else 999.0

        gross_pnl = round(sum(t.gross_pnl for t in self.closed_trades), 2)
        net_pnl = round(sum(t.net_pnl for t in self.closed_trades), 2)
        total_comm = round(sum(t.commission for t in self.closed_trades), 2)
        total_slip = round(sum(t.slippage_cost for t in self.closed_trades), 2)

        # Max Drawdown calculation
        peak = self.equity_curve[0]
        max_dd_dollars = 0.0
        max_dd_pct = 0.0
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd_dol = peak - eq
            dd_p = (dd_dol / peak * 100) if peak > 0 else 0.0
            if dd_dol > max_dd_dollars:
                max_dd_dollars = dd_dol
            if dd_p > max_dd_pct:
                max_dd_pct = dd_p

        # Sharpe Ratio (annualized assuming 252 trading days)
        returns = [t.net_pnl / self.initial_capital for t in self.closed_trades]
        mean_ret = sum(returns) / len(returns)
        variance = sum((r - mean_ret) ** 2 for r in returns) / max(1, len(returns) - 1)
        std_ret = math.sqrt(variance) if variance > 0 else 0.0001
        sharpe = round((mean_ret / std_ret) * math.sqrt(252), 2) if std_ret > 0 else 0.0

        return BacktestReport(
            total_trades=total_trades,
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=win_rate,
            profit_factor=profit_factor,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            total_commission=total_comm,
            total_slippage=total_slip,
            max_drawdown_dollars=round(max_dd_dollars, 2),
            max_drawdown_pct=round(max_dd_pct, 2),
            sharpe_ratio=sharpe,
            trades=self.closed_trades
        )
