---
name: web-theme-luxury
description: Drop a quiet luxury look onto a site in Tailwind v4: Bodoni Moda display, Jost body at small sizes, cream paper, near-black night bands and gold used as a hairline, never as decoration, generous spacing, no radius, no shadows. Use whenever a user says "luxury", "premium", "high-end", "elegant", "boutique", "like a fashion house", "black and gold" or "expensive-looking".
---

# Luxury theme

Expensive pages are quiet. The signals are space that nobody filled, type that is small and set with care, a high-contrast serif at a size where its hairlines show, and gold that is rare enough to mean something. Cheap luxury does the opposite: gold gradients, glitter, script fonts, drop shadows under everything. The rule is that every element must survive the question "would a printer charge extra for this?"; if not, it goes.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..600;1,6..96,400..600&family=Jost:wght@300..500&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Bodoni Moda", "Didot", "Bodoni 72", Georgia, serif;
  --font-sans: "Jost", "Futura", "Century Gothic", system-ui, sans-serif;

  /* Cream paper and near-black ink, both warmed toward hue 85 so the gold belongs. */
  --color-paper:   oklch(96% 0.014 85);
  --color-paper-2: oklch(92% 0.018 85);
  --color-ink:     oklch(18% 0.006 80);
  --color-ink-2:   oklch(44% 0.012 80);
  --color-line:    oklch(84% 0.020 85);

  /* Night bands: the black half of the palette, with its own cream text. */
  --color-night:     oklch(17% 0.006 80);
  --color-night-ink: oklch(93% 0.014 85);
  --color-night-ink-2: oklch(72% 0.012 85);

  /* Gold: bright on night, deep on cream. Text-safe in both places, used sparingly in both. */
  --color-gold:      oklch(78% 0.090 85);
  --color-gold-deep: oklch(50% 0.085 80);

  --radius-*: initial;
  --radius-sm: 0;
  --shadow-*: initial;

  --text-display: clamp(2.5rem, 1.5rem + 3.6vw, 4.75rem);
  --text-display--line-height: 1.04;
  --text-display--letter-spacing: -0.01em;
  --text-title: clamp(1.625rem, 1.3rem + 1vw, 2.125rem);
  --text-title--line-height: 1.15;
  --text-body: 0.9375rem;
  --text-body--line-height: 1.8;
  --text-label: 0.75rem;
  --text-label--line-height: 1;
  --text-label--letter-spacing: 0.28em;
}

@layer base {
  html { font-synthesis: none; }
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); font-weight: 350; letter-spacing: 0.01em; }
  h1, h2, h3 { font-family: var(--font-display); font-weight: 400; font-optical-sizing: auto; text-wrap: balance; }
  em { font-family: var(--font-display); font-style: italic; }
  a { color: inherit; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 0.35em; text-decoration-color: var(--color-line); }
  a:hover { text-decoration-color: currentColor; }
  :focus-visible { outline: 1px solid currentColor; outline-offset: 4px; }
  ::selection { background: var(--color-gold); color: var(--color-night); }
  .night { background: var(--color-night); color: var(--color-night-ink); }
}
```

```html
<section class="night">
  <div class="mx-auto grid max-w-6xl gap-16 px-6 py-24 sm:py-32 lg:grid-cols-[1fr_0.9fr] lg:items-end">
    <figure>
      <img src="/img/case-no-14.jpg" alt="A tan calfskin document case on a walnut bench, brass clasp open" width="900" height="1125" class="aspect-[4/5] w-full object-cover">
      <figcaption class="mt-4 text-label uppercase text-night-ink-2">Case No. 14 · Vachetta calf</figcaption>
    </figure>
    <div class="max-w-[34ch]">
      <p class="text-label uppercase text-gold">Atelier Ostrowska · Kraków</p>
      <h2 class="mt-8 text-display">A case made <em>once</em>, for one hand</h2>
      <p class="mt-8 text-body text-night-ink-2">Each piece is cut from a single hide, saddle-stitched with waxed linen at eight stitches to the inch, and takes eleven working days.</p>
      <p class="mt-10 border-t border-gold/40 pt-6 font-display text-title tabular-nums">2 400 €</p>
      <a href="/appointments" class="mt-10 inline-block border border-night-ink px-8 py-4 text-label uppercase no-underline transition-colors hover:bg-night-ink hover:text-night motion-reduce:transition-none">Book a fitting</a>
    </div>
  </div>
</section>
```

What this theme does: one serif display at weight 400 with optical sizing, body at 15px with 1.8 leading and a short measure, wide-tracked uppercase labels as the only "decoration", sections of 6 to 8rem vertical padding, a gold hairline (`border-gold/40`) once per section, gold text only on a night band and only for one label, outlined buttons that fill on hover, photography that is large, uncropped by rounded corners and never overlaid with text.

What it never does: shadows, radius, gradients (gold or otherwise), metallic textures, script or calligraphic fonts, bold weights above 500, more than one gold element per screen, filled gold buttons, icons, star ratings, "exclusive" badges, centred blocks of body copy, text under 12px.

## Variations

- **All-night site**: swap the roles: `body` takes `night` and `night-ink`, and `paper` becomes the occasional inverted band. Keep `gold` for labels; `gold-deep` is not needed.
- **Softer serif**: replace Bodoni Moda with `"Cormorant Garamond"` at weight 500 for jewellery or hospitality; raise `--text-body` to `1rem` because Cormorant's companion sizes run small.
- **Product grid**: `grid gap-x-8 gap-y-20 sm:grid-cols-2 lg:grid-cols-3` with the name in `font-display text-xl` and the price in `text-label tracking-[0.2em]` under it, no card borders, no hover zoom.
- **Gold on cream**: when a label must sit on paper, use `text-gold-deep` (5.4:1); the bright `gold` is 1.8:1 there and is a hairline colour only.

## Pitfalls

- Bodoni's hairlines vanish below about 20px on 1x screens; the display face is for headings, prices and pull quotes. Body and buttons stay in Jost.
- `--text-body: 0.9375rem` is the floor; going to 14px to look "more refined" fails low-vision readers on long copy. Make it feel small with tracking and leading, not size.
- `font-weight: 350` needs the variable Jost range in the `<link>` (`wght@300..500`); a static file snaps it to 400 or 300.
- `outline: 1px solid currentColor` on a 1px-bordered button can read as the border itself; the 4px offset is what makes it visible as a focus ring. Do not lower it.
- `night-ink-2` on `night` is 7.7:1; dimming it further for "mood" drops captions under 4.5:1 quickly at 12px. Check with `web-a11y-color-contrast`.
- Spacious layouts break on phones when the padding is fixed; scale it (`py-24 sm:py-32`) and let images go full width below `lg`.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-color-with-restraint`
- `web-design-images`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-design-tokens-to-tailwind`
- `web-theme-switcher`
