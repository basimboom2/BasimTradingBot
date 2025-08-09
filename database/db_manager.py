import os
import sqlite3
from datetime import datetime
from core.utils import load_key, encrypt_data, decrypt_data

DB_PATH = os.path.join(os.path.dirname(__file__), "basim_trading.db")
key = load_key()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor


def user_exists(username):
    """Return True if a user with given username exists."""
    conn, cursor = get_connection()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# ───── إنشاء الجداول ─────
def init_db():
    conn, cursor = get_connection()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_superuser INTEGER DEFAULT 0,
        device_id TEXT,
        telegram_id TEXT,
        status TEXT DEFAULT 'pending',
        txid TEXT,
        approved INTEGER DEFAULT 0,
        start_date TEXT,
        end_date TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        language TEXT DEFAULT 'en',
        theme TEXT DEFAULT 'light',
        notifications_enabled INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    conn.commit()
    conn.close()

# ───── المستخدمين ─────
def add_user(username, password, is_superuser=0, device_id=None, telegram_id=None):
    conn, cursor = get_connection()
    encrypted_password = encrypt_data(password, key)
    encrypted_device_id = encrypt_data(device_id, key) if device_id else None
    cursor.execute("""
    INSERT INTO users (username, password, is_superuser, device_id, telegram_id)
    VALUES (?, ?, ?, ?, ?)
    """, (username, encrypted_password, is_superuser, encrypted_device_id, telegram_id))
    conn.commit()
    conn.close()

