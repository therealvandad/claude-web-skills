---
name: web-email-table-layout
description: Build the HTML email skeleton for Gmail, Apple Mail, Outlook and Yahoo: full-width wrapper table, 600 px container with an MSO ghost table, preheader, columns and footer, spaced with cell padding and inline styles. Use whenever a user asks for an "email template", "HTML email", "email layout", "email looks broken in Outlook" or "how do I start an email".
---

# HTML email table layout

Email clients are not browsers. Gmail strips `<head>` styles in some apps, classic Outlook for Windows renders with Microsoft Word, and no client runs JavaScript. So the pack's Tailwind and JS rules do not apply here: layout is nested tables with `role="presentation"`, every style is inline on the `<td>` or the element, and the only reliable spacing is cell `padding` and spacer rows. Width is a `width` attribute *and* an inline style, because Outlook reads the attribute and everything else reads the style. Build this skeleton once and put every email inside it.

## Pattern

```html
<!DOCTYPE html>
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <title>Your order 48213 is on its way</title>
  <!--[if mso]>
  <noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
  <style>td, p, a, h1, h2 { font-family: Arial, sans-serif !important; }</style>
  <![endif]-->
  <style>
    body { margin:0; padding:0; word-spacing:normal; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }
    table, td { border-collapse:collapse; mso-table-lspace:0pt; mso-table-rspace:0pt; }
    img { border:0; display:block; line-height:100%; outline:none; text-decoration:none; -ms-interpolation-mode:bicubic; }
    a[x-apple-data-detectors], u + .body a, #MessageViewBody a { color:inherit !important; text-decoration:none !important; }
    @media screen and (max-width: 620px) {
      .col { display:block !important; width:100% !important; max-width:100% !important; }
      .pad { padding-left:16px !important; padding-right:16px !important; }
    }
  </style>
</head>
<body class="body" style="margin:0; padding:0; background-color:#f4f1ec;">
  <!-- Preheader: the inbox preview line. Hidden once opened; the &zwnj;&nbsp; run stops the footer bleeding into the preview. -->
  <div style="display:none; font-size:1px; line-height:1px; max-height:0; max-width:0; opacity:0; overflow:hidden; mso-hide:all;" aria-hidden="true">
    Royal Mail has it. Expected Saturday 24 October, before 1 pm.
    &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
  </div>

  <div role="article" aria-roledescription="email" aria-label="Your order is on its way" lang="en" style="background-color:#f4f1ec;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#f4f1ec" style="width:100%; background-color:#f4f1ec;">
    <tr>
      <td align="center" style="padding:24px 12px;">
        <!--[if mso]><table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" align="center"><tr><td><![endif]-->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" align="center" style="width:100%; max-width:600px; margin:0 auto;">
          <tr>
            <td class="pad" style="padding:0 24px 16px;">
              <a href="https://kettleandco.example" style="text-decoration:none;">
                <img src="https://cdn.kettleandco.example/email/logo.png" width="140" height="32" alt="Kettle &amp; Co" style="width:140px; height:32px; display:block;">
              </a>
            </td>
          </tr>
          <tr>
            <td bgcolor="#ffffff" class="pad" style="padding:32px 24px; background-color:#ffffff; border-radius:8px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;">
              <h1 style="margin:0 0 12px; font-size:24px; line-height:32px; font-weight:bold; color:#1c1917;">Your order is on its way</h1>
              <p style="margin:0 0 16px;">Royal Mail picked up order 48213 this morning. Expected delivery is Saturday 24 October, before 1 pm.</p>
              <!-- Spacer row: the only vertical space Outlook honours exactly -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td height="8" style="height:8px; line-height:8px; font-size:0;">&nbsp;</td></tr></table>
              <!-- Two columns: inline-block divs wrap on their own where media queries are stripped; .col stacks them where they work; ghost table holds Outlook at two columns -->
              <!--[if mso]><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td width="276" valign="top"><![endif]-->
              <div class="col" style="display:inline-block; width:100%; max-width:276px; vertical-align:top;">
                <p style="margin:0; font-size:13px; line-height:18px; color:#78716c;">Ships to</p>
                <p style="margin:0 0 16px;">Priya Raman<br>14 Harehills Lane<br>Leeds LS8 4DN</p>
              </div><!--[if mso]></td><td width="276" valign="top"><![endif]--><div class="col" style="display:inline-block; width:100%; max-width:276px; vertical-align:top;">
                <p style="margin:0; font-size:13px; line-height:18px; color:#78716c;">Tracking</p>
                <p style="margin:0 0 16px;"><a href="https://kettleandco.example/track/48213" style="color:#1d4ed8;">RM 4472 9018 1GB</a></p>
              </div>
              <!--[if mso]></td></tr></table><![endif]-->
            </td>
          </tr>
          <tr>
            <td class="pad" style="padding:24px; font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:20px; color:#78716c;">
              Kettle &amp; Co Ltd, 27 Call Lane, Leeds LS1 7BT, United Kingdom<br>
              You get these emails because you placed an order. <a href="https://kettleandco.example/email/preferences?u=48213" style="color:#78716c;">Email preferences</a>
            </td>
          </tr>
        </table>
        <!--[if mso]></td></tr></table><![endif]-->
      </td>
    </tr>
  </table>
  </div>
</body>
</html>
```

