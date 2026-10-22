---
name: web-a11y-color-contrast
description: Pick and verify colors that meet WCAG contrast (4.5:1 text, 3:1 large text, UI parts, focus rings), with Tailwind v4 palette pairs that pass in light and dark mode, non-color cues, and a tiny JS contrast checker. Use when a user says "contrast", "too light", "is this gray readable", "accessible colors", "color blind safe", or "Lighthouse contrast error".
---

# Color contrast

Low-contrast text is the single most common accessibility failure on the web and the easiest to
fix. WCAG 2.2 SC 1.4.3 requires 4.5:1 for normal text and 3:1 for large text (24px+, or 18.66px+
bold); SC 1.4.11 requires 3:1 for UI component boundaries, icons that carry meaning, and focus
indicators against adjacent colors. SC 1.4.1 says color must never be the only cue. Contrast is a
ratio of relative luminance, so "a slightly darker gray" is not a judgement call; compute it.

## Pattern

Tailwind v4 pairs that pass, chosen so you can stop guessing. The `@theme` block makes them
semantic tokens so a change in one place fixes the whole site.

```css
@import "tailwindcss";

@theme {
  --color-fg:        var(--color-gray-900);   /* 17.9:1 on white */
  --color-fg-muted:  var(--color-gray-600);   /* 7.2:1 on white, use for secondary text */
  --color-bg:        #ffffff;
  --color-bg-subtle: var(--color-gray-50);
  --color-link:      var(--color-blue-700);   /* 6.6:1 on white, 3.3:1 vs gray-900 text */
  --color-accent:    var(--color-blue-600);   /* white text on it: 5.2:1 */
  --color-danger:    var(--color-red-700);    /* 5.9:1 on white */
  --color-border:    var(--color-gray-400);   /* 3.0:1 on white: minimum for inputs */
}
```

```html
<main class="bg-bg text-fg dark:bg-gray-950 dark:text-gray-100">
  <p class="text-fg-muted dark:text-gray-400">Secondary copy stays at 7:1 light, 7.6:1 dark.</p>

  <!-- Links: color plus underline, so color is not the only cue (SC 1.4.1) -->
  <a href="/docs" class="text-link underline decoration-1 underline-offset-2 hover:decoration-2 dark:text-blue-400">Read the docs</a>

  <!-- Button: 5.2:1 text, and a 3:1 focus ring that works on light and dark -->
  <button type="button" class="rounded-md bg-accent px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:focus-visible:outline-blue-300">
    Save
  </button>

  <!-- Input border at 3:1; error uses icon + text, not just red -->
  <label for="email" class="block font-medium">Email</label>
  <input id="email" type="email" aria-invalid="true" aria-describedby="email-err"
         class="mt-1 w-full rounded-md border border-border bg-white px-3 py-2 text-fg aria-invalid:border-red-700 dark:bg-gray-900 dark:text-gray-100">
  <p id="email-err" class="mt-1 flex items-center gap-1 text-sm text-danger dark:text-red-400">
    <svg aria-hidden="true" class="size-4" viewBox="0 0 20 20" fill="currentColor"><path d="M10 2a8 8 0 100 16 8 8 0 000-16zm-1 4h2v5H9V6zm0 6h2v2H9v-2z"/></svg>
    Enter an address with an @ sign.
  </p>

  <!-- Status badge: shape and text carry meaning, color just reinforces -->
  <span class="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-sm font-medium text-green-900 dark:bg-green-950 dark:text-green-200">
    <span aria-hidden="true">&#10003;</span> Paid
  </span>
</main>
```

Check any pair without leaving the console:

```js
const lum = (hex) => {
  const [r, g, b] = hex.replace('#', '').match(/.{2}/g).map((c) => parseInt(c, 16) / 255)
    .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
export const contrast = (a, b) => {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return ((hi + 0.05) / (lo + 0.05)).toFixed(2);
};
// contrast('#4b5563', '#ffffff') -> "7.56"  (gray-600 on white)
```

Rules of thumb for the default Tailwind palette on white: `-600` and darker passes 4.5:1 for every
hue except yellow, lime, amber and cyan (need `-700`/`-800`); `-500` only passes for large text in
most hues; `-400` and lighter is decoration only. On `gray-950`, `-300` and lighter passes, `-400`
is the floor for body text.

## Variations

- **Dark mode**: do not invert blindly. Use `-400`/`-300` tints for colored text (`text-blue-400`),
  `-950`/`-900` tints for colored backgrounds, and lower the saturation of large fills; pure white
  text on pure black causes halation, so prefer `gray-100` on `gray-950`.
- **Large display text** (hero headlines) may use 3:1 pairs like `gray-500` on white, but keep the
  subcopy at 4.5:1.
- **Placeholder text** is still text: `placeholder:text-gray-500` (4.6:1), not the default gray-400.
- **Disabled controls** are exempt from contrast, but make disabled state obvious by more than
  fading: `disabled:opacity-50 disabled:cursor-not-allowed` plus explanatory help text nearby.

## Pitfalls

- Text over images or gradients: contrast varies per pixel. Add a scrim (`bg-black/60`) or a
  solid panel behind the text; test the lightest region.
- Thin or light-weight fonts at exactly 4.5:1 read worse than the number suggests. Add weight or
  bump a shade when using `font-light`.
- Color-only states: red border for errors, green dot for online, colored-only links in body text.
  Pair with an icon, text, underline or pattern. Around 1 in 12 men cannot tell red from green.
- Focus rings in the brand color on a brand-colored button vanish. Use `outline-offset-2` so the
  ring sits on the page background, or a two-tone ring (`ring-2 ring-white ring-offset-2`).
- Trusting Tailwind's palette names: `yellow-600` on white is 2.9:1. Check hue by hue.
- Lighthouse checks text only; it does not check icons, borders, focus rings or text on images.
  Spot-check those with the function above or the browser devtools color picker.

## Related skills

- `web-design-color-system`
- `web-design-dark-mode`
- `web-a11y-keyboard-and-focus`
- `web-form-input-states`
- `web-ui-badges-chips-tags`
- `web-design-ui-polish-checklist`
