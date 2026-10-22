---
name: web-page-docs
description: Build a documentation page or docs site in Tailwind v4: a three-column grid (sticky sidebar nav, content column, "on this page" TOC), search with a "/" shortcut, code blocks with copy buttons, prev/next links and a mobile sidebar. Use whenever a user asks for docs, a documentation site, API reference, developer guide, knowledge base or handbook.
---

# Documentation page

Docs have two readers: the one who knows where they are going (sidebar, search) and the one reading top to bottom (content column, TOC, prev/next). The layout is a fixed three-column grid, `16rem` sidebar, fluid content, `14rem` TOC, with the two outer columns sticky and independently scrollable so a long sidebar never pushes the content down. The content column has a `70ch` measure and starts at the same left edge on every page, which is what makes a docs site feel stable as you click around.

## Pattern

```html
<body class="bg-white text-stone-900">
  <header class="sticky top-0 z-20 border-b border-stone-200 bg-white/90 backdrop-blur">
    <div class="mx-auto flex h-14 max-w-screen-2xl items-center gap-6 px-4 sm:px-6">
      <a href="/docs" class="font-semibold">Ledgerline docs</a>
      <form role="search" action="/docs/search" class="ml-auto">
        <label for="docs-search" class="sr-only">Search docs</label>
        <input id="docs-search" name="q" type="search" placeholder="Search… ( / )" class="w-48 rounded-md border border-stone-300 px-3 py-1.5 text-sm sm:w-64" data-search>
      </form>
      <a href="/docs/api" class="hidden text-sm sm:block">API</a>
    </div>
  </header>

  <div class="mx-auto max-w-screen-2xl px-4 sm:px-6 lg:grid lg:grid-cols-[16rem_minmax(0,1fr)_14rem] lg:gap-10">

    <!-- 1. Sidebar: a details element on phones, a sticky scrolling column from lg -->
    <details class="group py-3 lg:contents" open data-sidebar>
      <summary class="cursor-pointer text-sm font-medium lg:hidden">Menu</summary>
      <nav aria-label="Docs" class="mt-3 lg:sticky lg:top-14 lg:mt-0 lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto lg:py-8">
        <p class="font-mono text-xs uppercase tracking-wide text-stone-500">Getting started</p>
        <ul class="mt-2 space-y-1 text-sm">
          <li><a href="/docs/install" class="block rounded px-2 py-1 hover:bg-stone-100">Install</a></li>
          <li><a href="/docs/first-ledger" aria-current="page" class="block rounded px-2 py-1 font-medium hover:bg-stone-100 aria-[current=page]:bg-stone-100">Your first ledger</a></li>
          <li><a href="/docs/webhooks" class="block rounded px-2 py-1 hover:bg-stone-100">Webhooks</a></li>
        </ul>
        <p class="mt-6 font-mono text-xs uppercase tracking-wide text-stone-500">Reference</p>
        <ul class="mt-2 space-y-1 text-sm">
          <li><a href="/docs/api/accounts" class="block rounded px-2 py-1 hover:bg-stone-100">Accounts</a></li>
          <li><a href="/docs/api/entries" class="block rounded px-2 py-1 hover:bg-stone-100">Entries</a></li>
        </ul>
      </nav>
    </details>

    <!-- 2. Content: breadcrumb, h1, prose, prev/next -->
    <main id="main" class="min-w-0 py-8 lg:py-10">
      <article class="docs-body max-w-[70ch]">
        <nav aria-label="Breadcrumb" class="text-sm text-stone-500">Getting started / Your first ledger</nav>
        <h1 class="mt-2 text-3xl font-semibold tracking-tight">Your first ledger</h1>
        <p class="mt-3 text-lg text-stone-600">Create a ledger, post two entries and read the balance. About 5 minutes with curl.</p>

        <h2 id="create">1. Create the ledger</h2>
        <p>Every ledger has a base currency that cannot change later.</p>
        <div class="relative" data-code>
          <pre class="overflow-x-auto rounded-lg bg-stone-900 p-4 text-sm text-stone-100"><code class="language-bash">curl -X POST https://api.ledgerline.dev/v1/ledgers \
  -H "Authorization: Bearer ll_test_..." \
  -d currency=GBP -d name="Shop till"</code></pre>
          <button type="button" class="absolute right-2 top-2 rounded border border-stone-700 px-2 py-1 text-xs text-stone-300 hover:bg-stone-800 focus-visible:outline-2 focus-visible:outline-white" data-copy>Copy</button>
        </div>
        <aside class="my-6 border-l-2 border-amber-500 bg-amber-50 px-4 py-3 text-sm" role="note"><strong>Test keys</strong> start with <code>ll_test_</code> and post to a sandbox that resets every night at 02:00 UTC.</aside>

        <h2 id="post">2. Post two entries</h2>
        <p>Entries are immutable. A mistake is corrected by a reversing entry, never an edit.</p>
        <h3 id="response">Response</h3>
        <p>You get the entry back with an <code>id</code> and a <code>posted_at</code> timestamp.</p>

        <h2 id="balance">3. Read the balance</h2>
        <p>Balances are computed, not stored; a 10-million-entry ledger answers in about 40 ms.</p>
      </article>

      <nav aria-label="Previous and next" class="mt-16 flex max-w-[70ch] justify-between gap-6 border-t border-stone-200 pt-6 text-sm">
        <a href="/docs/install" rel="prev" class="group"><span class="block text-stone-500">Previous</span><span class="font-medium group-hover:underline">← Install</span></a>
        <a href="/docs/webhooks" rel="next" class="group text-right"><span class="block text-stone-500">Next</span><span class="font-medium group-hover:underline">Webhooks →</span></a>
      </nav>
      <p class="mt-8 text-sm text-stone-500">Last updated <time datetime="2026-03-02">2 March 2026</time> · <a href="https://github.com/ledgerline/docs/edit/main/first-ledger.md" class="underline underline-offset-4">Edit this page</a></p>
    </main>

    <!-- 3. On this page: hidden below lg, sticky from lg -->
    <aside class="hidden lg:block">
      <nav aria-label="On this page" class="sticky top-14 py-10 text-sm" data-toc>
        <p class="font-medium">On this page</p>
        <ol class="mt-3 space-y-2 border-l border-stone-200 text-stone-500">
          <li><a href="#create" class="-ml-px block border-l border-transparent pl-3 hover:text-stone-900 aria-[current=true]:border-stone-900 aria-[current=true]:text-stone-900">Create the ledger</a></li>
          <li><a href="#post" class="-ml-px block border-l border-transparent pl-3 hover:text-stone-900 aria-[current=true]:border-stone-900 aria-[current=true]:text-stone-900">Post two entries</a></li>
          <li><a href="#response" class="-ml-px block border-l border-transparent pl-6 hover:text-stone-900 aria-[current=true]:border-stone-900 aria-[current=true]:text-stone-900">Response</a></li>
          <li><a href="#balance" class="-ml-px block border-l border-transparent pl-3 hover:text-stone-900 aria-[current=true]:border-stone-900 aria-[current=true]:text-stone-900">Read the balance</a></li>
        </ol>
      </nav>
    </aside>
  </div>
</body>
```

