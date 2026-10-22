---
name: web-section-newsletter-signup
description: Build a newsletter signup section: an inline one-field form with a labelled input, honeypot, privacy line, and fetch submit with inline success and error states that still works without JavaScript, in light and dark variants with Tailwind v4. Use whenever a user asks for a "newsletter box", "subscribe form", "email signup", "join the list", or "mailing list section".
---

# Newsletter signup

An email form earns a subscriber only if it says what arrives and how often, and if submitting feels instant. The form must be a real `<form>` posting to a real endpoint so it works with scripts off; JavaScript then intercepts the submit, posts with `fetch`, and swaps the form for a success message in place, with focus moved so screen readers hear it. A honeypot field catches dumb bots without a CAPTCHA.

## Pattern

```html
<section class="border-y border-stone-200 bg-stone-50 py-16 dark:border-stone-800 dark:bg-stone-900" aria-labelledby="news-heading">
  <div class="mx-auto grid max-w-6xl gap-8 px-4 sm:px-6 lg:grid-cols-[1fr_minmax(0,28rem)] lg:items-center lg:px-8">
    <div class="max-w-xl">
      <h2 id="news-heading" class="text-2xl font-semibold tracking-tight text-balance text-stone-900 sm:text-3xl dark:text-stone-100">
        The Allotment Letter: one email on the first Sunday of each month
      </h2>
      <p class="mt-3 text-stone-600 dark:text-stone-400">
        What to sow this month on a Leeds plot, one recipe from the harvest, and the seed swap dates. Written by Tom Bellamy, read by 3,800 people.
      </p>
    </div>

    <form action="/api/subscribe" method="post" class="w-full" data-newsletter novalidate>
      <div class="flex flex-col gap-3 sm:flex-row">
        <div class="flex-1">
          <label for="news-email" class="sr-only">Email address</label>
          <input id="news-email" name="email" type="email" autocomplete="email" inputmode="email" required
                 placeholder="you@example.com"
                 class="w-full rounded-md border border-stone-300 bg-white px-4 py-3 text-base text-stone-900 placeholder:text-stone-400 focus-visible:border-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 aria-[invalid=true]:border-red-700 dark:border-stone-700 dark:bg-stone-950 dark:text-stone-100"
                 aria-describedby="news-privacy news-error">
        </div>
        <button type="submit"
                class="rounded-md bg-stone-900 px-5 py-3 text-base font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 disabled:opacity-60 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-white">
          Get the letter
        </button>
      </div>

      <!-- Honeypot: hidden from people, filled by naive bots. Server rejects any submission where it is non-empty. -->
      <div class="absolute -left-[9999px]" aria-hidden="true">
        <label for="news-website">Leave this empty</label>
        <input id="news-website" name="website" type="text" tabindex="-1" autocomplete="off">
      </div>

      <p id="news-error" class="mt-2 text-sm text-red-700 dark:text-red-400" role="alert" hidden></p>
      <p id="news-privacy" class="mt-3 font-mono text-xs text-stone-500">
        No sharing, no tracking pixels. Unsubscribe link in every email. <a href="/privacy" class="underline underline-offset-4">Privacy notice</a>.
      </p>
    </form>

    <p class="rounded-md border border-stone-300 bg-white p-4 text-sm text-stone-800 lg:col-start-2 dark:border-stone-700 dark:bg-stone-950 dark:text-stone-200"
       data-newsletter-success tabindex="-1" hidden>
      Check your inbox. The first letter lands on the first Sunday; until then, the last three are at <a href="/archive" class="underline underline-offset-4">the archive</a>.
    </p>
  </div>
</section>
```

```js
const form = document.querySelector('[data-newsletter]');
const success = document.querySelector('[data-newsletter-success]');
const email = form.elements.email;
const error = form.querySelector('#news-error');
const button = form.querySelector('button[type=submit]');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  error.hidden = true;
  email.removeAttribute('aria-invalid');

  if (!email.validity.valid) {
    error.textContent = 'Enter an email address like you@example.com.';
    error.hidden = false;
    email.setAttribute('aria-invalid', 'true');
    email.focus();
    return;
  }

  button.disabled = true;
  button.textContent = 'Sending';
  try {
    const res = await fetch(form.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ email: email.value, website: form.elements.website.value }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    form.hidden = true;
    success.hidden = false;
    success.focus();
  } catch {
    error.textContent = 'That did not go through. Try again, or email tom@allotmentletter.co.uk.';
    error.hidden = false;
    button.disabled = false;
    button.textContent = 'Get the letter';
  }
});
```

Why these choices:

- `action` and `method` are real, so the form posts normally without JavaScript; the server should answer that case with a plain HTML thank-you page and the fetch case with JSON.
- The label is `sr-only` because the placeholder and the button make the purpose obvious visually, but the input still has an accessible name. Never rely on the placeholder alone.
- `novalidate` disables the browser's bubble so the inline message appears instead; `email.validity.valid` still uses the native check.
- The success paragraph lives in the DOM from the start with `hidden` and `tabindex="-1"`, so `focus()` moves screen-reader focus to it the moment it appears.
- The honeypot is positioned off-screen rather than `display:none`, because some bots skip invisible fields; `tabindex="-1"` and `aria-hidden` keep it out of the keyboard and reader order.
- The privacy line says what will not happen (no sharing, no pixels), which is what the hesitating reader is asking.

## Variations

- **Dark**: section `bg-stone-950 border-stone-800`, input `bg-stone-900 border-stone-700`, button inverts to `bg-stone-100 text-stone-900`. The success box becomes `bg-stone-900 border-stone-700`.
- **Stacked, centred, inside a CTA band**: drop the two-column grid, `max-w-md mx-auto text-center`, input and button stacked (`flex-col`) with `w-full` button. See `web-section-cta-band`.
- **With a first-name field**: add a second input before the email, `sm:grid sm:grid-cols-[1fr_1.4fr_auto]`; keep labels visible (`text-sm font-medium`) once there is more than one field.
- **Footer version**: `text-sm` input and button, no heading, one-line description; the shared markup lives in `web-layout-footer`.

## Pitfalls

- A success state that replaces the form with `innerHTML` and no focus move is silent for screen-reader users; show a pre-existing element and focus it.
- Submitting with `fetch` but leaving `action="#"` means a script error or a blocked request leaves the user with a form that does nothing. Keep the real endpoint.
- `type="email"` with `required` and no `novalidate` shows a browser bubble that disappears in two seconds and cannot be styled; handle validation inline as above.
- A visible "Leave this empty" honeypot (because the off-screen class got purged) confuses everyone; keep the class in the HTML source so Tailwind generates it, and test with CSS disabled.
- Double submits on slow connections create duplicate subscribers; disable the button while the request is in flight and re-enable only on failure.
- "Subscribe to our newsletter" with no frequency or content promise converts poorly. Name the thing, the cadence and the author.

## Related skills

- `web-form-submit-with-fetch`
- `web-form-validation`
- `web-form-input-states`
- `web-layout-footer`
- `web-section-cta-band`
- `web-a11y-aria-patterns`
