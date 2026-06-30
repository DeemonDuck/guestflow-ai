import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("GMAIL_SENDER")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT = os.getenv("GMAIL_RECIPIENT")


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

    subject = f"[{priority}] {category} Request — Room {room_number} ({guest_name})"

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

        print(f"\n EMAIL SENT — to {to_address} | Room {room_number} | {category} | {priority}")
        return {
            "status": "email_sent",
            "guest": guest_name,
            "recipient": to_address,
            "room": room_number,
            "category": category,
            "priority": priority
        }

    except Exception as e:
        print(f"\n EMAIL FAILED: {e}")
        return {"status": "email_failed", "error": str(e)}
