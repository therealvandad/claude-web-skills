---
name: web-motion-scroll-reveal
description: Build reveal-on-scroll (fade/slide-in as elements enter the viewport) with IntersectionObserver, data attributes, staggered children, and a no-JS/reduced-motion fallback that leaves content visible. Use whenever a user asks for "animate on scroll", "fade in when scrolled into view", "AOS-style", "reveal sections", "stagger cards as they appear", or "scroll animations" for a landing page.
---

# Reveal on scroll

Elements start slightly offset and transparent, then transition to their resting state the first time they enter the viewport. The important design decision is that the *hidden* state is applied by JavaScript, not by CSS: if the script fails, is blocked, or the user prefers reduced motion, nothing is ever hidden. IntersectionObserver does the work off the scroll event, so there is no scroll listener and no layout thrash.

## Pattern

```html
<section class="mx-auto max-w-5xl space-y-16 px-4 py-24">
  <h2 data-reveal class="text-3xl font-bold">What you get</h2>

  <ul data-reveal data-reveal-stagger class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
    <li class="rounded-xl border p-6">Fast</li>
    <li class="rounded-xl border p-6">Accessible</li>
    <li class="rounded-xl border p-6">Tiny</li>
  </ul>

  <figure data-reveal="left" class="rounded-xl bg-zinc-100 p-8 dark:bg-zinc-800">
    <img src="chart.svg" alt="Growth over 12 months" class="w-full" />
  </figure>
</section>
```

```css
/* Only elements the script has armed get a hidden state; only when motion is allowed. */
@media (prefers-reduced-motion: no-preference) {
  [data-reveal].is-armed {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 600ms cubic-bezier(0.2, 0, 0, 1), transform 600ms cubic-bezier(0.2, 0, 0, 1);
  }
  [data-reveal="left"].is-armed  { transform: translateX(-32px); }
  [data-reveal="right"].is-armed { transform: translateX(32px); }
  [data-reveal="scale"].is-armed { transform: scale(0.94); }

  [data-reveal-stagger].is-armed > * {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 500ms ease-out, transform 500ms ease-out;
    transition-delay: calc(var(--i, 0) * 90ms);
  }

  [data-reveal].is-visible,
  [data-reveal-stagger].is-visible > * {
    opacity: 1;
    transform: none;
  }
}
```

```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const targets = document.querySelectorAll('[data-reveal]');

function reveal(entries, observer) {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    entry.target.classList.add('is-visible');
    observer.unobserve(entry.target);          // reveal once, then stop watching
  }
}

function arm() {
  if (reduce.matches || !('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver(reveal, {
    rootMargin: '0px 0px -10% 0px',           // fire when 10% up from the bottom edge
    threshold: 0.1,
  });
  targets.forEach((el) => {
    if (el.hasAttribute('data-reveal-stagger')) {
      [...el.children].forEach((child, i) => child.style.setProperty('--i', i));
    }
    el.classList.add('is-armed');
    observer.observe(el);
  });
}

arm();
```

Why `is-armed` instead of hiding in CSS by default: search engines, print, screen readers and anyone with a failed script see full content. Why unobserve after the first hit: re-hiding content when the user scrolls back up is disorienting and makes anchors land on invisible text.

## Variations

- **Tailwind-only version** (no custom CSS): script toggles classes instead: armed = `motion-safe:opacity-0 motion-safe:translate-y-6 motion-safe:transition-[opacity,transform] motion-safe:duration-700`, visible = remove `opacity-0 translate-y-6`. List those literal strings in a static place so Tailwind keeps them.
- **Replay on every entry** (hero stats, decorative items): skip `unobserve` and toggle `is-visible` with `entry.isIntersecting`. Never do this for body text.
- **Direction by position**: pass `data-reveal="left"` to media on the left column and `right` on the right so sections slide toward their resting place (pairs with `web-layout-split-section`).
- **Earlier/later trigger**: `rootMargin: '0px 0px -25% 0px'` waits until the element is well inside the viewport; `'0px 0px 200px 0px'` pre-reveals just below the fold so slow scrollers never see blanks.

## Pitfalls

- Above-the-fold elements that start hidden delay LCP and look broken on a slow script. Do not put `data-reveal` on the hero, or arm it with `requestAnimationFrame` after first paint and a short threshold.
- Large `translateY` (100px+) makes content feel like it is falling in from nowhere; 16-32px is plenty. Big offsets also cause horizontal scrollbars with `translateX`; add `overflow-x-clip` on the section.
- `transform` on a parent breaks `position: fixed` children and creates stacking contexts. Reveal leaf sections, not the `<body>` wrapper.
- A `threshold` of 1 never fires for elements taller than the viewport. Use 0.1 or `0`.
- `IntersectionObserver` callbacks run after scroll settles, so a fast flick can reveal many items at once; stagger delays cap that visually. Keep total stagger under 600 ms or late items feel laggy.
- Reduced motion should not mean "fade only" by default; users with vestibular disorders mostly object to movement, but the safest default is no reveal at all. Offer a crossfade-only variant (`is-armed { transform: none }`) only if the design truly depends on it.

## Related skills

- `web-motion-reduced-motion`
- `web-motion-transitions`
- `web-motion-parallax-and-scroll-driven`
- `web-nav-scroll-spy-toc`
- `web-layout-split-section`
