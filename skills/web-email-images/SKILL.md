---
name: web-email-images
description: Add images to HTML email that survive every client: width and height attributes for Outlook, fluid CSS for phones, 2x retina files, styled alt text and background colour for blocked images, and decorative versus informative alt. Use when a user says "image in email", "email images blown up in Outlook", "images blocked" or "retina email images".
---

# Images in HTML email

Assume images are off. Classic Outlook blocks them until the reader clicks "Download pictures", many corporate tenants never allow them, and some readers turn them off on purpose. The email has to make sense from alt text and live text alone, so the headline, the price and the button are always HTML, never pixels. When images do load, three things decide whether they look right: an absolute HTTPS URL, a `width` attribute (classic Outlook ignores CSS widths and renders the file at its natural size), and fluid inline CSS so the same image shrinks on a phone.

## Pattern

```html
<!-- Hero: file is 1200x600 (2x), shown at 600x300. Cell colour shows when images are blocked. -->
<tr>
  <td bgcolor="#d6cfc4" style="background-color:#d6cfc4;">
    <a href="https://kettleandco.example/autumn?utm_source=email&amp;utm_medium=newsletter&amp;utm_campaign=autumn26" target="_blank">
      <img src="https://cdn.kettleandco.example/email/2026-10/autumn-hero@2x.jpg"
           width="600" height="300"
           alt="Autumn blends are back: Smoked Pear, Hojicha Chai and Bonfire Rooibos"
           style="display:block; width:100%; max-width:600px; height:auto; border:0;
                  font-family:Helvetica, Arial, sans-serif; font-size:18px; line-height:24px; color:#1c1917;">
    </a>
  </td>
</tr>

<!-- Product thumbnail beside live text: the alt says what it is, the text carries name and price -->
<tr>
  <td style="padding:24px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
      <tr>
        <td width="120" valign="top" style="width:120px;">
          <img src="https://cdn.kettleandco.example/products/kyusu-600-black@2x.jpg" width="120" height="120"
               alt="Black cast iron kyusu teapot, side view" style="display:block; width:120px; height:120px; border:0; border-radius:6px;">
        </td>
        <td valign="top" style="padding-left:16px; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px; color:#1c1917;">
          <strong>Cast iron kyusu, 600 ml</strong><br>
          Enamelled inside, side handle, steel mesh infuser. <span style="white-space:nowrap;">&pound;29.50</span>
        </td>
      </tr>
    </table>
  </td>
</tr>

<!-- Decorative flourish: empty alt so screen readers skip it -->
<img src="https://cdn.kettleandco.example/email/leaf-rule.png" width="64" height="8" alt="" style="display:block; width:64px; height:8px; border:0;">
```

What each attribute does:

- `width` and `height` attributes, unitless: classic Outlook sizes the image from them, and the reserved box stops the layout jumping in clients that load images late. With `height:auto` in the inline style, everyone else keeps the aspect ratio when `width:100%` shrinks it.
- `display:block`: removes the 3 to 4 px gap Gmail and Outlook.com leave under inline images.
- Styled `alt`: Apple Mail, Outlook.com, Yahoo and most Gmail views render alt text using the `<img>` font styles when the image is missing, so it reads as part of the design instead of a broken icon. Classic Outlook shows plain alt in a box and ignores the styling.
- `bgcolor` on the cell: when images are off, the reader sees a block in the hero's main colour, not a white hole.

## Variations

- **Retina**: export at exactly 2x the display width (1200 px for a 600 px hero) and compress hard: JPEG quality 60 to 70 at 2x looks sharper than quality 90 at 1x. Keep each file under about 200 KB and the whole email under about 1 MB.
- **Animated GIF**: classic Outlook shows only the first frame, so make frame one complete on its own (headline and product visible). Keep GIFs under 1 MB and avoid more than three flashes per second.
- **Background image with live text on top**: set it both ways, `background="https://...jpg"` attribute plus `background-image:url('https://...jpg'); background-size:cover; background-position:center;` inline, with a solid `bgcolor` that keeps the text readable when the image fails. Classic Outlook needs the VML wrapper from `web-email-outlook-fixes`.
- **Logo for dark mode**: give dark-ink logos a 2 px off-white outline baked into the PNG, or swap to a light version with the technique in `web-email-dark-mode`.

## Pitfalls

- A 1200 px file with no `width` attribute renders 1200 px wide in classic Outlook and pushes the email off-screen. Always set the attribute to the display width.
- Data URIs and base64 images are blocked by Gmail and classic Outlook, and they count towards Gmail's 102 KB clip. SVG does not render in Gmail or classic Outlook. WebP and AVIF still fail in classic Outlook and some Android clients, so send JPEG, PNG or GIF.
- An email that is one big image, or mostly images, scores badly with spam filters, is invisible with images off, cannot be read by screen readers, and cannot be zoomed or translated. Aim for at least 60% live text.
- Alt text is not a caption or a keyword list. Write what the reader would miss ("Autumn blends are back: ..."). For an image inside a link, the alt is the link's name, so describe the destination. Purely decorative images get `alt=""`, never a missing `alt`, which makes some screen readers read the file name.
- Gmail proxies images through its own servers and Apple Mail Privacy Protection preloads them, so open rates from tracking pixels are inflated and unreliable. Do not build logic on them.
- Spaces or unencoded `&` in image URLs break in Outlook. Use lowercase hyphenated file names and `&amp;` in query strings.

## Related skills

- `web-email-table-layout`
- `web-email-outlook-fixes`
- `web-email-dark-mode`
- `web-email-responsive`
- `web-a11y-images-and-media`
- `web-perf-images`
