from datetime import datetime, timedelta

from database.db import conn, cursor
from tools.analytics_tool import get_analytics


def _seed():
    created = (datetime.now() - timedelta(minutes=20)).isoformat(timespec="seconds")
    resolved = datetime.now().isoformat(timespec="seconds")
    cursor.execute(
        "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
        " VALUES ('A','1','General','Normal','x','resolved',?,?,0)", (created, resolved))
    cursor.execute(
        "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
        " VALUES ('A','2','General','High','y','open',?,?,1)", (created, created))
    cursor.execute("INSERT INTO feedback (guest_name,rating,comment,sentiment,manager_alerted,created_at)"
                   " VALUES ('A',4,'good','positive',0,?)", (resolved,))
    cursor.execute("INSERT INTO feedback (guest_name,rating,comment,sentiment,manager_alerted,created_at)"
                   " VALUES ('A',2,'bad','negative',1,?)", (resolved,))
    conn.commit()


def test_ticket_metrics():
    _seed()
    a = get_analytics()["tickets"]
    assert a["total"] == 2
    assert a["resolved"] == 1
    assert a["open"] == 1
    assert a["escalated"] == 1
    assert a["resolution_rate_pct"] == 50.0
    # resolved ticket was created 20 min before resolution
    assert 19 <= a["avg_resolution_minutes"] <= 21


def test_feedback_metrics():
    _seed()
    f = get_analytics()["feedback"]
    assert f["total"] == 2
    assert f["avg_rating"] == 3.0
    assert f["positive"] == 1
    assert f["negative"] == 1


def test_empty_analytics():
    a = get_analytics()
    assert a["tickets"]["total"] == 0
    assert a["tickets"]["avg_resolution_minutes"] is None
    assert a["feedback"]["avg_rating"] is None
