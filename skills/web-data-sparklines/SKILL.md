---
name: web-data-sparklines
description: Render tiny inline SVG sparklines (line or bar) inside table cells, KPI tiles and sentences, generated from a data-sparkline attribute by a few lines of JS, with the trend stated in text for screen readers. Use whenever a user asks for a "sparkline", "mini chart", "tiny graph in a table", "trend line next to a number", or "8-week trend column".
---

# Sparklines

A sparkline is a word-sized graphic: no axes, no labels, one hue, read in the context of the number beside it. Generating them from a `data-sparkline="142,158,131"` attribute keeps the markup declarative, so a server template or a CMS can emit the numbers and one script draws every sparkline on the page. The graphic is `aria-hidden`; the accessible version is the number and a short trend sentence that are already in the cell.

## Pattern

```html
<table class="w-full text-sm">
  <caption class="sr-only">Weekly units sold per product, last 8 weeks</caption>
  <thead class="text-left text-xs uppercase tracking-wide text-gray-500">
    <tr><th scope="col" class="py-2">Product</th><th scope="col" class="py-2 text-right">This week</th><th scope="col" class="py-2 pl-6">8-week trend</th></tr>
  </thead>
  <tbody class="divide-y divide-gray-200 dark:divide-gray-800">
    <tr>
      <th scope="row" class="py-2 font-medium">Oak side table</th>
      <td class="py-2 text-right tabular-nums">38</td>
      <td class="py-2 pl-6"><span data-sparkline="29,31,27,34,33,36,35,38" data-sparkline-label="units per week"></span></td>
    </tr>
    <tr>
      <th scope="row" class="py-2 font-medium">Walnut shelf, 90 cm</th>
      <td class="py-2 text-right tabular-nums">12</td>
      <td class="py-2 pl-6"><span data-sparkline="21,19,18,17,15,14,13,12" data-sparkline-type="bar" data-sparkline-label="units per week"></span></td>
    </tr>
  </tbody>
</table>
```

```css
@theme { --color-chart-1: oklch(50% 0.15 250); }
@layer base { @media (prefers-color-scheme: dark) { :root { --color-chart-1: oklch(72% 0.13 250); } } }
```

```js
const pct = new Intl.NumberFormat('en-GB', { style: 'percent', signDisplay: 'exceptZero', maximumFractionDigits: 0 });

function sparkline(el) {
  const values = el.dataset.sparkline.split(',').map(Number).filter(Number.isFinite);
  if (values.length < 2) return;
  const W = 96, H = 24, P = 3;                       // 4:1 box; keep the rendered size the same ratio
  const min = Math.min(...values), max = Math.max(...values), span = max - min || 1;
  const x = (i) => P + (i / (values.length - 1)) * (W - 2 * P);
  const y = (v) => H - P - ((v - min) / span) * (H - 2 * P);
  const last = values.at(-1), first = values[0];
  const trend = pct.format((last - first) / (first || 1));
  const label = el.dataset.sparklineLabel ?? '';
  let marks;
  if (el.dataset.sparklineType === 'bar') {
    const bw = (W - 2 * P) / values.length - 1;
    marks = values.map((v, i) => `<rect x="${P + i * (bw + 1)}" y="${y(v)}" width="${bw}" height="${H - P - y(v)}" class="fill-chart-1" />`).join('');
  } else {
    const d = 'M' + values.map((v, i) => `${x(i)},${y(v)}`).join('L');
    marks = `<path d="${d}" fill="none" stroke-width="1.5" stroke-linejoin="round" vector-effect="non-scaling-stroke" class="stroke-chart-1" />
             <circle cx="${x(values.length - 1)}" cy="${y(last)}" r="2" class="fill-chart-1" />`;
  }
  el.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" aria-hidden="true" focusable="false" class="inline-block h-6 w-24 align-middle">${marks}</svg>
    <span class="sr-only">${values.length} weeks of ${label}: ${values.join(', ')}. ${trend} from first to last.</span>`;
  el.title = `${values.join(', ')} (${trend})`;
}

document.querySelectorAll('[data-sparkline]').forEach(sparkline);
```

Why this shape: the `viewBox` is 96 by 24 and the rendered box is `w-24 h-6`, the same 4:1 ratio, so circles stay round without `preserveAspectRatio="none"`. The y-scale runs from the data minimum to maximum, which is what a sparkline is for: shape, not magnitude; the magnitude is the number in the next cell. The `sr-only` span states the values and the first-to-last change so a screen reader user gets the same information in the same place.

## Variations

- **In a KPI tile**: put the sparkline under the figure, `w-full h-8` with `viewBox="0 0 128 32"` and `preserveAspectRatio="none"` on a bar type only (bars survive stretching, circles and strokes do not).
- **Reference band**: draw a `<rect>` from the 25th to 75th percentile in `fill-chart-1/10` behind the line so the reader sees whether the latest point is unusual.
- **Inline in a sentence**: `<span data-sparkline="...">` inside a `<p>`; `align-middle` keeps it on the text baseline. Say the number in words next to it: "38 this week".
- **Win/loss**: bars of fixed height, `y` above or below a centre line; use `fill-chart-1` for positive and `fill-chart-1/40` for negative, same hue.

## Pitfalls

- Colouring sparklines green for up and red for down encodes meaning in colour alone and is wrong for metrics where down is good (churn, defects). One hue; the trend sentence carries the sign.
- Without `vector-effect="non-scaling-stroke"`, a `w-full` sparkline stretches the stroke into a blob on wide tiles.
- A flat series has `span === 0`; the `|| 1` guard keeps the line in the middle instead of producing `NaN` coordinates.
- Eight numbers in a `title` attribute is a passable hover hint, not an accessible name; keep `aria-hidden` on the SVG and the real text in the `sr-only` span.
- Sparklines in a `<td>` must share the same `viewBox` and width so shapes are comparable down the column; do not let one row's longer series produce a wider graphic.
- Rendering 500 sparklines with `innerHTML` in a loop is fine (sub-10 ms), but recalculating them on every table sort is not; render once, the SVG moves with the row.

## Related skills

- `web-data-svg-line-chart`
- `web-data-kpi-dashboard`
- `web-ui-data-table`
- `web-section-stats-band`
- `web-data-chart-accessibility`
