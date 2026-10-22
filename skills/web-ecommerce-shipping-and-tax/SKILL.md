---
name: web-ecommerce-shipping-and-tax
description: Show shipping options, costs, free-shipping thresholds and delivery-date estimates, and display tax correctly by region (VAT-inclusive in the EU and UK, tax added at checkout in the US) in a static shop, with integer minor-unit prices and Intl formatting. Use whenever a user asks about "shipping", "delivery date", "free shipping over", "VAT", "tax included" or "sales tax".
---

# Shipping and tax display

Two things surprise shoppers late and cost you the order: a shipping fee they did not expect and a tax line that changes the total. Show both on the product and cart pages, in the format their region expects. Keep one module with the rules as data: prices as integers in minor units (490 is 4.90), tax rates in basis points (1900 is 19 %), and all formatting through `Intl`. The module below computes the display; the checkout (`web-ecommerce-checkout-stripe`) must recompute the real amounts on its own.

## Pattern

```js
// /js/shipping.js  (all money is an integer in minor units: 490 = 4.90)
export const SHOP_TZ = 'Europe/Berlin';
const CUTOFF_HOUR = 14;                                                  // orders after 14:00 shop time ship the next business day
const HOLIDAYS = new Set(['2026-12-25', '2026-12-26', '2027-01-01']);   // ISO dates the warehouse is shut

export const REGIONS = {
  DE: { locale: 'de-DE', currency: 'EUR', tax: { mode: 'inclusive', rate: 1900 } },   // rate in basis points: 1900 = 19 %
  GB: { locale: 'en-GB', currency: 'GBP', tax: { mode: 'inclusive', rate: 2000 } },
  US: { locale: 'en-US', currency: 'USD', tax: { mode: 'exclusive', rate: 0 } },      // sales tax depends on the ship-to address
};

export const OPTIONS = [
  { id: 'standard', label: 'Standard',          price: 490, days: [3, 5], freeFrom: 6000 },
  { id: 'express',  label: 'Express',           price: 990, days: [1, 2] },
  { id: 'pickup',   label: 'Pick up in Leipzig', price: 0,   days: [1, 1] },
];

export function formatMoney(minor, region) {
  const { locale, currency } = REGIONS[region];
  const nf = new Intl.NumberFormat(locale, { style: 'currency', currency });
  return nf.format(minor / 10 ** nf.resolvedOptions().maximumFractionDigits);   // JPY has 0 decimals, KWD has 3
}

// VAT contained in a gross price: gross * rate / (1 + rate), rounded once
export const vatIncluded = (gross, rate) => Math.round((gross * rate) / (10000 + rate));

export function taxNote(price, region) {
  const { mode, rate } = REGIONS[region].tax;
  return mode === 'inclusive'
    ? `Incl. ${rate / 100}% VAT (${formatMoney(vatIncluded(price, rate), region)})`
    : 'Plus tax, calculated at checkout';
}

export const shippingCost = (opt, subtotal) => (opt.freeFrom != null && subtotal >= opt.freeFrom ? 0 : opt.price);
export function freeShippingHint(subtotal, region) {
  const std = OPTIONS.find((o) => o.freeFrom != null);
  return std && subtotal < std.freeFrom ? `Add ${formatMoney(std.freeFrom - subtotal, region)} for free shipping` : '';
}

const iso = (d) => d.toLocaleDateString('sv-SE');                      // YYYY-MM-DD in local time
const isBusinessDay = (d) => ![0, 6].includes(d.getDay()) && !HOLIDAYS.has(iso(d));
export function addBusinessDays(from, n) {
  const d = new Date(from);
  while (n > 0) { d.setDate(d.getDate() + 1); if (isBusinessDay(d)) n--; }
  return d;
}
const shopHour = (now) => Number(new Intl.DateTimeFormat('en-GB', { hour: 'numeric', hourCycle: 'h23', timeZone: SHOP_TZ }).format(now));

// Delivery window as a locale-formatted string: 'Mon, Oct 26 – Wed, Oct 28'
export function deliveryEstimate(opt, region, now = new Date()) {
  const late = shopHour(now) >= CUTOFF_HOUR;
  const dispatch = isBusinessDay(now) && !late ? now : addBusinessDays(now, 1);
  const [min, max] = opt.days.map((n) => addBusinessDays(dispatch, n));
  const fmt = new Intl.DateTimeFormat(REGIONS[region].locale, { weekday: 'short', day: 'numeric', month: 'short' });
  return iso(min) === iso(max) ? fmt.format(min) : fmt.formatRange(min, max);
}
```

