from datetime import datetime, timedelta

from database.db import conn, cursor
from tools.email_tool import send_email_tool
from tools.profile_tool import get_profile
from config import MANAGER_EMAIL


def create_ticket_tool(
    guest_name: str,
    issue: str,
    room_number: str = "N/A",
    category: str = "General",
    priority: str = "Normal",
    time: str = "N/A"
) -> dict:

    now = datetime.now().isoformat(timespec="seconds")

    # Persist the ticket so it can be tracked, assigned and resolved later
    cursor.execute(
        """
        INSERT INTO tickets
            (guest_name, room_number, category, priority, issue, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'open', ?, ?)
        """,
        (guest_name, room_number, category, priority, issue, now, now)
    )
    conn.commit()

    ticket_id = cursor.lastrowid

    print(f"\n SUPPORT TICKET CREATED  (#{ticket_id})")
    print(f"Guest    : {guest_name}")
    print(f"Room     : {room_number}")
    print(f"Category : {category}")
    print(f"Priority : {priority}")
    print(f"Status   : open")
    print(f"Issue    : {issue}")

    return {
        "status": "ticket_created",
        "ticket_id": ticket_id,
        "ticket_status": "open",
        "guest": guest_name,
        "room": room_number,
        "category": category,
        "priority": priority,
        "issue": issue,
        "created_at": now
    }


# Valid lifecycle states a ticket can move through
ALLOWED_STATUSES = ["open", "in_progress", "resolved"]


def _row_to_ticket(row) -> dict:
    return {
        "ticket_id": row[0],
        "guest_name": row[1],
        "room_number": row[2],
        "category": row[3],
        "priority": row[4],
        "issue": row[5],
        "ticket_status": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }


def list_tickets(status: str = None) -> list:
    """Return tickets, optionally filtered by status (e.g. 'open')."""
    if status:
        cursor.execute(
            "SELECT * FROM tickets WHERE status = ? ORDER BY id DESC",
            (status,)
        )
    else:
        cursor.execute("SELECT * FROM tickets ORDER BY id DESC")

    return [_row_to_ticket(row) for row in cursor.fetchall()]


def update_ticket_status(ticket_id: int, new_status: str) -> dict:
    """Move a ticket to a new lifecycle state.

    When a ticket transitions to 'resolved', automatically follow up with the
    guest to confirm the issue is actually fixed (closing the loop).
    """
    if new_status not in ALLOWED_STATUSES:
        return {
            "status": "error",
            "message": f"Invalid status '{new_status}'. Allowed: {ALLOWED_STATUSES}"
        }

    cursor.execute(
        "SELECT status, guest_name, room_number, category, issue FROM tickets WHERE id = ?",
        (ticket_id,)
    )
    row = cursor.fetchone()
    if row is None:
        return {
            "status": "error",
            "message": f"Ticket #{ticket_id} not found"
        }

    previous_status, guest_name, room_number, category, issue = row

    now = datetime.now().isoformat(timespec="seconds")
    cursor.execute(
        "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, ticket_id)
    )
    conn.commit()

    print(f"\n TICKET #{ticket_id} -> {new_status}")

    result = {
        "status": "ticket_updated",
        "ticket_id": ticket_id,
        "ticket_status": new_status,
        "updated_at": now
    }

    # Close the loop: confirm with the guest when the issue is marked resolved.
    # Only on the open/in_progress -> resolved transition, so re-saving a
    # resolved ticket doesn't spam the guest.
    if new_status == "resolved" and previous_status != "resolved":
        # Send to the guest's own email if we have it on file
        profile = get_profile(guest_name)
        guest_email = profile.get("contact_email") if profile else None

        follow_up = send_email_tool(
            guest_name=guest_name,
            message=(
                f"Hi {guest_name}, our team has marked your request "
                f"(\"{issue}\") as resolved. Has everything been taken care of "
                f"to your satisfaction? Just reply if you need anything else."
            ),
            room_number=room_number or "N/A",
            category=category or "General",
            priority="Normal",
            recipient=guest_email
        )
        result["guest_follow_up"] = follow_up

    return result


def find_stale_tickets(minutes: int = 30) -> list:
    """Return open tickets created more than `minutes` ago (still unattended)."""
    cutoff = datetime.now() - timedelta(minutes=minutes)

    cursor.execute("SELECT * FROM tickets WHERE status = 'open' ORDER BY id DESC")
    stale = []
    for row in cursor.fetchall():
        ticket = _row_to_ticket(row)
        try:
            created = datetime.fromisoformat(ticket["created_at"])
        except (TypeError, ValueError):
            continue
        if created < cutoff:
            stale.append(ticket)

    return stale


def escalate_stale_tickets(minutes: int = 30) -> list:
    """Alert a manager about open tickets older than `minutes`.

    Each ticket is escalated at most once (tracked via the `escalated` flag),
    so repeated runs never re-notify the same ticket.
    """
    cutoff = datetime.now() - timedelta(minutes=minutes)

    cursor.execute(
        "SELECT * FROM tickets WHERE status = 'open' AND escalated = 0 ORDER BY id DESC"
    )
    escalated = []
    for row in cursor.fetchall():
        ticket = _row_to_ticket(row)
        try:
            created = datetime.fromisoformat(ticket["created_at"])
        except (TypeError, ValueError):
            continue
        if created >= cutoff:
            continue

        tid = ticket["ticket_id"]

        # Mark escalated first so a notification failure can't cause re-escalation
        cursor.execute("UPDATE tickets SET escalated = 1 WHERE id = ?", (tid,))
        conn.commit()

        print(f"\n ESCALATING TICKET #{tid} (open for > {minutes} min)")

        alert = send_email_tool(
            guest_name=ticket["guest_name"],
            message=(
                f"ESCALATION: ticket #{tid} from guest {ticket['guest_name']} "
                f"(room {ticket['room_number']}) has been open for more than "
                f"{minutes} minutes and is still unattended.\n\n"
                f"Issue: {ticket['issue']}"
            ),
            room_number=ticket["room_number"] or "N/A",
            category=ticket["category"] or "General",
            priority="High",
            recipient=MANAGER_EMAIL
        )

        ticket["escalation_alert"] = alert
        escalated.append(ticket)

    return escalated
