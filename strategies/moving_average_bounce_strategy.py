import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "ma_period": 50,
            "bounce_tolerance_pct": 0.005
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        if len(data) < self.config["ma_period"] + 2:
            return { "action": "NONE", "confidence": 0 }
        close = data["close"]
        ma = close.rolling(window=self.config["ma_period"]).mean()
        last_price = close.iloc[-1]
        last_ma = ma.iloc[-1]
        tolerance = last_price * self.config["bounce_tolerance_pct"]

        if pd.isna(last_ma):
            return { "action": "NONE", "confidence": 0 }

        if abs(last_price - last_ma) <= tolerance:
            prev_price = close.iloc[-2]
            prev_ma = ma.iloc[-2]
            if prev_price < prev_ma and last_price > last_ma:
                return { "action": "BUY", "confidence": 0.8 }
            elif prev_price > prev_ma and last_price < last_ma:
                return { "action": "SELL", "confidence": 0.8 }

        return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.01
        tp_pct = 0.025
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }