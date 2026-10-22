---
name: web-theme-switcher
description: Build a multi-theme architecture in Tailwind v4: semantic tokens redefined per [data-theme], a radio picker with live swatch previews, no-flash persistence in localStorage and a checklist for adding a theme. Use whenever a user asks for a "theme switcher", "theme picker", "multiple themes", "brand switcher", "skins" or "white-label".
---

# Theme switcher

A switcher is not a set of alternative stylesheets; it is one stylesheet whose utilities read variables, plus a few blocks that change what those variables hold. In Tailwind v4 every colour, font and radius utility compiles to `var(--token)`, so redefining `--color-paper` under `[data-theme="terminal"]` re-skins every `bg-paper` on the page without touching markup. The discipline is the contract: every theme defines the same token names, and components never use a colour that is not a token.

## Pattern

```css
@import "tailwindcss";

/* The contract. Default values are the editorial theme; every other theme redefines all of these. */
@theme {
  --font-display: "Newsreader", Georgia, serif;
  --font-sans: "Public Sans", system-ui, sans-serif;
  --color-paper:   oklch(97% 0.010 70);   --color-paper-2: oklch(93% 0.014 70);
  --color-ink:     oklch(20% 0.015 60);   --color-ink-2:   oklch(45% 0.015 60);
  --color-line:    oklch(82% 0.014 70);
  --color-accent:  oklch(42% 0.14 25);    --color-accent-deep: oklch(34% 0.13 25);
  --color-on-accent: oklch(97% 0.010 70);  /* text on accent: light or dark per theme */
  --radius-ui: 0;
}

@custom-variant terminal (&:where([data-theme="terminal"], [data-theme="terminal"] *));

@layer base {
  [data-theme="corporate"] {
    --font-display: "IBM Plex Sans", system-ui, sans-serif;  --font-sans: var(--font-display);
    --color-paper: oklch(99% 0.003 245);  --color-paper-2: oklch(96.5% 0.006 245);
    --color-ink:   oklch(23% 0.020 250);  --color-ink-2:   oklch(47% 0.020 250);
    --color-line:  oklch(90% 0.008 245);
    --color-accent: oklch(48% 0.13 245); --color-accent-deep: oklch(40% 0.12 248);
    --color-on-accent: oklch(99% 0.003 245);
    --radius-ui: 0.375rem;
  }
  [data-theme="terminal"] {
    color-scheme: dark;
    --font-display: "JetBrains Mono", ui-monospace, monospace;  --font-sans: var(--font-display);
    --color-paper: oklch(17% 0.012 160);  --color-paper-2: oklch(21% 0.014 160);
    --color-ink:   oklch(88% 0.020 150);  --color-ink-2:   oklch(64% 0.025 155);
    --color-line:  oklch(32% 0.018 160);
    --color-accent: oklch(80% 0.17 150); --color-accent-deep: oklch(68% 0.16 150);
    --color-on-accent: oklch(17% 0.012 160);
    --radius-ui: 2px;
  }
  [data-theme] { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); }
  :focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
}
```

```html
<html lang="en" data-theme="editorial">
<head>
  <meta name="theme-color" content="oklch(97% 0.010 70)">
  <script>try { const t = localStorage.getItem("theme"); if (t) document.documentElement.dataset.theme = t; } catch {}</script>
</head>

<fieldset data-theme-picker class="flex flex-wrap gap-3">
  <legend class="mb-2 text-sm text-ink-2">Theme</legend>
  <label class="rounded-ui p-1 has-checked:outline-2 has-checked:outline-ink has-focus-visible:outline-accent">
    <input type="radio" name="theme" value="editorial" class="sr-only">
    <span data-theme="editorial" class="block w-32 rounded-ui border border-line p-3">
      <span class="block font-display text-2xl leading-none">Aa</span>
      <span class="mt-3 flex gap-1" aria-hidden="true"><i class="size-3 bg-paper-2"></i><i class="size-3 bg-ink"></i><i class="size-3 bg-accent"></i></span>
      <span class="mt-2 block text-xs">Editorial</span>
    </span>
  </label>
  <!-- repeat the label for corporate and terminal, changing value, data-theme and name -->
</fieldset>
```

