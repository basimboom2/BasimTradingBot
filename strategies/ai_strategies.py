import importlib
import os

STRATEGY_FOLDER = os.path.dirname(__file__)

def list_available_strategies():
    files = os.listdir(STRATEGY_FOLDER)
    strategies = []
    for file in files:
        if file.endswith(".py") and not file.startswith("__") and file not in [
            "strategy_engine.py", "ai_strategies.py", "base_strategy.py", "trade_executor.py"
        ]:
            strategies.append(file[:-3])  # Remove .py extension
    return strategies

def load_strategy(name, symbol, timeframe):
    try:
        module = importlib.import_module(f"strategies.{name}")
        strategy_class = getattr(module, "Strategy")
        return strategy_class(symbol, timeframe)
    except Exception as e:
        print(f"❌ Failed to load strategy {name}: {e}")
        return None