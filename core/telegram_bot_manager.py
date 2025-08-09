import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
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

# --- توحيد جلب التوكن والشات آي دي ---
BOT_TOKEN, ADMIN_CHAT_ID = decrypt_dev_info()
if ADMIN_CHAT_ID is not None:
    try:
        ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
    except Exception:
        pass

pending_days_input = {}       # developer_telegram_id -> username or dict(action, username)
pending_txid_input = {}       # user_chat_id: username (لتأكيد التجديد عبر الدردشة إن وُجد)

# --------------------------------------------
# إرسال طلب تفعيل مستخدم جديد (بأزرار موافقة/رفض)
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

# --------------------------------------------
# إرسال طلب تفعيل سوبر يوزر (بأزرار موافقة/رفض)
async def send_superuser_activation_request(username, request_id):
    bot = Bot(token=BOT_TOKEN)
    keyboard = [
        [
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_superuser_{request_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_superuser_{request_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"🔐 محاولة دخول من سوبر يوزر:\n"
        f"👤 المستخدم: {username}\n"
        f"🆔 الطلب: {request_id}\n\n"
        f"اختر الإجراء المناسب:"
    )
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=reply_markup)

# --------------------------------------------
# إرسال طلب تجديد اشتراك مع أزرار موافقة/رفض
async def send_txid_to_admin(username, txid):
    bot = Bot(token=BOT_TOKEN)
    keyboard = [
        [
            InlineKeyboardButton("✅ تأكيد التجديد", callback_data=f"txid_confirm_{username}"),
            InlineKeyboardButton("❌ رفض التجديد", callback_data=f"txid_reject_{username}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    def escape_md(text):
        escape_chars = r"\_*[]()~`>#+-=|{}.!$"
        return ''.join(['\\' + c if c in escape_chars else c for c in text])

    txid_escaped = escape_md(txid)

    text = (
        f"🔁 طلب تجديد اشتراك:\n"
        f"👤 المستخدم: {username}\n"
        f"💳 TxID:\n`{txid_escaped}`\n"
        f"\nهل ترغب بتأكيد التجديد؟"
    )

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

# --------------------------------------------
# إرسال تنبيه باقتراب انتهاء الاشتراك (لمطوّر أو للمستخدم حسب الحاجة)
async def send_subscription_reminder(username, days_left):
    bot = Bot(token=BOT_TOKEN)
    message = f"⏳ تبقى {days_left} يومًا على انتهاء اشتراكك، سارع بالتجديد الآن لتحصل على خصم 10%."
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🔔 تنبيه للمستخدم {username}:\n{message}")

# --------------------------------------------
# معالجة الضغط على زر الموافقة/الرفض لأي مستخدم جديد أو طلب تجديد أو سوبر يوزر
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # موافقة أو رفض سوبر يوزر
    if data.startswith("approve_superuser_") or data.startswith("reject_superuser_"):
        request_id = data.split("_superuser_")[1]
        try:
            from core import auth as auth_module
        except Exception:
            auth_module = None
        if data.startswith("approve_superuser_"):
            # موافقة سوبر يوزر
            await query.edit_message_text("✅ تم الموافقة على دخول السوبر يوزر.")
            if auth_module:
                auth_module.finalize_user_creation(f"superuser_{request_id}", None, approved=True)
        else:
            await query.edit_message_text("❌ تم رفض دخول السوبر يوزر.")
            if auth_module:
                auth_module.finalize_user_creation(f"superuser_{request_id}", None, approved=False)
        return

    # الموافقة على مستخدم جديد: نطلب إدخال عدد الأيام
    if data.startswith("approve_"):
        username = data.split("approve_")[1]
        pending_days_input[query.from_user.id] = username
        try:
            from core import auth as auth_module
        except Exception:
            auth_module = None
        if auth_module:
            auth_module.pending_users[username] = {'approved': None, 'finalized': False, 'waiting_days_input': True, 'device_id': None}
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🗓 أدخل عدد الأيام لتفعيل المستخدم {username}:"
        )
        await query.edit_message_text(f"✅ الموافقة المبدئية على المستخدم {username}. انتظر إدخال عدد الأيام.")

    # رفض مستخدم جديد
    elif data.startswith("reject_"):
        username = data.split("reject_")[1]
        reject_user(username)
        try:
            from core import auth as auth_module
        except Exception:
            auth_module = None
        if auth_module:
            auth_module.pending_users[username] = {'approved': False, 'finalized': True}
        await query.edit_message_text(f"❌ تم رفض المستخدم {username}.")

    # تأكيد تجديد اشتراك
    elif data.startswith("txid_confirm_"):
        username = data.split("txid_confirm_")[1]
        pending_days_input[query.from_user.id] = {"action": "renewal", "username": username}
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"📅 الرجاء إدخال عدد الأيام الجديدة لتجديد اشتراك {username}:")
        await query.edit_message_text(f"✅ استلمت طلب تجديد لمستخدم {username}. أرسل عدد الأيام هنا في المحادثة.")

    # رفض تجديد اشتراك
    elif data.startswith("txid_reject_"):
        username = data.split("txid_reject_")[1]
        update_subscription_status(username, None, None, is_renewal=False)
        await query.edit_message_text(f"❌ تم رفض تجديد اشتراك {username}.")

# --------------------------------------------
# معالجة رسائل المطور (إدخال عدد الأيام أو TxID)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id in pending_days_input:
        pending_val = pending_days_input.pop(user_id)
        if isinstance(pending_val, dict) and pending_val.get("action") == "renewal":
            username = pending_val.get("username")
            try:
                days = int(text.strip())
            except Exception:
                await update.message.reply_text("⚠️ أدخل رقمًا صحيحًا لعدد الأيام.")
                return
            today = datetime.now()
            start = today.strftime("%Y-%m-%d")
            end = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            try:
                update_subscription_status(username, start, end, is_renewal=True)
                await update.message.reply_text(f"✅ تم تجديد اشتراك {username} لمدة {days} يومًا.")
            except Exception as e:
                await update.message.reply_text(f"❌ فشل في تجديد الاشتراك: {e}")
            return

        # Approval for a NEW user
        username = pending_val
        try:
            days = int(text)
            today = datetime.now()
            start = today.strftime("%Y-%m-%d")
            end = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            from database.db_manager import get_user_by_username, update_subscription_status as _update_sub
            try:
                from core import auth as auth_module
                pending_device = auth_module.pending_users.get(username, {}).get('device_id')
            except Exception:
                pending_device = None
            if get_user_by_username(username):
                _update_sub(username, start, end, is_renewal=True)
                try:
                    from database.db_manager import get_user_by_username as _g, update_user_device
                    existing = _g(username)
                    stored_dev = existing[3] if existing and len(existing)>3 else None
                    if pending_device and not stored_dev:
                        update_user_device(username, pending_device)
                except Exception:
                    pass
            else:
                device_to_save = pending_device or "غير_محدد"
                res = insert_user_with_subscription(username, "تم_الموافقة", device_to_save, start, end)
                if isinstance(res, dict) and res.get("status") == "exists":
                    update_subscription_status(username, start, end, is_renewal=True)
            await update.message.reply_text(f"✅ تم تفعيل المستخدم {username} لمدة {days} يومًا.")
            try:
                from core import auth as auth_module
            except Exception:
                auth_module = None
            if auth_module and username in auth_module.pending_users:
                auth_module.pending_users[username].update({"approved": True, "finalized": True, "waiting_days_input": False})
        except ValueError:
            await update.message.reply_text("⚠️ أدخل رقمًا صحيحًا لعدد الأيام.")

    elif user_id in pending_txid_input:
        username = pending_txid_input.pop(user_id)
        txid = text
        save_txid_for_user(username, txid)
        await send_txid_to_admin(username, txid)
        await update.message.reply_text("📨 تم إرسال طلب التجديد للمطور، يرجى الانتظار.")

# --------------------------------------------
# إرسال رسالة للمستخدم (مثلاً عند الحاجة لإدخال TxID)
async def prompt_user_for_txid(username):
    bot = Bot(token=BOT_TOKEN)
    message = (
        f"⚠️ سينتهي اشتراكك خلال أيام.\n"
        f"للتجديد، أرسل المبلغ إلى عنوان USDT المحدد ثم أدخل TxID هنا."
    )
    user_chat_id = get_user_chat_id(username)
    if user_chat_id:
        pending_txid_input[user_chat_id] = username
        await bot.send_message(chat_id=user_chat_id, text=message)

def get_user_chat_id(username):
    return None  # مؤقتًا حتى يتم تفعيل التخزين

# --------------------------------------------
# دالة استقبال طلب تسجيل مستخدم جديد من auth.py
async def handle_new_user_request(context, username, ip_info, device_id):
    try:
        await send_activation_request(username, device_id)
    except Exception as e:
        print(f"⚠️ فشل إرسال طلب التفعيل للمطور: {e}")

# --------------------------------------------
# دالة استقبال طلب دخول سوبر يوزر من auth.py
async def handle_superuser_request(context, username, request_id):
    try:
        await send_superuser_activation_request(username, request_id)
    except Exception as e:
        print(f"⚠️ فشل إرسال طلب تفعيل السوبر يوزر: {e}")