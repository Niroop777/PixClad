import sqlite3
import config

conn = sqlite3.connect(config.DATABASE)
cursor = conn.cursor()

# ✅ Create users table (if not exists)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# ✅ Check if 'reset_requested_at' column exists, if not, add it

cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
if "reset_requested_at" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN reset_requested_at TIMESTAMP DEFAULT NULL")
    conn.commit()
    print("✅ Added 'reset_requested_at' column to users table.")

conn.close()
print("✅ SQLite database and users table setup complete!")
