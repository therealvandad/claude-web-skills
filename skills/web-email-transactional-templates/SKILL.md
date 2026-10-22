---
name: web-email-transactional-templates
description: 'Complete body blocks for the four transactional emails every shop or app sends: order receipt, password reset, welcome and shipping notice, each with subject, preheader and plain footer, built on the shared table skeleton. Use when a user asks for a "receipt email", "password reset email", "welcome email", "order confirmation" or "shipping notification".'
---

# Transactional email templates

A transactional email is sent because the reader did something: bought, forgot a password, signed up, is waiting for a parcel. They open it to do one task, so put the answer in the first screen, keep one button, and leave out promotions (mixing marketing into a receipt can turn it into a commercial message under CAN-SPAM and similar laws, and it hurts inbox placement). Build once on the skeleton from `web-email-table-layout` (wrapper, 600 px container, preheader, footer with address) and replace only the card cell below. Each block repeats `font-family`, `font-size`, `line-height` and `color` on its cells because classic Outlook resets them per `<td>`.

## Pattern

The slot every block goes into, inside the 600 px container:

```html
<tr>
  <td bgcolor="#ffffff" class="pad dm-card dm-text" style="padding:32px 24px; background-color:#ffffff; border-radius:8px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; mso-line-height-rule:exactly; color:#1c1917;">
    <!-- BODY BLOCK GOES HERE -->
  </td>
</tr>
```

**1. Receipt.** Subject: `Receipt for order 48213, £51.45`. Preheader: `Paid with Visa ending 4821. Ships Thursday 22 October.`

```html
<h1 style="margin:0 0 8px; font-size:24px; line-height:32px; color:#1c1917;">Thanks, Priya. Order 48213 is paid.</h1>
<p style="margin:0 0 24px; color:#57534e;">Placed Wednesday 21 October 2026 at 09:14. We will email again when it ships.</p>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
  <tr>
    <td style="padding:8px 0; border-bottom:1px solid #e7e5e4; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; color:#1c1917;">Cast iron kyusu, 600 ml<br><span style="color:#78716c;">Qty 1</span></td>
    <td align="right" valign="top" style="padding:8px 0; border-bottom:1px solid #e7e5e4; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; color:#1c1917;">&pound;29.50</td>
  </tr>
  <tr>
    <td style="padding:8px 0; border-bottom:1px solid #e7e5e4; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; color:#1c1917;">Hojicha Chai, 100 g<br><span style="color:#78716c;">Qty 2 at &pound;9.00</span></td>
    <td align="right" valign="top" style="padding:8px 0; border-bottom:1px solid #e7e5e4; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; color:#1c1917;">&pound;18.00</td>
  </tr>
  <tr>
    <td style="padding:8px 0 0; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; color:#57534e;">Delivery, Royal Mail Tracked 48</td>
    <td align="right" style="padding:8px 0 0; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; color:#57534e;">&pound;3.95</td>
  </tr>
  <tr>
    <td style="padding:8px 0 0; font-family:Helvetica, Arial, sans-serif; font-size:18px; line-height:26px; font-weight:bold; color:#1c1917;">Total</td>
    <td align="right" style="padding:8px 0 0; font-family:Helvetica, Arial, sans-serif; font-size:18px; line-height:26px; font-weight:bold; color:#1c1917;">&pound;51.45</td>
  </tr>
</table>
<p style="margin:24px 0 0; font-size:14px; line-height:20px; color:#57534e;">Billed to Priya Raman, 14 Harehills Lane, Leeds LS8 4DN. <a href="https://kettleandco.example/orders/48213" style="color:#1d4ed8;">View order and invoice</a></p>
```

**2. Password reset.** Subject: `Reset your Kettle & Co password`. Preheader: `This link works once and expires in 60 minutes.` The button is the bulletproof one from `web-email-typography-and-buttons`.

```html
<h1 style="margin:0 0 12px; font-size:24px; line-height:32px; color:#1c1917;">Reset your password</h1>
<p style="margin:0 0 24px;">Someone asked to reset the password for priya.raman@example.net. Use the button within 60 minutes; it works once.</p>
<!-- bulletproof button: "Choose a new password" -> https://kettleandco.example/account/reset?t=Qm7x2Vc9LkP4 -->
<p style="margin:24px 0 0; font-size:14px; line-height:20px; color:#57534e;">Button not working? Paste this into your browser:<br><a href="https://kettleandco.example/account/reset?t=Qm7x2Vc9LkP4" style="color:#1d4ed8; word-break:break-all;">https://kettleandco.example/account/reset?t=Qm7x2Vc9LkP4</a></p>
<p style="margin:16px 0 0; font-size:14px; line-height:20px; color:#57534e;">Requested 21 October 2026, 09:14 BST from Chrome on Windows near Leeds, UK. Not you? Ignore this email and your password stays the same.</p>
```

