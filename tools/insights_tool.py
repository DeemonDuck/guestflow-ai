"""Proactive operations intelligence.

Turns the data GuestFlow already stores (tickets + feedback) into patterns a
busy manager would otherwise miss:

* systemic issues   — a cluster of similar tickets in the same area/time window
* repeat rooms      — a single room generating many tickets
* feedback themes   — a topic recurring across negative reviews

Most "hotel AI" stops at answering guests. This is the bit that tells the hotel
what is *about* to become a problem.
"""
from collections import defaultdict
from datetime import datetime, timedelta

from database.db import cursor

# Tunable detection thresholds
SYSTEMIC_WINDOW_HOURS = 24      # look-back window for clustering
SYSTEMIC_THRESHOLD = 3          # >= N similar tickets in window -> systemic
REPEAT_ROOM_THRESHOLD = 3       # >= N tickets for one room -> repeat offender
FEEDBACK_THEME_THRESHOLD = 2    # >= N negative reviews on a theme -> trend

# Negative-feedback theme keywords
_THEMES = {
    "cleanliness": ["dirty", "unclean", "dust", "stain", "not clean"],
    "noise": ["noisy", "noise", "loud"],
    "staff/service": ["rude", "staff", "service", "unhelpful"],
    "wifi/internet": ["wifi", "internet", "connection"],
    "food/breakfast": ["food", "breakfast", "meal"],
    "temperature": ["ac", "cooling", "hot water", "cold", "heating"],
    "speed/waiting": ["slow", "late", "wait", "long", "delay"],
}


def _floor(room):
    if room and str(room)[:1].isdigit():
        return str(room)[0]
    return None


def _insight(kind, severity, message):
    return {"type": kind, "severity": severity, "message": message}


def get_insights() -> list:
    insights = []

    cursor.execute("SELECT room_number, category, status, created_at FROM tickets")
    tickets = cursor.fetchall()

    # --- Systemic issues: cluster of same category on same floor in window ---
    cutoff = datetime.now() - timedelta(hours=SYSTEMIC_WINDOW_HOURS)
    clusters = defaultdict(int)
    for room, category, status, created_at in tickets:
        try:
            created = datetime.fromisoformat(created_at)
        except (TypeError, ValueError):
            continue
        if created < cutoff:
            continue
        floor = _floor(room)
        if floor is None:
            continue
        clusters[(category, floor)] += 1

    for (category, floor), count in clusters.items():
        if count >= SYSTEMIC_THRESHOLD:
            insights.append(_insight(
                "systemic_issue",
                "high",
                f"Possible systemic issue: {count} '{category}' tickets on floor "
                f"{floor} in the last {SYSTEMIC_WINDOW_HOURS}h — likely one root cause.",
            ))

    # --- Repeat rooms: a single room with many tickets overall ---
    per_room = defaultdict(int)
    for room, category, status, created_at in tickets:
        if room and room != "N/A":
            per_room[room] += 1
    for room, count in per_room.items():
        if count >= REPEAT_ROOM_THRESHOLD:
            insights.append(_insight(
                "repeat_room",
                "medium",
                f"Room {room} has generated {count} tickets — may need a deeper fix.",
            ))

    # --- Recurring negative feedback themes ---
    cursor.execute("SELECT comment FROM feedback WHERE sentiment = 'negative'")
    comments = [c[0].lower() for c in cursor.fetchall() if c[0]]
    theme_counts = defaultdict(int)
    for comment in comments:
        for theme, keywords in _THEMES.items():
            if any(k in comment for k in keywords):
                theme_counts[theme] += 1
    for theme, count in theme_counts.items():
        if count >= FEEDBACK_THEME_THRESHOLD:
            insights.append(_insight(
                "feedback_theme",
                "medium",
                f"'{theme}' came up in {count} negative reviews — a recurring theme to address.",
            ))

    return insights
