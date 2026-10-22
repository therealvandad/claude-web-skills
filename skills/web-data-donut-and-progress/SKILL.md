---
name: web-data-donut-and-progress
description: Build donut charts and progress rings as inline SVG with stroke-dasharray and pathLength, a colour-blind-safe segment palette, a legend list with real values, a centre figure, and a motion-safe draw-in animation, in Tailwind v4. Use whenever a user asks for a "donut chart", "pie chart", "progress ring", "circular progress", "percentage circle", "share by category", or "storage used ring".
---

# Donut and progress rings

A donut is a stroked circle whose dash pattern covers part of the circumference. With `pathLength="100"` the maths disappears: a segment of 37 % is `stroke-dasharray="37 63"` offset by the segments before it. A progress ring is a donut with one segment. Both need the number written next to them, because people cannot read angles to better than about 10 %, and the legend must be a real list with values, not a colour key.

## Pattern

```html
<figure class="mx-auto flex max-w-xl flex-col items-center gap-6 px-4 sm:flex-row sm:items-start">
  <div id="channels" class="relative size-44 shrink-0"></div>
  <figcaption class="w-full">
    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Revenue by channel, Q3 2026</h2>
    <ul id="channels-legend" class="mt-3 divide-y divide-gray-200 text-sm dark:divide-gray-800"></ul>
  </figcaption>
</figure>

<!-- Progress ring: value lives in the markup, JS only sets the arc -->
<div class="inline-flex items-center gap-3">
  <svg viewBox="0 0 36 36" class="size-12 -rotate-90" aria-hidden="true">
    <circle cx="18" cy="18" r="15.5" fill="none" stroke-width="3" class="stroke-gray-200 dark:stroke-gray-800" />
    <circle cx="18" cy="18" r="15.5" fill="none" stroke-width="3" stroke-linecap="round" pathLength="100"
      class="stroke-chart-1 motion-safe:transition-[stroke-dasharray] motion-safe:duration-700"
      data-ring="68" stroke-dasharray="0 100" />
  </svg>
  <p class="text-sm"><span class="font-semibold tabular-nums">68 %</span> of 512 GB used</p>
</div>
```

```css
@theme {
  --color-chart-1: #0072b2; --color-chart-2: #e69f00; --color-chart-3: #009e73; --color-chart-4: #cc79a7; /* Okabe-Ito */
}
```

```js
const money = new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
const pct = new Intl.NumberFormat('en-IE', { style: 'percent', maximumFractionDigits: 0 });
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function donut(host, legend, data, { title, centreLabel }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  let offset = 0;
  const arcs = data.map((d, i) => {
    const share = (d.value / total) * 100;
    const arc = `<circle cx="18" cy="18" r="15.5" fill="none" stroke-width="4" pathLength="100"
      stroke-dasharray="${share} ${100 - share}" stroke-dashoffset="${-offset}" class="stroke-chart-${i + 1}">
      <title>${esc(d.label)}: ${money.format(d.value)} (${pct.format(d.value / total)})</title></circle>`;
    offset += share;
    return arc;
  }).join('');
  host.innerHTML = `
    <svg viewBox="0 0 36 36" role="img" aria-labelledby="${host.id}-t ${host.id}-d" class="size-full -rotate-90">
      <title id="${host.id}-t">${esc(title)}</title>
      <desc id="${host.id}-d">${data.map((d) => `${esc(d.label)} ${pct.format(d.value / total)}`).join(', ')}. Total ${money.format(total)}.</desc>
      ${arcs}
    </svg>
    <p class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
      <span class="text-xl font-semibold tabular-nums text-gray-900 dark:text-gray-100">${money.format(total)}</span>
      <span class="text-xs text-gray-500">${esc(centreLabel)}</span>
    </p>`;
  legend.innerHTML = data.map((d, i) => `
    <li class="flex items-center gap-3 py-2">
      <span aria-hidden="true" class="size-3 rounded-sm bg-chart-${i + 1}"></span>
      <span class="flex-1">${esc(d.label)}</span>
      <span class="tabular-nums text-gray-500">${pct.format(d.value / total)}</span>
      <span class="w-24 text-right tabular-nums font-medium">${money.format(d.value)}</span>
    </li>`).join('');
}

donut(document.getElementById('channels'), document.getElementById('channels-legend'), [
  { label: 'Direct', value: 48212.4 }, { label: 'Marketplace', value: 31905.15 },
  { label: 'Wholesale', value: 22470 }, { label: 'Other', value: 6118.9 },
], { title: 'Revenue by sales channel, third quarter 2026', centreLabel: 'Q3 total' });

// Progress rings: set the arc after first paint so the motion-safe transition draws it in
requestAnimationFrame(() => document.querySelectorAll('[data-ring]').forEach((c) => {
  c.setAttribute('stroke-dasharray', `${c.dataset.ring} ${100 - c.dataset.ring}`);
}));
```

Why this shape: `pathLength="100"` normalises the circumference so dasharray values are percentages, independent of radius. `-rotate-90` starts the first segment at twelve o'clock. Segment classes `stroke-chart-1..4` and legend swatches `bg-chart-1..4` come from the same tokens, so chart and legend can never disagree. The donut's `<desc>` lists every share; the legend `<ul>` is visible, so no hidden table is needed here. The progress ring is `aria-hidden` because the sentence beside it already says "68 % of 512 GB used".

## Variations

- **Live progress** (upload, quota that changes): put `role="progressbar" aria-valuenow="68" aria-valuemin="0" aria-valuemax="100" aria-label="Upload"` on the wrapper and update both `aria-valuenow` and the dasharray; see `web-motion-loading-and-progress`.
- **Semi-circle gauge**: `pathLength="200"`, dasharray `"${value} 200"`, and rotate by `-180deg` on a `viewBox` cropped to the top half (`0 0 36 20`).
- **Thin ring with gaps**: subtract `1` from each `share` in the dasharray and add `stroke-linecap="butt"`; the gaps separate adjacent segments without relying on colour contrast between them.
- **Half-size inline ring** in a table cell: `size-5`, `stroke-width="5"`, no centre text, the percentage in the next cell.

## Pitfalls

- A pie or donut with more than five segments is unreadable; group the tail into "Other" and show the full breakdown in a table.
- Adjacent segments must differ by more than hue: the Okabe-Ito set works for most colour vision deficiencies, but still write the percentage in the legend and in `<desc>`.
- `stroke-linecap="round"` on multi-segment donuts makes caps overlap the next segment; use it only on single-value rings.
- Animating `stroke-dashoffset` from `100` to `0` on load reads as a spinner for the first second; the `motion-safe:transition` here only animates the one change from `0 100` to the real value and does nothing under `prefers-reduced-motion`.
- The centre text is absolutely positioned HTML, not SVG `<text>`, so it scales with the page font and can use `tabular-nums`; keep `pointer-events-none` on it so `<title>` hovers still reach the arcs.
- Percentages from `Math.round` can sum to 99 or 101; show one decimal when any segment is under 5 %, or accept it and do not display a total next to the rounded parts.

## Related skills

- `web-motion-loading-and-progress`
- `web-data-kpi-dashboard`
- `web-data-chart-accessibility`
- `web-data-number-formatting`
- `web-motion-reduced-motion`
- `web-design-color-system`
