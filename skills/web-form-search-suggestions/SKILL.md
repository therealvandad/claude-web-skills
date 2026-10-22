---
name: web-form-search-suggestions
description: 'Build a site search box with live suggestions: a form that works without JS, a debounced fetch with AbortController, a suggestion listbox with arrow-key and Enter selection, aria-activedescendant, result-count announcements, and highlighted matches. Use whenever a user asks for "search with suggestions", "autocomplete search", "typeahead", "search as you type", "instant search", or "a search bar for the header".'
---

# Search with suggestions

Start from a form that submits to a results page, then enhance it. Suggestions are a convenience, not the only path, so a failed fetch or no JS must still leave a working search. The enhancement follows the ARIA combobox pattern (`aria-autocomplete="list"`, `aria-activedescendant`) with two network rules: debounce keystrokes (200 to 300 ms) so you do not fire a request per letter, and abort the previous request when a new one starts so a slow response for "ca" cannot overwrite the results for "cat". Every DOM update goes through `textContent` or `createElement`; suggestion strings come from a server and must never be inserted as HTML.

## Pattern

```html
<form role="search" action="/search" method="get" class="relative w-full max-w-md" data-search>
  <label for="q" class="sr-only">Search</label>
  <div class="relative">
    <svg class="pointer-events-none absolute inset-y-0 left-3 my-auto size-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 1 0 3.3 9.9l3.6 3.6a.75.75 0 1 0 1.1-1.1l-3.6-3.6A5.5 5.5 0 0 0 9 3.5ZM5 9a4 4 0 1 1 8 0 4 4 0 0 1-8 0Z" clip-rule="evenodd"/>
    </svg>
    <input id="q" name="q" type="search" placeholder="Search docs…" autocomplete="off" spellcheck="false"
      role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="q-list" aria-haspopup="listbox"
      class="block w-full rounded-full border border-gray-300 bg-white py-2 pr-4 pl-10 text-base text-gray-900 shadow-sm
             focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
             dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 [&::-webkit-search-cancel-button]:appearance-none">
  </div>
  <ul id="q-list" role="listbox" aria-label="Suggestions" hidden
    class="absolute z-20 mt-2 w-full overflow-hidden rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-900"></ul>
  <p class="sr-only" aria-live="polite" data-status></p>
</form>
```

