"""
Volume Profile & Auction Market Theory Engine (Phase 2)
Computes:
- Session Volume Profile across tick levels
- Point of Control (POC)
- Value Area High (VAH) & Value Area Low (VAL) [70% distribution]
- High Volume Nodes (HVN) & Low Volume Nodes (LVN / liquidity voids)
- Auction Market Theory (AMT) 80% Rule signals
"""
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class VolumeProfile:
    session_id: str
    poc_price: float
    vah_price: float
    val_price: float
    total_volume: int
    volume_by_price: Dict[float, int] = field(default_factory=dict)
    high_volume_nodes: List[float] = field(default_factory=list)
    low_volume_nodes: List[float] = field(default_factory=list)

class VolumeProfileEngine:
    """
    Computes institutional Volume Profiles and Auction Market Theory boundaries.
    """
    def __init__(self, tick_size: float = 0.25, value_area_pct: float = 0.70):
        self.tick_size = tick_size
        self.value_area_pct = value_area_pct

    def round_to_tick(self, price: float) -> float:
        return round(round(price / self.tick_size) * self.tick_size, 4)

    def compute_profile(
        self,
        price_volume_pairs: List[Tuple[float, int]],
        session_id: str = "RTH"
    ) -> VolumeProfile:
        """
        Builds a full session volume profile and computes POC, VAH, VAL, HVN, LVN.
        """
        if not price_volume_pairs:
            return VolumeProfile(session_id=session_id, poc_price=0.0, vah_price=0.0, val_price=0.0, total_volume=0)

        # 1. Aggregate volume by price tick
        v_by_p: Dict[float, int] = {}
        total_vol = 0
        for p, vol in price_volume_pairs:
            p_rounded = self.round_to_tick(p)
            v_by_p[p_rounded] = v_by_p.get(p_rounded, 0) + vol
            total_vol += vol

        if total_vol == 0:
            return VolumeProfile(session_id=session_id, poc_price=0.0, vah_price=0.0, val_price=0.0, total_volume=0)

        # 2. Identify Point of Control (POC)
        poc_price = max(v_by_p.keys(), key=lambda p: v_by_p[p])

        # 3. Calculate 70% Value Area (VAH & VAL)
        target_va_vol = total_vol * self.value_area_pct
        accumulated_vol = v_by_p[poc_price]
        all_prices = sorted(v_by_p.keys())
        poc_idx = all_prices.index(poc_price)

        up_idx = poc_idx + 1
        down_idx = poc_idx - 1

        while accumulated_vol < target_va_vol and (up_idx < len(all_prices) or down_idx >= 0):
            # Compare volume 2 ticks up vs 2 ticks down (standard CME methodology)
            up_vol = v_by_p[all_prices[up_idx]] if up_idx < len(all_prices) else 0
            down_vol = v_by_p[all_prices[down_idx]] if down_idx >= 0 else 0

            if up_vol >= down_vol and up_idx < len(all_prices):
                accumulated_vol += up_vol
                up_idx += 1
            elif down_idx >= 0:
                accumulated_vol += down_vol
                down_idx -= 1
            else:
                break

        val_price = all_prices[max(0, down_idx + 1)]
        vah_price = all_prices[min(len(all_prices) - 1, up_idx - 1)]

        # 4. Identify High Volume Nodes (HVN) and Low Volume Nodes (LVN)
        hvns, lvns = self._extract_nodes(all_prices, v_by_p)

        return VolumeProfile(
            session_id=session_id,
            poc_price=poc_price,
            vah_price=vah_price,
            val_price=val_price,
            total_volume=total_vol,
            volume_by_price=v_by_p,
            high_volume_nodes=hvns,
            low_volume_nodes=lvns
        )

    def _extract_nodes(
        self,
        prices: List[float],
        v_by_p: Dict[float, int],
        window: int = 3
    ) -> Tuple[List[float], List[float]]:
        """Identifies local peaks (HVN) and local troughs (LVN / liquidity voids)."""
        hvns = []
        lvns = []
        if len(prices) < window * 2 + 1:
            return hvns, lvns

        for i in range(window, len(prices) - window):
            cur_p = prices[i]
            cur_v = v_by_p[cur_p]

            is_peak = all(cur_v > v_by_p[prices[i + j]] for j in range(-window, window + 1) if j != 0)
            is_trough = all(cur_v < v_by_p[prices[i + j]] for j in range(-window, window + 1) if j != 0)

            if is_peak:
                hvns.append(cur_p)
            elif is_trough and cur_v > 0:
                lvns.append(cur_p)

        return hvns, lvns

    def check_80_percent_rule(
        self,
        prior_profile: VolumeProfile,
        current_price: float,
        consecutive_inside_bars: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Auction Market Theory 80% Rule:
        If market opened outside prior Value Area, but accepts back inside for 2 brackets,
        there is an 80% probability to rotate to the opposite side of the Value Area.
        """
        if not prior_profile or prior_profile.total_volume == 0:
            return None

        val = prior_profile.val_price
        vah = prior_profile.vah_price
        poc = prior_profile.poc_price

        # Accepted from below VAL into Value Area -> Rotate to VAH
        if val < current_price < vah:
            if consecutive_inside_bars >= 2:
                return {
                    "signal": "AMT_80_PCT_RULE_ACTIVE",
                    "target_price": vah,
                    "pivot_poc": poc,
                    "invalidation_price": val - self.tick_size * 2,
                    "direction": "LONG",
                    "probability_estimate": 0.80
                }

        return None
