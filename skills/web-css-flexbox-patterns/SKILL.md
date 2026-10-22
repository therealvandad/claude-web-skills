---
name: web-css-flexbox-patterns
description: 'The daily flexbox recipes in Tailwind v4 classes: perfect centering, space-between toolbars, wrapping tag rows with gap, "push this to the right" with ml-auto, sticky-footer columns, and the holy-grail shell. Use whenever a user asks to center something, align items in a row, build a toolbar or button bar, make chips wrap, or asks why flex items squish or overflow.'
---

# Flexbox patterns

Flexbox lays out items along **one axis** and is the right tool for bars, rows of controls, vertical stacks and anything that should size to its content. Use Grid when you need rows *and* columns to line up (see `web-css-responsive-grid`). Almost every flex bug comes from three defaults: items **shrink** (`flex-shrink: 1`), items have **`min-width: auto`** (they refuse to get smaller than their content), and the container does **not wrap**. The recipes below set those deliberately.

## Pattern

```html
<!-- 1. Center anything, both axes -->
<div class="flex min-h-64 items-center justify-center bg-gray-100">
  <p>Centered</p>
</div>

<!-- 2. Toolbar: logo left, actions right, everything vertically centered -->
<header class="flex items-center justify-between gap-4 border-b px-4 py-3">
  <a href="/" class="shrink-0 font-semibold">Logo</a>
  <nav class="flex items-center gap-2" aria-label="Primary">
    <a href="/docs" class="rounded px-3 py-2 hover:bg-gray-100">Docs</a>
    <a href="/pricing" class="rounded px-3 py-2 hover:bg-gray-100">Pricing</a>
    <button type="button" class="rounded bg-blue-600 px-3 py-2 text-white">Sign up</button>
  </nav>
</header>

<!-- 3. Push one item to the far end with ml-auto (no justify-between needed) -->
<div class="flex items-center gap-3 rounded-lg border p-3">
  <img src="avatar.jpg" alt="" class="size-10 shrink-0 rounded-full" />
  <div class="min-w-0">
    <p class="truncate font-medium">A very long user name that must truncate</p>
    <p class="truncate text-sm text-gray-500">user@example.com</p>
  </div>
  <button type="button" class="ml-auto shrink-0 rounded border px-3 py-1.5">Edit</button>
</div>

<!-- 4. Wrapping row of chips/tags with uniform gap -->
<ul class="flex flex-wrap gap-2" role="list">
  <li class="rounded-full bg-gray-200 px-3 py-1 text-sm">Design</li>
  <li class="rounded-full bg-gray-200 px-3 py-1 text-sm">Engineering</li>
  <li class="rounded-full bg-gray-200 px-3 py-1 text-sm">Accessibility</li>
</ul>

<!-- 5. Column with sticky footer: card whose button sits at the bottom -->
<article class="flex h-full flex-col rounded-xl border p-6">
  <h3 class="text-lg font-semibold">Title</h3>
  <p class="mt-2 text-gray-600">Body text of varying length.</p>
  <a href="#" class="mt-auto pt-4 font-medium text-blue-600">Read more →</a>
</article>

<!-- 6. Holy grail: header, (sidebar + main + aside), footer; stacks on mobile -->
<div class="flex min-h-dvh flex-col">
  <header class="border-b p-4">Header</header>
  <div class="flex flex-1 flex-col md:flex-row">
    <nav class="border-b p-4 md:w-56 md:shrink-0 md:border-b-0 md:border-r" aria-label="Sidebar">Nav</nav>
    <main class="min-w-0 flex-1 p-4">Main</main>
    <aside class="border-t p-4 md:w-64 md:shrink-0 md:border-t-0 md:border-l">Aside</aside>
  </div>
  <footer class="border-t p-4">Footer</footer>
</div>

<!-- 7. Button bar that goes full-width stacked on mobile, inline on sm+ -->
<div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
  <button type="button" class="rounded border px-4 py-2">Cancel</button>
  <button type="button" class="rounded bg-blue-600 px-4 py-2 text-white">Save</button>
</div>
```

The key classes, in order of how often you need them: `flex`, `items-center`, `justify-between`, `gap-*`, `flex-wrap`, `flex-1`, `shrink-0`, `min-w-0`, `ml-auto`/`mt-auto`, `flex-col` with a `sm:flex-row` upgrade.

## Variations

- **Equal-width children**: `flex-1` on every child (`flex: 1 1 0%`) splits the row evenly regardless of content; `grow` alone (`flex-grow: 1`) distributes only the *leftover* space, so longer content still gets a wider box.
- **Reverse order visually, not in DOM**: `flex-row-reverse` or `order-*` change the painted order only. Keep this for decoration (an image swapping sides), never for controls, because tab order follows the DOM.
- **Vertical centering of a single line of text next to an icon**: `inline-flex items-center gap-1.5` on the link or button, plus `size-4 shrink-0` on the SVG.
- **Space-around without the uneven outer edges**: use `justify-between` with padding on the container, or `gap-*` with `justify-center`; `justify-around` rarely looks right.

## Pitfalls

- **Text that won't truncate in a flex child**: the child needs `min-w-0` (overriding `min-width: auto`) before `truncate` or `overflow-hidden` has any effect. Same for `<pre>` and long URLs.
- **Images and icons getting squashed**: give them `shrink-0`, otherwise the shrink algorithm compresses them when space is tight.
- **Forgetting `flex-wrap`**: a row of 8 tags on a phone overflows the viewport. Any row with an unknown item count needs `flex-wrap`.
- **`h-full` on a card inside a grid that has no height**: `h-full` only works when the parent has a definite height; in Grid, items already stretch, so drop `h-full` and keep `flex flex-col` + `mt-auto`.
- **Using `space-x-*` instead of `gap-*`**: `space-x-*` adds margin to all-but-first children and breaks with `flex-wrap` and `flex-row-reverse`. Prefer `gap-*` everywhere.
- **`justify-center` with overflowing content clips the start**: centered overflow is cut off on both sides and the left part becomes unreachable. Use `justify-start` with `mx-auto` on children or add `overflow-x-auto`.

## Related skills

- `web-css-responsive-grid` for two-dimensional layouts
- `web-nav-responsive-navbar` for a complete header bar with mobile menu
- `web-ui-buttons` for button groups built on these bars
- `web-css-spacing-scale` for choosing gap values
- `web-ui-badges-chips-tags` for the chip row contents
