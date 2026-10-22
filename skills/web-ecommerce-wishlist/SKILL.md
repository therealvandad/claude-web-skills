---
name: web-ecommerce-wishlist
description: Add a wishlist to a static shop: a heart toggle (aria-pressed, localStorage) on product cards, a header count, a wishlist page with "move to cart", and a share link carrying the items in the URL, in Tailwind v4 and vanilla JS. Use whenever a user asks for a wishlist, favourites, "save for later", "heart button" or "share my list".
---

# Wishlist without an account

A wishlist is a set of SKUs the visitor wants to find again. On a static site it lives in `localStorage` (a `Set`, serialised as an array), the catalogue JSON supplies names and prices at render time, and sharing is a URL with the SKUs in a query string, which also makes the list survive a cleared browser if the owner ever sent it to themselves. The heart is a `<button aria-pressed>`, not a link and not a checkbox: it does something now and has a true/false state that assistive tech can read.

## Pattern

```js
// /js/wishlist.js
const KEY = 'shop:wishlist';
const listeners = new Set();
let skus = load();

function load() { try { return new Set(JSON.parse(localStorage.getItem(KEY)) ?? []); } catch { return new Set(); } }
function save() { try { localStorage.setItem(KEY, JSON.stringify([...skus])); } catch { /* optional */ } notify(); }
function notify() { for (const fn of listeners) fn([...skus]); }

export const has = (sku) => skus.has(sku);
export function toggle(sku) { skus.has(sku) ? skus.delete(sku) : skus.add(sku); save(); return skus.has(sku); }
export function remove(sku) { skus.delete(sku); save(); }
export function subscribe(fn) { listeners.add(fn); fn([...skus]); return () => listeners.delete(fn); }
export const shareUrl = () => `${location.origin}/wishlist/?items=${[...skus].join(',')}`;

window.addEventListener('storage', (e) => { if (e.key === KEY) { skus = load(); notify(); } });
```

```html
<!-- Heart on a card or buy box. Text in sr-only, state in aria-pressed, icon follows the state. -->
<button type="button" data-wish="soledad-480" aria-pressed="false"
        class="group rounded-full border border-stone-300 p-2 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 aria-pressed:border-rose-600">
  <span class="sr-only">Save Finca La Soledad, 480 g to wishlist</span>
  <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 fill-transparent stroke-current stroke-2 transition-colors group-aria-pressed:fill-rose-600 group-aria-pressed:stroke-rose-600"><path d="M12 21s-7-4.6-9.3-9A5.3 5.3 0 0 1 12 6.2 5.3 5.3 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>
</button>

<!-- Header link -->
<a href="/wishlist/" class="text-sm underline-offset-4 hover:underline">Wishlist <span data-wish-count class="tabular-nums">(0)</span></a>
```

```html
<!-- /wishlist/index.html -->
<main id="main" class="mx-auto max-w-5xl px-4 py-10">
  <div class="flex flex-wrap items-end justify-between gap-4">
    <h1 class="text-3xl font-semibold tracking-tight">Your wishlist</h1>
    <button type="button" data-share class="rounded-md border border-stone-300 px-3 py-1.5 text-sm hover:bg-stone-100">Copy share link</button>
  </div>
  <p data-shared-note hidden class="mt-3 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900">You are viewing someone else's list. <button type="button" data-import class="underline underline-offset-4">Add these to my wishlist</button></p>
  <p aria-live="polite" data-status class="mt-3 text-sm text-stone-600"></p>
  <ul role="list" data-wish-list class="mt-8 grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-3"></ul>
  <p data-wish-empty hidden class="mt-8 text-stone-500">Nothing saved yet. Tap the heart on any product and it shows up here, on this device.</p>
</main>
```