```js
// theme-switcher.js, loaded with type="module"
const FONTS = {
  editorial: "family=Newsreader:opsz,wght@6..72,400..500&family=Public+Sans:wght@400;500",
  corporate: "family=IBM+Plex+Sans:wght@400;500;600",
  terminal:  "family=JetBrains+Mono:wght@400;600",
};
const root = document.documentElement;
const picker = document.querySelector("[data-theme-picker]");

function loadFonts(theme) {
  if (!FONTS[theme] || document.querySelector(`link[data-font="${theme}"]`)) return;
  const link = Object.assign(document.createElement("link"), {
    rel: "stylesheet", href: `https://fonts.googleapis.com/css2?${FONTS[theme]}&display=swap`,
  });
  link.dataset.font = theme;
  document.head.append(link);
}

function applyTheme(theme) {
  if (!(theme in FONTS)) return;
  loadFonts(theme);
  root.dataset.theme = theme;
  try { localStorage.setItem("theme", theme); } catch {}
  const paper = getComputedStyle(root).getPropertyValue("--color-paper").trim();
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", paper);
}

if (!(root.dataset.theme in FONTS)) root.dataset.theme = "editorial";
picker.elements.namedItem("theme").value = root.dataset.theme;
loadFonts(root.dataset.theme);
picker.addEventListener("change", (event) => applyTheme(event.target.value));
for (const type of ["pointerenter", "focusin"]) {
  picker.addEventListener(type, () => Object.keys(FONTS).forEach(loadFonts), { once: true });
}
```

The preview works because custom properties cascade: a `<span data-theme="terminal">` inside an editorial page resolves `bg-paper` and `font-display` to the terminal values, so each swatch renders in its own theme without screenshots. The same trick themes a single section (`<section data-theme="terminal">`) for a code sample.

Adding a theme:

1. Copy one `[data-theme]` block, rename it and redefine every token in the contract; a missing token silently falls back to the default theme.
2. Set `color-scheme: dark` if the paper is dark, so form controls and scrollbars follow.
3. Check `ink`, `ink-2` and `on-accent` against `paper`, `paper-2` and `accent` (4.5:1) and `line` where it borders inputs (3:1).
4. Add the font query to `FONTS` and a `<label>` to the picker. Theme-specific quirks go in a `@custom-variant` like `terminal:`, not in a new token.

## Variations

- **Follow the system first**: when nothing is stored, pick with `matchMedia("(prefers-color-scheme: dark)").matches ? "terminal" : "editorial"` in the head script, and offer an "Automatic" radio that removes the key.
- **Many themes**: past five, swap the radios for a native `<select>` and keep one live preview card next to it with `data-theme` bound to the selected value.
- **Server-rendered**: store the choice in a cookie instead of `localStorage` and print `data-theme` on `<html>` from the server; the head script and flash both disappear.
- **Light and dark per theme**: give each theme a dark twin (`[data-theme="corporate"].dark`) rather than a separate theme name, so the picker and the dark toggle stay independent.

## Pitfalls

- `@theme inline` bakes the values into each utility instead of `var()`, which breaks switching completely; use plain `@theme` for anything a theme redefines.
- The head script must be inline and before the stylesheet's first paint; loaded as a module it runs after render and every visit flashes the default theme.
- Loading every theme's fonts on page load costs 200 to 400 KB; load the active one, and the rest only when the picker is approached.
- Hard-coded utilities like `text-white` or `bg-blue-600` survive every switch and break the darker themes; search for palette names before shipping (`web-craft-consistency-audit`).
- `localStorage` throws in some private modes and sandboxed frames; both reads and writes stay in `try`.
- The radio stays the focus target, so the label needs a visible `has-focus-visible:` ring; an `sr-only` input with no ring on its label is invisible to keyboard users.

## Related skills

- `web-css-variables-theming`
- `web-design-tokens-to-tailwind`
- `web-design-dark-mode`
- `web-js-storage`
- `web-perf-fonts`
- `web-theme-editorial`
- `web-theme-corporate-clean`
- `web-theme-terminal`
