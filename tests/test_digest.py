from datetime import datetime, timedelta

import tools.digest_tool as digest
import config
from database.db import conn, cursor


def _seed_pattern():
    now = datetime.now()
    # 3 maintenance tickets on floor 3 -> systemic insight
    for room in ("301", "305", "309"):
        ts = now.isoformat(timespec="seconds")
        cursor.execute(
            "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
            " VALUES ('G',?,'Maintenance','High','x','open',?,?,0)", (room, ts, ts))
    cursor.execute(
        "INSERT INTO feedback (guest_name,rating,comment,sentiment,manager_alerted,created_at)"
        " VALUES ('G',2,'room was dirty','negative',1,?)", (now.isoformat(timespec="seconds"),))
    conn.commit()


def test_compose_digest_includes_sections():
    body = digest.compose_digest()
    assert "TICKETS" in body
    assert "FEEDBACK" in body
    assert "INSIGHTS" in body


def test_compose_digest_surfaces_insights():
    _seed_pattern()
    body = digest.compose_digest()
    # systemic issue should appear in the digest
    assert "systemic issue" in body.lower()


def test_send_digest_goes_to_manager(captured_emails):
    res = digest.send_digest()
    assert res["status"] == "digest_sent"
    assert len(captured_emails) == 1
    assert captured_emails[0]["recipient"] == config.MANAGER_EMAIL
    assert "Operations Digest" in captured_emails[0]["message"]
