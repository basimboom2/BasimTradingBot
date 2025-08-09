import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "window": 5,
            "threshold": 0.001
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def detect_levels(self, highs, lows):
        support = []
        resistance = []
        window = self.config["window"]
        for i in range(window, len(highs) - window):
            is_support = all(lows[i] < lows[i - j] and lows[i] < lows[i + j] for j in range(1, window))
            is_resistance = all(highs[i] > highs[i - j] and highs[i] > highs[i + j] for j in range(1, window))
            if is_support:
                support.append((i, lows[i]))
            if is_resistance:
                resistance.append((i, highs[i]))
        return support, resistance

    def should_enter_trade(self, data):
        highs = data["high"]
        lows = data["low"]
        close = data["close"]

        # تأكد أن بياناتك كافية
        if len(close) < self.config["window"] * 2 + 2:
            return { "action": "NONE", "confidence": 0 }

        support_levels, resistance_levels = self.detect_levels(highs.values, lows.values)
        last_price = close.iloc[-1]

        for _, level in support_levels:
            if abs(last_price - level) / last_price < self.config["threshold"]:
                return { "action": "BUY", "confidence": 0.7 }
        for _, level in resistance_levels:
            if abs(last_price - level) / last_price < self.config["threshold"]:
                return { "action": "SELL", "confidence": 0.7 }

        return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.015
        tp_pct = 0.03
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }