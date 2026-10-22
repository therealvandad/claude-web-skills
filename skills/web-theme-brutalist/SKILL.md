---
name: web-theme-brutalist
description: 'Apply a deliberate brutalist look in Tailwind v4: heavy Archivo headings, IBM Plex Mono body, thick ink borders, hard offset shadows, zero radius, yellowed paper and one safety-orange surface, with passing contrast. Use whenever a user says "brutalist", "raw", "neo-brutalism", "anti-design", "ugly on purpose" or "punk zine".'
---

# Brutalist theme

Brutalism on the web is honesty about materials: borders are borders, text is text, nothing pretends to float. The look fails when it is actually careless (unreadable text, random sizes, Comic Sans irony). It works when every rough element is placed with care: thick rules on a strict grid, a mono body with real leading, one loud colour used as a surface with dark text on it, and hard shadows that are the same offset everywhere. The ugliness is a style; the alignment is not negotiable.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500..900&family=IBM+Plex+Mono:wght@400;500;700&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Archivo", "Arial Black", Impact, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "Courier New", monospace;
  --font-sans: var(--font-mono);           /* body is mono; there is no quiet face here */

  --color-paper:   oklch(96% 0.025 95);    /* yellowed newsprint, not white */
  --color-paper-2: oklch(90% 0.03 95);
  --color-ink:     oklch(12% 0.01 60);     /* never #000: it fights the paper */
  --color-ink-2:   oklch(40% 0.015 60);
  --color-line:    var(--color-ink);       /* borders are ink */
  --color-accent:  oklch(68% 0.19 45);     /* safety orange: a surface, never text */
  --color-accent-deep: oklch(58% 0.18 45);

  --radius-*: initial;
  --shadow-*: initial;
  --shadow-hard:    4px 4px 0 0 var(--color-ink);   /* the only shadow: solid, no blur */
  --shadow-hard-lg: 8px 8px 0 0 var(--color-ink);

  --text-display: clamp(3rem, 1rem + 8vw, 8rem);
  --text-display--line-height: 0.9;
  --text-display--letter-spacing: -0.04em;
  --text-title: clamp(1.75rem, 1.2rem + 2vw, 3rem);
  --text-title--line-height: 1.0;
  --text-body: 1rem;
  --text-body--line-height: 1.65;
  --text-label: 0.75rem;
  --text-label--line-height: 1;
  --text-label--letter-spacing: 0.08em;
}

