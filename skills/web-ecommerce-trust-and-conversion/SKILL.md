---
name: web-ecommerce-trust-and-conversion
description: Add the trust signals that actually lift conversion on a static shop (guarantee, returns, real reviews, clear contact details) plus a calm abandoned-cart reminder, in Tailwind v4. Refuses dark patterns: fake countdowns, fake "12 people viewing", pre-ticked add-ons, confirmshaming. Use whenever a user asks for "trust badges", "increase sales", "urgency", "abandoned cart" or "reduce drop-off".
---

# Trust and conversion, without tricks

A first-time buyer is asking three questions: is this a real business, what if it goes wrong, and will I get what I see. Answer each with a fact, placed where the doubt arises (next to the buy button, in the cart, at the payment step). Facts are policies you actually keep, contact details a person answers, and reviews you did not edit. Everything below is also true if the visitor checks it, which is why it keeps working. Tricks raise a number this week and cost you the customer, the review and, in the EU and UK, possibly a regulator's letter.

## Pattern

```html
<!-- Under the add-to-cart button: only promises that are in the policy pages -->
<ul role="list" class="mt-6 space-y-3 text-sm text-stone-700">
  <li class="flex gap-3"><span aria-hidden="true" class="font-semibold text-emerald-700">&#10003;</span>
    <p><strong class="font-medium text-stone-900">30 days to return it.</strong> Free return label in the box. <a href="/returns/" class="underline underline-offset-4">Returns policy</a></p></li>
  <li class="flex gap-3"><span aria-hidden="true" class="font-semibold text-emerald-700">&#10003;</span>
    <p><strong class="font-medium text-stone-900">Ships from Leipzig in 1 working day.</strong> <a href="/shipping/" class="underline underline-offset-4">Delivery times and costs</a></p></li>
  <li class="flex gap-3"><span aria-hidden="true" class="font-semibold text-emerald-700">&#10003;</span>
    <p><strong class="font-medium text-stone-900">4.7 from 212 reviews</strong>, including the 3-star ones. <a href="#reviews" class="underline underline-offset-4">Read them</a></p></li>
</ul>

<!-- Contact: footer, cart and checkout. A named person and hours beat a form-only page -->
<address class="mt-8 text-sm not-italic text-stone-700">
  <p class="font-medium text-stone-900">Questions before you order?</p>
  <p>Email <a href="mailto:help@example.com" class="underline underline-offset-4">help@example.com</a>
     or call <a href="tel:+493415550142" class="underline underline-offset-4">+49 341 555 0142</a>, Mon to Fri, 9:00 to 17:00 Berlin time.</p>
  <p class="mt-1 text-stone-600">Example Roasters GmbH, Kolonnadenstrasse 4, 04109 Leipzig. Registered: HRB 12345, VAT ID DE123456789.</p>
</address>

<!-- Abandoned-cart reminder: shown once, on the next visit, never as a popup -->
<aside id="cart-reminder" aria-label="Saved cart" hidden class="fixed inset-x-4 bottom-4 z-30 mx-auto flex max-w-md items-center gap-4 rounded-lg border border-stone-300 bg-white p-4 text-sm shadow-lg">
  <p class="flex-1"><span data-reminder-text>Your cart is saved.</span> Nothing is reserved, so stock can change.</p>
  <a href="/cart/" class="rounded-md bg-stone-900 px-3 py-2 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Back to cart</a>
  <button type="button" data-reminder-dismiss class="rounded-md px-2 py-2 text-stone-600 hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-stone-900"><span class="sr-only">Dismiss</span>&times;</button>
</aside>
```

```js
// /js/cart-reminder.js: runs on every page except /cart/ and /checkout/; uses the cart.js record
import { snapshot, format } from './cart.js';

const IDLE_MS = 30 * 60 * 1000;                      // cart untouched for 30 minutes counts as left behind
const box = document.getElementById('cart-reminder');
const read = (key) => { try { return JSON.parse(localStorage.getItem(key)) ?? {}; } catch { return {}; } };
const { count, subtotal } = snapshot();
const updated = read('shop:cart').updated ?? 0;

if (box && count > 0 && Date.now() - updated > IDLE_MS && read('shop:reminder').seen !== updated) {
  box.querySelector('[data-reminder-text]').textContent = `You left ${count} ${count === 1 ? 'item' : 'items'} (${format(subtotal)}) in your cart.`;
  box.hidden = false;
  try { localStorage.setItem('shop:reminder', JSON.stringify({ seen: updated })); } catch { /* shown again next time, acceptable */ }
}
box?.querySelector('[data-reminder-dismiss]').addEventListener('click', () => { box.hidden = true; });
```

## Variations

- **Email reminder**: only for visitors who typed an email at the start of checkout and ticked an unticked box saying they want a reminder. Send one email after about an hour with the cart contents and a link, one more after a day at most, and an unsubscribe link in both. This needs an email service; the static site only posts the address.
- **Where the signals go**: guarantee and returns beside the price, contact in the cart and payment step, reviews above the fold of the product page. At payment, add what happens next: "Confirmation by email in a minute, tracking when it ships".
- **Honest urgency**: say what is true. A real stock count from your data ("3 left"), a sale with an end date written as a date ("until Sunday 3 November"), a real dispatch cut-off ("order by 14:00 to ship today").
- **Sizing and fit doubts**: a short "How it fits" answer next to the size picker converts better than a badge.

## Pitfalls

- Refused and left out on purpose: **fake countdown timers** (a clock that resets on reload), **fake "12 people viewing" or "only 2 left"** numbers that are not read from real data, **pre-ticked add-ons** (insurance, newsletter, extra product), and **confirmshaming** ("No thanks, I don't like saving money"). Use a plain "No thanks" with equal weight, add-ons unticked, and counts only from real data.
- Also refuse the neighbours: hidden fees revealed at the last step, exit-intent popups, forced account creation, and a cancellation path longer than the sign-up.
- Do not show payment or security seals you have not earned, and do not treat "SSL secure" as a feature; HTTPS is the baseline. Show the payment methods you really accept.
- Show real reviews only, bad ones included, and never write `AggregateRating` structured data for numbers you made up; see `web-ecommerce-reviews`. Remove reviews only for abuse, not for score.
- A guarantee must match the returns page word for word, including who pays postage. A promise you quietly narrow later is worse than none.
- The reminder reads only this device's storage and sends nothing anywhere, so it needs no tracking consent. Keep it to one appearance per cart state, and do not steal focus or cover the checkout button.

## Related skills

- `web-ecommerce-cart`
- `web-ecommerce-reviews`
- `web-ecommerce-shipping-and-tax`
- `web-ecommerce-variants-and-stock`
- `web-ecommerce-checkout-stripe`
- `web-page-contact`
- `web-craft-copy-that-sounds-human`
- `web-ship-analytics-and-privacy`
