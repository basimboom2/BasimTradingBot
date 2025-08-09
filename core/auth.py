import time
import requests
import uuid
import asyncio
from datetime import datetime

from database.db_manager import (
    check_user,
    check_user_status,
    get_device_id,
    get_subscription_dates,
    get_user_by_username
)
from core.utils import check_superuser_login, decrypt_dev_info, get_ip_info, get_device_info

pending_users = {}

def send_telegram_request(username, request_id, device_id=None):
    bot_token, chat_id = decrypt_dev_info()
    if not bot_token or not chat_id:
        print("❌ لا يمكن إرسال إشعار تليجرام: بيانات غير متوفرة.")
        return False, None, None

    # جلب بيانات الجهاز والموقع
    device_info = get_device_info()
    ip_info = get_ip_info()

    info_str = (
        f"💻 الجهاز: {device_id or device_info.get('mac','')}\n"
        f"🌐 النظام: {device_info.get('system','')}, إصدار: {device_info.get('release','')}\n"
        f"🖥️ اسم المضيف: {device_info.get('node','')}\n"
        f"🔗 MAC: {device_info.get('mac','')}\n"
        f"🌍 IP: {ip_info.get('ip','')}, مدينة: {ip_info.get('city','')}, دولة: {ip_info.get('country','')}\n"
    )

    message = (
        f"🔐 محاولة دخول من سوبر يوزر:\n"
        f"👤 المستخدم: {username}\n"
        f"🆔 الطلب: {request_id}\n"
        f"\n{info_str}"
        f"\nاختر الإجراء:"
    )

    keyboard = [
        [
            {"text": "✅ موافقة", "callback_data": f"approve_superuser_{request_id}"},
            {"text": "❌ رفض", "callback_data": f"reject_superuser_{request_id}"}
        ]
    ]
    import json
    reply_markup = json.dumps({"inline_keyboard": keyboard}, ensure_ascii=False)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": reply_markup
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return True, bot_token, chat_id
        else:
            print("❌ فشل إرسال التليجرام:", response.text)
            return False, None, None
    except Exception as e:
        print("❌ استثناء أثناء الإرسال:", e)
        return False, None, None

def is_subscription_valid(username):
    start_str, end_str = get_subscription_dates(username)
    if not start_str or not end_str:
        return False
    try:
        now = datetime.now()
        start = datetime.fromisoformat(start_str)
        end = datetime.fromisoformat(end_str)
        return start <= now <= end
    except Exception:
        return False

