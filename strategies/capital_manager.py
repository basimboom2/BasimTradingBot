
from config.settings import CAPITAL_USDT, CAPITAL_PERCENTAGE_PER_TRADE, LEVERAGE
from core.binance_api import get_price
class Strategy:
    def __init__(self, symbol, timeframe, config=None):
        pass
    def should_enter_trade(self, data):
        return {"action": "NONE", "confidence": 0}
    def should_exit_trade(self, data):
        return {"action": "NONE", "confidence": 0}

def get_trade_quantity(symbol: str, entry_price: float = None) -> float:
    """
    احسب كمية الصفقة بناءً على رأس المال المتاح، النسبة المحددة، والرافعة المالية.
    """
    if entry_price is None:
        entry_price = get_price(symbol)
        if entry_price is None:
            raise ValueError(f"❌ Couldn't fetch price for {symbol}")

    capital_to_use = (CAPITAL_USDT * CAPITAL_PERCENTAGE_PER_TRADE / 100.0) * LEVERAGE
    quantity = capital_to_use / entry_price

    # تقريب الكمية لأقرب رقم عشري مناسب (يجب تعديله لاحقًا حسب كل عملة)
    return round(quantity, 3)