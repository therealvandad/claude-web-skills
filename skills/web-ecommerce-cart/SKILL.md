---
name: web-ecommerce-cart
description: 'Build a shopping cart for a static site with no backend: a localStorage cart.js module (integer cents, Intl formatting, cross-tab sync), "add to cart" buttons, a header badge and a mini-cart drawer with quantity steppers and subtotal, in Tailwind v4. Use whenever a user asks for a cart, basket, "add to cart", mini cart, cart drawer or cart count.'
---

# Cart in localStorage

A static shop has no session, so the cart is the browser's job. Keep one module as the single source of truth: an array of `{ sku, qty }` lines in `localStorage`, product names and prices looked up from the catalogue (never stored in the cart, so a price change on the site is a price change in every open cart), money as integers in minor units so `3 × 14.50` never becomes `43.499999`. Every piece of UI (badge, drawer, cart page) subscribes to the module and re-renders from a snapshot; the `storage` event keeps a second tab in step.

## Pattern

```js
// /js/cart.js
const KEY = 'shop:cart';
const VERSION = 1;
const MAX_QTY = 20;
const listeners = new Set();

// Normally fetched once from /data/products.json; prices are integers in cents.
export const catalogue = {
  'soledad-480': { name: 'Finca La Soledad, 480 g, whole bean', price: 1450, image: '/img/soledad-480.webp' },
  'dripper-02':  { name: 'Ceramic dripper, size 02, white',     price: 2400, image: '/img/dripper-02.webp' },
  'filters-100': { name: 'Paper filters, size 02, 100 pack',    price: 420,  image: '/img/filters-100.webp' },
};
export const money = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });
export const format = (cents) => money.format(cents / 100);

let lines = load();

function load() {
  try {
    const record = JSON.parse(localStorage.getItem(KEY));
    return record?.v === VERSION && Array.isArray(record.lines) ? record.lines.filter((l) => catalogue[l.sku]) : [];
  } catch { return []; }                                  // corrupt, private mode, or empty: start clean
}
function save() {
  try { localStorage.setItem(KEY, JSON.stringify({ v: VERSION, lines, updated: Date.now() })); } catch { /* storage is optional */ }
  notify();
}
function notify() { const s = snapshot(); for (const fn of listeners) fn(s); }

export function snapshot() {
  const items = lines.map((l) => ({ ...l, ...catalogue[l.sku], total: catalogue[l.sku].price * l.qty }));
  return { items, count: items.reduce((n, i) => n + i.qty, 0), subtotal: items.reduce((n, i) => n + i.total, 0) };
}
export function add(sku, qty = 1) { setQty(sku, (lines.find((l) => l.sku === sku)?.qty ?? 0) + qty); }
export function setQty(sku, qty) {
  qty = Math.min(MAX_QTY, Math.max(0, Math.trunc(Number(qty) || 0)));
  lines = qty === 0 ? lines.filter((l) => l.sku !== sku)
        : lines.some((l) => l.sku === sku) ? lines.map((l) => (l.sku === sku ? { ...l, qty } : l)) : [...lines, { sku, qty }];
  save();
}
export function remove(sku) { setQty(sku, 0); }
export function clear() { lines = []; save(); }
export function subscribe(fn) { listeners.add(fn); fn(snapshot()); return () => listeners.delete(fn); }

window.addEventListener('storage', (e) => { if (e.key === KEY) { lines = load(); notify(); } });   // other tab changed it
```

```html
<!-- Header button: badge is hidden at zero -->
<button type="button" data-cart-open aria-controls="cart" aria-expanded="false" class="relative rounded-md p-2 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">
  <span class="sr-only">Open cart,</span> Cart
  <span data-cart-count hidden class="absolute -right-1 -top-1 min-w-5 rounded-full bg-stone-900 px-1 text-center text-xs font-medium tabular-nums text-white">0</span>
</button>

<!-- On a product card or page -->
<button type="button" data-add="soledad-480" class="rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Add to cart, 14,50 €</button>

<!-- Drawer: native dialog, slides from the right from sm -->
<dialog id="cart" aria-labelledby="cart-title" class="m-0 ml-auto h-dvh w-full max-w-md bg-white p-0 shadow-xl backdrop:bg-stone-900/40 open:flex open:flex-col">
  <header class="flex items-center justify-between border-b border-stone-200 px-5 py-4">
    <h2 id="cart-title" class="text-lg font-semibold">Your cart</h2>
    <button type="button" data-cart-close class="rounded-md p-1 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-stone-900"><span class="sr-only">Close</span>&times;</button>
  </header>
  <ul role="list" data-cart-lines class="flex-1 divide-y divide-stone-200 overflow-y-auto px-5"></ul>
  <p data-cart-empty class="px-5 py-10 text-center text-stone-500">Nothing in here yet. <a href="/shop/" class="underline underline-offset-4">See the coffee</a></p>
  <footer class="border-t border-stone-200 px-5 py-4">
    <p class="flex justify-between text-sm"><span>Subtotal</span><strong data-cart-subtotal class="tabular-nums">0,00 €</strong></p>
    <p class="mt-1 text-xs text-stone-500">Shipping and VAT shown at checkout.</p>
    <a href="/checkout/" data-cart-checkout class="mt-4 block rounded-md bg-stone-900 px-5 py-3 text-center font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Go to checkout</a>
  </footer>
  <p aria-live="polite" class="sr-only" data-cart-status></p>
</dialog>
```

