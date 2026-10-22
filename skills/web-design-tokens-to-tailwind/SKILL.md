---
name: web-design-tokens-to-tailwind
description: 'Convert a design spec or Figma token export (colors, fonts, spacing, radii, shadows) into a Tailwind v4 `@theme` block: the namespace rules that turn each token into a utility, plus a script that transforms tokens.json into CSS. Use whenever a user hands over a style guide, Figma variables, a tokens file, or says "match our design system in Tailwind".'
---

# Design tokens to Tailwind v4

Tailwind v4 has no config file: the theme *is* a set of CSS variables in `@theme`, and the variable's namespace decides which utilities it generates. `--color-brand-500` becomes `bg-brand-500`, `text-brand-500`, `border-brand-500`; `--spacing-gutter` becomes `p-gutter`, `gap-gutter`; `--breakpoint-wide` becomes the `wide:` variant. So converting a design spec is mostly a renaming exercise: map each token into the right namespace, keep the designer's names where they are stable, and decide what to do with Tailwind's defaults (keep, extend, or replace).

## Pattern

Given a typical token export:

```json
{
  "color": { "brand": { "500": "#4F46E5", "600": "#4338CA" }, "neutral": { "900": "#111827" } },
  "font":  { "family": { "sans": "Inter", "display": "Satoshi" }, "size": { "body": "16px", "h1": "48px" } },
  "space": { "1": "4px", "2": "8px", "gutter": "24px" },
  "radius": { "control": "6px", "card": "12px" },
  "shadow": { "card": "0 1px 3px rgba(0,0,0,.1), 0 1px 2px rgba(0,0,0,.06)" },
  "breakpoint": { "tablet": "768px", "desktop": "1200px" }
}
```

The equivalent `@theme`, with each namespace mapped:

```css
@import "tailwindcss";

@theme {
  /* --color-*  →  bg-, text-, border-, ring-, fill-, stroke-, shadow- color utilities */
  --color-brand-500: #4f46e5;
  --color-brand-600: #4338ca;
  --color-neutral-900: #111827;

  /* --font-*  →  font-sans, font-display */
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-display: "Satoshi", "Inter", ui-sans-serif, sans-serif;

  /* --text-*  →  text-body, text-h1 (with optional --line-height / --letter-spacing / --font-weight) */
  --text-body: 1rem;    --text-body--line-height: 1.6;
  --text-h1: 3rem;      --text-h1--line-height: 1.1;  --text-h1--letter-spacing: -0.02em;  --text-h1--font-weight: 700;

  /* --spacing-*  →  p-, m-, gap-, w-, h-, inset- (named values; numeric scale is still 0.25rem * n) */
  --spacing-gutter: 1.5rem;

  /* --radius-*  →  rounded-control, rounded-card */
  --radius-control: 0.375rem;
  --radius-card: 0.75rem;

  /* --shadow-*  →  shadow-card */
  --shadow-card: 0 1px 3px rgb(0 0 0 / 0.10), 0 1px 2px rgb(0 0 0 / 0.06);

  /* --breakpoint-*  →  tablet:, desktop: variants (min-width) */
  --breakpoint-tablet: 48rem;
  --breakpoint-desktop: 75rem;

  /* --container-*  →  max-w-content and @container sizes */
  --container-content: 72rem;

  /* --ease-* and --animate-*  →  ease-brand, animate-pop */
  --ease-brand: cubic-bezier(0.2, 0.8, 0.2, 1);
}
```

```html
<section class="mx-auto max-w-content px-gutter tablet:px-8">
  <h1 class="font-display text-h1 text-neutral-900">Launch day</h1>
  <button class="rounded-control bg-brand-500 px-4 py-2 text-white shadow-card hover:bg-brand-600">Start</button>
</section>
```

A ten-line Node script turns the JSON into the CSS so the export stays the source of truth:

```js
// tokens-to-theme.mjs: node tokens-to-theme.mjs tokens.json > src/theme.css
import { readFileSync } from 'node:fs';
const NS = { color: 'color', 'font.family': 'font', 'font.size': 'text', space: 'spacing', radius: 'radius', shadow: 'shadow', breakpoint: 'breakpoint' };
const tokens = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const px = (v) => (/^\d+(\.\d+)?px$/.test(v) ? `${parseFloat(v) / 16}rem` : v);
const flat = (obj, path = []) => Object.entries(obj).flatMap(([k, v]) =>
  typeof v === 'object' ? flat(v, [...path, k]) : [[[...path, k], v]]);
const lines = flat(tokens).flatMap(([path, value]) => {
  const key = Object.keys(NS).find((p) => path.join('.').startsWith(p));
  if (!key) return [];
  const rest = path.slice(key.split('.').length).join('-');
  return [`  --${NS[key]}-${rest}: ${px(String(value))};`];
});
console.log(`@theme {\n${lines.join('\n')}\n}`);
```

## Variations

- **Replace instead of extend.** To drop Tailwind's defaults for a namespace, put `--color-*: initial;` (or `--font-*: initial;`, `--shadow-*: initial;`) first in the block, then declare yours. Smaller CSS and no stray `bg-blue-500` in reviews.
- **Tokens that are not utilities.** Values only used in your own CSS (z-index layers, animation durations) can go in a plain `:root { }` block; `@theme` is only for things that should generate classes. Use `@theme inline` when a token references another variable and must resolve at build time (`--color-primary: var(--color-brand-500)` without `inline` emits the `var()` as-is, which is usually fine).
- **Light/dark pairs from Figma modes.** Put the light values in `@theme`, the dark values under `.dark { --color-surface: ... }` in `@layer base`; see `web-design-color-system`.
- **Keep designer names.** `--color-primary`, `--spacing-gutter`, `--radius-card` make the Figma inspector and the code use the same vocabulary; only rename when the Figma name collides with a Tailwind default (e.g. a color called `red`).

## Pitfalls

- Token names with dots, slashes or spaces (`brand/primary`, `space.4`) are invalid CSS identifiers; convert separators to hyphens and strip spaces before writing the variable.
- Pixel values straight from Figma break `rem`-based scaling and zoom; divide by 16 (the script does) except for hairline borders, where `1px` is correct.
- Declaring `--spacing: 0.3rem` changes every numeric spacing utility (`p-4` becomes 1.2rem); only override the base if the design really uses a non-4px grid.
- Figma's "drop shadow" with blur 8 and spread 0 maps to `0 Xpx 8px 0`; the Y offset is separate from blur, and Figma's percent opacity becomes the alpha in `rgb(0 0 0 / 0.1)`.
- A `--breakpoint-*` in px works but mixes units with Tailwind's rem breakpoints; convert to rem so media queries respect browser zoom consistently.
- Dumping 400 tokens into `@theme` generates thousands of unused utilities only if they appear in markup, so size is fine, but editor autocomplete becomes noise; export only the tiers the components use.

## Related skills

- `web-css-variables-theming`
- `web-design-color-system`
- `web-design-typography-system`
- `web-design-shadows-and-elevation`
- `web-ship-tailwind-production`
