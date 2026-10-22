---
name: web-page-help-center
description: 'Build a help centre or support site in Tailwind v4: search with live filtering, category cards with article counts, FAQ accordions, a "still stuck" contact row, and an article page with "was this helpful" buttons. Use whenever a user asks for a help center, support page, FAQ page, knowledge base, "how do I" page or support hub.'
---

# Help centre

Someone on a help centre is already annoyed, so the page exists to get them off it. Search is the first thing, left-aligned with the heading so it is part of the page, not a hero. Then categories with counts (so the user can tell "Billing · 14 articles" is worth a click), the eight articles that answer most tickets, a short FAQ in native accordions, and a contact row that says how fast a human replies. The article page is a two-column `[16rem_minmax(0,1fr)]` with the category's other articles on the left and a yes/no feedback pair at the end.

## Pattern

Hub page:

```html
<main id="main" class="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8 lg:py-20">

  <!-- 1. Search: heading and input share the left edge -->
  <header class="max-w-[40rem]">
    <h1 class="text-4xl font-semibold tracking-tight sm:text-5xl">How can we help?</h1>
    <form role="search" action="/help/search" class="mt-6">
      <label for="help-q" class="sr-only">Search help articles</label>
      <input id="help-q" name="q" type="search" placeholder="Try “refund”, “export csv” or “two-factor”" class="w-full rounded-md border border-stone-300 px-4 py-3 text-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900" data-help-search>
    </form>
    <p class="mt-2 text-sm text-stone-500" data-help-count>83 articles · updated weekly</p>
  </header>

  <!-- 2. Categories: name, count, two example links so people know what is inside -->
  <section aria-labelledby="categories-heading" class="mt-16">
    <h2 id="categories-heading" class="font-mono text-xs uppercase tracking-wide text-stone-500">Browse by topic</h2>
    <ul role="list" class="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <li class="rounded-lg border border-stone-200 p-6">
        <h3 class="text-lg font-semibold"><a href="/help/billing" class="hover:underline hover:underline-offset-4">Billing and invoices</a></h3>
        <p class="mt-1 text-sm text-stone-500">14 articles</p>
        <ul class="mt-4 space-y-1 text-sm">
          <li><a href="/help/billing/change-card" class="underline underline-offset-4 decoration-stone-300 hover:decoration-stone-900">Change the card on file</a></li>
          <li><a href="/help/billing/vat" class="underline underline-offset-4 decoration-stone-300 hover:decoration-stone-900">Add a VAT number to invoices</a></li>
        </ul>
      </li>
      <li class="rounded-lg border border-stone-200 p-6">...Account and security · 11 articles...</li>
      <li class="rounded-lg border border-stone-200 p-6">...Exports and integrations · 19 articles...</li>
    </ul>
  </section>

  <!-- 3. Popular: a plain list, filtered live by the search box -->
  <section aria-labelledby="popular-heading" class="mt-16 grid gap-8 lg:grid-cols-[1fr_2fr]">
    <h2 id="popular-heading" class="text-2xl font-semibold tracking-tight lg:sticky lg:top-24 lg:self-start">Most read this month</h2>
    <ol class="divide-y divide-stone-200" data-help-list>
      <li class="py-3"><a href="/help/billing/refunds" class="hover:underline hover:underline-offset-4">How refunds work and how long they take</a> <span class="text-sm text-stone-500">· Billing</span></li>
      <li class="py-3"><a href="/help/exports/csv" class="hover:underline hover:underline-offset-4">Export transactions as CSV or Parquet</a> <span class="text-sm text-stone-500">· Exports</span></li>
      <li class="py-3"><a href="/help/account/two-factor" class="hover:underline hover:underline-offset-4">Set up two-factor authentication</a> <span class="text-sm text-stone-500">· Security</span></li>
      <li class="py-3"><a href="/help/account/lost-2fa" class="hover:underline hover:underline-offset-4">I lost my two-factor device</a> <span class="text-sm text-stone-500">· Security</span></li>
    </ol>
    <p hidden data-help-empty class="text-stone-600 lg:col-start-2">Nothing matches. Try fewer words, or <a href="#contact" class="underline underline-offset-4">ask us</a>.</p>
  </section>

  <!-- 4. FAQ: native accordions, exclusive via name -->
  <section aria-labelledby="faq-heading" class="mt-16 grid gap-8 lg:grid-cols-[1fr_2fr]">
    <h2 id="faq-heading" class="text-2xl font-semibold tracking-tight lg:self-start">Quick answers</h2>
    <div class="divide-y divide-stone-200">
      <details name="faq" class="group py-4">
        <summary class="flex cursor-pointer items-center justify-between font-medium">Can I pause my subscription?<span aria-hidden="true" class="transition group-open:rotate-45">+</span></summary>
        <p class="mt-3 max-w-[60ch] text-stone-600">Yes, for up to three months a year from Settings → Billing. Your data stays; exports and the API keep working read-only.</p>
      </details>
      <details name="faq" class="group py-4">
        <summary class="flex cursor-pointer items-center justify-between font-medium">Do you have a status page?<span aria-hidden="true" class="transition group-open:rotate-45">+</span></summary>
        <p class="mt-3 max-w-[60ch] text-stone-600">status.ledgerline.dev, with incident history back to 2022 and an RSS feed.</p>
      </details>
    </div>
  </section>

  <!-- 5. Still stuck: the human route, with a response time -->
  <section id="contact" aria-labelledby="contact-heading" class="mt-20 grid gap-6 border-t border-stone-200 pt-10 lg:grid-cols-[2fr_1fr] lg:items-center">
    <div class="max-w-[48ch]">
      <h2 id="contact-heading" class="text-2xl font-semibold tracking-tight">Still stuck?</h2>
      <p class="mt-2 text-stone-600">Email support is staffed 08:00 to 20:00 UK time, seven days. Median first reply last month: 42 minutes.</p>
    </div>
    <a href="/contact" class="justify-self-start rounded-md bg-stone-900 px-5 py-3 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 lg:justify-self-end">Email support</a>
  </section>
</main>
```

