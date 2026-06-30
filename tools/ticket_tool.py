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
