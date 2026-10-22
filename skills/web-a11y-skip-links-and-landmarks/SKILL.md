---
name: web-a11y-skip-links-and-landmarks
description: Add a "skip to main content" link that appears on focus, structure the page into named landmarks (banner, navigation, main, complementary, contentinfo, search, region), and label repeated regions so screen reader users can jump between them. Use when a user asks for "skip link", "skip navigation", "landmarks", "aria-label on nav", "bypass blocks", or an accessibility audit flags WCAG 2.4.1.
---

# Skip links and landmarks

WCAG 2.2 SC 2.4.1 (Bypass Blocks) requires a way past content repeated on every page, chiefly the
header navigation. Two mechanisms satisfy it together: a skip link as the first focusable element,
for keyboard users who do not run a screen reader, and landmarks, which screen readers list in a
rotor so users can jump straight to `main` or to a named `nav`. Landmarks come free from the right
HTML elements; the work is making sure there is one `main`, that repeated landmarks have unique
names, and that the skip link actually moves focus.

## Pattern

```html
<body class="min-h-dvh flex flex-col">
  <!-- First focusable element on the page. Invisible until focused. -->
  <a href="#main"
     class="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-blue-700 focus:px-4 focus:py-2 focus:text-white focus:outline-2 focus:outline-offset-2 focus:outline-blue-700">
    Skip to main content
  </a>

  <header class="border-b">
    <nav aria-label="Main" class="mx-auto flex max-w-6xl items-center gap-4 p-4">
      <a href="/" class="font-semibold">Acme</a>
      <ul class="flex gap-4">
        <li><a href="/docs">Docs</a></li>
        <li><a href="/blog">Blog</a></li>
      </ul>
      <form role="search" action="/search" class="ml-auto">
        <label for="q" class="sr-only">Search site</label>
        <input id="q" name="q" type="search" class="rounded-md border px-2 py-1" placeholder="Search">
      </form>
    </nav>
  </header>

  <div class="mx-auto flex w-full max-w-6xl flex-1 gap-8 p-4">
    <!-- tabindex=-1 lets the skip link target receive focus in every browser -->
    <main id="main" tabindex="-1" class="min-w-0 flex-1 outline-none">
      <h1 class="text-3xl font-bold">Getting started</h1>
      <nav aria-label="On this page" class="mt-4 text-sm">
        <ol><li><a href="#install">Install</a></li><li><a href="#configure">Configure</a></li></ol>
      </nav>
      <section id="install" aria-labelledby="install-h"><h2 id="install-h">Install</h2></section>
      <section id="configure" aria-labelledby="configure-h"><h2 id="configure-h">Configure</h2></section>
    </main>

    <aside aria-label="Related guides" class="hidden w-64 lg:block">
      <h2 class="font-semibold">Related</h2>
    </aside>
  </div>

  <footer class="border-t p-4">
    <nav aria-label="Footer" class="flex gap-4 text-sm">
      <a href="/privacy">Privacy</a><a href="/terms">Terms</a>
    </nav>
  </footer>
</body>
```

```js
// Safari and older Chrome scroll to the anchor but do not move focus. Fix it once, globally.
document.addEventListener('click', (e) => {
  const link = e.target.closest('a[href^="#"]');
  if (!link) return;
  const target = document.getElementById(decodeURIComponent(link.getAttribute('href').slice(1)));
  if (!target) return;
  if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  target.focus({ preventScroll: false });
});
```

Landmark map produced by this page: `banner` (header), `navigation "Main"`, `search`,
`main`, `navigation "On this page"`, `region "Install"`, `region "Configure"`,
`complementary "Related guides"`, `contentinfo` (footer), `navigation "Footer"`. Three navs, each
distinguishable by name; that is the whole point of `aria-label` here.

Why `sr-only` / `focus:not-sr-only`: the link is in the DOM and the tab order at all times, so it
is reachable, but visually hidden until focused. `display:none` or `visibility:hidden` would remove
it from the tab order and defeat it. The skip link must be the first thing in `<body>`, before any
logo link or cookie banner.

## Variations

- **Several skip targets** on complex pages: a small list, "Skip to content", "Skip to search",
  "Skip to filters"; render as `<nav aria-label="Skip links">` with each link styled the same way.
- **Skip past a long widget** (a carousel, a code block, a data table): put a skip link right
  before it, `<a href="#after-table" class="sr-only focus:not-sr-only">Skip table</a>`.
- **Sticky header**: add `scroll-margin-top` on `#main` (Tailwind `scroll-mt-20`) so the focused
  heading is not hidden under the bar (WCAG 2.2 SC 2.4.11).
- **Dashboard layouts**: `<nav aria-label="Primary">` for the sidebar, `<header>` for the top bar,
  one `<main>` per view; see `web-layout-dashboard-sidebar`.

## Pitfalls

- More than one `<main>`, or `<main>` inside an element with `hidden`. Screen readers expect
  exactly one visible main landmark.
- Unlabelled repeated landmarks: two `<nav>` elements with no name announce identically as
  "navigation". Name every nav when there is more than one. Do not include the word "navigation"
  in the label; it is announced already ("Main navigation navigation").
- Wrapping almost the whole page in `<nav>` or `<section aria-label>`; landmarks that contain
  everything help no one. Keep them to the real regions.
- `<header>`/`<footer>` nested inside `<article>`, `<section>`, `<main>` are not landmarks. That
  is correct behaviour; the page-level banner and contentinfo must be direct children of `<body>`
  (or of a wrapper div, which is fine).
- Skip link that scrolls but leaves focus on the link, so the next Tab goes back into the nav.
  The `tabindex="-1"` on the target and the focus script above fix it.
- Styling the skip link with `top:-100px` tricks; use `sr-only` so it is not clipped by
  `overflow:hidden` ancestors and does not cause a horizontal scrollbar.

## Related skills

- `web-a11y-semantic-html`
- `web-a11y-keyboard-and-focus`
- `web-nav-responsive-navbar`
- `web-nav-anchor-and-smooth-scroll`
- `web-layout-page-shell`
- `web-layout-dashboard-sidebar`
