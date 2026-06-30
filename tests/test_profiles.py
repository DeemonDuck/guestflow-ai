from tools.profile_tool import get_profile, save_profile


def test_create_and_get():
    save_profile("Sharma", preferences="High floor", is_vip=True)
    p = get_profile("Sharma")
    assert p is not None
    assert p["preferences"] == "High floor"
    assert p["is_vip"] is True


def test_merge_upsert_preserves_other_fields():
    save_profile("Sharma", preferences="High floor, extra pillows", is_vip=True)
    # Update only the email; preferences and VIP must survive
    save_profile("Sharma", contact_email="sharma@example.com")
    p = get_profile("Sharma")
    assert p["contact_email"] == "sharma@example.com"
    assert p["preferences"] == "High floor, extra pillows"
    assert p["is_vip"] is True


def test_unknown_profile_returns_none():
    assert get_profile("NoSuchGuest") is None
