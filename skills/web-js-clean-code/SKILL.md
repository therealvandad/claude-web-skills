---
name: web-js-clean-code
description: Refactor or write front-end JavaScript that stays readable - naming, small single-purpose functions, early returns, data-attribute hooks instead of class selectors, find/compute/paint separation, comments that explain why, modern syntax (optional chaining, destructuring, Intl). Use whenever a user says "clean this up", "refactor my script", "this function is too long", "code review my JS", or "vanilla JavaScript best practices".
---

# Clean vanilla JavaScript

Front-end scripts rot in a predictable way: one 200-line `main.js` with anonymous callbacks, `document.querySelector('.card .btn')` scattered everywhere, booleans named `flag`, and DOM reads mixed with business logic so nothing can be tested or reused. The cure is structural, not stylistic: **hook on data attributes**, split every feature into **find → compute → paint**, give each function one job and a verb name, and **return early** so the happy path reads top to bottom. Comments then only need to explain what the code cannot: the *why*.

## Pattern

Before: works, but every line knows about everything.

```js
document.querySelector('.filter').addEventListener('input', function (e) {
  var items = document.querySelectorAll('.grid .card'); var n = 0;
  for (var i = 0; i < items.length; i++) {
    if (items[i].querySelector('h3').innerText.toLowerCase().indexOf(e.target.value.toLowerCase()) > -1) {
      items[i].style.display = ''; n++;
    } else { items[i].style.display = 'none'; }
  }
  document.querySelector('.count').innerHTML = n + ' results';
});
```

After: hooks are explicit, logic is pure, DOM work is isolated, names say what and why.

```html
<section data-feature="product-filter">
  <label for="product-q" class="sr-only">Filter products</label>
  <input id="product-q" type="search" data-js="query" class="rounded border px-3 py-2" placeholder="Filter…">
  <p data-js="count" role="status" class="text-sm text-gray-500"></p>
  <ul data-js="list" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
    <li data-item data-name="Alpine Jacket">…</li>
    <li data-item data-name="Trail Runner">…</li>
  </ul>
</section>
```

```js
// /js/features/product-filter.js
import { debounce } from '../lib/timing.js';

export function initProductFilter(root) {
  // 1. find: resolve every hook once, fail fast if the markup is wrong
  const query = root.querySelector('[data-js="query"]');
  const count = root.querySelector('[data-js="count"]');
  const items = [...root.querySelectorAll('[data-item]')];
  if (!query || !count) throw new Error('product-filter: missing data-js hooks');

  const applyFilter = () => {
    const matches = filterItems(items, query.value);   // 2. compute (pure)
    paint(items, matches, count);                       // 3. paint
  };

  // debounce: typing fast on a 300-item grid otherwise re-lays out on every keystroke
  query.addEventListener('input', debounce(applyFilter, 150));
  applyFilter();
}

/** Pure: easy to unit test, no DOM mutation. Returns the subset that matches. */
export function filterItems(items, rawQuery) {
  const needle = normalise(rawQuery);
  if (!needle) return items;
  return items.filter((item) => normalise(item.dataset.name).includes(needle));
}

function paint(items, matches, count) {
  const visible = new Set(matches);
  for (const item of items) item.hidden = !visible.has(item);
  count.textContent = formatCount(matches.length);
}

// NFKD + strip accents so "Ålpine" matches "alpine"; users rarely type diacritics on mobile
const normalise = (s) => (s ?? '').normalize('NFKD').replace(/\p{M}/gu, '').trim().toLowerCase();

const plural = new Intl.PluralRules('en');
const formatCount = (n) => `${n} ${plural.select(n) === 'one' ? 'result' : 'results'}`;
```

## Variations

- **Early returns over nesting**: `if (!form.checkValidity()) return;` at the top of a handler instead of wrapping the whole body in `if (valid) { ... }`. Three levels of indentation is the smell threshold.
- **Name by role, not type**: `submitButton`, `priceInput`, `openModal()`, `isLoading`, `hasItems`. Booleans start with `is/has/can`; functions start with a verb; collections are plural.
- **Modern syntax that removes code**: `user?.address?.city ?? 'Unknown'`, `const { name, price = 0 } = product`, `Object.groupBy(items, (i) => i.category)`, `array.at(-1)`, `structuredClone(state)`, `Intl.NumberFormat`/`DateTimeFormat`/`RelativeTimeFormat` instead of hand-rolled formatting.
- **Config at the top**: magic numbers (`150`, `'/api/products'`) become named constants or a frozen `config` object; a reviewer should never have to ask what `400` means.

## Pitfalls

- Selecting by Tailwind or styling classes (`.grid .card`) couples behaviour to design; a redesign breaks the script. Only `data-*` and `id` are JS hooks.
- A function that both computes and paints cannot be tested without a DOM and cannot be reused for a different output. Keep `filterItems` pure and let `paint` be dumb.
- Comments that restate the code (`// increment i`) go stale and train readers to skip comments. Write the reason, the constraint, or the link to the bug.
- `var`, `function` hoisting and `this` in callbacks are three sources of surprise. Use `const`/`let`, arrow functions for callbacks, and module scope.
- Over-abstraction is also unclean: a `BaseComponent` class with lifecycle hooks for a filter box is a framework you now maintain. Two similar lines are cheaper than one premature helper.
- `innerText` forces layout and `innerHTML` with user data is XSS; use `textContent` for both reading and writing text.

## Related skills

- `web-js-dom-utilities`
- `web-js-modules-and-structure`
- `web-js-events-debounce-throttle`
- `web-js-state-and-render`
- `web-js-errors-and-logging`
