---
name: web-js-router-and-urls
description: Keep UI state in the URL (filters, tabs in query params or hash, shareable and back-button friendly) with URLSearchParams and the History API, plus a minimal client-side router for a single-page section. Use whenever a user says "shareable link to this filter", "back button doesn't work", "sync state with the URL", "pushState", "hash routing", or "SPA router without a framework".
---

# URL state and a minimal router

If a filter, tab or page is not in the URL, it cannot be shared, bookmarked, reloaded or reached with the back button. Two levels: for **state on a normal page** (filters, sort, open tab) write to `URLSearchParams` with `history.replaceState` and read it back on load and on `popstate`; for a **real multi-view section** (docs viewer, admin area) a 40-line router with `pushState` and route patterns is enough. Keep static-site defaults: real `<a href>` links everywhere so the content works with JS off and search engines can crawl it.

## Pattern

### 1. State in query params (filters, sort, pagination)

```html
<form data-js="filters" class="flex flex-wrap gap-3">
  <select name="sort"><option value="new">Newest</option><option value="price">Price</option></select>
  <input name="q" type="search" placeholder="Search" class="rounded border px-2 py-1">
  <label><input type="checkbox" name="instock" value="1"> In stock</label>
</form>
```

```js
// /js/lib/url-state.js
/** Read params as a plain object; checkboxes/absent keys come back undefined. */
export const readParams = () => Object.fromEntries(new URLSearchParams(location.search));

/** Merge into the URL without adding history entries. Empty/false values are removed, keeping URLs clean. */
export function writeParams(patch, { push = false } = {}) {
  const params = new URLSearchParams(location.search);
  for (const [key, value] of Object.entries(patch)) {
    if (value === '' || value == null || value === false) params.delete(key);
    else params.set(key, value);
  }
  const url = `${location.pathname}${params.size ? `?${params}` : ''}${location.hash}`;
  history[push ? 'pushState' : 'replaceState'](null, '', url);
}
```

```js
// /js/features/filters.js
import { readParams, writeParams } from '../lib/url-state.js';
const form = document.querySelector('[data-js="filters"]');

function formToParams() {
  const data = new FormData(form);
  return { sort: data.get('sort'), q: data.get('q')?.trim(), instock: data.has('instock') ? '1' : '' };
}
function paramsToForm(params) {
  form.elements.sort.value = params.sort ?? 'new';
  form.elements.q.value = params.q ?? '';
  form.elements.instock.checked = params.instock === '1';
}

form.addEventListener('input', () => { writeParams(formToParams()); applyFilters(formToParams()); });
form.addEventListener('submit', (e) => e.preventDefault());        // JS off: form GET already yields ?sort=&q=
window.addEventListener('popstate', () => { const p = readParams(); paramsToForm(p); applyFilters(p); });
paramsToForm(readParams()); applyFilters(readParams());            // restore on load / reload / shared link
```

### 2. A minimal client-side router

```html
<nav><a href="/app/" data-link>Home</a> <a href="/app/users/42" data-link>User 42</a></nav>
<main data-js="outlet" aria-live="polite" tabindex="-1"></main>
```

```js
// /js/lib/router.js
export function createRouter({ outlet, routes, notFound }) {
  const compiled = routes.map(({ path, render }) => ({
    pattern: new URLPattern({ pathname: path }),     // '/app/users/:id'
    render,
  }));

  async function navigate(url, { push = true } = {}) {
    const target = new URL(url, location.origin);
    const match = compiled.find((r) => r.pattern.test(target));
    if (push) history.pushState(null, '', target);
    const params = match?.pattern.exec(target)?.pathname.groups ?? {};
    const query = Object.fromEntries(target.searchParams);
    outlet.setAttribute('aria-busy', 'true');
    try {
      await (match ? match.render({ params, query, outlet }) : notFound({ outlet }));
    } finally {
      outlet.setAttribute('aria-busy', 'false');
      outlet.focus({ preventScroll: true });          // screen readers announce the new view
      if (push) window.scrollTo(0, 0);
    }
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-link]');
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return;
    if (link.origin !== location.origin || link.target === '_blank') return;
    event.preventDefault();
    navigate(link.href);
  });
  window.addEventListener('popstate', () => navigate(location.href, { push: false }));
  navigate(location.href, { push: false });
  return { navigate };
}
```

```js
// /js/pages/app.js
import { createRouter } from '../lib/router.js';
createRouter({
  outlet: document.querySelector('[data-js="outlet"]'),
  routes: [
    { path: '/app/', render: ({ outlet }) => { outlet.innerHTML = '<h1>Home</h1>'; } },
    { path: '/app/users/:id', render: async ({ params, outlet }) => {
        const user = await (await fetch(`/api/users/${params.id}`)).json();
        outlet.replaceChildren(Object.assign(document.createElement('h1'), { textContent: user.name }));
        document.title = `${user.name} · App`;
      } },
  ],
  notFound: ({ outlet }) => { outlet.innerHTML = '<h1>Not found</h1>'; },
});
```

## Variations

- **Hash routing** (`#/users/42`) needs no server config and works on GitHub Pages without a fallback: match on `location.hash.slice(1)` and listen to `hashchange` instead of `popstate`; the trade-off is that hashes are not sent to the server or indexed as separate pages.
- **Tabs and accordions**: store the open panel in `#panel-id` with `replaceState` so the hash never pollutes history; see `web-nav-tabs`.
- **Scroll restoration**: set `history.scrollRestoration = 'manual'` and stash `scrollY` in `history.state` before `pushState` if you want back to return to the previous scroll position in a long list.
- **View transitions**: wrap the `render` call in `document.startViewTransition(() => render(...))` when supported; see `web-motion-view-transitions`.

## Pitfalls

- Deep links to `/app/users/42` return 404 on static hosts unless every path is rewritten to the shell page (`_redirects` on Netlify, `vercel.json` rewrites, Cloudflare `_redirects`); see `web-ship-static-hosting`.
- `pushState` on every keystroke floods history; back then steps through each letter. Use `replaceState` for live edits and `pushState` only for deliberate navigation.
- Forgetting `popstate` makes the back button change the URL but not the page, which users read as "broken".
- `URLPattern` is in all evergreen browsers since 2024 but not in older Safari; check `'URLPattern' in window` and fall back to a simple regex (`path.replace(/:(\w+)/g, '(?<$1>[^/]+)')`) if you must support them.
- Rendering with `innerHTML` from route params or API data is XSS; use `textContent` as in the user route.
- Update `document.title` and move focus on every view change; otherwise screen reader and tab-title users get no signal that anything happened.

## Related skills

- `web-nav-tabs`
- `web-nav-pagination`
- `web-motion-view-transitions`
- `web-ship-static-hosting`
- `web-js-state-and-render`