@layer base {
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-mono); }
  h1, h2, h3 { font-family: var(--font-display); font-weight: 800; text-transform: uppercase; text-wrap: balance; }
  a { text-decoration: underline; text-decoration-thickness: 3px; text-underline-offset: 3px; }
  a:hover { background: var(--color-ink); color: var(--color-paper); text-decoration: none; }
  hr { border: 0; border-top: 3px solid var(--color-ink); }
  :focus-visible { outline: 3px dashed var(--color-ink); outline-offset: 3px; }
  ::selection { background: var(--color-accent); color: var(--color-ink); }
  button, [type="submit"] { font-family: var(--font-mono); font-weight: 700; }
}
```

```html
<main class="mx-auto max-w-6xl border-x-[3px] border-ink">
  <header class="flex flex-wrap items-center justify-between gap-4 border-b-[3px] border-ink px-5 py-3 text-label uppercase">
    <a href="/" class="font-display text-xl font-black no-underline">Ferro Club</a>
    <nav class="flex gap-5">
      <a href="/rides" aria-current="page" class="bg-ink px-2 py-1 text-paper no-underline">Rides</a>
      <a href="/kit" class="no-underline hover:underline">Kit</a>
      <a href="/join" class="no-underline hover:underline">Join</a>
    </nav>
  </header>

  <section class="grid md:grid-cols-[2fr_1fr]">
    <div class="border-b-[3px] border-ink p-6 md:border-b-0 md:border-r-[3px] md:p-10">
      <p class="text-label uppercase text-ink-2">Sunday, 06:30, every week, rain included</p>
      <h1 class="mt-4 text-display">Fixed gear.<br>No excuses.</h1>
      <p class="mt-8 max-w-[52ch] text-body">Sixty kilometres, two climbs, one café that opens early for us. Bring lights. Nobody is dropped on the way out; everybody is dropped on the way back.</p>
      <a href="/join" class="mt-8 inline-block border-[3px] border-ink bg-accent px-5 py-3 font-bold text-ink no-underline shadow-hard hover:translate-x-0.5 hover:translate-y-0.5 hover:bg-accent-deep hover:shadow-none motion-reduce:transition-none">Join the list, free</a>
    </div>
    <ul class="divide-y-[3px] divide-ink bg-paper-2 text-body">
      <li class="p-5"><span class="block text-label uppercase text-ink-2">Next ride</span><span class="font-bold tabular-nums">26 Oct, 06:30</span></li>
      <li class="p-5"><span class="block text-label uppercase text-ink-2">Route</span><span class="font-bold">Col de la Faucille, 61 km</span></li>
      <li class="p-5"><span class="block text-label uppercase text-ink-2">Riders last week</span><span class="font-bold tabular-nums">23</span></li>
    </ul>
  </section>

  <section class="border-t-[3px] border-ink p-6 md:p-10">
    <h2 class="text-title">Rules</h2>
    <ol class="mt-6 grid gap-5 sm:grid-cols-3">
      <li class="border-[3px] border-ink bg-paper p-5 shadow-hard"><span class="font-display text-4xl font-black">1</span><p class="mt-3 text-body">Lights front and back. Checked at the start.</p></li>
      <li class="border-[3px] border-ink bg-paper p-5 shadow-hard"><span class="font-display text-4xl font-black">2</span><p class="mt-3 text-body">Call the holes. Point, then shout.</p></li>
      <li class="border-[3px] border-ink bg-paper p-5 shadow-hard"><span class="font-display text-4xl font-black">3</span><p class="mt-3 text-body">Café is cash. The owner is 81.</p></li>
    </ol>
  </section>
</main>
```

What this theme does: one border weight (3px) everywhere, one shadow offset (4px) that collapses on press so the button physically moves, uppercase display headings at weight 800 with negative tracking, mono body at a readable 16px/1.65, orange only as a surface with ink text on it, hover that inverts to ink-on-paper, dashed focus ring that cannot be confused with a border.

What it never does: blur shadows, border radius, gradients, grey borders, orange or any colour as text, pure `#000` on pure `#fff`, mixed border weights, centred layouts, Comic Sans or "ironic" fonts, marquee or blink, text under 14px, animated glitch effects.

## Variations

- **Monochrome strict**: drop `accent` entirely; the primary button becomes `bg-ink text-paper` and hover inverts. Harder, closer to print brutalism.
- **Sticker variant**: one element per page gets `rotate-[-2deg]` with `shadow-hard-lg`; more than one and it becomes a scrapbook.
- **Dark mode**: `paper` to `oklch(16% 0.01 60)`, `ink` to `oklch(94% 0.02 95)`; shadows stay ink-coloured so they become light offsets on dark, which is correct. Override in `.dark`.
- **Softer type**: swap Archivo for `"Bricolage Grotesque"` at weight 700 with `text-transform: none`; the borders and shadows carry the style, the headings can stop shouting.

## Pitfalls

- Orange at 68% is 2.6:1 against the paper, so it is a surface only; the moment someone writes `text-accent` the page fails WCAG. Ink on orange is 7:1.
- Mono body copy needs the extra leading (1.65) and a shorter measure (52ch); at 1.5 and 70ch it reads like a stack trace.
- `border-x-[3px]` on the main container plus `border-[3px]` on children doubles to 6px at the edges; use `divide-*` for siblings and put the outer border on one element only.
- The press animation on the button must be a transform, not a margin change, or the layout shifts; `motion-reduce:transition-none` keeps the move but removes the easing.
- Uppercase headings in a display face need `text-wrap: balance` or they produce a one-word last line that looks like an error.
- Dashed focus outlines render poorly over the hard shadow; `outline-offset: 3px` clears it. Do not remove the outline to tidy it up.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-color-with-restraint`
- `web-design-borders-radius-dividers`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-design-tokens-to-tailwind`
- `web-theme-switcher`
