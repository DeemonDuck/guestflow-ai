from tools.profile_tool import get_profile, save_profile, erase_guest_data
from database.db import conn, cursor


def test_create_and_get():
    save_profile("Sharma", preferences="High floor", is_vip=True)
    p = get_profile("Sharma")
    assert p is not None
    assert p["preferences"] == "High floor"
    assert p["is_vip"] is True


def test_merge_upsert_preserves_other_fields():
    save_profile("Sharma", preferences="High floor, extra pillows", is_vip=True)
    # Update only the email; preferences and VIP must survive
    save_profile("Sharma", contact_email="sharma@example.com")
    p = get_profile("Sharma")
    assert p["contact_email"] == "sharma@example.com"
    assert p["preferences"] == "High floor, extra pillows"
    assert p["is_vip"] is True


def test_unknown_profile_returns_none():
    assert get_profile("NoSuchGuest") is None


def test_erase_guest_data_removes_pii():
    name = "EraseMe"
    save_profile(name, contact_email="erase@example.com", preferences="x")
    cursor.execute(
        "INSERT INTO feedback (guest_name,rating,comment,sentiment,manager_alerted,created_at)"
        " VALUES (?,3,'meh','neutral',0,'2026-01-01T00:00:00')", (name,))
    cursor.execute(
        "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
        " VALUES (?,'1','General','Normal','x','open','t','t',0)", (name,))
    conn.commit()

    result = erase_guest_data(name)

    assert result["status"] == "erased"
    assert get_profile(name) is None
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE guest_name = ?", (name,))
    assert cursor.fetchone()[0] == 0
    # ticket retained for stats but anonymized
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE guest_name = ?", (name,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE guest_name = '[deleted]'")
    assert cursor.fetchone()[0] >= 1
