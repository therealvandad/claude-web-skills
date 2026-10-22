---
name: web-js-events-debounce-throttle
description: Write correct event handling in vanilla JavaScript - delegation, `debounce` and `throttle` helpers, passive and once listeners, AbortController cleanup, custom events, and keyboard handling. Use whenever a user says "search as you type fires too often", "scroll handler is laggy", "resize event", "remove event listeners", "click handler on dynamic elements", or "memory leak from listeners".
---

# Events: delegate, rate-limit, clean up

Three habits cover most event bugs. **Delegate** one listener on a stable ancestor instead of one per child, so dynamically added elements just work. **Rate-limit** anything driven by `input`, `scroll`, `resize` or `pointermove`: debounce when you want the final value (search), throttle when you want steady updates (scroll position). **Clean up** with an `AbortController` so a widget can remove every listener it added in one call, which matters as soon as content is swapped without a page load.

## Pattern

```html
<label for="q" class="sr-only">Search</label>
<input id="q" type="search" data-js="search" class="w-full rounded border px-3 py-2" placeholder="Search…" autocomplete="off">
<p data-js="search-status" role="status" class="text-sm text-gray-500"></p>
<ul data-js="results" class="divide-y"></ul>
<button type="button" data-js="to-top" class="fixed bottom-4 right-4 rounded-full bg-gray-900 p-3 text-white" hidden>↑</button>
```

```js
// /js/timing.js
/** Run `fn` once `wait` ms have passed with no new call. Last arguments win. */
export function debounce(fn, wait = 250) {
  let timer;
  const debounced = (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), wait); };
  debounced.cancel = () => clearTimeout(timer);
  return debounced;
}

/** Run `fn` at most once per `wait` ms, with a trailing call so the last value is not lost. */
export function throttle(fn, wait = 100) {
  let last = 0, timer, pending;
  return (...args) => {
    const now = Date.now();
    pending = args;
    if (now - last >= wait) { last = now; fn(...pending); }
    else if (!timer) timer = setTimeout(() => { timer = null; last = Date.now(); fn(...pending); }, wait - (now - last));
  };
}

/** Coalesce to one call per animation frame; ideal for scroll/pointermove that touches the DOM. */
export function rafThrottle(fn) {
  let frame;
  return (...args) => { if (!frame) frame = requestAnimationFrame(() => { frame = null; fn(...args); }); };
}
```

```js
// /js/search.js
import { debounce, rafThrottle } from './timing.js';

export function initSearch(root = document) {
  const controller = new AbortController();              // one signal, many listeners
  const { signal } = controller;
  const input = root.querySelector('[data-js="search"]');
  const status = root.querySelector('[data-js="search-status"]');
  const results = root.querySelector('[data-js="results"]');
  const toTop = root.querySelector('[data-js="to-top"]');
  let request;

  const search = debounce(async (query) => {
    request?.abort();
    if (query.length < 2) { results.replaceChildren(); status.textContent = ''; return; }
    request = new AbortController();
    status.textContent = 'Searching…';
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`, { signal: request.signal });
      const items = await res.json();
      results.replaceChildren(...items.map((t) => Object.assign(document.createElement('li'), { textContent: t })));
      status.textContent = `${items.length} result${items.length === 1 ? '' : 's'}`;
    } catch (e) {
      if (e.name !== 'AbortError') status.textContent = 'Search failed.';
    }
  }, 300);

  input.addEventListener('input', () => search(input.value.trim()), { signal });
  input.addEventListener('keydown', (e) => { if (e.key === 'Escape') { input.value = ''; search.cancel(); results.replaceChildren(); } }, { signal });

  // delegation: works for results added later
  results.addEventListener('click', (e) => {
    const li = e.target.closest('li');
    if (li) results.dispatchEvent(new CustomEvent('result:pick', { bubbles: true, detail: { text: li.textContent } }));
  }, { signal });

  // scroll: passive (never calls preventDefault) + one DOM write per frame
  window.addEventListener('scroll', rafThrottle(() => { toTop.hidden = window.scrollY < 400; }), { passive: true, signal });
  toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }), { signal });

  return () => { controller.abort(); search.cancel(); request?.abort(); };   // teardown removes everything
}

const destroy = initSearch();
document.addEventListener('result:pick', (e) => console.log('picked', e.detail.text));
window.addEventListener('pagehide', destroy, { once: true });
```

## Variations

- **Resize**: prefer `ResizeObserver` on the element you care about over `window.resize`; it fires only when that box changes and is already batched per frame. Use `matchMedia('(min-width: 768px)').addEventListener('change', …)` for breakpoint flips.
- **Scroll position effects** (reveal, spy): `IntersectionObserver` beats a throttled scroll listener on both battery and accuracy; see `web-motion-scroll-reveal` and `web-nav-scroll-spy-toc`.
- **Leading-edge debounce** (fire immediately, then ignore for `wait`): good for "save" buttons to stop double submits; add a `leading` flag that calls `fn` when no timer is pending.
- **One-shot**: `{ once: true }` auto-removes after the first call (first interaction, `load`, `transitionend`).

## Pitfalls

- A debounced function created inside the handler is a new function every time, so it never debounces. Create it once, outside.
- Wheel and touch listeners without `{ passive: true }` block scrolling until your handler returns; Chrome warns about this in the console.
- Adding a listener in a function that runs on every render stacks duplicates; the same handler then fires N times. Delegate once at init, or clean up with the signal.
- Arrow functions as listeners cannot be removed by reference later; keep the reference or, better, use the `signal` option.
- `e.target` may be a child (`<svg>` inside a button). Always `closest('[data-action]')`, never compare `e.target` to the element.
- Keyboard: `click` already fires for Enter/Space on real `<button>`s. Only `<div>`s need manual key handling, which is a sign you should have used a button.

## Related skills

- `web-js-dom-utilities`
- `web-form-search-suggestions`
- `web-motion-scroll-reveal`
- `web-nav-sticky-header`
- `web-js-fetch-and-apis`
