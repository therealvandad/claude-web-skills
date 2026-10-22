---
name: web-design-borders-radius-dividers
description: Set a radius scale in Tailwind v4 `@theme`, nest rounded corners correctly (outer = inner + padding), choose between `border`, `ring` and `outline`, and build dividers with `divide-*`, `<hr>` and labelled separators. Use whenever a user asks about rounded corners, border radius, doubled borders, a divider or separator line, or nested cards whose corners clash.
---

# Borders, radius and dividers

Corners and lines are where a UI looks either crafted or assembled. Two rules carry most of it. First, pick a radius scale and use it consistently: inputs and buttons share one value, cards a larger one, pills are fully round. Second, nest radii mathematically: an element inside a rounded parent needs `inner = outer - padding`, otherwise the inner corner pokes out or leaves a thick wedge. Borders then come from three tools (`border`, `ring`, `outline`) that look alike but behave differently in layout, and dividers should be spacing, not boxes.

## Pattern

```css
@import "tailwindcss";

@theme {
  /* Radius scale: tokens override Tailwind's rounded-* names. */
  --radius-sm: 0.25rem;   /* 4px:  chips, checkboxes, table cells */
  --radius-md: 0.5rem;    /* 8px:  inputs, buttons, menu items */
  --radius-lg: 0.75rem;   /* 12px: cards, popovers */
  --radius-xl: 1rem;      /* 16px: panels, modals */
  --radius-2xl: 1.5rem;   /* 24px: hero media, feature blocks */
  /* rounded-full stays 9999px for pills and avatars */
}
```

```html
<!-- 1. Nested radii: card is rounded-xl (16px) with p-2 (8px), so the image inside gets 16 - 8 = 8px: rounded-md. -->
<article class="rounded-xl border border-gray-200 bg-white p-2 dark:border-gray-800 dark:bg-gray-900">
  <img src="/img/cover.jpg" width="640" height="360" alt="" class="aspect-video w-full rounded-md object-cover">
  <div class="p-4">
    <h3 class="font-semibold text-gray-900 dark:text-gray-100">Nested corners that fit</h3>
    <!-- Buttons inside a card at the same scale as inputs: rounded-md. -->
    <button class="mt-3 rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium hover:bg-gray-50
                   focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600
                   dark:border-gray-700 dark:hover:bg-gray-800">Read</button>
  </div>
</article>

<!-- 2. border vs ring vs outline on the same input: -->
<!-- border: takes layout space, fine at rest. ring: box-shadow, no layout shift, good for hover/selected.
     outline: outside the box, never clipped, reserved for focus. -->
<input type="text" placeholder="Search"
       class="w-full rounded-md border border-gray-300 bg-white px-3 py-2
              hover:ring-2 hover:ring-gray-200
              focus-visible:border-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500
              dark:border-gray-700 dark:bg-gray-900 dark:hover:ring-gray-800">

<!-- 3. Dividers between list rows: divide-y puts one line between siblings, none at the ends. -->
<ul class="divide-y divide-gray-200 rounded-lg border border-gray-200 dark:divide-gray-800 dark:border-gray-800">
  <li class="px-4 py-3">Invoices</li>
  <li class="px-4 py-3">Payouts</li>
  <li class="px-4 py-3">Tax documents</li>
</ul>

<!-- 4. Section divider: a real <hr> keeps semantics; style it, do not replace it with a div. -->
<hr class="my-10 border-gray-200 dark:border-gray-800">

<!-- 5. Labelled "or" divider: two lines with text centered, no absolute positioning. -->
<div class="my-6 flex items-center gap-4 text-sm text-gray-500" role="separator" aria-label="or">
  <span class="h-px flex-1 bg-gray-200 dark:bg-gray-800" aria-hidden="true"></span>
  <span>or continue with</span>
  <span class="h-px flex-1 bg-gray-200 dark:bg-gray-800" aria-hidden="true"></span>
</div>

<!-- 6. Button group: only the outer corners round, inner borders collapse with -ml-px. -->
<div class="inline-flex" role="group" aria-label="View">
  <button class="rounded-l-md border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50 focus-visible:z-10 focus-visible:outline-2 focus-visible:outline-indigo-600">List</button>
  <button class="-ml-px border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50 focus-visible:z-10 focus-visible:outline-2 focus-visible:outline-indigo-600">Grid</button>
  <button class="-ml-px rounded-r-md border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50 focus-visible:z-10 focus-visible:outline-2 focus-visible:outline-indigo-600">Map</button>
</div>
```

The nesting formula in practice: `rounded-xl` (16px) parent with `p-2` (8px) → child `rounded-md` (8px). `rounded-2xl` (24px) with `p-3` (12px) → child `rounded-lg` (12px). If padding is zero (image flush to the card edge), the child gets the same radius as the parent, or `overflow-hidden` on the parent and no radius on the child.

## Variations

- **Sharp / editorial.** `--radius-md: 0; --radius-lg: 0;` and keep only `rounded-full` for avatars. Dividers become `border-t-2 border-gray-950`.
- **Soft / consumer app.** Shift every token up one step (`--radius-md: 0.75rem`, cards `1.25rem`) and use `ring-1 ring-gray-950/5` instead of `border` so edges are lighter.
- **Vertical dividers in a toolbar.** `divide-x divide-gray-200` on a `flex` row, with `px-3` on each child so the line is not flush to the text; or a single `<span class="h-5 w-px bg-gray-200" aria-hidden="true">`.
- **Hairline borders on dark surfaces.** Use white at low alpha (`border-white/10`) rather than a grey step; it stays visible on any dark tone.

## Pitfalls

- Same radius on parent and child with padding between them produces the "thick corner" look; apply the subtraction rule or drop the child's radius.
- `overflow-hidden` to clip a child to the parent's radius also clips box-shadows, focus outlines and dropdowns inside; prefer giving the child its own matching radius.
- `ring-*` is `box-shadow`, so it is painted under siblings that come later in the DOM; add `focus-visible:z-10` (or `relative z-10`) in button groups so the focused ring is not half covered.
- Two adjacent bordered elements double the line to 2px; collapse with `-ml-px` / `-mt-px` or use `divide-*` on the parent instead of borders on children.
- `outline` ignores `border-radius` in old browsers only; modern browsers follow it, so `outline-offset-2` is safe on rounded elements. Never remove focus outlines without a visible replacement.
- `<hr>` has margins reset by Preflight and a 1px top border; set the color with `border-gray-200`, not `bg-*` (the background is transparent).

## Related skills

- `web-design-shadows-and-elevation`
- `web-design-tokens-to-tailwind`
- `web-ui-buttons`
- `web-ui-cards`
- `web-a11y-keyboard-and-focus`
