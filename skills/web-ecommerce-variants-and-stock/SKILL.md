---
name: web-ecommerce-variants-and-stock
description: Build size and colour pickers as native radio groups in Tailwind v4, resolve the chosen variant SKU, update price and stock text (in stock, only 3 left, sold out, back on a date), keep sold-out options selectable, and swap the button for a back-in-stock email form. Use whenever a user asks for "variants", "size picker", "colour swatches", "out of stock", "sold out" or "notify me".
---

# Variants and stock

Each combination of options is its own product: its own SKU, price and stock count. The page shows option groups, but the cart, checkout and stock check only ever see the resolved variant SKU (`dripper-02-celadon`). Build the pickers from native radio inputs inside `<fieldset>`s so arrow keys, form reset and screen readers work for free, and style the `<label>` with `has-checked:`. Do not disable sold-out options: a disabled radio cannot be focused, gives no reason, and hides the one action that still makes sense, asking to be told when it is back.

## Pattern

```html
<script type="application/json" id="variants">
{ "variants": [
  { "sku": "dripper-02-white",    "size": "02", "colour": "white",    "price": 2400, "stock": 34 },
  { "sku": "dripper-02-charcoal", "size": "02", "colour": "charcoal", "price": 2400, "stock": 3 },
  { "sku": "dripper-02-celadon",  "size": "02", "colour": "celadon",  "price": 2600, "stock": 0, "restock": "2026-11-14" },
  { "sku": "dripper-01-white",    "size": "01", "colour": "white",    "price": 2200, "stock": 12 },
  { "sku": "dripper-01-charcoal", "size": "01", "colour": "charcoal", "price": 2200, "stock": 0 },
  { "sku": "dripper-01-celadon",  "size": "01", "colour": "celadon",  "price": 2400, "stock": 9 }
] }
</script>

<form data-variant-form class="space-y-6">
  <fieldset>
    <legend class="text-sm font-medium">Colour: <span data-colour-name class="font-normal text-stone-600">White</span></legend>
    <div class="mt-2 flex gap-3">
      <!-- Repeat per colour: charcoal bg-stone-800, celadon bg-[#a9c4b0] -->
      <label class="cursor-pointer rounded-full p-0.5 ring-2 ring-transparent has-checked:ring-stone-900 has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-stone-900 data-soldout:opacity-40">
        <input type="radio" name="colour" value="white" data-label="White" checked class="sr-only">
        <span aria-hidden="true" class="block size-9 rounded-full border border-stone-400 bg-[#f4f1ea]"></span>
        <span class="sr-only">White <span data-note></span></span>
      </label>
    </div>
  </fieldset>
  <fieldset>
    <legend class="text-sm font-medium">Size</legend>
    <div class="mt-2 grid grid-cols-2 gap-2">
      <!-- Repeat for size 01, "1–2 cups" -->
      <label class="cursor-pointer rounded-md border border-stone-300 px-3 py-2 text-sm has-checked:border-stone-900 has-checked:bg-stone-900 has-checked:text-white has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-stone-900">
        <input type="radio" name="size" value="02" checked class="sr-only">02 · 1–4 cups <span data-note class="block text-xs opacity-75"></span>
      </label>
    </div>
  </fieldset>
</form>

<p data-price class="mt-6 text-2xl font-semibold tabular-nums">24,00 €</p>
<p data-stock role="status" class="mt-1 text-sm"></p>
<button type="button" data-add="dripper-02-white" class="mt-4 w-full rounded-md bg-stone-900 px-5 py-3 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Add to cart</button>

<form data-restock hidden action="/api/back-in-stock" method="post" class="mt-4 rounded-md border border-stone-200 p-4">
  <input type="hidden" name="sku">
  <label for="restock-email" class="block text-sm font-medium">Email me when this is back</label>
  <div class="mt-2 flex gap-2">
    <input id="restock-email" name="email" type="email" autocomplete="email" required class="min-w-0 flex-1 rounded-md border border-stone-300 px-3 py-2">
    <button class="rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Notify me</button>
  </div>
  <p class="mt-2 text-xs text-stone-500">One email when it's back in stock, then we delete your address.</p>
</form>
```

