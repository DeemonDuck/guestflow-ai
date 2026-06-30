"""Owner-facing analytics: the ROI picture for the hotel.

Aggregates the operational data GuestFlow already stores (tickets + feedback)
into the handful of numbers an owner cares about: how much work was handled,
how fast issues were resolved, how often things escalated, and the rating trend.
"""
from datetime import datetime

from database.db import cursor


def _parse(ts):
    try:
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def get_analytics() -> dict:
    # ---- Tickets ----
    cursor.execute("SELECT status, created_at, updated_at, escalated FROM tickets")
    rows = cursor.fetchall()

    total = len(rows)
    by_status = {"open": 0, "in_progress": 0, "resolved": 0}
    resolution_minutes = []
    escalated = 0

    for status, created, updated, esc in rows:
        by_status[status] = by_status.get(status, 0) + 1
        if esc:
            escalated += 1
        if status == "resolved":
            c, u = _parse(created), _parse(updated)
            if c and u:
                resolution_minutes.append((u - c).total_seconds() / 60)

    resolved = by_status.get("resolved", 0)
    avg_resolution = (
        round(sum(resolution_minutes) / len(resolution_minutes), 1)
        if resolution_minutes else None
    )
    resolution_rate = round(resolved / total * 100, 1) if total else None

    # ---- Feedback ----
    cursor.execute("SELECT rating, sentiment FROM feedback")
    frows = cursor.fetchall()
    ratings = [r for r, _ in frows if r is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    return {
        "tickets": {
            "total": total,
            "open": by_status.get("open", 0),
            "in_progress": by_status.get("in_progress", 0),
            "resolved": resolved,
            "resolution_rate_pct": resolution_rate,
            "avg_resolution_minutes": avg_resolution,
            "escalated": escalated,
        },
        "feedback": {
            "total": len(frows),
            "avg_rating": avg_rating,
            "positive": sum(1 for _, s in frows if s == "positive"),
            "negative": sum(1 for _, s in frows if s == "negative"),
        },
    }