Article page skeleton:

```html
<div class="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:grid lg:grid-cols-[16rem_minmax(0,1fr)] lg:gap-12 lg:px-8">
  <nav aria-label="Billing articles" class="hidden lg:sticky lg:top-24 lg:block lg:self-start">...links in this category, aria-current="page" on this one...</nav>
  <main id="main">
    <article class="max-w-[65ch]">
      <nav aria-label="Breadcrumb" class="text-sm text-stone-500">Help / Billing</nav>
      <h1 class="mt-2 text-3xl font-semibold tracking-tight">How refunds work and how long they take</h1>
      <p class="mt-2 text-sm text-stone-500">Updated <time datetime="2026-03-09">9 March 2026</time> · 2 min read</p>
      <div class="help-body">...steps as an ordered list, screenshots with alt text...</div>
    </article>
    <form class="mt-12 flex max-w-[65ch] flex-wrap items-center gap-3 border-t border-stone-200 pt-6 text-sm" data-helpful>
      <span id="helpful-label">Did this answer your question?</span>
      <button type="submit" name="helpful" value="yes" aria-describedby="helpful-label" class="rounded-md border border-stone-300 px-3 py-1.5 hover:bg-stone-50">Yes</button>
      <button type="submit" name="helpful" value="no" aria-describedby="helpful-label" class="rounded-md border border-stone-300 px-3 py-1.5 hover:bg-stone-50">No</button>
    </form>
  </main>
</div>
```

Live filter on the hub, and the feedback pair:

```js
const input = document.querySelector('[data-help-search]');
const items = [...document.querySelectorAll('[data-help-list] > li')];
const empty = document.querySelector('[data-help-empty]');
input.addEventListener('input', () => {
  const q = input.value.trim().toLowerCase();
  let shown = 0;
  for (const li of items) { li.hidden = q && !li.textContent.toLowerCase().includes(q); if (!li.hidden) shown++; }
  empty.hidden = shown > 0;
});

document.querySelector('[data-helpful]')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = event.submitter.value;
  await fetch('/api/helpful', { method: 'POST', body: new URLSearchParams({ url: location.pathname, value }) }).catch(() => {});
  event.currentTarget.replaceWith(Object.assign(document.createElement('p'), { role: 'status', className: 'mt-12 text-sm text-stone-600', textContent: value === 'yes' ? 'Thanks.' : 'Sorry about that. Email support and mention this page; it goes to the person who wrote it.' }));
});
```

Meta: `FAQPage` JSON-LD for the accordion questions on the hub, `Article` or `HowTo` on article pages with `dateModified`, both via `web-seo-structured-data`.

## Variations

- **Product-specific sections**: a top row of two or three product tabs (`web-nav-tabs`) that swap the category grid; keep the search global.
- **Status strip**: a one-line `role="status"` bar above the header fetched from the status page JSON: "All systems normal" or the current incident with a link.
- **Video answers**: the article body embeds a short screen recording with captions (`web-a11y-images-and-media`) above the written steps, never instead of them.
- **Dark**: `bg-stone-950`, category cards `border-stone-800`, keep the search input light-on-dark with a visible border; no glass.

## Pitfalls

- A centred search hero with a gradient background makes the help centre look like a landing page; people here want the input, not the mood.
- Categories without counts or example links are a guessing game; the two links inside each card are the real navigation.
- Live filtering the popular list is a convenience; the `<form role="search">` must still post to a real search page or the filter is the only search.
- Accordion FAQs hide content from search engines less than people think, but hide it from readers who scan; keep it to six questions and put long answers on article pages.
- "Was this helpful?" without a follow-up for "No" collects a number and helps nobody; the replacement text routes them somewhere.
- Screenshots of the product in articles go stale; date each article and show the date, so a reader knows when the screenshot was taken.

## Related skills

- `web-ui-accordion`
- `web-form-search-suggestions`
- `web-design-empty-and-error-states`
- `web-seo-structured-data`
- `web-page-docs`
- `web-page-contact`
- `web-craft-copy-that-sounds-human`
