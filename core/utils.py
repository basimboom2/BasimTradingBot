import requests
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import platform
import uuid
import socket

# --- دوال التشفير العامة باستخدام AES-256 ---

KEY_FILE = "secret.key"

def pad(data: bytes) -> bytes:
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def generate_key_file(filename=KEY_FILE):
    """توليد مفتاح وحفظه في ملف (AES-256)"""
    key = get_random_bytes(32)  # 256 بت
    with open(filename, "wb") as f:
        f.write(key)
    print(f"✅ تم إنشاء المفتاح في {filename}")

def load_key():
    """تحميل مفتاح التشفير الرئيسي من ملف secret.key"""
    if not os.path.exists(KEY_FILE):
        generate_key_file(KEY_FILE)
    return open(KEY_FILE, "rb").read()

def encrypt_data(data, key=None):
    """تشفير نص باستخدام AES-256 + IV عشوائي + PKCS7 Padding"""
    key = key or load_key()
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw = pad(data.encode())
    enc = cipher.encrypt(raw)
    return base64.b64encode(iv + enc).decode()

def decrypt_data(token, key=None):
    """فك تشفير نص باستخدام AES-256 + IV"""
    key = key or load_key()
    raw = base64.b64decode(token)
    iv = raw[:16]
    enc = raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = cipher.decrypt(enc)
    return unpad(dec).decode()

# --- دوال السوبر يوزر ---

SUPERUSER_KEY_FILE = "superuser.key"
SUPERUSER_DATA_FILE = "superuser.dat"

def generate_superuser_key():
    key = get_random_bytes(32)
    with open(SUPERUSER_KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_superuser_key():
    """تحميل مفتاح السوبر يوزر من ملف superuser.key"""
    if not os.path.exists(SUPERUSER_KEY_FILE):
        generate_superuser_key()
    return open(SUPERUSER_KEY_FILE, "rb").read()

def check_superuser_login(input_username, input_password):
    """التحقق من بيانات السوبر يوزر (اسم المستخدم وكلمة المرور)"""
    try:
        key = load_superuser_key()
        with open(SUPERUSER_DATA_FILE, "r") as fobj:
            token = fobj.read()
        data = decrypt_data(token, key)
        username, password = data.split(":", 1)
        return input_username == username and input_password == password
    except Exception:
        return False

def generate_superuser_data_interactive():
    """توليد بيانات سوبر يوزر مع تحقق من صلاحية الوصول"""
    import getpass

    admin_passcode = getpass.getpass("🛡️ أدخل رمز المدير لتوليد السوبر يوزر: ").strip()
    if admin_passcode != "MyAdminPass987!":
        print("❌ رمز المدير غير صحيح. تم إلغاء العملية.")
        return

    username = input("🧑‍💼 أدخل اسم السوبر يوزر: ").strip()
    password = getpass.getpass("🔒 أدخل كلمة المرور: ").strip()

    key = generate_superuser_key()
    enc = encrypt_data(f"{username}:{password}", key)

    with open(SUPERUSER_DATA_FILE, "w") as f:
        f.write(enc)

    print("✅ تم إنشاء ملفات السوبر يوزر بنجاح.")

# --- تشفير بيانات المطور (تليجرام) ---

DEV_INFO_FILE = "core/dev_info.dat"

def encrypt_dev_info_interactive():
    bot_token = input("🤖 أدخل bot token: ").strip()
    developer_chat_id = input("🧑‍💼 أدخل Telegram chat ID للمطور: ").strip()
    key = load_key()
    combined = f"{bot_token}###{developer_chat_id}"
    enc = encrypt_data(combined, key)
    with open(DEV_INFO_FILE, "w") as fobj:
        fobj.write(enc)
    print("✅ تم إنشاء ملف dev_info.dat المشفر بنجاح.")

def decrypt_dev_info():
    try:
        key = load_key()
        with open(DEV_INFO_FILE, "r") as fobj:
            enc = fobj.read()
        decrypted = decrypt_data(enc, key)
        bot_token, chat_id = decrypted.split("###", 1)
        return bot_token, chat_id
    except Exception as e:
        print("❌ فشل في فك تشفير dev_info:", str(e))
        return None, None

# --- تنفيذ مباشر ---

if __name__ == "__main__":
    print("🔐 إعداد مفاتيح المشروع")
    generate_key_file(KEY_FILE)
    generate_superuser_data_interactive()
    encrypt_dev_info_interactive()

# --- معلومات الجهاز وIP وMAC والنظام ---

def get_ip_info():
    """جلب عنوان IP والموقع الجغرافي للعميل"""
    try:
        res = requests.get("https://ipapi.co/json/")
        if res.status_code != 200:
            return {
                "ip": "unknown",
                "city": "unknown",
                "country": "unknown"
            }
        data = res.json()
        return {
            "ip": data.get("ip", "unknown"),
            "city": data.get("city", "unknown"),
            "country": data.get("country_name", "unknown")
        }
    except Exception:
        return {
            "ip": "error",
            "city": "error",
            "country": "error"
        }

def get_device_info():
    """جلب معلومات الجهاز: اسم النظام، اسم المضيف، MAC، عنوان IP"""
    try:
        device_info = {
            "node": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "mac": ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(0,8*6,8)][::-1]),
            "ip": socket.gethostbyname(socket.gethostname())
        }
        geo = get_ip_info()
        device_info.update(geo)
        return device_info
    except Exception as e:
        return {"error": str(e)}