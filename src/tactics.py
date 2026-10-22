import re

FREE_EMAIL = re.compile(r"[\w.+-]+@(gmail|yahoo|outlook|hotmail)\.(com|in)", re.IGNORECASE)

# Well-known employers. Flagged only when a free email address also appears.
BRANDS = ["infosys", "tcs", "wipro", "accenture", "amazon", "google", "microsoft"]

TACTIC_PATTERNS = {
    "fee_demanded": [
        r"registration fee", r"security deposit", r"training (fee|charges?)",
        r"processing fee", r"(pay|deposit)\s+(rs\.?|₹)\s?\d+",
    ],
    "off_platform_contact": [
        r"(contact|message|chat|reach|apply)[^.\n]{0,40}(whatsapp|telegram)",
        r"\bwhatsapp only\b", r"\btelegram\b",
    ],
    "free_email_domain": [FREE_EMAIL.pattern],
    "unrealistic_pay": [
        r"(earn|salary)[^.\n]{0,20}(per day|daily|weekly)[^.\n]{0,20}\d{4,}",
        r"(work from home|wfh)[^.\n]{0,30}(lakh|₹\s?\d{2,})",
    ],
    "no_interview": [
        r"instant (selection|joining|offer)", r"direct joining", r"no interview",
    ],
    "urgency": [
        r"apply (today|now|immediately)", r"limited (seats|slots|openings)",
        r"last (date|chance)",
    ],
    "early_sensitive_data": [
        r"aadhaar|aadhar", r"\bpan (card|number)\b", r"bank (account|details)",
    ],
}

TACTIC_LABELS = {
    "fee_demanded": "Fee demanded",
    "off_platform_contact": "Off-platform contact",
    "free_email_domain": "Free email posing as company",
    "unrealistic_pay": "Unrealistic pay",
    "no_interview": "No interview",
    "urgency": "Urgency or pressure",
    "early_sensitive_data": "Early sensitive data request",
    "impersonation": "Impersonation of a real company",
}

ALL_TACTICS = list(TACTIC_LABELS.keys())


def find_matches(text: str) -> dict:
    """Return {tactic: [(start, end, matched_text), ...]} for every rule that fires."""
    hits = {}
    for tactic, patterns in TACTIC_PATTERNS.items():
        spans = []
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                spans.append((m.start(), m.end(), m.group(0)))
        if spans:
            hits[tactic] = sorted(spans)

    # Impersonation rule: a well-known brand name plus a free email address.
    if FREE_EMAIL.search(text):
        spans = []
        for brand in BRANDS:
            for m in re.finditer(rf"\b{re.escape(brand)}\b", text, flags=re.IGNORECASE):
                spans.append((m.start(), m.end(), m.group(0)))
        if spans:
            hits["impersonation"] = sorted(spans)

    return hits