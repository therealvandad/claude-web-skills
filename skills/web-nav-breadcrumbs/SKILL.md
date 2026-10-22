---
name: web-nav-breadcrumbs
description: Build an accessible breadcrumb trail (nav aria-label="Breadcrumb", ordered list, separators as decoration, current page marked, collapses to "…" on narrow screens) with Tailwind v4, plus the matching BreadcrumbList JSON-LD for search engines. Use when a user asks for breadcrumbs, "Home / Products / Item" links, a path indicator, or hierarchy navigation.
---

# Breadcrumbs

Breadcrumbs tell the user where they are in a hierarchy and give one-click access to each ancestor. Mark them up as an ordered list inside `<nav aria-label="Breadcrumb">`, make the separators pure decoration (`aria-hidden`), and mark the last item with `aria-current="page"`. On narrow screens, keep the first and last two items visible and fold the middle into a "…" button that expands the full trail, so long paths never wrap into three lines. Search engines read the same hierarchy from a `BreadcrumbList` JSON-LD block.

## Pattern

```html
<nav aria-label="Breadcrumb" data-breadcrumb class="text-sm">
  <ol class="flex flex-wrap items-center gap-1.5 text-gray-500 dark:text-gray-400">
    <li class="flex items-center gap-1.5">
      <a href="/" class="rounded hover:text-gray-900 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:hover:text-white">Home</a>
    </li>
    <li data-crumb="middle" class="flex items-center gap-1.5">
      <svg class="size-4 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M7.5 5 12.5 10l-5 5"/></svg>
      <a href="/catalog" class="rounded hover:text-gray-900 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:hover:text-white">Catalog</a>
    </li>
    <li data-crumb="middle" class="flex items-center gap-1.5">
      <svg class="size-4 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M7.5 5 12.5 10l-5 5"/></svg>
      <a href="/catalog/furniture" class="rounded hover:text-gray-900 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:hover:text-white">Furniture</a>
    </li>
    <li class="flex items-center gap-1.5">
      <svg class="size-4 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M7.5 5 12.5 10l-5 5"/></svg>
      <a href="/catalog/furniture/chairs" class="rounded hover:text-gray-900 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:hover:text-white">Chairs</a>
    </li>
    <li class="flex items-center gap-1.5">
      <svg class="size-4 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M7.5 5 12.5 10l-5 5"/></svg>
      <span aria-current="page" class="max-w-[14rem] truncate font-medium text-gray-900 dark:text-white">Oak dining chair</span>
    </li>
  </ol>
</nav>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Catalog", "item": "https://example.com/catalog" },
    { "@type": "ListItem", "position": 3, "name": "Furniture", "item": "https://example.com/catalog/furniture" },
    { "@type": "ListItem", "position": 4, "name": "Chairs", "item": "https://example.com/catalog/furniture/chairs" },
    { "@type": "ListItem", "position": 5, "name": "Oak dining chair" }
  ]
}
</script>
```

```js
// breadcrumb.js: collapse middle crumbs below sm into an expandable "…" button
const collapseBreadcrumb = (nav) => {
  const middle = [...nav.querySelectorAll('[data-crumb="middle"]')];
  if (middle.length < 2) return;
  const mq = window.matchMedia('(max-width: 39.99rem)');
  const li = document.createElement('li');
  li.className = 'flex items-center gap-1.5';
  li.innerHTML = `${middle[0].firstElementChild.outerHTML}
    <button type="button" aria-expanded="false" class="rounded px-1 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-blue-600 dark:hover:text-white">
      <span aria-hidden="true">…</span><span class="sr-only">Show all ${middle.length} hidden pages</span>
    </button>`;
  middle[0].before(li);
  const btn = li.querySelector('button');

  const apply = (collapsed) => {
    li.hidden = !collapsed;
    middle.forEach((el) => { el.hidden = collapsed; });
  };
  btn.addEventListener('click', () => { apply(false); middle[0].querySelector('a').focus(); });
  mq.addEventListener('change', () => apply(mq.matches));
  apply(mq.matches);
};
document.querySelectorAll('[data-breadcrumb]').forEach(collapseBreadcrumb);
```

The separator sits inside each `<li>` after the first rather than as a `::before` with text, so copy-paste and screen readers get a clean "Home, Catalog, Furniture" list. The JSON-LD must match the visible trail; the last item has no `item` URL because it is the current page.

## Variations

- **Slash separators in CSS only**: remove the SVGs and add `[&>li+li]:before:mx-1 [&>li+li]:before:content-['/']` to the `<ol>`; generated content is ignored by most screen readers but not all, SVG with `aria-hidden` is the safer choice.
- **Back-link on mobile**: instead of collapsing, show only the parent as "← Chairs" below `sm:` by adding `max-sm:hidden` to all but the second-to-last `<li>`.
- **Icon home**: replace the "Home" text with a house SVG plus `<span class="sr-only">Home</span>`.
- **Generate from the URL**: split `location.pathname`, title-case segments and build `<li>`s; only acceptable when URLs are human-readable and every segment is a real page.

## Pitfalls

- Do not link the current page to itself: use a `<span aria-current="page">`, or if a link is required, keep `aria-current` on the `<a>`.
- `flex-wrap` is intentional; without it long trails overflow horizontally and `truncate` on every crumb makes them unreadable. Truncate only the last one.
- Breadcrumbs show hierarchy, not history. "Back to search results" is a different link; never populate crumbs from `document.referrer`.
- Keep the JSON-LD `position` sequence 1..n with no gaps; the rich result validator rejects gaps.
- A page with breadcrumbs still needs its `<h1>`; breadcrumbs are not a heading.
- When the trail is a child of a sticky header, give it `overflow-x-auto` rather than wrapping so the header height stays fixed.

## Related skills

- `web-seo-structured-data`: the full JSON-LD reference, including validation.
- `web-a11y-skip-links-and-landmarks`: labeling multiple `<nav>` regions.
- `web-seo-content-structure`: URL hierarchy the crumbs should mirror.
- `web-nav-sidebar`: deep hierarchies that need a side tree as well.
