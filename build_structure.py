import os

# تعريف هيكلية المجلدات والملفات
structure = {
    "config": ["settings.py"],
    "core": ["auth.py", "binance_client.py", "trade_manager.py", "utils.py"],
    "strategies": ["base.py", "scalping_fast.py", "scalping_normal.py", "ai_strategies.py"],
    "backtesting": ["backtest_engine.py"],
    "gui": [
        "main_window.py",
        os.path.join("tabs", "trading_tab.py"),
        os.path.join("tabs", "manual_trading_tab.py"),
        os.path.join("tabs", "backtest_tab.py"),
        os.path.join("tabs", "reports_tab.py"),
        os.path.join("tabs", "settings_tab.py"),
        os.path.join("tabs", "contact_tab.py"),
        os.path.join("widgets", "custom_widgets.py"),
        os.path.join("styles", "dark.qss"),
        os.path.join("styles", "light.qss"),
    ],
    "telegram": ["bot.py", "subscription.py"],
    "reports": ["report_generator.py", "charts.py"],
    "translations": ["ar.json", "en.json"],
    "database": ["models.py", "db_manager.py", os.path.join("migrations", ".gitkeep")],
    "data": [os.path.join("logs", ".gitkeep")],
    "tests": ["test_strategies.py"],
}

# ملفات الجذر
root_files = [
    "main.py",
    "generate_key.py",
    "requirements.txt",
    "README.md",
    "superuser_setup.py",
    ".env.example"
]

def create_structure():
    for folder, files in structure.items():
        os.makedirs(folder, exist_ok=True)
        for file in files:
            file_path = os.path.join(folder, file)
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            # إنشاء الملف إذا لم يكن موجودًا
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    pass

    # إنشاء ملفات الجذر
    for file in root_files:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                pass

    print("✅ تم بناء هيكلية المشروع بنجاح!")

if __name__ == "__main__":
    create_structure()
