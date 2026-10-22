---
name: web-ecommerce-order-status
description: 'Build order confirmation and tracking pages for a static shop: a thank-you page after Stripe Checkout, an order lookup form, a status timeline (paid, packed, shipped, delivered) from a JSON file or webhook-fed endpoint, and a "what to do if" section. Use whenever a user asks for "order tracking", "track my order", "order status", "thank you page" or "order confirmation".'
---

# Order confirmation and tracking

After paying, a buyer wants three things: proof it worked, when it arrives, and who to ask if it doesn't. A static site can serve all three without a database: the thank-you page reads the Stripe `session_id` from the URL and shows a reference; the tracking page loads `/orders/<token>.json`, a small file the shop owner writes when an order moves (or a `/api/orders/<token>` endpoint fed by the `checkout.session.completed` webhook), and renders it as a timeline. The token is an unguessable string from the confirmation email, never a sequential order number, because any file under `/orders/` is public to whoever knows its name.

## Pattern

```json
// /orders/k7m2-q9ax-4tpd.json   (written by the owner or by the webhook function)
{
  "reference": "MC-10482",
  "placed": "2026-10-19T14:12:00+02:00",
  "email_hint": "f***@posteo.de",
  "items": [{ "name": "Finca La Soledad, 480 g, whole bean", "qty": 2, "total": 2900 }, { "name": "Paper filters, size 02, 100 pack", "qty": 1, "total": 420 }],
  "shipping": 390, "total": 3710, "currency": "EUR",
  "status": "shipped",
  "steps": [
    { "key": "paid",      "at": "2026-10-19T14:12:00+02:00" },
    { "key": "packed",    "at": "2026-10-20T09:40:00+02:00" },
    { "key": "shipped",   "at": "2026-10-20T16:05:00+02:00", "carrier": "DHL", "tracking": "00340434161094000001", "url": "https://www.dhl.de/de/privatkunden/pakete-empfangen/verfolgen.html?piececode=00340434161094000001" },
    { "key": "delivered", "at": null, "expected": "2026-10-22" }
  ]
}
```

```html
<main id="main" class="mx-auto max-w-2xl px-4 py-10">
  <form data-lookup class="rounded-lg border border-stone-200 p-5" aria-labelledby="lookup-title">
    <h1 id="lookup-title" class="text-2xl font-semibold tracking-tight">Track your order</h1>
    <label for="token" class="mt-4 block text-sm font-medium">Tracking code from your confirmation email</label>
    <div class="mt-1 flex gap-2">
      <input id="token" name="token" required pattern="[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}" autocomplete="off" spellcheck="false" placeholder="k7m2-q9ax-4tpd" class="flex-1 rounded-md border border-stone-300 px-3 py-2 font-mono text-sm">
      <button type="submit" class="rounded-md bg-stone-900 px-4 py-2 text-sm font-medium text-white">Look up</button>
    </div>
    <p role="alert" data-lookup-error class="mt-2 text-sm text-red-700"></p>
  </form>

  <article data-order hidden class="mt-10">
    <header>
      <p class="text-sm text-stone-500">Order <span data-reference class="font-mono"></span>, placed <time data-placed></time></p>
      <h2 class="mt-1 text-2xl font-semibold" data-headline></h2>
    </header>

    <ol data-timeline class="relative mt-8 space-y-6 border-l-2 border-stone-200 pl-6"></ol>

    <h3 class="mt-10 text-lg font-semibold">What you ordered</h3>
    <ul role="list" data-items class="mt-3 divide-y divide-stone-200 text-sm"></ul>
    <p class="mt-3 flex justify-between text-sm"><span>Shipping</span><span data-shipping class="tabular-nums"></span></p>
    <p class="mt-1 flex justify-between font-medium"><span>Total paid</span><span data-total class="tabular-nums"></span></p>

    <section class="mt-10 rounded-lg bg-stone-50 p-5 text-sm" aria-labelledby="help-title">
      <h3 id="help-title" class="font-semibold">If something is off</h3>
      <dl class="mt-3 space-y-3">
        <div><dt class="font-medium">It has not arrived by the expected date</dt><dd class="text-stone-700">Give it two more working days, then email <a href="mailto:hello@marrowcoffee.de" class="underline underline-offset-4">hello@marrowcoffee.de</a> with the order number. We open a claim with the carrier the same day.</dd></div>
        <div><dt class="font-medium">Wrong or damaged item</dt><dd class="text-stone-700">Send a photo and we ship a replacement before you send anything back.</dd></div>
        <div><dt class="font-medium">Want to cancel</dt><dd class="text-stone-700">Possible until the order is packed; after that, return it unopened within 30 days for a full refund.</dd></div>
      </dl>
    </section>
  </article>
</main>
```

