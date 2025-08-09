
import pandas as pd
from core.binance_api import get_klines

def get_historical_data(symbol: str, interval: str, limit: int = 100):
    try:
        klines = get_klines(symbol, interval, limit)
        if not klines:
            print("❌ No kline data received.")
            return None

        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close",
            "volume", "close_time", "quote_asset_volume",
            "number_of_trades", "taker_buy_base_volume",
            "taker_buy_quote_volume", "ignore"
        ])

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df.astype(float)
        return df[["open", "high", "low", "close", "volume"]]
    except Exception as e:
        print(f"❌ Error loading historical data: {e}")
        return None
