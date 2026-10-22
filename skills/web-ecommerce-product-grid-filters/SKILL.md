---
name: web-ecommerce-product-grid-filters
description: Build a shop catalogue page in Tailwind v4: a product grid from JSON, category checkboxes, a price range, sort by price or newest, a live count, filter state in the URL and an empty state, in vanilla JS. Use whenever a user asks for a shop page, product listing, collection page, "filter products", "sort by price" or a catalogue grid.
---

# Product grid with filters and sort

A catalogue page is a list plus three questions: which kind, how much, in what order. Keep the answers in the URL (`?cat=coffee&max=20&sort=price-asc`) so a filtered view can be reloaded, shared and found by search; render the grid from a JSON array with prices as integer cents so filtering and sorting are plain number comparisons. Filters live in a `<form>` with real checkboxes and a `<select>`: they work without JS as a GET form, and with JS they apply on `change` without a reload. A count in a live region tells screen reader users that something happened.

## Pattern

```html
<main id="main" class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
  <h1 class="text-3xl font-semibold tracking-tight">Coffee and brewing gear</h1>
  <div class="mt-8 grid gap-8 lg:grid-cols-[14rem_1fr]">

    <form method="get" data-filters class="space-y-6 text-sm" aria-label="Filter products">
      <fieldset>
        <legend class="font-medium">Category</legend>
        <div class="mt-2 space-y-1.5">
          <label class="flex items-center gap-2"><input type="checkbox" name="cat" value="coffee" class="accent-stone-900"> Coffee <span class="text-stone-500" data-count-for="coffee"></span></label>
          <label class="flex items-center gap-2"><input type="checkbox" name="cat" value="brewing" class="accent-stone-900"> Brewing gear <span class="text-stone-500" data-count-for="brewing"></span></label>
          <label class="flex items-center gap-2"><input type="checkbox" name="cat" value="cups" class="accent-stone-900"> Cups <span class="text-stone-500" data-count-for="cups"></span></label>
        </div>
      </fieldset>
      <fieldset>
        <legend class="font-medium">Price up to</legend>
        <input type="range" name="max" min="5" max="100" step="5" value="100" class="mt-2 w-full accent-stone-900" aria-describedby="max-out">
        <output id="max-out" for="max" class="block tabular-nums text-stone-600">100 €</output>
      </fieldset>
      <label class="block">Sort by
        <select name="sort" class="mt-1 w-full rounded-md border border-stone-300 px-2 py-1.5">
          <option value="featured">Featured</option>
          <option value="price-asc">Price, low to high</option>
          <option value="price-desc">Price, high to low</option>
          <option value="newest">Newest</option>
        </select>
      </label>
      <button type="submit" class="rounded-md border border-stone-300 px-3 py-1.5 js:hidden">Apply</button>
      <button type="reset" class="text-stone-500 underline underline-offset-4">Clear filters</button>
    </form>

    <section aria-labelledby="results-heading">
      <h2 id="results-heading" class="sr-only">Products</h2>
      <p aria-live="polite" data-result-count class="text-sm text-stone-500"></p>
      <ul role="list" data-grid class="mt-4 grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-3 xl:grid-cols-4"></ul>
      <div data-empty hidden class="rounded-lg border border-dashed border-stone-300 p-10 text-center">
        <p class="font-medium">Nothing matches those filters.</p>
        <p class="mt-1 text-sm text-stone-500">Try a higher price limit or <button type="button" data-clear class="underline underline-offset-4">clear all filters</button>.</p>
      </div>
    </section>
  </div>
</main>
```

