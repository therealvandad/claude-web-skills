---
name: web-nav-pagination
description: Build pagination controls (previous/next, numbered pages with ellipsis windowing, current page marked, generated from a page count) and a "load more" button with fetch, plus guidance on when infinite scroll is worth it. Use when a user asks for pagination, page numbers, "next/previous", "load more", infinite scroll, or splitting a long list into pages.
---

# Pagination, load more, infinite scroll

Numbered pagination is the right default for anything a user may want to return to, share or scan (search results, catalogs, tables): every page has a URL, the footer is reachable, and the back button works. "Load more" is a good compromise for feeds where position matters less. Infinite scroll only wins for endless, low-stakes streams and costs you the footer, reachable focus order and memory. All three share the same server contract: `?page=N` (or a cursor) returns a slice plus a total.

## Pattern

```html
<nav aria-label="Pagination" data-pagination data-total="12" data-current="5" class="flex justify-center">
  <!-- Static fallback, replaced by the generator; keep it correct for no-JS and crawlers -->
  <ul class="flex items-center gap-1 text-sm">
    <li><a href="?page=4" rel="prev" class="rounded-md px-3 py-2 hover:bg-gray-100">Previous</a></li>
    <li><a href="?page=6" rel="next" class="rounded-md px-3 py-2 hover:bg-gray-100">Next</a></li>
  </ul>
</nav>
```

```js
// pagination.js: renders a window of page links around the current page: 1 … 4 5 6 … 12
const LINK = 'inline-flex min-w-10 items-center justify-center rounded-md px-3 py-2 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:hover:bg-gray-800';
const CURRENT = 'inline-flex min-w-10 items-center justify-center rounded-md bg-blue-600 px-3 py-2 font-semibold text-white';
const DISABLED = 'inline-flex items-center rounded-md px-3 py-2 text-gray-400 dark:text-gray-600';

const pageHref = (n) => { const u = new URL(location.href); u.searchParams.set('page', n); return u.pathname + u.search; };

const pageWindow = (current, total, around = 1) => {
  const pages = new Set([1, total]);
  for (let i = current - around; i <= current + around; i++) if (i >= 1 && i <= total) pages.add(i);
  const sorted = [...pages].sort((a, b) => a - b);
  return sorted.flatMap((p, i) => (i && p - sorted[i - 1] > 1 ? ['…', p] : [p]));
};

const renderPagination = (nav) => {
  const total = Number(nav.dataset.total);
  const current = Number(nav.dataset.current);
  const item = (inner) => `<li>${inner}</li>`;
  const link = (n, label = n, rel = '') =>
    `<a href="${pageHref(n)}" ${rel && `rel="${rel}"`} class="${LINK}" ${label !== n ? '' : `aria-label="Page ${n}"`}>${label}</a>`;

  const items = [
    current > 1 ? link(current - 1, 'Previous', 'prev') : `<span class="${DISABLED}" aria-disabled="true">Previous</span>`,
    ...pageWindow(current, total).map((p) =>
      p === '…' ? `<span class="px-2 text-gray-400" aria-hidden="true">…</span>`
      : p === current ? `<span class="${CURRENT}" aria-current="page" aria-label="Page ${p}">${p}</span>`
      : link(p)),
    current < total ? link(current + 1, 'Next', 'next') : `<span class="${DISABLED}" aria-disabled="true">Next</span>`,
  ];
  nav.innerHTML = `<ul class="flex flex-wrap items-center gap-1 text-sm">${items.map(item).join('')}</ul>`;
};
document.querySelectorAll('[data-pagination]').forEach(renderPagination);
```

Load more, same list, appended with `fetch`:

```html
<ul id="list" class="divide-y divide-gray-200 dark:divide-gray-800">…first page items…</ul>
<div class="mt-4 flex justify-center">
  <button type="button" data-load-more data-next="/api/items?page=2" aria-controls="list"
    class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 dark:border-gray-700 dark:hover:bg-gray-900">Load more</button>
</div>
<p class="sr-only" aria-live="polite" data-load-status></p>
```

```js
const btn = document.querySelector('[data-load-more]');
const status = document.querySelector('[data-load-status]');
btn?.addEventListener('click', async () => {
  btn.disabled = true; btn.textContent = 'Loading…';
  try {
    const res = await fetch(btn.dataset.next, { headers: { Accept: 'text/html' } });
    if (!res.ok) throw new Error(res.statusText);
    const { html, next, added } = await res.json(); // server returns rendered <li>s + next URL
    const list = document.getElementById(btn.getAttribute('aria-controls'));
    const first = list.children.length;
    list.insertAdjacentHTML('beforeend', html);
    list.children[first]?.querySelector('a, button')?.focus(); // move focus to the first new item
    status.textContent = `${added} more items loaded`;
    if (next) { btn.dataset.next = next; btn.disabled = false; btn.textContent = 'Load more'; }
    else btn.replaceWith(Object.assign(document.createElement('p'), { textContent: 'You have seen everything.', className: 'text-sm text-gray-500' }));
  } catch { btn.disabled = false; btn.textContent = 'Retry'; }
});
```

## Variations

- **Compact mobile**: render only Previous, "5 of 12", Next below `sm:` by hiding numbered items with `max-sm:hidden` and adding a `<li class="sm:hidden">` summary.
- **Infinite scroll**: wrap the load-more click in an `IntersectionObserver` on a sentinel `<div>` just above the button, keep the button as the fallback, stop auto-loading after ~3 pages and require a click so the footer stays reachable.
- **Cursor-based**: replace `?page=N` with `?after=<cursor>`; numbered links are then impossible, use prev/next only.
- **Page size selector**: a `<select name="per_page">` inside a `<form method="get">` that keeps other query params as hidden inputs.

## Pitfalls

- The current page is a `<span aria-current="page">`, not a link to itself; Previous/Next at the ends are spans with `aria-disabled`, not links with `href="#"`.
- Always render real `href`s with the full query string preserved (`pageHref` uses `URL`), so sorting and filters survive page changes and crawlers can follow them.
- After "load more", move focus to the first new item and announce via `aria-live`; otherwise keyboard and screen-reader users land at the end of the list with no cue.
- Infinite scroll with a sticky footer or a footer with links is a contradiction: the footer is never reachable. Cap auto-loads.
- Touch targets: `min-w-10` keeps each page link at least 40px wide; single-digit links are otherwise too narrow.
- `rel="prev"` / `rel="next"` are harmless and help some crawlers; do not add `<link rel="canonical">` pointing all pages at page 1.

## Related skills

- `web-js-fetch-and-apis`: error handling and timeouts for the load-more request.
- `web-ui-data-table`: paginating tables.
- `web-js-router-and-urls`: query-string state helpers.
- `web-ui-skeleton-and-loading`: loading placeholders while pages fetch.
