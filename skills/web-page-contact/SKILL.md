---
name: web-page-contact
description: 'Build a contact page in Tailwind v4: a short form beside the address, hours, phone and email, an accessible map embed, "which channel for what" guidance, and an inline success state. Use whenever a user asks for a contact page, contact us, "get in touch", enquiry form, support contact, booking request or "how do people reach us".'
---

# Contact page

People land here with one question: what is the fastest way to get an answer to my thing? So the page tells them which channel is for what before showing a form, puts the form and the direct details side by side (`1.1fr_0.9fr`: the form is the main task, the details are the alternative), and after submitting replaces the form with a specific promise ("we reply within one working day, from this address") instead of a generic thank-you. Hours, address and map come last; they matter only to the people who are coming in person.

## Pattern

```html
<main id="main" class="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">

  <!-- 1. Heading and routing: what goes where -->
  <header class="max-w-[40rem]">
    <h1 class="text-4xl font-semibold tracking-tight sm:text-5xl">Contact</h1>
    <p class="mt-4 text-lg text-stone-600">Order problems go fastest by phone. Trade and wholesale enquiries use the form. Press: <a href="mailto:press@hale-ceramics.co.uk" class="underline underline-offset-4">press@hale-ceramics.co.uk</a>.</p>
  </header>

  <div class="mt-14 grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:gap-20">

    <!-- 2. Form: five fields, one submit. Replaced by the success block after a fetch submit. -->
    <section aria-labelledby="form-heading" data-contact>
      <h2 id="form-heading" class="text-xl font-semibold">Send a message</h2>
      <form action="/api/contact" method="post" class="mt-6 grid gap-5" novalidate>
        <div class="grid gap-5 sm:grid-cols-2">
          <div>
            <label for="name" class="block text-sm font-medium">Name</label>
            <input id="name" name="name" autocomplete="name" required class="mt-1.5 w-full rounded-md border border-stone-300 px-3 py-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">
          </div>
          <div>
            <label for="email" class="block text-sm font-medium">Email</label>
            <input id="email" name="email" type="email" autocomplete="email" required class="mt-1.5 w-full rounded-md border border-stone-300 px-3 py-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">
          </div>
        </div>
        <div>
          <label for="topic" class="block text-sm font-medium">What is it about?</label>
          <select id="topic" name="topic" class="mt-1.5 w-full rounded-md border border-stone-300 px-3 py-2">
            <option value="trade">Trade or wholesale</option>
            <option value="commission">A commission</option>
            <option value="order">An existing order</option>
            <option value="other">Something else</option>
          </select>
        </div>
        <div>
          <label for="message" class="block text-sm font-medium">Message</label>
          <textarea id="message" name="message" rows="5" required minlength="20" class="mt-1.5 w-full rounded-md border border-stone-300 px-3 py-2"></textarea>
          <p id="message-help" class="mt-1 text-sm text-stone-500">For orders, include the order number (it starts with HC-).</p>
        </div>
        <input type="text" name="company_website" tabindex="-1" autocomplete="off" class="hidden" aria-hidden="true"> <!-- honeypot -->
        <button type="submit" class="justify-self-start rounded-md bg-stone-900 px-5 py-2.5 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Send message</button>
      </form>
      <!-- Success state: hidden until the fetch resolves -->
      <div hidden data-success role="status" class="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-5">
        <p class="font-medium">Sent. Thanks, <span data-success-name></span>.</p>
        <p class="mt-1 text-sm text-stone-600">Sara reads these each morning and replies within one working day from hello@hale-ceramics.co.uk. Check spam if nothing arrives by Thursday.</p>
      </div>
    </section>

    <!-- 3. Direct channels: address block, phone, email, hours -->
    <aside aria-labelledby="details-heading" class="lg:border-l lg:border-stone-200 lg:pl-10">
      <h2 id="details-heading" class="text-xl font-semibold">Or come and find us</h2>
      <address class="mt-6 space-y-5 not-italic text-stone-700">
        <p>Hale Ceramics<br>Unit 4, Cockpit Yard<br>Northington Street<br>London WC1N 2NP</p>
        <p><a href="tel:+442072426190" class="underline underline-offset-4">020 7242 6190</a><br><a href="mailto:hello@hale-ceramics.co.uk" class="underline underline-offset-4">hello@hale-ceramics.co.uk</a></p>
      </address>
      <h3 class="mt-8 text-sm font-medium">Studio hours</h3>
      <dl class="mt-2 grid grid-cols-[8rem_1fr] gap-y-1 text-sm text-stone-700" data-hours>
        <dt>Tuesday to Friday</dt><dd>10:00 to 18:00</dd>
        <dt>Saturday</dt><dd>11:00 to 16:00</dd>
        <dt>Sunday, Monday</dt><dd>Closed</dd>
      </dl>
      <p class="mt-2 text-sm text-stone-500" data-open-now hidden></p>
    </aside>
  </div>

  <!-- 4. Map: iframe with a title, lazy, and a plain link for people who cannot use it -->
  <section aria-labelledby="map-heading" class="mt-20">
    <h2 id="map-heading" class="sr-only">Map</h2>
    <iframe src="https://www.openstreetmap.org/export/embed.html?bbox=-0.1195,51.5215,-0.1155,51.5240&layer=mapnik&marker=51.5228,-0.1175" title="Map showing Hale Ceramics at Cockpit Yard, London" loading="lazy" class="aspect-[3/1] w-full rounded-lg border border-stone-200"></iframe>
    <p class="mt-2 text-sm text-stone-500"><a href="https://www.openstreetmap.org/?mlat=51.5228&mlon=-0.1175#map=18/51.5228/-0.1175" class="underline underline-offset-4">Open in OpenStreetMap</a> · Nearest tube: Chancery Lane, 6 minutes.</p>
  </section>
</main>
```

