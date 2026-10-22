---
name: web-email-dark-mode
description: 'Make HTML email look deliberate in dark mode: color-scheme meta tags, prefers-color-scheme styles for Apple Mail, [data-ogsc] and [data-ogsb] hooks for Outlook.com and new Outlook, logo swaps, and colours that survive forced inversion. Use when a user says "email dark mode", "logo disappears in dark mode" or "Outlook inverts my colours".'
---

# Dark mode in HTML email

There is no single dark mode in email; there are three behaviours, and you design for all of them at once.

| Behaviour | Clients (2026) | What you control |
|---|---|---|
| Honours your dark styles | Apple Mail (macOS, iOS, iPadOS), Outlook for Mac, Thunderbird | Everything, through `@media (prefers-color-scheme: dark)` |
| Partial inversion: light backgrounds go dark, dark text goes light | Outlook.com, new Outlook for Windows, Outlook for iOS and Android, Gmail for Android | Override with `[data-ogsc]` / `[data-ogsb]` in Outlook.com and new Outlook; nothing in Gmail |
| Full inversion: every colour flipped | Gmail for iOS, classic Outlook for Windows | Nothing, only colour choices that invert well |

Gmail on the web does not change the message at all. Because you cannot stop the inverting clients, pick a palette that reads in both directions, then add exact dark styles for the clients that let you.

## Pattern

```html
<head>
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <style>
    :root { color-scheme: light dark; supported-color-schemes: light dark; }

    @media (prefers-color-scheme: dark) {
      .dm-page  { background-color:#1c1917 !important; }
      .dm-card  { background-color:#292524 !important; }
      .dm-text  { color:#f5f5f4 !important; }
      .dm-muted { color:#a8a29e !important; }
      .dm-link  { color:#93c5fd !important; }
      .logo-light { display:none !important; }
      .logo-dark  { display:block !important; max-height:none !important; overflow:visible !important; }
    }
  </style>
  <!-- Separate block: Gmail drops a whole <style> block it cannot parse, attribute selectors included -->
  <style>
    /* Outlook.com and new Outlook: no media query, but they tag every element they recolour */
    [data-ogsb] .dm-page  { background-color:#1c1917 !important; }
    [data-ogsb] .dm-card  { background-color:#292524 !important; }
    [data-ogsc] .dm-text  { color:#f5f5f4 !important; }
    [data-ogsc] .dm-muted { color:#a8a29e !important; }
    [data-ogsc] .dm-link  { color:#93c5fd !important; }
    [data-ogsc] .logo-light { display:none !important; }
    [data-ogsc] .logo-dark  { display:block !important; max-height:none !important; overflow:visible !important; }
  </style>
</head>

<body class="body dm-page" style="margin:0; background-color:#f4f1ec; color:#1c1917;">
  <!-- ... wrapper and 600 px container from web-email-table-layout ... -->
  <tr>
    <td class="dm-page" style="padding:0 24px 16px; background-color:#f4f1ec;">
      <img class="logo-light" src="https://cdn.kettleandco.example/email/logo-ink.png" width="140" height="32" alt="Kettle &amp; Co" style="display:block; border:0;">
      <!--[if !mso]><!-->
      <div class="logo-dark" style="display:none; max-height:0; overflow:hidden; mso-hide:all;">
        <img src="https://cdn.kettleandco.example/email/logo-cream.png" width="140" height="32" alt="Kettle &amp; Co" style="display:block; border:0;">
      </div>
      <!--<![endif]-->
    </td>
  </tr>
  <tr>
    <td class="dm-card dm-text" bgcolor="#ffffff" style="padding:32px 24px; background-color:#ffffff; color:#1c1917; font-family:Helvetica, Arial, sans-serif; font-size:16px; line-height:24px;">
      <h1 class="dm-text" style="margin:0 0 12px; font-size:24px; line-height:32px; color:#1c1917;">Bonfire Rooibos is back</h1>
      <p class="dm-muted" style="margin:0 0 16px; color:#57534e;">Smoked rooibos, cinnamon and orange peel. Caffeine free, &pound;8.50 for 100 g.</p>
      <a class="dm-link" href="https://kettleandco.example/bonfire-rooibos" style="color:#1d4ed8; text-decoration:underline;">Read the tasting notes</a>
    </td>
  </tr>
</body>
```

Why it works: the meta tags and `:root` declaration tell Apple Mail the email supports both schemes, so it applies your media query instead of its own auto-darkening. `!important` is required because the light values are inline. Outlook.com and new Outlook add `data-ogsc` (original style colour) and `data-ogsb` (original style background) to elements they recolour; the descendant selectors match once an ancestor carries those attributes, which is why the `body` and wrapper cells have inline `color` and `background-color`. The dark logo is hidden from classic Outlook twice, by the conditional comment and by `mso-hide:all`, because Word ignores `display:none` on some elements.

## Variations

- **Single image that works on both**: a transparent PNG logo with a 2 px cream outline, or a logo placed on its own fixed-colour "badge" cell. No swap needed, and it also survives Gmail iOS and classic Outlook, where no swap works.
- **Apple Mail only, no extra markup**: `<picture><source srcset="logo-cream.png" media="(prefers-color-scheme: dark)"><img src="logo-ink.png" ...></picture>`. Other clients show the `<img>`.
- **Keep white text white in Gmail iOS**: wrap text in `<div class="gmail-screen"><div class="gmail-diff">` and add `u + .body .gmail-screen { background:#000; mix-blend-mode:screen; } u + .body .gmail-diff { background:#000; mix-blend-mode:difference; }`. Fragile; use it on one hero headline, not the whole email.
- **Light-only email**: declare `content="light"` in both metas and `color-scheme: light`. Apple Mail then leaves it alone; the inverting clients still invert.

## Pitfalls

- Pure `#ffffff` and `#000000` invert into each other with harsh contrast. Use off-white `#f4f1ec` and near-black `#1c1917`; they flip into softer tones.
- Text baked into images never inverts. A dark-on-transparent headline image vanishes on a dark background. Keep text live.
- Brand colours shift under partial inversion: a mid-blue button can turn pale with white text that no longer passes contrast. Check every coloured cell in Outlook.com dark and Gmail Android; give buttons colours that keep 4.5:1 either way.
- Gmail does not support `prefers-color-scheme` or attribute selectors, and one rule it rejects can cost the whole `<style>` block. Keep the `[data-ogsc]` rules in their own block, apart from media queries and resets.
- Microsoft has changed how Outlook.com tags elements more than once. Re-test the `[data-ogsc]` hooks in Outlook.com and new Outlook each quarter, not just once.
- Dark images with transparent edges show a light halo after inversion. Export photos as JPEG with a background matched to the cell colour.

## Related skills

- `web-email-images`
- `web-email-typography-and-buttons`
- `web-email-testing-and-deliverability`
- `web-design-dark-mode`
- `web-a11y-color-contrast`
