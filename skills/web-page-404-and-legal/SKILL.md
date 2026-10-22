---
name: web-page-404-and-legal
description: 'Build site utility pages in Tailwind v4: a 404 with search and likely destinations, a maintenance page with a 503 status, and privacy or terms pages with a sticky table of contents, "last updated" and canonical. Use whenever a user asks for a 404 page, "page not found", maintenance page, privacy policy page, terms of service or legal page.'
---

# 404, maintenance and legal pages

These pages are read by people who did not want to be there. A 404 should get them to the right page in one click: say what happened, show the URL they tried, offer search and the four pages people actually want. It is the one page that earns a centred layout, because there is nothing to read. Legal pages are the opposite: 3,000 words with numbered sections that lawyers and users both need to cite, so they get a left-aligned `[14rem_minmax(0,1fr)]` grid with a sticky table of contents, visible dates and a canonical URL so the policy has one address.

## Pattern

404 page (the server must send status `404`, not `200`):

```html
<main id="main" class="flex min-h-dvh flex-col items-center justify-center px-4 py-16 text-center">
  <p class="font-mono text-sm text-stone-500">404</p>
  <h1 class="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">There is no page at this address</h1>
  <p class="mt-3 max-w-[44ch] text-stone-600">You asked for <code class="rounded bg-stone-100 px-1.5 py-0.5 text-sm" data-attempted-url>/this/path</code>. It may have moved, or the link had a typo.</p>

  <form role="search" action="/search" class="mt-8 flex w-full max-w-md gap-2">
    <label for="nf-q" class="sr-only">Search the site</label>
    <input id="nf-q" name="q" type="search" class="min-w-0 flex-1 rounded-md border border-stone-300 px-3 py-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900" data-search-input>
    <button type="submit" class="rounded-md bg-stone-900 px-4 py-2 font-medium text-white">Search</button>
  </form>

  <nav aria-label="Likely destinations" class="mt-10">
    <ul class="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm">
      <li><a href="/" class="underline underline-offset-4">Home</a></li>
      <li><a href="/docs" class="underline underline-offset-4">Docs</a></li>
      <li><a href="/pricing" class="underline underline-offset-4">Pricing</a></li>
      <li><a href="/help" class="underline underline-offset-4">Help centre</a></li>
    </ul>
  </nav>
  <p class="mt-10 text-sm text-stone-500">Followed a link from our site? <a href="mailto:hello@ledgerline.dev?subject=Broken%20link" class="underline underline-offset-4">Tell us</a> and we will fix it.</p>
</main>
```

```js
// Show the path they tried and pre-fill search from its last segment.
const path = location.pathname;
document.querySelector('[data-attempted-url]').textContent = path;
const guess = decodeURIComponent(path.split('/').filter(Boolean).at(-1) ?? '').replace(/[-_]+/g, ' ').replace(/\.\w+$/, '');
if (guess) document.querySelector('[data-search-input]').value = guess;
```

Maintenance page: same centred shell, `<h1>Back by 03:30 UTC</h1>`, one line on what is happening, a link to the status page, and the server responds `503` with a `Retry-After` header so crawlers come back instead of de-indexing.

Legal page (privacy, terms, cookies share this layout):