```html
<p class="text-lg tabular-nums"><span data-price>14,50 €</span>
  <span data-tax-note class="block text-sm text-stone-600">Incl. 19% VAT (2,32 €)</span></p>

<fieldset class="mt-6">
  <legend class="font-medium">Delivery</legend>
  <ul role="list" data-shipping class="mt-2 space-y-2"></ul>
  <p data-free-hint class="mt-2 text-sm text-stone-600"></p>
</fieldset>
<p class="mt-2 text-xs text-stone-500">Estimates assume dispatch Monday to Friday. Order by 14:00 (Berlin) to ship today.</p>
```

```js
// /js/shipping-ui.js: re-render when the cart changes
import { subscribe } from './cart.js';
import { OPTIONS, REGIONS, formatMoney, shippingCost, deliveryEstimate, freeShippingHint } from './shipping.js';

const stored = localStorage.getItem('shop:region');
const region = REGIONS[stored] ? stored : 'DE';          // let the visitor change it; never guess silently
const list = document.querySelector('[data-shipping]');

subscribe(({ subtotal }) => {
  const chosen = list.querySelector(':checked')?.value ?? OPTIONS[0].id;
  list.innerHTML = OPTIONS.map((o) => {
    const cost = shippingCost(o, subtotal);
    return `<li><label class="flex cursor-pointer items-start gap-3 rounded-md border border-stone-300 p-3 has-checked:border-stone-900 has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-stone-900">
      <input type="radio" name="shipping" value="${o.id}" class="mt-1" ${o.id === chosen ? 'checked' : ''}>
      <span class="flex-1"><span class="block font-medium">${o.label}</span>
        <span class="block text-sm text-stone-600">Arrives ${deliveryEstimate(o, region)}</span></span>
      <span class="tabular-nums">${cost === 0 ? 'Free' : formatMoney(cost, region)}</span></label></li>`;
  }).join('');
  document.querySelector('[data-free-hint]').textContent = freeShippingHint(subtotal, region);
});
```

## Variations

- **Reduced VAT rates**: give each product a `taxRate` (coffee is 7 % in Germany, books 7 %, most goods 19 %) and pass it to `vatIncluded` instead of the region rate.
- **US**: keep catalogue prices without tax, show "Plus tax, calculated at checkout", and let Stripe Tax or a similar service price the ship-to address. Never hardcode one state's rate.
- **B2B toggle**: store net prices, show gross by default for consumers and add an "excl. VAT" switch that swaps `taxNote` for a net label.
- **Rates by weight or zone**: replace `price` with a function `(subtotal, weightGrams, country) => minor`; keep the same `OPTIONS` shape so the UI does not change.

## Pitfalls

- In the EU and UK, prices shown to consumers include VAT; in the US they exclude sales tax. Show the region's convention everywhere (listing, cart, checkout) and check current rules for the countries you sell to, because this is law, not styling.
- Round VAT once per line or per order, as your invoice does, never per unit then summed; totals must match the checkout to the cent.
- Never use `toFixed(2)` or divide by 100: yen has no decimals and dinar has three. `resolvedOptions().maximumFractionDigits` gives the right divisor.
- Show shipping cost before the last checkout step; unexpected costs are one of the top reasons for abandoned carts. A flat estimate with "final price at checkout" beats silence.
- A delivery date is a promise. Use a range, count business days and your closing days, state the cut-off hour in the shop time zone, and say "estimated". The code above runs in the visitor's time zone for day arithmetic, so recompute on the server for order emails.
- Radio group inside a `fieldset` with a `legend` gives screen readers the group name; keep the price inside the label so it is announced with the option.

## Related skills

- `web-ecommerce-cart`
- `web-ecommerce-checkout-stripe`
- `web-ecommerce-discount-codes`
- `web-ecommerce-order-status`
- `web-ecommerce-trust-and-conversion`
- `web-i18n-dates-currency`
- `web-data-number-formatting`
