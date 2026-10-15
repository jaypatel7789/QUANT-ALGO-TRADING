"""
Binance Futures Public Ingestion Engine (Institutional Orderflow & Derivatives Alpha)
Fetches real-time and historical:
1. Perpetual Funding Rates (8h / 1h)
2. Global Open Interest (Aggregated BTC/USDT)
3. Top-of-Book Depth & Bid-Ask Queue Skew
Zero API Key / Zero Cost / No Authentication Required.
"""

import json
import ssl
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

DATA_DIR = Path("F:/multi agent/data/binance_futures")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class BinanceFuturesEngine:
    BASE_URL = "https://fapi.binance.com"

    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def _http_get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        query = ""
        if params:
            query = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.BASE_URL}{endpoint}{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) InstitutionalQuant/1.0"})
        with urllib.request.urlopen(req, timeout=10, context=self.ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_funding_rates(self, symbol: str = "BTCUSDT", limit: int = 1000) -> pd.DataFrame:
        """Fetches historical 8-hour funding rate prints for BTCUSDT."""
        cache_file = DATA_DIR / f"funding_rates_{symbol}.csv"
        try:
            raw = self._http_get("/fapi/v1/fundingRate", {"symbol": symbol, "limit": limit})
            df = pd.DataFrame(raw)
            if not df.empty:
                df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms", utc=True)
                df["fundingRate"] = df["fundingRate"].astype(float)
                df.sort_values("fundingTime", inplace=True)
                df.to_csv(cache_file, index=False)
                return df
        except Exception as e:
            print(f"[!] Warning: Failed to fetch live funding rates: {e}")
            if cache_file.exists():
                return pd.read_csv(cache_file)
        return pd.DataFrame()

    def fetch_open_interest_history(self, symbol: str = "BTCUSDT", period: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Fetches historical Open Interest aggregates (15m, 1h, 4h, 1d)."""
        cache_file = DATA_DIR / f"open_interest_{symbol}_{period}.csv"
        try:
            raw = self._http_get("/futures/data/openInterestHist", {"symbol": symbol, "period": period, "limit": limit})
            df = pd.DataFrame(raw)
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                df["sumOpenInterest"] = df["sumOpenInterest"].astype(float)
                df["sumOpenInterestValue"] = df["sumOpenInterestValue"].astype(float)
                df.sort_values("timestamp", inplace=True)
                df.to_csv(cache_file, index=False)
                return df
        except Exception as e:
            print(f"[!] Warning: Failed to fetch live open interest: {e}")
            if cache_file.exists():
                return pd.read_csv(cache_file)
        return pd.DataFrame()

    def fetch_orderbook_depth(self, symbol: str = "BTCUSDT", limit: int = 100) -> Dict[str, Any]:
        """Fetches current L2 orderbook snapshot and computes bid/ask depth skew."""
        try:
            depth = self._http_get("/fapi/v1/depth", {"symbol": symbol, "limit": limit})
            bids = np.array([[float(p[0]), float(p[1])] for p in depth.get("bids", [])])
            asks = np.array([[float(p[0]), float(p[1])] for p in depth.get("asks", [])])
            
            total_bid_vol = bids[:, 1].sum() if len(bids) > 0 else 0.0
            total_ask_vol = asks[:, 1].sum() if len(asks) > 0 else 0.0
            depth_imbalance = (total_bid_vol - total_ask_vol) / (total_bid_vol + total_ask_vol + 1e-9)

            return {
                "best_bid": bids[0, 0] if len(bids) > 0 else 0.0,
                "best_ask": asks[0, 0] if len(asks) > 0 else 0.0,
                "total_bid_vol": total_bid_vol,
                "total_ask_vol": total_ask_vol,
                "depth_imbalance": depth_imbalance,
                "timestamp": depth.get("T", int(time.time() * 1000))
            }
        except Exception as e:
            print(f"[!] Warning: Failed to fetch depth: {e}")
            return {"best_bid": 0.0, "best_ask": 0.0, "depth_imbalance": 0.0}

    def compute_regime_analytics(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Synthesizes funding rates, open interest changes, and orderbook skew into macro alpha signals."""
        fr_df = self.fetch_funding_rates(symbol, limit=100)
        oi_df = self.fetch_open_interest_history(symbol, period="1h", limit=100)
        depth = self.fetch_orderbook_depth(symbol, limit=100)

        current_fr = fr_df["fundingRate"].iloc[-1] if not fr_df.empty else 0.0001
        mean_fr = fr_df["fundingRate"].mean() if not fr_df.empty else 0.0001
        std_fr = fr_df["fundingRate"].std() + 1e-9 if not fr_df.empty else 0.0001
        fr_zscore = (current_fr - mean_fr) / std_fr

        current_oi = oi_df["sumOpenInterest"].iloc[-1] if not oi_df.empty else 100000.0
        prev_oi = oi_df["sumOpenInterest"].iloc[-2] if len(oi_df) > 1 else current_oi
        oi_delta_pct = ((current_oi - prev_oi) / prev_oi) * 100.0

        # Institutional Regime Detection
        # Negative FR + Rising OI = Short Squeeze Accumulation (High-probability long impulse)
        # Extremely High FR (> 0.04%) = Overcrowded Longs (High probability long liquidation flush)
        if current_fr < -0.0001 and oi_delta_pct > 0.5:
            regime = "SHORT_SQUEEZE_ACCUMULATION"
            bias = "BULLISH_IMPULSE"
        elif current_fr > 0.0004:
            regime = "LONG_LIQUIDATION_OVERHANG"
            bias = "BEARISH_EXHAUSTION"
        elif depth["depth_imbalance"] > 0.20:
            regime = "BID_SIDE_ABSORPTION"
            bias = "BULLISH_SUPPORT"
        elif depth["depth_imbalance"] < -0.20:
            regime = "ASK_SIDE_LIQUIDITY_WALL"
            bias = "BEARISH_RESISTANCE"
        else:
            regime = "BALANCED_ORDER_FLOW"
            bias = "NEUTRAL_COHERENCE"

        return {
            "symbol": symbol,
            "current_funding_rate": current_fr,
            "annualized_funding_pct": current_fr * 3 * 365 * 100.0,
            "funding_zscore": fr_zscore,
            "open_interest_btc": current_oi,
            "open_interest_delta_pct": oi_delta_pct,
            "depth_imbalance": depth["depth_imbalance"],
            "regime": regime,
            "directional_bias": bias,
            "timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat()
        }

if __name__ == "__main__":
    engine = BinanceFuturesEngine()
    analytics = engine.compute_regime_analytics("BTCUSDT")
    print("=" * 60)
    print("  BINANCE FUTURES INSTITUTIONAL ORDER FLOW ANALYTICS")
    print("=" * 60)
    for k, v in analytics.items():
        if isinstance(v, float):
            print(f"  {k:30}: {v:+.4f}")
        else:
            print(f"  {k:30}: {v}")
    print("=" * 60)
