from datetime import datetime, timedelta

from database.db import conn, cursor
from tools.ticket_tool import (
    create_ticket_tool,
    list_tickets,
    update_ticket_status,
    find_stale_tickets,
    escalate_stale_tickets,
)


def test_create_persists_ticket():
    res = create_ticket_tool("Asha", "AC not cooling", room_number="101")
    assert res["ticket_status"] == "open"
    assert res["ticket_id"] is not None

    tickets = list_tickets()
    assert len(tickets) == 1
    assert tickets[0]["guest_name"] == "Asha"


def test_status_validation_rejects_unknown():
    res = create_ticket_tool("Asha", "issue")
    out = update_ticket_status(res["ticket_id"], "banana")
    assert out["status"] == "error"


def test_update_missing_ticket():
    out = update_ticket_status(999999, "resolved")
    assert out["status"] == "error"


def test_lifecycle_transitions(captured_emails):
    res = create_ticket_tool("Asha", "issue")
    tid = res["ticket_id"]
    assert update_ticket_status(tid, "in_progress")["ticket_status"] == "in_progress"
    assert update_ticket_status(tid, "resolved")["ticket_status"] == "resolved"


def test_resolve_follow_up_fires_once(captured_emails):
    res = create_ticket_tool("Asha", "issue")
    tid = res["ticket_id"]

    r1 = update_ticket_status(tid, "resolved")
    assert "guest_follow_up" in r1
    assert len(captured_emails) == 1

    # Re-saving a resolved ticket must NOT email the guest again
    r2 = update_ticket_status(tid, "resolved")
    assert "guest_follow_up" not in r2
    assert len(captured_emails) == 1


def _insert_old_open_ticket(minutes_old):
    ts = (datetime.now() - timedelta(minutes=minutes_old)).isoformat(timespec="seconds")
    cursor.execute(
        "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
        " VALUES ('Asha','1','General','Normal','x','open',?,?,0)",
        (ts, ts),
    )
    conn.commit()
    return cursor.lastrowid


def test_find_stale_only_returns_old_open():
    old = _insert_old_open_ticket(60)
    create_ticket_tool("Fresh", "new issue")  # fresh, should not be stale
    stale = find_stale_tickets(30)
    assert [t["ticket_id"] for t in stale] == [old]


def test_escalation_alerts_once(captured_emails):
    _insert_old_open_ticket(60)

    first = escalate_stale_tickets(30)
    assert len(first) == 1
    assert len(captured_emails) == 1

    second = escalate_stale_tickets(30)
    assert second == []
    assert len(captured_emails) == 1  # no re-notification
