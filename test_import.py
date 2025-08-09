import core.telegram_bot_manager as tgm

print("📂 المسار الفعلي للملف:", tgm.__file__)
print("📜 الدوال والمحتويات داخل telegram_bot_manager:")
print(dir(tgm))

if hasattr(tgm, "handle_new_user_request"):
    print("✅ الدالة handle_new_user_request موجودة")
else:
    print("❌ الدالة handle_new_user_request غير موجودة")
