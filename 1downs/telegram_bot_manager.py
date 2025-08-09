
import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database.db_manager import (
    insert_user_with_subscription,
    reject_user,
    save_txid_for_user,
    get_subscription_dates,
    update_subscription_status
)
from core.utils import decrypt_dev_info, get_device_info

BOT_TOKEN, ADMIN_CHAT_ID = decrypt_dev_info()
if ADMIN_CHAT_ID is not None:
    try:
        ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
    except Exception:
        pass

pending_days_input = {}       # developer_telegram_id -> username or dict(action, username)
pending_txid_input = {}       # user_chat_id: username

# ─────────────────────────────────────────────
# طلب تفعيل مستخدم جديد (موافقة أو رفض)
async def send_activation_request(username, device_id):
    bot = Bot(token=BOT_TOKEN)
    device_info = get_device_info()
    info_str = (
        f"💻 الجهاز: {device_id}\n"
        f"🌐 النظام: {device_info.get('system','')}, إصدار: {device_info.get('release','')}\n"
        f"🖥️ اسم المضيف: {device_info.get('node','')}\n"
        f"🔗 MAC: {device_info.get('mac','')}\n"
        f"🌍 IP: {device_info.get('ip','')}, مدينة: {device_info.get('city','')}, دولة: {device_info.get('country','')}\n"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{username}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{username}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"🔐 طلب تسجيل دخول جديد:\n👤 المستخدم: {username}\n{info_str}\nهل ترغب بالموافقة؟"
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=reply_markup)

# ─────────────────────────────────────────────
# طلب تجديد اشتراك (إرسال TXID إلى المطور)
async def send_txid_to_admin(username, txid):
    bot = Bot(token=BOT_TOKEN)
    keyboard = [
        [
            InlineKeyboardButton("✅ تأكيد التجديد", callback_data=f"txid_confirm_{username}"),
            InlineKeyboardButton("❌ رفض التجديد", callback_data=f"txid_reject_{username}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"🔁 طلب تجديد اشتراك:\n👤 المستخدم: {username}\n💳 TxID: `{txid}`\nهل ترغب بتأكيد التجديد؟"
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=reply_markup, parse_mode="Markdown")

# ─────────────────────────────────────────────
# معالجة الرد من المطور (callback_query)
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data
    bot = Bot(token=BOT_TOKEN)

    if callback_data.startswith("approve_"):
        username = callback_data.split("approve_")[1]
        pending_days_input[query.from_user.id] = username
        await query.edit_message_text(f"✅ تم قبول المستخدم {username}.\n📆 الرجاء إدخال عدد أيام الاشتراك.")

    elif callback_data.startswith("reject_"):
        username = callback_data.split("reject_")[1]
        reject_user(username)
        await query.edit_message_text(f"❌ تم رفض المستخدم {username}.")

    elif callback_data.startswith("txid_confirm_"):
        username = callback_data.split("txid_confirm_")[1]
        pending_days_input[query.from_user.id] = {"action": "renewal", "username": username}
        await query.edit_message_text(f"🔁 تأكيد تجديد الاشتراك للمستخدم {username}.\n📆 الرجاء إدخال عدد الأيام الجديدة.")

    elif callback_data.startswith("txid_reject_"):
        username = callback_data.split("txid_reject_")[1]
        await query.edit_message_text(f"❌ تم رفض تجديد الاشتراك للمستخدم {username}.")

# ─────────────────────────────────────────────
# استقبال عدد الأيام من المطور (بعد الموافقة أو التجديد)
async def handle_dev_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pending_days_input:
        return

    entry = pending_days_input.pop(user_id)
    try:
        days = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ يرجى إدخال عدد صحيح من الأيام.")
        return

    if isinstance(entry, dict) and entry.get("action") == "renewal":
        username = entry["username"]
        start = datetime.now().date().isoformat()
        end = (datetime.now() + timedelta(days=days)).date().isoformat()
        update_subscription_status(username=username, status="فعال", start=start, end=end)
        await update.message.reply_text(f"✅ تم تجديد الاشتراك لـ {username} حتى {end}.")

    elif isinstance(entry, str):
        username = entry
        start = datetime.now().date().isoformat()
        end = (datetime.now() + timedelta(days=days)).date().isoformat()
        insert_user_with_subscription(username=username, status="فعال", start=start, end=end)
        await update.message.reply_text(f"✅ تم تفعيل الاشتراك لـ {username} حتى {end}.")

# ─────────────────────────────────────────────
# إرسال تنبيه للمستخدم باقتراب انتهاء الاشتراك
async def send_subscription_reminder(username, days_left):
    bot = Bot(token=BOT_TOKEN)
    message = f"⏳ تبقى {days_left} يومًا على انتهاء اشتراكك، سارع بالتجديد الآن لتحصل على خصم 10%."
    print(f"[Reminder] {username}: {message}")
