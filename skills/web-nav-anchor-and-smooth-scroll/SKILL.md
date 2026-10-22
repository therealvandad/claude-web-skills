---
name: web-nav-anchor-and-smooth-scroll
description: Set up in-page anchor links done right: stable ids, scroll-margin-top so targets clear a sticky header, smooth scrolling gated by prefers-reduced-motion, focus moved to the target for keyboard and screen-reader users, "back to top", heading anchor links. Use when a user asks for jump links, "scroll to section", smooth scroll, anchors landing under the header, back-to-top button, or section links.
---

# Anchor links and smooth scrolling

In-page links are the simplest navigation on the web and the most commonly broken: targets hide under sticky headers, smooth scroll ignores motion preferences, and after the jump keyboard focus is still on the link at the top of the page. Three lines of CSS fix the first two; a tiny click handler fixes the third by moving focus to the target. Keep the native `href="#id"` so every link works with JS disabled, copies as a real URL, and shows in the browser's history.

## Pattern

```css
/* 1. Smooth scroll only for people who have not asked for reduced motion */
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
}
/* 2. Every anchor target lands below the sticky header (header height + breathing room) */
:root { --header-h: 4rem; }
:target, [id] { scroll-margin-top: calc(var(--header-h) + 1rem); }
/* 3. Programmatic focus on a section should not draw a ring; links/buttons inside still do */
[tabindex="-1"]:focus:not(:focus-visible) { outline: none; }
```

```html
<header class="sticky top-0 z-40 h-16 bg-white dark:bg-gray-950">
  <nav aria-label="Sections" class="mx-auto flex h-full max-w-5xl items-center gap-4 px-4 text-sm font-medium">
    <a href="#features" class="hover:text-blue-600 focus-visible:outline-2 focus-visible:outline-blue-600">Features</a>
    <a href="#pricing" class="hover:text-blue-600 focus-visible:outline-2 focus-visible:outline-blue-600">Pricing</a>
    <a href="#faq" class="hover:text-blue-600 focus-visible:outline-2 focus-visible:outline-blue-600">FAQ</a>
  </nav>
</header>

<main class="mx-auto max-w-5xl px-4">
  <section id="features" tabindex="-1" class="py-16 scroll-mt-20">
    <h2 class="group text-2xl font-bold">
      Features
      <a href="#features" class="ml-1 text-blue-600 opacity-0 transition-opacity group-hover:opacity-100 focus-visible:opacity-100 motion-reduce:transition-none" aria-label="Link to Features">#</a>
    </h2>
    …
  </section>
  <section id="pricing" tabindex="-1" class="py-16 scroll-mt-20">…</section>
  <section id="faq" tabindex="-1" class="py-16 scroll-mt-20">…</section>
</main>

<a href="#top" data-back-to-top hidden
  class="fixed bottom-4 right-4 z-30 rounded-full bg-gray-900 p-3 text-white shadow-lg transition-opacity hover:bg-gray-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 motion-reduce:transition-none dark:bg-white dark:text-gray-900">
  <span class="sr-only">Back to top</span>
  <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 19V5m-7 7 7-7 7 7"/></svg>
</a>
```

```js
// anchors.js: move focus to the target after an in-page jump; show back-to-top past one viewport
const focusTarget = (hash) => {
  const target = hash && document.getElementById(decodeURIComponent(hash.slice(1)));
  if (!target) return;
  if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  target.focus({ preventScroll: true }); // the browser already scrolled; do not fight it
};
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]');
  if (!a || a.hash === '#' || a.hash === '#top') return;
  // Let the browser scroll (respects scroll-behavior and scroll-margin), then focus
  requestAnimationFrame(() => setTimeout(() => focusTarget(a.hash), 0));
});
window.addEventListener('hashchange', () => focusTarget(location.hash));
if (location.hash) focusTarget(location.hash);

const topBtn = document.querySelector('[data-back-to-top]');
if (topBtn) {
  const toggle = () => { topBtn.hidden = window.scrollY < window.innerHeight; };
  window.addEventListener('scroll', toggle, { passive: true });
  toggle();
  topBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    document.querySelector('h1, main')?.focus?.({ preventScroll: true });
  });
}
```

`scroll-margin-top` on the target (Tailwind `scroll-mt-20`) is what prevents the "landed under the header" bug; `scroll-padding-top` on `html` does the same globally and is the better choice when the header height is known. Smooth scroll is CSS so you never need `scrollIntoView` for plain links.

## Variations

- **Global instead of per-element**: `html { scroll-padding-top: var(--header-h); }` and drop `scroll-mt-*` from sections. Use per-element margins only for exceptions.
- **Tailwind-only, no CSS file**: `motion-safe:scroll-smooth` on `<html>` and `scroll-mt-20` on targets cover the common case.
- **Header height that changes** (shrinking header): keep `--header-h` updated from the header script, see `web-nav-sticky-header`.
- **Offset with JS when the header is `fixed` and unknown height**: `const h = header.getBoundingClientRect().height; document.documentElement.style.setProperty('--header-h', h + 'px')` on load and resize.

## Pitfalls

- `href="#"` scrolls to the top and pollutes the URL with an empty hash; buttons that do nothing navigational should be `<button type="button">`.
- Ids must be valid and unique; prefer lowercase-hyphenated slugs. Characters like `?` or spaces in ids break `#` links and `querySelector` (use `CSS.escape` if you must).
- `scroll-behavior: smooth` on `html` also affects `window.scrollTo` and `scrollIntoView` with default behavior; pass `behavior: 'auto'` for programmatic jumps that should be instant (restoring scroll position, pagination).
- `target.focus()` without `preventScroll` triggers a second scroll that can fight the smooth one; always pass `{ preventScroll: true }` after a native jump.
- `:target` styling (highlighting the jumped-to section) only applies after the hash changes; clicking the same link twice does not retrigger it.
- Back-to-top as a `fixed` button covers content on small screens; respect safe areas with `bottom-[max(1rem,env(safe-area-inset-bottom))]`.

## Related skills

- `web-nav-sticky-header`: the header that creates the offset problem.
- `web-nav-scroll-spy-toc`: highlighting the current section while scrolling.
- `web-a11y-keyboard-and-focus`: focus management rules used here.
- `web-motion-reduced-motion`: the `motion-safe:` / `motion-reduce:` variants.
- `web-a11y-skip-links-and-landmarks`: the skip link is the most important anchor on the page.
