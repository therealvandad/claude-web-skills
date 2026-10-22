---
name: web-page-blog-index
description: 'Build a blog index or post listing page in Tailwind v4: a featured latest post, a category filter that works as links and as client-side filtering, a magazine card grid, pagination and an RSS link. Use whenever a user asks for a blog page, blog home, news page, articles list, "all posts", journal, changelog list or a post archive.'
---

# Blog index page

The index answers "what is new, what is here, how do I find the one I want". So the newest post gets the most space (a featured block at the top, not a card like the others), categories sit where a reader looks before scanning (above the grid, left-aligned), and the grid itself is three-up with a visible date and category on every card. Pagination at the bottom, RSS in the header: the two ways a returning reader keeps up.

## Pattern

```html
<main id="main" class="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8 lg:py-20">

  <!-- 1. Heading row: what this is, plus RSS. Left-aligned with a measure. -->
  <header class="flex flex-wrap items-end justify-between gap-6">
    <div class="max-w-[40rem]">
      <h1 class="text-4xl font-semibold tracking-tight sm:text-5xl">Writing</h1>
      <p class="mt-3 text-lg text-stone-600">Engineering notes, release write-ups and the occasional post-mortem. 142 posts since 2019.</p>
    </div>
    <a href="/blog/feed.xml" class="inline-flex items-center gap-2 text-sm font-medium underline underline-offset-4">RSS feed</a>
  </header>

  <!-- 2. Featured: the latest post at 1.3/1, image on the right so the text keeps the left edge. -->
  <article class="mt-12 grid gap-8 border-t border-stone-200 pt-10 lg:grid-cols-[1.3fr_1fr] lg:items-center">
    <div>
      <p class="font-mono text-xs uppercase tracking-wide text-stone-500">Latest · Engineering · <time datetime="2026-03-14">14 Mar 2026</time></p>
      <h2 class="mt-3 text-3xl font-semibold leading-tight tracking-tight text-balance sm:text-4xl"><a href="/blog/avif-migration" class="hover:underline hover:underline-offset-4">We moved 40,000 product images to AVIF. Here is what broke.</a></h2>
      <p class="mt-4 max-w-[55ch] text-stone-600">Page weight fell 61%. Safari 15 users saw grey boxes for two days. Both were our fault.</p>
      <p class="mt-4 text-sm text-stone-500">Priya Raman · 9 min read</p>
    </div>
    <a href="/blog/avif-migration" tabindex="-1" aria-hidden="true">
      <img src="/img/blog/avif-waterfall.webp" width="1200" height="800" fetchpriority="high" alt="" class="aspect-[3/2] w-full rounded-lg object-cover">
    </a>
  </article>

  <!-- 3. Category filter: real links so it works without JS; JS turns them into instant filters. -->
  <nav aria-label="Categories" class="mt-16 flex flex-wrap gap-2 border-b border-stone-200 pb-4" data-filter>
    <a href="/blog" aria-current="page" data-category="all" class="rounded-full border border-stone-300 px-3 py-1 text-sm aria-[current=page]:border-stone-900 aria-[current=page]:bg-stone-900 aria-[current=page]:text-white">All <span class="text-stone-400 aria-[current=page]:text-stone-300">142</span></a>
    <a href="/blog/engineering" data-category="engineering" class="rounded-full border border-stone-300 px-3 py-1 text-sm hover:border-stone-900 aria-[current=page]:border-stone-900 aria-[current=page]:bg-stone-900 aria-[current=page]:text-white">Engineering <span class="text-stone-400">58</span></a>
    <a href="/blog/releases" data-category="releases" class="rounded-full border border-stone-300 px-3 py-1 text-sm hover:border-stone-900 aria-[current=page]:border-stone-900 aria-[current=page]:bg-stone-900 aria-[current=page]:text-white">Releases <span class="text-stone-400">47</span></a>
    <a href="/blog/company" data-category="company" class="rounded-full border border-stone-300 px-3 py-1 text-sm hover:border-stone-900 aria-[current=page]:border-stone-900 aria-[current=page]:bg-stone-900 aria-[current=page]:text-white">Company <span class="text-stone-400">37</span></a>
  </nav>

  <!-- 4. Grid: category + date visible on every card, headings are the links. -->
  <ul role="list" class="mt-8 grid gap-x-8 gap-y-12 sm:grid-cols-2 lg:grid-cols-3" data-posts>
    <li data-category="releases" class="flex flex-col">
      <a href="/blog/march-release" tabindex="-1" aria-hidden="true"><img src="/img/blog/march-release.webp" width="800" height="500" loading="lazy" alt="" class="aspect-[8/5] w-full rounded-lg object-cover"></a>
      <p class="mt-4 font-mono text-xs uppercase tracking-wide text-stone-500">Releases · <time datetime="2026-03-04">4 Mar</time></p>
      <h3 class="mt-2 text-lg font-semibold leading-snug"><a href="/blog/march-release" class="hover:underline hover:underline-offset-4">March release: bulk export, two new regions, 40% faster search</a></h3>
      <p class="mt-2 line-clamp-2 text-sm text-stone-600">Export up to 50,000 rows as CSV or Parquet, Frankfurt and São Paulo regions, and a rebuilt search index.</p>
    </li>
    <li data-category="engineering" class="flex flex-col">...</li>
    <li data-category="company" class="flex flex-col">...</li>
  </ul>
  <p hidden data-empty class="mt-8 text-stone-600">No posts in this category yet.</p>

  <!-- 5. Pagination: real links, rel hints for crawlers. -->
  <nav aria-label="Pagination" class="mt-16 flex items-center justify-between border-t border-stone-200 pt-6 text-sm">
    <a href="/blog/page/2" rel="next" class="font-medium underline underline-offset-4">Older posts</a>
    <p class="text-stone-500">Page 1 of 12</p>
  </nav>
</main>
```

