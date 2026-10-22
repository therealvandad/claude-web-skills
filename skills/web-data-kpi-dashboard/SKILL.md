---
name: web-data-kpi-dashboard
description: 'Build a KPI dashboard section in Tailwind v4: a responsive grid of metric tiles with the figure, a delta versus the previous period, a trend arrow that knows whether up is good, and a 7/30/90-day range switch. Use whenever a user asks for a "dashboard", "KPI cards", "metrics overview", "stats tiles with arrows", or "admin home page numbers".'
---

# KPI dashboard

A KPI tile answers three questions in under a second: what is the number, which way is it moving, and is that good. The number is large and tabular, the delta is a percentage with an explicit sign, and the arrow colour depends on the metric (churn going down is green). A range switch rerenders every tile from one data object, so the tiles never disagree about the period. Everything is a `<dl>` so each label and value stay paired for screen readers.

## Pattern

```html
<section aria-labelledby="kpi-title" class="mx-auto max-w-6xl px-4">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <h2 id="kpi-title" class="text-lg font-semibold text-gray-900 dark:text-gray-100">Overview</h2>
    <fieldset class="flex rounded-lg border border-gray-300 p-0.5 text-sm dark:border-gray-700">
      <legend class="sr-only">Time range</legend>
      <label class="cursor-pointer rounded-md px-3 py-1 has-[:checked]:bg-gray-900 has-[:checked]:text-white has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-indigo-600 dark:has-[:checked]:bg-gray-100 dark:has-[:checked]:text-gray-900">
        <input type="radio" name="range" value="7" class="sr-only"> 7 days</label>
      <label class="cursor-pointer rounded-md px-3 py-1 has-[:checked]:bg-gray-900 has-[:checked]:text-white has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-indigo-600 dark:has-[:checked]:bg-gray-100 dark:has-[:checked]:text-gray-900">
        <input type="radio" name="range" value="30" checked class="sr-only"> 30 days</label>
      <label class="cursor-pointer rounded-md px-3 py-1 has-[:checked]:bg-gray-900 has-[:checked]:text-white has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-indigo-600 dark:has-[:checked]:bg-gray-100 dark:has-[:checked]:text-gray-900">
        <input type="radio" name="range" value="90" class="sr-only"> 90 days</label>
    </fieldset>
  </div>
  <dl id="kpis" class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-live="polite"></dl>
</section>
```