```js
// /js/order-status.js
const LABELS = { paid: 'Payment received', packed: 'Packed', shipped: 'Handed to carrier', delivered: 'Delivered' };
const money = (cents, currency) => new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(cents / 100);
const when = (iso) => new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso));
const day = (iso) => new Intl.DateTimeFormat('de-DE', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date(iso));

const form = document.querySelector('[data-lookup]');
const article = document.querySelector('[data-order]');

async function show(token) {
  const error = form.querySelector('[data-lookup-error]');
  error.textContent = '';
  const res = await fetch(`/orders/${encodeURIComponent(token)}.json`, { cache: 'no-store' }).catch(() => null);
  if (!res?.ok) { error.textContent = 'No order with that code. Check the email again; the code has three groups of four characters.'; return; }
  const o = await res.json();
  article.querySelector('[data-reference]').textContent = o.reference;
  Object.assign(article.querySelector('[data-placed]'), { textContent: when(o.placed), dateTime: o.placed });
  const current = o.steps.find((s) => s.key === o.status);
  const next = o.steps.find((s) => !s.at);
  article.querySelector('[data-headline]').textContent =
    o.status === 'delivered' ? `Delivered on ${day(current.at)}` : next?.expected ? `On its way, expected ${day(next.expected)}` : LABELS[o.status];

  article.querySelector('[data-timeline]').innerHTML = o.steps.map((s) => `
    <li class="relative" ${s.key === o.status ? 'aria-current="step"' : ''}>
      <span aria-hidden="true" class="absolute -left-[1.95rem] top-1 size-3.5 rounded-full border-2 ${s.at ? 'border-stone-900 bg-stone-900' : 'border-stone-300 bg-white'}"></span>
      <p class="${s.at ? 'font-medium' : 'text-stone-500'}">${LABELS[s.key]}</p>
      <p class="text-sm text-stone-600">${s.at ? when(s.at) : s.expected ? `Expected ${day(s.expected)}` : 'Not yet'}</p>
      ${s.tracking ? `<p class="text-sm">${s.carrier} <a href="${s.url}" class="font-mono underline underline-offset-4" rel="noopener">${s.tracking}</a></p>` : ''}
    </li>`).join('');

  article.querySelector('[data-items]').innerHTML = o.items.map((i) => `<li class="flex justify-between py-2"><span>${i.qty} × ${i.name}</span><span class="tabular-nums">${money(i.total, o.currency)}</span></li>`).join('');
  article.querySelector('[data-shipping]').textContent = money(o.shipping, o.currency);
  article.querySelector('[data-total]').textContent = money(o.total, o.currency);
  article.hidden = false;
  history.replaceState(null, '', `?t=${token}`);
}

form.addEventListener('submit', (e) => { e.preventDefault(); show(form.elements.token.value.trim().toLowerCase()); });
const fromUrl = new URLSearchParams(location.search).get('t');
if (fromUrl) { form.elements.token.value = fromUrl; show(fromUrl); }
```

**Thank-you page** (`/thanks/?session_id=cs_test_…`): heading "Thanks, your order is in", one sentence that the confirmation email with the tracking code is on its way to the address they typed at checkout, the last 8 characters of `session_id` as a reference to quote, `clear()` from `cart.js`, and a link back to the shop. Do not try to display the order contents from `localStorage`; the cart may have changed in another tab, and Stripe's receipt is the authority.

## Variations

- **Webhook-fed endpoint**: the function that receives `checkout.session.completed` writes the same JSON shape to KV under a random token and emails it; `show()` fetches `/api/orders/${token}` instead. Owner updates (packed, shipped) come from a tiny admin form or a CLI script that writes to KV.
- **Owner-uploaded JSON**: a spreadsheet row per order exported by a 15-line script into `/orders/*.json` and deployed; fine for a few orders a day.
- **Email + order number lookup**: only with the endpoint variant, where the server checks both; a static JSON cannot keep a secret from the person who already found it.
- **Printable confirmation**: `@media print` hides the form and help box; buyers do print these.

## Pitfalls

- Sequential file names (`/orders/10482.json`) let anyone enumerate every customer's order; use 12 random characters and tell the buyer where to find them.
- Putting the full email or address in the JSON leaks it to anyone with the link; a hint (`f***@posteo.de`) is enough to reassure.
- "Expected Wednesday" without the date is wrong by Thursday; print the date, and compute the headline from data, not from copy written on Monday.
- `fetch` of a JSON that was just redeployed may be cached by the CDN; `cache: 'no-store'` and a short `Cache-Control` on `/orders/*`.
- A timeline of four grey circles with no `aria-current` is a decoration; the current step is marked in the markup, not only by colour.
- The help section is the most-read part of the page after the headline; write it as answers to the three real questions, in the voice of `web-craft-copy-that-sounds-human`.

## Related skills

- `web-ecommerce-checkout-stripe`
- `web-ecommerce-cart`
- `web-section-steps-timeline`
- `web-js-fetch-and-apis`
- `web-data-number-formatting`
- `web-craft-copy-that-sounds-human`
- `web-design-empty-and-error-states`
