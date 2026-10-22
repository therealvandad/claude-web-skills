---
name: web-motion-parallax-and-scroll-driven
description: Build scroll-driven animations with pure CSS (animation-timeline: scroll() / view()) for parallax backgrounds, reading-progress bars, and elements that fade or scale as they pass through the viewport, with an @supports gate, reduced-motion handling, and a JS fallback. Use whenever a user asks for "parallax", "animate on scroll position", "progress bar as I scroll", "scroll-linked", "scrubbed animation", or "scroll-driven animations".
---

# Parallax and scroll-driven animations

Scroll-driven animations bind a normal `@keyframes` animation to scroll position instead of time: the browser scrubs it as the user scrolls, on the compositor, with no `scroll` listener and no jank. `animation-timeline: scroll()` tracks a scroll container's progress (reading-progress bars, parallax); `animation-timeline: view()` tracks an element's own journey through the viewport (fade/scale as it enters). Support (2026): Chrome/Edge 115+, Safari 26+, Firefox 110+ behind a flag until recent releases; check caniuse before relying on it. Wrap everything in `@supports (animation-timeline: scroll())` so unsupported browsers get a static page, which is the correct fallback for decoration.

## Pattern

```html
<!-- 1. Reading progress bar bound to the document scroll -->
<div class="progress fixed inset-x-0 top-0 z-50 h-1 origin-left bg-blue-600" aria-hidden="true"></div>

<!-- 2. Parallax hero: background layer moves slower than the content -->
<header class="relative isolate h-[70vh] overflow-hidden">
  <img src="/img/mountains.jpg" alt="" aria-hidden="true"
       class="parallax-bg absolute inset-0 -z-10 size-full object-cover" />
  <div class="flex h-full items-center justify-center bg-black/30 px-4 text-center text-white">
    <h1 class="text-4xl font-bold sm:text-6xl">Base camp</h1>
  </div>
</header>

<!-- 3. Items that fade and rise as they travel through the viewport -->
<section class="mx-auto max-w-3xl space-y-24 px-4 py-24">
  <article class="enter rounded-xl border p-8">First</article>
  <article class="enter rounded-xl border p-8">Second</article>
  <article class="enter rounded-xl border p-8">Third</article>
</section>
```

```css
@supports (animation-timeline: scroll()) {
  @media (prefers-reduced-motion: no-preference) {

    /* 1. Scrub 0 -> 100% of the page scroll into scaleX 0 -> 1 */
    .progress {
      animation: grow linear both;
      animation-timeline: scroll(root block);
    }
    @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

    /* 2. Move the background by less than the scroll distance (ratio ~0.4) */
    .parallax-bg {
      scale: 1.3;                       /* oversize so edges never show */
      animation: drift linear both;
      animation-timeline: scroll(root block);
      animation-range: 0 100vh;         /* only while the hero is on screen */
    }
    @keyframes drift { to { transform: translateY(40vh); } }

    /* 3. Fade/rise during the first 40% of the element's entry into view */
    .enter {
      animation: rise linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 40%;
    }
    @keyframes rise {
      from { opacity: 0; transform: translateY(32px) scale(0.97); }
    }
  }
}
```

```js
// Fallback for the progress bar only (parallax and reveal just stay static when unsupported).
if (!CSS.supports('animation-timeline: scroll()') &&
    !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const bar = document.querySelector('.progress');
  const update = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? scrollY / max : 0})`;
  };
  addEventListener('scroll', update, { passive: true });
  update();
}
```

Why `linear` timing: with a scroll timeline the easing is applied across scroll distance, not time; anything but `linear` makes the element lag the finger. Why `both`: the element holds the `from` state before the range starts and the `to` state after.

## Variations

- **Named scroll container**: for a scrolling `<main>` instead of the document, set `scroll-timeline-name: --main` on it and use `animation-timeline: --main` on any descendant (or ancestor, via `timeline-scope`).
- **Horizontal scroll galleries**: `animation-timeline: view(inline)` plus `animation-range: cover` for a scrubbed scale as cards pass the centre of a scroll-snap row (`web-ui-carousel`).
- **Sticky "pinned" scenes**: a tall section with a `sticky top-0` child; animate the child's children with `view()` on the tall parent via `timeline-scope`, so the content changes while the frame stays pinned.
- **Range keywords**: `entry`, `exit`, `cover`, `contain`; `entry 0% entry 100%` is the whole time the element is crossing the bottom edge, `cover` is its full on-screen lifetime.

## Pitfalls

- Parallax is a classic vestibular trigger. Keep ratios gentle (0.2-0.5), never apply to text, and always gate on `prefers-reduced-motion: no-preference`; users with the setting get a plain image.
- `transform`-based parallax on a background that is not oversized reveals empty strips at the edges; `scale: 1.3` (or extra height) covers the travel distance.
- A `scroll` listener fallback that does layout reads (`getBoundingClientRect`) inside the handler causes jank; read `scrollY`/`scrollHeight` only, write transforms, and throttle with `requestAnimationFrame` if you add more work.
- `animation-timeline` must come *after* the `animation` shorthand, because the shorthand resets `animation-timeline` to `auto`. Order matters.
- The `.enter` pattern keeps animating backwards when the user scrolls up (the keyframe is scrubbed). If content must stay revealed, use `IntersectionObserver` (`web-motion-scroll-reveal`) instead.
- `position: fixed` inside a transformed parent breaks. Keep the progress bar outside the parallax header, as a direct child of `<body>`.
- Overflow clipping: `view()` timelines measure against the nearest scroll container; an ancestor with `overflow: hidden` that is not the one scrolling can make the range never fire. Prefer `overflow: clip` for decorative clipping.

## Related skills

- `web-motion-scroll-reveal`
- `web-motion-reduced-motion`
- `web-motion-keyframes`
- `web-css-sticky-and-fixed`
- `web-perf-web-vitals`