def check_user(username, password):
    conn, cursor = get_connection()
    cursor.execute("SELECT password, status FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        encrypted, status = row
        try:
            if decrypt_data(encrypted, key) == password and status == "active":
                return True
        except:
            pass
    return False

def check_user_status(username):
    conn, cursor = get_connection()
    cursor.execute("SELECT status FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def activate_user(username):
    conn, cursor = get_connection()
    cursor.execute("UPDATE users SET status='active' WHERE username=?", (username,))
    conn.commit()
    conn.close()

def reject_user(username):
    conn, cursor = get_connection()
    cursor.execute("UPDATE users SET status='rejected' WHERE username=?", (username,))
    conn.commit()
    conn.close()

def update_user_password(username, new_password):
    conn, cursor = get_connection()
    encrypted = encrypt_data(new_password, key)
    cursor.execute("UPDATE users SET password=? WHERE username=?", (encrypted, username))
    conn.commit()
    conn.close()

def delete_user(username):
    conn, cursor = get_connection()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

def set_device_id(username, device_id):
    conn, cursor = get_connection()
    encrypted_device_id = encrypt_data(device_id, key)
    cursor.execute("UPDATE users SET device_id=? WHERE username=?", (encrypted_device_id, username))
    conn.commit()
    conn.close()

def get_device_id(username):
    conn, cursor = get_connection()
    cursor.execute("SELECT device_id FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return decrypt_data(row[0], key)
        except Exception:
            return None
    return None

# ───── الاشتراكات ─────
def add_subscription(user_id, start_date, end_date):
    conn, cursor = get_connection()
    cursor.execute("""
    INSERT INTO subscriptions (user_id, start_date, end_date)
    VALUES (?, ?, ?)
    """, (user_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_active_subscription(user_id):
    conn, cursor = get_connection()
    cursor.execute("""
    SELECT start_date, end_date FROM subscriptions
    WHERE user_id=? AND is_active=1
    ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def cancel_subscription(user_id):
    conn, cursor = get_connection()
    cursor.execute("UPDATE subscriptions SET is_active=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# ───── الإعدادات ─────
def get_user_settings(user_id):
    conn, cursor = get_connection()
    cursor.execute("SELECT language, theme, notifications_enabled FROM user_settings WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else ("en", "light", 1)

def update_user_settings(user_id, language=None, theme=None, notifications_enabled=None):
    conn, cursor = get_connection()
    cursor.execute("SELECT id FROM user_settings WHERE user_id=?", (user_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""
        UPDATE user_settings SET language=?, theme=?, notifications_enabled=?
        WHERE user_id=?
        """, (language, theme, notifications_enabled, user_id))
    else:
        cursor.execute("""
        INSERT INTO user_settings (user_id, language, theme, notifications_enabled)
        VALUES (?, ?, ?, ?)
        """, (user_id, language, theme, notifications_enabled))
    conn.commit()
    conn.close()

# ───── السجلات ─────
def log_action(user_id, action):
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO activity_logs (user_id, action) VALUES (?, ?)", (user_id, action))
    conn.commit()
    conn.close()

# ───── تنفيذ مباشر ─────
if __name__ == "__main__":
    init_db()
    print("✅ تم إنشاء قاعدة البيانات والجداول بنجاح.")

# ───── دوال متقدمة للمشروع ─────

def insert_user_with_subscription(username, password, device_id, start_date, end_date):
    conn, cursor = get_connection()
    try:
        # Check if username already exists - avoid UNIQUE constraint problems
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        if existing:
            # user already exists - do not insert again
            return {"status": "exists", "user_id": existing[0]}

        encrypted_password = encrypt_data(password, key)
        encrypted_device_id = encrypt_data(device_id, key) if device_id else None
        cursor.execute("""
            INSERT INTO users (username, password, is_superuser, device_id, status)
            VALUES (?, ?, 0, ?, 'active')
        """, (username, encrypted_password, encrypted_device_id))
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO subscriptions (user_id, start_date, end_date, is_active)
            VALUES (?, ?, ?, 1)
        """, (user_id, start_date, end_date))
        conn.commit()
        return {"status": "created", "user_id": user_id}
    finally:
        conn.close()

def get_subscription_dates(username):
    conn, cursor = get_connection()
    cursor.execute("""
        SELECT s.start_date, s.end_date
        FROM subscriptions s
        JOIN users u ON s.user_id = u.id
        WHERE u.username = ? AND s.is_active = 1
        ORDER BY s.id DESC LIMIT 1
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None)

def get_user_id(username):
    conn, cursor = get_connection()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_user_device_id(username):
    conn, cursor = get_connection()
    cursor.execute("SELECT device_id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return decrypt_data(row[0], key)
        except Exception:
            return None
    return None

def set_user_device_id(username, device_id):
    conn, cursor = get_connection()
    encrypted_device_id = encrypt_data(device_id, key)
    cursor.execute("UPDATE users SET device_id = ? WHERE username = ?", (encrypted_device_id, username))
    conn.commit()
    conn.close()

def update_user_status(username, status):
    conn, cursor = get_connection()
    cursor.execute("UPDATE users SET status = ? WHERE username = ?", (status, username))
    conn.commit()
    conn.close()

def approve_user(username):
    conn, cursor = get_connection()
    cursor.execute("UPDATE users SET approved = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def save_txid_for_user(username, txid):
    conn, cursor = get_connection()
    cursor.execute("UPDATE users SET txid = ? WHERE username = ?", (txid, username))
    conn.commit()
    conn.close()


def update_subscription_status(username, start=None, end=None, is_renewal=False):
    print(f"⚙️ تحديث الاشتراك: {username} من {start} إلى {end} (is_renewal={is_renewal})")
    username = username.strip().split()[1] if username.startswith("renew") else username
    conn, cursor = get_connection()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_row = cursor.fetchone()
    if user_row:
        user_id = user_row[0]

        cursor.execute("SELECT id FROM subscriptions WHERE user_id = ?", (user_id,))
        sub_exists = cursor.fetchone()

        if start and end:
            if sub_exists:
                cursor.execute("""
                    UPDATE subscriptions
                    SET start_date = ?, end_date = ?, is_active = 1
                    WHERE user_id = ?
                """, (start, end, user_id))
            else:
                cursor.execute("""
                    INSERT INTO subscriptions (user_id, start_date, end_date, is_active)
                    VALUES (?, ?, ?, 1)
                """, (user_id, start, end))

        # إذا كان تحديث بسبب تجديد، لا تعدل حالة المستخدم
        if not is_renewal:
            cursor.execute(
                "UPDATE users SET status = ?, approved = ? WHERE username = ?",
                ("فعال", 1, username)
            )

        conn.commit()
    conn.close()


# ───── دالة التحقق من الاشتراك (للاستخدام في الواجهة والمشروع) ─────
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
        # باقي أكواد db_manager الأصلية هنا...

# ───────────────────────────────
# دالة الحصول على بيانات المستخدم حسب اسم المستخدم
def get_user_by_username(username):
    """
    ترجع بيانات المستخدم من جدول users حسب اسم المستخدم.
    تعيد None إذا لم يتم العثور على المستخدم.
    """
    conn, cursor = get_connection()
    cursor.execute("""
        SELECT id, username, password, is_superuser, device_id, telegram_id, status, txid, approved, start_date, end_date
        FROM users
        WHERE username = ?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    return row
