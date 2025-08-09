import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "lookback": 3
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        open_ = data["open"]
        close = data["close"]
        high = data["high"]
        low = data["low"]

        if len(close) < self.config["lookback"]:
            return { "action": "NONE", "confidence": 0 }

        last_candle = {
            "open": open_.iloc[-1],
            "close": close.iloc[-1],
            "high": high.iloc[-1],
            "low": low.iloc[-1]
        }
        prev_candle = {
            "open": open_.iloc[-2],
            "close": close.iloc[-2],
            "high": high.iloc[-2],
            "low": low.iloc[-2]
        }

        # Bullish engulfing
        if prev_candle["close"] < prev_candle["open"] and last_candle["close"] > last_candle["open"] and last_candle["close"] > prev_candle["open"] and last_candle["open"] < prev_candle["close"]:
            return { "action": "BUY", "confidence": 0.75 }

        # Bearish engulfing
        if prev_candle["close"] > prev_candle["open"] and last_candle["close"] < last_candle["open"] and last_candle["close"] < prev_candle["open"] and last_candle["open"] > prev_candle["close"]:
            return { "action": "SELL", "confidence": 0.75 }

        return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.013
        tp_pct = 0.027
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }