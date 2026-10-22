---
name: web-email-newsletter-template
description: 'Build a newsletter email: view-in-browser bar, masthead, lead story with image, a two-column "also this month" row, a product spotlight and a compliant footer with unsubscribe, preferences and postal address, kept under Gmail''s 102 KB clip. Use when a user asks for a "newsletter template", "email newsletter layout", "monthly digest email" or "marketing email".'
---

# Newsletter email template

A newsletter is read in a few seconds and skimmed from the top, so the structure is fixed: one lead story that carries the send, a short row of secondary items, one product or offer, and a footer that keeps you legal and out of the spam folder. Build it on the skeleton from `web-email-table-layout`, take columns from `web-email-responsive` and the button from `web-email-typography-and-buttons`, and swap only the rows below. Every story is live text plus one image, so the email still reads with images blocked.

## Pattern

Rows go inside the 600 px container, between the preheader and the closing wrapper. The preheader for this issue: `Smoked Pear is back, a 3-minute guide to cold brew, and 10% off tins until Sunday.`

```html
<!-- 1. Utility bar: view in browser -->
<tr>
  <td class="pad" align="right" style="padding:0 24px 12px; font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:18px; color:#78716c;">
    Trouble reading this? <a href="https://kettleandco.example/newsletter/42" style="color:#78716c; text-decoration:underline;">View in your browser</a>
  </td>
</tr>

<!-- 2. Masthead -->
<tr>
  <td class="pad dm-card" bgcolor="#ffffff" style="padding:20px 24px; background-color:#ffffff; border-radius:8px 8px 0 0; border-bottom:1px solid #e7e5e4; font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:18px; color:#78716c;">
    <a href="https://kettleandco.example/?utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign=n42"><img src="https://cdn.kettleandco.example/email/logo.png" width="120" height="28" alt="Kettle &amp; Co" style="display:block; width:120px; height:28px; border:0;"></a>
    <span style="display:block; padding-top:8px;">The Steep, issue 42, October 2026</span>
  </td>
</tr>

<!-- 3. Lead story: image, headline link, two sentences, text link -->
<tr>
  <td bgcolor="#ffffff" class="dm-card" style="background-color:#ffffff;">
    <a href="https://kettleandco.example/journal/smoked-pear?utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign=n42"><img class="fluid" src="https://cdn.kettleandco.example/email/n42/smoked-pear@2x.jpg" width="600" height="300" alt="A glass cup of Smoked Pear black tea beside a halved pear" style="display:block; width:100%; max-width:600px; height:auto; border:0;"></a>
  </td>
</tr>
<tr>
  <td bgcolor="#ffffff" class="pad dm-card dm-text" style="padding:24px 24px 32px; background-color:#ffffff; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; mso-line-height-rule:exactly; color:#1c1917;">
    <h1 class="h1" style="margin:0 0 8px; font-size:28px; line-height:34px; color:#1c1917;"><a href="https://kettleandco.example/journal/smoked-pear" style="color:#1c1917; text-decoration:none;">Smoked Pear is back for autumn</a></h1>
    <p style="margin:0 0 16px;">We rebuilt the blend with Lapsang from Fujian and dried pear from Kent. It is gentler than last year, and 14 of our 20 testers brewed it a second time.</p>
    <a href="https://kettleandco.example/journal/smoked-pear" style="color:#1d4ed8; font-weight:bold; text-decoration:underline;">Read how we made it</a>
  </td>
</tr>

<!-- 4. Also this month: two columns on desktop, stacked on phones (ghost table + inline-block, see web-email-responsive) -->
<tr>
  <td class="pad dm-card" bgcolor="#faf9f7" style="padding:24px; background-color:#faf9f7; font-size:0; text-align:center; border-top:1px solid #e7e5e4;">
    <!--[if mso]><table role="presentation" width="552" cellspacing="0" cellpadding="0" border="0"><tr><td width="264" valign="top"><![endif]-->
    <div class="col" style="display:inline-block; width:100%; max-width:264px; vertical-align:top;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr>
        <td style="padding:0 12px 16px 0; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; text-align:left; color:#1c1917;">
          <strong style="font-size:17px; line-height:24px;">Cold brew in 3 minutes</strong><br>Fifteen grams, 500 ml of water, fridge overnight. <a href="https://kettleandco.example/journal/cold-brew" style="color:#1d4ed8;">The method</a>
        </td>
      </tr></table>
    </div><!--[if mso]></td><td width="288" valign="top"><![endif]--><div class="col" style="display:inline-block; width:100%; max-width:288px; vertical-align:top;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr>
        <td style="padding:0 0 16px 12px; font-family:Helvetica, Arial, sans-serif; font-size:15px; line-height:22px; text-align:left; color:#1c1917;">
          <strong style="font-size:17px; line-height:24px;">Meet the Leeds packers</strong><br>Four people, one Call Lane workshop, 2,300 tins a week. <a href="https://kettleandco.example/journal/packers" style="color:#1d4ed8;">Say hello</a>
        </td>
      </tr></table>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
  </td>
</tr>

<!-- 5. Offer: bulletproof button from web-email-typography-and-buttons -->
<tr>
  <td bgcolor="#1c1917" class="pad" style="padding:32px 24px; background-color:#1c1917; text-align:center; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#f5f5f4;">
    <h2 style="margin:0 0 8px; font-size:22px; line-height:28px; color:#ffffff;">10% off all 100 g tins until Sunday</h2>
    <p style="margin:0 0 20px;">Code <strong>STEEP10</strong> at checkout. Ends Sunday 25 October.</p>
    <!-- button: "Shop the tins" -> https://kettleandco.example/teas?utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign=n42 -->
  </td>
</tr>

<!-- 6. Footer: reason, unsubscribe, preferences, address -->
<tr>
  <td class="pad" style="padding:24px; font-family:Helvetica, Arial, sans-serif; font-size:13px; line-height:20px; color:#78716c; text-align:center;">
    You get The Steep because you signed up at kettleandco.example on 3 March 2026.<br>
    <a href="https://kettleandco.example/u/Zk3p9Qx7?list=steep" style="color:#57534e; text-decoration:underline;">Unsubscribe</a> &nbsp;|&nbsp;
    <a href="https://kettleandco.example/email/preferences?u=Zk3p9Qx7" style="color:#57534e; text-decoration:underline;">Email preferences</a><br>
    Kettle &amp; Co Ltd, 27 Call Lane, Leeds LS1 7BT, United Kingdom
  </td>
</tr>
```

