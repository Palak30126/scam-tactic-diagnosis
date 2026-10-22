import re
import pandas as pd

URL = re.compile(r"https?://\S+|www\.\S+")
EMAIL_LOCAL = re.compile(r"[\w.+-]+(?=@[\w-]+\.[\w.]+)")   # keeps the domain, which is a scam signal
AADHAAR = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
PHONE = re.compile(r"(?<!\d)(\+?\d[\d\- ]{8,}\d)(?!\d)")

TEXT_COLS = ["title", "company_profile", "description", "requirements", "benefits"]


def scrub_pii(text) -> str:
    """Remove personal identifiers. Order matters: Aadhaar and PAN run before the phone pattern."""
    text = str(text)
    text = URL.sub("[URL]", text)
    text = EMAIL_LOCAL.sub("[USER]", text)
    text = AADHAAR.sub("[ID]", text)
    text = PAN.sub("[ID]", text)
    text = PHONE.sub("[PHONE]", text)
    return text


def combine_text(row) -> str:
    parts = [str(row[c]) for c in TEXT_COLS if c in row and pd.notna(row[c])]
    return scrub_pii(" \n ".join(parts))


def build_text(df: pd.DataFrame) -> pd.Series:
    return df.apply(combine_text, axis=1)