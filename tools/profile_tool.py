from datetime import datetime

from database.db import conn, cursor


def _row_to_profile(row) -> dict:
    return {
        "guest_name": row[0],
        "contact_email": row[1],
        "preferences": row[2],
        "is_vip": bool(row[3]),
        "notes": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def get_profile(guest_name: str) -> dict | None:
    """Return a guest's stored profile, or None if they have no profile yet."""
    cursor.execute(
        "SELECT * FROM guest_profiles WHERE guest_name = ?",
        (guest_name,)
    )
    row = cursor.fetchone()
    return _row_to_profile(row) if row else None


def save_profile(
    guest_name: str,
    contact_email: str = None,
    preferences: str = None,
    is_vip: bool = None,
    notes: str = None
) -> dict:
    """Create or update a guest profile.

    Only the fields you pass are changed; anything left as None keeps its
    existing value (a merge/upsert), so partial updates never wipe other data.
    """
    now = datetime.now().isoformat(timespec="seconds")
    existing = get_profile(guest_name)

    if existing:
        merged = {
            "contact_email": contact_email if contact_email is not None else existing["contact_email"],
            "preferences": preferences if preferences is not None else existing["preferences"],
            "is_vip": existing["is_vip"] if is_vip is None else is_vip,
            "notes": notes if notes is not None else existing["notes"],
        }
        cursor.execute(
            """
            UPDATE guest_profiles
            SET contact_email = ?, preferences = ?, is_vip = ?, notes = ?, updated_at = ?
            WHERE guest_name = ?
            """,
            (
                merged["contact_email"],
                merged["preferences"],
                1 if merged["is_vip"] else 0,
                merged["notes"],
                now,
                guest_name,
            )
        )
    else:
        cursor.execute(
            """
            INSERT INTO guest_profiles
                (guest_name, contact_email, preferences, is_vip, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guest_name,
                contact_email,
                preferences,
                1 if is_vip else 0,
                notes,
                now,
                now,
            )
        )

    conn.commit()
    print(f"\n GUEST PROFILE SAVED — {guest_name}")
    return get_profile(guest_name)


def erase_guest_data(guest_name: str) -> dict:
    """Right-to-erasure: remove a guest's PII.

    Deletes the profile and feedback outright, and anonymizes their tickets
    (kept for operational stats but stripped of the guest's identity).
    """
    cursor.execute("DELETE FROM guest_profiles WHERE guest_name = ?", (guest_name,))
    profiles_deleted = cursor.rowcount

    cursor.execute("DELETE FROM feedback WHERE guest_name = ?", (guest_name,))
    feedback_deleted = cursor.rowcount

    cursor.execute(
        "UPDATE tickets SET guest_name = '[deleted]' WHERE guest_name = ?",
        (guest_name,)
    )
    tickets_anonymized = cursor.rowcount

    cursor.execute("DELETE FROM guest_events WHERE guest_name = ?", (guest_name,))
    events_deleted = cursor.rowcount

    conn.commit()
    print(f"\n GUEST DATA ERASED — {guest_name}")

    return {
        "status": "erased",
        "guest_name": guest_name,
        "profiles_deleted": profiles_deleted,
        "feedback_deleted": feedback_deleted,
        "tickets_anonymized": tickets_anonymized,
        "events_deleted": events_deleted,
    }
