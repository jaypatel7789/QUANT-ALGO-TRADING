"""
Unit Tests for Quantitative Backtester & Indicators (Phase 8)
Using Python standard library unittest.
"""
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.skills.algo_trading_skill import AlgoTradingSkill

class TestAlgoTradingSkill(unittest.TestCase):
    def setUp(self):
        self.algo = AlgoTradingSkill()

    def test_indicators_calculation(self):
        prices = [100.0 + i for i in range(30)]
        res = self.algo.calculate_indicators(prices)
        self.assertIn("sma_20", res)
        self.assertIn("ema_20", res)
        self.assertIn("rsi_14", res)
        self.assertEqual(res["trend"], "Bullish")

    def test_edge_case_empty_and_short_series(self):
        # Empty
        res_empty = self.algo.backtest_strategy([])
        self.assertFalse(res_empty["success"])

        # Short series
        res_short = self.algo.backtest_strategy([100.0, 101.0, 102.0], slow_period=20)
        self.assertFalse(res_short["success"])
        self.assertEqual(res_short["total_trades"], 0)

    def test_edge_case_zero_variance_flat_series(self):
        # Flat series: no trades, no crash
        flat_prices = [100.0] * 50
        res = self.algo.backtest_strategy(flat_prices, fast_period=5, slow_period=20)
        self.assertTrue(res["success"])
        self.assertEqual(res["total_trades"], 0)
        self.assertEqual(res["total_pnl"], 0.0)
        self.assertEqual(res["sharpe_ratio"], 0.0)

    def test_fees_and_slippage_impact(self):
        # Trending prices that generate trades
        prices = [100.0, 101.0, 99.0, 98.0, 105.0, 110.0, 115.0, 120.0, 118.0, 110.0, 105.0] * 5

        res_frictionless = self.algo.backtest_strategy(prices, fee_pct=0.0, slippage_pct=0.0)
        res_with_friction = self.algo.backtest_strategy(prices, fee_pct=0.002, slippage_pct=0.001)

        # Net profit with fees and slippage must be lower than frictionless
        if res_frictionless["total_trades"] > 0:
            self.assertLess(res_with_friction["final_equity"], res_frictionless["final_equity"])

    def test_max_drawdown_calculation(self):
        # Deterministic series with a known 50% drop
        prices = [100.0] * 20 + [200.0] * 5 + [100.0] * 5
        res = self.algo.backtest_strategy(prices, fast_period=5, slow_period=10)
        # Should record drawdown
        self.assertGreater(res["max_drawdown_pct"], 0.0)

    def test_reproducible_hash_and_metadata(self):
        prices = [100.0 + (i % 7) for i in range(40)]
        res1 = self.algo.backtest_strategy(prices)
        res2 = self.algo.backtest_strategy(prices)
        self.assertEqual(res1["dataset_hash"], res2["dataset_hash"])
        self.assertEqual(res1["sharpe_ratio"], res2["sharpe_ratio"])

if __name__ == "__main__":
    unittest.main()
