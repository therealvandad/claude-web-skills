---
name: web-email-responsive
description: Make HTML email fluid on phones with the hybrid method: max-width cells and inline-block columns that wrap without media queries, MSO ghost tables for Outlook, and a small @media block that stacks, resizes and pads where supported. Use when a user says "responsive email", "email columns won't stack", "email too small on iPhone" or "mobile email layout".
---

# Responsive HTML email

Media queries in email are an upgrade, not the foundation. Apple Mail, iOS Mail, Outlook.com and new Outlook, Yahoo and Gmail with a Google account honour `@media` in `<style>`. Gmail's app with a non-Google address (GANGA) and some webmail views have historically dropped embedded styles, and classic Outlook for Windows ignores `max-width` and has no media queries at all. The hybrid method works in all of them: columns are `inline-block` divs with a `max-width` that wrap on their own when the screen is narrower than two columns, a ghost table pins them side by side in Outlook, and the media query only tidies up where it exists. Start from the skeleton in `web-email-table-layout`.

## Pattern

```html
<head>
  <style>
    @media screen and (max-width: 620px) {
      .pad    { padding-left:16px !important; padding-right:16px !important; }
      .col    { display:block !important; width:100% !important; max-width:100% !important; }
      .pad-col { padding-left:0 !important; padding-top:16px !important; }
      .fluid  { width:100% !important; height:auto !important; }
      .h1     { font-size:26px !important; line-height:32px !important; }
      .hide   { display:none !important; max-height:0 !important; overflow:hidden !important; mso-hide:all !important; }
      .btn a  { display:block !important; text-align:center !important; }
    }
  </style>
</head>

<!-- Article row: image left, text right on desktop; stacked, image first, on phones -->
<tr>
  <td class="pad" style="padding:24px; font-size:0; text-align:center; background-color:#ffffff;">
    <!--[if mso]><table role="presentation" width="552" cellspacing="0" cellpadding="0" border="0"><tr><td width="216" valign="top"><![endif]-->
    <div class="col" style="display:inline-block; width:100%; max-width:216px; vertical-align:top;">
      <img class="fluid" src="https://cdn.kettleandco.example/email/2026-10/hojicha-tin@2x.jpg" width="216" height="216"
           alt="Hojicha Chai tin, 100 g, on a wooden counter" style="display:block; width:216px; max-width:100%; height:auto; border:0;">
    </div><!--[if mso]></td><td width="336" valign="top"><![endif]--><div class="col" style="display:inline-block; width:100%; max-width:336px; vertical-align:top;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
          <td style="padding:0 0 0 24px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; text-align:left; color:#1c1917;" class="pad-col">
            <h2 style="margin:0 0 8px; font-size:20px; line-height:26px; color:#1c1917;">Hojicha Chai</h2>
            <p style="margin:0 0 16px;">Roasted green tea with cardamom and clove. Brews in 3 minutes at 95&nbsp;&deg;C. &pound;9.00 for 100&nbsp;g.</p>
            <table role="presentation" class="btn" cellspacing="0" cellpadding="0" border="0"><tr>
              <td bgcolor="#1d4ed8" style="border-radius:6px;"><a href="https://kettleandco.example/hojicha-chai" style="display:inline-block; padding:12px 24px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:20px; font-weight:bold; color:#ffffff; text-decoration:none;">Shop Hojicha Chai</a></td>
            </tr></table>
          </td>
        </tr>
      </table>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
  </td>
</tr>
```

How it behaves: the parent cell has `font-size:0` so the whitespace between inline-blocks is zero wide and the two columns (216 + 336 = 552, the 600 px container minus 24 px padding each side) fit. Below 552 px they wrap by themselves even if the `<style>` block is gone. Where media queries work, `.col` goes full width and `.pad-col` can drop its left padding. The Outlook ghost table `width` values must equal the `max-width` of each div, and the comment markers sit directly against the closing and opening `</div><div>` so no stray whitespace creates a gap.

## Variations

- **Reverse stack order**: write the image column second in the source, add `dir="rtl"` on the cell holding the columns and `dir="ltr"` on each column's inner cell. Desktop shows image left; phones show it first.
- **Hide a desktop-only element**: `class="hide"` as above, with `mso-hide:all` for Outlook. Hidden content still counts towards the 102 KB Gmail clip, so use sparingly.
- **Two stat tiles side by side on phones**: skip `.col` and give both tiles `width="50%"` in one table row; they stay in a row at 320 px if the text is short.
- **Fluid body copy for tablets**: leave the container at `max-width:600px` and let it shrink; do not add a separate tablet breakpoint.

## Pitfalls

- Gmail ignores the whole `<style>` block if it holds a parse error or an unsupported at-rule. Keep media queries in one small clean block and inline every base style.
- Outlook ignores `max-width` on images and divs. Always pair it with a `width` attribute on images and the ghost table around columns.
- Use `screen and (max-width: 620px)`, not `(max-width: 600px)`: the 600 px container plus 12 px gutters needs 624 px, so a 610 px window would otherwise keep the desktop padding while the container is already squeezed.
- Tap targets under 44 x 44 px are hard to hit on phones. Give links in lists `padding:12px 0` as a block, and keep body text at 16 px so iOS does not enlarge it.
- Do not rely on `display:none` to ship a separate mobile layout: it doubles the markup, risks the 102 KB clip, and Yahoo and some Gmail views show both copies.
- Test at 320, 375 and 414 px widths plus a 768 px tablet. Samsung Mail and the Gmail app render at different effective widths than a browser resize shows.

## Related skills

- `web-email-table-layout`
- `web-email-outlook-fixes`
- `web-email-images`
- `web-email-typography-and-buttons`
- `web-css-container-queries`
