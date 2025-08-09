import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "volume_window": 20,
            "spike_multiplier": 2.0
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        volume = data["volume"]
        close = data["close"]
        open_ = data["open"]

        if len(volume) < self.config["volume_window"] + 1:
            return { "action": "NONE", "confidence": 0 }

        recent_volumes = volume.iloc[-self.config["volume_window"]-1:-1]
        avg_volume = recent_volumes.mean()
        current_volume = volume.iloc[-1]
        current_body = close.iloc[-1] - open_.iloc[-1]

        if current_volume > self.config["spike_multiplier"] * avg_volume:
            if current_body > 0:
                return { "action": "BUY", "confidence": 0.85 }
            elif current_body < 0:
                return { "action": "SELL", "confidence": 0.85 }

        return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.012
        tp_pct = 0.028
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }