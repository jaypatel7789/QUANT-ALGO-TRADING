"""
Options Dealer Gamma Exposure (GEX) & 0DTE Magnetism Engine (Phase 3)
Calculates:
- Dollar Gamma Exposure per strike (Call GEX & Put GEX)
- Total Net GEX across the S&P 500 options chain
- Zero Gamma Flip Price Level (boundary between mean-reversion and momentum expansion)
- Major Call Wall (upper magnet/pin) & Put Wall (downside magnet/pin)
- Volatility Regime classification: Positive Gamma (Fade/Mean-Reversion) vs Negative Gamma (Breakout)
"""
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class OptionContract:
    strike: float
    option_type: str  # 'C' or 'P'
    open_interest: int
    gamma: float
    iv: float = 0.15
    dte: float = 0.0  # 0 for 0DTE contracts

@dataclass
class GammaProfile:
    spot_price: float
    net_gex_dollars: float
    zero_gamma_level: float
    call_wall_strike: float
    put_wall_strike: float
    regime: str  # "POSITIVE_GAMMA_MEAN_REVERSION" or "NEGATIVE_GAMMA_EXPANSION"
    gamma_by_strike: Dict[float, float] = field(default_factory=dict)
    volatility_expectation: str = "LOW_VOL_COMPRESSION"

class GammaEngine:
    """
    Computes institutional dealer gamma positioning for S&P 500 options.
    """
    def __init__(self, contract_multiplier: int = 100):
        self.multiplier = contract_multiplier

    def calculate_gex(
        self,
        contracts: List[OptionContract],
        spot_price: float
    ) -> GammaProfile:
        """
        Calculates Net Dealer Gamma across the options surface.
        Dealer call gamma contributes positively; dealer put gamma contributes negatively.
        """
        if not contracts or spot_price <= 0:
            return GammaProfile(
                spot_price=spot_price,
                net_gex_dollars=0.0,
                zero_gamma_level=spot_price,
                call_wall_strike=spot_price,
                put_wall_strike=spot_price,
                regime="NEUTRAL"
            )

        gex_by_strike: Dict[float, float] = {}
        call_gex_by_strike: Dict[float, float] = {}
        put_gex_by_strike: Dict[float, float] = {}

        total_net_gex = 0.0

        for c in contracts:
            # GEX in Dollar Gamma per 1% move:
            # Dollar GEX = OI * 100 * Gamma * (Spot^2) * 0.01
            dollar_gamma = c.open_interest * self.multiplier * c.gamma * (spot_price ** 2) * 0.01

            if c.strike not in gex_by_strike:
                gex_by_strike[c.strike] = 0.0
                call_gex_by_strike[c.strike] = 0.0
                put_gex_by_strike[c.strike] = 0.0

            if c.option_type.upper() == 'C':
                call_gex_by_strike[c.strike] += dollar_gamma
                gex_by_strike[c.strike] += dollar_gamma
                total_net_gex += dollar_gamma
            else:
                put_gex_by_strike[c.strike] += dollar_gamma
                gex_by_strike[c.strike] -= dollar_gamma
                total_net_gex -= dollar_gamma

        # Identify Major Walls
        call_wall = max(call_gex_by_strike.keys(), key=lambda k: call_gex_by_strike[k]) if call_gex_by_strike else spot_price
        put_wall = max(put_gex_by_strike.keys(), key=lambda k: put_gex_by_strike[k]) if put_gex_by_strike else spot_price

        # Approximate Zero Gamma Flip Level
        zero_gamma = self._locate_zero_gamma(gex_by_strike, spot_price)

        # Classify Regime
        if total_net_gex >= 0:
            regime = "POSITIVE_GAMMA_MEAN_REVERSION"
            vol_exp = "LOW_VOL_COMPRESSION"
        else:
            regime = "NEGATIVE_GAMMA_EXPANSION"
            vol_exp = "HIGH_VOL_MOMENTUM"

        return GammaProfile(
            spot_price=spot_price,
            net_gex_dollars=round(total_net_gex, 2),
            zero_gamma_level=round(zero_gamma, 2),
            call_wall_strike=call_wall,
            put_wall_strike=put_wall,
            regime=regime,
            gamma_by_strike=gex_by_strike,
            volatility_expectation=vol_exp
        )

    def _locate_zero_gamma(self, gex_by_strike: Dict[float, float], fallback: float) -> float:
        """Finds the price where cumulative Net Gamma flips sign."""
        sorted_strikes = sorted(gex_by_strike.keys())
        if len(sorted_strikes) < 2:
            return fallback

        for i in range(len(sorted_strikes) - 1):
            s1, s2 = sorted_strikes[i], sorted_strikes[i + 1]
            g1, g2 = gex_by_strike[s1], gex_by_strike[s2]
            if (g1 <= 0 and g2 > 0) or (g1 >= 0 and g2 < 0):
                # Linear interpolation
                if (g2 - g1) != 0:
                    fraction = abs(g1) / abs(g2 - g1)
                    return s1 + fraction * (s2 - s1)
                return (s1 + s2) / 2.0

        return fallback

    def get_trading_bias(self, profile: GammaProfile, current_price: float) -> Dict[str, Any]:
        """Provides structural guidance based on current spot vs GEX walls."""
        if profile.regime == "POSITIVE_GAMMA_MEAN_REVERSION":
            # Dealer hedging dampens volatility
            if current_price >= profile.call_wall_strike - 2.0:
                return {
                    "bias": "SHORT_MEAN_REVERSION",
                    "reason": "Approaching Major Call Wall in Positive Gamma regime (dealer selling resistance)",
                    "target": profile.zero_gamma_level,
                    "confidence": 0.72
                }
            elif current_price <= profile.put_wall_strike + 2.0:
                return {
                    "bias": "LONG_MEAN_REVERSION",
                    "reason": "Approaching Major Put Wall in Positive Gamma regime (dealer buying support)",
                    "target": profile.zero_gamma_level,
                    "confidence": 0.75
                }
            else:
                return {
                    "bias": "RANGE_FADE",
                    "reason": "Inside Positive Gamma pocket, fade extremes back to POC/Zero Gamma",
                    "target": profile.zero_gamma_level,
                    "confidence": 0.68
                }
        else:
            # Negative Gamma: dealer hedging accelerates moves
            return {
                "bias": "MOMENTUM_BREAKOUT",
                "reason": "Negative Gamma regime: dealer hedging accelerates market moves. Fading is high risk.",
                "target": profile.put_wall_strike if current_price < profile.zero_gamma_level else profile.call_wall_strike,
                "confidence": 0.70
            }
