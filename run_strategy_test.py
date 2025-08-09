
from strategies.strategy_engine import StrategyEngine

if __name__ == "__main__":
    # إعداد المحرك على رمز TRXUSDT وفريم 15 دقيقة
    engine = StrategyEngine("TRXUSDT", "15m")
    engine.load_strategies()

    # تحليل وتنفيذ الصفقات مرة واحدة (بدون حلقة زمنية مستمرة)
    analysis = engine.analyze_market()
    if analysis:
        print(f"✅ Found {len(analysis)} opportunities.")
    else:
        print("🚫 No signals returned.")
