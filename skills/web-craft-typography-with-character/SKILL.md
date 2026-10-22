---
name: web-craft-typography-with-character
description: Pair fonts beyond the default Inter/system sans: named pairings (Fraunces/IBM Plex, Instrument Serif/Geist, Space Grotesk/JetBrains Mono), display headings with optical sizing and deliberate weight, when a serif or mono earns its place, as Tailwind v4 @theme tokens. Use whenever a user says the type "looks generic", "looks like every AI site", "boring font", or wants headings with character.
---

# Typography with character

Inter at `font-bold tracking-tight` on every heading is the typographic equivalent of a stock photo: fine, and instantly forgettable, because it is what every generated page ships with. Type is the cheapest place to give a site a voice. One display face chosen for the subject (a serif for words, a grotesk for tools, a mono for data), one quiet text face, and a few deliberate settings (weight below bold, optical size, real italics) separate a page that was designed from one that was defaulted.

## Pattern

```html
<!-- In <head>: two families, only the axes and weights you use. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Fraunces", "Iowan Old Style", Georgia, serif;
  --font-sans: "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", monospace;

  /* Display sizes carry their own leading and tracking so headings never inherit body defaults. */
  --text-display: clamp(2.75rem, 1.8rem + 3.5vw, 5rem);
  --text-display--line-height: 1.02;
  --text-display--letter-spacing: -0.01em;
  --text-title: clamp(1.75rem, 1.3rem + 1.5vw, 2.5rem);
  --text-title--line-height: 1.15;
  --text-title--letter-spacing: 0;
}

@layer base {
  html { font-synthesis: none; }                 /* never fake a bold or italic that was not loaded */
  h1, h2, h3 { font-family: var(--font-display); font-weight: 450; font-optical-sizing: auto; text-wrap: balance; }
  body { font-feature-settings: "kern", "liga"; }
}
```

```html
<article class="mx-auto max-w-2xl px-6 py-16 text-stone-800">
  <p class="font-mono text-xs uppercase tracking-[0.18em] text-stone-500">Field notes · No. 14</p>

  <h1 class="mt-4 text-display text-stone-950 [font-variation-settings:'opsz'_144]">
    The kettle that <em class="font-light italic text-stone-600">almost</em> boiled
  </h1>

  <p class="mt-6 text-lg leading-8">
    Variable optical size is the point of Fraunces: at 144 the serifs sharpen and the contrast rises,
    so a headline looks engraved while the same family at 9 stays sturdy in a caption.
  </p>

  <h2 class="mt-12 text-title">What changed in the second batch</h2>
  <p class="mt-3 leading-7">Body text stays in Plex Sans at 400. Headings get the display face; nothing else does.</p>

  <p class="mt-8 font-mono text-sm tabular-nums text-stone-500">Read in 6 min · 1,240 words · 14 Oct 2026</p>
</article>
```

Why these choices:

- `font-weight: 450` on a variable display face reads as "set", not "shouted". Bold display type at 60px is a template reflex; drop to 400 to 500 and let size do the work.
- Negative tracking belongs to geometric sans at large sizes (`-0.02em`). A serif wants `0` or slightly positive; tracking a serif tight is a visible tell.
- The mono eyebrow with `tracking-[0.18em]` replaces the generic `text-indigo-600 uppercase` label and adds a second voice at no cost.
- `tabular-nums` on any line with numbers (dates, prices, stats) stops them jittering and signals attention to detail.

Pairings that work, all free (Google Fonts unless noted):

- **Fraunces + IBM Plex Sans + IBM Plex Mono**: warm editorial, slightly odd. Essays, food, craft, small studios.
- **Instrument Serif (400 and italic only) + Geist (Vercel, open licence)**: quiet and sharp. SaaS that wants to look like a publication. Headings must stay `font-normal`; there is no bold.
- **Space Grotesk headings + JetBrains Mono labels and code + Inter body**: developer tools, hardware, anything technical.
- **Inter Tight headings at `font-medium tracking-[-0.02em]` + Newsreader body with `opsz`**: documentation and long reads; Inter Tight is Inter with the generic knocked out of it.
- **One superfamily, three voices**: IBM Plex Sans / Serif / Mono share metrics, so mixing them never looks mismatched.

## Variations

- **Tech product, no serif**: `--font-display: "Space Grotesk"`, headings `font-medium tracking-[-0.02em]`, everything numeric in `font-mono tabular-nums`. Contrast comes from mono vs grotesk, not from weight.
- **Self-hosted fonts**: download the variable woff2, `@font-face { font-family: "Fraunces"; src: url(/fonts/fraunces.woff2) format("woff2"); font-weight: 300 600; font-display: swap; }` and preload the display face only. See `web-perf-fonts`.
- **Dark mode**: light text on dark looks thinner. Bump body to `dark:font-[450]` on a variable face, or add `dark:[-webkit-font-smoothing:antialiased]`; do not switch to bold.
- **Pull quote or big number**: one element per page at `text-display` in the display face, `font-light italic` for a quote, `tabular-nums` for a number. One, not one per section.

## Pitfalls

- Loading seven weights of Inter "just in case" costs 400 KB and still looks default. Two families, at most four files.
- Instrument Serif has no bold: `font-bold` on it makes the browser smear a fake one. `font-synthesis: none` turns that into an obvious regular, which is the correct failure.
- Tailwind's `text-5xl` keeps `line-height: 1`, but `text-4xl` and below carry 1.1 to 1.5; a heading that wraps at `text-4xl` with body leading looks like a paragraph. Define display sizes with their own `--line-height` as above.
- Serif body text at 14 px on a 1x screen turns to mud. Keep serifs for 18 px+ or headings; body under 16 px should be a sans.
- `text-balance` is ignored above roughly six lines of text; it is for headings, not paragraphs. Use `text-pretty` on body copy.
- Google Fonts CSS without `display=swap` blocks text rendering for up to 3 s on slow connections; the preconnect lines matter as much as the stylesheet link.

## Related skills

- `web-design-typography-system`
- `web-css-fluid-typography`
- `web-perf-fonts`
- `web-craft-anti-generic-design`
- `web-craft-finishing-details`
- `web-craft-copy-that-sounds-human`