```js
function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

function initSearch(form) {
  const input = form.querySelector('[role=combobox]');
  const list = form.querySelector('[role=listbox]');
  const status = form.querySelector('[data-status]');
  let controller = null;
  let items = [];
  let active = -1;

  function setOpen(open) {
    list.hidden = !open;
    input.setAttribute('aria-expanded', String(open));
    if (!open) highlight(-1);
  }

  function highlight(i) {
    const options = list.querySelectorAll('[role=option]');
    options.forEach((o) => o.removeAttribute('aria-selected'));
    active = i;
    const opt = options[i];
    if (opt) opt.setAttribute('aria-selected', 'true');
    input.setAttribute('aria-activedescendant', opt ? opt.id : '');
  }

  function render(query) {
    list.replaceChildren(...items.map((item, i) => {
      const li = document.createElement('li');
      li.id = `q-opt-${i}`;
      li.setAttribute('role', 'option');
      li.dataset.url = item.url;
      li.className = 'cursor-default px-4 py-2 text-sm text-gray-900 aria-selected:bg-blue-600 aria-selected:text-white dark:text-gray-100';
      const idx = item.title.toLowerCase().indexOf(query.toLowerCase());
      if (idx === -1) li.textContent = item.title;
      else {                                                     // bold the matched substring, safely
        const mark = Object.assign(document.createElement('mark'), { textContent: item.title.slice(idx, idx + query.length),
          className: 'bg-transparent font-semibold text-inherit' });
        li.append(item.title.slice(0, idx), mark, item.title.slice(idx + query.length));
      }
      return li;
    }));
    setOpen(items.length > 0);
    status.textContent = items.length ? `${items.length} suggestions. Use up and down arrows to review.` : 'No suggestions.';
  }

  const fetchSuggestions = debounce(async (query) => {
    controller?.abort();
    controller = new AbortController();
    try {
      const res = await fetch(`/api/suggest?q=${encodeURIComponent(query)}`, { signal: controller.signal });
      if (!res.ok) throw new Error(res.statusText);
      items = (await res.json()).slice(0, 8);
      render(query);
    } catch (err) {
      if (err.name !== 'AbortError') { items = []; setOpen(false); }   // fail quietly: plain submit still works
    }
  }, 250);

  input.addEventListener('input', () => {
    const q = input.value.trim();
    if (q.length < 2) { controller?.abort(); items = []; setOpen(false); return; }
    fetchSuggestions(q);
  });

  input.addEventListener('keydown', (e) => {
    const n = items.length;
    if (list.hidden && e.key !== 'ArrowDown') return;
    if (e.key === 'ArrowDown') { e.preventDefault(); if (list.hidden && n) setOpen(true); highlight((active + 1) % n); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); highlight((active - 1 + n) % n); }
    else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); location.href = items[active].url; }
    else if (e.key === 'Escape') { e.preventDefault(); setOpen(false); }
  });

  list.addEventListener('mousedown', (e) => e.preventDefault());
  list.addEventListener('click', (e) => { const opt = e.target.closest('[role=option]'); if (opt) location.href = opt.dataset.url; });
  input.addEventListener('blur', () => setOpen(false));
}

document.querySelectorAll('[data-search]').forEach(initSearch);
```

Why these choices: `role="search"` on the form is a landmark screen-reader users can jump to. `type="search"` gives mobile keyboards a Search key and Escape-clears on desktop; the `::-webkit-search-cancel-button` reset removes the mismatched native X. A 2-character minimum stops a request on the first keystroke. Enter with no highlighted option falls through to the native submit, so the user lands on the full results page. `mousedown` + `preventDefault` on the list keeps focus in the input so the `blur` close does not race the click.

## Variations

- **Recent searches** when the field is empty: on `focus`, read an array from `localStorage`, render it with a "Recent" heading row (`role="presentation"`), and save each submitted query.
- **Grouped results** (Docs / Blog / API): make the API return `{ group, title, url }`, render a non-selectable `<li role="presentation" class="px-4 pt-2 text-xs font-semibold uppercase text-gray-500">` before each group, and keep `items` flat for arrow navigation.
- **Header search that expands**: show only the icon as a `<button>` on mobile, which toggles a full-width overlay form with the input autofocused; see `web-nav-responsive-navbar`.
- **Keyboard shortcut**: `document.addEventListener('keydown', e => { if (e.key === '/' && !/input|textarea/i.test(e.target.tagName)) { e.preventDefault(); input.focus(); } })`, and show the hint `<kbd>/</kbd>` inside the field on `md:` screens.

## Pitfalls

- Inserting suggestion text with `innerHTML` to bold matches is an XSS hole; build nodes as above.
- Without `AbortController`, responses arrive out of order and the list flickers to stale results. Also ignore `AbortError` or every keystroke logs an error.
- Debounce only the fetch, not the keystroke handling; clearing the list when the query drops below the minimum must happen immediately.
- `autocomplete="off"` on a `type="search"` input is needed or the browser's own history dropdown stacks on top of yours.
- The listbox must be a sibling positioned under the input with `absolute` and a `z-*` above the page header; inside a header with `overflow-hidden` it is clipped.
- Hard limit the rendered items (8 here); long lists are slow to arrow through and announce poorly.

## Related skills

- `web-form-select-and-combobox`
- `web-js-events-debounce-throttle`
- `web-js-fetch-and-apis`
- `web-nav-responsive-navbar`
- `web-a11y-aria-patterns`
- `web-form-input-states`
