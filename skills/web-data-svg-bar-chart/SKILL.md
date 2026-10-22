---
name: web-data-svg-bar-chart
description: Generate a responsive inline SVG bar chart from a JS data array (no chart library) with a viewBox, nice axis ticks, labels, theme colours from CSS variables and a hidden data table for screen readers. Use whenever a user asks for a "bar chart", "column chart", "graph of monthly numbers", "revenue per month", or "chart without a library".
---

# SVG bar chart

A bar chart is forty lines of JavaScript that turn an array into `<rect>` and `<text>` elements inside a `viewBox`. No library means no 200 kB bundle, no canvas that screen readers cannot read, and colours that follow your theme because they are Tailwind `fill-*` classes. The chart scales with its container; the data also lives in a visually hidden `<table>` so assistive tech reads the real numbers, not a picture of them.

## Pattern

```html
<figure class="mx-auto max-w-3xl px-4 text-gray-700 dark:text-gray-300">
  <figcaption class="flex flex-wrap items-baseline justify-between gap-2">
    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Revenue, 2025</h2>
    <p class="text-sm text-gray-500">Monthly, EUR, excluding VAT</p>
  </figcaption>
  <div id="revenue" class="mt-4"></div>
</figure>
```

```css
@theme {
  --color-chart-1: oklch(50% 0.15 250);   /* one hue for a single series */
  --color-chart-grid: oklch(88% 0 0);
}
@layer base {
  @media (prefers-color-scheme: dark) {
    :root { --color-chart-1: oklch(72% 0.13 250); --color-chart-grid: oklch(30% 0 0); }
  }
}
```

```js
const money = new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR' });
const compact = new Intl.NumberFormat('en-IE', { notation: 'compact', maximumFractionDigits: 0 });
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function niceScale(max, ticks = 4) {
  const raw = max / ticks, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * mag >= raw) * mag;
  return { step, top: Math.ceil(max / step) * step };
}

function barChart(host, data, { title, valueLabel, format = money }) {
  const W = 640, H = 320, m = { top: 12, right: 8, bottom: 36, left: 52 };
  const iw = W - m.left - m.right, ih = H - m.top - m.bottom;
  const { step, top } = niceScale(Math.max(...data.map((d) => d.value)));
  const slot = iw / data.length, bw = slot * 0.68, pad = (slot - bw) / 2;
  const x = (i) => m.left + i * slot + pad;
  const y = (v) => m.top + ih - (v / top) * ih;
  const ticks = Array.from({ length: Math.round(top / step) + 1 }, (_, i) => i * step);
  const hi = data.reduce((a, b) => (b.value > a.value ? b : a));
  const lo = data.reduce((a, b) => (b.value < a.value ? b : a));
  const total = data.reduce((s, d) => s + d.value, 0);
  const id = host.id;

  const grid = ticks.map((t) => `
    <line x1="${m.left}" x2="${W - m.right}" y1="${y(t)}" y2="${y(t)}" class="stroke-chart-grid" stroke-width="1" />
    <text x="${m.left - 8}" y="${y(t)}" text-anchor="end" dominant-baseline="middle" class="fill-current text-[11px]">${compact.format(t)}</text>`).join('');

  const bars = data.map((d, i) => `
    <rect x="${x(i)}" y="${y(d.value)}" width="${bw}" height="${y(0) - y(d.value)}" rx="2" class="fill-chart-1">
      <title>${esc(d.label)}: ${format.format(d.value)}</title>
    </rect>
    <text x="${x(i) + bw / 2}" y="${H - m.bottom + 18}" text-anchor="middle" class="fill-current text-[11px]">${esc(d.label)}</text>`).join('');

  host.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${id}-t ${id}-d" class="h-auto w-full tabular-nums">
      <title id="${id}-t">${esc(title)}</title>
      <desc id="${id}-d">${data.length} bars. Highest: ${esc(hi.label)} at ${format.format(hi.value)}. Lowest: ${esc(lo.label)} at ${format.format(lo.value)}. Total ${format.format(total)}.</desc>
      ${grid}${bars}
    </svg>
    <table class="sr-only">
      <caption>${esc(title)}</caption>
      <thead><tr><th scope="col">Period</th><th scope="col">${esc(valueLabel)}</th></tr></thead>
      <tbody>${data.map((d) => `<tr><th scope="row">${esc(d.label)}</th><td>${format.format(d.value)}</td></tr>`).join('')}</tbody>
    </table>`;
}

