import time
from core.binance_api import (
    place_market_order,
    place_limit_order,
    place_trailing_stop_order,
    cancel_order,
    get_price
)
from config.settings import CAPITAL_PERCENTAGE_PER_TRADE, TRAILING_STOP_CALLBACK
from strategies.capital_manager import get_trade_quantity
from core.order_tracker import track_order_execution

class TradeExecutor:
    def __init__(self, symbol, is_scalp_fast):
        self.symbol = symbol
        self.is_scalp_fast = is_scalp_fast

    def execute_trade(self, side, entry_price, sl, tp, use_trailing=False):
        print(f"🔃 Preparing to execute {side} trade on {self.symbol}...")

        # حساب الكمية بناءً على رأس المال ونسبة المخاطرة
        quantity = get_trade_quantity(self.symbol, entry_price)

        # تنفيذ أمر الدخول
        if self.is_scalp_fast or use_trailing:
            order = place_market_order(self.symbol, side, quantity)
            print(f"✅ Market order placed: {order}")
        else:
            order = place_limit_order(self.symbol, side, quantity, entry_price)
            print(f"✅ Limit order placed at {entry_price}")

        # تأكيد تنفيذ الدخول
        if not track_order_execution(order):
            print("❌ Order failed to execute.")
            return

        # تنفيذ Trailing Stop بدلاً من SL/TP إذا مفعل
        if use_trailing:
            trailing_order = place_trailing_stop_order(
                symbol=self.symbol,
                side="SELL" if side == "BUY" else "BUY",
                quantity=quantity,
                callback_rate=TRAILING_STOP_CALLBACK
            )
            print(f"🎯 Trailing Stop order placed: {trailing_order}")
            return

        # أوامر TP و SL (يدويًا كـ OCO)
        opposite_side = "SELL" if side == "BUY" else "BUY"
        tp_order = place_limit_order(self.symbol, opposite_side, quantity, tp)
        sl_order = place_limit_order(self.symbol, opposite_side, quantity, sl, stop=True)

        print(f"📍 TP Order: {tp_order}, SL Order: {sl_order}")

        # متابعة تنفيذ أوامر الخروج
        while True:
            if track_order_execution(tp_order):
                cancel_order(sl_order)
                print("✅ TP hit, SL cancelled.")
                break
            elif track_order_execution(sl_order):
                cancel_order(tp_order)
                print("🛑 SL hit, TP cancelled.")
                break
            time.sleep(3)