```js
// /js/cart-ui.js
import { subscribe, add, setQty, remove, format } from './cart.js';

const dialog = document.getElementById('cart');
const status = dialog.querySelector('[data-cart-status]');

const lineHTML = ({ sku, name, image, qty, total }) => `
  <li class="flex gap-4 py-4" data-sku="${sku}">
    <img src="${image}" width="64" height="64" alt="" class="size-16 rounded bg-stone-100 object-cover">
    <div class="flex-1 text-sm">
      <p class="font-medium">${name}</p>
      <div class="mt-2 flex items-center justify-between">
        <div class="inline-flex items-center rounded-md border border-stone-300">
          <button type="button" data-step="-1" aria-label="Decrease quantity of ${name}" class="px-2.5 py-1 hover:bg-stone-100">−</button>
          <input type="number" inputmode="numeric" min="0" max="20" value="${qty}" aria-label="Quantity of ${name}" class="w-10 border-x border-stone-300 py-1 text-center tabular-nums [appearance:textfield]">
          <button type="button" data-step="1" aria-label="Increase quantity of ${name}" class="px-2.5 py-1 hover:bg-stone-100">+</button>
        </div>
        <p class="tabular-nums">${format(total)}</p>
      </div>
      <button type="button" data-remove class="mt-1 text-xs text-stone-500 underline underline-offset-4">Remove</button>
    </div>
  </li>`;

subscribe(({ items, count, subtotal }) => {
  document.querySelectorAll('[data-cart-count]').forEach((el) => { el.textContent = count; el.hidden = count === 0; });
  dialog.querySelector('[data-cart-lines]').innerHTML = items.map(lineHTML).join('');
  dialog.querySelector('[data-cart-empty]').hidden = count > 0;
  dialog.querySelector('[data-cart-subtotal]').textContent = format(subtotal);
  dialog.querySelector('[data-cart-checkout]').toggleAttribute('hidden', count === 0);
});

document.addEventListener('click', (e) => {
  const addBtn = e.target.closest('[data-add]');
  if (addBtn) { add(addBtn.dataset.add); status.textContent = 'Added to cart'; dialog.showModal(); return; }
  if (e.target.closest('[data-cart-open]')) dialog.showModal();
  if (e.target.closest('[data-cart-close]')) dialog.close();
  const li = e.target.closest('[data-sku]');
  if (!li) return;
  const input = li.querySelector('input');
  if (e.target.closest('[data-step]')) setQty(li.dataset.sku, Number(input.value) + Number(e.target.closest('[data-step]').dataset.step));
  if (e.target.closest('[data-remove]')) { remove(li.dataset.sku); status.textContent = 'Removed from cart'; }
});
dialog.addEventListener('change', (e) => { const li = e.target.closest('[data-sku]'); if (li && e.target.type === 'number') setQty(li.dataset.sku, e.target.value); });
dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });   // backdrop click
```

## Variations

- **Full cart page** (`/cart/`): same `subscribe` callback rendering into a `<table>` with columns Product / Quantity / Price, the drawer becomes a shortcut to it; keep the drawer for "added" feedback.
- **Variants**: make the line key `sku` the full variant SKU (`soledad-480-espresso`) and store `{ sku, qty, options: { grind: 'espresso' } }` for display; see `web-ecommerce-variants-and-stock`.
- **Toast instead of opening the drawer**: `web-ui-toast-notifications` with "Added. View cart" is calmer on product grids where people add several things in a row.
- **Expiry**: drop a cart older than 30 days in `load()` by checking `record.updated`; prices and stock will have moved on.

## Pitfalls

- Storing the price in the cart line lets a stale tab show yesterday's price and, worse, tempts you to send it to checkout. Checkout must price from its own catalogue (`web-ecommerce-checkout-stripe`); the cart only sends `sku` and `qty`.
- Floating-point money: `0.1 + 0.2`. Keep cents as integers everywhere and divide by 100 only inside `format`.
- Re-rendering the whole list while the quantity input has focus drops the caret; `change` (not `input`) on the number field, and the steppers re-render only after a click, so focus loss is acceptable. For a type-ahead feel, update the single `<li>` in place.
- The `storage` event never fires in the tab that wrote; `save()` calls `notify()` itself.
- `<dialog>` without `showModal()` has no focus trap or backdrop; a `div` drawer needs `web-a11y-keyboard-and-focus` to do that by hand.
- A cart badge that reads "3" with no accessible name is announced as "Cart 3"; the `sr-only` prefix makes it "Open cart, Cart 3". Good enough; "3 items" is better if the number is interpolated.
- Private mode or a full quota throws on `setItem`; the cart still works in memory for this page load, which is why every storage call is wrapped.

## Related skills

- `web-js-storage`
- `web-ecommerce-checkout-stripe`
- `web-ecommerce-variants-and-stock`
- `web-ecommerce-discount-codes`
- `web-ui-modal-dialog`
- `web-ui-toast-notifications`
- `web-data-number-formatting`
- `web-js-state-and-render`
