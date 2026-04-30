import sqlite3


# Connect to SQLite database
conn = sqlite3.connect("guestflow.db", check_same_thread=False)

# Cursor helps execute SQL commands
cursor = conn.cursor()


# Create guest_events table
cursor.execute("""
CREATE TABLE IF NOT EXISTS guest_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT,
    event_type TEXT
)
""")

conn.commit()