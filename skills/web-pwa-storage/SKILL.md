---
name: web-pwa-storage
description: Store PWA app data in IndexedDB through a 40-line promise wrapper with versioned migrations, show usage against quota, request persistent storage, and let users export and import a JSON backup. Use when a user says "save data offline", "IndexedDB", "localStorage is full", "storage quota", "data disappeared", "persist storage" or "backup and restore my data".
---

# App data storage for PWAs

`localStorage` is synchronous, string-only and capped around 5 MB; it is fine for a theme choice (`web-js-storage`), not for app data. IndexedDB is the store that every browser supports, holds structured data and Blobs, and works in service workers. Its raw API is event-based and verbose, so wrap it once in promises. Then deal with the part people skip: browser storage is "best effort" and can be evicted. Show usage, ask for persistence at a sensible moment, and give users an export so their data never lives only in one browser.

## Pattern

```js
// /js/db.js - promise wrapper over IndexedDB, no library
const DB_NAME = "notes-app", VERSION = 2;
const MIGRATIONS = [                       // index = from-version; never edit a shipped step, append
  (db) => db.createObjectStore("notes", { keyPath: "id" }),
  (db, tx) => tx.objectStore("notes").createIndex("by_updated", "updatedAt"),
];
let dbPromise = null;

export function openDB() {
  return dbPromise ??= new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, VERSION);
    req.onupgradeneeded = (e) => { for (let v = e.oldVersion; v < VERSION; v++) MIGRATIONS[v](req.result, req.transaction); };
    req.onsuccess = () => {
      const db = req.result;
      db.onversionchange = () => { db.close(); dbPromise = null; };  // a newer tab is upgrading: step aside
      resolve(db);
    };
    req.onerror = () => { dbPromise = null; reject(req.error); };
    req.onblocked = () => console.warn("Close other tabs of this app to finish the upgrade.");
  });
}
const done = (req) => new Promise((res, rej) => { req.onsuccess = () => res(req.result); req.onerror = () => rej(req.error); });

export async function tx(stores, mode, fn) {
  const t = (await openDB()).transaction(stores, mode);
  const finished = new Promise((res, rej) => { t.oncomplete = res; t.onerror = t.onabort = () => rej(t.error); });
  const result = await fn(t);               // only await IDB requests inside fn, or the transaction auto-commits
  await finished;
  return result;
}

export const store = (name) => ({
  get: (key) => tx(name, "readonly", (t) => done(t.objectStore(name).get(key))),
  all: () => tx(name, "readonly", (t) => done(t.objectStore(name).getAll())),
  byIndex: (index, query) => tx(name, "readonly", (t) => done(t.objectStore(name).index(index).getAll(query))),
  put: (value) => tx(name, "readwrite", (t) => done(t.objectStore(name).put(value))),
  delete: (key) => tx(name, "readwrite", (t) => done(t.objectStore(name).delete(key))),
});

export async function storageInfo() {      // estimates, rounded on purpose by browsers
  const { usage = 0, quota = 0 } = (await navigator.storage?.estimate?.()) ?? {};
  return { usage, quota, persisted: (await navigator.storage?.persisted?.()) ?? false };
}
export const requestPersist = async () => (await navigator.storage?.persist?.()) ?? false;

export async function exportAll(names = ["notes"]) {
  const data = { app: DB_NAME, version: VERSION, exportedAt: new Date().toISOString(), stores: {} };
  for (const n of names) data.stores[n] = await store(n).all();
  return new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
}
export async function importAll(file) {
  const data = JSON.parse(await file.text());
  if (data.app !== DB_NAME || data.version > VERSION) throw new Error("This backup is from another app or a newer version.");
  const names = Object.keys(data.stores);
  await tx(names, "readwrite", (t) => {    // one transaction: all or nothing
    for (const n of names) { const s = t.objectStore(n); s.clear(); data.stores[n].forEach((row) => s.put(row)); }
  });
}
```

