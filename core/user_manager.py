import time
import uuid
from database.db_manager import insert_user
from core.utils import encrypt_data, decrypt_dev_info, get_device_info, hash_password
import requests
from datetime import datetime, timedelta

USDT_WALLET_ADDRESS = "TRX-USDT-XXXXXXXXXXXXXXXXX"  # يتم تعديله حسب محفظة المطور

def send_registration_request_to_telegram(username, request_id, device_id):
    bot_token, chat_id = decrypt_dev_info()
    if not bot_token or not chat_id:
        print("❌ فشل في قراءة بيانات تليجرام المطور.")
        return False, None, None

    # جلب معلومات الجهاز بشكل مفصّل
    device_info = get_device_info()
    info_str = (
        f"💻 الجهاز: {device_id}\n"
        f"🌐 النظام: {device_info.get('system','')}, إصدار: {device_info.get('release','')}\n"
        f"🖥️ اسم المضيف: {device_info.get('node','')}\n"
        f"🔗 MAC: {device_info.get('mac','')}\n"
        f"🌍 IP: {device_info.get('ip','')}, مدينة: {device_info.get('city','')}, دولة: {device_info.get('country','')}\n"
    )

    message = (
        f"🟡 طلب تسجيل مستخدم جديد:\n"
        f"👤 الاسم: {username}\n"
        f"{info_str}"
        f"🆔 الطلب: {request_id}\n\n"
        f"للموافقة أرسل: approve {request_id} [عدد_الأيام]\n"
        f"للرفض أرسل: reject {request_id}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=data)
        return response.status_code == 200, bot_token, chat_id
    except Exception as e:
        print("❌ خطأ أثناء الإرسال:", e)
        return False, None, None

def wait_for_telegram_response(bot_token, chat_id, request_id, timeout=60):
    print("⏳ في انتظار موافقة المطور...")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    seen_updates = set()
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
            for update in data.get("result", []):
                update_id = update["update_id"]
                if update_id in seen_updates:
                    continue
                seen_updates.add(update_id)

                msg = update.get("message", {})
                text = msg.get("text", "")
                from_id = str(msg.get("chat", {}).get("id", ""))

                if from_id != chat_id:
                    continue

                if text.lower().startswith(f"approve {request_id}"):
                    parts = text.strip().split()
                    if len(parts) == 3 and parts[2].isdigit():
                        days = int(parts[2])
                        return "approve", days
                    else:
                        return "invalid", None
                elif text.lower() == f"reject {request_id}":
                    return "reject", None

            time.sleep(2)
        except Exception as e:
            print("⚠️ خطأ أثناء انتظار الرد:", e)
            time.sleep(2)

    return "timeout", None

def request_user_registration(username, password, device_id):
    request_id = str(uuid.uuid4())[:8]
    sent, bot_token, chat_id = send_registration_request_to_telegram(username, request_id, device_id)
    if not sent:
        return {"status": "fail", "reason": "telegram-failed"}

    decision, days = wait_for_telegram_response(bot_token, chat_id, request_id)
    if decision == "approve":
        if not days:
            return {"status": "fail", "reason": "invalid-duration"}
        hashed_pw = hash_password(password)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        # تشفير بيانات الجهاز وربطها بالمستخدم داخل قاعدة البيانات
        encrypted_device_id = encrypt_data(device_id)
        insert_user(username, hashed_pw, start_date.isoformat(), end_date.isoformat(), encrypted_device_id)
        print(f"✅ تم تسجيل المستخدم '{username}' لمدة {days} يوم، مربوط بالجهاز '{device_id}'")
        return {"status": "success", "days": days}
    elif decision == "reject":
        print("❌ تم رفض تسجيل المستخدم من قبل المطور.")
        return {"status": "rejected"}
    elif decision == "invalid":
        print("❌ صيغة الرد من المطور غير صحيحة.")
        return {"status": "fail", "reason": "invalid-reply"}
    else:
        print("⌛ لم يتم الرد من المطور خلال المهلة.")
        return {"status": "fail", "reason": "timeout"}