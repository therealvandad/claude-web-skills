---
name: web-theme-nature-organic
description: Drop a warm, organic look onto a site in Tailwind v4: Fraunces with its soft axis, Source Sans 3 body, oat paper, forest ink, a moss accent, clay and moss tint surfaces, a faint paper grain, arched and rounded photography, no shadows. Use whenever a user says "natural", "organic", "earthy", "eco", "sustainable", "garden", "farm", "wellness", "botanical" or "warm and calm".
---

# Nature organic theme

Organic does not mean green everywhere. Real natural materials are mostly warm neutrals (oat, sand, bark) with green appearing as a living accent, so the page reads calm rather than "eco brand". The texture comes from three places: a serif whose soft axis rounds its terminals, a faint grain on the paper, and photography framed in arches and large radii instead of rectangles. Keep the shapes soft and the colours earthy, and leave the leaf icons out.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..600,0..100;1,9..144,300..600,0..100&family=Source+Sans+3:wght@400;600&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Fraunces", "Iowan Old Style", Georgia, serif;
  --font-sans: "Source Sans 3", "Segoe UI", system-ui, sans-serif;

  /* Oat and sand paper (hue 80 to 85), ink pulled toward forest green (hue 150). */
  --color-paper:   oklch(96% 0.018 85);
  --color-paper-2: oklch(91.5% 0.028 80);
  --color-ink:     oklch(25% 0.030 150);
  --color-ink-2:   oklch(45% 0.030 140);
  --color-line:    oklch(84% 0.030 85);

  /* Moss is the one accent. Clay and moss tints are surfaces only. */
  --color-accent:      oklch(46% 0.09 145);
  --color-accent-deep: oklch(38% 0.08 145);
  --color-moss-tint:   oklch(91% 0.035 140);
  --color-clay-tint:   oklch(89% 0.040 55);
  --color-clay:        oklch(50% 0.110 45);   /* small text on paper only: seasonal tags */

  --radius-sm: 0.5rem;
  --radius-md: 0.875rem;
  --radius-lg: 1.5rem;
  --radius-xl: 2.5rem;
  --shadow-*: initial;

  --text-display: clamp(2.5rem, 1.5rem + 3.4vw, 4.5rem);
  --text-display--line-height: 1.05;
  --text-display--letter-spacing: -0.015em;
  --text-title: clamp(1.5rem, 1.25rem + 0.9vw, 2rem);
  --text-title--line-height: 1.2;
  --text-body: 1.0625rem;
  --text-body--line-height: 1.65;
  --text-label: 0.8125rem;
  --text-label--line-height: 1.2;
  --text-label--letter-spacing: 0.04em;
}