**3. Welcome.** Subject: `Welcome to Kettle & Co, Priya`. Preheader: `Three things worth doing in your first week.`

```html
<h1 style="margin:0 0 12px; font-size:24px; line-height:32px; color:#1c1917;">Welcome, Priya</h1>
<p style="margin:0 0 20px;">Your account is ready. Here is where most people start:</p>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
  <tr>
    <td width="32" valign="top" style="padding:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; font-weight:bold; color:#1d4ed8;">1.</td>
    <td style="padding:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;"><strong>Pick a tea.</strong> Order the 25 g sample tin (&pound;3.50) before you commit to 100 g.</td>
  </tr>
  <tr>
    <td width="32" valign="top" style="padding:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; font-weight:bold; color:#1d4ed8;">2.</td>
    <td style="padding:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;"><strong>Save your address</strong> so checkout takes under a minute.</td>
  </tr>
  <tr>
    <td width="32" valign="top" style="padding:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; font-weight:bold; color:#1d4ed8;">3.</td>
    <td style="padding:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;"><strong>Read the brewing guide</strong> for water temperature and timings per tea.</td>
  </tr>
</table>
<!-- bulletproof button: "Browse the teas" -> https://kettleandco.example/teas?utm_source=email&amp;utm_campaign=welcome -->
<p style="margin:24px 0 0; font-size:14px; line-height:20px; color:#57534e;">Reply to this email and a person in Leeds will answer, usually the same day.</p>
```

**4. Shipping notice.** Subject: `Order 48213 has shipped, due Monday`. Preheader: `Royal Mail RM 4472 9018 1GB. Delivery before 1 pm on 26 October.`

```html
<h1 style="margin:0 0 12px; font-size:24px; line-height:32px; color:#1c1917;">Your order is on its way</h1>
<p style="margin:0 0 20px;">Royal Mail collected 2 items today. Expected delivery: <strong>Monday 26 October, before 1 pm</strong>.</p>
<!-- Progress: three equal cells, filled up to the current step -->
<table role="presentation" width="100%" cellspacing="4" cellpadding="0" border="0">
  <tr>
    <td width="33%" height="6" bgcolor="#1d4ed8" style="height:6px; font-size:0; line-height:0; mso-line-height-rule:exactly;">&nbsp;</td>
    <td width="33%" height="6" bgcolor="#1d4ed8" style="height:6px; font-size:0; line-height:0; mso-line-height-rule:exactly;">&nbsp;</td>
    <td width="33%" height="6" bgcolor="#e7e5e4" style="height:6px; font-size:0; line-height:0; mso-line-height-rule:exactly;">&nbsp;</td>
  </tr>
  <tr>
    <td style="font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:18px; color:#1c1917;">Ordered</td>
    <td style="font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:18px; font-weight:bold; color:#1c1917;">Shipped</td>
    <td style="font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:18px; color:#78716c;">Delivered</td>
  </tr>
</table>
<!-- bulletproof button: "Track parcel RM 4472 9018 1GB" -> https://kettleandco.example/track/48213 -->
<p style="margin:24px 0 0; font-size:14px; line-height:20px; color:#57534e;">Ships to Priya Raman, 14 Harehills Lane, Leeds LS8 4DN. No one in? Royal Mail leaves a card and holds the parcel at the Harehills delivery office for 18 days.</p>
```

## Variations

- **Footer**: transactional mail needs the postal address and a reason ("You received this because you placed order 48213") but no unsubscribe, since the reader cannot opt out of a receipt. Link to notification settings instead.
- **Plain brand header**: swap the logo for a text wordmark in a `<td>` if you cannot count on images loading; receipts are often read with images blocked.
- **Order summary as a card**: put the receipt table inside a cell with `bgcolor="#f5f5f4"` and `padding:16px` to set it apart from the thanks line.
- **Localised dates and money**: format on the server per the recipient's locale and set `lang` on the `<html>` tag and the wrapper `<div>` to match.

## Pitfalls

- Never put the reset token or a password in the preheader, the subject or an image. Tokens are single-use, expire in under an hour, and are bound to the account.
- Turn click tracking off for reset and verification links. Link rewriting adds a redirect hop, breaks signed URLs and shows the reader an unfamiliar domain.
- Send transactional mail from its own subdomain or IP stream (for example `mail.kettleandco.example`) so a bad newsletter send does not delay receipts. Authenticate it per `web-email-testing-and-deliverability`.
- Test with real extremes: a layout that survives "Qty 1" often breaks at 14 line items or a 40-character product name.
- Always include a plain-text part. Password resets are often read in clients with HTML disabled; see `web-email-plain-text-and-accessibility`.

## Related skills

- `web-email-table-layout`
- `web-email-typography-and-buttons`
- `web-email-dark-mode`
- `web-email-testing-and-deliverability`
- `web-email-plain-text-and-accessibility`
- `web-craft-real-content`
