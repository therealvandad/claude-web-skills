---
name: web-email-plain-text-and-accessibility
description: Write the plain-text alternative for an HTML email and make the HTML accessible: multipart/alternative structure, readable text layout, lang and title, presentation tables, real headings and lists, data tables with header cells, link and alt text, contrast and font size. Use when a user asks for "plain text version", "accessible email", "screen reader email" or "email alt text".
---

# Plain text and accessibility in email

Two kinds of reader never see your design: those whose client shows only text (Apple Watch, terminal and some corporate gateways, spam scanners) and those whose screen reader walks the source order. Both are served by the same habit: the message must make sense as a linear sequence of words. Spam filters also compare the HTML and plain parts, and a missing or mismatched plain part costs reputation. So send a hand-written plain-text part, keep the HTML in a logical reading order, and use structure that assistive tech can read.

## Pattern

Send `multipart/alternative` with the plain part first and the HTML part last (clients show the last part they support). Most ESPs build this when you supply both bodies:

```text
Content-Type: multipart/alternative; boundary="b1_9c2f"

--b1_9c2f
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

--b1_9c2f
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

--b1_9c2f--
```

The plain-text part, written by hand rather than auto-stripped from the HTML. Lines stay under about 70 characters, each URL sits on its own line, and the footer carries the address and unsubscribe link:

```text
YOUR ORDER IS ON ITS WAY

Hi Priya,

Royal Mail collected 2 items today. Expected delivery: Monday 26 October,
before 1 pm.

Track parcel RM 4472 9018 1GB:
https://kettleandco.example/track/48213

Ships to
  Priya Raman
  14 Harehills Lane
  Leeds LS8 4DN

Questions? Reply to this email.

--
Kettle & Co Ltd, 27 Call Lane, Leeds LS1 7BT, United Kingdom
You received this because you placed order 48213.
Email preferences: https://kettleandco.example/email/preferences?u=48213
```

The accessible HTML shape, inside the skeleton from `web-email-table-layout`:

```html
<html lang="en" dir="ltr" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head><meta charset="UTF-8"><title>Your order 48213 is on its way</title></head>
<body style="margin:0; background-color:#f4f1ec;">
  <div role="article" aria-roledescription="email" aria-label="Your order 48213 is on its way" lang="en">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td align="center">
      <!-- layout tables all carry role="presentation" -->
      <h1 style="margin:0 0 12px; font-family:Helvetica, Arial, sans-serif; font-size:24px; line-height:32px; color:#1c1917;">Your order is on its way</h1>
      <h2 style="margin:24px 0 8px; font-family:Helvetica, Arial, sans-serif; font-size:18px; line-height:24px; color:#1c1917;">What is in the parcel</h2>

      <!-- Real data: no role="presentation", header cells with scope -->
      <table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;">
        <tr>
          <th scope="col" align="left" style="padding:8px 0; font-family:Helvetica, Arial, sans-serif; font-size:14px; line-height:20px; color:#57534e; border-bottom:1px solid #e7e5e4;">Item</th>
          <th scope="col" align="right" style="padding:8px 0; font-family:Helvetica, Arial, sans-serif; font-size:14px; line-height:20px; color:#57534e; border-bottom:1px solid #e7e5e4;">Price</th>
        </tr>
        <tr>
          <td style="padding:8px 0; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;">Hojicha Chai, 100 g, quantity 2</td>
          <td align="right" style="padding:8px 0; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;">&pound;18.00</td>
        </tr>
      </table>

      <!-- Real list: ul/li with inline styles reads as "list, 3 items" -->
      <ul style="margin:16px 0; padding:0 0 0 20px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;">
        <li style="margin:0 0 4px;">Delivery by Royal Mail Tracked 48</li>
        <li style="margin:0 0 4px;">Signature not required</li>
      </ul>

      <a href="https://kettleandco.example/track/48213" style="color:#1d4ed8; text-decoration:underline;">Track parcel RM 4472 9018 1GB</a>
      <img src="https://cdn.kettleandco.example/email/tin-hojicha@2x.jpg" width="120" height="120" alt="Hojicha Chai tin, green label" style="display:block; border:0;">
      <img src="https://cdn.kettleandco.example/email/leaf-rule.png" width="64" height="8" alt="" style="display:block; border:0;">
    </td></tr></table>
  </div>
</body>
</html>
```

## Variations

- **Mixed-language email**: put `lang="fr"` on the element holding the French copy so a screen reader switches voice; keep `lang` on `<html>` as the main language.
- **Receipt without a data table**: if you lay line items out as presentation tables, repeat the label in each row ("Quantity 2, 18 pounds") so it still makes sense without column headers.
- **Plain text from a template**: generate it in the same build step and diff the link lists against the HTML so a link added to one is added to the other.
- **Hidden text for screen readers**: avoid it. Clients strip `clip` and `position:absolute` tricks; write visible text that works for everyone.

## Pitfalls

- A layout table without `role="presentation"` is announced as a table with rows and columns for every nested box. Data tables, by contrast, must not carry it, or their headers are lost.
- Source order is reading order. Columns reversed with `dir="rtl"` or stacked in a different order on mobile are read in source order, so put the headline first in the HTML.
- Contrast must reach 4.5:1 for body text (3:1 for 24 px or bold 19 px and up) in light and in dark mode. `#78716c` on white is 4.8:1; `#a8a29e` on white fails.
- "Click here", "Read more" and bare URLs as link text are useless in a screen reader's link list. Name the destination ("Track parcel RM 4472 9018 1GB"). Underline links; colour alone does not mark them.
- Body text under 14 px, light grey footers and all-caps paragraphs are hard to read. Keep body at 16 px and tap targets at least 44 px tall.
- Alt text rules: informative images get a short description of what the reader would miss, decorative ones get `alt=""`, a linked image gets the destination. Never write "image of".
- A plain part that says only "Your email client does not support HTML" gives readers and spam filters nothing to work with.

## Related skills

- `web-email-table-layout`
- `web-email-images`
- `web-email-typography-and-buttons`
- `web-email-testing-and-deliverability`
- `web-a11y-color-contrast`
- `web-a11y-images-and-media`
