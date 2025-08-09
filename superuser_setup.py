# superuser_setup.py
from Crypto.Random import get_random_bytes
from core.utils import encrypt_data

def generate_key():
    key = get_random_bytes(32)  # AES-256
    with open("superuser.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    return open("superuser.key", "rb").read()

def encrypt_superuser(username, password, key):
    data = f"{username}:{password}"
    token = encrypt_data(data, key)
    with open("superuser.dat", "w") as fobj:
        fobj.write(token)
    print("✅ تم إنشاء ملف superuser.dat المشفر.")

if __name__ == "__main__":
    # شغّل هذا الملف مرة واحدة فقط
    key = generate_key()
    username = input("أدخل اسم السوبر يوزر: ")
    password = input("أدخل كلمة مرور السوبر يوزر: ")
    encrypt_superuser(username, password, key)