@layer base {
  :root {
    --grain: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.05'/%3E%3C/svg%3E");
  }
  body { background: var(--grain), var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); }
  h1, h2, h3 { font-family: var(--font-display); font-weight: 400; font-variation-settings: "SOFT" 100; font-optical-sizing: auto; text-wrap: balance; }
  em { font-family: var(--font-display); font-style: italic; font-variation-settings: "SOFT" 100; }
  a { color: var(--color-accent); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 0.2em; }
  a:hover { color: var(--color-accent-deep); }
  :focus-visible { outline: 2px solid var(--color-accent); outline-offset: 3px; border-radius: var(--radius-sm); }
  ::selection { background: var(--color-moss-tint); }
  img { border-radius: var(--radius-lg); }
}
```

```html
<section class="mx-auto grid max-w-6xl gap-12 px-6 py-20 md:grid-cols-[0.8fr_1fr] md:items-center lg:gap-20">
  <img src="/img/hornbeam-hedge.jpg" alt="A young hornbeam hedge in October, leaves turning copper" width="720" height="900" class="aspect-[4/5] w-full rounded-t-full object-cover">
  <div>
    <p class="text-label font-semibold uppercase text-clay">Plant before the ground freezes</p>
    <h2 class="mt-4 text-display">Autumn is for <em>roots</em></h2>
    <p class="mt-6 max-w-[48ch] text-body text-ink-2">Bare-root hedging goes out from the first of November. Planted now, it spends winter growing roots and leafs out in April without needing a hose.</p>
    <ul class="mt-10 divide-y divide-line rounded-lg bg-paper-2 px-6">
      <li class="flex items-baseline gap-4 py-4"><span class="font-display text-xl">Hornbeam</span><span class="text-ink-2">60–80 cm, bundle of 25</span><span class="ml-auto tabular-nums">£42</span></li>
      <li class="flex items-baseline gap-4 py-4"><span class="font-display text-xl">Field maple</span><span class="text-ink-2">40–60 cm, bundle of 25</span><span class="ml-auto tabular-nums">£36</span></li>
      <li class="flex items-baseline gap-4 py-4"><span class="font-display text-xl">Hawthorn</span><span class="text-ink-2">60–80 cm, bundle of 50</span><span class="ml-auto tabular-nums">£48</span></li>
    </ul>
    <a href="/bare-root" class="mt-8 inline-block rounded-full bg-accent px-6 py-3 font-semibold text-paper no-underline hover:bg-accent-deep">Reserve for November</a>
    <p class="mt-4 text-sm text-ink-2">Hollow Oak Nursery, Lower Slaughter. Collection or delivery within 40 miles.</p>
  </div>
</section>
```

What this theme does: Fraunces at weight 400 with `SOFT` 100 for headings and italics, a sans body at 17px, warm paper with a 5% grain, moss only on buttons, links and focus, clay only for one small seasonal label, sand (`paper-2`) and the two tints as the only surfaces, an arched (`rounded-t-full`) or `rounded-xl` frame on hero photos and `rounded-lg` everywhere else, pill buttons.

What it never does: leaf, sprout or globe icons, saturated "eco green" (chroma above 0.12), green text for body copy, shadows or glows, gradients, blob shapes behind images, hand-drawn script fonts, stock photos of hands holding soil, more than one arch per screen, grain over 6% opacity.

## Variations

- **Clay-led**: swap the roles for a ceramics or bakery site: accent becomes `oklch(50% 0.11 45)`, moss drops to a tint, ink moves to bark `oklch(26% 0.03 50)`.
- **Dark forest**: `paper` to `oklch(21% 0.02 150)`, `paper-2` to `oklch(26% 0.025 150)`, `ink` to `oklch(93% 0.02 85)`, accent to `oklch(76% 0.10 140)` with `text-paper` on buttons; lower the grain opacity to `.03` because noise reads louder on dark.
- **Section bands**: alternate `bg-moss-tint` and `bg-clay-tint` full-width bands with `rounded-xl mx-3` on desktop so each band reads as a cut piece of paper, not a stripe.
- **No grain**: on pages with heavy photography, set `body { background: var(--color-paper) }` for that template; the photos already carry the texture.

## Pitfalls

- The `SOFT` axis only works if it is in the font URL (`SOFT@...0..100`); without it, `font-variation-settings` silently does nothing and Fraunces looks sharp.
- `img { border-radius }` in base also rounds logos and icons; add `rounded-none` on those, or scope the rule to `main img`.
- `rounded-t-full` on a landscape image gives a shallow dome, not an arch; arches need a portrait ratio like `aspect-[4/5]` or `aspect-[3/4]`.
- The grain is a data URI repeated across the page; it costs nothing to load, but a `background-attachment: fixed` version repaints on scroll and janks on phones. Leave it scrolling.
- `ink-2` on `clay-tint` is 5.2:1 and the margin is thin; do not lighten `ink-2` for softness. Check with `web-a11y-color-contrast`.
- Green and clay together are a red-green pair for colour-blind readers; never use them alone to signal in stock versus sold out.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-color-with-restraint`
- `web-craft-finishing-details`
- `web-design-images`
- `web-css-aspect-ratio-media`
- `web-css-variables-theming`
- `web-theme-switcher`
