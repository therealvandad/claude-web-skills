---
name: web-layout-card-grid
description: Build a responsive grid of equal-height cards (blog posts, products, projects, team members) with properly cropped images, consistent text areas and a footer row pinned to the bottom, in Tailwind v4. Use whenever a user asks for a blog index, article list, product grid, portfolio, catalogue, "cards in a grid", gallery with captions or team page.
---

# Card grid

Card grids break in two predictable ways: images of different aspect ratios make rows ragged, and cards with different text lengths leave their "Read more" links at different heights. Fix both at the structure level: a fixed `aspect-ratio` box with `object-cover` for every image, and a flex-column card whose last row is pushed down with `mt-auto`. The grid itself is three lines of Tailwind; everything else is discipline inside the card.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="posts-heading">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <h2 id="posts-heading" class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">From the blog</h2>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Guides and notes on building for the web.</p>
      </div>
      <a href="/blog" class="text-sm font-semibold text-blue-600 hover:text-blue-500">All posts <span aria-hidden="true">&rarr;</span></a>
    </div>

    <ul role="list" class="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3 lg:gap-8">

      <li>
        <article class="group relative flex h-full flex-col overflow-hidden rounded-2xl bg-white ring-1 ring-gray-200 transition-shadow hover:shadow-lg has-[a:focus-visible]:ring-2 has-[a:focus-visible]:ring-blue-600 motion-reduce:transition-none dark:bg-gray-900 dark:ring-gray-800">
          <img src="/img/posts/tailwind-v4.jpg" width="800" height="450" alt="" loading="lazy" decoding="async"
               class="aspect-video w-full object-cover transition-transform group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100">
          <div class="flex flex-1 flex-col p-6">
            <p class="flex items-center gap-2 text-xs text-gray-500">
              <time datetime="2026-10-14">Oct 14, 2026</time>
              <span aria-hidden="true">&middot;</span>
              <span>6 min read</span>
            </p>
            <h3 class="mt-3 text-lg font-semibold text-gray-900 dark:text-white">
              <a href="/blog/tailwind-v4-migration" class="after:absolute after:inset-0 focus-visible:outline-none">
                Moving a static site to Tailwind v4
              </a>
            </h3>
            <p class="mt-2 line-clamp-3 text-sm text-gray-600 dark:text-gray-400">
              What changed, what broke, and the three config lines you actually need. A practical migration log from a real project.
            </p>
            <div class="mt-auto flex items-center gap-2 pt-6">
              <span class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-300">CSS</span>
              <span class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-300">Tailwind</span>
            </div>
          </div>
        </article>
      </li>

      <!-- repeat <li><article> per card -->

    </ul>
  </div>
</section>
```

Why these choices:

- `aspect-video w-full object-cover`: every image occupies the same 16:9 box and is cropped, not squashed. Explicit `width`/`height` still matter for no-CLS before CSS loads.
- `flex h-full flex-col` on the article and `flex-1 flex-col` on the body, then `mt-auto` on the tag row: tags sit at the same baseline in every card regardless of excerpt length.
- `line-clamp-3` caps the excerpt so one verbose post does not stretch its row.
- Clickable card: the only link is the title; its `after:absolute after:inset-0` pseudo-element stretches the hit area over the whole card. Screen readers get one link with a meaningful name instead of "image link, title link, read more link".
- `has-[a:focus-visible]:ring-2` shows the focus ring on the card itself because the link's own outline is removed; keyboard users still see focus.
- `group-hover:scale-[1.03]` on the image inside `overflow-hidden` is the subtle hover cue; `motion-reduce:` cancels it.

## Variations

- **Products**: swap `aspect-video` for `aspect-square`, put price in the `mt-auto` row (`<p class="font-semibold">$24</p>`), and add an "Add to cart" `<button>` with `relative z-10` so it sits above the stretched link.
- **Team members**: `aspect-[3/4]` portrait images, centered text, no stretched link; cards without a destination should not have hover lift.
- **Auto-fit without breakpoints**: `grid-cols-[repeat(auto-fill,minmax(18rem,1fr))]` lets the grid decide column count from available space, handy inside sidebars or containers (see `web-css-container-queries`).
- **Featured first card**: `sm:col-span-2 lg:col-span-2 lg:row-span-2` on the first `<li>` with a larger image; make sure the rest still fill a 3-column grid (1 + 4 = 2 rows).

## Pitfalls

- `h-full` on the article does nothing unless the `<li>` is a grid item (grid stretches items by default); if you wrap the article in an extra `<div>`, add `h-full` to that too.
- A stretched-link overlay with `after:absolute` needs `relative` on the card and makes every other link inside the card unreachable by mouse unless it has `relative z-10`.
- Images with `alt="Blog post thumbnail"` next to a title link add noise; thumbnails that merely illustrate the title should have `alt=""`.
- `loading="lazy"` on the first row of cards above the fold delays their render. Lazy-load from the second row down or use `loading="eager"` on the first three.
- Mixing `gap-6` here and `gap-8` elsewhere on the same page breaks the rhythm; match the gap to the section's spacing scale.
- Card heights still differ when one title wraps to two lines and another to one; either `line-clamp-2` the title or accept it, but do not fix heights in pixels.

## Related skills

- `web-ui-cards`
- `web-layout-feature-grid`
- `web-css-responsive-grid`
- `web-css-aspect-ratio-media`
- `web-css-container-queries`
- `web-perf-images`
- `web-nav-pagination`
