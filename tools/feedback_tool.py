"""Review / feedback management.

COMPLIANCE NOTE (read before changing this file):
The public review invitation is sent to EVERY guest, regardless of rating or
sentiment. It is never conditioned on a positive rating. Selectively soliciting
public reviews only from happy guests ("review gating") violates Google's review
policies and FTC guidance and is intentionally NOT done here.

Negative feedback triggers a private internal alert to the manager so the hotel
can recover the guest experience quickly. This is an internal operations signal
only — it never suppresses, blocks or diverts the guest's ability to post a
public review.
"""
from datetime import datetime

from database.db import conn, cursor
from tools.email_tool import send_email_tool
from tools.profile_tool import get_profile
from config import (
    HOTEL_NAME,
    MANAGER_EMAIL,
    REVIEW_LINK,
    REVIEW_ALERT_THRESHOLD,
)

# Words that suggest an unhappy guest when no numeric rating is given
_NEGATIVE_WORDS = [
    "bad", "terrible", "awful", "worst", "dirty", "rude", "poor",
    "disappointed", "disappointing", "horrible", "complaint", "refund",
    "unhappy", "noisy", "broken", "cold", "slow", "never again",
]


def _classify(rating, comment) -> str:
    """Return 'negative', 'positive' or 'neutral'.

    Used only to decide whether to alert the manager — NOT to decide who is
    allowed to leave a public review.
    """
    if rating is not None:
        if rating <= REVIEW_ALERT_THRESHOLD:
            return "negative"
        return "positive"

    if comment:
        text = comment.lower()
        if any(word in text for word in _NEGATIVE_WORDS):
            return "negative"

    return "neutral"


def request_feedback(guest_name: str, recipient: str = None) -> dict:
    """Ask a guest for feedback after checkout.

    The public review link (if configured) is included for EVERY guest.
    """
    # Prefer the guest's own email; the recipient override / env fallback
    # is handled downstream by send_email_tool.
    if recipient is None:
        profile = get_profile(guest_name)
        recipient = profile.get("contact_email") if profile else None

    review_line = (
        f"\n\nIf you have a moment, we'd be grateful if you'd share your "
        f"experience here: {REVIEW_LINK}"
        if REVIEW_LINK else ""
    )

    message = (
        f"Hi {guest_name}, thank you for staying with {HOTEL_NAME}! "
        f"We'd love to hear how your stay was — your feedback helps us improve."
        f"{review_line}"
    )

    return send_email_tool(
        guest_name=guest_name,
        message=message,
        category="Post-Stay Feedback",
        priority="Normal",
        recipient=recipient,
    )


def submit_feedback(guest_name: str, rating: int = None, comment: str = None) -> dict:
    """Record a guest's feedback and alert the manager if it looks negative."""
    sentiment = _classify(rating, comment)
    now = datetime.now().isoformat(timespec="seconds")

    manager_alerted = 0
    alert_result = None

    # Service recovery: privately notify the manager about unhappy guests.
    if sentiment == "negative":
        alert_result = send_email_tool(
            guest_name=guest_name,
            message=(
                f"NEGATIVE FEEDBACK from {guest_name}.\n"
                f"Rating: {rating if rating is not None else 'n/a'}\n"
                f"Comment: {comment or '(none)'}\n\n"
                f"Reach out to recover the guest experience before they leave a "
                f"public review."
            ),
            category="Guest Feedback Alert",
            priority="High",
            recipient=MANAGER_EMAIL,
        )
        manager_alerted = 1

    cursor.execute(
        """
        INSERT INTO feedback (guest_name, rating, comment, sentiment, manager_alerted, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (guest_name, rating, comment, sentiment, manager_alerted, now)
    )
    conn.commit()
    feedback_id = cursor.lastrowid

    print(f"\n FEEDBACK #{feedback_id} — {guest_name} — {sentiment}")

    return {
        "status": "feedback_recorded",
        "feedback_id": feedback_id,
        "guest_name": guest_name,
        "rating": rating,
        "sentiment": sentiment,
        "manager_alerted": bool(manager_alerted),
        "manager_alert": alert_result,
        "created_at": now,
    }


def list_feedback() -> list:
    cursor.execute("SELECT * FROM feedback ORDER BY id DESC")
    rows = cursor.fetchall()
    return [
        {
            "feedback_id": r[0],
            "guest_name": r[1],
            "rating": r[2],
            "comment": r[3],
            "sentiment": r[4],
            "manager_alerted": bool(r[5]),
            "created_at": r[6],
        }
        for r in rows
    ]