```html
<section aria-labelledby="data-h" class="grid gap-3 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
  <h2 id="data-h" class="font-semibold">Data on this device</h2>
  <label class="grid gap-1 text-sm">Storage used <meter data-meter min="0" max="1" value="0" class="w-full"></meter></label>
  <p data-usage class="text-sm text-slate-600 dark:text-slate-300"></p>
  <div class="flex flex-wrap gap-2">
    <button type="button" data-export class="rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:bg-white dark:text-slate-900">Export backup</button>
    <label class="cursor-pointer rounded-md border border-slate-300 px-3 py-2 text-sm font-medium focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-slate-900 dark:border-slate-600">
      Import backup <input type="file" accept=".json,application/json" data-import class="sr-only">
    </label>
  </div>
  <p data-data-status role="status" class="text-sm"></p>
</section>
<script type="module">
  import { storageInfo, exportAll, importAll } from "/js/db.js";
  const $ = (s) => document.querySelector(s);
  const mb = (b) => `${(b / 1e6).toFixed(1)} MB`;
  async function render() {
    const { usage, quota, persisted } = await storageInfo();
    $("[data-meter]").value = quota ? usage / quota : 0;
    $("[data-usage]").textContent = `${mb(usage)} of about ${mb(quota)}. ${persisted ? "Protected from automatic cleanup." : "The browser may clear this if space runs low."}`;
  }
  $("[data-export]").addEventListener("click", async () => {
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(await exportAll()), download: `notes-backup-${new Date().toISOString().slice(0, 10)}.json` });
    a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  $("[data-import]").addEventListener("change", async (e) => {
    try { await importAll(e.target.files[0]); $("[data-data-status]").textContent = "Backup restored."; render(); }
    catch (err) { $("[data-data-status]").textContent = `Import failed: ${err.message}`; }
    e.target.value = "";
  });
  render();
</script>
```

Call `requestPersist()` after a meaningful moment (the app is installed, or the user saved their tenth note), not on load. Chromium grants or denies silently based on engagement and install state, Firefox shows a permission prompt, Safari 17+ decides by heuristics. A denial is normal; keep the export button prominent either way.

## Variations

- **Blobs and files**: put `Blob`s straight into a store (images, audio drafts). For export, convert to data URLs with `FileReader` or zip them separately; `JSON.stringify` turns a Blob into `{}`.
- **Large binary files**: the Origin Private File System (`await navigator.storage.getDirectory()`) is faster for big files and works in all modern browsers; keep the metadata in IndexedDB.
- **Live updates across tabs**: after each write, `new BroadcastChannel("db").postMessage({ store: "notes" })` and re-render in the listener (`web-js-state-and-render`).
- **Save the backup as a real file**: pass the Blob to `saveFile` from `web-pwa-share-and-files` to get a native save dialog where supported.

## Pitfalls

- Inside `tx`, awaiting `fetch` or a timer lets the transaction auto-commit, and the next request throws `TransactionInactiveError`. Fetch first, then open the transaction.
- Safari deletes all script-writable storage (IndexedDB, Cache Storage, `localStorage`) for a site after seven days of Safari use without a visit, unless the app was added to the Home Screen. A granted `persist()` also protects it. Tell Safari users to install or export.
- Quota is a share of free disk, not a fixed number: often gigabytes on desktop, far less on a full phone, tiny in private windows. Catch `QuotaExceededError` on writes and offer cleanup.
- An upgrade is blocked while another tab holds the old version open. `onversionchange` closing the connection is what lets the new tab proceed.
- Importing a backup from an older version needs migrating rows, not just a version check; keep a `migrateRow(row, fromVersion)` next to `MIGRATIONS`.
- IndexedDB is not encrypted and is readable by any script on your origin. Do not store tokens or secrets there, and clear user data on sign-out.

## Related skills

- `web-js-storage`
- `web-pwa-offline-forms`
- `web-pwa-share-and-files`
- `web-pwa-service-worker-offline`
- `web-js-state-and-render`
- `web-design-empty-and-error-states`
