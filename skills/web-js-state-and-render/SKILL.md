---
name: web-js-state-and-render
description: Build an interactive widget (filters, cart, counter, todo, calculator) with a tiny store + pure `render(state)` function in vanilla JavaScript, no framework. Use whenever a user says "keep the UI in sync", "state management without React", "the DOM gets out of sync", "re-render on change", or wants reactive behaviour on a static page.
---

# State and render: one object, one function

Bugs in interactive vanilla pages almost always come from the DOM being the source of truth: you toggle a class here, update a count there, and the two drift apart. The fix is the same idea frameworks use, minus the framework: keep **one plain state object**, change it only through `setState`, and have **one `render(state)` function** that paints the whole widget from scratch. For widgets under a few hundred nodes, re-rendering everything is cheaper than reasoning about diffs, and the code stays obvious.

## Pattern

```html
<section data-widget="cart" class="mx-auto max-w-md rounded-lg border p-4">
  <h2 class="text-lg font-semibold">Cart</h2>
  <ul data-js="items" class="my-3 divide-y"></ul>
  <p class="flex justify-between"><span>Total</span><strong data-js="total">$0.00</strong></p>
  <form data-js="add" class="mt-3 flex gap-2">
    <label class="sr-only" for="item-name">Item name</label>
    <input id="item-name" name="name" required class="flex-1 rounded border px-2 py-1" placeholder="Item">
    <input name="price" type="number" step="0.01" min="0" required class="w-24 rounded border px-2 py-1" aria-label="Price">
    <button class="rounded bg-gray-900 px-3 text-white">Add</button>
  </form>
</section>
```

```js
// /js/store.js
export function createStore(initial) {
  let state = structuredClone(initial);
  const listeners = new Set();
  return {
    get: () => state,
    set(patch) {                                    // patch: object or (prev) => object
      const next = typeof patch === 'function' ? patch(state) : patch;
      state = { ...state, ...next };
      for (const fn of listeners) fn(state);
    },
    subscribe(fn) { listeners.add(fn); fn(state); return () => listeners.delete(fn); },
  };
}
```

```js
// /js/cart.js
import { createStore } from './store.js';

const money = new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' });

export function initCart(root) {
  const items = root.querySelector('[data-js="items"]');
  const total = root.querySelector('[data-js="total"]');
  const form = root.querySelector('[data-js="add"]');

  const store = createStore({ items: [], nextId: 1 });

  // --- actions: the only place state changes ---
  const add = (name, price) => store.set((s) => ({
    items: [...s.items, { id: s.nextId, name, price, qty: 1 }], nextId: s.nextId + 1,
  }));
  const remove = (id) => store.set((s) => ({ items: s.items.filter((i) => i.id !== id) }));
  const changeQty = (id, delta) => store.set((s) => ({
    items: s.items.map((i) => (i.id === id ? { ...i, qty: Math.max(1, i.qty + delta) } : i)),
  }));

  // --- render: pure function of state, touches the DOM nowhere else ---
  function render(state) {
    items.replaceChildren(...state.items.map(renderItem));
    total.textContent = money.format(state.items.reduce((sum, i) => sum + i.price * i.qty, 0));
    root.classList.toggle('is-empty', state.items.length === 0);
  }
  function renderItem(item) {
    const li = document.createElement('li');
    li.className = 'flex items-center gap-2 py-2';
    li.dataset.id = item.id;
    li.innerHTML = `
      <span class="flex-1"></span>
      <button type="button" data-action="dec" class="px-2" aria-label="Decrease quantity">−</button>
      <span data-js="qty" class="w-6 text-center"></span>
      <button type="button" data-action="inc" class="px-2" aria-label="Increase quantity">+</button>
      <button type="button" data-action="remove" class="ml-2 text-red-600" aria-label="Remove">×</button>`;
    li.querySelector('span').textContent = `${item.name} · ${money.format(item.price)}`;  // user data: textContent
    li.querySelector('[data-js="qty"]').textContent = item.qty;
    return li;
  }

  // --- events: delegated once, map to actions ---
  items.addEventListener('click', (e) => {
    const button = e.target.closest('[data-action]');
    if (!button) return;
    const id = Number(button.closest('li').dataset.id);
    ({ inc: () => changeQty(id, 1), dec: () => changeQty(id, -1), remove: () => remove(id) })[button.dataset.action]();
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const data = new FormData(form);
    add(data.get('name').trim(), Number(data.get('price')));
    form.reset();
    form.elements.name.focus();
  });

  const unsubscribe = store.subscribe(render);
  return () => unsubscribe();                     // teardown for SPA panels / tests
}

document.querySelectorAll('[data-widget="cart"]').forEach(initCart);
```

## Variations

- **Persist**: `store.subscribe((s) => localStorage.setItem('cart', JSON.stringify(s)))` and seed `createStore` from storage; see `web-js-storage` for versioning and quota handling.
- **Derived values**: compute totals, filtered lists and "is empty" inside `render`, never store them; derived state in the store is the second-most-common source of drift.
- **Preserve focus and input text** across re-renders by rendering only the list region (as above) and keeping the form outside the re-rendered subtree. If you must re-render an input, save `document.activeElement.id` and `selectionStart`, then restore after.
- **Many widgets**: give each `initCart(root)` its own store; share state between widgets via one store passed in, or use `CustomEvent` on `document` for loose coupling.

## Pitfalls

- Mutating state in place (`state.items.push(x)`) skips `set`, so nothing re-renders. Always return new arrays/objects; `structuredClone` the initial value so callers cannot keep a reference.
- Rebuilding a list of thousands of rows on every keystroke stutters. Render on `requestAnimationFrame`, or keep DOM nodes keyed by `data-id` and only add/remove the delta.
- `innerHTML` templates are fine for *static* markup, but insert user or API strings with `textContent` as shown, or you have an XSS bug.
- Updating the DOM from inside `render` for one state branch and from an event handler for another is the drift you were trying to avoid. The event handler only calls actions.
- Forgetting the teardown: a store subscription keeps the widget's DOM alive after it is removed. Return and call the unsubscribe.

## Related skills

- `web-js-dom-utilities`
- `web-js-storage`
- `web-js-web-components`
- `web-js-events-debounce-throttle`
- `web-layout-pricing-table`
