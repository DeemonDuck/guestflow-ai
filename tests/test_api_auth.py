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
