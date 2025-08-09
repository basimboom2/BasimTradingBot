import sqlite3

db_path = "database/basim_trading.db"  # عدله حسب مكانك

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

username = "30"  # عدله حسب المستخدم اللي بتجرب عليه

# 1. هل المستخدم موجود؟
cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
user = cursor.fetchone()
print("👤 USER:", user)

if user:
    user_id = user[0]
    # 2. هل لديه اشتراك؟
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
    sub = cursor.fetchone()
    print("📦 SUBSCRIPTION:", sub)
else:
    print("❌ المستخدم غير موجود")

conn.close()