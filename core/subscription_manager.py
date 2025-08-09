import json

import requests
from datetime import datetime, timedelta
from database.db_manager import get_connection, get_subscription_dates, get_user_id, get_user_device_id, set_user_device_id, update_user_status
from core.utils import decrypt_dev_info

USDT_WALLET_ADDRESS = "TRX-USDT-XXXXXXXXXXXXXXXXX"  # العنوان الثابت للمطور

def get_days_remaining(username):
    _, end_str = get_subscription_dates(username)
    if not end_str:
        return None
    try:
        end_date = datetime.fromisoformat(end_str)
        delta = end_date - datetime.now()
        days_left = delta.days + (1 if delta.seconds > 0 else 0)
        return days_left
    except Exception:
        return None

def should_show_renewal_prompt(username):
    days = get_days_remaining(username)
    return days is not None and 0 < days <= 5

def record_txid_request(username, txid):
    conn, cursor = get_connection()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS renewal_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            txid TEXT,
            created_at TEXT
        );
    """)
    cursor.execute("""
        INSERT INTO renewal_requests (username, txid, created_at)
        VALUES (?, ?, ?)
    """, (username, txid, datetime.now().isoformat()))
    conn.commit()
    conn.close()



def notify_telegram_txid(username, txid):
    """
    إرسال طلب تجديد اشتراك إلى المطور عبر Telegram API مع أزرار موافقة/رفض.
    """
    try:
        bot_token, chat_id = decrypt_dev_info()
    except Exception:
        bot_token, chat_id = None, None

    # جلب تاريخ انتهاء الاشتراك
    try:
        _, end_str = get_subscription_dates(username)
    except Exception:
        end_str = None

    message = (
        f"🔁 طلب تجديد اشتراك:\n"
        f"👤 المستخدم: {username}\n"
        f"📅 الاشتراك الحالي ينتهي في: {end_str if end_str else 'غير معروف'}\n"
        f"💸 TxID: `{txid}`"
    )

    if bot_token and chat_id:
        try:
            keyboard = [
                [
                    {"text": "✅ موافقة", "callback_data": f"approve_renew {username} [عدد_الأيام]"},
                    {"text": "❌ رفض", "callback_data": f"reject_renew {username}"}
                ]
            ]
            reply_markup = json.dumps({"inline_keyboard": keyboard}, ensure_ascii=False)
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "reply_markup": reply_markup
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print("❌ خطأ أثناء إرسال رسالة التليجرام:", e)
            return False
    else:
        print("⚠️ بيانات التليجرام غير متوفرة")
        return False

def handle_renewal_decision(command_text):
    parts = command_text.strip().split()
    if not parts:
        return "❌ أمر غير صالح"

    action = parts[0].lower()
    if action not in ("approve_renew", "reject_renew"):
        return "❌ أمر غير معروف"

    if len(parts) < 2:
        return "❌ الرجاء تحديد اسم المستخدم"

    username = parts[1]

    if action == "approve_renew":
        if len(parts) < 3 or not parts[2].isdigit():
            return "❌ الرجاء تحديد عدد الأيام (مثال: approve_renew basim 30)"
        days = int(parts[2])
        return extend_subscription(username, days)

    elif action == "reject_renew":
        return f"🚫 تم رفض تجديد اشتراك المستخدم: {username}"

def extend_subscription(username, extra_days):
    conn, cursor = get_connection()
    cursor.execute("""
        SELECT s.id, s.end_date
        FROM subscriptions s
        JOIN users u ON u.id = s.user_id
        WHERE u.username = ? AND s.is_active = 1
        ORDER BY s.id DESC LIMIT 1
    """, (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return "❌ لم يتم العثور على اشتراك مفعل لهذا المستخدم."

    sub_id, end_str = row
    try:
        end_date = datetime.fromisoformat(end_str)
        new_end = end_date + timedelta(days=extra_days)
        cursor.execute("UPDATE subscriptions SET end_date = ? WHERE id = ?", (new_end.isoformat(), sub_id))
        conn.commit()
        return f"✅ تم تمديد اشتراك {username} حتى {new_end.strftime('%Y-%m-%d')}"
    except Exception as e:
        return f"⚠️ فشل في التمديد: {e}"
    finally:
        conn.close()

# --- إضافات للموافقة على مستخدم جديد ---

def temporarily_approve_user(username, days):
    # حفظ عدد الأيام في جدول مؤقت، أو تحديث الحقل status فقط
    conn, cursor = get_connection()
    cursor.execute("UPDATE users SET status = 'waiting_duration', temp_days = ? WHERE username = ?", (days, username))
    conn.commit()
    conn.close()

def process_final_approval(username):
    conn, cursor = get_connection()
    cursor.execute("SELECT id, temp_days FROM users WHERE username = ? AND status = 'waiting_duration'", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    user_id, days = row
    now = datetime.now()
    end = now + timedelta(days=days)

    # إنشاء الاشتراك
    cursor.execute("INSERT INTO subscriptions (user_id, start_date, end_date, is_active) VALUES (?, ?, ?, 1)", (user_id, now.isoformat(), end.isoformat()))

    # تحديث حالة المستخدم وتخزين الجهاز
    device_id = get_user_device_id()
    cursor.execute("UPDATE users SET status = 'active', device_id = ?, temp_days = NULL WHERE id = ?", (device_id, user_id))
    conn.commit()
    conn.close()
    return True

def reject_new_user(username):
    conn, cursor = get_connection()
    cursor.execute("DELETE FROM users WHERE username = ? AND status = 'pending'", (username,))
    conn.commit()
    conn.close()
