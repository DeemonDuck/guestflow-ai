"""Manager daily digest.

Composes a short operations briefing from the data GuestFlow already has
(analytics + proactive insights) and emails it to the manager. Point a scheduler
at POST /digest/run to make it a true "morning brief".
"""
from config import HOTEL_NAME, MANAGER_EMAIL
from tools.analytics_tool import get_analytics
from tools.insights_tool import get_insights
from tools.email_tool import send_email_tool


def compose_digest() -> str:
    """Build the plain-text digest body from current data."""
    a = get_analytics()
    t = a["tickets"]
    f = a["feedback"]
    insights = get_insights()

    lines = [
        f"{HOTEL_NAME} — Operations Digest",
        "=" * 40,
        "",
        "TICKETS",
        f"  Open:         {t['open']}",
        f"  In progress:  {t['in_progress']}",
        f"  Resolved:     {t['resolved']}",
        f"  Escalated:    {t['escalated']}",
    ]
    if t["avg_resolution_minutes"] is not None:
        lines.append(f"  Avg resolution: {t['avg_resolution_minutes']} min")

    lines += [
        "",
        "FEEDBACK",
        f"  Responses:    {f['total']}",
        f"  Avg rating:   {f['avg_rating'] if f['avg_rating'] is not None else 'n/a'}",
        f"  Negative:     {f['negative']}",
        "",
        "INSIGHTS (what may need attention)",
    ]
    if insights:
        for item in insights:
            lines.append(f"  [{item['severity'].upper()}] {item['message']}")
    else:
        lines.append("  No issues detected — operations look healthy.")

    return "\n".join(lines)


def send_digest(recipient: str = None) -> dict:
    """Compose the digest and email it to the manager."""
    body = compose_digest()
    result = send_email_tool(
        guest_name="Manager",
        message=body,
        category="Operations Digest",
        priority="Normal",
        recipient=recipient or MANAGER_EMAIL,
    )
    return {"status": "digest_sent", "email": result, "body": body}
