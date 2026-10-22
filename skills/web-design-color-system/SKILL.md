---
name: web-design-color-system
description: 'Build a color system in Tailwind v4: a brand ramp (50 to 950) in OKLCH, neutral and status ramps, semantic tokens (surface, text, border, accent) that flip for dark mode, and contrast checks. Use whenever a user asks for a palette, brand colors, "pick colors for my site", theme colors, or wants to replace Tailwind''s default colors with their own.'
---

# Color system

A color system has two layers. The **ramp layer** is raw material: ~11 steps of a brand hue, a neutral and the status hues (success, warning, danger). The **semantic layer** is what components use: `bg-surface`, `text-fg`, `border-line`, `bg-accent`. Components never touch ramp steps directly, so dark mode and rebrands are a swap of semantic values, not a search-and-replace across HTML. Tailwind v4 makes both layers plain CSS variables in `@theme`, and OKLCH gives ramps whose steps look evenly spaced, unlike HSL.

## Pattern

```css
@import "tailwindcss";

@theme {
  /* Ramp layer: one hue (indigo-ish, h=275), lightness steps from 97% to 20%, chroma peaks mid-ramp. */
  --color-brand-50:  oklch(97% 0.02 275);
  --color-brand-100: oklch(93% 0.04 275);
  --color-brand-200: oklch(87% 0.08 275);
  --color-brand-300: oklch(78% 0.13 275);
  --color-brand-400: oklch(68% 0.18 275);
  --color-brand-500: oklch(58% 0.21 275);   /* the "brand color" */
  --color-brand-600: oklch(50% 0.20 275);   /* buttons: white text passes 4.5:1 here */
  --color-brand-700: oklch(43% 0.17 275);
  --color-brand-800: oklch(36% 0.13 275);
  --color-brand-900: oklch(29% 0.09 275);
  --color-brand-950: oklch(20% 0.06 275);

  /* Neutral tinted toward the brand hue (tiny chroma) so greys do not look dead next to it. */
  --color-neutral-50:  oklch(98.5% 0.003 275);
  --color-neutral-100: oklch(96% 0.004 275);
  --color-neutral-200: oklch(91% 0.006 275);
  --color-neutral-300: oklch(84% 0.008 275);
  --color-neutral-400: oklch(68% 0.012 275);
  --color-neutral-500: oklch(55% 0.014 275);
  --color-neutral-600: oklch(45% 0.014 275);
  --color-neutral-700: oklch(36% 0.012 275);
  --color-neutral-800: oklch(26% 0.010 275);
  --color-neutral-900: oklch(19% 0.008 275);
  --color-neutral-950: oklch(13% 0.006 275);

  /* Status hues: only the steps components actually use. */
  --color-success-500: oklch(65% 0.17 150);  --color-success-700: oklch(45% 0.14 150);
  --color-warning-500: oklch(78% 0.16 80);   --color-warning-700: oklch(55% 0.14 70);
  --color-danger-500:  oklch(60% 0.21 25);   --color-danger-700:  oklch(47% 0.19 25);

  /* Semantic layer: what components reference. Light values here. */
  --color-surface:        var(--color-neutral-50);
  --color-surface-raised: white;
  --color-fg:             var(--color-neutral-900);
  --color-fg-muted:       var(--color-neutral-600);
  --color-line:           var(--color-neutral-200);
  --color-accent:         var(--color-brand-600);
  --color-accent-hover:   var(--color-brand-700);
  --color-on-accent:      white;
}

/* Dark values: re-point the semantic tokens only. */
@layer base {
  @media (prefers-color-scheme: dark) {
    :root {
      --color-surface:        var(--color-neutral-950);
      --color-surface-raised: var(--color-neutral-900);
      --color-fg:             var(--color-neutral-100);
      --color-fg-muted:       var(--color-neutral-400);
      --color-line:           var(--color-neutral-800);
      --color-accent:         var(--color-brand-400);   /* lighter on dark so it still reads */
      --color-accent-hover:   var(--color-brand-300);
      --color-on-accent:      var(--color-neutral-950);
    }
  }
}
```

```html
<section class="bg-surface text-fg">
  <article class="rounded-xl border border-line bg-surface-raised p-6">
    <h2 class="text-xl font-semibold">Pro plan</h2>
    <p class="mt-1 text-fg-muted">Everything in Free, plus unlimited projects.</p>
    <button class="mt-4 rounded-lg bg-accent px-4 py-2 font-medium text-on-accent hover:bg-accent-hover
                   focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
      Upgrade
    </button>
    <p class="mt-3 text-sm text-danger-700">Card expired</p>
  </article>
</section>
```

Because the semantic tokens are defined in `@theme`, `bg-surface`, `text-fg-muted` and `border-line` are real utilities with all variants (`hover:`, `md:`, `dark:`) for free.

## Variations

- **Class-based dark toggle.** Replace the media query with `.dark { ... }` and add `@custom-variant dark (&:where(.dark, .dark *));` so `dark:` utilities also follow the class. See `web-design-dark-mode`.
- **Generate a ramp from one hex.** Convert the brand color to OKLCH (any browser devtools color picker shows it), keep its hue, and step lightness 97/93/87/78/68/58/50/43/36/29/20 with chroma rising to the 500 step and falling after.
- **Two accents.** Add `--color-accent-2` from a hue 150 to 180 degrees away (complement) for charts and highlights; keep the primary for every interactive element so users learn one "clickable" color.
- **Replace Tailwind's palette entirely.** Start the block with `--color-*: initial;` to drop every default color, then declare only your ramps. Smaller CSS and no accidental `bg-blue-500`.

## Pitfalls

- OKLCH chroma above ~0.2 at mid lightness falls outside sRGB on many screens; browsers clamp it, so two steps can render identically. Check on a non-P3 monitor or keep chroma at 0.21 or below.
- "Brand-500" as a button background with white text usually fails 4.5:1. Use the 600 or 700 step for filled buttons and keep 500 for icons and large text.
- Pure black text on pure white is harsh and makes thin fonts shimmer; `neutral-900` on `neutral-50` is the usual fix without losing contrast.
- Never encode meaning in color alone: pair `text-danger-700` with an icon or the word "Error" for color-blind users and screen readers.
- Semantic variables must be set on `:root` (or `.dark`), not inside `@theme` for the dark branch; `@theme` does not accept nested media queries.
- Status colors need their own contrast check against both surfaces; a warning yellow that works on white vanishes on `neutral-950`.

## Related skills

- `web-design-dark-mode`
- `web-a11y-color-contrast`
- `web-css-variables-theming`
- `web-design-tokens-to-tailwind`
- `web-design-shadows-and-elevation`