Submit and success state, built on `web-form-submit-with-fetch`:

```js
const section = document.querySelector('[data-contact]');
const form = section.querySelector('form');
const success = section.querySelector('[data-success]');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const button = form.querySelector('button[type=submit]');
  button.disabled = true;
  button.textContent = 'Sending…';
  try {
    const response = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    success.querySelector('[data-success-name]').textContent = form.name.value.trim().split(' ')[0];
    form.hidden = true;
    success.hidden = false;
    success.focus?.();
  } catch {
    button.disabled = false;
    button.textContent = 'Send message';
    form.insertAdjacentHTML('beforeend', '<p role="alert" class="text-sm text-red-700">Could not send. Email us instead: hello@hale-ceramics.co.uk</p>');
  }
});
```

Meta: `LocalBusiness` JSON-LD with `address`, `telephone`, `openingHoursSpecification` and `geo`, via `web-seo-structured-data`. The `<title>` is "Contact · Hale Ceramics", not "Contact Us | Home".

## Variations

- **No physical location**: drop the map and address; the aside lists email, a support hours line, response time and links to the help centre and status page.
- **Multiple offices**: the aside becomes a `divide-y` list of offices, each an `<address>` with its own hours; one map per office is too much, link to maps instead.
- **Booking or quote request**: add date and budget fields and route the submit to a calendar tool; the success block then says what happens next ("You will get a 20-minute call slot to pick").
- **"Open now" line**: a small script compares the current time in the studio's zone (`Intl.DateTimeFormat` with `timeZone: 'Europe/London'`) with the hours and fills `[data-open-now]`; leave it hidden when JS is off.

## Pitfalls

- A contact page that is only a form hides the phone number from the person whose parcel is late; the alternative channels earn the right column.
- "Thank you for your submission. We will get back to you shortly." is the generic state; say who replies, from what address and by when.
- Replacing the form without moving focus leaves screen reader users on a vanished button; the success block has `role="status"` and gets focus (add `tabindex="-1"`).
- Map iframes without `title` fail accessibility audits and without `loading="lazy"` cost 400 KB before the form renders.
- `tel:` links need the international form (`+44...`) to dial correctly from abroad; display the local form.
- The honeypot must be hidden with CSS, not `type="hidden"`, or bots skip it and humans never see it; keep `tabindex="-1"` so keyboard users do not land in it.

## Related skills

- `web-form-submit-with-fetch`
- `web-form-validation`
- `web-form-layout`
- `web-seo-structured-data`
- `web-craft-copy-that-sounds-human`
- `web-page-about-team`
- `web-page-help-center`
