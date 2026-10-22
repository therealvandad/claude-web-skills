---
name: web-css-variables-theming
description: Set up a themeable site with CSS custom properties and Tailwind v4 @theme: brand tokens that become utilities, semantic tokens (bg, fg, accent, line) that flip for dark mode or a brand switch, read from CSS and JS. Use whenever a user asks for a theme, brand colours, "change the colour in one place", CSS variables, design tokens, or multi-brand.
---

# CSS variables and Tailwind v4 theming

Tailwind v4 is built on CSS variables: every `@theme` token becomes both a utility class and a `var(--…)` you can read anywhere. The trick that keeps a theme maintainable is **two layers of tokens**. Primitive tokens name raw values (`--color-blue-600`); semantic tokens name *roles* (`--color-bg`, `--color-fg`, `--color-accent`). Components only ever use the semantic layer, so dark mode or a rebrand is a handful of reassignments in one file, not a hunt through templates for `bg-white dark:bg-gray-900`.

## Pattern

```css
/* src/input.css */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));   /* class-based toggle; drop for OS-only */

/* 1. Primitive brand tokens: become bg-brand-500, text-brand-700, border-brand-200 ... */
@theme {
  --color-brand-50:  oklch(97% 0.02 250);
  --color-brand-200: oklch(90% 0.06 250);
  --color-brand-500: oklch(60% 0.18 250);
  --color-brand-700: oklch(45% 0.16 250);
  --color-brand-900: oklch(28% 0.10 250);
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --radius-card: 1rem;                           /* rounded-card */
}

/* 2. Semantic tokens, declared with @theme inline so the utility reads the
      *variable* (var(--bg)) at use time and re-evaluates when .dark changes it. */
@theme inline {
  --color-bg: var(--bg);
  --color-bg-muted: var(--bg-muted);
  --color-fg: var(--fg);
  --color-fg-muted: var(--fg-muted);
  --color-accent: var(--accent);
  --color-accent-fg: var(--accent-fg);
  --color-line: var(--line);
}

/* 3. The actual values, light by default, overridden under .dark */
@layer base {
  :root {
    --bg: oklch(100% 0 0);
    --bg-muted: oklch(97% 0.005 250);
    --fg: oklch(20% 0.02 250);
    --fg-muted: oklch(50% 0.02 250);
    --accent: var(--color-brand-500);
    --accent-fg: white;
    --line: oklch(90% 0.01 250);
    color-scheme: light;
  }
  .dark {
    --bg: oklch(18% 0.02 250);
    --bg-muted: oklch(24% 0.02 250);
    --fg: oklch(95% 0.01 250);
    --fg-muted: oklch(70% 0.02 250);
    --accent: oklch(72% 0.16 250);              /* lighter accent for dark bg */
    --accent-fg: oklch(18% 0.02 250);
    --line: oklch(32% 0.02 250);
    color-scheme: dark;
  }
  body { background: var(--bg); color: var(--fg); }
}
```

```html
<!-- Components use roles only. No dark: variants needed for colour. -->
<article class="rounded-card border border-line bg-bg-muted p-6 text-fg">
  <h3 class="font-semibold">Themed card</h3>
  <p class="mt-2 text-fg-muted">Muted copy that stays readable in both modes.</p>
  <button type="button"
          class="mt-4 rounded-md bg-accent px-4 py-2 text-accent-fg hover:bg-accent/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
    Action
  </button>
</article>
```

Reading a token in JS (for canvas, charts, inline SVG): `getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()`.

## Variations

- **Multiple brands or tenants**: add `[data-brand="acme"] { --accent: …; }` next to `.dark`. Switching brand is one attribute on `<html>`. Combine freely: `.dark[data-brand="acme"]`.
- **OS preference only** (no toggle): delete the `@custom-variant` line and wrap the `.dark` block in `@media (prefers-color-scheme: dark) { :root { … } }`.
- **Opacity modifiers keep working** on semantic colours (`bg-accent/20`) because Tailwind uses `color-mix()` for variable-based colours.
- **Component-scoped variables**: `.btn { --btn-bg: var(--accent); background: var(--btn-bg); } .btn--danger { --btn-bg: var(--color-red-600); }` keeps variants to one line each; combine with Tailwind's arbitrary properties `[--btn-bg:theme(--color-red-600)]` when you need it inline.

## Pitfalls

- **`@theme` versus `@theme inline`**: plain `@theme { --color-bg: var(--bg) }` inlines the *value* at build time and the dark override never applies. Any token that references another variable that changes at runtime must be in `@theme inline`.
- **Declaring tokens outside `@theme`** (`:root { --color-x: … }`) gives you a variable but *no utility*; `bg-x` will not exist. Put utility-generating tokens in `@theme`, raw runtime values in `:root`.
- **`theme()` function from v3**: still works for compatibility, but in v4 prefer `var(--color-brand-500)` directly in CSS; it is just a variable now.
- **Forgetting `color-scheme`**: without it, form controls, scrollbars and the default `<select>` stay light in dark mode.
- **Same accent in both modes**: saturated mid-tone brand colours often fail contrast on dark backgrounds. Give dark mode its own lighter accent and check with `web-a11y-color-contrast`.
- **Token sprawl**: if you need `--color-bg-muted-hover-active`, you have gone too far. Six to ten semantic colours cover most sites; use opacity modifiers (`bg-accent/10`) for states.
- **Resetting the default palette**: `@theme { --color-*: initial; }` removes every Tailwind colour so only yours exist; do this deliberately for strict brand compliance, and know that `gray-*` disappears too.

## Related skills

- `web-design-color-system` for building the palette and contrast rules
- `web-design-dark-mode` for the toggle, persistence and flash-free loading
- `web-design-tokens-to-tailwind` for converting a Figma token export into this file
- `web-css-layers-and-organization` for where the `@layer base` block lives
- `web-css-fluid-typography` and `web-css-spacing-scale` for non-colour tokens
