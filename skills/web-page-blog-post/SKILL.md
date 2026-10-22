---
name: web-page-blog-post
description: 'Build a blog post or article page in Tailwind v4: title block with byline, date and reading time, a 65ch prose column beside a sticky table of contents, figures with captions, author box, related posts and Article JSON-LD. Use whenever a user asks for a blog page, article layout, post template, "long-form reading page" or a newsletter archive entry.'
---

# Blog post page

A post page has one job: let someone read 1,500 words without friction. Everything else on the page (table of contents, author box, related posts) exists to answer "what is this, who wrote it, how long will it take, what next" without interrupting the reading column. The layout is a left-aligned title block, a lead figure wider than the text, then a `65ch` prose column with a sticky table of contents in a narrow right column. The reading column is never centred on a wide container; it starts at the same left edge as the title.

## Pattern

```html
<main id="main" class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
  <article class="py-12 lg:py-20">

    <!-- 1. Title block: section, date, reading time, title, deck, byline. The reader decides here. -->
    <header class="max-w-[44rem]">
      <p class="font-mono text-xs uppercase tracking-wide text-stone-500">
        <a href="/blog/engineering" class="hover:text-stone-900">Engineering</a> ·
        <time datetime="2026-03-14">14 March 2026</time> · <span data-reading-time>9 min read</span>
      </p>
      <h1 class="mt-4 text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl">We moved 40,000 product images to AVIF. Here is what broke.</h1>
      <p class="mt-5 text-xl leading-relaxed text-stone-600">Page weight fell 61%. Safari 15 users saw grey boxes for two days. Both were our fault.</p>
      <address class="mt-6 flex items-center gap-3 not-italic">
        <img src="/img/team/priya-raman.jpg" width="40" height="40" alt="" class="size-10 rounded-full object-cover">
        <p class="text-sm"><a href="/authors/priya-raman" rel="author" class="font-medium">Priya Raman</a><span class="block text-stone-500">Platform engineer</span></p>
      </address>
    </header>

    <!-- 2. Lead figure: full container width, deliberately wider than the prose. -->
    <figure class="mt-10">
      <img src="/img/blog/avif-waterfall.webp" width="1600" height="900" fetchpriority="high" alt="Network waterfall: 42 image requests shrinking from 3.1 MB to 1.2 MB" class="aspect-video w-full rounded-lg object-cover">
      <figcaption class="mt-2 text-sm text-stone-500">Checkout page, cold cache, Fast 3G throttling. Before: 3.1 MB. After: 1.2 MB.</figcaption>
    </figure>

    <!-- 3. Body beside TOC. Prose first in the DOM; TOC is a sticky aside on the right from lg. -->
    <div class="mt-12 grid gap-12 lg:grid-cols-[minmax(0,1fr)_14rem] lg:gap-16">
      <div class="post-body max-w-[65ch]" data-post-body>
        <h2 id="why-avif">Why AVIF and not WebP</h2>
        <p>WebP would have saved 34%. AVIF saved 61% on the same 40,000 files at the same SSIM score, and 92% of our sessions were already on a browser that decodes it.</p>
        <h2 id="what-broke">What broke</h2>
        <h3 id="safari-15">Safari 15 got no fallback</h3>
        <p>Our <code>&lt;picture&gt;</code> element listed AVIF only. The CDN rewrite dropped the JPEG source.</p>
        <pre><code class="language-html">&lt;picture&gt;
  &lt;source srcset="/img/p/8841.avif" type="image/avif"&gt;
  &lt;img src="/img/p/8841.jpg" width="800" height="800" alt="Oak side table, 45 cm"&gt;
&lt;/picture&gt;</code></pre>
        <blockquote><p>Two days of grey boxes cost more than the bandwidth we saved that month.</p></blockquote>
        <h2 id="rollout">The rollout we should have done</h2>
        <p>Ten percent of traffic, one category, one week. Then the rest.</p>
      </div>

      <aside class="hidden lg:block">
        <nav aria-label="On this page" class="sticky top-24 border-l border-stone-200 pl-4 text-sm" data-toc>
          <p class="font-medium">On this page</p>
          <ol class="mt-3 space-y-2 text-stone-500">
            <li><a href="#why-avif" class="hover:text-stone-900 aria-[current=true]:font-medium aria-[current=true]:text-stone-900">Why AVIF</a></li>
            <li><a href="#what-broke" class="hover:text-stone-900 aria-[current=true]:font-medium aria-[current=true]:text-stone-900">What broke</a></li>
            <li class="pl-3"><a href="#safari-15" class="hover:text-stone-900 aria-[current=true]:font-medium aria-[current=true]:text-stone-900">Safari 15</a></li>
            <li><a href="#rollout" class="hover:text-stone-900 aria-[current=true]:font-medium aria-[current=true]:text-stone-900">The rollout</a></li>
          </ol>
        </nav>
      </aside>
    </div>

    <!-- 4. Author box: who to believe, where to follow. Same width as the prose. -->
    <footer class="mt-16 flex max-w-[65ch] gap-4 border-t border-stone-200 pt-8">
      <img src="/img/team/priya-raman.jpg" width="56" height="56" alt="" class="size-14 rounded-full object-cover">
      <div class="text-sm">
        <p class="font-medium">Priya Raman</p>
        <p class="mt-1 text-stone-600">Runs the image pipeline and the CDN. Previously four years at a print-on-demand shop that shipped 11 million posters.</p>
        <p class="mt-2"><a href="https://mastodon.social/@priyar" rel="me" class="underline underline-offset-4">@priyar</a> · <a href="/authors/priya-raman" class="underline underline-offset-4">All posts</a></p>
      </div>
    </footer>
  </article>

  <!-- 5. Related: three cards, same section, newest first. -->
  <section aria-labelledby="related-heading" class="border-t border-stone-200 py-12">
    <h2 id="related-heading" class="text-2xl font-semibold tracking-tight">More from engineering</h2>
    <ul role="list" class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">...web-layout-card-grid...</ul>
  </section>
</main>
```