```html
<main id="main" class="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:grid lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-16 lg:px-8 lg:py-20">

  <!-- TOC: sticky left column from lg; a details element above the text below lg -->
  <nav aria-label="Sections" class="lg:sticky lg:top-24 lg:self-start">
    <details class="group text-sm lg:contents" open>
      <summary class="cursor-pointer font-medium lg:hidden">Contents</summary>
      <p class="hidden font-medium lg:block">Contents</p>
      <ol class="mt-3 space-y-2 text-stone-500" data-toc>
        <li><a href="#collect" class="hover:text-stone-900 aria-[current=true]:text-stone-900">1. What we collect</a></li>
        <li><a href="#use" class="hover:text-stone-900 aria-[current=true]:text-stone-900">2. How we use it</a></li>
        <li><a href="#share" class="hover:text-stone-900 aria-[current=true]:text-stone-900">3. Who we share it with</a></li>
        <li><a href="#retain" class="hover:text-stone-900 aria-[current=true]:text-stone-900">4. How long we keep it</a></li>
        <li><a href="#rights" class="hover:text-stone-900 aria-[current=true]:text-stone-900">5. Your rights</a></li>
        <li><a href="#changes" class="hover:text-stone-900 aria-[current=true]:text-stone-900">6. Changes to this policy</a></li>
      </ol>
    </details>
  </nav>

  <article class="legal-body mt-10 max-w-[65ch] lg:mt-0">
    <h1 class="text-3xl font-semibold tracking-tight sm:text-4xl">Privacy policy</h1>
    <p class="mt-3 text-sm text-stone-500">Last updated <time datetime="2026-02-01">1 February 2026</time> · Effective <time datetime="2026-03-01">1 March 2026</time> · <a href="/legal/privacy/changes" class="underline underline-offset-4">See what changed</a></p>
    <p class="mt-6 text-lg text-stone-600">The short version: we store what you type into Ledgerline, we do not sell it, and you can export or delete it yourself from Settings.</p>

    <h2 id="collect">1. What we collect</h2>
    <p>Account details (name, email, company), the ledgers and entries you create, and server logs (IP address, browser, pages visited) kept for 30 days.</p>
    <h3 id="collect-cookies">1.1 Cookies</h3>
    <p>One session cookie (<code>ll_session</code>, expires when you sign out) and one preference cookie for dark mode. No advertising cookies, no third-party analytics.</p>
    <h2 id="use">2. How we use it</h2>
    <p>To run the service, to bill you, and to email you about outages and invoices. Product emails have an unsubscribe link; outage emails do not.</p>
    <h2 id="share">3. Who we share it with</h2>
    <p>Stripe (payments, Ireland), Hetzner (hosting, Germany), Postmark (email, US, under the EU-US Data Privacy Framework). Nobody else without a court order.</p>
    <h2 id="retain">4. How long we keep it</h2>
    <h2 id="rights">5. Your rights</h2>
    <h2 id="changes">6. Changes to this policy</h2>
    <p>We post changes here and email account owners 30 days before they take effect. Questions: <a href="mailto:privacy@ledgerline.dev">privacy@ledgerline.dev</a>, or write to Ledgerline Ltd, 14 Orchard Street, Bristol BS1 3EJ.</p>
  </article>
</main>
```

```css
.legal-body {
  & h2 { @apply mt-12 scroll-mt-24 text-xl font-semibold tracking-tight; }
  & h3 { @apply mt-8 scroll-mt-24 text-base font-semibold; }
  & p, & ul, & ol { @apply mt-4 leading-relaxed text-stone-700; }
  & ol { @apply list-decimal pl-6; }
  & a { @apply underline underline-offset-4; }
}
@media print { nav, header, footer { display: none; } .legal-body { max-width: none; } }
```

The TOC highlight uses `web-nav-scroll-spy-toc`. Meta: `<link rel="canonical" href="https://ledgerline.dev/legal/privacy">` so `/privacy`, `/legal/privacy/` and the PDF export all point to one URL; `<title>Privacy policy · Ledgerline</title>`; legal pages are indexable, the 404 and maintenance pages are `noindex`.

## Variations

- **Playful 404**: one image or illustration above the heading, nothing animated; the search and links stay exactly where they are.
- **Static hosts**: name the file `404.html` at the root (GitHub Pages, Cloudflare Pages, Netlify all serve it with a real 404 status); see `web-ship-static-hosting`.
- **Terms page**: same layout; sections are numbered clauses (`7.2`), use `<ol>` for sub-clauses, and add a "Definitions" section first.
- **Cookie policy with a table**: a `<table>` of cookie name, purpose, expiry, set by (`web-ui-data-table`), which is what regulators ask for.

## Pitfalls

- A 404 that returns status 200 is indexed as a real page; check with `curl -I`.
- Maintenance without `503` and `Retry-After` can drop the whole site from search results within days.
- Legal text as one unbroken `max-w-7xl` column is a 180-character measure; the `65ch` article column is for the reader, the TOC is for the citation.
- Heading ids that are numbers (`#1`) break when a section is inserted; name them by topic and keep the number only in the visible text.
- "Last updated" with no date, or a date in the footer only, fails most privacy audits; put both dates under the `<h1>` as `<time>` elements.
- A 404 that auto-redirects to the homepage after 5 seconds destroys the user's chance to read the URL and fix the typo.

## Related skills

- `web-design-empty-and-error-states`
- `web-nav-scroll-spy-toc`
- `web-seo-meta-tags`
- `web-ship-static-hosting`
- `web-ship-launch-checklist`
- `web-ship-analytics-and-privacy`
- `web-ui-data-table`
