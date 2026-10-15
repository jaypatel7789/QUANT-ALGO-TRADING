import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import os

def cache_all_data():
    os.makedirs("f:/multi agent/data/cache", exist_ok=True)
    terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(terminal_path):
        print("MT5 init failed")
        return
        
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    
    symbols = ["GOLD.i#", "BTCUSD#"]
    tfs = [
        ("1h", mt5.TIMEFRAME_H1),
        ("15m", mt5.TIMEFRAME_M15),
        ("5m", mt5.TIMEFRAME_M5),
        ("1m", mt5.TIMEFRAME_M1)
    ]
    
    for sym in symbols:
        mt5.symbol_select(sym, True)
        clean_sym = "gold" if "GOLD" in sym else "btc"
        for tf_name, tf in tfs:
            file_path = f"f:/multi agent/data/cache/{clean_sym}_{tf_name}.pkl"
            if os.path.exists(file_path):
                print(f"Already cached: {file_path}")
                continue
                
            print(f"Fetching {sym} {tf_name}...", flush=True)
            if tf_name in ["1h", "15m"]:
                rates = mt5.copy_rates_range(sym, tf, one_year_ago, now)
            else:
                rates = mt5.copy_rates_from_pos(sym, tf, 0, 45000)
                
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df["time"] = pd.to_datetime(df["time"], unit="s")
                df.set_index("time", inplace=True)
                df.to_pickle(file_path)
                print(f"Saved {file_path}: {len(df)} bars ({df.index[0]} to {df.index[-1]})", flush=True)
            else:
                print(f"No rates returned for {sym} {tf_name}", flush=True)
                
    mt5.shutdown()
    print("All datasets cached successfully!", flush=True)

if __name__ == "__main__":
    cache_all_data()
