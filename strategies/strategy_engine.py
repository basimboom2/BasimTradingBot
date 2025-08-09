# strategy_engine.py

import time
from strategies.ai_strategies import list_available_strategies, load_strategy
from core.news_filter import is_safe_to_trade  # سيتم تنفيذه لاحقًا
from market_data import get_historical_data

class StrategyEngine:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategies = []

    def load_strategies(self):
        self.strategies.clear()
        for name in list_available_strategies():
            strategy = load_strategy(name, self.symbol, self.timeframe)
            if strategy:
                self.strategies.append(strategy)

    def analyze_market(self):
        # إحضار بيانات السوق
        data = get_historical_data(self.symbol, self.timeframe)
        if data is None or data.empty:
            print("❌ No data available")
            return None

        # دمج فلتر الأخبار (placeholder فقط حالياً)
        if not is_safe_to_trade():
            print("🛑 News risk detected. Trading disabled.")
            return None

        results = []

        for strategy in self.strategies:
            signal = strategy.should_enter_trade(data)
            if signal["action"] != "NONE":
                entry_price = data["close"].iloc[-1]
                sl_tp = strategy.get_stop_loss_take_profit(data, entry_price)
                results.append({
                    "strategy": strategy.__class__.__name__,
                    "signal": signal,
                    "entry": entry_price,
                    "sl_tp": sl_tp
                })

        return results

# مثال للاستخدام:
if __name__ == "__main__":
    engine = StrategyEngine("TRXUSDT", "15m")
    engine.load_strategies()

    while True:
        analysis = engine.analyze_market()
        if analysis:
            for res in analysis:
                from core.trade_executor import TradeExecutor
                # تحديد نوع السكالب (مبدئيًا نستخدم True لو الاستراتيجية فيها "ScalpingFast")
                is_scalp_fast = "Fast" in res["strategy"]
                executor = TradeExecutor("TRXUSDT", is_scalp_fast)
                executor.execute_trade(
                side=res["signal"]["action"],
                entry_price=res["entry"],
                sl=res["sl_tp"]["sl"],
                tp=res["sl_tp"]["tp"],
                use_trailing=res["signal"].get("trailing", False)
                )

        
                print(f"✅ {res['strategy']}: {res['signal']['action']} @ {res['entry']} | SL: {res['sl_tp']['sl']} TP: {res['sl_tp']['tp']}")
        time.sleep(60 * 15)  # كل 15 دقيقة