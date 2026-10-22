---
name: web-theme-swiss
description: Drop a complete Swiss / International Typographic Style look onto a site in Tailwind v4: one grotesk, a visible 12-column grid, flush-left ragged-right type, near-white paper, near-black ink, one red accent, thick rules, no radius, no shadows. Use whenever a user says "Swiss style", "Helvetica look", "international style", "grid-based", "Bauhaus-ish", "poster-like" or "clean and typographic".
---

# Swiss theme

The Swiss style is a grid you can feel and one typeface doing all the work. Everything sits flush left on column lines, sizes jump by large steps instead of creeping, and colour is a single red used like a stamp. It looks designed because the grid is the design: the content is arranged, not decorated. The risk is sterility, so the theme keeps generous white space and lets the type get very large.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400..700&display=swap">
```

```css
@import "tailwindcss";

@theme {
  /* One family for everything. The mono is only for figures in tables. */
  --font-sans: "Instrument Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, "SF Mono", monospace;

  --color-paper:   oklch(99% 0.002 250);
  --color-paper-2: oklch(95% 0.004 250);
  --color-ink:     oklch(14% 0.005 250);
  --color-ink-2:   oklch(46% 0.008 250);
  --color-line:    oklch(14% 0.005 250);   /* rules are ink, not grey */
  --color-line-soft: oklch(86% 0.006 250); /* grid guides only */
  --color-accent:      oklch(52% 0.19 28);
  --color-accent-deep: oklch(44% 0.17 28);

  --radius-*: initial;
  --shadow-*: initial;

  --text-display: clamp(3.5rem, 1rem + 9vw, 9rem);
  --text-display--line-height: 0.92;
  --text-display--letter-spacing: -0.03em;
  --text-title: clamp(2rem, 1.2rem + 2.5vw, 3.5rem);
  --text-title--line-height: 1.0;
  --text-title--letter-spacing: -0.02em;
  --text-body: 1.0625rem;
  --text-body--line-height: 1.5;
  --text-label: 0.8125rem;
  --text-label--line-height: 1.2;
  --text-label--letter-spacing: 0.02em;

  --spacing-gutter: 1.5rem;
}

@layer base {
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); font-feature-settings: "ss01", "kern"; }
  h1, h2, h3 { font-weight: 600; text-wrap: balance; }
  a { text-decoration: none; }
  a:hover { color: var(--color-accent); }
  hr { border: 0; border-top: 2px solid var(--color-line); }
  :focus-visible { outline: 3px solid var(--color-accent); outline-offset: 2px; }
  ::selection { background: var(--color-accent); color: var(--color-paper); }
  /* The grid: 12 columns, one gutter token, no max-width tricks inside. */
  .grid-12 { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: var(--spacing-gutter); }
}
```

```html
<main class="mx-auto max-w-[88rem] px-6 lg:px-10">
  <header class="grid-12 items-start border-t-2 border-line pt-3">
    <p class="col-span-6 text-label font-medium md:col-span-3">Kunsthalle Nord</p>
    <p class="col-span-6 text-label text-ink-2 md:col-span-3">Programme, autumn 2026</p>
    <nav class="col-span-12 mt-4 flex gap-6 text-label md:col-span-6 md:mt-0 md:justify-end">
      <a href="/exhibitions" aria-current="page" class="border-b-2 border-accent pb-0.5">Exhibitions</a>
      <a href="/visit">Visit</a>
      <a href="/archive">Archive</a>
    </nav>
  </header>

  <section class="grid-12 py-20 md:py-32">
    <h1 class="col-span-12 text-display md:col-span-10">Concrete, 1958<span class="text-accent">.</span></h1>
    <p class="col-span-12 mt-10 max-w-[40ch] text-body md:col-start-7 md:col-span-6">
      Eighty-one works on paper from the Zurich group, shown together for the first time since the Helmhaus exhibition. Open until 11 January.
    </p>
    <a href="/tickets" class="col-span-12 mt-8 inline-block w-fit bg-ink px-6 py-3 text-label font-medium text-paper hover:bg-accent md:col-start-7">Buy tickets, CHF 14</a>
  </section>

  <section class="border-t-2 border-line py-12">
    <h2 class="text-title">Opening hours</h2>
    <ul class="grid-12 mt-8 text-body">
      <li class="col-span-12 flex justify-between border-t border-line-soft py-3 md:col-span-6"><span>Tuesday to Friday</span><span class="font-mono tabular-nums">10:00 – 18:00</span></li>
      <li class="col-span-12 flex justify-between border-t border-line-soft py-3 md:col-span-6"><span>Thursday</span><span class="font-mono tabular-nums">10:00 – 21:00</span></li>
      <li class="col-span-12 flex justify-between border-t border-line-soft py-3 md:col-span-6"><span>Saturday, Sunday</span><span class="font-mono tabular-nums">11:00 – 17:00</span></li>
      <li class="col-span-12 flex justify-between border-t border-line-soft py-3 md:col-span-6"><span>Monday</span><span class="text-accent">Closed</span></li>
    </ul>
  </section>
</main>
```

What this theme does: everything flush left on the 12-column grid, with the body copy starting at column 7 so the headline owns the left half; two sizes of rule (2px ink for sections, 1px soft for rows); type steps of roughly 1:2.5 between body and title and again to display; red only on the active nav item, one punctuation mark, hover, focus and one state word.

What it never does: centred text, shadows, border radius, gradients, a second colour, icons, a serif, more than one weight step between adjacent elements, justified text, `tracking-widest` uppercase labels (Swiss labels are mixed case with near-zero tracking).

## Variations

- **Inverted poster section**: `bg-ink text-paper` with the display headline and the same red; keep it to one section and never add a border, the colour change is the border.
- **Show the grid** as a design element: `.grid-12 > *` with `outline: 1px solid var(--color-line-soft)` behind a `?grid` query param during development, or permanently in a hero at 6% opacity for a drafting-table feel.
- **Dark mode**: swap `paper` and `ink`, lift `line-soft` to `oklch(30% 0.006 250)`, keep the red at `oklch(62% 0.19 28)` so white-on-red buttons still pass. Override in `.dark`, not in `@theme`.
- **Narrower Grotesk**: Instrument Sans has a `wdth` axis; `font-stretch: 90%` on display sizes gets closer to poster condensed without a second family.

## Pitfalls

- Display type at 9rem with `-0.03em` tracking collides in letter pairs like "rt" at small viewports; the clamp floor of 3.5rem exists so it never renders tight at phone width. Do not lower it.
- `--radius-*: initial` also removes `rounded-full` from avatars and radio buttons; give those an explicit `rounded-[50%]`.
- Red at 52% passes 5.2:1 with white text; the deep step is for hover only, and red is never body text longer than one word.
- Flush-left rag produces ugly widows on long paragraphs; cap paragraphs at `max-w-[40ch]` and use `text-pretty`.
- The grid breaks the moment a child gets `mx-auto` or `max-w-prose`; position with `col-start-*` and `col-span-*` only.
- Many Swiss revivals add uppercase everywhere; it halves reading speed and is not the style. Capitals are for one word on a poster, not for navigation.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-color-with-restraint`
- `web-craft-layout-with-intention`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-design-tokens-to-tailwind`
- `web-theme-switcher`
