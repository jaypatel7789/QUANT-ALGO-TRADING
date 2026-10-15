"""
MetaTrader 5 Live BTC/USD Algorithmic Trading Bot
Executes the Adaptive Trend-Following Strategy (EMA 21/55 + RSI + ATR Trailing Stop)
directly on the active MetaTrader 5 terminal.

Broker: XMGlobal-MT5 6 (Interbank Feed)
Symbol: BTCUSD#
"""
import os
import sys
import time
import math
from datetime import datetime, timezone
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

# Fix Windows stdout encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configuration
TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
SYMBOL = "BTCUSD#"
TIMEFRAME = mt5.TIMEFRAME_H4  # 4-Hour timeframe
MAGIC_NUMBER = 20260925       # Unique ID for bot orders

FAST_EMA = 20
SLOW_EMA = 50
TREND_EMA = 200
RSI_PERIOD = 14
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.5
MAX_LOT_SIZE = 0.05
DEFAULT_LOT_SIZE = 0.01

DRY_RUN = True  # Set to False to enable real live order execution on MT5

def connect_mt5():
    """Initializes connection to MT5 terminal."""
    if not mt5.initialize(TERMINAL_PATH):
        print(f"[!] MT5 initialization failed: {mt5.last_error()}")
        return False
    
    account = mt5.account_info()
    if account is None:
        print("[!] Failed to retrieve MT5 account info.")
        return False

    print(f"[✓] Connected to MT5 Server: {account.server}")
    print(f"    Account: {account.login} | Balance: ${account.balance:,.2f} {account.currency} | Equity: ${account.equity:,.2f}")
    
    # Ensure symbol is active
    if not mt5.symbol_select(SYMBOL, True):
        print(f"[!] Failed to select symbol {SYMBOL}")
        return False

    return True

def fetch_indicator_data():
    """Fetches recent bars and calculates EMA, RSI, and ATR."""
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 250)
    if rates is None or len(rates) < 220:
        print("[!] Insufficient bars for indicator calculation.")
        return None

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    
    # EMAs
    df["ema_fast"] = df["close"].ewm(span=FAST_EMA, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=SLOW_EMA, adjust=False).mean()
    df["ema_trend"] = df["close"].ewm(span=TREND_EMA, adjust=False).mean()

    # True Range & ATR
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["close"].shift(1)).abs()
    tr3 = (df["low"] - df["close"].shift(1)).abs()
    df["tr"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr"] = df["tr"].rolling(ATR_PERIOD).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
    rs = gain / (loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

def get_open_positions():
    """Returns open positions for this symbol and magic number."""
    positions = mt5.positions_get(symbol=SYMBOL)
    if positions is None:
        return []
    return [p for p in positions if p.magic == MAGIC_NUMBER]

def open_buy_order(lot_size, stop_loss_price):
    """Sends a Buy Market order to MT5."""
    tick = mt5.symbol_info_tick(SYMBOL)
    if not tick:
        print("[!] Failed to get current tick for order.")
        return False

    price = tick.ask
    deviation = 20

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": float(lot_size),
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": float(stop_loss_price),
        "tp": 0.0,
        "deviation": deviation,
        "magic": MAGIC_NUMBER,
        "comment": "BTC_Trend_Bot_V1",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if DRY_RUN:
        print(f"[DRY RUN] Would execute BUY {lot_size} lots {SYMBOL} @ ${price:,.2f} with SL=${stop_loss_price:,.2f}")
        return True

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[!] Order failed: {result.comment} (code {result.retcode})")
        return False

    print(f"[✓] BUY order executed: Ticket #{result.order}, Volume: {lot_size}, Price: ${result.price:,.2f}")
    return True

def close_position(ticket, volume):
    """Closes an open position."""
    tick = mt5.symbol_info_tick(SYMBOL)
    if not tick:
        return False

    price = tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_SELL,
        "position": ticket,
        "price": price,
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "BTC_Trend_Exit",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if DRY_RUN:
        print(f"[DRY RUN] Would close position #{ticket} of {volume} lots @ ${price:,.2f}")
        return True

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[!] Close failed: {result.comment} (code {result.retcode})")
        return False

    print(f"[✓] Position #{ticket} closed at ${result.price:,.2f}")
    return True

def run_strategy_cycle():
    """Evaluates indicators and executes strategy logic."""
    df = fetch_indicator_data()
    if df is None:
        return

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    price = latest["close"]
    fast = latest["ema_fast"]
    slow = latest["ema_slow"]
    trend = latest["ema_trend"]
    atr = latest["atr"]
    rsi = latest["rsi"]

    tick = mt5.symbol_info_tick(SYMBOL)
    current_bid = tick.bid if tick else price
    current_ask = tick.ask if tick else price

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {SYMBOL} Market Analysis:")
    print(f"  Live Bid: ${current_bid:,.2f} | Ask: ${current_ask:,.2f}")
    print(f"  Fast EMA (20): ${fast:,.2f} | Slow EMA (50): ${slow:,.2f} | Trend EMA (200): ${trend:,.2f}")
    print(f"  RSI (14): {rsi:.2f} | ATR (14): ${atr:,.2f}")

    open_pos = get_open_positions()

    if len(open_pos) == 0:
        print("  Status: No open bot positions.")
        # Entry Condition:
        # Macro Bullish: Price > 200 EMA
        # Momentum: Fast EMA > Slow EMA
        # Entry zone: RSI between 45 and 68
        is_bullish = (price > trend) and (fast > slow) and (45.0 <= rsi <= 68.0)
        
        if is_bullish:
            print("  ==> [SIGNAL] Bullish Confluence Detected! Preparing BUY entry...")
            initial_stop = current_bid - (ATR_MULTIPLIER * atr)
            open_buy_order(DEFAULT_LOT_SIZE, initial_stop)
        else:
            reasons = []
            if price <= trend: reasons.append("Price <= 200 EMA")
            if fast <= slow: reasons.append("Fast EMA <= Slow EMA")
            if rsi < 45 or rsi > 68: reasons.append(f"RSI {rsi:.1f} outside 45-68")
            print(f"  ==> No entry signal. ({', '.join(reasons)})")
    else:
        for pos in open_pos:
            print(f"  Open Position Ticket #{pos.ticket}: Volume {pos.volume}, Entry ${pos.price_open:,.2f}, PnL: ${pos.profit:,.2f}")
            # Dynamic Trailing Stop check
            trailing_stop = current_bid - (ATR_MULTIPLIER * atr)
            if trailing_stop > pos.sl:
                print(f"  ==> Updating trailing stop from ${pos.sl:,.2f} to ${trailing_stop:,.2f}")
                if not DRY_RUN:
                    req = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "sl": trailing_stop,
                        "tp": pos.tp
                    }
                    mt5.order_send(req)

            # Exit condition on trend flip
            if fast < slow and price < slow:
                print("  ==> [EXIT] Trend Flip Detected. Closing position...")
                close_position(pos.ticket, pos.volume)

if __name__ == "__main__":
    print("=" * 60)
    print("       STARTING MT5 BTC/USD ALGORITHMIC TRADING BOT        ")
    print(f"       Mode: {'DRY RUN (Simulation)' if DRY_RUN else 'LIVE TRADING'}")
    print("=" * 60)

    if not connect_mt5():
        sys.exit(1)

    try:
        # Run single scan or continuous loop
        run_strategy_cycle()
        print("\n[✓] Cycle complete. Set loop or run continuously as scheduled task.")
    finally:
        mt5.shutdown()
        print("[✓] MT5 disconnected cleanly.")
