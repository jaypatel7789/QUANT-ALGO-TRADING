"""
Unit Tests for Institutional Trading Engines & S&P 500 Strategy Orchestrator
Tests:
- OrderFlowEngine: Footprint, POC, Delta imbalances, Passive absorption, CVD divergence
- VolumeProfileEngine: POC, 70% Value Area (VAH/VAL), HVN/LVN, 80% Rule
- GammaEngine: Dealer GEX, Zero Gamma Flip, Call/Put Walls, Regime classification
- InstitutionalBacktester: FIFO queue simulation, slippage, commission, risk metrics
- StrategyOrchestrator: Multi-edge convergence signal generation & simulation
"""
import unittest
import time
from core.trading import (
    OrderFlowEngine,
    FootprintBar,
    OrderFlowTick,
    VolumeProfileEngine,
    VolumeProfile,
    GammaEngine,
    GammaProfile,
    InstitutionalBacktester,
    InstitutionalStrategyOrchestrator
)
from core.trading.gamma_engine import OptionContract

class TestInstitutionalTrading(unittest.TestCase):
    def setUp(self):
        self.of_engine = OrderFlowEngine(tick_size=0.25, imbalance_ratio=3.0)
        self.vp_engine = VolumeProfileEngine(tick_size=0.25, value_area_pct=0.70)
        self.gamma_engine = GammaEngine(contract_multiplier=100)
        self.orchestrator = InstitutionalStrategyOrchestrator(instrument="/ES")

    # =========================================================================
    # 1. Order Flow Tests
    # =========================================================================
    def test_footprint_aggregation_and_poc(self):
        base_time = 1_700_000_000_000_000_000
        ticks = [
            OrderFlowTick(base_time + 10, 5000.0, 50, +1),
            OrderFlowTick(base_time + 20, 5000.25, 200, +1), # POC level
            OrderFlowTick(base_time + 30, 5000.25, 100, -1),
            OrderFlowTick(base_time + 40, 5000.5, 30, +1),
        ]
        bars = self.of_engine.aggregate_footprint(ticks, bar_duration_ns=60_000_000_000)
        self.assertEqual(len(bars), 1)
        bar = bars[0]
        self.assertEqual(bar.poc_price, 5000.25)
        self.assertEqual(bar.total_volume, 380)
        self.assertEqual(bar.delta, 50 + 200 - 100 + 30)

    def test_diagonal_bid_ask_imbalances(self):
        bar = FootprintBar(
            start_time_ns=0, end_time_ns=60_000_000_000,
            open=5000.0, high=5000.5, low=5000.0, close=5000.5
        )
        # Price 5000.0 has 10 bid vol
        bar.levels[5000.0] = {"bid_vol": 10, "ask_vol": 5}
        # Price 5000.25 has 40 ask vol (40 / 10 = 4.0x ratio >= 3.0 threshold -> Buying Imbalance)
        bar.levels[5000.25] = {"bid_vol": 5, "ask_vol": 40}

        imbalances = self.of_engine.detect_imbalances(bar)
        self.assertTrue(any(imb["type"] == "buying_imbalance" and imb["price"] == 5000.25 for imb in imbalances))

    def test_bullish_absorption_detection(self):
        # Heavy sell volume at low, but price closes at high above POC
        bar = FootprintBar(
            start_time_ns=0, end_time_ns=60_000_000_000,
            open=5002.0, high=5004.0, low=5000.0, close=5003.5,
            total_volume=500
        )
        bar.levels[5000.0] = {"bid_vol": 250, "ask_vol": 10}  # Large bid sell volume absorbed
        bar.levels[5002.0] = {"bid_vol": 50, "ask_vol": 50}
        bar.poc_price = 5002.0

        signal = self.of_engine.detect_absorption(bar, min_extreme_vol=100)
        self.assertEqual(signal, "BULLISH_ABSORPTION")

    # =========================================================================
    # 2. Volume Profile Tests
    # =========================================================================
    def test_volume_profile_value_area(self):
        # Create bell-shaped distribution around 5000.0
        pv_pairs = [
            (4995.0, 50),
            (4998.0, 200),
            (5000.0, 1000),  # POC
            (5002.0, 300),
            (5005.0, 80),
        ]
        profile = self.vp_engine.compute_profile(pv_pairs)
        self.assertEqual(profile.poc_price, 5000.0)
        self.assertLessEqual(profile.val_price, 5000.0)
        self.assertGreaterEqual(profile.vah_price, 5000.0)
        self.assertEqual(profile.total_volume, 1630)

    def test_auction_market_80_percent_rule(self):
        prior_vp = VolumeProfile(
            session_id="DAY1",
            poc_price=5000.0,
            vah_price=5010.0,
            val_price=4990.0,
            total_volume=10000
        )
        # Opened below VAL, now trading inside value area at 4995.0
        signal = self.vp_engine.check_80_percent_rule(prior_vp, current_price=4995.0, consecutive_inside_bars=2)
        self.assertIsNotNone(signal)
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["target_price"], 5010.0)

    # =========================================================================
    # 3. Options Dealer Gamma (GEX) Tests
    # =========================================================================
    def test_dealer_gamma_regime_and_walls(self):
        spot = 5000.0
        contracts = [
            # Call Wall at 5050
            OptionContract(strike=5050.0, option_type="C", open_interest=10000, gamma=0.005),
            # Put Wall at 4950
            OptionContract(strike=4950.0, option_type="P", open_interest=8000, gamma=0.004),
            # ATM Call at 5000
            OptionContract(strike=5000.0, option_type="C", open_interest=5000, gamma=0.010),
        ]
        profile = self.gamma_engine.calculate_gex(contracts, spot_price=spot)
        self.assertEqual(profile.call_wall_strike, 5050.0)
        self.assertEqual(profile.put_wall_strike, 4950.0)
        self.assertGreater(profile.net_gex_dollars, 0)
        self.assertEqual(profile.regime, "POSITIVE_GAMMA_MEAN_REVERSION")

    # =========================================================================
    # 4. Institutional Backtester FIFO Queue & Slippage Tests
    # =========================================================================
    def test_fifo_queue_fill_simulation(self):
        bt = InstitutionalBacktester(instrument="/ES", initial_capital=50000.0, tick_size=0.25)
        # Submit limit buy at 5000.0 with 100 contracts resting ahead in queue
        bt.submit_limit_order("BUY", price=5000.0, resting_depth_estimate=100, stop_loss=4995.0, take_profit=5010.0)

        # 1. Trade at 5000.0 with 60 volume (aggressive sells) -> Not filled yet (40 ahead)
        bt.process_tick(timestamp_ns=100, price=5000.0, volume=60, side=-1)
        self.assertIsNone(bt.open_position)

        # 2. Trade at 5000.0 with 50 volume -> Queue cleared -> Position filled!
        bt.process_tick(timestamp_ns=200, price=5000.0, volume=50, side=-1)
        self.assertIsNotNone(bt.open_position)
        self.assertEqual(bt.open_position["entry_price"], 5000.0)

        # 3. Price rallies to 5010.0 -> Take Profit reached!
        bt.process_tick(timestamp_ns=300, price=5010.0, volume=10, side=+1)
        self.assertIsNone(bt.open_position)
        self.assertEqual(len(bt.closed_trades), 1)

        trade = bt.closed_trades[0]
        # 10 points * $50 = $500 gross; minus $3.70 commission = $496.30 net
        self.assertAlmostEqual(trade.gross_pnl, 500.0, places=1)
        self.assertAlmostEqual(trade.net_pnl, 496.30, places=1)

    def test_stop_loss_slippage_applied(self):
        bt = InstitutionalBacktester(instrument="/ES", slippage_ticks=1, tick_size=0.25)
        # Directly open position for test
        ord = bt.submit_limit_order("BUY", price=5000.0, resting_depth_estimate=0, stop_loss=4995.0)
        bt.process_tick(timestamp_ns=10, price=4999.0, volume=1, side=-1) # triggers instant fill

        # Price drops to stop loss 4995.0
        bt.process_tick(timestamp_ns=20, price=4995.0, volume=10, side=-1)
        self.assertEqual(len(bt.closed_trades), 1)
        trade = bt.closed_trades[0]
        self.assertEqual(trade.exit_reason, "STOP_LOSS")
        # 1 tick adverse slippage = exited at 4994.75 instead of 4995.0
        self.assertEqual(trade.exit_price, 4994.75)
        self.assertEqual(trade.slippage_cost, 12.50)

    # =========================================================================
    # 5. Multi-Edge Convergence Orchestrator Tests
    # =========================================================================
    def test_convergence_signal_evaluation(self):
        prior_vp = VolumeProfile(
            session_id="PRIOR", poc_price=5000.0, vah_price=5015.0, val_price=4985.0, total_volume=5000
        )
        gamma = GammaProfile(
            spot_price=4985.0, net_gex_dollars=1_500_000.0, zero_gamma_level=4970.0,
            call_wall_strike=5050.0, put_wall_strike=4950.0, regime="POSITIVE_GAMMA_MEAN_REVERSION"
        )
        # Bar at VAL with Bullish Absorption
        bar = FootprintBar(
            start_time_ns=0, end_time_ns=60_000_000_000,
            open=4987.0, high=4989.0, low=4985.0, close=4988.0,
            absorption_signals=["BULLISH_ABSORPTION"]
        )

        signal = self.orchestrator.evaluate_convergence(
            current_price=4985.5,
            current_bar=bar,
            gamma_profile=gamma,
            prior_volume_profile=prior_vp
        )
        self.assertIsNotNone(signal)
        self.assertEqual(signal.direction, "BUY")
        self.assertEqual(signal.setup_name, "POSITIVE_GAMMA_VAL_ABSORPTION_FADE")
        self.assertGreaterEqual(signal.confidence, 0.70)
        self.assertEqual(signal.take_profit, 5000.0) # Targets POC

if __name__ == "__main__":
    unittest.main()
