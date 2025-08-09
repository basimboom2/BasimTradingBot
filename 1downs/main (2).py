
import sys
import threading
import asyncio
import nest_asyncio
nest_asyncio.apply()

# Keep original imports and behavior; we only replace console input with GUI login
from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow

from core.auth import login  # kept for backward compatibility if other modules import main
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters
from core.telegram_bot_manager import button, handle_message
from core.utils import decrypt_dev_info

def run_polling_bot():
    BOT_TOKEN, _ = decrypt_dev_info()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(BOT_TOKEN).build()
    # --- Handlers ---
    app.add_handler(CallbackQueryHandler(button))  # handle inline buttons
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("📡 بوت التليجرام يعمل (polling thread)...")
    app.run_polling()

def main():
    try:
        # Start telegram polling in background thread (kept as original behavior)
        polling_thread = threading.Thread(target=run_polling_bot, daemon=True)
        polling_thread.start()

        # Launch GUI login window instead of console input
        app = QApplication(sys.argv)
        login_win = LoginWindow()
        login_win.show()
        sys.exit(app.exec_())

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    main()
