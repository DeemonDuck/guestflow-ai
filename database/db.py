import os
import sqlite3


# DB path is configurable so tests can run against an isolated temporary
# database (set GUESTFLOW_DB before import). Defaults to the app database.
DB_PATH = os.getenv("GUESTFLOW_DB", "guestflow.db")

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# WAL mode allows concurrent readers alongside a writer, and a busy timeout lets
# operations wait briefly for a lock instead of failing — safer under load.
# (A real production deployment should move to Postgres; this is a mitigation.)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA busy_timeout=5000")

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