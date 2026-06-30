import tools.feedback_tool as fb
import config


def test_negative_rating_alerts_manager(captured_emails):
    res = fb.submit_feedback("Asha", rating=2, comment="dirty room")
    assert res["sentiment"] == "negative"
    assert res["manager_alerted"] is True
    assert len(captured_emails) == 1
    assert captured_emails[0]["recipient"] == config.MANAGER_EMAIL


def test_positive_rating_no_alert(captured_emails):
    res = fb.submit_feedback("Asha", rating=5, comment="great stay")
    assert res["sentiment"] == "positive"
    assert res["manager_alerted"] is False
    assert len(captured_emails) == 0


def test_negative_comment_without_rating(captured_emails):
    res = fb.submit_feedback("Asha", comment="terrible service")
    assert res["sentiment"] == "negative"


def test_neutral_comment(captured_emails):
    res = fb.submit_feedback("Asha", comment="it was fine")
    assert res["sentiment"] == "neutral"
    assert len(captured_emails) == 0


def test_review_link_offered_to_every_guest(captured_emails, monkeypatch):
    # Compliance: the review invite is unconditional (not gated on rating).
    monkeypatch.setattr(fb, "REVIEW_LINK", "https://g.page/r/REVIEW")
    fb.request_feedback("Asha")
    assert len(captured_emails) == 1
    assert "https://g.page/r/REVIEW" in captured_emails[0]["message"]
