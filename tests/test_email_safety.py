from tools import email_tool


def test_clean_header_strips_crlf():
    injected = "Normal\r\nBcc: victim@evil.com"
    cleaned = email_tool._clean_header(injected)
    assert "\r" not in cleaned and "\n" not in cleaned


def test_valid_email_accepts_good_address():
    assert email_tool._valid_email("guest@example.com")


def test_valid_email_rejects_injection_and_garbage():
    assert not email_tool._valid_email("x@y.com\nBcc: victim@evil.com")
    assert not email_tool._valid_email("not-an-email")
    assert not email_tool._valid_email(None)


def test_send_rejects_invalid_recipient_without_smtp():
    # Invalid recipient must be rejected before any SMTP connection
    res = email_tool.send_email_tool("Guest", "hi", recipient="x@y.com\nBcc: evil@x.com")
    assert res["status"] == "email_failed"
