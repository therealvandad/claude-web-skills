---
name: web-ui-carousel
description: 'Build a carousel/slider with CSS scroll-snap: swipeable slides, previous/next buttons, dot indicators synced by IntersectionObserver, optional autoplay that pauses on hover, focus and reduced motion. Use whenever a user asks for a carousel, slider, slideshow, image gallery strip, product scroller, testimonial rotator, or "swipe through" cards, without a library.'
---

# Scroll-snap carousel

A scroller with `scroll-snap-type` is a carousel the browser already knows how to drive: touch swiping, trackpad, keyboard arrows when focused, and momentum are native, and the content is just a list that works with no JavaScript. Script only adds conveniences: buttons that call `scrollBy`, dots that reflect the visible slide, and autoplay that stops the moment the user shows interest. This beats a translate-based slider on size, accessibility and feel.

## Pattern

```html
<section aria-roledescription="carousel" aria-label="Featured products" class="relative mx-auto max-w-5xl px-4">
  <ul id="carousel" tabindex="0" aria-live="polite"
    class="flex snap-x snap-mandatory gap-4 overflow-x-auto scroll-smooth motion-reduce:scroll-auto
           [scrollbar-width:none] [&::-webkit-scrollbar]:hidden
           focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-600">
    <li class="w-[85%] shrink-0 snap-center sm:w-[48%] lg:w-[32%]" aria-roledescription="slide" aria-label="1 of 4">
      <article class="h-full overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
        <img src="/img/one.jpg" alt="Oak desk in a bright studio" width="640" height="400" loading="lazy" class="aspect-[16/10] w-full object-cover">
        <div class="p-4"><h3 class="font-semibold">Studio desk</h3><p class="text-sm text-gray-600 dark:text-gray-400">From $420</p></div>
      </article>
    </li>
    <li class="w-[85%] shrink-0 snap-center sm:w-[48%] lg:w-[32%]" aria-roledescription="slide" aria-label="2 of 4">…</li>
    <li class="w-[85%] shrink-0 snap-center sm:w-[48%] lg:w-[32%]" aria-roledescription="slide" aria-label="3 of 4">…</li>
    <li class="w-[85%] shrink-0 snap-center sm:w-[48%] lg:w-[32%]" aria-roledescription="slide" aria-label="4 of 4">…</li>
  </ul>

  <div class="mt-4 flex items-center justify-between">
    <div class="flex gap-2">
      <button type="button" data-dir="-1" aria-label="Previous slide"
        class="rounded-full border border-gray-300 p-2 hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 disabled:opacity-40 dark:border-gray-700 dark:hover:bg-gray-800">
        <svg class="size-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 0 1-.02 1.06L8.83 10l3.94 3.71a.75.75 0 1 1-1.04 1.08l-4.5-4.25a.75.75 0 0 1 0-1.08l4.5-4.25a.75.75 0 0 1 1.06.02Z" clip-rule="evenodd"/></svg>
      </button>
      <button type="button" data-dir="1" aria-label="Next slide" class="rounded-full border border-gray-300 p-2 hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 disabled:opacity-40 dark:border-gray-700 dark:hover:bg-gray-800">
        <svg class="size-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 0 1 .02-1.06L11.17 10 7.23 6.29a.75.75 0 1 1 1.04-1.08l4.5 4.25a.75.75 0 0 1 0 1.08l-4.5 4.25a.75.75 0 0 1-1.06-.02Z" clip-rule="evenodd"/></svg>
      </button>
    </div>
    <div id="dots" class="flex gap-2" role="group" aria-label="Choose slide"></div>
    <button type="button" id="autoplay" aria-pressed="true" class="text-sm text-gray-600 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-indigo-600 dark:text-gray-400">Pause</button>
  </div>
</section>
```

