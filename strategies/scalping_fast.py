from strategies.base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    def should_enter_trade(self, data):
        if data['close'].iloc[-1] > data['open'].iloc[-1]:
            return {"action": "BUY", "confidence": 0.75}
        else:
            return {"action": "NONE", "confidence": 0}

    def should_exit_trade(self, data):
        if data['close'].iloc[-1] < data['open'].iloc[-1]:
            return {"action": "EXIT", "confidence": 0.75}
        else:
            return {"action": "NONE", "confidence": 0}