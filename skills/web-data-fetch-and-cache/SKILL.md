---
name: web-data-fetch-and-cache
description: 'Load chart data from JSON or CSV in vanilla JS: a quote-aware CSV parser, localStorage caching with a max age, timeouts, polling that pauses in hidden tabs, and loading, stale and error states. Use whenever a user asks to "load data from a CSV", "fetch JSON for a chart", "cache API results", "refresh every minute", or "show last updated".'
---

# Fetch and cache data

A data page has four states, not one: loading, fresh, stale (showing cached data while a refresh runs or after it failed) and error with nothing to show. Most hand-rolled dashboards only handle "fresh" and go blank on a slow network. The pattern below shows cached data instantly, revalidates in the background, says how old the numbers are, and parses CSV with quoted fields correctly, because `line.split(',')` breaks on the first `"Smith, Jane"`.

## Pattern

```html
<section class="mx-auto max-w-3xl px-4" aria-labelledby="sales-h">
  <div class="flex items-baseline justify-between gap-2">
    <h2 id="sales-h" class="text-lg font-semibold">Sales by region</h2>
    <p id="sales-status" class="text-sm text-gray-500" role="status">Loading…</p>
  </div>
  <div id="sales" class="mt-4" aria-busy="true"></div>
  <button id="sales-retry" type="button" hidden class="mt-2 rounded border px-3 py-1 text-sm focus-visible:outline-2 focus-visible:outline-offset-2">Try again</button>
</section>
```

```js
export function parseCSV(text) {
  const rows = []; let row = [], field = '', q = false;
  text = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') q = false;
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); rows.push(row); row = []; field = '';
    } else field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [head, ...body] = rows.filter((r) => r.some((f) => f.trim() !== ''));
  return body.map((r) => Object.fromEntries(head.map((h, i) => [h.trim(), r[i] ?? ''])));
}

async function getJSONorCSV(url, { timeout = 8000 } = {}) {
  const res = await fetch(url, { signal: AbortSignal.timeout(timeout), headers: { Accept: 'application/json, text/csv' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (res.headers.get('content-type') ?? '').includes('json') ? res.json() : parseCSV(await res.text());
}

const read = (k) => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } };
const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* quota or private mode */ } };

export async function loadCached(url, { maxAge = 5 * 60_000, onData, onState }) {
  const key = `cache:v1:${url}`, hit = read(key);
  if (hit) onData(hit.data, { stale: Date.now() - hit.at > maxAge, at: hit.at });
  if (hit && Date.now() - hit.at <= maxAge) return;
  onState('refreshing', hit);
  try {
    const data = await getJSONorCSV(url);
    write(key, { at: Date.now(), data });
    onData(data, { stale: false, at: Date.now() });
  } catch (err) {
    onState(hit ? 'stale-error' : 'error', hit, err);
  }
}

export function poll(fn, ms) {
  let id;
  const start = () => { clearInterval(id); fn(); id = setInterval(fn, ms); };
  document.addEventListener('visibilitychange', () => (document.hidden ? clearInterval(id) : start()));
  start();
}

const host = document.getElementById('sales'), status = document.getElementById('sales-status');
const retry = document.getElementById('sales-retry');
const time = (at) => new Date(at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
const run = () => loadCached('/data/sales.csv', {
  maxAge: 60_000,
  onData(rows, { stale, at }) {
    host.setAttribute('aria-busy', 'false'); retry.hidden = true;
    renderTable(host, rows); // your chart or table render
    status.textContent = `${stale ? 'Cached' : 'Updated'} ${time(at)}`;
  },
  onState(state, hit) {
    if (state === 'refreshing' && !hit) status.textContent = 'Loading…';
    if (state === 'stale-error') status.textContent = `Offline, showing data from ${time(hit.at)}`;
    if (state === 'error') { status.textContent = 'Could not load sales data.'; retry.hidden = false; }
  },
});
retry.addEventListener('click', run);
poll(run, 60_000);
```

Why this shape: cached data paints before the network answers, the status line always says how old the numbers are, and a failed refresh keeps the old numbers on screen instead of replacing them with an error. The parser walks characters once, so quoted commas, escaped `""`, CRLF line endings and a UTF-8 BOM from Excel all survive.

## Variations

- **Typed CSV columns**: everything parses as a string. Map once after parsing: `rows.map((r) => ({ ...r, amount: Number(r.amount), date: new Date(r.date) }))`, and drop rows where `Number.isNaN`.
- **Cache per session**: swap `localStorage` for `sessionStorage` when data must not outlive the tab, or for IndexedDB when payloads pass 1 MB.
- **Server-sent freshness**: if the API sends `ETag`, store it with the data and send `If-None-Match`; a `304` means only the timestamp needs updating.
- **Skeleton first load**: put a `web-ui-skeleton-and-loading` placeholder inside the host and replace it in `onData`.

## Pitfalls

- Never insert parsed CSV or JSON strings with `innerHTML` unescaped; a cell containing `<img onerror>` runs. Use `textContent` or an escape helper.
- Formula injection: a CSV cell starting with `=`, `+`, `-` or `@` executes when re-exported to Excel. Prefix those with `'` on export (see `web-data-table-export`).
- Bump the `v1` in the cache key when the data shape changes, or old cached objects will break the renderer.
- `setInterval` polling in a background tab wastes battery and API quota; the `visibilitychange` pause is part of the pattern, not an extra.
- `AbortSignal.timeout` needs a 2022+ browser; without a timeout a hung request leaves "Loading…" forever.
- Fetching a local `.csv` from `file://` fails with CORS; serve the folder (`npx serve`) during development.

## Related skills

- `web-js-fetch-and-apis`
- `web-js-storage`
- `web-data-table-export`
- `web-data-number-formatting`
- `web-design-empty-and-error-states`
- `web-ui-skeleton-and-loading`
