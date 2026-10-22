---
name: web-nav-sticky-header
description: Build a sticky site header that shrinks when the page is scrolled and hides when scrolling down, reappearing on scroll up, using a cheap scroll listener with requestAnimationFrame, data attributes for state, and a prefers-reduced-motion fallback. Use when a user asks for a sticky/fixed header, "header that hides when I scroll", a shrinking navbar, or a compact header on scroll.
---

# Sticky header that shrinks and hides on scroll

`position: sticky` alone gives you a header that stays put; most sites also want it to get out of the way. The reliable approach is two state flags set from a throttled scroll handler: `data-scrolled` (past a threshold, so shrink and add a shadow) and `data-hidden` (user is scrolling down and past the header height, so slide it up). Everything visual is CSS reacting to those attributes, which keeps the JS tiny and lets `motion-reduce:` turn the slide into an instant change. A small hysteresis stops the header from flickering on trackpad bounces.

## Pattern

```html
<header data-header
  class="sticky top-0 z-40 bg-white/90 backdrop-blur transition-[translate,box-shadow,padding] duration-300 ease-out motion-reduce:transition-none data-[scrolled]:shadow-md data-[hidden]:-translate-y-full dark:bg-gray-950/90">
  <nav aria-label="Main" class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 transition-[padding] duration-300 motion-reduce:transition-none [[data-scrolled]_&]:py-2">
    <a href="/" class="flex items-center gap-2 font-bold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
      <img src="/logo.svg" alt="" class="h-8 w-auto transition-[height] duration-300 motion-reduce:transition-none [[data-scrolled]_&]:h-6">
      Acme
    </a>
    <ul class="flex gap-4 text-sm font-medium">
      <li><a href="/features" class="hover:text-blue-600">Features</a></li>
      <li><a href="/pricing" class="hover:text-blue-600">Pricing</a></li>
    </ul>
  </nav>
</header>

<main>…</main>
```

```js
// sticky-header.js
const initStickyHeader = (header, { shrinkAt = 24, hideAfter = 8 } = {}) => {
  let lastY = window.scrollY;
  let ticking = false;

  const update = () => {
    const y = window.scrollY;
    const dy = y - lastY;
    header.toggleAttribute('data-scrolled', y > shrinkAt);
    // Hide only when scrolling down, past the header, and by more than the hysteresis
    if (dy > hideAfter && y > header.offsetHeight) header.setAttribute('data-hidden', '');
    else if (dy < -hideAfter || y <= header.offsetHeight) header.removeAttribute('data-hidden');
    lastY = y;
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(update); ticking = true; }
  }, { passive: true });

  // Always reveal when focus lands inside the header (keyboard users) or the user starts scrolling up with keys
  header.addEventListener('focusin', () => header.removeAttribute('data-hidden'));
  update();
};
initStickyHeader(document.querySelector('[data-header]'));
```

Expose the current header height for anchors and sticky elements under it:

```css
@layer base {
  :root { --header-h: 4.5rem; }
  :root:has([data-header][data-scrolled]) { --header-h: 3rem; }
  html { scroll-padding-top: calc(var(--header-h) + 1rem); }
}
```

The `[[data-scrolled]_&]:` arbitrary variant means "this element when an ancestor has `data-scrolled`", so children can shrink without their own JS. `translate-y` is composited and cheap; animating `height` or `top` would trigger layout every frame.

## Variations

- **Shrink only, never hide**: delete the `data-hidden` lines; keep the shadow and padding change. Safer for sites with important header actions (cart, search).
- **Hide only on mobile**: wrap the hide logic in `if (window.matchMedia('(max-width: 47.99rem)').matches)`, since desktop has room to keep the bar.
- **Scroll-driven, no JS**: `animation-timeline: scroll()` can drive shrink (not direction-aware hide): define `@keyframes shrink { to { padding-block: .5rem; box-shadow: var(--shadow-md) } }` and apply `animation: shrink linear both; animation-timeline: scroll(); animation-range: 0 100px;` behind `@supports (animation-timeline: scroll())`.
- **Transparent over hero**: start with `bg-transparent text-white` and switch to `data-[scrolled]:bg-white data-[scrolled]:text-gray-900`.

## Pitfalls

- `sticky` fails silently if any ancestor has `overflow: hidden/auto` or the header is not tall enough to be sticky inside its parent. Keep the header a direct child of `<body>`.
- Hiding the header while a keyboard user tabs into it leaves focus on an invisible link; the `focusin` listener above is not optional.
- Without hysteresis (`hideAfter`), iOS rubber-banding and trackpad micro-scrolls toggle the header every frame.
- `backdrop-blur` is expensive on large areas; keep the header short and avoid blur on low-end targets or add `supports-[backdrop-filter]:bg-white/70`.
- Changing header height shifts the layout below only if the header is `fixed`; with `sticky` the space is reserved from the taller state, so the shrink does not cause CLS.
- Anchor links under a sticky header land hidden unless `scroll-padding-top` or `scroll-margin-top` is set (see the CSS above).

## Related skills

- `web-nav-responsive-navbar`: the bar content and mobile toggle.
- `web-nav-anchor-and-smooth-scroll`: `scroll-margin-top` under this header.
- `web-css-sticky-and-fixed`: sticky mechanics and z-index strategy.
- `web-motion-reduced-motion`: the `motion-reduce:` variant used here.
- `web-motion-parallax-and-scroll-driven`: the no-JS scroll-timeline variation.
