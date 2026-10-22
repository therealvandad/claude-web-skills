---
name: web-data-chart-accessibility
description: Make SVG charts accessible: role="img" with a generated title and text summary, a visible "show as table" toggle, direct labels, SVG patterns and shapes so series never rely on colour alone, and colour-blind-safe categorical and sequential scales. Use whenever a user asks for an "accessible chart", "screen reader chart", "colour blind safe colours", "chart alt text", or "data table fallback".
---

# Chart accessibility

A chart is a picture of numbers, so it fails three groups at once: screen reader users get nothing, keyboard users cannot reach tooltips, and about 1 in 12 men cannot tell the red series from the green one. The fix is layered: say the takeaway in words, offer the exact numbers as a real table, and encode each series twice (colour plus pattern, shape or a direct label). Done this way, the chart also gets better for everyone, because a sentence summary and direct labels are faster to read than a legend.

## Pattern

```html
<figure class="mx-auto max-w-3xl px-4" aria-labelledby="sig-t">
  <h2 id="sig-t" class="text-lg font-semibold">Sign-ups by channel, Q3 2026</h2>
  <p id="sig-sum" class="mt-1 text-sm text-gray-600 dark:text-gray-400"><!-- generated summary --></p>
  <div id="sig-chart" class="mt-4"></div>
  <details class="mt-3 text-sm">
    <summary class="cursor-pointer rounded underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2">Show as table</summary>
    <div id="sig-table" class="mt-2 overflow-x-auto"></div>
  </details>
</figure>
```

```css
@theme {
  /* Okabe-Ito: distinguishable with protanopia, deuteranopia and tritanopia */
  --color-series-1: #0072b2;  /* blue */
  --color-series-2: #e69f00;  /* orange */
  --color-series-3: #009e73;  /* bluish green */
  --color-series-4: #cc79a7;  /* reddish purple */
}
```

```js
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const pct = new Intl.NumberFormat(undefined, { style: 'percent' });
const fills = ['fill-series-1', 'fill-series-2', 'fill-series-3', 'fill-series-4']; // full names so Tailwind finds them
const patterns = [
  '', // solid
  '<path d="M0 6 L6 0" stroke="white" stroke-width="1.5"/>',            // diagonal
  '<circle cx="3" cy="3" r="1.3" fill="white"/>',                        // dots
  '<path d="M0 3 H6" stroke="white" stroke-width="1.5"/>',               // horizontal
];

function summarise(data, unit) {
  const sorted = [...data].sort((a, b) => b.value - a.value), total = data.reduce((s, d) => s + d.value, 0);
  const [top, second] = sorted, last = sorted.at(-1);
  return `${data.length} channels, ${total.toLocaleString()} ${unit} in total. ${top.label} leads with ${pct.format(top.value / total)}, ` +
    `${(top.value / second.value).toFixed(1)} times ${second.label}. ${last.label} is smallest at ${pct.format(last.value / total)}.`;
}

function accessibleBars(id, data, { unit }) {
  const W = 600, row = 44, H = data.length * row, max = Math.max(...data.map((d) => d.value)), lx = 130;
  const defs = patterns.map((p, i) => `<pattern id="${id}-p${i}" width="6" height="6" patternUnits="userSpaceOnUse">
      <rect width="6" height="6" class="${fills[i]}"/>${p}</pattern>`).join('');
  const bars = data.map((d, i) => {
    const w = ((W - lx - 70) * d.value) / max, y = i * row + 8;
    return `<text x="${lx - 8}" y="${y + 14}" text-anchor="end" class="fill-current text-[13px]">${esc(d.label)}</text>
      <rect x="${lx}" y="${y}" width="${w}" height="28" fill="url(#${id}-p${i % 4})" class="stroke-gray-900 dark:stroke-white" stroke-width="1"/>
      <text x="${lx + w + 6}" y="${y + 14}" dominant-baseline="middle" class="fill-current text-[13px]">${d.value.toLocaleString()}</text>`;
  }).join('');
  document.getElementById(`${id}-chart`).innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${id}-t ${id}-sum" class="h-auto w-full tabular-nums">
      <defs>${defs}</defs>${bars}</svg>`;
  document.getElementById(`${id}-sum`).textContent = summarise(data, unit);
  document.getElementById(`${id}-table`).innerHTML = `<table class="w-full text-left">
    <thead><tr><th scope="col" class="py-1 pr-4">Channel</th><th scope="col" class="py-1 text-right">${esc(unit)}</th></tr></thead>
    <tbody>${data.map((d) => `<tr class="border-t border-gray-200 dark:border-gray-800"><th scope="row" class="py-1 pr-4 font-normal">${esc(d.label)}</th><td class="py-1 text-right">${d.value.toLocaleString()}</td></tr>`).join('')}</tbody></table>`;
}

accessibleBars('sig', [
  { label: 'Organic search', value: 4182 }, { label: 'Referral', value: 1927 },
  { label: 'Newsletter', value: 1364 }, { label: 'Paid social', value: 611 },
], { unit: 'sign-ups' });
```

Why this shape: the summary is computed from the data, so it never goes stale, and the SVG points `aria-labelledby` at the heading and summary instead of duplicating them. Each bar carries a direct label and value, so the legend disappears entirely; the pattern and outline are the second encoding for anyone who cannot separate the fills. The table sits in `<details>`, visible to everyone who wants exact numbers, not hidden behind `sr-only`.

## Variations

- **Line charts**: vary `stroke-dasharray` (`none`, `6 3`, `2 3`) and the point marker (circle, square, triangle) per series, and label each line at its last point instead of using a legend.
- **Sequential scale** (heatmaps, choropleths): one hue stepping in lightness, e.g. `oklch(95% 0.03 250)` to `oklch(35% 0.12 250)` in five steps, or viridis. Never a red-to-green ramp; for diverging data use blue to orange (`#2166ac` / `#f7f7f7` / `#b35806`).
- **Keyboard-explorable points**: give each mark `tabindex="0"` and an `aria-label` like "March: 2,140", plus a visible `focus-visible:` outline. Only do this for small charts; 365 tab stops is a trap, use the table instead.
- **Test it**: Chrome DevTools > Rendering > "Emulate vision deficiencies", and run the page through a screen reader to hear the summary once.

## Pitfalls

- `role="img"` hides every child from assistive tech, so text inside the SVG is not read. The accessible name and summary must carry the meaning.
- A legend that matches colour swatches to names fails WCAG 1.4.1 on its own. Direct labels, patterns or shapes are the fix, not a better palette alone.
- Adjacent fills need 3:1 contrast against the background (WCAG 1.4.11) or an outline; Okabe-Ito yellow `#f0e442` fails on white, so it is left out above.
- Alt text that says "bar chart of sign-ups" describes the picture, not the data. State the comparison or trend the chart exists to show.
- A `sr-only` table is invisible to sighted keyboard and low-vision users who also want the numbers. Prefer a visible toggle.
- Animated chart entrances must respect `prefers-reduced-motion`; wrap them in `motion-safe:`.

## Related skills

- `web-data-svg-bar-chart`
- `web-data-svg-line-chart`
- `web-data-heatmap-calendar`
- `web-a11y-color-contrast`
- `web-a11y-images-and-media`
- `web-a11y-aria-patterns`
