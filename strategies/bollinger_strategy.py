import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "period": 20,
            "deviation": 2
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        close = data["close"]
        if len(close) < self.config["period"] + 2:
            return { "action": "NONE", "confidence": 0 }
        ma = close.rolling(window=self.config["period"]).mean()
        std = close.rolling(window=self.config["period"]).std()
        upper = ma + self.config["deviation"] * std
        lower = ma - self.config["deviation"] * std
        last_close = close.iloc[-1]
        last_upper = upper.iloc[-1]
        last_lower = lower.iloc[-1]

        if pd.isna(last_upper) or pd.isna(last_lower):
            return { "action": "NONE", "confidence": 0 }

        if last_close < last_lower:
            return { "action": "BUY", "confidence": 0.9 }
        elif last_close > last_upper:
            return { "action": "SELL", "confidence": 0.9 }
        else:
            return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.01
        tp_pct = 0.02
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }