"""
Institutional Quantitative Algorithmic Trading Core Engine
Provides high-frequency order flow analytics, volume profile decomposition,
options dealer gamma hedging analysis, automated MetaTrader 5 live execution,
and multi-timeframe backtesting research pipelines.
"""

from .trading.order_flow_engine import OrderFlowEngine, FootprintBar, OrderFlowTick
from .trading.volume_profile_engine import VolumeProfileEngine, VolumeProfile
from .trading.gamma_engine import GammaEngine, GammaProfile
from .trading.institutional_backtester import InstitutionalBacktester, SimulatedTrade, BacktestReport
from .trading.strategy_orchestrator import InstitutionalStrategyOrchestrator

__version__ = "1.0.0"
__all__ = [
    "OrderFlowEngine",
    "FootprintBar",
    "OrderFlowTick",
    "VolumeProfileEngine",
    "VolumeProfile",
    "GammaEngine",
    "GammaProfile",
    "InstitutionalBacktester",
    "SimulatedTrade",
    "BacktestReport",
    "InstitutionalStrategyOrchestrator",
]
