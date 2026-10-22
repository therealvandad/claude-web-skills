---
name: web-craft-color-with-restraint
description: 'Build a restrained palette in Tailwind v4: oklch neutrals tinted toward one accent instead of gray, a single accent used only where the user acts, a second hue only for state, tinted surfaces instead of gray-50. Use whenever a user says "too much purple", "too many colours", "rainbow gradient", "looks AI generated", or wants colours that look premium or designed.'
---

# Colour with restraint

Pure `gray-*` neutrals plus `indigo-600` is what a page looks like when no colour decision was made: it is Tailwind's own example palette, so every reader has seen it a thousand times. Add a purple-to-blue gradient and a pink glow and the page announces itself as generated. Restraint reads as designed because it is evidence of a decision: one hue was chosen, the neutrals were tinted toward it so the page feels like one material, and the accent appears only where the user should act. Everything else is ink on paper.

## Pattern

```css
@import "tailwindcss";

@theme {
  /* One hue for the whole site. 55 is terracotta; see Variations for others. */
  --hue: 55;

  /* Paper and ink: neutrals that share the accent hue at tiny chroma, so greys are warm, not dead. */
  --color-paper:     oklch(98% 0.006 var(--hue));   /* page background, replaces white */
  --color-paper-2:   oklch(95% 0.010 var(--hue));   /* section band, replaces gray-50 */
  --color-paper-3:   oklch(91% 0.014 var(--hue));   /* input background, table stripe */
  --color-ink:       oklch(22% 0.015 var(--hue));   /* headings and body, replaces gray-900 */
  --color-ink-2:     oklch(45% 0.015 var(--hue));   /* secondary text, replaces gray-500 */
  --color-line:      oklch(85% 0.012 var(--hue));   /* borders, replaces gray-200 */

  /* One accent, two steps. Used on the primary action, focus ring and active state only. */
  --color-accent:      oklch(55% 0.16 var(--hue));
  --color-accent-deep: oklch(45% 0.15 var(--hue));
  --color-accent-tint: oklch(94% 0.04 var(--hue));  /* highlight surface: selected row, callout */

  /* A second hue exists only for state, never for decoration. */
  --color-ok:   oklch(55% 0.14 150);
  --color-warn: oklch(70% 0.15 80);
  --color-bad:  oklch(55% 0.19 25);
}

@layer base {
  body { background: var(--color-paper); color: var(--color-ink); }
  ::selection { background: var(--color-accent-tint); }
}
```

```html
<header class="border-b border-line">
  <nav class="mx-auto flex max-w-6xl items-center gap-8 px-6 py-4 text-sm">
    <a href="/" class="font-medium">Ember Roasters</a>
    <a href="/beans" aria-current="page" class="text-ink underline decoration-accent decoration-2 underline-offset-[6px]">Beans</a>
    <a href="/brewing" class="text-ink-2 hover:text-ink">Brewing</a>
    <a href="/subscribe" class="ml-auto rounded-md bg-accent px-4 py-2 font-medium text-paper hover:bg-accent-deep focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">Start a subscription</a>
  </nav>
</header>

<section class="bg-paper-2">
  <div class="mx-auto grid max-w-6xl gap-10 px-6 py-20 lg:grid-cols-[1fr_1fr]">
    <article class="border border-line bg-paper p-8">
      <h2 class="text-2xl font-medium">Monthly, 500 g</h2>
      <p class="mt-1 text-ink-2">Two bags, roasted the Monday before they ship.</p>
      <p class="mt-6 text-4xl font-medium tabular-nums">24 €<span class="text-base text-ink-2"> / month</span></p>
      <p class="mt-4 inline-flex items-center gap-2 text-sm text-ok"><span class="size-1.5 rounded-full bg-ok" aria-hidden="true"></span> Next roast: 3 November</p>
    </article>
    <article class="border border-line bg-accent-tint p-8">
      <p class="font-mono text-xs uppercase tracking-widest text-accent-deep">Most chosen</p>
      <h2 class="mt-2 text-2xl font-medium">Fortnightly, 250 g</h2>
      <p class="mt-1 text-ink-2">One bag every two weeks. Always fresh, never stale on the shelf.</p>
      <p class="mt-6 text-4xl font-medium tabular-nums">14 €<span class="text-base text-ink-2"> / fortnight</span></p>
    </article>
  </div>
</section>
```

Where the accent is allowed: the primary button, the focus ring, the active nav underline, one highlighted surface (`bg-accent-tint`), link underlines in body text. Where it is not: headings, icons in squares, section backgrounds, gradients, the second button. If the accent appears more than three times on one screen, something has been decorated instead of designed.

Deriving the palette from a logo or photo:

1. Open the image in browser devtools, pick the dominant colour, switch the picker to OKLCH and read the hue (the third number).
2. Set `--hue` to it. Accent chroma `0.12` to `0.18` at `55%` lightness; neutrals share the hue at chroma `0.004` to `0.015`.
3. Only if you need a second hue, take `--hue + 180` for `--color-bad` or a chart series. Never for a second button.

## Variations

- **Cool instead of warm**: `--hue: 250` (slate-blue) or `230` (steel). Same chroma values; the neutrals become a `zinc` that is alive instead of dead. For a green-tinted paper (print, outdoors) use `--hue: 140` with neutral chroma `0.008`.
- **Dark mode**: swap paper and ink and raise chroma slightly so the tint survives: `--color-paper: oklch(16% 0.012 var(--hue))`, `--color-ink: oklch(94% 0.008 var(--hue))`, accent to `oklch(70% 0.14 var(--hue))` so it still passes on the dark paper. Re-point the variables in `.dark` or a media query, not in `@theme`.
- **Loud brand colour (neon, hot pink)**: keep it as the accent but shrink its area: a 2 px underline, a dot, the button. Loud colours at small sizes read as confident; at section size they read as a template.
- **A gradient that earns it**: same hue, two lightness steps, as a surface only: `bg-linear-to-b from-paper to-paper-2`. Never two hues, never on text.
- **Kill the defaults**: start `@theme` with `--color-*: initial;` so `bg-indigo-600` and `text-gray-500` stop existing and nobody reaches for them.

## Pitfalls

- `indigo-600` reads as "Tailwind default" even on an otherwise good page; the same is true of `blue-600` buttons on `gray-50` bands. Any hue at the same chroma looks more considered.
- Tinted paper plus accent text fails contrast sooner than white plus black. Check `ink-2` on `paper-2` (needs 4.5:1) and `text-paper` on `bg-accent` (the 55% accent passes; a 65% one will not).
- Neutral chroma above about `0.02` turns the page yellow or lilac instead of warm or cool. Stay under `0.015` for text and borders.
- OKLCH chroma over `0.2` at mid lightness clips on sRGB screens, so two steps render the same. Keep accents at `0.19` or below.
- Status colours are also a tell when used decoratively: a green check icon on every feature card is the ⚡ emoji of colour. Use `ok`/`warn`/`bad` for actual state only.
- `text-transparent bg-clip-text` on a heading is both a palette tell and a contrast failure at the light stop; headings are `text-ink`.

## Related skills

- `web-design-color-system`
- `web-a11y-color-contrast`
- `web-design-dark-mode`
- `web-css-variables-theming`
- `web-craft-anti-generic-design`
- `web-craft-finishing-details`
- `web-design-shadows-and-elevation`