```js
function initCarousel(root) {
  const track = root.querySelector('#carousel');
  const slides = [...track.children];
  const dots = root.querySelector('#dots');
  const prev = root.querySelector('[data-dir="-1"]'), next = root.querySelector('[data-dir="1"]');
  const playBtn = root.querySelector('#autoplay');
  let current = 0, timer = null;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Dots
  slides.forEach((_, i) => {
    const b = document.createElement('button');
    b.type = 'button'; b.setAttribute('aria-label', `Go to slide ${i + 1}`);
    b.className = 'size-2.5 rounded-full bg-gray-300 aria-[current=true]:bg-indigo-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 dark:bg-gray-700';
    b.addEventListener('click', () => goTo(i));
    dots.append(b);
  });

  const goTo = (i) => slides[(i + slides.length) % slides.length].scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', inline: 'center', block: 'nearest' });
  prev.addEventListener('click', () => goTo(current - 1));
  next.addEventListener('click', () => goTo(current + 1));

  // Keep `current`, dots and button state in sync with whatever the user scrolled to
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      current = slides.indexOf(en.target);
      [...dots.children].forEach((d, i) => d.setAttribute('aria-current', i === current));
    });
  }, { root: track, threshold: 0.6 });
  slides.forEach((s) => io.observe(s));

  // Autoplay: off under reduced motion; pauses on hover, focus, hidden tab
  const start = () => { if (!timer && !reduceMotion && playBtn.getAttribute('aria-pressed') === 'true') timer = setInterval(() => goTo(current + 1), 5000); };
  const stop = () => { clearInterval(timer); timer = null; };
  playBtn.addEventListener('click', () => {
    const playing = playBtn.getAttribute('aria-pressed') === 'true';
    playBtn.setAttribute('aria-pressed', String(!playing));
    playBtn.textContent = playing ? 'Play' : 'Pause';
    playing ? stop() : start();
  });
  ['mouseenter', 'focusin', 'touchstart'].forEach((ev) => root.addEventListener(ev, stop, { passive: true }));
  ['mouseleave', 'focusout'].forEach((ev) => root.addEventListener(ev, start));
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
  if (reduceMotion) { playBtn.setAttribute('aria-pressed', 'false'); playBtn.textContent = 'Play'; }
  start();
}
initCarousel(document.querySelector('[aria-roledescription="carousel"]'));
```

Why this shape: `snap-mandatory` with `snap-center` on each slide gives clean stops; `scrollIntoView` with `inline: 'center'` reuses the same snapping for buttons and dots so there is one source of truth (the scroll position). The IntersectionObserver reads that truth back instead of guessing from an index. Autoplay is opt-out-by-default for `prefers-reduced-motion` because moving content is a WCAG 2.2.2 failure unless it can be paused.

## Variations

- **One slide per view (hero slider)**: `w-full snap-start` on slides and `snap-x snap-mandatory` on the track; drop the `sm:`/`lg:` widths.
- **Peek the next slide**: keep `w-[85%]` and add `px-[7.5%]` + `scroll-px-[7.5%]` on the track so the edges hint at more content.
- **Thumbnails as dots**: generate `<button>`s containing `<img>` instead of circles; same `goTo` handler.
- **Infinite loop**: scroll-snap cannot wrap, so `goTo` already wraps the index and jumps back to slide 1 after the last. For a seamless loop, clone the first/last slides and reset `scrollLeft` silently on reaching a clone.
- **No JS at all**: delete the buttons and dots; the track alone is a fully working swipeable list with a scrollbar (remove the scrollbar-hiding classes in that case).

## Pitfalls

- Hiding the scrollbar removes the only visual affordance for mouse users without buttons; hide it only when you render prev/next controls.
- `scroll-smooth` fights `prefers-reduced-motion`; the `motion-reduce:scroll-auto` class and the `behavior` check in JS both matter.
- Slides must be `shrink-0`; otherwise flex squeezes them to fit and nothing scrolls.
- Autoplay that cannot be paused, or that keeps moving while a user is tabbing through it, is an accessibility failure. Pause on `focusin` and expose a visible Pause control.
- `aria-live="polite"` on the track makes screen readers announce slide changes from autoplay; remove it if slides change only by user action to avoid double announcements.
- Lazy-load images beyond the first two (`loading="lazy"`) and set `width`/`height` so the track does not jump as images arrive.

## Related skills

- `web-ui-cards`
- `web-layout-testimonials`
- `web-motion-reduced-motion`
- `web-css-aspect-ratio-media`
- `web-perf-images`
