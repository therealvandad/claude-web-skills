---
name: web-motion-counters-and-tickers
description: Build animated number counters (count up on scroll into view, eased, locale-formatted, static under reduced motion) and an infinite CSS logo/text marquee that pauses on hover/focus and degrades to a scroll-snap row. Use whenever a user asks for "stats that count up", "animated numbers", "odometer", "logo marquee", "scrolling ticker", "news ticker", or "brands that scroll by themselves".
---

# Counters and tickers

Two staples of marketing pages that are easy to get wrong. A count-up counter is pure JS (`requestAnimationFrame` interpolation, triggered once by IntersectionObserver), so the final number must be in the HTML from the start: no-JS users, crawlers, and reduced-motion users all see "12,400+" immediately. A marquee is pure CSS (`transform` keyframes on a duplicated track) and must pause on hover and focus, never hide content that is only reachable by waiting, and fall back to a plain horizontally scrollable row.

## Pattern

**Counters**

```html
<dl class="grid grid-cols-2 gap-8 text-center sm:grid-cols-3">
  <div>
    <dt class="text-sm text-zinc-600">Customers</dt>
    <dd class="text-4xl font-bold tabular-nums" data-counter="12400" data-suffix="+">12,400+</dd>
  </div>
  <div>
    <dt class="text-sm text-zinc-600">Uptime</dt>
    <dd class="text-4xl font-bold tabular-nums" data-counter="99.98" data-decimals="2" data-suffix="%">99.98%</dd>
  </div>
  <div>
    <dt class="text-sm text-zinc-600">Countries</dt>
    <dd class="text-4xl font-bold tabular-nums" data-counter="42">42</dd>
  </div>
</dl>
```

```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

function countUp(el, duration = 1600) {
  const target = parseFloat(el.dataset.counter);
  const decimals = Number(el.dataset.decimals ?? 0);
  const suffix = el.dataset.suffix ?? '';
  const fmt = new Intl.NumberFormat(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  const start = performance.now();
  el.setAttribute('aria-label', fmt.format(target) + suffix);   // screen readers hear the final value only

  function frame(now) {
    const t = Math.min(1, (now - start) / duration);
    el.textContent = fmt.format(target * easeOutCubic(t)) + suffix;
    if (t < 1) requestAnimationFrame(frame);
    else el.removeAttribute('aria-label');
  }
  requestAnimationFrame(frame);
}

if (!reduce && 'IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries, obs) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      countUp(e.target);
      obs.unobserve(e.target);
    }
  }, { threshold: 0.5 });
  document.querySelectorAll('[data-counter]').forEach((el) => io.observe(el));
}
```

**Ticker / marquee**

```html
<section aria-label="Trusted by" class="overflow-hidden py-8 [mask-image:linear-gradient(90deg,transparent,black_10%,black_90%,transparent)]">
  <div class="marquee flex w-max gap-12 hover:[animation-play-state:paused] focus-within:[animation-play-state:paused]">
    <ul class="flex shrink-0 items-center gap-12">
      <li><img src="/logos/a.svg" alt="Acme" class="h-8" /></li>
      <li><img src="/logos/b.svg" alt="Globex" class="h-8" /></li>
      <li><img src="/logos/c.svg" alt="Initech" class="h-8" /></li>
    </ul>
    <ul class="flex shrink-0 items-center gap-12" aria-hidden="true">
      <li><img src="/logos/a.svg" alt="" class="h-8" /></li>
      <li><img src="/logos/b.svg" alt="" class="h-8" /></li>
      <li><img src="/logos/c.svg" alt="" class="h-8" /></li>
    </ul>
  </div>
</section>
```

```css
@media (prefers-reduced-motion: no-preference) {
  .marquee { animation: marquee 30s linear infinite; }
  @keyframes marquee { to { transform: translateX(calc(-50% - 1.5rem)); } } /* half track + half the gap */
}
@media (prefers-reduced-motion: reduce) {
  .marquee { width: 100%; overflow-x: auto; scroll-snap-type: x mandatory; }
  .marquee > ul:last-child { display: none; }   /* no duplicate when it does not loop */
  .marquee li { scroll-snap-align: start; }
}
```

Why duplicate the list: the track scrolls exactly half its width, and the second copy slides in where the first was, so the loop is seamless. Why `aria-hidden` on the clone: screen readers hear each logo once. Why `tabular-nums` on counters: digits keep a fixed width so the number does not jitter horizontally while counting.

## Variations

- **Speed by content length**: set `--items` and use `animation-duration: calc(var(--items) * 4s)` so longer tickers do not race.
- **Reverse direction / second row**: `[animation-direction:reverse]` on a second track for the two-row "wall" effect.
- **Vertical ticker** (news headlines): same technique with `flex-col` and `translateY(-50%)`; add `aria-live="off"` so updates do not spam screen readers.
- **Odometer-style digits**: wrap each digit in an `overflow-hidden` span of fixed height and `translateY` a column of 0-9; heavier, use only for one hero number.
- **Format big numbers** compactly with `new Intl.NumberFormat(undefined, { notation: 'compact' })` ("1.2M"); animate the raw value and format on each frame.

## Pitfalls

- Counting from 0 while the stat is above the fold delays the first meaningful paint of the number; the HTML already holds the final value, so only arm the observer, do not blank the text first.
- Counters inside a `dd` with `data-counter` that re-enter the viewport should not re-run; `unobserve` handles it. Avoid re-running on tab switches, SPA re-renders, or `pageshow` from bfcache.
- A marquee with interactive links needs a pause on `focus-within` (done above) and the links in the hidden clone must be unfocusable: add `tabindex="-1"` to cloned `<a>`s or keep clones non-interactive.
- `translateX(-50%)` only loops cleanly when the two copies plus gaps are identical widths; the `- 1.5rem` term compensates for the `gap-12` between the copies. Change both together.
- Images with no intrinsic size make the track width jump as they load, visible as a stutter; set `width`/`height` attributes or `h-8 w-auto` plus `aspect-ratio`.
- Very long durations (`60s+`) look frozen; very short (`<15s`) are unreadable. 20-40 s for a viewport-wide track is the usual range, and `linear` is mandatory; any easing makes a loop visibly pulse.

## Related skills

- `web-motion-scroll-reveal`
- `web-motion-keyframes`
- `web-motion-reduced-motion`
- `web-ui-carousel`
- `web-layout-testimonials`
