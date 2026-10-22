---
name: web-email-typography-and-buttons
description: Style text and calls to action in HTML email: font stacks with a web font where supported, the Outlook Times New Roman fix, px line-heights, link colours, and bulletproof buttons clickable in classic Outlook. Use when a user asks for an "email button", "CTA in email", "font in my email", "links turn blue" or "button broken in Outlook".
---

# Email typography and bulletproof buttons

Type in email has three audiences. Apple Mail, iOS Mail, Outlook for Mac and Samsung Mail load web fonts. Gmail, Yahoo, Outlook.com and new Outlook ignore them and fall back down your stack. Classic Outlook for Windows renders with Word, which ignores the stack entirely and drops to Times New Roman unless you force a font for it. So design in the fallback (Helvetica/Arial or Georgia), treat the web font as a bonus, and give every text cell its own `font-family`, `font-size`, `line-height` and `color`. Buttons follow the same logic: a styled `<a>` with padding looks right everywhere, but classic Outlook ignores padding on inline elements, so only the words are clickable unless you add the MSO spacing hack below.

## Pattern

```html
<!-- In <head>: web font only for clients outside classic Outlook; forced fallbacks for Word -->
<!--[if !mso]><!-->
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600&display=swap" rel="stylesheet">
<!--<![endif]-->
<!--[if mso]>
<style>
  td, p, a, span, li { font-family: Arial, sans-serif !important; }
  h1, h2, .serif { font-family: Georgia, serif !important; }
</style>
<![endif]-->

<!-- In the body card -->
<td style="padding:32px 24px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; mso-line-height-rule:exactly; color:#1c1917;">
  <h1 style="margin:0 0 12px; font-family:'Source Serif 4', Georgia, 'Times New Roman', serif; font-size:28px; line-height:34px; font-weight:600; color:#1c1917;">Reset your password</h1>
  <p style="margin:0 0 24px;">We got a request to reset the password for priya.raman@example.net. The link below works once and expires in 60 minutes.</p>

  <!-- Bulletproof button: padding for everyone, em-space spacers and text-raise for classic Outlook -->
  <table role="presentation" cellspacing="0" cellpadding="0" border="0">
    <tr>
      <td bgcolor="#1d4ed8" style="border-radius:6px; background-color:#1d4ed8;">
        <a href="https://kettleandco.example/account/reset?t=Qm7x2Vc9LkP4" target="_blank" style="display:inline-block; padding:14px 28px; background-color:#1d4ed8; border-radius:6px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:20px; font-weight:bold; color:#ffffff; text-decoration:none; mso-padding-alt:0; text-underline-color:#1d4ed8;"><!--[if mso]><i style="mso-font-width:175%; mso-text-raise:21pt;">&emsp;</i><span style="mso-text-raise:10.5pt;"><![endif]-->Choose a new password<!--[if mso]></span><i style="mso-font-width:175%;">&emsp;&#8203;</i><![endif]--></a>
      </td>
    </tr>
  </table>

  <p style="margin:24px 0 0; font-size:14px; line-height:20px; color:#57534e;">
    Didn't ask for this? Ignore this email and your password stays the same. Questions go to
    <a href="mailto:help@kettleandco.example" style="color:#1d4ed8; text-decoration:underline;">help@kettleandco.example</a>.
  </p>
</td>
```

How the button works: every client except classic Outlook sees a padded inline-block link, so the whole blue area is the hit target. `mso-padding-alt:0` stops Outlook applying half the padding. Inside conditional comments, the two `<i>` elements hold an em space widened by `mso-font-width` (16 px x 175% = 28 px, matching the side padding), and `mso-text-raise` on the first `<i>` (twice the vertical padding, in pt) plus the `<span>` (once) builds the height. The link now wraps the padding, so Outlook users can click anywhere on the button. `text-underline-color` matching the background hides the underline Outlook adds to every link.

Rules for the text around it:

- **Stacks**: `Helvetica, Arial, sans-serif`; `Georgia, 'Times New Roman', serif`; system UI as `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`. Quote multi-word names with single quotes, since the `style` attribute already uses double quotes.
- **Sizes**: body 16 px (never under 14 px), small print 13 to 14 px, H1 24 to 32 px. Line-height in px, about 1.5x for body and 1.2x for headings.
- **Spacing**: reset `margin:0` on every `<h1>` to `<h3>` and `<p>`, then add the bottom margin you want. Yahoo and Outlook.com add their own heading margins otherwise.

## Variations

- **Outline button**: `background-color:#ffffff; border:2px solid #1d4ed8; color:#1d4ed8;` on the `<a>` with padding reduced by 2 px (`12px 26px`) so it matches the solid button's size. Set the cell `bgcolor` to the page colour.
- **Full-width on phones**: add `class="btn"` to the inner table and `@media screen and (max-width:620px){ .btn { width:100% !important; } .btn a { display:block !important; text-align:center !important; } }`.
- **Two buttons in a row**: one table, three cells: button, a `width="12"` spacer cell, button. Stack them with the column technique from `web-email-responsive` if the labels are long.
- **Pixel-perfect rounded corners in Outlook**: classic Outlook squares off `border-radius`. If the brand needs the curve there, use the VML `v:roundrect` button in `web-email-outlook-fixes`.

## Pitfalls

- Never use `<button>`, `<form>` or JavaScript `onclick`. Most clients strip them, and the rest show a dead control. A CTA is always an `<a href>`.
- Unitless `line-height:1.5` is read differently by Outlook and some Android clients. Use px, and add `mso-line-height-rule:exactly` or Outlook adds its own leading on top.
- Classic Outlook paints links in its default blue and purple. Put `color` and `text-decoration` inline on every `<a>`. If Outlook still overrides a coloured heading link, wrap the text in `<span style="color:...">` inside the link.
- Gmail and Yahoo will never show your web font, so check spacing in the fallback too. A wide display face swapped for Arial can push a headline onto three lines.
- iOS Mail scales text under 13 px. Keep `-webkit-text-size-adjust:100%` on `body` and do not set small print below 13 px.
- Button labels say what happens ("Choose a new password", "Track parcel RM 4472 9018 1GB"), never "Click here". Screen-reader users often jump from link to link and hear only the label.

## Related skills

- `web-email-table-layout`
- `web-email-outlook-fixes`
- `web-email-dark-mode`
- `web-email-plain-text-and-accessibility`
- `web-ui-buttons`
- `web-craft-typography-with-character`
