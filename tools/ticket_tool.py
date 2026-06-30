from datetime import datetime

from database.db import conn, cursor


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
    """Move a ticket to a new lifecycle state."""
    if new_status not in ALLOWED_STATUSES:
        return {
            "status": "error",
            "message": f"Invalid status '{new_status}'. Allowed: {ALLOWED_STATUSES}"
        }

    cursor.execute("SELECT id FROM tickets WHERE id = ?", (ticket_id,))
    if cursor.fetchone() is None:
        return {
            "status": "error",
            "message": f"Ticket #{ticket_id} not found"
        }

    now = datetime.now().isoformat(timespec="seconds")
    cursor.execute(
        "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, ticket_id)
    )
    conn.commit()

    print(f"\n TICKET #{ticket_id} -> {new_status}")

    return {
        "status": "ticket_updated",
        "ticket_id": ticket_id,
        "ticket_status": new_status,
        "updated_at": now
    }
