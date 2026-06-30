"""Shared pytest fixtures.

Critically, this sets GUESTFLOW_DB to a throwaway temp database BEFORE any
application module is imported, so tests never touch the real guestflow.db.
"""
import atexit
import os
import tempfile

# Must run before importing anything that imports database.db
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["GUESTFLOW_DB"] = _tmp.name
os.environ.pop("API_KEY", None)  # default to dev mode unless a test sets it


@atexit.register
def _cleanup_tmp_db():
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass


import pytest

from database.db import conn, cursor


@pytest.fixture(autouse=True)
def clean_db():
    """Start every test from empty tables for isolation."""
    for table in ("tickets", "feedback", "guest_profiles", "guest_events"):
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    yield


@pytest.fixture
def captured_emails(monkeypatch):
    """Stub the email sender in every module that uses it; capture calls."""
    calls = []

    def fake_send(*args, **kwargs):
        calls.append(kwargs)
        return {"status": "email_sent", "recipient": kwargs.get("recipient")}

    import tools.ticket_tool
    import tools.feedback_tool
    import tools.digest_tool
    monkeypatch.setattr(tools.ticket_tool, "send_email_tool", fake_send)
    monkeypatch.setattr(tools.feedback_tool, "send_email_tool", fake_send)
    monkeypatch.setattr(tools.digest_tool, "send_email_tool", fake_send)
    return calls
