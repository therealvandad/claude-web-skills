---
name: web-section-stats-band
description: 'Build a stats band or numbers section: three or four large figures with labels, a source line, and an optional count-up that respects reduced motion, as a semantic <dl> in Tailwind v4. Use whenever a user asks for a "stats section", "numbers section", "key figures", "by the numbers", "our impact in numbers", or "big numbers under the hero".'
---

# Stats band

A stats band is the one place on a marketing page where a number does the talking. It only works if the numbers are specific (2,340 not "thousands"), sourced (a date or a report), and typographically dominant: big tabular figures, small labels, hairlines between items. The markup is a `<dl>` because each item is a term (the label) with a value (the figure); screen readers read "Deliveries completed, 2,340" as a pair instead of two loose paragraphs.

## Pattern

```html
<section class="border-y border-stone-200 bg-stone-50 py-16 sm:py-20 dark:border-stone-800 dark:bg-stone-950" aria-labelledby="stats-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <div class="max-w-xl">
      <p class="font-mono text-xs uppercase tracking-widest text-stone-500">Hallam & Daughters, joinery, Sheffield</p>
      <h2 id="stats-heading" class="mt-3 text-3xl font-semibold tracking-tight text-balance text-stone-900 sm:text-4xl dark:text-stone-100">
        Forty years of fitted kitchens, measured
      </h2>
    </div>

    <dl class="mt-12 grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4 lg:divide-x lg:divide-stone-200 dark:lg:divide-stone-800">
      <div class="flex flex-col lg:px-6 lg:first:pl-0">
        <dt class="mt-2 text-sm text-stone-600 dark:text-stone-400">Kitchens fitted since 1986</dt>
        <dd class="order-first text-4xl font-semibold tracking-tight tabular-nums text-stone-900 sm:text-5xl dark:text-stone-100"
            data-count="2340" data-suffix="">2,340</dd>
      </div>
      <div class="flex flex-col lg:px-6">
        <dt class="mt-2 text-sm text-stone-600 dark:text-stone-400">Average from survey to install</dt>
        <dd class="order-first text-4xl font-semibold tracking-tight tabular-nums text-stone-900 sm:text-5xl dark:text-stone-100"
            data-count="11" data-suffix=" days">11 days</dd>
      </div>
      <div class="flex flex-col lg:px-6">
        <dt class="mt-2 text-sm text-stone-600 dark:text-stone-400">Customers who would recommend us</dt>
        <dd class="order-first text-4xl font-semibold tracking-tight tabular-nums text-stone-900 sm:text-5xl dark:text-stone-100"
            data-count="98" data-suffix="%">98%</dd>
      </div>
      <div class="flex flex-col lg:px-6">
        <dt class="mt-2 text-sm text-stone-600 dark:text-stone-400">Joiners on the workshop floor</dt>
        <dd class="order-first text-4xl font-semibold tracking-tight tabular-nums text-stone-900 sm:text-5xl dark:text-stone-100"
            data-count="14" data-suffix="">14</dd>
      </div>
    </dl>

    <p class="mt-10 font-mono text-xs text-stone-500">
      Source: job book and post-install survey, January 2025 to December 2025. Recommendation figure is 412 of 420 responses.
    </p>
  </div>
</section>
```

```js
// Count-up on first view. Skipped entirely under prefers-reduced-motion: the HTML already holds the final text.
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const fmt = new Intl.NumberFormat('en-GB');

function countUp(el) {
  const target = Number(el.dataset.count);
  const suffix = el.dataset.suffix ?? '';
  const duration = 900;
  const start = performance.now();
  const tick = (now) => {
    const t = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = fmt.format(Math.round(target * eased)) + suffix;
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

if (!reduce && 'IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      countUp(e.target);
      io.unobserve(e.target);
    }
  }, { threshold: 0.4 });
  document.querySelectorAll('[data-count]').forEach((el) => io.observe(el));
}
```

Why these choices:

- `<dt>` (label) comes first in the source because the spec requires it, and `flex flex-col` plus `order-first` on the `<dd>` puts the figure on top visually. Screen readers still get label-then-value.
- `tabular-nums` keeps digits the same width so the count-up does not jitter horizontally.
- `data-count` holds the raw number; the text content holds the formatted final value, so the figure is correct with JavaScript off.
- `lg:divide-x` draws hairlines only on desktop; on phones the 2-column grid relies on spacing.
- The source line is not decoration. A figure without a date or sample size is a claim; with one it is evidence.

## Variations

- **Dark band**: `bg-stone-950 text-stone-100 border-stone-800`, labels `text-stone-400`, divide lines `divide-stone-800`. Keep the figures white, not an accent colour; one accent is allowed on a single headline figure (`text-amber-500`).
- **Three figures, no heading**: drop the heading block, use `sm:grid-cols-3`, and put the source line directly under the `<dl>`. Works as a thin strip between a hero and the next section.
- **Figure with sparkline or trend**: add `<span class="ml-2 text-base font-medium text-emerald-700">+12%</span>` inside the `<dd>` after the number. Use one colour for up and plain text for down; do not colour every figure.
- **Compact inline row**: `flex flex-wrap gap-x-10 gap-y-4` with `text-2xl` figures and `text-xs` labels beside them. Use inside a hero or a sidebar rather than as its own section.

## Pitfalls

- Starting every figure at 0 and counting up is the main cause of layout shift in stats bands: "0" is narrower than "2,340". Set the final text in HTML and let the script overwrite it, or add `min-w-[4ch]` to each `<dd>`.
- Rounded marketing numbers ("10,000+", "99%") read as invented. Use the real figure, and if you must round, say so in the source line.
- A `<dl>` with wrapper `<div>`s is valid HTML, but a `<dl>` with `<li>` is not. Do not switch to `<ul>` for styling; `grid` works on the `<dl>` directly.
- Count-up for a value with a decimal (4.7) rounds to integers in the snippet above. Pass `data-decimals="1"` and use `toFixed` instead of `Math.round`.
- Four figures on `lg:grid-cols-4` with long labels wrap to three lines on 1024px screens. Keep labels under about 35 characters or drop to `lg:grid-cols-3`.
- Animating numbers that the user cannot see change (below the fold at load) is wasted work; the IntersectionObserver guards this, so do not replace it with a `load` listener.

## Related skills

- `web-motion-counters-and-tickers`
- `web-motion-reduced-motion`
- `web-craft-real-content`
- `web-craft-anti-generic-design`
- `web-layout-landing-page`
- `web-css-responsive-grid`
