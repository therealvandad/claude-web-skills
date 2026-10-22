---
name: web-css-container-queries
description: 'Make a component respond to its parent''s width instead of the viewport, using CSS @container and Tailwind v4''s built-in @container / @md: / @lg: variants. Use whenever a card, widget or sidebar panel must work in both a narrow column and full-width, when a user says "responsive component", "this card breaks in the sidebar", or asks about container queries.'
---

# Container queries

Media queries ask "how wide is the viewport?". That is the wrong question for a card that lives in a 3-column grid on one page and a 16rem sidebar on another: the viewport is identical, the available space is not. Container queries ask "how wide is my parent?", so one component carries its own responsive rules and works anywhere it is dropped. Tailwind v4 ships container query variants by default (no plugin): `@container` marks the parent, and `@sm:` `@md:` `@lg:` and friends style children based on that parent's width.

## Pattern

A product card that is a vertical stack when narrow and a horizontal media-object when its container is at least 28rem (Tailwind's `@md` container breakpoint).

```html
<!-- The grid cell is the container. Each card measures its own cell. -->
<ul class="grid gap-6 md:grid-cols-[2fr_1fr]" role="list">
  <li class="@container">
    <article class="flex flex-col overflow-hidden rounded-xl border border-gray-200 @md:flex-row dark:border-gray-700">
      <img
        src="/img/product.jpg" alt="" width="640" height="480"
        class="aspect-video w-full object-cover @md:aspect-square @md:w-48 @md:shrink-0"
      />
      <div class="flex flex-col gap-2 p-4 @md:p-6">
        <h3 class="text-base font-semibold @md:text-lg">Trail Runner 3</h3>
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Lightweight shoe with a grippy outsole. The description wraps as needed.
        </p>
        <div class="mt-auto flex items-center justify-between gap-3 pt-2">
          <span class="font-semibold">$129</span>
          <button type="button" class="rounded-md bg-blue-600 px-3 py-2 text-sm text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
            Add to cart
          </button>
        </div>
      </div>
    </article>
  </li>
  <li class="@container">
    <!-- same card markup; it stays stacked because its column is narrow -->
  </li>
</ul>
```

Tailwind's default container breakpoints: `@3xs` 16rem, `@2xs` 18rem, `@xs` 20rem, `@sm` 24rem, `@md` 28rem, `@lg` 32rem, `@xl` 36rem, `@2xl` 42rem, up to `@7xl` 80rem. Arbitrary: `@min-[30rem]:flex-row`. Max-width: `@max-md:hidden`.

The same thing in plain CSS, when you are not using Tailwind for a component:

```css
.card-wrap { container-type: inline-size; }           /* measure width only */

.card { display: flex; flex-direction: column; }
@container (min-width: 28rem) {
  .card { flex-direction: row; }
  .card img { width: 12rem; aspect-ratio: 1; }
}
```

## Variations

- **Named containers** for nested components: `@container/sidebar` on the parent and `@md/sidebar:grid-cols-2` on a descendant query that specific ancestor, skipping any closer `@container` in between. Plain CSS: `container: sidebar / inline-size;` and `@container sidebar (min-width: 28rem)`.
- **Container units for fluid sizing**: `cqw`, `cqi`, `cqh` are percentages of the container, so `text-[clamp(1rem,4cqi,2rem)]` gives a heading that scales with its card, not the window.
- **Style queries** (`@container style(--variant: compact)`) let a parent flip a child's layout via a custom property; Chromium and Safari support them, Firefox is catching up, so treat as enhancement.
- **Mix with viewport queries** when it genuinely is about the screen: use `md:` for the page grid (how many columns) and `@md:` for what each card does inside its column.

## Pitfalls

- **The container is not the element you style**: `@container` goes on the *parent*; `@md:` goes on *children*. Putting both on the same element does nothing, because an element cannot query its own size (that would be circular).
- **A container cannot size itself from its contents** along the queried axis. `container-type: inline-size` makes the element's inline size independent of its children, so a container with `w-fit` or inside a `flex` row with no width collapses to zero. Give the container a width (`w-full`, a grid track, `flex-1`).
- **Do not make the whole page a container** just to use `@md:` everywhere; wrap each component that needs it. Many large containers add layout cost and hide what is being measured.
- **Grid cells as containers**: the `<li>`/wrapper must be the container, not the `<article>` that you are restyling. The pattern above wraps for exactly this reason.
- **`@container` is also a Tailwind variant prefix name**: the class `@container` sets `container-type: inline-size`; the old v3 `container` class (max-width utility) is unrelated and still exists. Don't confuse them.
- **Arbitrary query classes need no spaces**: `@min-[30rem]:flex-row`, not `@min-[30 rem]`.

## Related skills

- `web-css-responsive-grid` for the outer grid these cards live in
- `web-css-fluid-typography` for `clamp()` and `cqi`-based sizing
- `web-ui-cards` for complete card anatomy
- `web-layout-dashboard-sidebar` where widgets must survive a collapsible sidebar
- `web-css-flexbox-patterns` for the stack-to-row switch itself
