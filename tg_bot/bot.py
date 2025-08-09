import asyncio
import json
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters
)
from core.utils import decrypt_dev_info, get_ip_info
from database.db_manager import approve_user, reject_user
from core.auth import pending_users, finalize_user_creation

DEV_INFO_PATH = "core/dev_info.dat"

BOT_TOKEN = None
DEVELOPER_CHAT_ID = None

# ✅ [تصحيح] استخدام try/except مرة واحدة فقط بشكل صحيح
try:
    dev_info = decrypt_dev_info()
    BOT_TOKEN, DEVELOPER_CHAT_ID = dev_info
except Exception as e:
    print("❌ فشل في جلب بيانات التليجرام:", e)
    BOT_TOKEN = None
    DEVELOPER_CHAT_ID = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 أهلاً بك في بوت الإدارة.")

async def handle_login_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("approve_"):
        username = data.split("_", 1)[1]
        pending = pending_users.get(username)
        if pending:
            user_info = pending["user_info"]
            await query.message.reply_text(f"⏳ أرسل عدد أيام الاشتراك لـ {username}:")
            context.user_data["awaiting_days_for"] = username
        else:
            await query.message.reply_text("❌ لم يتم العثور على هذا المستخدم.")
    elif data.startswith("reject_"):
        username = data.split("_", 1)[1]
        reject_user(username)
        pending_users.pop(username, None)
        await query.message.reply_text(f"❌ تم رفض دخول المستخدم {username}.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_days_for" in context.user_data:
        username = context.user_data.pop("awaiting_days_for")
        try:
            days = int(update.message.text.strip())
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            finalize_user_creation(username, start_date, end_date)
            pending_users.pop(username, None)
            await update.message.reply_text(f"✅ تم تفعيل اشتراك {username} لمدة {days} يوم.")
        except ValueError:
            await update.message.reply_text("⚠️ من فضلك أدخل رقم صالح لعدد الأيام.")

async def notify_admin_of_login(username, device_id):
    ip_info = get_ip_info()
    location = f"{ip_info.get('city', 'غير معروف')}, {ip_info.get('country', 'غير معروف')}"
    text = (
        f"🔐 طلب تسجيل دخول جديد:\n"
        f"👤 المستخدم: {username}\n"
        f"🖥 الجهاز: {device_id}\n"
        f"🌐 IP: {ip_info.get('ip', 'غير معروف')}\n"
        f"📍 الموقع الجغرافي: {location}\n"
    )
    text += "هل ترغب بالموافقة؟"
    keyboard = [
        [
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{username}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{username}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=text, reply_markup=reply_markup)

async def run_telegram_bot():
    print("📡 بوت التليجرام يعمل...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_login_request))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()
    await app.run_polling()  # ✅ التصحيح هنا (بدلاً من updater)
    # لا داعي للأسطر التالية:
    # await app.stop()
    # await app.shutdown()