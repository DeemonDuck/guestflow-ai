import os
import re
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("GMAIL_SENDER")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT = os.getenv("GMAIL_RECIPIENT")

# Basic single-address email shape (no spaces/newlines allowed)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean_header(value: str) -> str:
    """Strip CR/LF so user-supplied values can't inject extra email headers."""
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def _valid_email(address: str) -> bool:
    return bool(address) and bool(_EMAIL_RE.match(address))


def send_email_tool(
    guest_name: str,
    message: str,
    room_number: str = "N/A",
    category: str = "General",
    priority: str = "Normal",
    time: str = "N/A",
    recipient: str = None
) -> dict:

    # Fall back to the generic mailbox if no explicit recipient is given
    to_address = recipient or RECIPIENT

    # Reject malformed / injection-bearing recipients before sending
    if not _valid_email(to_address):
        print("EMAIL SKIPPED: invalid recipient address")
        return {"status": "email_failed", "error": "invalid recipient address"}

    # Sanitize every value that lands in a header to prevent header injection
    s_priority = _clean_header(priority)
    s_category = _clean_header(category)
    s_room = _clean_header(room_number)
    s_guest = _clean_header(guest_name)

    subject = f"[{s_priority}] {s_category} Request — Room {s_room} ({s_guest})"

    body = f"""
Guest Request Details
---------------------
Guest     : {guest_name}
Room      : {room_number}
Category  : {category}
Priority  : {priority}
Time      : {time}

Message:
{message}
""".strip()

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = to_address

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, APP_PASSWORD)
            server.sendmail(SENDER, to_address, msg.as_string())

        # Avoid logging PII (recipient address / guest name) in plain logs
        print(f"EMAIL SENT — {s_category} | {s_priority}")
        return {
            "status": "email_sent",
            "guest": guest_name,
            "recipient": to_address,
            "room": room_number,
            "category": category,
            "priority": priority
        }

    except Exception as e:
        # Log details server-side only; do not leak them back to the caller
        print(f"EMAIL FAILED: {type(e).__name__}")
        return {"status": "email_failed", "error": "email delivery failed"}
