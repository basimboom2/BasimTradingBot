import sys
from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow
import threading
import asyncio
import nest_asyncio
nest_asyncio.apply()

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

from core.auth import login

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from core.telegram_bot_manager import button, handle_message

from core.utils import decrypt_dev_info

def run_polling_bot():
    BOT_TOKEN, _ = decrypt_dev_info()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    # --- إضافة الـ handlers المطلوبة ---
    app.add_handler(CallbackQueryHandler(button))  # لمعالجة ضغط الأزرار التفاعلية (الموافقة/الرفض)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # لمعالجة رسائل المطور (عدد الأيام أو إدخالات أخرى)
    # يمكنك إضافة أوامر أخرى هنا إذا أردت (مثل /start أو /help)
    print("📡 بوت التليجرام يعمل (polling thread)...")
    app.run_polling()

def main():
    try:
        polling_thread = threading.Thread(
            target=run_polling_bot, daemon=True
        )
        polling_thread.start()

        result = login(username, password)
        if result["status"] == "success":
            print(f"✅ دخول {result['role']} - {username}")

            app = QApplication(sys.argv)
            window = MainWindow(username=username, role=result["role"])
            window.show()
            sys.exit(app.exec_())
        else:
            print("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")

    # تشغيل واجهة تسجيل الدخول الجديدة
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()