```js
// /js/catalogue.js
const money = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });
const form = document.querySelector('[data-filters]');
const grid = document.querySelector('[data-grid]');
let products = [];   // [{ sku, name, cat, price: 1450, image, added: '2026-09-02', featured: 3 }, ...]

const sorters = {
  featured:   (a, b) => (a.featured ?? 99) - (b.featured ?? 99),
  'price-asc':  (a, b) => a.price - b.price,
  'price-desc': (a, b) => b.price - a.price,
  newest:     (a, b) => b.added.localeCompare(a.added),
};

const card = (p) => `
  <li>
    <a href="/shop/${p.sku}/" class="group block focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-stone-900">
      <img src="${p.image}" width="600" height="600" loading="lazy" alt="" class="aspect-square w-full rounded-lg bg-stone-100 object-cover">
      <h3 class="mt-3 text-sm font-medium group-hover:underline">${p.name}</h3>
      <p class="text-sm tabular-nums text-stone-700">${money.format(p.price / 100)}</p>
    </a>
    <button type="button" data-add="${p.sku}" class="mt-2 text-sm underline underline-offset-4">Add to cart</button>
  </li>`;

function readFilters() {
  const data = new FormData(form);
  return { cats: data.getAll('cat'), max: Number(data.get('max')) * 100, sort: data.get('sort') };
}

function render() {
  const { cats, max, sort } = readFilters();
  const shown = products
    .filter((p) => (cats.length === 0 || cats.includes(p.cat)) && p.price <= max)
    .sort(sorters[sort] ?? sorters.featured);
  grid.innerHTML = shown.map(card).join('');
  document.querySelector('[data-empty]').hidden = shown.length > 0;
  document.querySelector('[data-result-count]').textContent = `${shown.length} of ${products.length} products`;
  form.querySelector('#max-out').value = `${max / 100} €`;
  const params = new URLSearchParams(new FormData(form));
  history.replaceState(null, '', params.toString() ? `?${params}` : location.pathname);
}

function applyUrl() {
  const params = new URLSearchParams(location.search);
  for (const cb of form.querySelectorAll('[name=cat]')) cb.checked = params.getAll('cat').includes(cb.value);
  if (params.has('max')) form.elements.max.value = params.get('max');
  if (params.has('sort')) form.elements.sort.value = params.get('sort');
}

const res = await fetch('/data/products.json');
products = await res.json();
for (const el of form.querySelectorAll('[data-count-for]')) el.textContent = `(${products.filter((p) => p.cat === el.dataset.countFor).length})`;
applyUrl();
render();
form.addEventListener('change', render);
form.addEventListener('input', (e) => { if (e.target.type === 'range') render(); });
form.addEventListener('submit', (e) => { e.preventDefault(); render(); });
form.addEventListener('reset', () => setTimeout(render));            // reset applies after the event
document.querySelector('[data-clear]').addEventListener('click', () => form.reset());
```

Register a `js:` variant once in CSS so the submit button exists only for the no-JS case: `@custom-variant js (&:where(.js, .js *));` with `document.documentElement.classList.add('js')` as the first inline script. Load the module with `<script type="module" src="/js/catalogue.js">`; top-level `await` is fine in modules.

## Variations

- **Filters in a drawer on phones**: wrap the form in a `<details class="lg:open">` or a `<dialog>` opened by a "Filters (2)" button that shows the active count; keep the sort select outside, next to the result count.
- **Price as two inputs** (min and max): two `type="number"` fields with `inputmode="decimal"`; multiply by 100 once in `readFilters`, and treat an empty field as no limit.
- **Facets from the data**: build the category checkboxes from `new Set(products.map(p => p.cat))` when the list changes often; keep the labels in a small map so "brewing" renders as "Brewing gear".
- **Active filter chips**: render the checked values as removable chips above the grid (`web-ui-badges-chips-tags`); clicking a chip unchecks its box and calls `render()`.

## Pitfalls

- Filtering on floating-point euros (`p.price <= 14.5`) works until a price is `0.1 + 0.2`; keep cents as integers and convert the slider's euro value once.
- `history.pushState` on every slider move floods the back button; `replaceState` keeps one history entry per page.
- Re-rendering the grid steals nothing from the filter form, but it does drop focus if the user tabbed into a card; render on `change`, not on every keystroke in a search field (debounce, see `web-js-events-debounce-throttle`).
- A live region that reads "47 of 120 products" on every slider tick is noisy; `aria-live="polite"` waits for a pause, and the `input` handler only fires for the range.
- Grid images without `width`/`height` and `aspect-square` make the page jump as they load, especially after a sort.
- Empty state with only "No results" strands the user; say what to change and give a one-click way out.
- `products.json` over a few hundred items is fine; thousands need pagination (`web-nav-pagination`) or a search index, not a bigger JSON.

## Related skills

- `web-layout-card-grid`
- `web-ecommerce-cart`
- `web-page-product-detail`
- `web-form-choices`
- `web-ui-badges-chips-tags`
- `web-js-router-and-urls`
- `web-data-number-formatting`
- `web-design-empty-and-error-states`
