from database.db import conn, cursor

def update_crm_tool(guest_name, event_type):

    cursor.execute(
        """
        INSERT INTO guest_events (guest_name, event_type)
        VALUES (?, ?)
        """,
        (guest_name, event_type)
    )

    conn.commit()

    print("\n CRM UPDATED IN SQLITE")

    return {
        "status": "crm_updated",
        "guest_name": guest_name,
        "event_type": event_type
    }


def get_guest_history_tool(guest_name):

    cursor.execute(
        """
        SELECT * FROM guest_events
        WHERE guest_name = ?
        """,
        (guest_name,)
    )

    history = cursor.fetchall()

    print("\n GUEST HISTORY RETRIEVED")
    print(history)

    return history