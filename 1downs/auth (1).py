
from database.db_manager import get_connection
from datetime import datetime

def login(username, password):
    conn, cursor = get_connection()
    cursor.execute("SELECT id, username, password, status, approved FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        # مستخدم جديد → بانتظار الموافقة
        return {"status": "waiting_approval"}

    user_id, db_username, db_password, status, approved = row

    if password != db_password:
        return {"status": "fail"}

    # التحقق من الاشتراك
    cursor.execute("SELECT start_date, end_date FROM subscriptions WHERE user_id = ?", (user_id,))
    sub_row = cursor.fetchone()
    if not sub_row:
        return {"status": "expired"}

    start_date, end_date = sub_row
    if datetime.fromisoformat(end_date) < datetime.now():
        return {"status": "expired"}

    # إذا كان قيد المراجعة
    if approved == 0 or status == "معلق":
        return {"status": "waiting_approval"}

    # إذا سوبر يوزر
    if status == "superuser":
        return {"status": "superuser"}

    return {"status": "active"}
