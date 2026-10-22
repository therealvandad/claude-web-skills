---
name: web-ecommerce-checkout-stripe
description: 'Add checkout to a static site with Stripe in test mode: Payment Links for single "buy now" buttons, or a tiny serverless function that creates a Checkout Session from the localStorage cart (prices from its own list, never the client), plus success and cancel pages. Use whenever a user says "checkout", "take payments", "Stripe", "buy button" or "pay with card".'
---

# Checkout from a static site with Stripe

A static site cannot take card details itself and should not try. Hand the payment to Stripe-hosted Checkout, which handles cards, wallets, 3-D Secure, VAT and receipts, and comes back to your success page. Two routes: a **Payment Link** is a URL you make in the Stripe Dashboard, zero code, right for one product per button; a **Checkout Session** is created on demand by a 20-line serverless function when the cart holds several products. In both, the price lives in Stripe or in the function, so nothing a visitor edits in DevTools can change what they pay. Build and test everything with test-mode keys (`sk_test_…`, `pk_test_…`) and the test card `4242 4242 4242 4242` (any future expiry, any CVC, any postcode); switch to live keys only in the hosting provider's secret settings, never in a file that is deployed.

## Pattern

**A. Payment Link, one product, no cart.** Dashboard → Payment Links → New, pick the product (Finca La Soledad 480 g, 14.50 €), allow adjustable quantity, set the confirmation page to `https://shop.example/thanks/`. Use the test-mode link on the page:

```html
<a href="https://buy.stripe.com/test_7sI5kE1Ab9Kq0Zq000?prefilled_email=&client_reference_id=soledad-480"
   class="inline-block rounded-md bg-stone-900 px-5 py-3 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">
  Buy now, 14,50 €
</a>
```

**B. Checkout Session from the cart.** The page posts `[{ sku, qty }]` to a function; the function maps SKUs to test-mode Price IDs and asks Stripe for a session URL.

```html
<main id="main" class="mx-auto max-w-lg px-4 py-10">
  <h1 class="text-2xl font-semibold">Checkout</h1>
  <ul role="list" data-summary class="mt-6 divide-y divide-stone-200 text-sm"></ul>
  <p class="mt-4 flex justify-between font-medium"><span>Subtotal</span><span data-subtotal class="tabular-nums"></span></p>
  <p class="text-xs text-stone-500">Shipping and VAT are calculated on the next step, before you pay.</p>
  <button type="button" data-pay class="mt-6 w-full rounded-md bg-stone-900 px-5 py-3 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 disabled:opacity-50">Continue to payment</button>
  <p role="alert" data-error class="mt-3 text-sm text-red-700"></p>
  <p class="mt-6 text-xs text-stone-500">Payment is handled by Stripe. We never see your card number.</p>
</main>
```

