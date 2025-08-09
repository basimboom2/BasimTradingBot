import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "range_lookback": 20,
            "breakout_buffer_pct": 0.001
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        highs = data["high"]
        lows = data["low"]
        close = data["close"]

        if len(close) < self.config["range_lookback"] + 1:
            return { "action": "NONE", "confidence": 0 }

        recent_high = highs.iloc[-self.config["range_lookback"]-1:-1].max()
        recent_low = lows.iloc[-self.config["range_lookback"]-1:-1].min()
        current_close = close.iloc[-1]
        buffer = self.config["breakout_buffer_pct"] * current_close

        if current_close > recent_high + buffer:
            return { "action": "BUY", "confidence": 0.85 }
        elif current_close < recent_low - buffer:
            return { "action": "SELL", "confidence": 0.85 }
        else:
            return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.013
        tp_pct = 0.03
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }