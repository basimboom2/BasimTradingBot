import pandas as pd
from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def __init__(self, symbol, timeframe, config=None):
        default_config = {
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9
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

    def compute_macd(self, series, fast, slow, signal):
        fast_ema = series.ewm(span=fast, adjust=False).mean()
        slow_ema = series.ewm(span=slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        return macd, macd_signal

    def should_enter_trade(self, data):
        close = data["close"]
        rsi = self.compute_rsi(close, self.config["rsi_period"])
        macd, macd_signal = self.compute_macd(close, self.config["macd_fast"], self.config["macd_slow"], self.config["macd_signal"])

        if len(rsi) < 2 or len(macd) < 2 or len(macd_signal) < 2 or pd.isna(rsi.iloc[-1]) or pd.isna(macd.iloc[-1]) or pd.isna(macd_signal.iloc[-1]):
            return { "action": "NONE", "confidence": 0 }

        latest_rsi = rsi.iloc[-1]
        macd_cross_up = macd.iloc[-2] < macd_signal.iloc[-2] and macd.iloc[-1] > macd_signal.iloc[-1]
        macd_cross_down = macd.iloc[-2] > macd_signal.iloc[-2] and macd.iloc[-1] < macd_signal.iloc[-1]

        if latest_rsi < self.config["rsi_oversold"] and macd_cross_up:
            return { "action": "BUY", "confidence": 0.9 }
        elif latest_rsi > self.config["rsi_overbought"] and macd_cross_down:
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
        sl_pct = 0.012
        tp_pct = 0.025
        sl = round(entry_price * (1 - sl_pct), 4)
        tp = [round(entry_price * (1 + tp_pct), 4)]
        return { "sl": sl, "tp": tp }