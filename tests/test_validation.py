from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_rating_out_of_range_rejected():
    assert client.post("/feedback/Guest", json={"rating": 9999}).status_code == 422
    assert client.post("/feedback/Guest", json={"rating": 0}).status_code == 422


def test_valid_rating_accepted():
    # rating 5 is positive -> no email side effect
    assert client.post("/feedback/Guest", json={"rating": 5}).status_code == 200


def test_invalid_email_rejected():
    assert client.post(
        "/profiles/Guest", json={"contact_email": "not-an-email"}
    ).status_code == 422


def test_valid_email_accepted():
    assert client.post(
        "/profiles/Guest", json={"contact_email": "guest@example.com"}
    ).status_code == 200


def test_overlong_comment_rejected():
    assert client.post(
        "/feedback/Guest", json={"comment": "x" * 5000}
    ).status_code == 422
