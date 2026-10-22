---
name: web-js-storage
description: Write a safe `storage.js` module for localStorage/sessionStorage with JSON, namespaced keys, schema versioning and migration, expiry, quota and private-mode errors, cross-tab sync, plus when to switch to IndexedDB. Use whenever a user says "remember the user's choice", "save to localStorage", "persist the theme/cart/form", "keep data after reload", or "store offline data".
---

# Browser storage without surprises

`localStorage` is synchronous, string-only, ~5 MB, and throws in some private-browsing modes or when full. Wrapped naively it works on your machine and corrupts the first time you change the data shape. Wrap it once: JSON in and out, a key prefix so unrelated scripts on the same origin don't collide, a version number so old data can be migrated or discarded, and every call in `try/catch` so a storage failure never breaks the page (the feature degrades, the site keeps working).

## Pattern

```js
// /js/storage.js
const PREFIX = 'mysite:';           // change per project; keeps keys from colliding
const VERSION = 2;                  // bump when a stored shape changes

const migrations = {
  // v1 -> v2: `theme` was 'night', now 'dark'
  2: (data) => (data?.theme === 'night' ? { ...data, theme: 'dark' } : data),
};

export function createStorage(area = localStorage) {
  const safe = (fn, fallback) => { try { return fn(); } catch { return fallback; } };

  function read(key, fallback = null) {
    const raw = safe(() => area.getItem(PREFIX + key), null);
    if (raw === null) return fallback;
    let record;
    try { record = JSON.parse(raw); } catch { remove(key); return fallback; }   // corrupt: drop it
    if (record.expires && Date.now() > record.expires) { remove(key); return fallback; }
    let { v = 1, data } = record;
    while (v < VERSION) { v += 1; data = migrations[v]?.(data) ?? data; }
    if (record.v !== VERSION) write(key, data);                               // persist migrated shape
    return data ?? fallback;
  }

  function write(key, data, { ttl } = {}) {
    const record = { v: VERSION, data, ...(ttl ? { expires: Date.now() + ttl } : {}) };
    try {
      area.setItem(PREFIX + key, JSON.stringify(record));
      return true;
    } catch (error) {
      if (error?.name === 'QuotaExceededError') console.warn(`storage full, could not save "${key}"`);
      return false;                     // callers treat storage as optional
    }
  }

  const remove = (key) => safe(() => area.removeItem(PREFIX + key));
  const clear = () => safe(() => Object.keys(area).filter((k) => k.startsWith(PREFIX)).forEach((k) => area.removeItem(k)));

  /** Fires when another tab changes this key. Returns unsubscribe. */
  function watch(key, callback) {
    const handler = (e) => { if (e.storageArea === area && e.key === PREFIX + key) callback(read(key)); };
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }

  return { read, write, remove, clear, watch };
}

export const local = createStorage(localStorage);
export const session = createStorage(sessionStorage);
```

```html
<form data-js="prefs" class="space-y-2">
  <label class="flex items-center gap-2"><input type="checkbox" name="compact"> Compact layout</label>
  <label class="flex items-center gap-2">Theme
    <select name="theme"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select>
  </label>
</form>
```

```js
// /js/prefs.js
import { local } from './storage.js';

const form = document.querySelector('[data-js="prefs"]');
const defaults = { compact: false, theme: 'system' };

function apply(prefs) {
  document.documentElement.classList.toggle('compact', prefs.compact);
  document.documentElement.dataset.theme = prefs.theme;
  form.elements.compact.checked = prefs.compact;
  form.elements.theme.value = prefs.theme;
}

apply({ ...defaults, ...local.read('prefs', {}) });     // merge so new fields get defaults
form.addEventListener('change', () => {
  const prefs = { compact: form.elements.compact.checked, theme: form.elements.theme.value };
  apply(prefs);
  local.write('prefs', prefs);
});
local.watch('prefs', (prefs) => prefs && apply({ ...defaults, ...prefs }));   // other tab changed it
```

## Variations

- **Expiring cache**: `local.write('feed', items, { ttl: 5 * 60_000 })` then `local.read('feed') ?? await fetchFeed()`; good for API responses you are allowed to show stale.
- **Session-only**: use `session` for multi-step form drafts (`web-form-multi-step`) so data dies with the tab; never put passwords or tokens in either area (readable by any script on the origin).
- **Large or structured data** (files, thousands of records, blobs): switch to IndexedDB. The minimal API: `indexedDB.open(name, version)` with `onupgradeneeded` creating `db.createObjectStore('items', { keyPath: 'id' })`, then transactions; it is async and holds hundreds of MB. Wrap it in promises once or accept a pinned helper if the skill scope allows.
- **Cookies** only when the *server* must read the value (auth, locale for SSR); set `SameSite=Lax; Secure; Path=/`.

## Pitfalls

- Reading on every render is synchronous disk I/O on some browsers. Read once at startup, keep the value in memory (see `web-js-state-and-render`), and write on change.
- `JSON.stringify` drops `undefined`, functions, `Map`, `Set` and `Date` becomes a string. Convert at the edge (`date.toISOString()`, `[...set]`).
- Safari in private mode once threw on every `setItem`; some browsers clear storage after 7 days without interaction. Treat storage as a cache, never the only copy of important data.
- The `storage` event fires only in *other* tabs, not the one that wrote. Update the current tab yourself.
- Forgetting the version: changing a field name silently breaks every returning visitor. Bump `VERSION`, add a migration, or at least discard old shapes.
- Storage is per origin: `localhost:3000` and `localhost:5173` do not share, and neither does `http` with `https`.

## Related skills

- `web-js-state-and-render`
- `web-design-dark-mode`
- `web-form-multi-step`
- `web-perf-caching-and-service-worker`
- `web-ship-analytics-and-privacy`