Why each piece is there: the `xmlns:v` and `xmlns:o` namespaces let Outlook parse VML later. `x-apple-disable-message-reformatting` stops iOS Mail zooming out the layout. `PixelsPerInch` keeps Outlook from scaling images on 120 DPI screens. The MSO `<style>` forces Arial in Outlook, which otherwise drops to Times New Roman the moment it meets a font it does not know. `u + .body a` and `#MessageViewBody a` kill the blue auto-links Gmail and Samsung Mail add to addresses and dates. The outer table carries `bgcolor` because Gmail ignores `background-color` on `<body>`. The ghost table (`<!--[if mso]>`) gives Outlook a fixed 600 px, since Word ignores `max-width`. `role="presentation"` stops screen readers announcing "table, 3 rows" for every layout box; `role="article"` with `aria-roledescription="email"` on the wrapper gives them a landmark to jump to.

## Variations

- **Full-bleed header band**: put `bgcolor` on a full-width outer `<td>` and nest a second 600 px container inside it; one container per band, stacked, rather than one container with coloured rows.
- **Three columns**: three inline-block divs at `max-width:184px` inside a `font-size:0` cell (so whitespace between them is zero wide), with a three-cell ghost table of `width="184"`.
- **Reverse stacking order on mobile** (image right on desktop, first on mobile): put the image column second in source and set `dir="rtl"` on the ghost table row, `dir="ltr"` back on each column.
- **Dividers**: a `<tr><td height="1" bgcolor="#e7e5e4" style="height:1px; line-height:1px; font-size:0;">&nbsp;</td></tr>` row. `<hr>` renders differently in every client.

## Pitfalls

- `margin` on tables and divs is ignored by Outlook and unreliable in Gmail. Space with `padding` on `<td>`, spacer rows, or the `margin` on `<p>` and `<h1>` which do survive; reset those to `margin:0` first.
- Gmail clips the message at 102 KB of HTML and shows "[Message clipped]", which hides your footer and unsubscribe link. Minify, drop comments before sending, and do not inline styles that nothing reads. Images do not count; markup does.
- Gmail limits `<style>` to about 16 KB and drops the whole block if it contains an unsupported `@import` or a parse error. Inline anything that must hold; keep the head for media queries and fixes only.
- Classic Outlook inserts a page break and a white gap in any single table taller than about 1,790 px. Split long emails into stacked tables, one per section.
- Each new `<td>` in Outlook resets the font to Times New Roman 12 pt. Repeat `font-family`, `font-size`, `line-height` and `color` on every text-bearing cell, not only on the wrapper.
- Set `bgcolor` on the `<td>`, not the `<table>`: Outlook at 120 DPI draws 1 px light seams between cells when the colour sits on the table.

## Related skills

- `web-email-typography-and-buttons`
- `web-email-responsive`
- `web-email-outlook-fixes`
- `web-email-transactional-templates`
- `web-email-plain-text-and-accessibility`
- `web-craft-copy-that-sounds-human`
