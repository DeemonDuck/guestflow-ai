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
    updated_at TEXT,
    escalated INTEGER DEFAULT 0
)
""")

# Migration: add 'escalated' column to tickets tables created before this field
cursor.execute("PRAGMA table_info(tickets)")
_ticket_columns = [c[1] for c in cursor.fetchall()]
if "escalated" not in _ticket_columns:
    cursor.execute("ALTER TABLE tickets ADD COLUMN escalated INTEGER DEFAULT 0")

# Create guest_profiles table (durable per-guest preferences & contact info)
cursor.execute("""
CREATE TABLE IF NOT EXISTS guest_profiles (
    guest_name TEXT PRIMARY KEY,
    contact_email TEXT,
    preferences TEXT,
    is_vip INTEGER DEFAULT 0,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
)
""")

# Create feedback table (post-stay guest feedback for review management)
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL,
    rating INTEGER,
    comment TEXT,
    sentiment TEXT,
    manager_alerted INTEGER DEFAULT 0,
    created_at TEXT
)
""")

conn.commit()