The unsubscribe link must work in one click with no login, and the same URL backs the `List-Unsubscribe` header set at send time (see `web-email-testing-and-deliverability`).

## Variations

- **Digest of many links**: replace the lead story with a list of 5 to 8 headline rows (headline link, one line of text, 12 px bottom padding). Beyond about 8 items the markup nears Gmail's 102 KB clip.
- **No images at all**: drop the hero image in row 3 and swap the masthead logo for a text wordmark in 22 px bold. Nothing is lost when images are blocked.
- **Sponsor or ad slot**: a labelled row ("Sponsored") with its own `bgcolor` between stories two and three, never above the lead story.
- **Dark footer band**: put `bgcolor="#1c1917"` on the full-width outer `<td>` for the footer and flip link colours to `#d6d3d1`; add the `dm-*` classes from `web-email-dark-mode`.

## Pitfalls

- Gmail clips at 102 KB of HTML. Check the final file with `wc -c` after minifying and inlining; keep newsletters under about 90 KB so personalisation tokens cannot push the footer past the cut.
- Hiding the unsubscribe link in 10 px grey text on grey is a reliable way to get "Report spam" clicks instead. Keep it 13 px, with a contrast ratio of at least 4.5:1.
- UTM parameters on every link are fine, but write `&amp;` in the `href` and keep the URL short; very long tracking URLs inflate the file and wrap badly in the plain-text part.
- A newsletter that is one flattened image is clipped, unreadable with images blocked and spam-filter bait. Keep headlines, prices and codes as live text.
- Always send a plain-text alternative and test the email in Outlook, Gmail and Apple Mail dark mode before scheduling.

## Related skills

- `web-email-table-layout`
- `web-email-responsive`
- `web-email-images`
- `web-email-testing-and-deliverability`
- `web-email-plain-text-and-accessibility`
- `web-section-newsletter-signup`