```js
// /js/variants.js
import { format } from './cart.js';
const { variants } = JSON.parse(document.getElementById('variants').textContent);
const form = document.querySelector('[data-variant-form]');
const stockEl = document.querySelector('[data-stock]');
const addBtn = document.querySelector('[data-add]');
const restock = document.querySelector('[data-restock]');
const LOW = 3;                                                   // show a count only at or below this, and only if true
const date = new Intl.DateTimeFormat('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });

const find = (opts) => variants.find((v) => Object.entries(opts).every(([k, val]) => v[k] === val));

function stockText(v) {
  if (v.stock > LOW) return ['In stock, ships in 1–2 working days', 'text-emerald-800'];
  if (v.stock > 0) return [`Only ${v.stock} left in this colour and size`, 'text-amber-800'];
  if (v.restock) return [`Sold out. Expected back ${date.format(new Date(v.restock))}`, 'text-stone-600'];
  return ['Sold out, no restock date yet', 'text-stone-600'];
}

function update() {
  const opts = Object.fromEntries(new FormData(form));
  for (const input of form.querySelectorAll('input[type="radio"]')) {          // would picking this option land on a sold-out variant?
    const other = find({ ...opts, [input.name]: input.value });
    const out = !other || other.stock === 0;
    input.closest('label').toggleAttribute('data-soldout', out);
    input.closest('label').querySelector('[data-note]').textContent = out ? '(sold out)' : '';
  }
  const v = find(opts);
  const [text, tone] = stockText(v);
  document.querySelector('[data-colour-name]').textContent = form.querySelector('[name="colour"]:checked').dataset.label;
  document.querySelector('[data-price]').textContent = format(v.price);
  stockEl.textContent = text;
  stockEl.className = `mt-1 text-sm ${tone}`;
  addBtn.hidden = v.stock === 0;
  addBtn.dataset.add = v.sku;
  addBtn.textContent = `Add to cart, ${format(v.price)}`;
  restock.hidden = v.stock > 0;
  restock.elements.sku.value = v.sku;
  const url = new URL(location.href);
  url.searchParams.set('variant', v.sku);
  history.replaceState(null, '', url);                           // shareable, no history spam
}

const linked = variants.find((v) => v.sku === new URLSearchParams(location.search).get('variant'));
if (linked) { form.elements.colour.value = linked.colour; form.elements.size.value = linked.size; }
form.addEventListener('change', update);
update();
```

## Variations

- **Many sizes (clothing)**: a `grid-cols-4 sm:grid-cols-6` of size pills plus a "Size guide" `<dialog>` link next to the legend; keep the chosen size in the URL so a shared link opens on it.
- **Text-only colour options**: when there are more than six colours, use a native `<select>` labelled "Colour" with "(sold out)" in the option text; swatches stop scanning well past that.
- **Live stock**: replace the inline JSON with `fetch('/data/stock.json', { cache: 'no-store' })` written by the order webhook, and render the static numbers first so the page works if the fetch fails.
- **Preorder**: `"stock": 0, "preorder": true, "ships": "2026-11-14"` keeps the button as "Preorder, ships 14 November" instead of the restock form; say the date on the button, not only in small print.

## Pitfalls

- `disabled` on sold-out radios removes them from keyboard and screen-reader paths and explains nothing; keep them enabled, mark them `data-soldout`, add "(sold out)" to the accessible name, and switch the button for the restock form.
- A swatch that is only a colour fails people who cannot tell celadon from grey; the legend shows the chosen colour name and every swatch has an `sr-only` name. Light swatches need a border with 3:1 contrast against the page.
- Stock in a static file is stale the moment someone buys. Stripe Checkout does not track inventory, so the checkout function must refuse SKUs at zero and the `checkout.session.completed` webhook must decrement stock.
- "Only 3 left" must come from the real count, never a hard-coded scarcity line; see `web-ecommerce-trust-and-conversion`.
- The cart key is the variant SKU, and the cart catalogue needs every variant; adding the parent `dripper-02` makes "which colour?" a support email.
- Listening for `click` on labels misses arrow-key changes within a radio group; listen for `change` on the form.

## Related skills

- `web-page-product-detail`
- `web-ecommerce-cart`
- `web-form-choices`
- `web-form-submit-with-fetch`
- `web-a11y-color-contrast`
- `web-ecommerce-trust-and-conversion`
- `web-seo-structured-data`
