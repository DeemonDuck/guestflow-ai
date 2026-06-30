from datetime import datetime, timedelta

from database.db import conn, cursor
from tools.insights_tool import get_insights


def _add_ticket(room, category, created_min_ago=10):
    ts = (datetime.now() - timedelta(minutes=created_min_ago)).isoformat(timespec="seconds")
    cursor.execute(
        "INSERT INTO tickets (guest_name,room_number,category,priority,issue,status,created_at,updated_at,escalated)"
        " VALUES ('G',?,?,'High','x','open',?,?,0)",
        (room, category, ts, ts),
    )
    conn.commit()


def _add_negative_feedback(comment):
    cursor.execute(
        "INSERT INTO feedback (guest_name,rating,comment,sentiment,manager_alerted,created_at)"
        " VALUES ('G',2,?,'negative',1,?)",
        (comment, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


def test_no_insights_when_quiet():
    assert get_insights() == []


def test_systemic_issue_detected():
    # 3 Maintenance tickets on floor 3 within the window
    _add_ticket("301", "Maintenance")
    _add_ticket("305", "Maintenance")
    _add_ticket("309", "Maintenance")
    kinds = [i["type"] for i in get_insights()]
    assert "systemic_issue" in kinds


def test_repeat_room_detected():
    for _ in range(3):
        _add_ticket("404", "Housekeeping", created_min_ago=5000)  # old, not systemic
    insights = get_insights()
    assert any(i["type"] == "repeat_room" and "404" in i["message"] for i in insights)


def test_feedback_theme_detected():
    _add_negative_feedback("the room was dirty")
    _add_negative_feedback("very dirty bathroom and dust everywhere")
    insights = get_insights()
    assert any(i["type"] == "feedback_theme" and "cleanliness" in i["message"] for i in insights)
