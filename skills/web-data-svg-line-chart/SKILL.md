---
name: web-data-svg-line-chart
description: Generate a line or area chart as inline SVG from a JS array, with axes, gridlines, a hover and keyboard tooltip, theme colours and a hidden data table, no chart library, in Tailwind v4. Use whenever a user asks for a "line chart", "line graph", "trend over time", "area chart", "sign-ups per week", or "a graph with tooltips".
---

# SVG line chart

A line chart is one `<path>` whose `d` is built from the data, plus gridlines and labels placed with the same two scale functions. The hard part is the tooltip: a hover-only tooltip excludes keyboard and touch users, so this one is driven by a nearest-point lookup on `pointermove` and by arrow keys when the SVG is focused, and the text goes into a `role="status"` element so it is announced. Everything else is the bar-chart recipe with a different mark.

## Pattern

```html
<figure class="relative mx-auto max-w-3xl px-4 text-gray-700 dark:text-gray-300">
  <figcaption>
    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">New sign-ups per week</h2>
    <p class="text-sm text-gray-500">Last 12 weeks. Hover, tap or focus the chart and use arrow keys.</p>
  </figcaption>
  <div id="signups" class="relative mt-4"></div>
</figure>
```

```css
@theme { --color-chart-1: oklch(50% 0.15 250); --color-chart-grid: oklch(88% 0 0); }
@layer base { @media (prefers-color-scheme: dark) { :root { --color-chart-1: oklch(72% 0.13 250); --color-chart-grid: oklch(30% 0 0); } } }
```

```js
const num = new Intl.NumberFormat('en-GB');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function niceScale(max, ticks = 4) {
  const raw = max / ticks, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * mag >= raw) * mag;
  return { step, top: Math.ceil(max / step) * step };
}

function lineChart(host, data, { title, valueLabel, area = true }) {
  const W = 640, H = 300, m = { top: 12, right: 16, bottom: 32, left: 44 };
  const iw = W - m.left - m.right, ih = H - m.top - m.bottom, n = data.length;
  const { step, top } = niceScale(Math.max(...data.map((d) => d.value)));
  const x = (i) => m.left + (i / (n - 1)) * iw;
  const y = (v) => m.top + ih - (v / top) * ih;
  const line = 'M' + data.map((d, i) => `${x(i)},${y(d.value)}`).join('L');
  const ticks = Array.from({ length: Math.round(top / step) + 1 }, (_, i) => i * step);
  const every = Math.ceil(n / 6);                       // at most ~6 x labels
  const first = data[0].value, last = data[n - 1].value;
  const change = new Intl.NumberFormat('en-GB', { style: 'percent', signDisplay: 'exceptZero', maximumFractionDigits: 0 }).format((last - first) / first);
  const id = host.id;

  host.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" tabindex="0" aria-labelledby="${id}-t ${id}-d" aria-describedby="${id}-tip"
         class="h-auto w-full tabular-nums rounded-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-chart-1">
      <title id="${id}-t">${esc(title)}</title>
      <desc id="${id}-d">${n} points from ${esc(data[0].label)} to ${esc(data[n - 1].label)}. Started at ${num.format(first)}, ended at ${num.format(last)}, ${change} overall.</desc>
      ${ticks.map((t) => `<line x1="${m.left}" x2="${W - m.right}" y1="${y(t)}" y2="${y(t)}" class="stroke-chart-grid" />
        <text x="${m.left - 8}" y="${y(t)}" text-anchor="end" dominant-baseline="middle" class="fill-current text-[11px]">${num.format(t)}</text>`).join('')}
      ${data.map((d, i) => i % every ? '' : `<text x="${x(i)}" y="${H - 8}" text-anchor="middle" class="fill-current text-[11px]">${esc(d.label)}</text>`).join('')}
      ${area ? `<path d="${line}L${x(n - 1)},${y(0)}L${x(0)},${y(0)}Z" class="fill-chart-1/15" />` : ''}
      <path d="${line}" fill="none" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" class="stroke-chart-1" />
      <g data-cursor hidden>
        <line y1="${m.top}" y2="${m.top + ih}" class="stroke-current" stroke-dasharray="3 3" />
        <circle r="5" class="fill-chart-1 stroke-white dark:stroke-gray-950" stroke-width="2" />
      </g>
    </svg>
    <output id="${id}-tip" role="status" hidden
      class="pointer-events-none absolute -translate-x-1/2 -translate-y-full rounded-md bg-gray-900 px-2 py-1 text-xs text-white shadow dark:bg-gray-100 dark:text-gray-900"></output>
    <table class="sr-only"><caption>${esc(title)}</caption>
      <thead><tr><th scope="col">Period</th><th scope="col">${esc(valueLabel)}</th></tr></thead>
      <tbody>${data.map((d) => `<tr><th scope="row">${esc(d.label)}</th><td>${num.format(d.value)}</td></tr>`).join('')}</tbody></table>`;

  const svg = host.querySelector('svg'), cursor = svg.querySelector('[data-cursor]'), tip = host.querySelector('output');
  let active = -1;
  const show = (i) => {
    active = Math.max(0, Math.min(n - 1, i));
    const d = data[active];
    cursor.hidden = tip.hidden = false;
    cursor.querySelector('line').setAttribute('x1', x(active)); cursor.querySelector('line').setAttribute('x2', x(active));
    cursor.querySelector('circle').setAttribute('cx', x(active)); cursor.querySelector('circle').setAttribute('cy', y(d.value));
    tip.textContent = `${d.label}: ${num.format(d.value)}`;
    tip.style.left = `${(x(active) / W) * 100}%`; tip.style.top = `calc(${(y(d.value) / H) * 100}% - 10px)`;
  };
  const hide = () => { cursor.hidden = tip.hidden = true; };
  svg.addEventListener('pointermove', (e) => {
    const r = svg.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    show(Math.round(((px - m.left) / iw) * (n - 1)));
  });
  svg.addEventListener('pointerleave', hide);
  svg.addEventListener('focus', () => show(n - 1));
  svg.addEventListener('blur', hide);
  svg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') show(active + 1); else if (e.key === 'ArrowLeft') show(active - 1);
    else if (e.key === 'Home') show(0); else if (e.key === 'End') show(n - 1); else return;
    e.preventDefault();
  });
}

