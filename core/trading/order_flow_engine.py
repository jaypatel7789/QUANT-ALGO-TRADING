"""
Order Flow & Footprint Microstructure Engine (Phase 1)
Analyzes:
- Nanosecond tick-by-tick order execution
- Bid x Ask Footprint clusters
- Cumulative Volume Delta (CVD)
- Diagonal Bid/Ask imbalances (stacked imbalances)
- Passive limit order absorption & aggressive exhaustion
- Trapped traders and delta divergence
"""
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class OrderFlowTick:
    timestamp_ns: int
    price: float
    volume: int
    side: int  # +1 for aggressive buy (at ask), -1 for aggressive sell (at bid)

@dataclass
class FootprintBar:
    start_time_ns: int
    end_time_ns: int
    open: float
    high: float
    low: float
    close: float
    total_volume: int = 0
    delta: int = 0
    buy_volume: int = 0
    sell_volume: int = 0
    # price -> {"bid_vol": int, "ask_vol": int}
    levels: Dict[float, Dict[str, int]] = field(default_factory=dict)
    poc_price: float = 0.0
    absorption_signals: List[str] = field(default_factory=list)
    imbalances: List[Dict[str, Any]] = field(default_factory=list)

class OrderFlowEngine:
    """
    Real-time & historical order flow engine for S&P 500 (/ES) futures.
    Computes footprint clusters, CVD, delta imbalances, and absorption signals.
    """
    def __init__(self, tick_size: float = 0.25, imbalance_ratio: float = 3.0):
        self.tick_size = tick_size
        self.imbalance_ratio = imbalance_ratio  # 300% volume imbalance threshold
        self.cvd = 0  # Cumulative Volume Delta
        self.cvd_history: List[Tuple[int, int]] = []  # [(timestamp_ns, cvd)]

    def round_to_tick(self, price: float) -> float:
        """Rounds price to nearest instrument tick size (e.g. 0.25 for /ES)."""
        return round(round(price / self.tick_size) * self.tick_size, 4)

    def aggregate_footprint(
        self,
        ticks: List[OrderFlowTick],
        bar_duration_ns: int = 300_000_000_000  # 5 minutes in nanoseconds
    ) -> List[FootprintBar]:
        """Aggregates a stream of raw ticks into discrete Footprint bars."""
        if not ticks:
            return []

        bars: List[FootprintBar] = []
        current_bar: Optional[FootprintBar] = None
        current_bar_start = ticks[0].timestamp_ns

        for t in ticks:
            if current_bar is None or (t.timestamp_ns - current_bar_start >= bar_duration_ns):
                if current_bar is not None:
                    self._finalize_bar(current_bar)
                    bars.append(current_bar)

                current_bar_start = (t.timestamp_ns // bar_duration_ns) * bar_duration_ns
                current_bar = FootprintBar(
                    start_time_ns=current_bar_start,
                    end_time_ns=current_bar_start + bar_duration_ns,
                    open=t.price,
                    high=t.price,
                    low=t.price,
                    close=t.price
                )

            # Update bar price action
            p_rounded = self.round_to_tick(t.price)
            current_bar.high = max(current_bar.high, p_rounded)
            current_bar.low = min(current_bar.low, p_rounded)
            current_bar.close = p_rounded
            current_bar.total_volume += t.volume

            # Track level volume
            if p_rounded not in current_bar.levels:
                current_bar.levels[p_rounded] = {"bid_vol": 0, "ask_vol": 0}

            if t.side > 0:
                current_bar.levels[p_rounded]["ask_vol"] += t.volume
                current_bar.buy_volume += t.volume
                current_bar.delta += t.volume
                self.cvd += t.volume
            else:
                current_bar.levels[p_rounded]["bid_vol"] += t.volume
                current_bar.sell_volume += t.volume
                current_bar.delta -= t.volume
                self.cvd -= t.volume

            self.cvd_history.append((t.timestamp_ns, self.cvd))

        if current_bar is not None and current_bar.total_volume > 0:
            self._finalize_bar(current_bar)
            bars.append(current_bar)

        return bars

    def _finalize_bar(self, bar: FootprintBar):
        """Calculates POC, imbalances, and absorption patterns for a finished footprint bar."""
        max_vol = -1
        poc = bar.close
        for price, data in bar.levels.items():
            level_vol = data["bid_vol"] + data["ask_vol"]
            if level_vol > max_vol:
                max_vol = level_vol
                poc = price
        bar.poc_price = poc

        # Detect Diagonal Imbalances
        bar.imbalances = self.detect_imbalances(bar)

        # Detect Passive Limit Order Absorption
        absorption = self.detect_absorption(bar)
        if absorption:
            bar.absorption_signals.append(absorption)

    def detect_imbalances(self, bar: FootprintBar) -> List[Dict[str, Any]]:
        """
        Calculates diagonal bid/ask volume imbalances.
        Buying Imbalance: Ask volume at P >= 3x Bid volume at (P - 1 tick).
        Selling Imbalance: Bid volume at P >= 3x Ask volume at (P + 1 tick).
        """
        imbalances = []
        prices = sorted(bar.levels.keys())
        min_vol_filter = 15  # Minimum volume filter to avoid dividing noise

        for p in prices:
            ask_vol = bar.levels[p]["ask_vol"]
            bid_vol = bar.levels[p]["bid_vol"]

            # Diagonal Buying Imbalance (Ask vs lower Bid)
            lower_price = self.round_to_tick(p - self.tick_size)
            if lower_price in bar.levels:
                lower_bid = bar.levels[lower_price]["bid_vol"]
                if lower_bid > 0 and ask_vol >= min_vol_filter:
                    ratio = ask_vol / lower_bid
                    if ratio >= self.imbalance_ratio:
                        imbalances.append({
                            "type": "buying_imbalance",
                            "price": p,
                            "volume": ask_vol,
                            "counter_volume": lower_bid,
                            "ratio": round(ratio, 2)
                        })

            # Diagonal Selling Imbalance (Bid vs higher Ask)
            higher_price = self.round_to_tick(p + self.tick_size)
            if higher_price in bar.levels:
                higher_ask = bar.levels[higher_price]["ask_vol"]
                if higher_ask > 0 and bid_vol >= min_vol_filter:
                    ratio = bid_vol / higher_ask
                    if ratio >= self.imbalance_ratio:
                        imbalances.append({
                            "type": "selling_imbalance",
                            "price": p,
                            "volume": bid_vol,
                            "counter_volume": higher_ask,
                            "ratio": round(ratio, 2)
                        })

        return imbalances

    def detect_absorption(self, bar: FootprintBar, min_extreme_vol: int = 100) -> Optional[str]:
        """
        Identifies institutional passive absorption at the bar extremes:
        - Bullish Absorption: High sell volume hitting the bid at the bar low,
          yet price closes near the high or above POC (passive limit buyers absorbed all selling).
        - Bearish Absorption: High buy volume hitting the ask at the bar high,
          yet price closes near the low or below POC (passive limit sellers absorbed all buying).
        """
        if not bar.levels or bar.total_volume < min_extreme_vol:
            return None

        # Check Bullish Absorption at Bar Low
        low_data = bar.levels.get(bar.low, {"bid_vol": 0, "ask_vol": 0})
        if low_data["bid_vol"] >= min_extreme_vol and bar.close > bar.low:
            if bar.close >= bar.poc_price:
                return "BULLISH_ABSORPTION"

        # Check Bearish Absorption at Bar High
        high_data = bar.levels.get(bar.high, {"bid_vol": 0, "ask_vol": 0})
        if high_data["ask_vol"] >= min_extreme_vol and bar.close < bar.high:
            if bar.close <= bar.poc_price:
                return "BEARISH_ABSORPTION"

        return None

    def detect_cvd_divergence(self, bars: List[FootprintBar], lookback: int = 4) -> Optional[str]:
        """
        Detects CVD (Cumulative Volume Delta) Divergence:
        - Bullish Divergence: Price creates Lower Low, but Delta/CVD creates Higher Low (seller exhaustion).
        - Bearish Divergence: Price creates Higher High, but Delta/CVD creates Lower High (buyer exhaustion).
        """
        if len(bars) < lookback:
            return None

        recent = bars[-lookback:]
        p_first, p_last = recent[0], recent[-1]

        # Price lower low, but cumulative delta significantly higher
        if p_last.low < p_first.low and p_last.delta > p_first.delta and p_last.delta > 0:
            return "BULLISH_CVD_DIVERGENCE"

        # Price higher high, but cumulative delta significantly lower
        if p_last.high > p_first.high and p_last.delta < p_first.delta and p_last.delta < 0:
            return "BEARISH_CVD_DIVERGENCE"

        return None
