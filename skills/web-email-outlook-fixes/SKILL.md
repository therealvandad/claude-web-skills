---
name: web-email-outlook-fixes
description: Fix classic Outlook for Windows (the Word rendering engine): MSO conditional comments, ghost tables, VML bulletproof buttons with rounded corners, VML background images, exact line-heights, spacer rows and DPI scaling. Use when a user says "Outlook breaks my email", "background image missing in Outlook", "rounded button in Outlook" or "extra spacing in Outlook".
---

# Outlook fixes for HTML email

Classic Outlook for Windows (2016 through 2024 and the Microsoft 365 desktop app) renders email with Microsoft Word. It ignores `max-width`, `border-radius`, CSS `background-image`, `margin` on tables and padding on inline elements, and it adds line spacing nobody asked for. New Outlook for Windows, Outlook.com and Outlook for Mac use browser engines and need none of this. Conditional comments are how you talk only to Word: `mso` matches classic Outlook, and every other client treats the markup as a plain HTML comment. Keep each fix small and always supply a normal fallback for everything else.

## Pattern

```html
<!-- 1. Conditional comment syntax -->
<!--[if mso]>      Only classic Outlook sees this.       <![endif]-->
<!--[if !mso]><!--> Everyone except classic Outlook.     <!--<![endif]-->
<!--[if gte mso 9]> Outlook 2000 and later; the VML guard. <![endif]-->

<!-- 2. In <head>: stop 120 DPI scaling, force fonts, remove stray spacing -->
<!--[if mso]>
<noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
<style>
  table, td, div, p, h1, h2 { font-family: Arial, sans-serif !important; }
  table { border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
</style>
<![endif]-->

<!-- 3. Bulletproof VML button: 220 x 48, 6 px radius (6/48 = 13% arcsize) -->
<div>
  <!--[if mso]>
  <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word"
      href="https://kettleandco.example/track/48213" style="height:48px; width:220px; v-text-anchor:middle;"
      arcsize="13%" stroke="f" fillcolor="#1d4ed8">
    <w:anchorlock/>
    <center style="font-family:Arial, sans-serif; font-size:16px; font-weight:bold; color:#ffffff;">Track your parcel</center>
  </v:roundrect>
  <![endif]-->
  <!--[if !mso]><!-->
  <a href="https://kettleandco.example/track/48213" style="display:inline-block; width:220px; line-height:48px; background-color:#1d4ed8; border-radius:6px; font-family:Helvetica, Arial, sans-serif; font-size:16px; font-weight:bold; color:#ffffff; text-align:center; text-decoration:none;">Track your parcel</a>
  <!--<![endif]-->
</div>

<!-- 4. VML background image: CSS background + VML rect with fixed height and a solid fallback colour -->
<tr>
  <td background="https://cdn.kettleandco.example/email/2026-10/hero-bg.jpg" bgcolor="#2b3a2f" width="600" height="280" valign="top"
      style="width:600px; height:280px; background-color:#2b3a2f; background-image:url('https://cdn.kettleandco.example/email/2026-10/hero-bg.jpg'); background-size:cover; background-position:center;">
    <!--[if gte mso 9]>
    <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:600px; height:280px;">
      <v:fill type="frame" src="https://cdn.kettleandco.example/email/2026-10/hero-bg.jpg" color="#2b3a2f"/>
      <v:textbox inset="0,0,0,0" style="mso-fit-shape-to-text:false;">
    <![endif]-->
    <div style="padding:48px 32px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; mso-line-height-rule:exactly; color:#ffffff;">
      <h1 style="margin:0 0 8px; font-size:32px; line-height:38px; mso-line-height-rule:exactly; color:#ffffff;">Autumn blends are back</h1>
      <p style="margin:0;">Smoked Pear, Hojicha Chai and Bonfire Rooibos, from &pound;8.50.</p>
    </div>
    <!--[if gte mso 9]></v:textbox></v:rect><![endif]-->
  </td>
</tr>

<!-- 5. Line-height and spacer fixes -->
<p style="margin:0; font-size:16px; line-height:24px; mso-line-height-rule:exactly;">Body copy with exact leading.</p>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr>
  <td height="24" style="height:24px; font-size:24px; line-height:24px; mso-line-height-rule:exactly;">&nbsp;</td>
</tr></table>
```

Why each fix exists: Word refuses `border-radius`, so the VML `roundrect` draws the curve and `w:anchorlock` stops a click on the label from selecting the shape instead of following the link. VML needs the `xmlns:v` declaration (declared on the `<html>` tag in `web-email-table-layout`, repeated inline here so a snippet works alone). The VML background needs a fixed height; if the text inside is taller, Outlook clips it. `mso-line-height-rule:exactly` makes Word honour your px line-height instead of treating it as a minimum. Spacer cells set `font-size` equal to `height`, because Word will not make a row shorter than one line of its font.

## Variations

- **Ghost table for a fixed 600 px width**: `<!--[if mso]><table role="presentation" width="600" align="center" cellspacing="0" cellpadding="0" border="0"><tr><td><![endif]-->` before the container and the matching close after it. Word then ignores the missing `max-width`.
- **Hide something from Outlook**: `mso-hide:all` inline, or wrap it in `<!--[if !mso]><!-->...<!--<![endif]-->`. Use both for dark-mode logo swaps.
- **Outlook-only fallback link**: show a "view in browser" line to Word only, `<!--[if mso]><p>View in browser: https://kettleandco.example/e/48213</p><![endif]-->`.
- **Target a version**: `<!--[if mso 16]>` for Outlook 2016 and later, `<!--[if (mso 12)|(mso 14)]>` for older ones. In 2026 there is rarely a reason to go below `gte mso 9`.

## Pitfalls

- Every opened conditional must be closed, and an unbalanced `<!--[if mso]><table>` without its closing half will break every other client's layout. Test in Outlook.com and Gmail as well as classic Outlook.
- VML images and backgrounds are blocked until the reader clicks "Download pictures", so keep `bgcolor` and readable text colour on the cell.
- Do not use the `!mso` form around the whole body to hide a broken layout from Outlook. Fix the layout; Outlook users are often your enterprise customers.
- `<!--[if mso]>` is not matched by new Outlook, Outlook.com or Outlook for Mac. Never put required content only inside an `mso` block.
- Outlook ignores `padding` on `<a>` and `<span>`, and `margin` on `<div>` and `<table>`. Put padding on `<td>` and spacing in spacer rows.
- The VML `<center>` label does not wrap; keep button labels short and size the shape in px, not %.

## Related skills

- `web-email-table-layout`
- `web-email-typography-and-buttons`
- `web-email-images`
- `web-email-responsive`
- `web-email-testing-and-deliverability`
