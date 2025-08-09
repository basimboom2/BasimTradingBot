from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, symbol, timeframe, config=None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = config or {}

    @abstractmethod
    def should_enter_trade(self, data):
        pass

    def should_exit_trade(self, data):
        return {"action": "NONE", "confidence": 0}

    def get_stop_loss_take_profit(self, data, entry_price):
        return {"sl": None, "tp": []}