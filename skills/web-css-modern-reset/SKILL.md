---
name: web-css-modern-reset
description: Base styles to add on top of Tailwind v4's Preflight: what Preflight already resets, plus an @layer base block for text-wrap balance, reduced-motion-aware smooth scroll, a global focus ring, scrollbar and selection colours, media and form defaults. Use when a user starts a new site, asks for a CSS reset or normalize, or asks why headings and lists look unstyled.
---

# Modern CSS reset on top of Preflight

Tailwind v4 injects **Preflight** (a modern-normalize derivative) into the `base` layer when you `@import "tailwindcss"`. It zeroes margins, sets `box-sizing: border-box`, makes images `display: block; max-width: 100%`, strips list bullets and heading sizes, inherits fonts on form controls, and sets `border-style: solid` with a 1px default so `border` utilities work. You do not add another reset on top of it; you add a *small* base layer for the things Preflight deliberately leaves alone: focus rings, text wrapping, scroll behaviour, selection, scrollbars, and project defaults for body text.

## Pattern

```css
/* src/input.css */
@import "tailwindcss";

@layer base {
  /* Scroll: smooth only for people who have not asked for reduced motion */
  html {
    scroll-behavior: smooth;
    scroll-padding-top: 5rem;                 /* room for a sticky header on #anchors */
    -webkit-text-size-adjust: 100%;
    hanging-punctuation: first last;          /* Safari; harmless elsewhere */
  }
  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }

  /* Body defaults; colours come from theme tokens (see web-css-variables-theming) */
  body {
    min-height: 100dvh;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    overflow-wrap: anywhere;                  /* long URLs never widen the layout */
  }

  /* Text wrapping: headings balance, paragraphs avoid orphans */
  h1, h2, h3, h4, blockquote { text-wrap: balance; }
  p, li, figcaption { text-wrap: pretty; max-width: 75ch; }

  /* One focus ring everywhere, only for keyboard/programmatic focus */
  :focus-visible {
    outline: 2px solid var(--color-blue-600);
    outline-offset: 2px;
    border-radius: 0.125rem;
  }
  :focus:not(:focus-visible) { outline: none; }

  /* Media: fill width, keep ratio, no inline gap (Preflight sets display:block already) */
  img, video, canvas, svg { height: auto; }
  img { font-style: italic; }                 /* alt text looks like a caption when image fails */
  svg:not([fill]) { fill: currentColor; }

  /* Forms */
  input, textarea, select, button { font: inherit; color: inherit; }
  textarea { field-sizing: content; min-height: 3lh; }   /* grows with content; progressive */
  button, [role="button"], summary { cursor: pointer; }
  :disabled { cursor: not-allowed; }
  input[type="search"]::-webkit-search-cancel-button { -webkit-appearance: none; }

  /* Selection and scrollbars pick up the theme */
  ::selection { background: var(--color-blue-600); color: white; }
  * { scrollbar-width: thin; scrollbar-color: var(--color-gray-400) transparent; }

  /* Tables and misc */
  table { border-collapse: collapse; width: 100%; }
  th { text-align: start; }
  [hidden] { display: none !important; }
  [id] { scroll-margin-top: 5rem; }           /* belt and braces with scroll-padding-top */
}
```

Things Preflight already does that you should **not** redo: `*, ::before, ::after { box-sizing: border-box; margin: 0; padding: 0; border: 0 solid }`, `html { line-height: 1.5; font-family: var(--font-sans) }`, headings and `b/strong` inherit size and weight, `ol/ul { list-style: none }`, `img/video { display: block; max-width: 100% }`, `button { background: transparent; appearance: button }`, `textarea { resize: vertical }`, placeholder colour at 50% opacity.

## Variations

- **Restore list bullets inside prose**: Preflight removes them globally. Add `.prose ul { list-style: disc; padding-left: 1.5em }` in `@layer base` (or use `list-disc pl-6` utilities) only where content is authored, not in nav lists.
- **Opt out of Preflight entirely** (legacy site, CMS content): `@layer theme, base, components, utilities; @import "tailwindcss/theme.css" layer(theme); @import "tailwindcss/utilities.css" layer(utilities);` and skip `preflight.css`. Then you own the whole reset above and more.
- **Dark-mode focus ring**: use a semantic token (`outline-color: var(--accent)`) instead of a hard-coded blue so it contrasts on both backgrounds.
- **Stricter `prefers-reduced-motion`**: the block above neuters all animation; if you want *some* motion to survive, remove it and use Tailwind's `motion-safe:`/`motion-reduce:` per animation instead (see `web-motion-reduced-motion`).

## Pitfalls

- **Adding `normalize.css` or a classic reset** alongside Preflight: double resets fight over borders and button styles. One reset only.
- **`outline: none` on `:focus`** without a `:focus-visible` replacement removes keyboard focus for everyone. The pair above shows a ring to keyboard users and hides it after mouse clicks.
- **Global `text-wrap: balance` on paragraphs**: browsers cap balancing at a few lines and it costs layout time; `balance` for headings, `pretty` for body.
- **`overflow-wrap: anywhere` on code blocks** splits tokens unpredictably; give `pre, code { overflow-wrap: normal; overflow-x: auto }`.
- **`field-sizing` and `hanging-punctuation`** are progressive: supported in Chromium/Safari, ignored elsewhere, which is fine. Do not rely on them for layout.
- **Base styles outside `@layer base`** are unlayered and beat every Tailwind utility (unlayered CSS wins over layered). Put all element selectors in `@layer base` so `text-lg` on an `<h2>` still works.
- **`[id] { scroll-margin-top }`** is coarse; if a page has no sticky header, drop both scroll offsets.

## Related skills

- `web-css-layers-and-organization` for where this file sits and how layers interact
- `web-css-variables-theming` for the tokens referenced here
- `web-a11y-keyboard-and-focus` for focus ring design and focus order
- `web-motion-reduced-motion` for a finer reduced-motion strategy
- `web-design-typography-system` for body and heading scales set on top of this base
- `web-ship-project-setup` for the `input.css` build pipeline
