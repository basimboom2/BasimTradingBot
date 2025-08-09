from Crypto.Random import get_random_bytes

def generate_key():
    key = get_random_bytes(32)  # AES-256
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("✅ تم إنشاء مفتاح التشفير (AES-256) وحفظه في secret.key")

if __name__ == "__main__":
    generate_key()