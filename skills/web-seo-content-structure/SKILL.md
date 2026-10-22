---
name: web-seo-content-structure
description: 'Structure page content for search engines and readers: one H1 and a clean heading outline, descriptive internal links, scannable sections, real text instead of text-in-images, in-page anchors, author and date for articles. Use when a user asks "SEO for this page", "heading structure", "how many H1", "internal linking", "blog post structure", "content outline", or "why doesn''t this page rank".'
---

# Content structure for search and readers

Search engines rank pages by understanding what they are about and whether they answer the query;
they understand it from the same structure people use to scan: the title, the headings, the first
paragraph, the link text pointing in and out. There is no separate "SEO markup" for this. A page
with one clear `<h1>`, `<h2>` sections that each answer a sub-question, text that is real HTML
(not pixels), and links whose text names the destination is already optimised. Everything below is
the same semantics that `web-a11y-semantic-html` asks for, plus editorial discipline.

## Pattern

An article page that does everything right. The same skeleton works for docs and long landing pages.

```html
<main id="main" class="mx-auto max-w-prose px-4 py-12">
  <article>
    <header>
      <!-- Breadcrumb trail doubles as internal links with descriptive text -->
      <nav aria-label="Breadcrumb" class="text-sm">
        <ol class="flex gap-2">
          <li><a href="/" class="underline">Home</a> /</li>
          <li><a href="/blog/" class="underline">Blog</a> /</li>
          <li aria-current="page">Why we charge per seat</li>
        </ol>
      </nav>

      <!-- Exactly one h1; it matches the <title> minus the brand, and the og:title -->
      <h1 class="mt-6 text-4xl font-bold text-balance">Why we charge per seat (and not per project)</h1>

      <!-- Lede: the answer in two sentences. This is what the snippet and AI overviews quote. -->
      <p class="mt-4 text-lg text-gray-700 dark:text-gray-300">
        Per-seat pricing keeps costs predictable for small teams and lets large ones add people
        without renegotiating. Here is the math and the trade-offs.
      </p>

      <p class="mt-4 text-sm text-gray-600 dark:text-gray-400">
        By <a href="/team/jane" rel="author" class="underline">Jane Doe</a>,
        <time datetime="2026-10-01">1 October 2026</time>.
        Updated <time datetime="2026-10-15">15 October 2026</time>. 6 min read.
      </p>
    </header>

    <!-- Table of contents: in-page links with ids on the headings -->
    <nav aria-label="On this page" class="mt-8 rounded-lg border p-4 text-sm">
      <h2 class="font-semibold">Contents</h2>
      <ol class="mt-2 list-inside list-decimal">
        <li><a href="#predictable-costs" class="underline">Predictable costs for small teams</a></li>
        <li><a href="#large-teams" class="underline">What large teams pay</a></li>
        <li><a href="#alternatives" class="underline">Alternatives we rejected</a></li>
      </ol>
    </nav>

    <!-- h2 per sub-question; the heading text is what people would search for -->
    <h2 id="predictable-costs" class="mt-12 scroll-mt-24 text-2xl font-semibold">Predictable costs for small teams</h2>
    <p class="mt-4">A five-person team pays <strong>$145 a month</strong>, every month, regardless of how many projects they run.</p>

    <h2 id="large-teams" class="mt-12 scroll-mt-24 text-2xl font-semibold">What large teams pay</h2>
    <h3 class="mt-6 text-xl font-semibold">Volume discounts</h3>
    <p class="mt-4">Above 100 seats the per-seat price drops; see the
      <a href="/pricing#enterprise" class="underline">enterprise tier on the pricing page</a>.</p>

    <h2 id="alternatives" class="mt-12 scroll-mt-24 text-2xl font-semibold">Alternatives we rejected</h2>
    <ul class="mt-4 list-inside list-disc">
      <li><strong>Per project:</strong> penalises teams who organise work well.</li>
      <li><strong>Usage-based:</strong> unpredictable bills; see <a href="/blog/usage-pricing-postmortem" class="underline">our usage-pricing post-mortem</a>.</li>
    </ul>
  </article>

  <!-- Related links keep crawlers and readers moving deeper into the site -->
  <aside aria-labelledby="related-h" class="mt-16 border-t pt-8">
    <h2 id="related-h" class="text-xl font-semibold">Related reading</h2>
    <ul class="mt-4 space-y-2">
      <li><a href="/blog/how-seats-are-counted" class="underline">How we count active seats</a></li>
      <li><a href="/docs/billing" class="underline">Billing documentation</a></li>
    </ul>
  </aside>
</main>
```

Why each piece earns its place:

- **One `<h1>`** that matches the `<title>` intent. HTML allows several; search engines and screen
  readers both work better with one, so treat it as a rule.
- **Heading outline** `h1 > h2 > h3` with no skipped levels is also the page's featured-snippet
  and "jump to section" source. Headings are questions or claims, not puns.
- **First paragraph answers the question.** Snippets, previews and AI summaries lean on it.
- **Link text names the target** ("enterprise tier on the pricing page", not "click here"). It is
  what the linked page gets ranked for and what screen reader users hear in the links list.
- **Dates and author** in real `<time>` and `rel="author"` support freshness and E-E-A-T signals
  and match the `Article` JSON-LD.
- **Text is text.** Headlines in images are invisible to search; use HTML and webfonts.

## Variations

- **Landing page**: `<h1>` is the value proposition; each `<section>` gets an `<h2>` that names a
  benefit or an objection ("Pricing", "Security", "How it compares"), not "Section 2".
- **Docs page**: same shape with `<h2>` per task; add "Next" and "Previous" links in a
  `<nav aria-label="Pagination">` so every page links to two siblings.
- **Category / listing page**: `<h1>` names the category, an intro paragraph of 2-3 sentences
  above the grid, each card an `<article>` with an `<h2>` link; paginate with real links.
- **Hub and spoke**: a pillar page (`/pricing-guide`) links to each deep post; every deep post
  links back to the pillar in the first screen. This is the internal-linking structure that works.

## Pitfalls

- Heading levels chosen for size: an `<h4>` because it looked right. Pick the level by outline,
  style with Tailwind.
- Multiple `<h1>`s from a template (site logo wrapped in `<h1>` on every page plus the article
  title). The logo is a link, not a heading.
- Generic link text: "Read more", "here", "Learn more" repeated across cards. Make the card's
  heading the link, or include the subject ("Read more about seat counting").
- Burying the answer: 400 words of story before the point. Put the answer first, the story after.
- Thin or duplicated pages: tag archives, "page 2" of pagination, near-identical city pages. Either
  make them substantive, `noindex` them, or canonicalize to the parent.
- Keyword stuffing and invisible text. Both are penalised; write the sentence a human would, with
  the obvious phrase in the heading once.
- Hiding content behind JS tabs or accordions is fine for Google (it indexes hidden HTML), but
  content loaded only after a click or scroll is not in the HTML and may never be indexed.

## Related skills

- `web-a11y-semantic-html`
- `web-seo-meta-tags`
- `web-seo-structured-data`
- `web-seo-sitemap-robots-urls`
- `web-nav-breadcrumbs`
- `web-nav-scroll-spy-toc`
- `web-design-typography-system`
