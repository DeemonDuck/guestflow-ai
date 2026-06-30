"""Intent classifier tests.

These load a sentence-transformer model on import, so they are a little slower
than the rest of the suite, but they guard the auto-routing behavior.
"""
from intent_classifier import classify_intent


def test_booking_intent():
    assert classify_intent("I have a reservation and I'm checking in soon") == "booking_confirmed"


def test_guest_request_intent():
    assert classify_intent("I want a refund for the bad service") == "guest_request"


def test_checkout_intent():
    assert classify_intent("I have checked out and my stay is over") == "checkout_complete"