lineChart(document.getElementById('signups'), [
  { label: 'W29', value: 142 }, { label: 'W30', value: 158 }, { label: 'W31', value: 131 }, { label: 'W32', value: 176 },
  { label: 'W33', value: 190 }, { label: 'W34', value: 168 }, { label: 'W35', value: 204 }, { label: 'W36', value: 221 },
  { label: 'W37', value: 197 }, { label: 'W38', value: 236 }, { label: 'W39', value: 251 }, { label: 'W40', value: 243 },
], { title: 'New sign-ups per week, weeks 29 to 40 of 2026', valueLabel: 'Sign-ups' });
```

Why this shape: `vector-effect="non-scaling-stroke"` keeps the line 2.5 px thick at every width instead of thinning on phones. The tooltip is an HTML `<output>` positioned in percentages of the SVG box, so it is not clipped by the `viewBox` and can use normal Tailwind classes; `role="status"` makes arrow-key moves audible. The `<desc>` tells the story (start, end, percentage change) and the table carries the values.

## Variations

- **Two series**: pass `series: [{ name, data }]`, draw one `<path>` each with `stroke-chart-1` and `stroke-chart-2`, give the second `stroke-dasharray="6 4"` so they differ without colour, and add a `<ul>` legend with the same dash drawn in a tiny inline SVG.
- **Smooth curve**: replace the `L` joins with cubic segments (`C` using the midpoint between neighbours as control points). Only for continuous quantities such as temperature; sign-ups per week are discrete, keep them straight.
- **Temperature with negatives**: compute `min` as well and let `y` map `[min, top]`; draw the zero gridline with `stroke-current` so it stands out.
- **No area**: `area: false` for charts with several series; overlapping translucent fills are unreadable.

## Pitfalls

- `x(i)` divides by `n - 1`; a single data point divides by zero. Guard `n < 2` and show the value as text instead.
- Positioning the tooltip inside the SVG with `<foreignObject>` breaks in Safari in several ways; keep it as an HTML sibling in a `relative` wrapper.
- `tabindex="0"` on an `<svg>` is focusable in all current browsers, but it must have a visible focus ring; `outline` on SVG works in Chromium and Firefox, Safari needs the ring on the wrapper (`focus-within:ring-2` on the host).
- Do not fire `role="status"` updates on every `pointermove` pixel; `show()` only changes text when the index changes, which is why it rounds to the nearest point first.
- A y-axis that does not start at zero is acceptable for temperatures and stock prices, misleading for counts. Default to zero and opt out deliberately.
- Twelve x labels at 640 wide overlap at 375 px; the `every` divisor caps labels at six. For dates, use `Intl.DateTimeFormat` with `{ month: 'short' }` and label only month boundaries.

## Related skills

- `web-data-svg-bar-chart`
- `web-data-sparklines`
- `web-data-chart-accessibility`
- `web-data-number-formatting`
- `web-ui-tooltip-and-popover`
- `web-a11y-keyboard-and-focus`
