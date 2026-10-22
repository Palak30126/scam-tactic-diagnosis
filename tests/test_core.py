from src.clean import scrub_pii
from src.tactics import find_matches
from src.verdict import highlight


def test_scrub_removes_phone_and_email_local_part():
    out = scrub_pii("Call 9876543210 or write to priya.rao@example.com")
    assert "9876543210" not in out
    assert "priya.rao" not in out
    assert "example.com" in out          # domain is kept on purpose


def test_scrub_removes_pan_and_aadhaar():
    out = scrub_pii("PAN ABCDE1234F, Aadhaar 1234 5678 9012")
    assert "ABCDE1234F" not in out
    assert "1234 5678 9012" not in out


def test_fee_rule_fires():
    hits = find_matches("Please pay a registration fee of Rs. 999 to confirm.")
    assert "fee_demanded" in hits


def test_clean_posting_has_no_tactics():
    assert find_matches("We are hiring a Python developer. Apply via our careers page.") == {}


def test_impersonation_needs_brand_and_free_email():
    text = "Infosys HR team, write to infosys.hr@gmail.com"
    assert "impersonation" in find_matches(text)
    assert "impersonation" not in find_matches("Infosys is hiring. Apply on infosys.com")


def test_highlight_escapes_html():
    text = "a <b>x</b> c"
    out = highlight(text, [(2, 5, "<b>")])
    assert "<b>" not in out
    assert "<mark>&lt;b&gt;</mark>" in out