```css
.docs-body {
  & h2 { @apply mt-10 scroll-mt-20 text-xl font-semibold tracking-tight; }
  & h3 { @apply mt-6 scroll-mt-20 text-base font-semibold; }
  & p, & ul, & ol { @apply mt-4 leading-relaxed; }
  & code:not(pre code) { @apply rounded bg-stone-100 px-1 py-0.5 font-mono text-[0.9em]; }
  & pre { @apply mt-4; }
}
```

The three bits of JS the page needs: `/` focuses search, copy buttons on code blocks, and the TOC highlight from `web-nav-scroll-spy-toc` (it sets `aria-current="true"`).

```js
document.addEventListener('keydown', (event) => {
  if (event.key !== '/' || event.target.matches('input, textarea, [contenteditable]')) return;
  event.preventDefault();
  document.querySelector('[data-search]').focus();
});

for (const block of document.querySelectorAll('[data-code]')) {
  const button = block.querySelector('[data-copy]');
  button.addEventListener('click', async () => {
    await navigator.clipboard.writeText(block.querySelector('code').textContent);
    button.textContent = 'Copied';
    setTimeout(() => (button.textContent = 'Copy'), 1500);
  });
}
```

Meta: `TechArticle` JSON-LD with `headline`, `dateModified` and `author` (the organisation), `BreadcrumbList` from the breadcrumb, via `web-seo-structured-data`. Each page has its own `<title>` ("Your first ledger · Ledgerline docs") and canonical.

## Variations

- **Two columns**: for small docs (under 20 pages) drop the TOC column: `lg:grid-cols-[16rem_minmax(0,1fr)]` and keep the content measure.
- **API reference**: content column becomes `xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]`, prose on the left and a sticky request/response code panel on the right, `web-nav-tabs` for languages.
- **Versions**: a `<select>` in the sidebar head that navigates to `/docs/v2/...`; keep the same path across versions so the switch lands on the same page.
- **Dark code only**: keep the page light and the `<pre>` dark; a fully dark docs site needs `web-design-dark-mode` and a toggle, not a default.

## Pitfalls

- The content column must be `minmax(0,1fr)`, not `1fr`, or a wide `<pre>` stretches the grid past the viewport.
- A sidebar without `lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto` grows with its links and the sticky never engages.
- `<details open>` on the sidebar with `lg:contents` lets the same markup serve both widths; without `lg:contents` the grid sees one child instead of two.
- Headings without stable `id`s break every link in search results and chat threads after the next edit.
- `navigator.clipboard` needs HTTPS or localhost; on `file://` the copy button silently fails, so test on a server.
- Search as an `<input>` with no form action is JS-only; the form posts to a real search page as the baseline (`web-form-search-suggestions` adds live results).

## Related skills

- `web-nav-scroll-spy-toc`
- `web-nav-sidebar`
- `web-nav-breadcrumbs`
- `web-form-search-suggestions`
- `web-css-sticky-and-fixed`
- `web-seo-structured-data`
- `web-page-help-center`
