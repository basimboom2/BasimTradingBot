import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "period": 14,
            "overbought": 70,
            "oversold": 30
        }
        merged_config = default_config | (config or {})
        super().__init__(symbol, timeframe, merged_config)

    def compute_rsi(self, series, period):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def should_enter_trade(self, data):
        close = data["close"]
        rsi = self.compute_rsi(close, self.config["period"])
        if len(rsi) == 0 or pd.isna(rsi.iloc[-1]):
            return { "action": "NONE", "confidence": 0 }

        latest_rsi = rsi.iloc[-1]
        if latest_rsi > self.config["overbought"]:
            return { "action": "SELL", "confidence": round((latest_rsi - self.config["overbought"]) / 30, 2) }
        elif latest_rsi < self.config["oversold"]:
            return { "action": "BUY", "confidence": round((self.config["oversold"] - latest_rsi) / 30, 2) }
        else:
            return { "action": "NONE", "confidence": 0 }

    def should_exit_trade(self, data):
        price = data['close'].iloc[-1]
        ma = data['close'].rolling(window=20).mean().iloc[-1]
        if price < ma:
            return { "action": "EXIT", "confidence": 0.7 }
        return { "action": "NONE", "confidence": 0 }

    def get_stop_loss_take_profit(self, data, entry_price):
        sl_pct = 0.01  # 1% stop loss
        tp_pct = 0.02  # 2% take profit
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }