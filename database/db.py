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

# Create tickets table (guest issues that need to be tracked to resolution)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL,
    room_number TEXT,
    category TEXT,
    priority TEXT,
    issue TEXT,
    status TEXT DEFAULT 'open',
    created_at TEXT,
    updated_at TEXT
)
""")

conn.commit()