Client-side filter: intercepts the category links on the current page only, hides cards, updates the URL so a refresh shows the same view.

```js
const filter = document.querySelector('[data-filter]');
const cards = [...document.querySelectorAll('[data-posts] > li')];
const empty = document.querySelector('[data-empty]');

function applyFilter(category) {
  let shown = 0;
  for (const card of cards) {
    const visible = category === 'all' || card.dataset.category === category;
    card.hidden = !visible;
    if (visible) shown++;
  }
  empty.hidden = shown > 0;
  for (const link of filter.querySelectorAll('a')) {
    if (link.dataset.category === category) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }
}

filter.addEventListener('click', (event) => {
  const link = event.target.closest('a[data-category]');
  if (!link) return;
  event.preventDefault();
  applyFilter(link.dataset.category);
  history.replaceState(null, '', link.dataset.category === 'all' ? '/blog' : `/blog?category=${link.dataset.category}`);
});

applyFilter(new URLSearchParams(location.search).get('category') ?? 'all');
```

Meta: `<link rel="alternate" type="application/rss+xml" title="Writing" href="/blog/feed.xml">` in the head, `rel="next"` / `rel="prev"` on pagination links, canonical pointing at the unfiltered page.

## Variations

- **Magazine opener**: replace the featured block with `lg:grid-cols-[2fr_1fr]`: the lead post on the left, a `divide-y` list of the next three posts (title and date only) on the right.
- **Changelog or release notes**: drop the images, make each card a `grid-cols-[6rem_1fr]` row with the version in mono on the left and a `<h3>` plus bullet list on the right.
- **Load more instead of pages**: keep the `rel="next"` link, but let JS fetch the next page's `<ul>` and append its items (see `web-nav-pagination` for the trade-offs).
- **Author or tag page**: the same layout with the heading replaced by the author's photo, name and bio, and the filter removed.

## Pitfalls

- Featuring the first post *and* repeating it in the grid shows it twice above the fold; skip it in the grid.
- Filter chips as `<button>`s only work with JS and give crawlers nothing; links to real category pages are the baseline, JS is the upgrade.
- Hiding cards with `display:none` in a grid with `gap-y-12` is fine; hiding them with `opacity-0` leaves holes.
- `line-clamp-2` on the excerpt is for layout, not for writing: still write excerpts that make sense cut at two lines.
- Equal-height cards that stretch an image to fill (`object-cover` on a fixed `aspect-*`) crop faces; choose the crop or store a focal point.
- Empty filter results with no message look broken; the `[data-empty]` paragraph covers it (see `web-design-empty-and-error-states`).

## Related skills

- `web-layout-card-grid`
- `web-nav-pagination`
- `web-page-blog-post`
- `web-design-empty-and-error-states`
- `web-seo-sitemap-robots-urls`
- `web-js-router-and-urls`
- `web-craft-real-content`