```js
// /js/wishlist-ui.js
import { has, toggle, remove, subscribe, shareUrl } from './wishlist.js';
import { catalogue, format, add as addToCart } from './cart.js';

const status = document.querySelector('[data-status]');
const say = (text) => { if (status) status.textContent = text; };

// Hearts anywhere on the site
subscribe((skus) => {
  document.querySelectorAll('[data-wish]').forEach((b) => b.setAttribute('aria-pressed', String(skus.includes(b.dataset.wish))));
  document.querySelectorAll('[data-wish-count]').forEach((el) => (el.textContent = `(${skus.length})`));
});
document.addEventListener('click', (e) => {
  const heart = e.target.closest('[data-wish]');
  if (heart) say(toggle(heart.dataset.wish) ? 'Saved to wishlist' : 'Removed from wishlist');
});

// Wishlist page
const list = document.querySelector('[data-wish-list]');
if (list) {
  const shared = new URLSearchParams(location.search).get('items')?.split(',').filter((s) => catalogue[s]);
  document.querySelector('[data-shared-note]').hidden = !shared?.length;

  const render = (skus) => {
    const items = (shared?.length ? shared : skus).map((sku) => ({ sku, ...catalogue[sku] }));
    document.querySelector('[data-wish-empty]').hidden = items.length > 0;
    list.innerHTML = items.map(({ sku, name, price, image }) => `
      <li class="text-sm">
        <a href="/shop/${sku}/"><img src="${image}" width="600" height="600" loading="lazy" alt="" class="aspect-square w-full rounded-lg bg-stone-100 object-cover"></a>
        <h2 class="mt-3 font-medium">${name}</h2>
        <p class="tabular-nums text-stone-700">${format(price)}</p>
        <div class="mt-2 flex gap-3">
          <button type="button" data-move="${sku}" class="rounded-md bg-stone-900 px-3 py-1.5 text-white">Add to cart</button>
          ${shared?.length ? '' : `<button type="button" data-unwish="${sku}" class="text-stone-500 underline underline-offset-4">Remove</button>`}
        </div>
      </li>`).join('');
  };
  subscribe(render);

  list.addEventListener('click', (e) => {
    const move = e.target.closest('[data-move]'); const un = e.target.closest('[data-unwish]');
    if (move) { addToCart(move.dataset.move); say(`${catalogue[move.dataset.move].name} added to cart`); }
    if (un) { remove(un.dataset.unwish); say('Removed from wishlist'); }
  });
  document.querySelector('[data-share]').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(shareUrl()); say('Link copied. Anyone with it sees this list.'); }
    catch { say(`Copy this link: ${shareUrl()}`); }
  });
  document.querySelector('[data-import]').addEventListener('click', () => { for (const s of shared) if (!has(s)) toggle(s); history.replaceState(null, '', '/wishlist/'); location.reload(); });
}
```

## Variations

- **Save for later from the cart**: a "Save for later" button on a cart line calls `toggle(sku)` then `removeFromCart(sku)`; show saved items in a second list under the cart with "Move to cart".
- **Native share on phones**: prefer `navigator.share({ title: 'My wishlist', url: shareUrl() })` when `navigator.canShare?.()` is true, and fall back to the clipboard.
- **Price drop note**: store `{ sku, priceWhenSaved }` instead of bare SKUs and render "was 16,00 € when you saved it" when the catalogue price is lower; only true data, see `web-ecommerce-trust-and-conversion`.
- **Email the list to yourself**: a `mailto:` link with the share URL in the body needs no server and no consent machinery.

## Pitfalls

- Hearts rendered server-side as `aria-pressed="false"` flash to pressed after the module loads; acceptable, but render the page's hearts inside the first `subscribe` callback before images paint, or hide them until `.js` is on `<html>`.
- A heart as `<a href="#">` scrolls to top and announces "link"; a `<div onclick>` is unreachable by keyboard. Use `<button aria-pressed>`.
- Share URLs that encode names and prices can be edited to show wrong prices; encode SKUs only and let the page look them up.
- `navigator.clipboard.writeText` rejects outside a user gesture or on `http://`; keep it in the click handler and fall back to showing the link.
- A shared list that silently merges into the viewer's own list is confusing; show the banner and make import an explicit button.
- Storing the wishlist under a key another script also uses (`'wishlist'`) collides on shared hosting origins; prefix with the site name.

## Related skills

- `web-ecommerce-cart`
- `web-js-storage`
- `web-a11y-aria-patterns`
- `web-ui-toast-notifications`
- `web-layout-card-grid`
- `web-ecommerce-trust-and-conversion`
