---
name: web-pwa-offline-forms
description: Queue form submissions in an IndexedDB outbox when offline and replay them later, with Background Sync where supported and an online/visibility fallback everywhere else, idempotency keys and honest status messages. Use when a user says "submit while offline", "offline form", "queue requests", "background sync", "retry when back online" or "don't lose what I typed".
---

# Offline form submissions

A PWA that opens offline but loses the form the user just filled in is worse than no PWA. The fix is an outbox: write every submission to IndexedDB first, then try to send it; whatever fails stays queued and is replayed later. Background Sync lets the service worker replay even after the tab is closed, but it only exists in Chromium browsers (Chrome, Edge, Samsung Internet, Opera). Firefox and Safari have no `SyncManager`, so the page must also replay on `online`, on tab focus and on load. Build the fallback first; Background Sync is the bonus.

## Pattern

One classic script shared by the page (`<script defer>`) and the worker (`importScripts`), so both replay the same queue:

```js
// /js/outbox.js - deliberately exports self.Outbox
self.Outbox = (() => {
  const open = () => new Promise((res, rej) => {
    const r = indexedDB.open("app-outbox", 1);
    r.onupgradeneeded = () => r.result.createObjectStore("requests", { keyPath: "id" });
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  });
  const run = async (mode, fn) => {
    const t = (await open()).transaction("requests", mode); const req = fn(t.objectStore("requests"));
    return new Promise((res, rej) => { t.oncomplete = () => res(req.result); t.onerror = () => rej(t.error); });
  };
  const add = (item) => run("readwrite", (s) => s.put(item));
  const all = () => run("readonly", (s) => s.getAll());
  const remove = (id) => run("readwrite", (s) => s.delete(id));
  const retryable = (status) => status >= 500 || status === 408 || status === 429;

  async function notify(msg) {
    if (self.clients) for (const c of await self.clients.matchAll()) c.postMessage(msg); // in the worker
    else self.dispatchEvent(new CustomEvent("outbox", { detail: msg }));                // in the page
  }
  let running = null;
  function replay() { // resolves with the number still queued; rejects while offline so sync retries
    return running ??= (async () => {
      for (const item of await all()) {
        const res = await fetch(item.url, { method: "POST", credentials: "same-origin",
          headers: { "Content-Type": "application/json", "Idempotency-Key": item.id }, body: JSON.stringify(item.body) });
        if (retryable(res.status)) throw new Error(`server ${res.status}, retry later`);
        await remove(item.id);                    // sent, or rejected for good (4xx): never retry
        notify({ type: "outbox", id: item.id, ok: res.ok, status: res.status });
      }
      return (await all()).length;
    })().finally(() => { running = null; });
  }
  return { add, all, replay };
})();
```

```html
<form id="note-form" action="/api/notes" method="post" class="grid max-w-md gap-3">
  <label class="grid gap-1 text-sm font-medium">Note
    <textarea name="text" required rows="4" class="rounded-md border border-slate-300 p-2 focus-visible:outline-2 focus-visible:outline-blue-600 dark:border-slate-600 dark:bg-slate-900"></textarea>
  </label>
  <button class="justify-self-start rounded-md bg-blue-700 px-4 py-2 font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Save note</button>
  <p id="note-status" role="status" class="text-sm text-slate-600 dark:text-slate-300"></p>
</form>
<script src="/js/outbox.js" defer></script>
<script type="module">
  const form = document.querySelector("#note-form");
  const status = document.querySelector("#note-status");
  const flush = () => Outbox.replay().catch(() => {});

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await Outbox.add({ id: crypto.randomUUID(), url: form.action, body: Object.fromEntries(new FormData(form)) });
    form.reset();                                 // queued first: closing the tab now loses nothing
    status.textContent = "Saving...";
    try { await Outbox.replay(); }
    catch {
      status.textContent = "You're offline. Saved on this device and will send when you reconnect.";
      const reg = await navigator.serviceWorker?.ready;
      if (reg && "sync" in reg) reg.sync.register("outbox").catch(() => {}); // Chromium only
    }
  });
  const show = ({ ok, status: code }) => {
    status.textContent = ok ? "Sent." : `Not accepted by the server (${code}). Check the note and try again.`;
  };
  addEventListener("outbox", (e) => show(e.detail));
  navigator.serviceWorker?.addEventListener("message", (e) => { if (e.data?.type === "outbox") show(e.data); });
  // Fallback for Firefox and Safari, and a second chance everywhere
  addEventListener("online", flush);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") flush(); });
  flush();
</script>
```

```js
// sw.js - add near the top (importScripts only works during the worker's first evaluation)
importScripts("/js/outbox.js");
self.addEventListener("sync", (e) => {
  if (e.tag === "outbox") e.waitUntil(Outbox.replay()); // a rejection makes the browser retry with backoff
});
```

The server must treat `Idempotency-Key` as unique: store it with the record and return the original result on a repeat. A request can reach the server while its response is lost, and the page and the worker can replay at the same moment; the key turns both into no-ops.

## Variations

- **Pending badge**: show `(await Outbox.all()).length` next to the nav ("2 notes waiting to send") so the user knows what is not on the server yet.
- **Files**: IndexedDB stores `Blob`s directly. Keep `FormData` entries as `[name, value]` pairs, rebuild a `FormData` on replay and drop the JSON `Content-Type`; check quota first (`web-pwa-storage`).
- **Forms you cannot change**: in the worker's fetch handler, catch a failed `POST` to `/api/`, put `await request.clone().json()` into the outbox and answer `new Response(JSON.stringify({ queued: true }), { status: 202 })`. The page must still read `queued` and tell the user.
- **No JavaScript**: the form keeps its `action` and `method`, so it still posts normally when the script fails; only the offline queue is lost.

## Pitfalls

- `navigator.onLine === true` only means a network interface is up, not that the server is reachable (captive portals, dead Wi-Fi). Always try the request; never gate on `onLine` alone.
- Background Sync gives up after a few attempts (Chrome: three) and each `sync` event has a time limit. The page fallback is what eventually empties the queue, so keep it even in Chromium.
- A session can expire while a request waits. A `401` is a 4xx and gets dropped above; if that matters, treat `401` as retryable, keep the item and send the user to sign in before replaying.
- Do not queue payments, deletes or anything whose meaning changes with time without asking the user again on replay.
- The outbox holds personal data on the device. Clear it on sign-out, and never queue requests with an `Authorization` header copied in.
- Test the sync path from DevTools > Application > Service workers ("Sync" field, tag `outbox`) and watch Background services > Background sync; `web-pwa-testing-and-audit`.

## Related skills

- `web-pwa-service-worker-offline`
- `web-pwa-storage`
- `web-form-submit-with-fetch`
- `web-form-validation`
- `web-ui-toast-notifications`
- `web-pwa-testing-and-audit`
