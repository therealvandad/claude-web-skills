---
name: web-nav-scroll-spy-toc
description: Build a table of contents that highlights the section currently in view (scroll spy) using IntersectionObserver, generated from the page's h2/h3 headings, sticky on desktop and a collapsible "On this page" disclosure on mobile, with Tailwind v4. Use when a user asks for a table of contents, "on this page" links, scroll spy, active section highlighting, or docs-style side navigation.
---

# Scroll-spy table of contents

A TOC earns its place on long articles and docs pages: it shows the shape of the page and where the reader is. Build it from the headings so it never drifts out of sync with content, and track the current section with `IntersectionObserver` instead of measuring offsets on every scroll event. The "current" heading is the one closest to a reading line near the top of the viewport; a `rootMargin` makes the observer fire around that line. The links are ordinary anchors, so without JS the TOC still works, it just does not highlight.

## Pattern

```html
<div class="mx-auto grid max-w-6xl gap-10 px-4 lg:grid-cols-[1fr_16rem]">
  <article data-toc-source class="prose max-w-none dark:prose-invert">
    <h1>Deploying a static site</h1>
    <h2 id="prerequisites">Prerequisites</h2> <p>…</p>
    <h2 id="build">Build</h2> <p>…</p>
    <h3 id="build-env">Environment variables</h3> <p>…</p>
    <h2 id="deploy">Deploy</h2> <p>…</p>
  </article>

  <aside class="lg:order-last">
    <details data-toc open class="group lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto">
      <summary class="flex cursor-pointer list-none items-center justify-between rounded-md border border-gray-200 px-3 py-2 text-sm font-semibold lg:cursor-default lg:border-0 lg:px-0 dark:border-gray-800 [&::-webkit-details-marker]:hidden">
        On this page
        <svg class="size-4 transition-transform group-open:rotate-180 motion-reduce:transition-none lg:hidden" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M5.5 7.5 10 12l4.5-4.5"/></svg>
      </summary>
      <nav aria-label="Table of contents" class="mt-2 border-l border-gray-200 text-sm dark:border-gray-800">
        <ol data-toc-list class="space-y-1"></ol>
      </nav>
    </details>
  </aside>
</div>
```

```js
// toc.js: build the list from headings, then observe them
const LINK = 'block border-l-2 border-transparent py-1 pl-3 text-gray-600 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-blue-600 aria-[current=true]:border-blue-600 aria-[current=true]:font-medium aria-[current=true]:text-blue-600 dark:text-gray-400 dark:hover:text-white';

const slugify = (s) => s.toLowerCase().trim().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');

const buildToc = (source, list) => {
  const headings = [...source.querySelectorAll('h2, h3')];
  headings.forEach((h) => { if (!h.id) h.id = slugify(h.textContent); });
  list.innerHTML = headings.map((h) =>
    `<li class="${h.tagName === 'H3' ? 'ml-3' : ''}"><a href="#${h.id}" class="${LINK}">${h.textContent}</a></li>`).join('');
  return headings;
};

const spy = (headings, list) => {
  const links = new Map(headings.map((h) => [h.id, list.querySelector(`a[href="#${CSS.escape(h.id)}"]`)]));
  let activeId = null;
  const setActive = (id) => {
    if (id === activeId) return;
    links.get(activeId)?.removeAttribute('aria-current');
    links.get(id)?.setAttribute('aria-current', 'true');
    activeId = id;
  };

  const visible = new Set();
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((e) => (e.isIntersecting ? visible.add(e.target) : visible.delete(e.target)));
    // Current = the topmost heading inside the reading band; if none, the last heading above it
    const inBand = headings.filter((h) => visible.has(h));
    if (inBand.length) return setActive(inBand[0].id);
    const above = headings.filter((h) => h.getBoundingClientRect().top < 0).at(-1);
    if (above) setActive(above.id);
  }, { rootMargin: '-80px 0px -70% 0px', threshold: 0 });
  headings.forEach((h) => observer.observe(h));

  // Clicking a link marks it immediately so there is no lag while smooth scroll runs
  list.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (a) setActive(a.hash.slice(1));
  });
};

const source = document.querySelector('[data-toc-source]');
const list = document.querySelector('[data-toc-list]');
if (source && list) spy(buildToc(source, list), list);
```

```css
/* Headings land below the sticky header; smooth scroll only when motion is OK */
h2, h3 { scroll-margin-top: 6rem; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
```

The `rootMargin: '-80px 0px -70% 0px'` shrinks the observed area to a band from 80px (your header height) down to 30% of the viewport. A heading "is current" when it enters that band; when none is in it (long sections), the last heading that scrolled above becomes current.

## Variations

- **Only h2s**: change the selector to `h2`; nested h3 lists make long TOCs noisy. Alternatively, show h3s only under the active h2 with `[&:not(:has([aria-current]))]:hidden`-style grouping.
- **Progress indicator**: add a thin bar that fills with `scrollY / (scrollHeight - innerHeight)`; cheap to compute inside the same observer callback or a passive scroll listener.
- **Update the URL**: `history.replaceState(null, '', '#' + id)` inside `setActive`, so a refresh returns to the section. Skip this if you also use hash-driven tabs on the page.
- **Mobile bottom sheet**: keep the `<details>` but make it `fixed bottom-0 inset-x-0 z-30 bg-white` below `lg:`, with the summary as a persistent bar.

## Pitfalls

- Generated ids must be unique; if two headings share text, append an index (`slug-2`) or you will link and highlight the wrong one.
- Headings need `scroll-margin-top` or every click scrolls the heading under the sticky header.
- Do not mark links `aria-current="page"`; the page is not changing. `aria-current="true"` (or `"location"`) is the right token.
- Measuring with `getBoundingClientRect` on every scroll event is the thing IntersectionObserver avoids; keep layout reads inside the observer callback only.
- `lg:sticky` on the `<details>` needs `lg:self-start` if the grid stretches it; add `self-start` to the `<aside>` or the sticky element never scrolls.
- `max-h` plus `overflow-y-auto` on the TOC keeps very long lists reachable on short screens; without it the bottom links are unreachable.

## Related skills

- `web-nav-anchor-and-smooth-scroll`: in-page links, `scroll-margin-top`, focus after jump.
- `web-nav-sticky-header`: exposing header height as a CSS variable.
- `web-motion-scroll-reveal`: another IntersectionObserver use with staggering.
- `web-seo-content-structure`: heading outline the TOC depends on.
