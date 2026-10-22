---
name: web-ecommerce-discount-codes
description: 'Add a promo code field to a static shop''s cart: rules in a codes.json (percent, fixed, free shipping, minimum spend, dates, eligible SKUs), an applied-code chip with remove, specific error copy, and Stripe as the final authority at checkout. Use whenever a user asks for a "discount code", "coupon", "promo code", "voucher", "apply code" or "% off".'
---

# Discount codes

A code field does two jobs: show the buyer what the code is worth before they pay, and make sure the payment page charges exactly that. On a static site the first job runs in the browser from a small rules file; the second belongs to Stripe (or your checkout function), because anything in `/data/codes.json` is public and anything computed in the browser can be edited. Keep amounts in integer cents, apply percentages to eligible lines only, round once, and write every error so the buyer knows what to do next ("You're 6,50 € away"), not just that it failed.

## Pattern

```json
// /data/codes.json: public codes only. Influencer and staff codes live in Stripe, never here.
{
  "WELCOME10": { "type": "percent", "value": 10, "label": "10 % off your first order" },
  "BREWGEAR5": { "type": "fixed", "value": 500, "label": "5,00 € off brewing gear", "for": "drippers and filters", "skus": ["dripper-02", "filters-100"], "minSubtotal": 3000 },
  "OCTSHIP":   { "type": "shipping", "label": "Free shipping in October", "minSubtotal": 2500, "startsAt": "2026-10-01T00:00:00+02:00", "endsAt": "2026-10-31T23:59:59+01:00" }
}
```

```html
<div data-promo class="border-t border-stone-200 py-4">
  <form data-promo-form novalidate>
    <label for="promo" class="block text-sm font-medium">Discount code</label>
    <div class="mt-1 flex gap-2">
      <input id="promo" name="code" autocomplete="off" autocapitalize="characters" spellcheck="false" aria-describedby="promo-msg"
             class="min-w-0 flex-1 rounded-md border border-stone-300 px-3 py-2 uppercase focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-stone-900 aria-invalid:border-red-600">
      <button class="rounded-md border border-stone-900 px-4 py-2 text-sm font-medium hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Apply</button>
    </div>
  </form>
  <div data-promo-applied hidden class="flex items-center justify-between gap-3 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
    <p><strong data-promo-code class="font-semibold"></strong> · <span data-promo-label></span></p>
    <button type="button" data-promo-remove class="underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-emerald-900">Remove<span class="sr-only"> discount code</span></button>
  </div>
  <p id="promo-msg" data-promo-msg aria-live="polite" class="mt-2 min-h-5 text-sm text-red-700"></p>
  <p data-promo-row hidden class="flex justify-between text-sm"><span>Discount</span><span data-promo-amount class="tabular-nums text-emerald-800"></span></p>
</div>
```

```js
// /js/discount.js
import { subscribe, format } from './cart.js';
const KEY = 'shop:code';
const rules = await fetch('/data/codes.json').then((r) => (r.ok ? r.json() : {})).catch(() => ({}));
const day = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', timeZone: 'Europe/Berlin' });
const $ = (s) => document.querySelector(`[data-promo${s}]`);
let code = (() => { try { return localStorage.getItem(KEY) ?? ''; } catch { return ''; } })();
let cart;

export const normalise = (raw) => raw.normalize('NFKC').toUpperCase().replace(/[\s-]/g, '');

export function evaluate(code, { items, subtotal }, now = new Date()) {
  const rule = rules[code];
  if (!rule) return { error: `We don't recognise "${code}". Check the spelling; codes have no spaces.` };
  if (rule.startsAt && now < new Date(rule.startsAt)) return { error: `${code} starts on ${day.format(new Date(rule.startsAt))}.` };
  if (rule.endsAt && now > new Date(rule.endsAt)) return { error: `${code} ended on ${day.format(new Date(rule.endsAt))}.` };
  const base = items.filter((i) => !rule.skus || rule.skus.includes(i.sku)).reduce((n, i) => n + i.total, 0);
  if (base === 0) return { error: `${code} is for ${rule.for ?? 'other products'}, and there are none in your cart.` };
  if (subtotal < (rule.minSubtotal ?? 0)) return { error: `${code} needs a subtotal of ${format(rule.minSubtotal)}. You're ${format(rule.minSubtotal - subtotal)} away.` };
  const amount = rule.type === 'percent' ? Math.round((base * rule.value) / 100) : rule.type === 'fixed' ? Math.min(rule.value, base) : 0;
  return { code, label: rule.label, amount, freeShipping: rule.type === 'shipping' };
}

