---
name: web-css-responsive-grid
description: 'Build responsive CSS Grid layouts with Tailwind v4: auto-fit/auto-fill columns that reflow without breakpoints, named grid-template-areas for page layouts, and span/placement utilities. Use whenever a user asks for a grid, columns, "cards that wrap", "as many per row as fit", a page layout with sidebar and content, or asks why their grid overflows on mobile.'
---

# Responsive CSS Grid

Grid solves two-dimensional layout: rows *and* columns at once. Reach for it when items must line up in both directions (card grids, dashboards, page shells). Flexbox is for one-dimensional rows or columns (see `web-css-flexbox-patterns`). The two big wins of Grid are **intrinsic responsiveness** (`auto-fit` + `minmax` reflows without a single media query) and **named areas** (rearrange a whole page layout per breakpoint by rewriting one string).

## Pattern

### 1. Auto-fit grid: "as many columns as fit, each at least 16rem"

Tailwind v4 has no built-in `auto-fit` utility, so define it once in `@theme` and then use it like any other `grid-cols-*` class.

```css
@import "tailwindcss";

@theme {
  /* grid-cols-fit  → repeat(auto-fit, minmax(min(16rem, 100%), 1fr)) */
  --grid-template-columns-fit: repeat(auto-fit, minmax(min(16rem, 100%), 1fr));
  --grid-template-columns-fill: repeat(auto-fill, minmax(min(16rem, 100%), 1fr));
}
```

```html
<ul class="grid grid-cols-fit gap-6" role="list">
  <li class="rounded-xl border border-gray-200 p-6 dark:border-gray-700">Card 1</li>
  <li class="rounded-xl border border-gray-200 p-6 dark:border-gray-700">Card 2</li>
  <li class="rounded-xl border border-gray-200 p-6 dark:border-gray-700">Card 3</li>
  <li class="rounded-xl border border-gray-200 p-6 dark:border-gray-700">Card 4</li>
</ul>
```

Why `min(16rem, 100%)`: on a 320px-wide phone, a plain `minmax(16rem, 1fr)` forces a 256px minimum *plus* padding and can overflow. Wrapping it in `min(…, 100%)` caps the minimum at the container width.

One-off without `@theme`: `grid-cols-[repeat(auto-fit,minmax(min(16rem,100%),1fr))]`.

### 2. Breakpoint grid with spans (explicit control)

```html
<section class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
  <article class="sm:col-span-2 lg:col-span-2 lg:row-span-2">Featured</article>
  <article>Item</article>
  <article>Item</article>
  <article class="lg:col-span-2">Wide item</article>
  <article>Item</article>
</section>
```

### 3. Named areas for a page shell (header, nav, main, aside, footer)

```html
<style>
  .shell {
    display: grid;
    gap: 1rem;
    grid-template-areas:
      "header"
      "nav"
      "main"
      "aside"
      "footer";
    grid-template-columns: minmax(0, 1fr);
  }
  @media (min-width: 64rem) {              /* matches Tailwind lg */
    .shell {
      grid-template-columns: 14rem minmax(0, 1fr) 18rem;
      grid-template-rows: auto 1fr auto;
      grid-template-areas:
        "header header header"
        "nav    main   aside"
        "footer footer footer";
      min-height: 100dvh;
    }
  }
</style>

<div class="shell">
  <header class="[grid-area:header] border-b p-4">Header</header>
  <nav class="[grid-area:nav] p-4" aria-label="Primary">Nav</nav>
  <main class="[grid-area:main] p-4">Main</main>
  <aside class="[grid-area:aside] p-4">Aside</aside>
  <footer class="[grid-area:footer] border-t p-4">Footer</footer>
</div>
```

Areas keep the DOM in reading order (header, nav, main, aside, footer) while visually rearranging per breakpoint. Screen readers and keyboard users still get a sensible order.

## Variations

- **`auto-fill` vs `auto-fit`**: `auto-fit` stretches the last row's items to fill the track; `auto-fill` keeps empty ghost tracks so 2 cards in a 4-wide space stay card-sized. Use `grid-cols-fill` (defined above) for product grids where you don't want one lonely item stretching across the whole row.
- **Equal-height rows**: Grid items stretch by default (`align-items: stretch`). To make the *content* fill too, give each card `flex flex-col` and push the footer with `mt-auto`.
- **Dense packing**: add `grid-flow-dense` (`grid-auto-flow: dense`) to let small items backfill gaps left by spanning items; order on screen then differs from DOM order, so avoid it for content where sequence matters.
- **Subgrid for aligned card internals**: `grid-rows-[subgrid] row-span-3` on each card lets the title, body and button rows align across all cards in a row. Supported in all current browsers.

## Pitfalls

- **`1fr` is really `minmax(auto, 1fr)`**: long unbreakable content (URLs, `<pre>`, wide images) will blow the column out. Use `minmax(0, 1fr)` or put `min-w-0` on the item. This is the number one "my grid overflows" cause.
- **Don't nest `grid-cols-*` on children with `w-full` hacks**: a child of a grid already fills its track; adding widths causes double-counting with `gap`.
- **Fixed-pixel column counts on mobile**: `grid-cols-3` with no `sm:` prefix squeezes three columns onto a phone. Start from `grid-cols-1` and add columns upward.
- **`gap` is not margin**: `gap-6` only spaces between tracks; outer spacing still needs padding on the container.
- **Placing items with `col-start-*` and `row-start-*` across many breakpoints gets unreadable fast**: switch to `grid-template-areas` as soon as you have more than two placed items.
- **Arbitrary-value classes can't contain spaces**: write `grid-cols-[repeat(auto-fit,minmax(16rem,1fr))]` with no spaces, or use `_` for a space; the `@theme` approach avoids this entirely.

## Related skills

- `web-css-flexbox-patterns` for one-dimensional rows and bars
- `web-layout-card-grid` and `web-layout-feature-grid` for finished card grids
- `web-layout-dashboard-sidebar` and `web-layout-page-shell` for full app and page shells
- `web-css-container-queries` when the grid should respond to its container, not the viewport
- `web-css-spacing-scale` for choosing gap sizes
