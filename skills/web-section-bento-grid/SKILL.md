---
name: web-section-bento-grid
description: 'Build a bento grid section: mixed-size tiles with column and row spans, one hero tile with a real screenshot, dense packing with no holes, and a sensible single-column order on phones, in Tailwind v4. Use whenever a user asks for a "bento", "bento box layout", "Apple-style feature grid", "mixed size cards", or "tiles of different sizes".'
---

# Bento grid

A bento grid gives features different sizes because they have different weights: one thing deserves a screenshot, two deserve a sentence, one deserves a number. The spans are the point; if every tile is the same size it is a card grid. Build it on a fixed column count (`lg:grid-cols-6`) with explicit `col-span` and `row-span` per tile, `grid-flow-dense` to fill gaps, and a DOM order that already reads well as a single column, because that is what phones get.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="bento-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <div class="max-w-xl">
      <p class="font-mono text-xs uppercase tracking-widest text-stone-500">Rota, Bristol cafe scheduling</p>
      <h2 id="bento-heading" class="mt-3 text-3xl font-semibold tracking-tight text-balance text-stone-900 sm:text-4xl dark:text-stone-100">
        The week's shifts, sorted on a Sunday night in nine minutes
      </h2>
    </div>

    <ul role="list" class="mt-12 grid auto-rows-[minmax(10rem,auto)] grid-flow-dense grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">

      <!-- Hero tile: screenshot, spans 4 columns and 2 rows on desktop -->
      <li class="relative overflow-hidden rounded-lg border border-stone-300 bg-white sm:col-span-2 lg:col-span-4 lg:row-span-2 dark:border-stone-700 dark:bg-stone-950">
        <div class="p-6">
          <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Drag a name onto a shift</h3>
          <p class="mt-1 max-w-md text-sm text-stone-600 dark:text-stone-400">Conflicts, holiday and the 11-hour rest rule are checked as you drop. Red outline means it will not save.</p>
        </div>
        <figure class="px-6 pb-0">
          <img src="/img/rota-week-view.webp" width="1200" height="720" alt="Week view: seven columns of shifts, Tuesday evening highlighted with a red outline and the note 'Priya: under 11h rest'"
               class="w-full rounded-t-md border border-b-0 border-stone-300 dark:border-stone-700" loading="lazy">
        </figure>
      </li>

      <!-- Stat tile -->
      <li class="flex flex-col justify-between rounded-lg border border-stone-300 bg-stone-50 p-6 lg:col-span-2 dark:border-stone-700 dark:bg-stone-900">
        <p class="text-sm text-stone-600 dark:text-stone-400">Average time to publish a week's rota</p>
        <p class="mt-4 text-5xl font-semibold tracking-tight tabular-nums text-stone-900 dark:text-stone-100">9<span class="text-2xl text-stone-500"> min</span></p>
        <p class="mt-2 font-mono text-xs text-stone-500">Median across 312 cafes, Q3 2025</p>
      </li>

      <!-- Text tile -->
      <li class="rounded-lg border border-stone-300 bg-white p-6 lg:col-span-2 dark:border-stone-700 dark:bg-stone-950">
        <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Staff swap shifts themselves</h3>
        <p class="mt-1 text-sm text-stone-600 dark:text-stone-400">A swap request goes to everyone qualified for the station. First accept wins; you only see the result.</p>
      </li>

      <!-- Wide tile with a small image -->
      <li class="grid gap-4 rounded-lg border border-stone-300 bg-white p-6 sm:col-span-2 sm:grid-cols-[1fr_auto] lg:col-span-3 dark:border-stone-700 dark:bg-stone-950">
        <div>
          <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Payroll export that matches the timesheet</h3>
          <p class="mt-1 text-sm text-stone-600 dark:text-stone-400">CSV for Xero and BrightPay with breaks deducted and bank-holiday rates applied.</p>
        </div>
        <img src="/img/rota-export.webp" width="240" height="160" alt="" class="h-24 w-auto self-end rounded border border-stone-300 dark:border-stone-700" loading="lazy">
      </li>

      <!-- Quote tile -->
      <li class="rounded-lg border border-stone-300 bg-white p-6 lg:col-span-3 dark:border-stone-700 dark:bg-stone-950">
        <blockquote class="text-sm leading-relaxed text-stone-700 dark:text-stone-300">
          "I used to do the rota on a Sunday with a spreadsheet and a bottle of wine. Now it is nine minutes and no wine."
        </blockquote>
        <p class="mt-3 font-mono text-xs text-stone-500">Hannah Okafor, owner, Two Cups, Stokes Croft</p>
      </li>
    </ul>
  </div>
</section>
```

Why these choices:

- Six columns at `lg:` divide into 4+2, 3+3 and 2+2+2, so tiles can be a third, a half or two-thirds wide without fractional spans.
- `auto-rows-[minmax(10rem,auto)]` gives every row a floor height so stat tiles do not collapse, while text-heavy tiles can still grow.
- `grid-flow-dense` lets a later small tile back-fill a hole left by the hero's `row-span-2`; without it the grid leaves empty cells.
- DOM order is reading order on phones: hero, the headline number, then supporting points. Spans only change the desktop arrangement; nothing is reordered with `order-*`.
- Tiles are `<li>` in a `<ul role="list">` because they are a set of parallel features; the hero tile carries a `<figure>` for its screenshot.
- Hairline borders and two surface tints (white, stone-50) instead of shadows, glass or gradients; the hierarchy comes from size and content, not decoration.

## Variations

- **Dark**: `bg-stone-950` section, tiles `bg-stone-900 border-stone-800`, the stat tile `bg-stone-800`. Keep the screenshot bright; it is the only thing allowed to glow.
- **Compact 4-column**: `lg:grid-cols-4` with the hero at `lg:col-span-2 lg:row-span-2` and four single tiles. Works for exactly five features.
- **Edge-to-edge image tiles**: drop `p-6` on an image tile and let the `<img>` fill with `h-full w-full object-cover`; add `aspect-video` on phones so it has a height before the image loads.
- **Interactive tile**: a tile that is a link gets `<a class="block h-full">` wrapping its content and `hover:border-stone-900 focus-visible:outline-2` on the link, not on the `<li>`.

## Pitfalls

- Tiles collapsing to a strange order on phones is the most common bento bug: a `row-span-2` hero placed last in the DOM so it "fits" on desktop ends up at the bottom on mobile. Put tiles in reading order and let `grid-flow-dense` do the fitting.
- The hero screenshot without `width`/`height` shifts every tile below it when it loads. Always set both, and give edge-to-edge image tiles an `aspect-*` placeholder.
- `row-span-2` with `auto-rows-auto` (no min height) makes the hero as tall as two text tiles, which is often shorter than its image; set a `minmax` floor or `min-h-` on the hero.
- Seven tiles in a six-column grid leave a gap no matter what; count spans so each row totals six, or let the last tile span the remainder.
- A bento of six tiles with icon-in-coloured-square headers is the three-card template with extra steps. Each tile should hold a different kind of content: an image, a number, a quote, a sentence.
- Rounded `rounded-2xl` plus `shadow-lg` on every tile is the AI tell; `rounded-lg` and a hairline are enough. See `web-craft-anti-generic-design`.

## Related skills

- `web-layout-feature-grid`
- `web-css-responsive-grid`
- `web-design-images`
- `web-perf-images`
- `web-craft-layout-with-intention`
- `web-craft-anti-generic-design`
