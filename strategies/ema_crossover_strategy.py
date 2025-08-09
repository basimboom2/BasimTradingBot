import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "fast_period": 9,
            "slow_period": 21
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def should_enter_trade(self, data):
        close = data["close"]
        fast_ema = close.ewm(span=self.config["fast_period"], adjust=False).mean()
        slow_ema = close.ewm(span=self.config["slow_period"], adjust=False).mean()

        if len(fast_ema) < 2 or len(slow_ema) < 2 or pd.isna(fast_ema.iloc[-1]) or pd.isna(slow_ema.iloc[-1]):
            return { "action": "NONE", "confidence": 0 }

        if fast_ema.iloc[-2] < slow_ema.iloc[-2] and fast_ema.iloc[-1] > slow_ema.iloc[-1]:
            return { "action": "BUY", "confidence": 1.0 }
        elif fast_ema.iloc[-2] > slow_ema.iloc[-2] and fast_ema.iloc[-1] < slow_ema.iloc[-1]:
            return { "action": "SELL", "confidence": 1.0 }
        else:
            return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.015  # 1.5% SL
        tp_pct = 0.03   # 3% TP
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }