---
name: web-interactive-filters-url-state
description: Build faceted filtering for a list or grid (checkbox facets, a numeric range, a sort select) where the URL query string is the single source of truth, so filtered views are shareable, reload-safe and back-button friendly. Use whenever a user asks for "filters that update the URL", "shareable filter link", "filter sidebar", "facets", or "back button resets my filters".
---

# Faceted filters with URL state

The right state object for a filter UI is the URL itself: `?type=apartment&type=house&max=2500&sort=price-asc` is shareable, bookmarkable and already serialised. Read the query string into a filter object, derive the rendered list from it, and write it back with `history.pushState` on change. The form is a real `<form method="get">`, so without JavaScript submitting it produces the same URL and a server (or a static page that re-reads the URL on load) can render the same view.

## Pattern

```html
<div data-widget="filters" class="mx-auto grid max-w-6xl gap-6 p-4 lg:grid-cols-[16rem_1fr]">
  <form method="get" data-js="form" class="space-y-6 lg:sticky lg:top-4 lg:self-start" aria-labelledby="filters-title">
    <h2 id="filters-title" class="text-lg font-semibold">Filter listings</h2>
    <fieldset>
      <legend class="text-sm font-medium">Property type</legend>
      <div class="mt-2 space-y-1 text-sm">
        <label class="flex items-center gap-2"><input type="checkbox" name="type" value="apartment" class="accent-indigo-600"> Apartment</label>
        <label class="flex items-center gap-2"><input type="checkbox" name="type" value="house" class="accent-indigo-600"> House</label>
        <label class="flex items-center gap-2"><input type="checkbox" name="type" value="studio" class="accent-indigo-600"> Studio</label>
      </div>
    </fieldset>
    <div>
      <label for="max" class="text-sm font-medium">Max rent: <output data-js="max-out" for="max">€3,000</output></label>
      <input id="max" name="max" type="range" min="500" max="3000" step="50" value="3000" class="mt-2 w-full accent-indigo-600">
    </div>
    <div>
      <label for="sort" class="text-sm font-medium">Sort by</label>
      <select id="sort" name="sort" class="mt-1 w-full rounded-lg border border-gray-300 px-2 py-1.5 dark:border-gray-700 dark:bg-gray-900">
        <option value="newest">Newest</option><option value="price-asc">Rent: low to high</option><option value="price-desc">Rent: high to low</option>
      </select>
    </div>
    <div class="flex gap-2">
      <button class="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white">Apply</button>
      <button type="button" data-js="reset" class="rounded-lg px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800">Clear all</button>
    </div>
  </form>
  <section aria-labelledby="results-title">
    <h2 id="results-title" class="sr-only">Results</h2>
    <p data-js="status" aria-live="polite" class="text-sm text-gray-600 dark:text-gray-400"></p>
    <ul data-js="list" class="mt-3 grid gap-4 sm:grid-cols-2 xl:grid-cols-3"></ul>
  </section>
</div>
```

```js
// /js/filters.js
const listings = [
  { id: 1, title: 'Bright 2-room on Kastanienallee', type: 'apartment', rent: 1450, added: '2026-10-18' },
  { id: 2, title: 'Family house in Pankow with garden', type: 'house', rent: 2800, added: '2026-10-11' },
  { id: 3, title: 'Studio near Ostkreuz', type: 'studio', rent: 890, added: '2026-10-20' },
  { id: 4, title: 'Top-floor loft, Kreuzberg', type: 'apartment', rent: 2150, added: '2026-10-02' },
];
const euro = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
const DEFAULTS = { type: [], max: 3000, sort: 'newest' };

function readFilters(search = location.search) {          // URL -> filter object
  const p = new URLSearchParams(search);
  return { type: p.getAll('type'), max: Number(p.get('max')) || DEFAULTS.max, sort: p.get('sort') || DEFAULTS.sort };
}
function writeFilters(f, { replace = false } = {}) {       // filter object -> URL, omitting defaults
  const p = new URLSearchParams();
  f.type.forEach((t) => p.append('type', t));
  if (f.max !== DEFAULTS.max) p.set('max', f.max);
  if (f.sort !== DEFAULTS.sort) p.set('sort', f.sort);
  const url = p.size ? `${location.pathname}?${p}` : location.pathname;
  history[replace ? 'replaceState' : 'pushState'](null, '', url);
}
function apply(f) {
  const sorters = { newest: (a, b) => b.added.localeCompare(a.added), 'price-asc': (a, b) => a.rent - b.rent, 'price-desc': (a, b) => b.rent - a.rent };
  return listings.filter((l) => (f.type.length === 0 || f.type.includes(l.type)) && l.rent <= f.max).sort(sorters[f.sort]);
}

export function initFilters(root) {
  const form = root.querySelector('[data-js="form"]');
  const list = root.querySelector('[data-js="list"]');
  const status = root.querySelector('[data-js="status"]');
  const maxOut = root.querySelector('[data-js="max-out"]');

  function syncForm(f) {                                   // paint the controls from the filter object
    form.querySelectorAll('[name="type"]').forEach((cb) => { cb.checked = f.type.includes(cb.value); });
    form.elements.max.value = f.max;
    form.elements.sort.value = f.sort;
    maxOut.value = euro.format(f.max);
  }
  function render(f) {
    const rows = apply(f);
    list.replaceChildren(...rows.map(renderCard));
    status.textContent = rows.length ? `${rows.length} of ${listings.length} listings` : 'No listings match. Try raising the max rent.';
  }
  function renderCard(l) {
    const li = document.createElement('li');
    li.className = 'rounded-xl border border-gray-200 p-4 dark:border-gray-800';
    li.innerHTML = `<h3 class="font-medium"></h3><p class="mt-1 text-sm text-gray-600 dark:text-gray-400"></p>`;
    li.children[0].textContent = l.title;
    li.children[1].textContent = `${l.type} · ${euro.format(l.rent)} / month`;
    return li;
  }
  function fromForm() {
    const d = new FormData(form);
    return { type: d.getAll('type'), max: Number(d.get('max')), sort: d.get('sort') };
  }
  const update = () => { const f = fromForm(); writeFilters(f); render(f); };

  form.addEventListener('submit', (e) => { e.preventDefault(); update(); });   // no-JS path still works
  form.addEventListener('change', update);                                     // live update on any control
  form.elements.max.addEventListener('input', () => { maxOut.value = euro.format(form.elements.max.value); });
  root.querySelector('[data-js="reset"]').addEventListener('click', () => { syncForm(DEFAULTS); update(); });
  const onPop = () => { const f = readFilters(); syncForm(f); render(f); };   // back/forward
  window.addEventListener('popstate', onPop);

  const initial = readFilters();
  syncForm(initial); render(initial); writeFilters(initial, { replace: true });
  return () => window.removeEventListener('popstate', onPop);
}

document.querySelectorAll('[data-widget="filters"]').forEach(initFilters);
```

Why this shape: `readFilters` and `writeFilters` are the only code that knows the URL format, and `apply` is a pure function of `(data, filters)`, so you can unit-test both without a DOM. Defaults are omitted from the URL to keep links short and so the untouched page has a clean address.

## Variations

- **Remote data**: replace the `listings` constant with a fetch on init (see `web-data-fetch-and-cache`); for server-side filtering, pass the same `URLSearchParams` to the API and keep `apply` as a no-op.
- **Facet counts**: in `render`, compute how many rows each checkbox would yield if toggled and write it next to the label (`Apartment (12)`); disable options that would give zero.
- **Range with two thumbs**: use two `<input type="range">` for `min` and `max` stacked with `grid [grid-area:1/1]`, clamp so min ≤ max, and serialise both.
- **Mobile drawer**: on small screens wrap the form in a `<dialog>` opened by a "Filters (3)" button that shows the count of active facets; see `web-ui-modal-dialog`.

## Pitfalls

- `pushState` on every `input` event of a range slider floods history with hundreds of entries. Update the `<output>` on `input`, push state only on `change`, or use `replaceState` while dragging.
- Forgetting `popstate` means Back changes the URL but not the list; always re-read the URL and repaint on it, and never store filter state anywhere else.
- Repeated keys (`type=a&type=b`) are the standard encoding for multi-select and `getAll` reads them; do not invent `type=a,b`, it breaks the no-JS form submission.
- Validate what you read from the URL: an unknown `sort` value must fall back to a default or `sorters[f.sort]` is `undefined` and `.sort()` silently does nothing.
- Keep the `aria-live` status short and written once per render; announcing each card is noise.
- `lg:sticky` on the form needs `self-start`, otherwise the grid stretches it to the column height and it never sticks.

## Related skills

- `web-js-router-and-urls`
- `web-js-state-and-render`
- `web-form-choices`
- `web-ecommerce-product-grid-filters`
- `web-ui-modal-dialog`
- `web-data-fetch-and-cache`