Prose styles without a plugin, scoped to the body so the rest of the page keeps Preflight defaults:

```css
.post-body {
  @apply text-lg leading-relaxed text-stone-800;
  & h2 { @apply mt-12 scroll-mt-24 text-2xl font-semibold tracking-tight; }
  & h3 { @apply mt-8 scroll-mt-24 text-xl font-semibold; }
  & p, & ul, & ol { @apply mt-5; }
  & a { @apply underline underline-offset-4 decoration-stone-400 hover:decoration-stone-900; }
  & blockquote { @apply mt-8 border-l-2 border-stone-900 pl-5 text-xl italic text-stone-600; }
  & pre { @apply mt-6 overflow-x-auto rounded-lg bg-stone-900 p-4 text-sm text-stone-100; }
  & img { @apply mt-8 rounded-lg; }
}
```

Reading time, computed once so it never drifts from the content:

```js
const body = document.querySelector('[data-post-body]');
const words = body.textContent.trim().split(/\s+/).length;
document.querySelector('[data-reading-time]').textContent = `${Math.max(1, Math.round(words / 230))} min read`;
```

TOC highlighting: drop in `web-nav-scroll-spy-toc`; it sets `aria-current="true"` on the link whose heading is in view, which the `aria-[current=true]:` classes above style.

Meta: `<title>` is the post title plus site name, `<link rel="canonical">`, `og:type="article"`, `article:published_time`, and an `Article` JSON-LD block with `headline`, `datePublished`, `author` and `image` from `web-seo-structured-data`.

## Variations

- **No TOC** (posts under 800 words or fewer than three `h2`s): drop the aside and the grid; the article stays `max-w-[65ch]` at the left edge, not centred.
- **TOC on mobile**: add a `<details class="lg:hidden"><summary>On this page</summary>...</details>` before the body and keep the sticky aside for `lg`.
- **Full-bleed figures**: wrap `<main>` in the `content-grid` utility from `web-craft-layout-with-intention` and give a figure `class="full-bleed"` so one image breaks the container.
- **Series**: a `<nav aria-label="Series">` box above the body: "Part 2 of 4 · Image pipeline" with prev and next links.

## Pitfalls

- Centring the prose column in a `max-w-7xl` container leaves 20rem of empty gutter on each side; the eye reads it as unfinished. Align left, give the TOC the spare width.
- `max-w-prose` is 65ch of the *base* size; if the body is `text-lg`, set the measure on the body element itself so the ch unit matches.
- Heading ids must be stable and human (`#what-broke`, not `#h2-3`) or shared links break on every edit.
- Sticky TOC without `scroll-mt-*` on headings scrolls targets under the site header.
- `<pre>` blocks inside a `1fr` grid column push the column wider than the viewport on phones unless the column is `minmax(0,1fr)` and the `<pre>` has `overflow-x-auto`.
- Skipping `width` and `height` on the lead image shifts the whole article down when it loads.

## Related skills

- `web-nav-scroll-spy-toc`
- `web-seo-structured-data`
- `web-layout-card-grid`
- `web-design-typography-system`
- `web-css-fluid-typography`
- `web-page-blog-index`
- `web-craft-layout-with-intention`
