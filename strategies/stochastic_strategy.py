import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "fastk_period": 14,
            "slowk_period": 3,
            "slowd_period": 3
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        high = data["high"]
        low = data["low"]
        close = data["close"]

        lowest_low = low.rolling(self.config["fastk_period"]).min()
        highest_high = high.rolling(self.config["fastk_period"]).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(self.config["slowd_period"]).mean()

        if len(k) < 2 or len(d) < 2 or pd.isna(k.iloc[-1]) or pd.isna(d.iloc[-1]):
            return { "action": "NONE", "confidence": 0 }

        k_val = k.iloc[-1]
        d_val = d.iloc[-1]

        if k_val < 20 and k_val > d_val:
            return { "action": "BUY", "confidence": 0.8 }
        elif k_val > 80 and k_val < d_val:
            return { "action": "SELL", "confidence": 0.8 }
        else:
            return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.012
        tp_pct = 0.022
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }