# Labelling Guideline

## Unit
One posting or message = one row. Include job posts, internship offers, and WhatsApp/Telegram messages.

## fake (0 or 1)
- 1 (fake): the posting asks for money or sensitive data, uses only untraceable contact, or the employer cannot be verified.
- 0 (real): a verifiable employer, a normal hiring process, and no payment or sensitive-data requests.
- If unsure, label 1 only when at least one tactic below is clearly present. Otherwise label 0.

## tactics (semicolon-separated, zero or more)
Use exactly these names:
- fee_demanded: asks for a registration, security, training, or processing fee
- off_platform_contact: asks you to contact only via WhatsApp or Telegram
- free_email_domain: uses gmail/yahoo/outlook/hotmail as the company's contact
- unrealistic_pay: very high pay for no skills or experience
- no_interview: "instant selection", "direct joining", "no interview"
- urgency: "apply today", "limited seats", "last chance"
- early_sensitive_data: asks for Aadhaar, PAN, or bank details before hiring
- impersonation: names a well-known company but the contact does not match it

Rules:
- A genuine posting that mentions WhatsApp for a group or a community is NOT off_platform_contact unless it is the only contact.
- Do not infer a tactic from tone alone. The text must show it.
- Record anything unusual in the notes column.

## Privacy
Before saving, replace phone numbers, emails, names of private people, and Aadhaar/PAN numbers with [PHONE], [USER], or [ID]. The code also does this, but do it yourself first.
Use only public material. Do not collect posts from private groups.