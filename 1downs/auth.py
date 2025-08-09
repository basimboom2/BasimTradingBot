import time
import requests
import uuid
import asyncio
from database.db_manager import (
    check_user,
    check_user_status,
    get_device_id,
    get_subscription_dates
)
from core.utils import check_superuser_login, decrypt_dev_info, get_ip_info
from datetime import datetime

def send_telegram_request(username, request_id):
    bot_token, chat_id = decrypt_dev_info()
    if not bot_token or not chat_id:
        print("❌ لا يمكن إرسال إشعار تليجرام: بيانات غير متوفرة.")
        return False, None, None

    message = (
        f"🔐 محاولة دخول من سوبر يوزر:\n"
        f"👤 المستخدم: {username}\n"
        f"🆔 الطلب: {request_id}\n\n"
        f"أرسل 'approve {request_id}' للموافقة أو 'reject {request_id}' للرفض."
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

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

def check_telegram_reply_polling(bot_token, chat_id, request_id, timeout=30):
    print("⏳ في انتظار موافقة المطور عبر polling...")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    start_time = time.time()
    seen_update_ids = set()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
            for update in data.get("result", []):
                update_id = update["update_id"]
                if update_id in seen_update_ids:
                    continue
                seen_update_ids.add(update_id)
                message = update.get("message", {})
                text = message.get("text", "")
                from_chat_id = str(message.get("chat", {}).get("id", ""))

                if from_chat_id != chat_id:
                    continue

                if f"approve {request_id}" in text.lower():
                    return "approve"
                elif f"reject {request_id}" in text.lower():
                    return "reject"

            time.sleep(2)
        except Exception as e:
            print("⚠️ خطأ أثناء فحص الردود:", e)
            time.sleep(2)

    return "timeout"

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
            from core.utils import get_device_info
            dev = get_device_info() or {}
            device_id = dev.get('mac') or dev.get('node') or dev.get('ip') or None
        except Exception:
            device_id = None

    # --- تحقق مبكر إذا كان المستخدم موجود بالفعل وجهازه واشتراكه صالح ---
    try:
        from database.db_manager import get_user_by_username, get_subscription_dates
        from datetime import datetime
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
            # إذا كل شيء تمام → دخول مباشر بدون إرسال طلب للمطور
            print(f'✅ دخول مباشر للمستخدم {username}')
            return {'status': 'success', 'role': 'user'}
    except Exception as e:
        pass

    # التحقق من بيانات السوبر يوزر
    if check_superuser_login(username, password):
        request_id = str(uuid.uuid4())[:8]
        sent, token, chat_id = send_telegram_request(username, request_id)
        if not sent:
            return {"status": "fail", "role": None}

        decision = check_telegram_reply_polling(token, chat_id, request_id)
        if decision == "approve":
            return {"status": "success", "role": "superuser"}
        elif decision == "reject":
            print("❌ تم رفض دخول السوبر يوزر من قِبل المطور.")
            return {"status": "fail", "role": None}
        else:
            print("⌛ انتهت مهلة انتظار رد المطور.")
            return {"status": "fail", "role": None}

    # تحقق من المستخدم العادي
    if check_user(username, password):
        status = check_user_status(username)
        # إذا المستخدم في حالة pending -> أعد إرسال طلب للمطور وانتظر إدخال الأيام
        if status == "pending":
            print("📩 إرسال إشعار للمطور بخصوص مستخدم جديد...")
            ip_info = get_ip_info()
            from core import telegram_bot_manager
            try:
                running_loop = asyncio.get_running_loop()
                running_loop.create_task(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
            except RuntimeError:
                asyncio.run(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
            print("⏳ بانتظار موافقة المطور...")
            return {"status": "pending", "role": None}

        if status != "active":
            print("⚠️ المستخدم غير مفعل.")
            return {"status": "fail", "role": None}

        # التحقق من الاشتراك
        if not is_subscription_valid(username):
            print("⚠️ الاشتراك منتهي أو غير صالح.")
            return {"status": "fail", "role": None}

        # التحقق من الجهاز المسجل
        try:
            registered_device = get_device_id(username)
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
        running_loop.create_task(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
    except RuntimeError:
        asyncio.run(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
    # إضافة المستخدم الجديد إلى قائمة الانتظار لحين موافقة المطور وإدخال عدد الأيام
    pending_users[username] = {
        'approved': None,
        'finalized': False,
        'waiting_days_input': True,
        'device_id': device_id
    }
    print(f'⏳ بانتظار رد المطور وإدخال عدد الأيام لتفعيل المستخدم {username}...')
    start_wait = time.time()
    while time.time() - start_wait < 300:  # مهلة 5 دقائق
        if pending_users.get(username, {}).get('finalized'):
            if pending_users[username]['approved']:
                return {'status': 'success', 'role': 'user'}
            else:
                return {'status': 'fail', 'role': None}
        time.sleep(2)
    print('⌛ انتهت مهلة انتظار رد المطور.')
    return {'status': 'fail', 'role': None}
# قائمة انتظار تسجيل المستخدمين الجدد (قيد الموافقة من المطور)
pending_users = {}

def finalize_user_creation(username, device_id, approved=True):
    """تُستخدم بعد موافقة المطور لإنشاء المستخدم نهائيًا"""
    if username in pending_users:
        pending_users[username]['approved'] = approved
        pending_users[username]['device_id'] = device_id
        pending_users[username]['finalized'] = True
        print(f"✅ تم {'تفعيل' if approved else 'رفض'} المستخدم: {username}")
    else:
        print(f"⚠️ لا يوجد طلب معلق لهذا المستخدم: {username}")
    # --- تحقق مبكر إذا كان المستخدم موجود بالفعل وجهازه واشتراكه صالح ---
    try:
        from database.db_manager import get_user_by_username, get_subscription_dates, get_device_id
        from datetime import datetime
        user_data = get_user_by_username(username)
        if user_data:
            # Use get_device_id to obtain decrypted device id stored in DB
            stored_device_id = get_device_id(username)
            start_date, end_date = get_subscription_dates(username)
            # If stored device exists and provided device_id doesn't match => reject
            if stored_device_id and device_id and stored_device_id != device_id:
                print('❌ الجهاز الحالي غير مصرح به لهذا الحساب. تواصل مع المطور.')
                return {'status': 'fail', 'role': None}
            # If subscription has an end_date, check if expired
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date).date()
                except Exception:
                    # attempt parse yyyy-mm-dd
                    end_dt = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d').date()
                if datetime.now().date() > end_dt:
                    print('❌ الاشتراك منتهي. برجاء التجديد.')
                    return {'status': 'fail', 'role': None}
            # All good: allow direct login (the higher-level password check will still apply afterward)
            print(f'✅ مستخدم موجود مع جهاز/اشتراك صالح: {username}')
            # Note: we only shortcut the developer notification; actual credential check continues below.
            # Indicate ready-to-login status
            # Continue to normal password check by not returning failure here.
    except Exception as e:
        # fall through to regular authentication flow on any issue
        pass
        print("❌ استثناء أثناء الإرسال:", e)
        return False, None, None

def check_telegram_reply_polling(bot_token, chat_id, request_id, timeout=30):
    print("⏳ في انتظار موافقة المطور عبر polling...")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    start_time = time.time()
    seen_update_ids = set()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
            for update in data.get("result", []):
                update_id = update["update_id"]
                if update_id in seen_update_ids:
                    continue
                seen_update_ids.add(update_id)
                message = update.get("message", {})
                text = message.get("text", "")
                from_chat_id = str(message.get("chat", {}).get("id", ""))

                if from_chat_id != chat_id:
                    continue

                if f"approve {request_id}" in text.lower():
                    return "approve"
                elif f"reject {request_id}" in text.lower():
                    return "reject"

            time.sleep(2)
        except Exception as e:
            print("⚠️ خطأ أثناء فحص الردود:", e)
            time.sleep(2)

    return "timeout"

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
            from core.utils import get_device_info
            dev = get_device_info() or {}
            device_id = dev.get('mac') or dev.get('node') or dev.get('ip') or None
        except Exception:
            device_id = None

    # --- تحقق مبكر إذا كان المستخدم موجود بالفعل وجهازه واشتراكه صالح ---
    try:
        from database.db_manager import get_user_by_username, get_subscription_dates
        from datetime import datetime
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
            # إذا كل شيء تمام → دخول مباشر بدون إرسال طلب للمطور
            print(f'✅ دخول مباشر للمستخدم {username}')
            return {'status': 'success', 'role': 'user'}
    except Exception as e:
        pass

    # التحقق من بيانات السوبر يوزر
    if check_superuser_login(username, password):
        request_id = str(uuid.uuid4())[:8]
        sent, token, chat_id = send_telegram_request(username, request_id)
        if not sent:
            return {"status": "fail", "role": None}

        decision = check_telegram_reply_polling(token, chat_id, request_id)
        if decision == "approve":
            return {"status": "success", "role": "superuser"}
        elif decision == "reject":
            print("❌ تم رفض دخول السوبر يوزر من قِبل المطور.")
            return {"status": "fail", "role": None}
        else:
            print("⌛ انتهت مهلة انتظار رد المطور.")
            return {"status": "fail", "role": None}

    # تحقق من المستخدم العادي
    if check_user(username, password):
        status = check_user_status(username)
        # إذا المستخدم في حالة pending -> أعد إرسال طلب للمطور وانتظر إدخال الأيام
        if status == "pending":
            print("📩 إرسال إشعار للمطور بخصوص مستخدم جديد...")
            ip_info = get_ip_info()
            from core import telegram_bot_manager
            try:
                running_loop = asyncio.get_running_loop()
                running_loop.create_task(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
            except RuntimeError:
                asyncio.run(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
            print("⏳ بانتظار موافقة المطور...")
            return {"status": "pending", "role": None}

        if status != "active":
            print("⚠️ المستخدم غير مفعل.")
            return {"status": "fail", "role": None}

        # التحقق من الاشتراك
        if not is_subscription_valid(username):
            print("⚠️ الاشتراك منتهي أو غير صالح.")
            return {"status": "fail", "role": None}

        # التحقق من الجهاز المسجل
        try:
            registered_device = get_device_id(username)
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
        running_loop.create_task(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
    except RuntimeError:
        asyncio.run(telegram_bot_manager.handle_new_user_request(context=None, username=username, ip_info=ip_info, device_id=device_id))
    # إضافة المستخدم الجديد إلى قائمة الانتظار لحين موافقة المطور وإدخال عدد الأيام
    pending_users[username] = {
        'approved': None,
        'finalized': False,
        'waiting_days_input': True,
        'device_id': device_id
    }
    print(f'⏳ بانتظار رد المطور وإدخال عدد الأيام لتفعيل المستخدم {username}...')
    start_wait = time.time()
    while time.time() - start_wait < 300:  # مهلة 5 دقائق
        if pending_users.get(username, {}).get('finalized'):
            if pending_users[username]['approved']:
                return {'status': 'success', 'role': 'user'}
            else:
                return {'status': 'fail', 'role': None}
        time.sleep(2)
    print('⌛ انتهت مهلة انتظار رد المطور.')
    return {'status': 'fail', 'role': None}
# قائمة انتظار تسجيل المستخدمين الجدد (قيد الموافقة من المطور)
pending_users = {}

def finalize_user_creation(username, device_id, approved=True):
    """تُستخدم بعد موافقة المطور لإنشاء المستخدم نهائيًا"""
    if username in pending_users:
        pending_users[username]['approved'] = approved
        pending_users[username]['device_id'] = device_id
        pending_users[username]['finalized'] = True
        print(f"✅ تم {'تفعيل' if approved else 'رفض'} المستخدم: {username}")
    else:
        print(f"⚠️ لا يوجد طلب معلق لهذا المستخدم: {username}")