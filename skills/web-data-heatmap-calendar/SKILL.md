---
name: web-data-heatmap-calendar
description: Build a contribution-style calendar heatmap as inline SVG from dated counts: 53 weeks of day cells, month and weekday labels, a five-step single-hue colour scale, hover and keyboard tooltips, a legend and a hidden monthly table. Use whenever a user asks for a "heatmap", "contribution graph", "GitHub-style calendar", "activity calendar", "streak chart", or "days with data coloured in".
---

# Calendar heatmap

A calendar heatmap puts a year of daily counts into a grid you can read at a glance: columns are weeks, rows are weekdays, and the colour of each cell is its count on a five-step scale. It is 371 `<rect>`s in one `<svg>`, generated from a `Map` of ISO dates to numbers. The scale is one hue at five lightnesses, which survives every kind of colour-blindness, and the legend plus a monthly totals table give non-visual access without 365 tab stops.

## Pattern

```html
<figure class="mx-auto max-w-4xl px-4 text-gray-700 dark:text-gray-300">
  <figcaption class="flex flex-wrap items-baseline justify-between gap-2">
    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Workouts logged, last 12 months</h2>
    <p id="heat-summary" class="text-sm text-gray-500"></p>
  </figcaption>
  <div id="heat" class="relative mt-4 overflow-x-auto"></div>
</figure>
```

```css
@theme {
  --color-heat-0: oklch(95% 0.01 250); --color-heat-1: oklch(85% 0.07 250); --color-heat-2: oklch(72% 0.12 250);
  --color-heat-3: oklch(58% 0.15 250); --color-heat-4: oklch(42% 0.14 250);
}
@layer base { @media (prefers-color-scheme: dark) { :root {
  --color-heat-0: oklch(25% 0.01 250); --color-heat-1: oklch(38% 0.08 250); --color-heat-2: oklch(52% 0.12 250);
  --color-heat-3: oklch(66% 0.14 250); --color-heat-4: oklch(80% 0.12 250);
} } }
```

```js
const dayFmt = new Intl.DateTimeFormat('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
const monFmt = new Intl.DateTimeFormat('en-GB', { month: 'short' });
const num = new Intl.NumberFormat('en-GB');
const iso = (d) => d.toISOString().slice(0, 10);

// counts: Map<'YYYY-MM-DD', number>. end: last day shown (default today).
function heatmap(host, counts, { unit = 'workouts', end = new Date() } = {}) {
  const C = 12, G = 3, STEP = C + G, LEFT = 30, TOP = 18, WEEKS = 53;
  const start = new Date(Date.UTC(end.getUTCFullYear(), end.getUTCMonth(), end.getUTCDate() - WEEKS * 7 + 1));
  start.setUTCDate(start.getUTCDate() - ((start.getUTCDay() + 6) % 7));           // back to Monday
  const max = Math.max(1, ...counts.values());
  const level = (n) => (n === 0 ? 0 : Math.min(4, 1 + Math.floor((n / max) * 3.999)));
  const cells = [], months = [], monthly = new Map();
  let total = 0, active = 0;
  for (let d = new Date(start), i = 0; d <= end; d.setUTCDate(d.getUTCDate() + 1), i++) {
    const key = iso(d), n = counts.get(key) ?? 0, week = Math.floor(i / 7), row = i % 7;
    total += n; if (n) active++;
    const mk = key.slice(0, 7); monthly.set(mk, (monthly.get(mk) ?? 0) + n);
    if (d.getUTCDate() === 1 && week < WEEKS - 1) months.push(`<text x="${LEFT + week * STEP}" y="${TOP - 6}" class="fill-current text-[10px]">${monFmt.format(d)}</text>`);
    cells.push(`<rect x="${LEFT + week * STEP}" y="${TOP + row * STEP}" width="${C}" height="${C}" rx="2" class="fill-heat-${level(n)}"
      data-date="${key}" data-count="${n}" tabindex="-1"><title>${dayFmt.format(d)}: ${num.format(n)} ${unit}</title></rect>`);
  }
  const W = LEFT + WEEKS * STEP, H = TOP + 7 * STEP;
  host.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" tabindex="0" aria-labelledby="${host.id}-t ${host.id}-d" aria-describedby="${host.id}-tip"
         class="block h-auto min-w-[${W}px] max-w-none focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-heat-3">
      <title id="${host.id}-t">Daily ${unit}, ${dayFmt.format(start)} to ${dayFmt.format(end)}</title>
      <desc id="${host.id}-d">${num.format(total)} ${unit} on ${active} days. Use arrow keys to move between days.</desc>
      ${['Mon', 'Wed', 'Fri'].map((l, i) => `<text x="0" y="${TOP + i * 2 * STEP + C - 2}" class="fill-current text-[10px]">${l}</text>`).join('')}
      ${months.join('')}${cells.join('')}
    </svg>
    <output id="${host.id}-tip" role="status" hidden class="pointer-events-none absolute -translate-x-1/2 rounded-md bg-gray-900 px-2 py-1 text-xs text-white dark:bg-gray-100 dark:text-gray-900"></output>
    <p class="mt-2 flex items-center justify-end gap-1 text-xs text-gray-500">Less
      ${[0, 1, 2, 3, 4].map((l) => `<span aria-hidden="true" class="size-3 rounded-sm bg-heat-${l}"></span>`).join('')} More
      <span class="sr-only">Scale: 0, then four steps up to ${num.format(max)} per day.</span></p>
    <table class="sr-only"><caption>Monthly totals of ${unit}</caption>
      <thead><tr><th scope="col">Month</th><th scope="col">${unit}</th></tr></thead>
      <tbody>${[...monthly].map(([m, n]) => `<tr><th scope="row">${m}</th><td>${num.format(n)}</td></tr>`).join('')}</tbody></table>`;
  document.getElementById('heat-summary').textContent = `${num.format(total)} ${unit} on ${active} of ${WEEKS * 7} days`;

  const svg = host.querySelector('svg'), tip = host.querySelector('output'), rects = [...svg.querySelectorAll('rect')];
  let i = rects.length - 1;
  const show = (idx) => {
    i = Math.max(0, Math.min(rects.length - 1, idx)); const r = rects[i];
    tip.hidden = false; tip.textContent = r.querySelector('title').textContent;
    tip.style.left = `${r.x.baseVal.value + C / 2}px`; tip.style.top = `${r.y.baseVal.value - 28}px`;
    rects.forEach((q) => q.removeAttribute('stroke')); r.setAttribute('stroke', 'currentColor');
  };
  svg.addEventListener('pointerover', (e) => { const k = rects.indexOf(e.target); if (k > -1) show(k); });
  svg.addEventListener('pointerleave', () => { tip.hidden = true; });
  svg.addEventListener('focus', () => show(i));
  svg.addEventListener('blur', () => { tip.hidden = true; });
  svg.addEventListener('keydown', (e) => {
    const step = { ArrowRight: 7, ArrowLeft: -7, ArrowDown: 1, ArrowUp: -1 }[e.key];
    if (step === undefined) return; e.preventDefault(); show(i + step);
  });
}

