---
name: web-theme-retro
description: 'Drop a deliberate period look onto a site in Tailwind v4: 70s print with Caprasimo display, Bricolage Grotesque body, mustard, orange and brown stripe bands, pill buttons and thick brown rules, or a 90s web variant, both with real contrast. Use whenever a user says "retro", "vintage", "70s", "90s website", "old school", "nostalgic", "groovy" or "like an old poster".'
---

# Retro theme

A period look works when it borrows the era's decisions, not its limitations. 70s print had a heavy rounded serif, three warm inks, stripes printed as flat bands and lots of brown; it did not have low contrast, it had cheap paper. Take the type, the ink set and the stripe, set them on a modern grid with modern readability, and the page reads as a homage. Add fake wear, scratches and a sepia filter, and it reads as a costume.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caprasimo&family=Bricolage+Grotesque:opsz,wght@12..96,400..700&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Caprasimo", "Cooper Black", "Georgia", serif;
  --font-sans: "Bricolage Grotesque", "Trebuchet MS", system-ui, sans-serif;

  /* Newsprint cream and chocolate brown: the paper and ink of a 1974 poster. */
  --color-paper:   oklch(94% 0.035 85);
  --color-paper-2: oklch(89% 0.060 85);
  --color-ink:     oklch(26% 0.045 45);
  --color-ink-2:   oklch(42% 0.050 45);
  --color-line:    oklch(26% 0.045 45);   /* rules are ink, never grey */

  /* The three-ink stripe. Surfaces only; ink text passes on all three except brown. */
  --color-mustard: oklch(82% 0.13 80);
  --color-orange:  oklch(70% 0.15 55);
  --color-brown:   oklch(36% 0.07 45);
  --color-accent:      oklch(48% 0.15 40);  /* burnt orange: buttons and links, paper text on it */
  --color-accent-deep: oklch(40% 0.13 40);

  --radius-*: initial;
  --radius-sm: 0.375rem;
  --radius-md: 0.75rem;
  --radius-lg: 1.5rem;
  --shadow-*: initial;

  --text-display: clamp(2.75rem, 1.4rem + 5vw, 6rem);
  --text-display--line-height: 0.95;
  --text-display--letter-spacing: -0.01em;
  --text-title: clamp(1.5rem, 1.2rem + 1.2vw, 2.25rem);
  --text-title--line-height: 1.1;
  --text-body: 1.0625rem;
  --text-body--line-height: 1.6;
  --text-label: 0.8125rem;
  --text-label--line-height: 1.2;
  --text-label--letter-spacing: 0.08em;
}

@layer base {
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); font-variation-settings: "opsz" 14; }
  h1, h2, h3 { font-family: var(--font-display); font-weight: 400; font-synthesis: none; text-wrap: balance; }
  a { color: var(--color-accent); text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 0.2em; }
  a:hover { color: var(--color-accent-deep); }
  :focus-visible { outline: 3px solid var(--color-ink); outline-offset: 3px; border-radius: var(--radius-sm); }
  ::selection { background: var(--color-mustard); }
  /* Hard-stop bands, printed flat. Not a gradient: every stop is doubled. */
  .stripes { height: 1.5rem; background: linear-gradient(var(--color-mustard) 0 33.3%, var(--color-orange) 0 66.6%, var(--color-brown) 0); }
}
```

```html
<section class="bg-paper-2">
  <div class="stripes" aria-hidden="true"></div>
  <div class="mx-auto grid max-w-6xl gap-10 px-6 py-16 lg:grid-cols-[1.2fr_1fr] lg:py-24">
    <div>
      <p class="text-label font-semibold uppercase">Glenmore Roller Rink · Every Saturday</p>
      <h2 class="mt-4 text-display">Skate Night, lights down at eight</h2>
      <p class="mt-6 max-w-[44ch] text-body text-ink-2">Two hours of disco, funk and the odd ballad on a maple floor laid in 1977. Skate hire is included, socks are not.</p>
      <a href="/tickets" class="mt-8 inline-block rounded-full bg-accent px-7 py-3 font-semibold text-paper no-underline hover:bg-accent-deep">Get tickets, £9</a>
    </div>
    <ol class="self-end border-y-4 border-line">
      <li class="flex items-baseline gap-4 border-b-2 border-line py-4"><span class="font-display text-title tabular-nums">8:00</span><span>Doors, warm-up laps</span></li>
      <li class="flex items-baseline gap-4 border-b-2 border-line py-4"><span class="font-display text-title tabular-nums">8:45</span><span>Couples skate</span></li>
      <li class="flex items-baseline gap-4 py-4"><span class="font-display text-title tabular-nums">9:30</span><span>Limbo, then last song at 10</span></li>
    </ol>
  </div>
</section>
```

What this theme does: Caprasimo for headings and numerals only, a grotesk body at 17px, brown ink on cream everywhere, the three-ink stripe once at the top of a section, thick ink rules (4px outer, 2px inner) instead of boxes, pill buttons in burnt orange with cream text, tight display leading (0.95) that a print layout would use.

What it never does: fake paper wear, scratches, halftone overlays, sepia or grain filters, drop shadows, smooth gradients, a stripe on every section, orange or mustard as text, more than one display face, all-caps Caprasimo, rotated "vintage" stamps, low-contrast faded inks to look old.

## Variations

- **90s web**: `--font-display` and `--font-sans` to `"Times New Roman", Times, serif` and `Verdana, Geneva, sans-serif`; paper to silver `oklch(84% 0 0)`, ink to `oklch(20% 0 0)`, links to `oklch(40% 0.22 265)` with `a:visited { color: oklch(40% 0.18 320) }` (both above 6:1). Buttons get `border: 2px outset oklch(95% 0 0)` and `active:border-style:inset`. Keep 16px body and the focus ring; no marquee, no blink, no autoplaying MIDI.
- **Dark 70s**: `paper` to `oklch(22% 0.03 45)`, `ink` to `oklch(92% 0.04 85)`, accent to `oklch(72% 0.15 55)` with `text-paper` on buttons; the stripe keeps its colours.
- **Sunburst**: one `repeating-conic-gradient(var(--color-mustard) 0 10deg, var(--color-paper-2) 0 20deg)` behind a headline in a hero, masked to a semicircle; never behind body text.
- **Rounded panels**: event cards as `rounded-lg border-4 border-line bg-mustard p-6`, ink text on mustard is 8.9:1.

## Pitfalls

- Caprasimo has one weight; asking for `font-bold` makes the browser fake a heavier one that smears. `font-synthesis: none` on `h1, h2, h3` prevents it.
- Ink on `orange` is 5.6:1, fine for labels; `text-paper` on `orange` is 2.3:1 and fails, which is why buttons use the deeper `accent`.
- The stripe has three colours with no text; mark it `aria-hidden="true"` and never encode meaning in it.
- Tight `line-height: 0.95` on the display clips descenders when a heading wraps onto a line with a link underline; give links inside headings `text-underline-offset: 0.1em` or avoid them.
- `font-variation-settings: "opsz" 14` on the body is inherited by headings set in Bricolage; reset it there or the large sizes look clumsy.
- Period colour combinations fail colour-blind readers fast (brown and green, orange and red); keep state colours out of the retro set entirely.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-color-with-restraint`
- `web-design-borders-radius-dividers`
- `web-a11y-color-contrast`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-theme-switcher`