def login(username, password, device_id=None):
    # Ensure we have a device_id (gather from system if not provided)
    if device_id is None:
        try:
            dev = get_device_info() or {}
            device_id = dev.get('mac') or dev.get('node') or dev.get('ip') or None
        except Exception:
            device_id = None

    # تحقق من وجود المستخدم في قاعدة البيانات
    user_data = get_user_by_username(username)
    if user_data:
        stored_device_id = user_data[3] if len(user_data) > 3 else None
        start_date, end_date = get_subscription_dates(username)
        if stored_device_id and device_id and stored_device_id != device_id:
            print('❌ الجهاز الحالي غير مصرح به لهذا الحساب.')
            return {'status': 'fail', 'role': None}
        if end_date and datetime.now().date() > datetime.strptime(end_date, '%Y-%m-%d').date():
            print('❌ الاشتراك منتهي. برجاء التجديد.')
            return {'status': 'fail', 'role': None}
        print(f'✅ دخول مباشر للمستخدم {username}')
        return {'status': 'success', 'role': 'user'}

    # التحقق من بيانات السوبر يوزر
    if check_superuser_login(username, password):
        request_id = str(uuid.uuid4())[:8]
        sent, token, chat_id = send_telegram_request(username, request_id, device_id=device_id)
        if not sent:
            return {"status": "fail", "role": None}
        pending_users[f"superuser_{request_id}"] = {
            'username': username,
            'approved': None,
            'finalized': False,
            'waiting_approval': True
        }
        print("⏳ في انتظار موافقة المطور على دخول السوبر يوزر...")
        return {"status": "pending_superuser", "role": "superuser"}

    # تحقق من المستخدم العادي
    if check_user(username, password):
        status = check_user_status(username)
        if status == "pending":
            print("📩 إرسال إشعار للمطور بخصوص مستخدم جديد...")
            ip_info = get_ip_info()
            from core import telegram_bot_manager
            try:
                running_loop = asyncio.get_running_loop()
                running_loop.create_task(
                    telegram_bot_manager.handle_new_user_request(
                        context=None, username=username,
                        ip_info=ip_info, device_id=device_id
                    )
                )
            except RuntimeError:
                asyncio.run(
                    telegram_bot_manager.handle_new_user_request(
                        context=None, username=username,
                        ip_info=ip_info, device_id=device_id
                    )
                )
            print("⏳ بانتظار موافقة المطور...")
            return {"status": "pending", "role": None}

        if status != "active":
            print("⚠️ المستخدم غير مفعل.")
            return {"status": "fail", "role": None}

        if not is_subscription_valid(username):
            print("⚠️ الاشتراك منتهي أو غير صالح.")
            return {"status": "fail", "role": None}

        try:
            user_data = get_user_by_username(username)
            registered_device = user_data[3] if user_data and len(user_data) > 3 else None
        except Exception:
            registered_device = None

        if registered_device and device_id and registered_device != device_id:
            print("⚠️ هذا الحساب مربوط بجهاز مختلف.")
            return {"status": "fail", "role": None}
        return {"status": "success", "role": "user"}

    # إذا لم يكن المستخدم موجود → مستخدم جديد: نرسل طلب تفعيل للمطور
    ip_info = get_ip_info()
    from core import telegram_bot_manager
    try:
        running_loop = asyncio.get_running_loop()
        running_loop.create_task(
            telegram_bot_manager.handle_new_user_request(
                context=None, username=username,
                ip_info=ip_info, device_id=device_id
            )
        )
    except RuntimeError:
        asyncio.run(
            telegram_bot_manager.handle_new_user_request(
                context=None, username=username,
                ip_info=ip_info, device_id=device_id
            )
        )
    pending_users[username] = {
        'approved': None,
        'finalized': False,
        'waiting_days_input': True,
        'device_id': device_id
    }
    print(f'⏳ بانتظار رد المطور وإدخال عدد الأيام لتفعيل المستخدم {username}...')
    return {'status': 'pending', 'role': None}

def finalize_user_creation(username, device_id=None, approved=True):
    """تُستخدم بعد موافقة المطور لإنشاء المستخدم نهائيًا"""
    if username in pending_users:
        pending_users[username]['approved'] = approved
        pending_users[username]['device_id'] = device_id
        pending_users[username]['finalized'] = True
        pending_users[username]['waiting_approval'] = False
        print(f"✅ تم {'تفعيل' if approved else 'رفض'} المستخدم: {username}")
    else:
        print(f"⚠️ لا يوجد طلب معلق لهذا المستخدم: {username}")

def get_login_status(username, password, device_id=None):
    """
    دالة تستخدم login() لكن ترجع حالة نصية فقط لتسهيل تعامل الواجهة معها
    """
    try:
        result = login(username, password, device_id)
        status = result.get('status')
        role = result.get('role')

        if status == 'pending':
            return 'waiting_approval'
        if status == 'pending_superuser':
            for key, val in pending_users.items():
                if key.startswith("superuser_") and val.get("approved") is True:
                    return 'superuser'
            return 'waiting_superuser_approval'
        if status == 'fail':
            return 'fail'
        if role == 'superuser' and status == 'success':
            return 'superuser'
        if status == 'success' and role == 'user':
            return 'active'
        return 'fail'
    except Exception as e:
        print(f"⚠️ خطأ في get_login_status: {e}")
        return 'fail'