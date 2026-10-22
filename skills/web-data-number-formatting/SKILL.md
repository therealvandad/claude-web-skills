---
name: web-data-number-formatting
description: Format numbers for display with the built-in Intl API, no library: thousands separators, currency, percent, units (kB, km/h), compact notation (1.2K, 3.4M), signed deltas and relative time ("3 days ago"), via cached formatters and data-attributes. Use whenever a user asks to "format a number", "show as money", "add commas", "1.2K style", "time ago", or "percent with one decimal".
---

# Number formatting with Intl

Every number on a page is read by a person in a locale: `1234.5` is "1,234.50" in the US, "1.234,50" in Germany and "1 234,50" in France. `Intl.NumberFormat` and `Intl.RelativeTimeFormat` ship in every browser, know those rules, and cost zero bytes. Build formatters once (they are slow to construct, fast to call), keep the raw value in the HTML so the page still makes sense without the script, and let a `data-format` attribute say how each number should look.

## Pattern

```html
<dl class="grid gap-4 sm:grid-cols-3 tabular-nums">
  <div class="rounded-lg border border-gray-200 p-4 dark:border-gray-800">
    <dt class="text-sm text-gray-500">Revenue</dt>
    <dd class="text-2xl font-semibold" data-format="currency" data-currency="EUR" data-value="48210.4">48210.40 EUR</dd>
  </div>
  <div class="rounded-lg border border-gray-200 p-4 dark:border-gray-800">
    <dt class="text-sm text-gray-500">Conversion</dt>
    <dd class="text-2xl font-semibold" data-format="percent" data-value="0.0347">3.47%</dd>
  </div>
  <div class="rounded-lg border border-gray-200 p-4 dark:border-gray-800">
    <dt class="text-sm text-gray-500">Page views</dt>
    <dd class="text-2xl font-semibold" data-format="compact" data-value="1284530">1284530</dd>
    <p class="text-sm" data-format="delta" data-value="0.124">+12.4%</p>
  </div>
</dl>
<p class="mt-4 text-sm text-gray-500">Updated <time datetime="2026-10-20T09:15:00Z" data-format="relative">20 Oct 2026, 09:15</time></p>
```

```js
const locale = document.documentElement.lang || navigator.language;
const cache = new Map();

function nf(options) {
  const key = JSON.stringify(options);
  if (!cache.has(key)) cache.set(key, new Intl.NumberFormat(locale, options));
  return cache.get(key);
}

const formats = {
  number: (v) => nf({ maximumFractionDigits: 2 }).format(v),
  currency: (v, el) => nf({ style: 'currency', currency: el.dataset.currency ?? 'USD' }).format(v),
  percent: (v) => nf({ style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(v),
  compact: (v) => nf({ notation: 'compact', maximumFractionDigits: 1 }).format(v),
  delta: (v) => nf({ style: 'percent', signDisplay: 'exceptZero', maximumFractionDigits: 1 }).format(v),
  unit: (v, el) => nf({ style: 'unit', unit: el.dataset.unit, unitDisplay: 'short' }).format(v),
  bytes: (v) => {
    const units = ['byte', 'kilobyte', 'megabyte', 'gigabyte', 'terabyte'];
    const i = Math.min(units.length - 1, Math.floor(Math.log10(Math.max(v, 1)) / 3));
    return nf({ style: 'unit', unit: units[i], maximumFractionDigits: 1 }).format(v / 1000 ** i);
  },
};

const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
const steps = [['year', 31536000], ['month', 2592000], ['week', 604800], ['day', 86400], ['hour', 3600], ['minute', 60], ['second', 1]];

function timeAgo(date, now = Date.now()) {
  const diff = (date.getTime() - now) / 1000;
  const [unit, secs] = steps.find(([, s]) => Math.abs(diff) >= s) ?? steps.at(-1);
  return rtf.format(Math.round(diff / secs), unit);
}

export function formatAll(root = document) {
  for (const el of root.querySelectorAll('[data-format]')) {
    const kind = el.dataset.format;
    if (kind === 'relative') {
      const d = new Date(el.getAttribute('datetime'));
      el.textContent = timeAgo(d);
      el.title = d.toLocaleString(locale, { dateStyle: 'medium', timeStyle: 'short' });
      continue;
    }
    const v = Number(el.dataset.value);
    if (!Number.isFinite(v) || !formats[kind]) continue;
    el.textContent = formats[kind](v, el);
    if (kind === 'delta') el.classList.add(v >= 0 ? 'text-green-700' : 'text-red-700', v >= 0 ? 'dark:text-green-400' : 'dark:text-red-400');
  }
}

formatAll();
setInterval(() => formatAll(), 60_000); // keep "time ago" honest
```

Why this shape: the server-rendered text is a readable fallback, `data-value` holds the machine value so formatting never parses a formatted string, and the `nf` cache means a table of 2,000 cells builds three formatters, not 2,000. `signDisplay: 'exceptZero'` gives "+12.4%" and "-3.1%" with a real minus sign, and `numeric: 'auto'` gives "yesterday" instead of "1 day ago".

## Variations

- **Fixed locale** (an invoice must match the billing country): pass `'de-DE'` instead of `locale`; never mix the user's locale with a hard-coded currency symbol in a string.
- **Compact with long names**: `{ notation: 'compact', compactDisplay: 'long' }` gives "1.3 million" for headlines where "1.3M" looks too terse.
- **Ranges**: `nf({ style: 'currency', currency: 'EUR' }).formatRange(20, 45)` gives "€20.00 – €45.00" with the locale's dash.
- **Parts for styling**: `formatToParts(48210.4)` returns `[{type:'currency'}, {type:'integer'}, ...]`; wrap the `fraction` part in `<span class="text-gray-500">` for a muted decimal.

## Pitfalls

- Money is not a float: `0.1 + 0.2` is `0.30000000000000004`. Store integer cents and divide by 100 only at display time, or round with `maximumFractionDigits` before summing.
- Currency code and fraction digits are tied: `JPY` has 0 decimals, `KWD` has 3. Let Intl pick them; do not force `minimumFractionDigits: 2` on every currency.
- Never parse a formatted string back to a number ("1.234" is one thousand in German). Keep the raw value in `data-value` or in your data array.
- Use `tabular-nums` on columns and changing figures so digits line up and counters do not jitter.
- Unit identifiers are a fixed list (`kilometer-per-hour`, `megabyte`, `celsius`); an unknown one throws a `RangeError`. Wrap custom input in `try`.
- Relative time drifts: "just now" becomes wrong after a minute. Refresh on an interval, and keep the absolute date in `title` and the `datetime` attribute.

## Related skills

- `web-data-kpi-dashboard`
- `web-data-svg-bar-chart`
- `web-data-table-export`
- `web-i18n-dates-currency`
- `web-motion-counters-and-tickers`
- `web-js-dom-utilities`
