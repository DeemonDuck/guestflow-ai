"""Populate the database with realistic demo data.

Run this before a demo so the dashboard looks alive (tickets in every state,
profiles, feedback) instead of empty:

    python seed_demo.py

It is non-destructive: profiles are merge-upserted, and ticket/feedback seeding
is skipped if demo data is already present, so re-running it is safe.
"""
from datetime import datetime, timedelta

from database.db import conn, cursor
from tools.profile_tool import save_profile

DEMO_GUESTS = ["Rahul Sharma", "Priya Nair", "Amit Verma", "Sara Khan"]


def _iso(dt):
    return dt.isoformat(timespec="seconds")


def seed():
    now = datetime.now()

    # --- Profiles (merge upsert — safe to re-run) ---
    save_profile(
        "Rahul Sharma",
        contact_email="rahul@example.com",
        preferences="High floor, extra pillows",
        is_vip=True,
        notes="Anniversary in August",
    )
    save_profile(
        "Priya Nair",
        contact_email="priya@example.com",
        preferences="Vegetarian breakfast, quiet room",
    )
    save_profile(
        "Amit Verma",
        contact_email="amit@example.com",
        preferences="Early check-in",
    )
    # Sara Khan intentionally has no profile (first-time guest).

    # --- Avoid duplicating ticket/feedback rows on re-run ---
    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE guest_name IN (?, ?, ?, ?)",
        tuple(DEMO_GUESTS),
    )
    if cursor.fetchone()[0] > 0:
        conn.commit()
        print("Demo tickets/feedback already present — profiles refreshed, skipping the rest.")
        return

    # --- Tickets in every lifecycle state ---
    # (guest, room, category, priority, issue, status, created_min_ago, updated_min_ago, escalated)
    tickets = [
        ("Rahul Sharma", "101", "Maintenance", "High", "AC not cooling", "resolved", 120, 95, 0),
        ("Priya Nair", "204", "Housekeeping", "Normal", "Need extra towels", "resolved", 60, 52, 0),
        ("Amit Verma", "309", "Maintenance", "High", "Hot water not working", "in_progress", 45, 40, 0),
        ("Sara Khan", "410", "Front Desk", "Normal", "Late checkout request", "open", 10, 10, 0),
        ("Priya Nair", "204", "Maintenance", "High", "TV remote broken", "open", 90, 90, 1),  # stale + escalated
    ]
    for g, room, cat, pri, issue, status, c_off, u_off, esc in tickets:
        cursor.execute(
            "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (g, room, cat, pri, issue, status,
             _iso(now - timedelta(minutes=c_off)),
             _iso(now - timedelta(minutes=u_off)), esc),
        )

    # --- Feedback (mix of sentiment) ---
    feedback = [
        ("Rahul Sharma", 5, "Wonderful stay, the staff were great!", "positive", 0),
        ("Priya Nair", 4, "Comfortable and clean.", "positive", 0),
        ("Amit Verma", 2, "Hot water issue took too long to fix.", "negative", 1),
        ("Sara Khan", 3, "Average experience.", "neutral", 0),
    ]
    for g, rating, comment, sentiment, alerted in feedback:
        cursor.execute(
            "INSERT INTO feedback (guest_name,rating,comment,sentiment,manager_alerted,created_at)"
            " VALUES (?,?,?,?,?,?)",
            (g, rating, comment, sentiment, alerted, _iso(now)),
        )

    # --- Some prior events so guest history isn't empty ---
    for g in ["Rahul Sharma", "Priya Nair", "Amit Verma"]:
        cursor.execute(
            "INSERT INTO guest_events (guest_name, event_type) VALUES (?, 'booking_confirmed')",
            (g,),
        )

    conn.commit()
    print("Seeded demo data: 3 profiles, 5 tickets (open/in_progress/resolved/escalated), 4 feedback entries.")


if __name__ == "__main__":
    seed()