function render() {
  const result = code ? evaluate(code, cart) : null;
  const applied = result && !result.error;
  $('-applied').hidden = !code;
  $('-form').hidden = Boolean(code);
  $('-code').textContent = code;
  $('-label').textContent = applied ? result.label : 'not applied yet';
  $('-msg').textContent = result?.error ?? '';
  $('-row').hidden = !applied || result.amount === 0;
  $('-amount').textContent = applied ? `−${format(result.amount)}` : '';
  document.dispatchEvent(new CustomEvent('discount:change', { detail: applied ? result : null }));   // totals and shipping listen
}

$('-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const input = e.target.elements.code;
  const next = normalise(input.value);
  if (!next) { $('-msg').textContent = 'Type a code first.'; input.focus(); return; }
  const result = evaluate(next, cart);
  input.setAttribute('aria-invalid', String(Boolean(result.error)));
  if (result.error) { $('-msg').textContent = result.error; input.focus(); return; }
  code = next;
  try { localStorage.setItem(KEY, code); } catch { /* still applied for this page */ }
  render();
  $('-remove').focus();
});
$('-remove').addEventListener('click', () => { code = ''; try { localStorage.removeItem(KEY); } catch {} render(); $('-form').elements.code.focus(); });
subscribe((snap) => { cart = snap; render(); });   // re-check whenever quantities change
```

At checkout, send `code` with the lines and let the function resolve it against Stripe's own Promotion Codes (create each in the Dashboard with the same code, limits and expiry):

```js
// functions/api/checkout.js, inside onRequestPost: read `const { lines, code } = await request.json()`, then after building `body`
if (code) {
  const res = await fetch(`https://api.stripe.com/v1/promotion_codes?code=${encodeURIComponent(code)}&active=true&limit=1`, { headers: { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}` } });
  const promo = (await res.json()).data?.[0];
  if (!promo) return Response.json({ error: `The code ${code} is no longer valid. Remove it and try again.` }, { status: 400 });
  body.delete('allow_promotion_codes');                 // Stripe rejects a session that sets both
  body.set('discounts[0][promotion_code]', promo.id);
}
```

## Variations

- **Code from a link**: `/cart/?code=WELCOME10` in a newsletter. On load, read `new URLSearchParams(location.search).get('code')`, run it through the same submit path, then `history.replaceState` to drop the parameter so a shared URL does not carry it.
- **Collapsed field**: wrap the form in `<details><summary>Have a discount code?</summary>…</details>` when most buyers have none; a big empty field sends people off to search for codes and some never come back.
- **Automatic discounts** ("10 % off 1 kg bags"): no field at all; evaluate a rule marked `"auto": true` on every cart change and show it as a labelled line, exactly like an applied code.
- **Stripe-only**: keep `allow_promotion_codes=true` and no field on your site. Simplest and safest, but the buyer sees the saving only on Stripe's page.

## Pitfalls

- `codes.json` is downloadable by anyone. Put only codes you would print on a postcard in it; single-use, staff and partner codes exist only in Stripe and are checked by the function.
- Silently dropping a code when the cart falls below the minimum feels like bait and switch. Keep the chip, say "not applied yet" with the amount still needed, and apply it again when the cart qualifies.
- A percentage of the whole subtotal when the rule covers two SKUs gives away too much. Filter eligible lines first, then `Math.round` once on their sum, so the preview matches Stripe to the cent.
- Dates without an offset are read in the buyer's time zone. Store ISO strings with `+01:00`/`+02:00` and format with `timeZone: 'Europe/Berlin'` so "ended 31 October" means your midnight.
- A free-shipping code must reach the shipping calculation (the `discount:change` event), and the free-shipping threshold is checked after the discount; see `web-ecommerce-shipping-and-tax`.
- Red text alone fails colour-blind and screen-reader users: the message is real text in a live region tied to the input with `aria-describedby`, and `aria-invalid` flips the border.

## Related skills

- `web-ecommerce-cart`
- `web-ecommerce-checkout-stripe`
- `web-ecommerce-shipping-and-tax`
- `web-form-validation`
- `web-form-input-states`
- `web-js-storage`
- `web-data-number-formatting`