```js
// /js/checkout.js
import { snapshot, format } from './cart.js';
const { items, subtotal } = snapshot();
document.querySelector('[data-summary]').innerHTML = items.map((i) => `<li class="flex justify-between py-2"><span>${i.qty} × ${i.name}</span><span class="tabular-nums">${format(i.total)}</span></li>`).join('');
document.querySelector('[data-subtotal]').textContent = format(subtotal);

const button = document.querySelector('[data-pay]');
button.disabled = items.length === 0;
button.addEventListener('click', async () => {
  button.disabled = true; button.textContent = 'Opening secure payment…';
  try {
    const res = await fetch('/api/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lines: items.map(({ sku, qty }) => ({ sku, qty })) }) });
    const data = await res.json();
    if (!res.ok || !data.url) throw new Error(data.error ?? 'Checkout unavailable');
    location.href = data.url;                              // Stripe-hosted page; cart stays until /thanks/
  } catch (error) {
    document.querySelector('[data-error]').textContent = `We couldn't start the payment (${error.message}). Nothing was charged. Try again in a minute or email hello@shop.example.`;
    button.disabled = false; button.textContent = 'Continue to payment';
  }
});
```

```js
// functions/api/checkout.js  (Cloudflare Pages Function; Netlify/Vercel need only a different export shape)
const PRICES = {                       // test-mode Price IDs from the Dashboard; the function is the price list
  'soledad-480': 'price_1QzTestSoledad480',
  'dripper-02':  'price_1QzTestDripper02',
  'filters-100': 'price_1QzTestFilters100',
};
export async function onRequestPost({ request, env }) {
  const { lines } = await request.json().catch(() => ({}));
  if (!Array.isArray(lines) || lines.length === 0 || lines.length > 20) return Response.json({ error: 'Empty or invalid cart' }, { status: 400 });

  const body = new URLSearchParams({
    mode: 'payment',
    success_url: 'https://shop.example/thanks/?session_id={CHECKOUT_SESSION_ID}',
    cancel_url: 'https://shop.example/cart/?cancelled=1',
    'automatic_tax[enabled]': 'true',
    'shipping_address_collection[allowed_countries][0]': 'DE',
    'shipping_address_collection[allowed_countries][1]': 'AT',
    allow_promotion_codes: 'true',
  });
  lines.forEach(({ sku, qty }, i) => {
    if (!PRICES[sku]) throw new Error(`unknown sku ${sku}`);
    body.set(`line_items[${i}][price]`, PRICES[sku]);
    body.set(`line_items[${i}][quantity]`, String(Math.min(20, Math.max(1, Math.trunc(qty) || 1))));
  });

  const res = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`, 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  const session = await res.json();
  if (!res.ok) { console.error(session.error); return Response.json({ error: 'Payment provider error' }, { status: 502 }); }
  return Response.json({ url: session.url });
}
```

Set `STRIPE_SECRET_KEY=sk_test_…` as an environment variable in the host's dashboard (Cloudflare: Settings → Variables, encrypted). Success page `/thanks/`: thank the buyer, show the order reference from `session_id`, call `clear()` from `cart.js`, link to `web-ecommerce-order-status`. Cancel page is the cart with a one-line note: "Payment cancelled, nothing was charged. Your cart is still here."

## Variations

- **Digital goods**: no `shipping_address_collection`; set `success_url` to a page that fetches the download link from a function which verifies `session.payment_status === 'paid'` first.
- **Collect the buyer's phone or a gift message**: `phone_number_collection[enabled]=true` and `custom_fields[0][key]=gift_note&custom_fields[0][label][type]=custom&custom_fields[0][label][custom]=Gift message&custom_fields[0][type]=text`.
- **Fulfilment**: a second function receives the `checkout.session.completed` webhook (verify the `Stripe-Signature` header with the webhook secret), stores the order in KV or emails you; the success page alone is not proof of payment, a buyer can close the tab before it loads.
- **Embedded Checkout** (`ui_mode=embedded`) keeps the buyer on your domain but needs Stripe.js on the page; the hosted redirect needs no script and no publishable key.

## Pitfalls

- A secret key in `main.js`, in HTML, or committed in `.env` is a live-mode disaster waiting for the key swap. Only the function reads `env.STRIPE_SECRET_KEY`; the browser never sees a `sk_` string. Test-mode keys leak less dangerously, but the habit is the point.
- Trusting client prices (`unit_amount` from the request body) lets anyone buy the grinder for 1 cent; map SKUs to Price IDs server-side or keep an amount table in the function.
- Clearing the cart when the user clicks "Continue to payment" loses it if they cancel; clear only on `/thanks/`.
- Forgetting `{CHECKOUT_SESSION_ID}` in `success_url` leaves the thanks page with nothing to show or verify.
- Payment Links are per product; a Payment Link with "adjustable quantity" is a cart of one. Several products need a Session.
- Test with declines too: `4000 0000 0000 9995` is declined for insufficient funds; the cancel path and the error copy must read well.
- Stripe-hosted Checkout handles VAT and shipping copy; your own page must not promise a total it cannot compute. "Shipping and VAT on the next step" is honest.

## Related skills

- `web-ecommerce-cart`
- `web-ecommerce-order-status`
- `web-ecommerce-discount-codes`
- `web-ecommerce-shipping-and-tax`
- `web-form-submit-with-fetch`
- `web-js-fetch-and-apis`
- `web-ship-static-hosting`
