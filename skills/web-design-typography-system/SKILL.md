---
name: web-design-typography-system
description: 'Set up a complete typography system in Tailwind v4: font stacks in `@theme`, a modular type scale with paired line-heights, measure (line length), heading vs body rules, and ready-made heading/prose classes. Use whenever a user asks about fonts, font sizes, "make the text look professional", headings, readability, line height, or "set up typography" for a site.'
---

# Typography system

Most sites look amateur because of type, not color: too many sizes, headings with body line-height, lines 120 characters long. A typography system is three decisions made once, in `@theme`, and then only referenced: which fonts, which sizes (a scale with a ratio), and how long a line may be. Tailwind v4 lets you encode each as a token so every `text-*` and `font-*` utility you use afterwards is already correct.

## Pattern

```css
/* src/input.css */
@import "tailwindcss";

@theme {
  /* 1. Fonts: a display face for headings, a text face for body, mono for code.
     System fallbacks are listed so text renders before web fonts arrive. */
  --font-display: "Inter Variable", "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-body: "Inter Variable", "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;

  /* 2. Type scale: ratio 1.25 (major third) from a 1rem base, rounded to clean rems.
     Each size carries its own line-height so `text-lg` is always well-leaded. */
  --text-xs: 0.75rem;    --text-xs--line-height: 1rem;
  --text-sm: 0.875rem;   --text-sm--line-height: 1.25rem;
  --text-base: 1rem;     --text-base--line-height: 1.6;      /* unitless = scales with size */
  --text-lg: 1.125rem;   --text-lg--line-height: 1.6;
  --text-xl: 1.25rem;    --text-xl--line-height: 1.4;
  --text-2xl: 1.5rem;    --text-2xl--line-height: 1.3;   --text-2xl--letter-spacing: -0.01em;
  --text-3xl: 1.875rem;  --text-3xl--line-height: 1.2;   --text-3xl--letter-spacing: -0.015em;
  --text-4xl: 2.5rem;    --text-4xl--line-height: 1.1;   --text-4xl--letter-spacing: -0.02em;
  --text-5xl: 3.25rem;   --text-5xl--line-height: 1.05;  --text-5xl--letter-spacing: -0.025em;

  /* 3. Measure: the max line length for running text. 65ch is the sweet spot (45 to 75). */
  --container-prose: 65ch;
}

/* Base: body gets the text face; headings get the display face and balanced wrapping. */
@layer base {
  html { font-family: var(--font-body); -webkit-font-smoothing: antialiased; }
  h1, h2, h3, h4 { font-family: var(--font-display); text-wrap: balance; }
  p, li { text-wrap: pretty; } /* avoids single-word last lines */
}
```

```html
<article class="mx-auto max-w-prose px-4 py-12">
  <p class="text-sm font-medium uppercase tracking-wide text-indigo-600">Guide</p>
  <h1 class="mt-2 text-4xl font-bold text-gray-900 sm:text-5xl dark:text-gray-50">
    A type scale you set once and never fight again
  </h1>
  <p class="mt-4 text-lg text-gray-600 dark:text-gray-300">
    One ratio, nine sizes, a line-height for each. Everything else is a class name.
  </p>
  <h2 class="mt-12 text-2xl font-semibold text-gray-900 dark:text-gray-50">Why a ratio</h2>
  <p class="mt-4 text-base text-gray-700 dark:text-gray-300">
    Sizes picked by eye drift. A ratio makes every jump feel intentional and lets you drop a step
    on mobile (<code class="rounded bg-gray-100 px-1 font-mono text-sm dark:bg-gray-800">sm:text-5xl</code>)
    without the hierarchy collapsing.
  </p>
  <ul class="mt-4 list-disc space-y-1 pl-6 text-base text-gray-700 dark:text-gray-300">
    <li>Body: 16px minimum, line-height 1.5 to 1.7.</li>
    <li>Headings: tighter leading (1.1 to 1.3) and slightly negative tracking above 24px.</li>
    <li>Small text: 14px for metadata only, never for paragraphs.</li>
  </ul>
</article>
```

The `--text-*--line-height` and `--text-*--letter-spacing` sub-tokens are a Tailwind v4 feature: `text-2xl` now emits font-size, line-height and letter-spacing together, so you stop writing `leading-tight tracking-tight` on every heading.

## Variations

- **Ratio by mood.** 1.2 (minor third) for dense dashboards and docs; 1.25 for marketing sites; 1.333 (perfect fourth) for editorial pages with big display headings. Regenerate the rems; keep the same token names.
- **Fluid headings.** Replace the top sizes with `clamp()` so they scale between breakpoints: `--text-4xl: clamp(2rem, 1.5rem + 2.5vw, 3rem);`. See `web-css-fluid-typography`.
- **Serif editorial.** `--font-display: "Fraunces", Georgia, serif;` with `--text-base--line-height: 1.7` and `font-medium` instead of `font-bold` on headings; serifs look heavy at 700.
- **Long-form prose without a plugin.** Put `[&_p]:mt-4 [&_h2]:mt-10 [&_h2]:text-2xl [&_h2]:font-semibold` on the article wrapper, or define a `.prose-basic` class in `@layer components` with the same rules.

## Pitfalls

- Loading a web font without a fallback stack causes invisible text; always list `system-ui, sans-serif` after the custom face and set `font-display: swap` in the `@font-face` (see `web-perf-fonts`).
- `leading-*` utilities override the per-size line-height. If a heading looks loose, check for a stray `leading-relaxed` inherited from a parent, not the token.
- Text under 14px fails readability for most users and often fails WCAG contrast at light weights; keep `text-xs` for badges and captions only.
- `text-wrap: balance` is for short headings (up to ~6 lines); applying it to paragraphs costs layout time and does nothing useful.
- Using `max-w-prose` on a flex child that also has `w-full` has no effect if the parent is narrower; the measure only limits, it never widens.
- Do not skip heading levels for visual size. Use `<h2 class="text-lg">` when the structure needs an h2 but the design wants it small; size and level are independent.

## Related skills

- `web-css-fluid-typography`
- `web-perf-fonts`
- `web-design-tokens-to-tailwind`
- `web-design-color-system`
- `web-seo-content-structure`