barChart(document.getElementById('revenue'), [
  { label: 'Jan', value: 18420.5 }, { label: 'Feb', value: 16980.0 }, { label: 'Mar', value: 21340.75 },
  { label: 'Apr', value: 19875.2 }, { label: 'May', value: 23410.0 }, { label: 'Jun', value: 25102.4 },
  { label: 'Jul', value: 22890.1 }, { label: 'Aug', value: 20115.6 }, { label: 'Sep', value: 26740.3 },
  { label: 'Oct', value: 28215.9 }, { label: 'Nov', value: 24560.0 }, { label: 'Dec', value: 31002.45 },
], { title: 'Monthly revenue 2025 in euro', valueLabel: 'Revenue (EUR)' });
```

Why this shape: the `viewBox` fixes the coordinate system at 640 by 320, so every scale is computed once and the browser handles resizing. `niceScale` rounds the axis top to 1, 2, 2.5 or 5 times a power of ten, so ticks read "10K, 20K, 30K" instead of "7,750". Colours are `fill-chart-1` and `stroke-chart-grid`, which Tailwind generates from the `@theme` tokens, so dark mode is a variable swap and not a rerender. The `<desc>` is generated from the data: it says what a sighted user would take from the chart in one glance, and the `<table>` gives the exact values.

## Variations

- **Horizontal bars** (long category names): swap the axes, `x` becomes the value scale and `y` the band scale, and put labels left of each bar with `text-anchor="end"`. Height grows with `data.length * 28`.
- **Grouped bars** (two series): divide each slot into `series.length` sub-bars and use `fill-chart-1`, `fill-chart-2` from a colour-blind-safe set (see `web-data-chart-accessibility`); add a `<ul>` legend above the chart, never only a colour key inside the SVG.
- **Value labels on bars**: add `<text x="${x(i) + bw / 2}" y="${y(d.value) - 6}" text-anchor="middle">` with `compact.format`; drop the y-axis ticks when you do, one or the other.
- **Highlight the current period**: give the last bar `fill-chart-1` and the rest `fill-chart-1/50`. One hue, two opacities, no second colour.

## Pitfalls

- `fill="var(--color-chart-1)"` as a presentation attribute is not reliably supported; use a class (`fill-chart-1`) or `style="fill: var(--color-chart-1)"`.
- SVG `<text>` scales with the `viewBox`, so 11 px labels at 640 wide are 6 px on a 375 px phone. Either keep the chart at least 320 px wide inside a scroll container, or render every second label when `host.clientWidth < 480` and recompute in a `ResizeObserver`.
- Interpolating labels from an API into `innerHTML` without escaping is an XSS hole; the `esc` helper is not optional.
- A `<title>` on each `<rect>` gives a native hover tooltip only; it is not keyboard reachable. The hidden table is the accessible path, the tooltip is a bonus.
- Starting bars at a non-zero baseline exaggerates differences. The y-scale always starts at 0 here; if you truncate, say so in the caption.
- Animating bars from height 0 on load causes layout jank and ignores reduced motion. If you must, animate `transform: scaleY()` under `motion-safe:` with `transform-origin: bottom`, never `height`.

## Related skills

- `web-data-svg-line-chart`
- `web-data-chart-accessibility`
- `web-data-number-formatting`
- `web-ui-data-table`
- `web-section-stats-band`
- `web-design-color-system`