heatmap(document.getElementById('heat'), new Map([['2026-10-20', 1], ['2026-10-18', 2], ['2026-10-15', 1], ['2026-09-30', 3], ['2026-09-27', 1]]));
```

Why this shape: dates are handled in UTC throughout so a DST change does not produce a duplicated or missing cell. The SVG has intrinsic `width`/`height` and sits in an `overflow-x-auto` wrapper, so on a phone it scrolls rather than shrinking to 2 px cells. One focus stop on the `<svg>` plus arrow keys gives keyboard users a day-by-day walk, announced through the `role="status"` output, while the hidden monthly table gives the overview. `level()` scales by the maximum in the data, so a light user's three workouts still reach the dark end.

## Variations

- **Fixed thresholds instead of relative**: replace `level` with `[0, 1, 3, 5, 8]` buckets when the scale must be comparable across users or years, and say the thresholds in the legend's `sr-only` text.
- **Sunday-first weeks**: drop the `+ 6` in the Monday alignment and change the weekday labels; US audiences expect Sunday on top.
- **Click to filter**: dispatch a `CustomEvent('day-select', { detail: { date } })` from `show()` on click or Enter and let the page's list filter to that day.
- **Diverging scale** (temperature anomaly): two hues around a neutral centre, blue to grey to orange, five steps each side, with the zero value always the neutral grey.

## Pitfalls

- `new Date('2026-10-18')` parses as UTC midnight but `toISOString` on a local-time date can slip a day west of Greenwich; build and read every date in UTC as above.
- 371 `<title>` elements are a hover tooltip only; the `output` tooltip and the keyboard walk exist because `<title>` is unreachable from the keyboard and unreliable on touch.
- A heatmap scaled to the container (`w-full`) becomes unreadable under 700 px; horizontal scroll with `min-w` is the right trade here, as with wide tables.
- Green-to-red scales fail for the most common colour-blindness; a single hue at five lightnesses is both safer and calmer. Check level 0 against level 1 for at least 3:1 contrast with `web-a11y-color-contrast`.
- `tabindex="-1"` on each `<rect>` keeps them out of the tab order while allowing `focus()` if you add click-to-select; without it, some browsers put every rect in the tab order once one has an event handler.
- Month labels are placed at the week containing the 1st; two short months can collide at the first column, which is why the last-week guard drops a label that would overflow.

## Related skills

- `web-data-svg-bar-chart`
- `web-data-chart-accessibility`
- `web-data-fetch-and-cache`
- `web-a11y-color-contrast`
- `web-ui-tooltip-and-popover`