```js
const fmt = {
  eur: new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }),
  int: new Intl.NumberFormat('en-IE'),
  pct: new Intl.NumberFormat('en-IE', { style: 'percent', maximumFractionDigits: 1 }),
  delta: new Intl.NumberFormat('en-IE', { style: 'percent', signDisplay: 'exceptZero', maximumFractionDigits: 1 }),
};

// One object, keyed by range. current and previous are the same length of period.
const metrics = {
  7:  [{ key: 'revenue', label: 'Revenue', current: 6842.3, previous: 6210.75, format: 'eur', good: 'up' },
       { key: 'signups', label: 'New sign-ups', current: 212, previous: 198, format: 'int', good: 'up' },
       { key: 'churn', label: 'Churn rate', current: 0.0121, previous: 0.0108, format: 'pct', good: 'down' },
       { key: 'aov', label: 'Average order', current: 84.6, previous: 86.1, format: 'eur', good: 'up' }],
  30: [{ key: 'revenue', label: 'Revenue', current: 28215.9, previous: 26740.3, format: 'eur', good: 'up' },
       { key: 'signups', label: 'New sign-ups', current: 931, previous: 802, format: 'int', good: 'up' },
       { key: 'churn', label: 'Churn rate', current: 0.0417, previous: 0.0452, format: 'pct', good: 'down' },
       { key: 'aov', label: 'Average order', current: 83.2, previous: 85.4, format: 'eur', good: 'up' }],
  90: [{ key: 'revenue', label: 'Revenue', current: 79516.5, previous: 71120.2, format: 'eur', good: 'up' },
       { key: 'signups', label: 'New sign-ups', current: 2604, previous: 2211, format: 'int', good: 'up' },
       { key: 'churn', label: 'Churn rate', current: 0.1188, previous: 0.1264, format: 'pct', good: 'down' },
       { key: 'aov', label: 'Average order', current: 82.9, previous: 84.7, format: 'eur', good: 'up' }],
};

function tile(m, days) {
  const change = m.previous ? (m.current - m.previous) / m.previous : 0;
  const better = change === 0 ? null : (change > 0) === (m.good === 'up');
  const tone = better === null ? 'text-gray-500' : better ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-700 dark:text-rose-400';
  const arrow = change === 0 ? '→' : change > 0 ? '↑' : '↓';
  const word = change === 0 ? 'unchanged' : change > 0 ? 'up' : 'down';
  return `
    <div class="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-950">
      <dt class="text-sm text-gray-600 dark:text-gray-400">${m.label}</dt>
      <dd class="mt-1 flex flex-wrap items-baseline gap-x-3">
        <span class="text-3xl font-semibold tracking-tight tabular-nums text-gray-900 dark:text-gray-100">${fmt[m.format].format(m.current)}</span>
        <span class="text-sm font-medium tabular-nums ${tone}">
          <span aria-hidden="true">${arrow}</span> ${fmt.delta.format(change)}
          <span class="sr-only">, ${word}${better === null ? '' : better ? ', improvement' : ', worse'}</span>
        </span>
      </dd>
      <dd class="mt-1 text-xs text-gray-500">vs previous ${days} days: ${fmt[m.format].format(m.previous)}</dd>
    </div>`;
}

const dl = document.getElementById('kpis');
const render = (days) => { dl.innerHTML = metrics[days].map((m) => tile(m, days)).join(''); };
document.querySelectorAll('input[name="range"]').forEach((r) => r.addEventListener('change', () => render(r.value)));
render(document.querySelector('input[name="range"]:checked').value);
```

Why this shape: `good: 'up' | 'down'` on each metric is the only honest way to colour deltas; a hard-coded "green for positive" calls rising churn an improvement. The visible delta uses `signDisplay: 'exceptZero'` so "+4.8%" and "-2.6%" are unambiguous even without the arrow or the colour, and the `sr-only` suffix adds "improvement" or "worse" for screen readers. The range switch is a native radio group styled with `has-[:checked]`, so it works with arrow keys for free. `aria-live="polite"` on the `<dl>` announces the rerender once.

## Variations

- **Sparkline per tile**: add a `<dd>` with `<span data-sparkline="...">` from `web-data-sparklines` under the figure; pass the daily series in the metric object.
- **Linked tiles**: wrap the whole tile content in `<a href="/reports/revenue">` with `hover:border-gray-400` and keep the `<dt>`/`<dd>` inside; the whole card is one tab stop.
- **Loading state**: render tiles with `animate-pulse` placeholders of the same height while the fetch is pending (`web-ui-skeleton-and-loading`); never leave the grid empty, it shifts the page.
- **Targets instead of previous period**: compute `change` against `m.target` and label the footer "of 30,000 target"; a progress ring from `web-data-donut-and-progress` fits in the corner.

## Pitfalls

- Deltas against a previous period of a different length (this month vs last quarter) are meaningless; the data object stores equal windows, keep it that way.
- A metric whose previous value is 0 divides by zero; the `m.previous ? ... : 0` guard renders "0%", better is "new" text, add that case if it happens in your data.
- Colouring every delta and every figure turns the grid into a traffic light; only the delta carries colour, and the figure stays neutral.
- Four tiles at `sm:grid-cols-2` and twelve at `xl:grid-cols-4` is fine; eight tiles on a phone is a wall of numbers. Show the four that matter and link to the rest.
- `innerHTML` rerender on range change drops focus if focus was inside the grid; the switch is outside the `<dl>`, which is why focus survives.
- Percent formats expect fractions: `0.0417`, not `4.17`; mixing the two is the most common dashboard bug.

## Related skills

- `web-section-stats-band`
- `web-data-sparklines`
- `web-data-number-formatting`
- `web-layout-dashboard-sidebar`
- `web-motion-counters-and-tickers`
- `web-ui-skeleton-and-loading`
