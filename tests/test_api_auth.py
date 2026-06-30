import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_dev_mode_allows_without_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", None)
    assert client.get("/analytics").status_code == 200


def test_enforced_rejects_missing_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "secret")
    assert client.get("/analytics").status_code == 401


def test_enforced_rejects_wrong_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "secret")
    assert client.get("/analytics", headers={"X-API-Key": "nope"}).status_code == 401


def test_enforced_accepts_correct_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "secret")
    assert client.get("/analytics", headers={"X-API-Key": "secret"}).status_code == 200


def test_fail_closed_when_required_without_key(tmp_path):
    """With REQUIRE_AUTH set and no API_KEY, the app must refuse to start."""
    import os
    import subprocess
    import sys

    env = dict(os.environ)
    env["REQUIRE_AUTH"] = "true"
    env.pop("API_KEY", None)
    env["GUESTFLOW_DB"] = str(tmp_path / "failclosed.db")

    proc = subprocess.run(
        [sys.executable, "-c", "import main"],
        capture_output=True, text=True, env=env,
    )
    assert proc.returncode != 0
    assert "API_KEY" in (proc.stderr + proc.stdout)
