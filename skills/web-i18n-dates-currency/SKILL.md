---
name: web-i18n-dates-currency
description: Format dates, times, numbers, prices, units, lists, relative times and plural categories per locale with the built-in Intl APIs, no library, in markup that still reads without JavaScript. Use when a user says "format the date for Germany", "show prices in euros", "1,000 vs 1.000", "3 days ago", "localise numbers", "time zones" or "Intl".
---

# Locale-aware dates, numbers and currency

`12/03/2026` is December in New York and March in London; `1.234` is one thousand in Berlin and one point two in Boston. Never build these strings by hand. The browser ships the full CLDR data behind `Intl`, so one formatter per locale gives correct digits, separators, month names, currency placement and plural categories for every language, including Arabic digits and right-to-left marks. Render a sensible default in the HTML (ISO date, plain amount) and let a small module upgrade it to the reader's locale.

## Pattern

Machine values live in attributes; the visible text is a fallback that the script replaces:

```html
<html lang="de">
...
<article class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
  <p>Veröffentlicht <time data-fmt="date" datetime="2026-03-14T15:30:00Z">2026-03-14</time>
     (<time data-fmt="relative" datetime="2026-03-14T15:30:00Z">14.03.</time>)</p>
  <p class="text-2xl font-semibold tabular-nums text-gray-900 dark:text-white">
    <data data-fmt="money" data-currency="EUR" value="1234.5">EUR 1234.50</data>
  </p>
  <p>Autoren: <span data-fmt="list" data-items='["Lena","Omar","Yael"]'>Lena, Omar, Yael</span></p>
  <p><data data-fmt="number" value="1234567.891">1234567.891</data> Downloads</p>
</article>
<script type="module" src="/js/format.js"></script>
```

```js
// js/format.js - one cached formatter per (type, locale, options)
const locale = document.documentElement.lang || navigator.language;
const cache = new Map();
function fmt(Ctor, opts = {}) {
  const key = Ctor.name + JSON.stringify(opts);
  if (!cache.has(key)) cache.set(key, new Ctor(locale, opts));
  return cache.get(key);
}

export const formatDate = (d, opts = { dateStyle: 'long' }) => fmt(Intl.DateTimeFormat, opts).format(new Date(d));
export const formatNumber = (n, opts) => fmt(Intl.NumberFormat, opts).format(n);
export const formatMoney = (n, currency) => fmt(Intl.NumberFormat, { style: 'currency', currency }).format(n);
export const formatList = (items, type = 'conjunction') => fmt(Intl.ListFormat, { type }).format(items);

const UNITS = [['year', 31536e6], ['month', 2592e6], ['week', 6048e5], ['day', 864e5], ['hour', 36e5], ['minute', 6e4]];
export function formatRelative(d, now = Date.now()) {
  const diff = new Date(d) - now;
  const [unit, ms] = UNITS.find(([, ms]) => Math.abs(diff) >= ms) ?? ['second', 1e3];
  return fmt(Intl.RelativeTimeFormat, { numeric: 'auto' }).format(Math.round(diff / ms), unit);
}

const handlers = {
  date: el => formatDate(el.dateTime),
  relative: el => formatRelative(el.dateTime),
  money: el => formatMoney(Number(el.value), el.dataset.currency),
  number: el => formatNumber(Number(el.value)),
  list: el => formatList(JSON.parse(el.dataset.items)),
};
for (const el of document.querySelectorAll('[data-fmt]')) {
  el.textContent = handlers[el.dataset.fmt]?.(el) ?? el.textContent;
}
```

What the same values become (Node 24 / current browsers):

```text
              date              money        number          list               relative(-1 day)
en-US   March 14, 2026      €1,234.50    1,234,567.891   Lena, Omar, and Yael   yesterday
de-DE   14. März 2026       1.234,50 €   1.234.567,891   Lena, Omar und Yael    gestern
ar-EG   ١٤ مارس ٢٠٢٦        ١٬٢٣٤٫٥٠ €   ١٬٢٣٤٬٥٦٧٫٨٩١   Lena وOmar وYael        أمس
he-IL   14 במרץ 2026        1,234.50 ₪*  1,234,567.891   Lena, Omar ו-Yael      אתמול
```

(*with `currency: 'ILS'`.) Plural categories are data too, and they differ: `new Intl.PluralRules('ar').select(n)` for 0, 1, 2, 3, 11, 100 gives `zero, one, two, few, many, other`; English only has `one` and `other`; Hebrew adds `two`. Pick the string with that category (`web-i18n-translation-strings`), never with `n === 1`.

## Variations

- **Time zones**: a meeting time must show in the reader's zone, a shop's opening hours in the shop's. Pass `timeZone: 'Europe/Berlin'` for the latter; omit it for the former. Add `timeZoneName: 'short'` when both could be confused.
- **Digits in Arabic**: the region decides. Plain `ar` and `ar-AE` give `1,234.5`, `ar-EG` and `ar-SA` give `١٬٢٣٤٫٥`. Force either with `ar-EG-u-nu-latn` or the option `numberingSystem: 'arab'`/`'latn'` instead of replacing digits by hand.
- **Compact and units**: `{ notation: 'compact' }` turns 12500 into `13K` in English (German only abbreviates from a million, `1,2 Mio.`); `{ style: 'unit', unit: 'kilometer-per-hour' }` gives `50 km/h`; `{ style: 'percent' }` takes a fraction, so pass `0.256` for `25,6 %`.
- **Ranges**: `formatRange(start, end)` exists on both `DateTimeFormat` ("14.–16. März 2026") and `NumberFormat` ("€10 – €20"); it removes repeated parts that string concatenation would duplicate.

## Pitfalls

- `new Date('2026-03-14')` is midnight UTC, which is still 13 March in America. Store date-only values as `YYYY-MM-DD`, format them with `timeZone: 'UTC'`, and keep real instants as full ISO strings with `Z`.
- Currency is not implied by locale: `de-CH` users may pay in EUR. Always pass `currency` explicitly, and never convert by formatting; formatting only changes symbols. JPY has no minor unit (`¥1,235`), so do not hard-code two decimals.
- Creating a formatter is slow, calling `format` is cheap. Cache formatters as above instead of calling `toLocaleString()` in a loop over 1,000 table rows.
- Formatted output may contain invisible characters (U+200F right-to-left mark, U+202F narrow no-break space in French). Do not compare or parse formatted strings; test against `formatToParts()` or the raw value.
- Use `tabular-nums` on prices and counters so digits do not jitter, and keep the value in `<data value>` or `<time datetime>` so crawlers and copy-paste get the machine form.
- Sorting names? Use `Intl.Collator(locale).compare`, not `<`: `ä` sorts with `a` in German but after `z` in Swedish.

## Related skills

- `web-i18n-translation-strings`
- `web-i18n-multilanguage-structure`
- `web-i18n-rtl`
- `web-ui-data-table`
- `web-layout-pricing-table`
