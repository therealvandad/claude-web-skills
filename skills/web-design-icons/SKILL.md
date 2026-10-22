---
name: web-design-icons
description: Use SVG icons correctly on a Tailwind site: inline SVG with `currentColor`, a sprite referenced with `<use>`, a size scale, icon-plus-text alignment, decorative vs meaningful icons and accessible icon-only buttons. Use whenever a user asks to add icons, "use Heroicons/Lucide", an icon button, a sprite, or whether to use Font Awesome or an icon font (no).
---

# Icons

Icons are vector line art that must match the text next to them in size and color. Inline SVG does that natively: `fill="currentColor"` or `stroke="currentColor"` inherits the text color, `size-5` sets width and height in the same rem units as the type scale, and there is nothing to download. Icon fonts fail all three tests (they anti-alias like text, break when fonts are blocked, and read as random glyphs to screen readers), so this pack never uses them.

## Pattern

```html
<!-- 1. A sprite: one hidden SVG at the top of <body> (or a separate icons.svg file). -->
<svg xmlns="http://www.w3.org/2000/svg" class="hidden" aria-hidden="true">
  <symbol id="i-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
  </symbol>
  <symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 6 9 17l-5-5"/>
  </symbol>
  <symbol id="i-x" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 6 6 18M6 6l12 12"/>
  </symbol>
</svg>

<!-- 2. Decorative icon next to a label: aria-hidden, the text carries the meaning. -->
<button class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white
               hover:bg-indigo-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
  <svg class="size-4 shrink-0" aria-hidden="true"><use href="#i-check"/></svg>
  Save changes
</button>

<!-- 3. Icon-only button: the accessible name comes from aria-label; hit area stays 44px. -->
<button type="button" aria-label="Close dialog"
        class="inline-flex size-11 items-center justify-center rounded-full text-gray-500
               hover:bg-gray-100 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-indigo-600
               dark:hover:bg-gray-800 dark:hover:text-gray-100">
  <svg class="size-5" aria-hidden="true"><use href="#i-x"/></svg>
</button>

<!-- 4. Meaningful standalone icon (no text at all): give it a title and role. -->
<svg class="size-5 text-green-600" role="img" aria-labelledby="ok-title">
  <title id="ok-title">Verified</title>
  <use href="#i-check"/>
</svg>

<!-- 5. Inline icon inside running text: align to the cap height, not the baseline. -->
<p class="text-gray-700 dark:text-gray-300">
  Search with
  <svg class="inline size-[1em] align-[-0.125em]" aria-hidden="true"><use href="#i-search"/></svg>
  anywhere on the page.
</p>
```

Size scale that pairs with the type scale: `size-4` (16px) next to `text-sm`, `size-5` (20px) next to `text-base`, `size-6` (24px) in toolbars and nav, `size-8` or larger only for feature illustrations. Stroke width stays 1.5 to 2 at every size; if a 2px stroke looks heavy at `size-4`, use the icon set's 1.5 variant rather than scaling the stroke.

## Variations

- **External sprite file.** Move the `<svg>` to `/icons.svg` and reference `<use href="/icons.svg#i-check"/>`. It caches once across pages, but it must be same-origin and will not work from `file://`; keep the inline sprite for prototypes.
- **Copy from an icon set.** Lucide, Heroicons and Tabler ship MIT-licensed 24px SVGs with `currentColor` already set; paste the inner paths into a `<symbol>` and keep the original `viewBox`. Do not mix sets; stroke widths and corner radii differ.
- **Two-tone icons.** Use `fill="currentColor"` for the main shape and `class="fill-current opacity-30"` on a secondary path; one color, two intensities, works in any theme.
- **Animated state icons.** Swap symbols with `hidden`/`block` on a wrapper (`group-aria-expanded:rotate-180` on a chevron is the common one) inside `motion-safe:transition-transform`.

## Pitfalls

- Omitting `aria-hidden="true"` on decorative icons makes screen readers announce "image" or the symbol id before every button label.
- An icon-only `<button>` without `aria-label` has no name; `title` alone is not enough (not read reliably, not shown on touch).
- Setting `width`/`height` attributes on the `<svg>` instead of classes stops `size-*` from working; strip them and keep only `viewBox`.
- `shrink-0` is required on icons inside flex rows, or long labels squash the icon to 0 width on narrow screens.
- Targets smaller than 24px with no padding fail WCAG target-size; wrap the icon in a `size-10` or `size-11` button and center it.
- A sprite placed at the end of `<body>` makes icons pop in late on slow connections; put it right after `<body>` or in the external file with `<link rel="preload" as="image">`.

## Related skills

- `web-ui-buttons`
- `web-a11y-images-and-media`
- `web-a11y-aria-patterns`
- `web-nav-responsive-navbar`
- `web-design-ui-polish-checklist`
