
import sqlite3, os, sys, glob

# Try common locations for DB
candidates = [
    os.path.join(os.path.dirname(__file__), "basim_trading.db"),
    os.path.join(os.path.dirname(__file__), "database", "basim_trading.db"),
    os.path.join(os.path.dirname(__file__), "database", "basim_trading.sqlite"),
    os.path.join(os.path.dirname(__file__), "database.db"),
]

DB_PATH = None
for c in candidates:
    if os.path.exists(c):
        DB_PATH = c
        break

# fallback: search for any .db file under the project
if DB_PATH is None:
    for p in glob.glob(os.path.join(os.path.dirname(__file__), "**", "*.db"), recursive=True):
        DB_PATH = p
        break

if DB_PATH is None:
    print("Database file not found in project. Searched candidates:", candidates)
    sys.exit(1)
else:
    print("Using DB at:", DB_PATH)

def ensure_column(table, column, coltype, default=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    if column not in cols:
        default_sql = f" DEFAULT {default}" if default is not None else ""
        sql = f'ALTER TABLE {table} ADD COLUMN {column} {coltype}{default_sql}'
        cur.execute(sql)
        print(f"Added column {column} to {table}")
    else:
        print(f"Column {column} already exists in {table}")
    conn.commit()
    conn.close()

def main():
    # ensure users table has required columns used by code
    ensure_column("users", "txid", "TEXT", "NULL")
    ensure_column("users", "approved", "INTEGER", "0")
    ensure_column("users", "start_date", "TEXT", "NULL")
    ensure_column("users", "end_date", "TEXT", "NULL")

    print("init_db completed.")

if __name__ == '__main__':
    main()
    ensure_column("subscriptions", "status", "TEXT", "'فعال'")
