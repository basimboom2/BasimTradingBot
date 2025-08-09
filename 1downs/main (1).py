
import sys
import threading
import asyncio
import nest_asyncio
nest_asyncio.apply()

from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow

from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters
from core.telegram_bot_manager import button, handle_message
from core.utils import decrypt_dev_info

def run_polling_bot():
    BOT_TOKEN, _ = decrypt_dev_info()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("📡 بوت التليجرام يعمل (polling thread)...")
    app.run_polling()

def main():
    try:
        polling_thread = threading.Thread(target=run_polling_bot, daemon=True)
        polling_thread.start()

        app = QApplication(sys.argv)
        login_win = LoginWindow()
        login_win.show()
        sys.exit(app.exec_())

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    main()
