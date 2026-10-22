---
name: web-ui-cards
description: 'Build card components with Tailwind: media, body, meta and actions anatomy; equal-height cards in a grid; the accessible "whole card is clickable" pattern that keeps one real link; horizontal and compact variants. Use whenever a user asks for a card, tile, post preview, product card, profile card, info box, or a "clickable card".'
---

# Cards

A card is a bordered or elevated container that groups one thing: an image, a title, a line or two of text, some metadata, and an action. The design pitfalls are subtle: text that is not vertically aligned across a row, images that stretch, and the "clickable card" that becomes a 400-character link name for screen readers or a `<div onclick>` that keyboards cannot reach. The pattern below solves all three: flex-column body with `mt-auto` footer, fixed aspect ratio media, and a single real `<a>` whose hit area is stretched with a pseudo-element.

## Pattern

```html
<ul class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3" role="list">
  <li>
    <article class="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white
                    transition-shadow hover:shadow-lg focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2
                    motion-reduce:transition-none dark:border-gray-800 dark:bg-gray-900 dark:ring-offset-gray-950">
      <img src="/img/post-1.jpg" alt="" width="640" height="360" loading="lazy"
        class="aspect-video w-full object-cover transition-transform duration-300 group-hover:scale-[1.03] motion-reduce:transition-none">

      <div class="flex flex-1 flex-col p-5">
        <p class="text-xs font-medium uppercase tracking-wide text-indigo-600 dark:text-indigo-400">Engineering</p>
        <h3 class="mt-2 text-lg font-semibold leading-snug text-gray-900 dark:text-gray-100">
          <!-- The one real link. after:absolute after:inset-0 stretches its hit area over the whole card. -->
          <a href="/blog/scroll-snap-carousels" class="after:absolute after:inset-0 focus:outline-none">
            Building carousels with scroll-snap
          </a>
        </h3>
        <p class="mt-2 line-clamp-3 text-sm text-gray-600 dark:text-gray-400">
          Native scrolling, snap points and a sprinkle of JavaScript beat any slider library on size and accessibility.
        </p>

        <footer class="mt-auto flex items-center justify-between pt-5 text-sm text-gray-500">
          <div class="flex items-center gap-2">
            <img src="/img/avatar.jpg" alt="" width="32" height="32" class="size-8 rounded-full">
            <span>Sam Rivera</span>
          </div>
          <time datetime="2026-10-18">18 Oct</time>
        </footer>
      </div>

      <!-- Secondary action sits above the stretched link (z-10) so it stays clickable -->
      <button type="button" aria-label="Save article" class="absolute right-3 top-3 z-10 rounded-full bg-white/90 p-2 text-gray-700 shadow hover:bg-white focus-visible:outline-2 focus-visible:outline-indigo-600 dark:bg-gray-900/90 dark:text-gray-200">
        <svg class="size-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M5 3a2 2 0 0 0-2 2v12.5a.5.5 0 0 0 .8.4L10 13.5l6.2 4.4a.5.5 0 0 0 .8-.4V5a2 2 0 0 0-2-2H5Z"/></svg>
      </button>
    </article>
  </li>
  <!-- more <li> cards -->
</ul>
```

Why this shape: the `<a>` wraps only the title, so its accessible name is the title, yet `after:absolute after:inset-0` on it (inside a `relative` card) makes the entire card its click target. Focus is shown on the card via `focus-within:ring-2` rather than on the invisible pseudo-element. `flex h-full flex-col` plus `flex-1` on the body and `mt-auto` on the footer align footers across a row even when descriptions differ in length. `line-clamp-3` caps the description so cards do not balloon.

## Variations

- **Horizontal card** (list view): `class="flex flex-col sm:flex-row"` on the article, `sm:w-48 sm:aspect-auto` on the image, and the body keeps `flex-1`.
- **Elevated instead of bordered**: drop `border` and use `shadow-sm hover:shadow-md`; in dark mode prefer a lighter surface (`dark:bg-gray-800`) over bigger shadows, which vanish on dark backgrounds.
- **Product card**: image `aspect-square`, price in `<p class="font-semibold tabular-nums">`, and an "Add to cart" `<button>` with `z-10` in the footer; the stretched link goes to the product page, the button does not navigate.
- **Stat / KPI card**: no media; `<dl>` with `<dt class="text-sm text-gray-500">` and `<dd class="text-3xl font-bold tabular-nums">`. Not clickable; no stretched link.
- **Selectable card** (choose a plan): wrap in `<label>` with a hidden radio, style with `has-[:checked]:ring-2 has-[:checked]:ring-indigo-600`; see `web-form-choices`.

## Pitfalls

- Do not make the whole card an `<a>`: its accessible name becomes every word inside, nested interactive elements are invalid HTML, and copying text becomes a drag. One link, stretched, is the standard.
- `onclick` on a `<div>` is not keyboard-focusable and announces nothing; if you must, add `tabindex="0"`, `role="link"` and a keydown handler, but the stretched-link approach needs none of that.
- Any secondary control inside the card (save button, author link) needs `relative z-10` (or `z-10` with `absolute`), otherwise the stretched pseudo-element covers it.
- `h-full` on the article only works if the grid item (`<li>`) stretches; grid items stretch by default, flex items need `items-stretch`.
- Always give images explicit `width` and `height` plus `object-cover` so the grid does not shift as images load and portrait photos do not distort.
- `line-clamp` hides content; make sure the full text is reachable on the target page, and never clamp the title.
- `focus:outline-none` on the link is safe only because the card shows `focus-within:ring`; remove one and you must restore the other.

## Related skills

- `web-layout-card-grid`
- `web-ui-badges-chips-tags`
- `web-design-shadows-and-elevation`
- `web-a11y-keyboard-and-focus`
- `web-motion-hover-microinteractions`
