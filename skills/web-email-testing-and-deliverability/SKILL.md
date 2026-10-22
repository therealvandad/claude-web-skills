---
name: web-email-testing-and-deliverability
description: Get HTML email into the inbox and verify it renders: SPF, DKIM and DMARC DNS records with example values, List-Unsubscribe and one-click List-Unsubscribe-Post headers, spam-trigger content, the 102 KB Gmail clip and which clients to test. Use when a user says "emails go to spam", "set up SPF DKIM DMARC", "unsubscribe header", "test my email" or "Gmail bulk sender rules".
---

# Email testing and deliverability

An email that renders perfectly but lands in spam, or is rejected outright, does nothing. Since 2024 Gmail and Yahoo require authentication and one-click unsubscribe from anyone sending more than 5,000 messages a day, and Outlook.com, Hotmail and Live added the same SPF, DKIM and DMARC bar for high-volume senders in 2025. Small senders get filtered on the same signals, so set all of this up before the first send. Use a dedicated sending subdomain (`mail.kettleandco.example`) so marketing reputation cannot damage receipts and password resets.

## Pattern

DNS records on the sending domain (zone-file syntax; your ESP supplies the exact hosts and keys):

```text
; SPF: one record per domain, max 10 DNS lookups, authorised senders only. ~all while testing, -all once stable.
mail.kettleandco.example.            IN TXT "v=spf1 include:amazonses.com ~all"

; DKIM: public key published under a selector. 2048-bit RSA; split strings over 255 characters.
s1._domainkey.mail.kettleandco.example. IN TXT "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq3x...IDAQAB"

; DMARC: start at p=none, read the reports for 2 to 4 weeks, then quarantine, then reject.
_dmarc.kettleandco.example.          IN TXT "v=DMARC1; p=none; rua=mailto:dmarc-reports@kettleandco.example; adkim=r; aspf=r; fo=1"
; later:  "v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc-reports@kettleandco.example"
; final:  "v=DMARC1; p=reject; rua=mailto:dmarc-reports@kettleandco.example"
```

Alignment is what DMARC checks: the visible `From:` domain must match (or be a subdomain of) the domain that passed SPF or DKIM. Sending `From: Kettle & Co <hello@kettleandco.example>` through a signing domain of `esp-mail.example` passes DKIM but fails DMARC; sign with your own domain.

Headers added when sending marketing mail (not receipts or resets):

```text
From: Kettle & Co <hello@mail.kettleandco.example>
List-Unsubscribe: <https://kettleandco.example/u/Zk3p9Qx7?list=steep>, <mailto:unsubscribe@kettleandco.example?subject=unsubscribe-Zk3p9Qx7>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

`List-Unsubscribe-Post` is the RFC 8058 signal that the HTTPS URL accepts a bare `POST` with the body `List-Unsubscribe=One-Click` and unsubscribes at once: no login, no confirmation page, no cookies, done within two days. Both headers must be covered by the DKIM signature, or receivers may ignore them. Keep a visible unsubscribe link in the footer as well.

Check everything from a shell and from a real message:

```bash
dig +short TXT mail.kettleandco.example           # SPF
dig +short TXT s1._domainkey.mail.kettleandco.example
dig +short TXT _dmarc.kettleandco.example
wc -c newsletter.html                             # keep under ~90000 bytes: Gmail clips at 102 KB
# In Gmail: open the message, "Show original", and look for:
#   SPF: PASS   DKIM: PASS   DMARC: PASS
```

## Variations

- **Testing rendering**: Litmus or Email on Acid for screenshots across 90+ clients, Mailtrap or Mailpit to catch mail locally without sending, and real accounts for the clients that matter to you: Gmail web and Android app, Apple Mail on macOS and iOS (light and dark), classic Outlook for Windows (the Word engine), new Outlook, Outlook.com with `[data-ogsc]` dark mode, and Yahoo Mail.
- **Testing reputation**: mail-tester.com for a quick 10-point score, Google Postmaster Tools for domain reputation and spam rate at Gmail, Microsoft SNDS for Outlook.com. Keep the Gmail spam-complaint rate under 0.10%; at 0.30% you lose mitigation eligibility.
- **Warm-up for a new domain or IP**: start at a few hundred messages a day to your most engaged addresses, roughly double each day, and stop at the first spike in bounces or complaints.
- **Pre-send checklist**: subject and preheader read well together, every link opens, alt text on every image, plain-text part present, physical address in the footer, tested in dark mode.

## Pitfalls

- Two SPF records on one domain invalidate both. Merge them into one `v=spf1` line, and watch the 10-lookup limit when stacking `include:` entries.
- Jumping straight to `p=reject` blocks your own legitimate mail from tools you forgot (support desk, billing, a CRM). Run `p=none` first and read the aggregate reports.
- Spam-trigger content matters less than reputation, but these still cost points: ALL CAPS or `!!!` in the subject, "FREE", "Act now", "Congratulations, you won"; a subject that fakes `Re:` or `Fwd:`; URL shorteners; link text that shows one domain while the `href` goes to another; one big image with little text; broken HTML; attachments, especially `.zip` or `.html`.
- Buying or scraping lists, or mailing addresses that have not opened in 12 months, produces complaints and spam-trap hits that no template fix can offset. Remove hard bounces immediately and sunset unengaged contacts.
- Do not rely on open rates: Apple Mail Privacy Protection and Gmail's image proxy inflate them. Judge by clicks and conversions.
- Do not test only in a browser at a narrow width. Classic Outlook, Gmail's non-Google-account view and Samsung Mail behave differently from any browser.

## Related skills

- `web-email-table-layout`
- `web-email-dark-mode`
- `web-email-newsletter-template`
- `web-email-transactional-templates`
- `web-email-plain-text-and-accessibility`
- `web-ship-launch-checklist`
