---
name: web-pwa-service-worker-offline
description: Build a production service worker for a PWA - a build-time precache list with hashes, named strategies (cache-first, network-first with timeout, stale-while-revalidate) routed by request type, separate caches with trimming, navigation preload and an offline page. Use when a user says "work offline", "offline mode", "cache the app shell", "PWA service worker" or "load instantly on repeat visits".
---

# Service worker for offline PWAs

`web-perf-caching-and-service-worker` gives you the 25-line worker that is enough for a brochure site. An installable app needs more: a precache list generated at build time (so you never ship a stale hard-coded list), one strategy per kind of request, caches that do not grow forever, and a worker that stays correct across deploys. The structure below is the whole thing; everything else in the PWA group plugs into it.

## Pattern

Generate the precache list at build time so the worker always matches the deployed files:

```js
// scripts/precache.mjs - node scripts/precache.mjs  (run after Tailwind build and hashing)
import { readdirSync, statSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";
const walk = (dir) => readdirSync(dir).flatMap((n) => { const p = join(dir, n); return statSync(p).isDirectory() ? walk(p) : [p]; });
const files = walk("dist").filter((p) => /\.(html|css|js|woff2|svg|webmanifest)$/.test(p) && !p.endsWith("sw.js"));
const entries = files.map((p) => ({ url: "/" + p.replace(/^dist[\\/]/, "").replace(/\\/g, "/"), rev: createHash("md5").update(readFileSync(p)).digest("hex").slice(0, 8) }));
const version = createHash("md5").update(JSON.stringify(entries)).digest("hex").slice(0, 8);
let sw = readFileSync("src/sw.js", "utf8");
sw = sw.replace("__PRECACHE__", JSON.stringify(entries)).replace("__VERSION__", version);
writeFileSync("dist/sw.js", sw);
```

```js
// src/sw.js  -> dist/sw.js (at the site root)
const VERSION = "__VERSION__";
const PRECACHE = __PRECACHE__;            // [{ url, rev }]
const CACHES = { pre: `pre-${VERSION}`, pages: "pages", api: "api", img: "img" };
const OFFLINE = "/offline.html";

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHES.pre).then((c) =>
    Promise.all(PRECACHE.map(({ url, rev }) =>
      fetch(`${url}?__rev=${rev}`, { cache: "reload" }).then((r) => { if (!r.ok) throw new Error(url); return c.put(url, r); })))));
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k.startsWith("pre-") && k !== CACHES.pre).map((k) => caches.delete(k)));
    if (self.registration.navigationPreload) await self.registration.navigationPreload.enable();
    await self.clients.claim();
  })());
});

const cacheFirst = async (req, name) => (await caches.match(req)) ?? putAndReturn(req, name, await fetch(req));
const staleWhileRevalidate = async (req, name) => {
  const hit = await caches.match(req);
  const refresh = fetch(req).then((res) => putAndReturn(req, name, res)).catch(() => hit);
  return hit ?? refresh;
};
const networkFirst = async (req, name, ms = 3000, preload) => {
  const timer = new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), ms));
  try { return putAndReturn(req, name, await Promise.race([preload ?? fetch(req), timer])); }
  catch { return (await caches.match(req)) ?? (req.mode === "navigate" ? caches.match(OFFLINE) : Response.error()); }
};
async function putAndReturn(req, name, res) {
  if (res && res.ok && res.type !== "opaque") { const c = await caches.open(name); c.put(req, res.clone()); trim(name, 60); }
  return res;
}
async function trim(name, max) {                         // keep runtime caches bounded
  const c = await caches.open(name); const keys = await c.keys();
  if (keys.length > max) { await c.delete(keys[0]); trim(name, max); }
}

self.addEventListener("fetch", (e) => {
  const { request } = e; const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== location.origin) return;
  if (PRECACHE.some((p) => p.url === url.pathname)) return e.respondWith(cacheFirst(request, CACHES.pre));
  if (request.mode === "navigate") return e.respondWith(networkFirst(request, CACHES.pages, 3000, e.preloadResponse));
  if (url.pathname.startsWith("/api/")) return e.respondWith(networkFirst(request, CACHES.api, 5000));
  if (request.destination === "image") return e.respondWith(staleWhileRevalidate(request, CACHES.img));
  if (/\.[a-f0-9]{8}\.(css|js|woff2)$/.test(url.pathname)) e.respondWith(cacheFirst(request, CACHES.pre));
});

self.addEventListener("message", (e) => { if (e.data?.type === "SKIP_WAITING") self.skipWaiting(); });
```

```html
<script type="module">
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js", { updateViaCache: "none" })
      .catch((err) => console.warn("sw failed", err));
  }
</script>
```

`/offline.html` is a precached, self-contained page (inline the small amount of CSS it needs, no external fonts) that explains the situation and offers a retry button: `web-design-empty-and-error-states`.

## Variations

- **App shell for a client-rendered app**: precache `/index.html` and respond to every navigation with it (`caches.match("/index.html")`), then let the page fetch data. Only do this when the HTML truly never changes between routes.
- **Offline-first data**: for an app that must open offline, invert the API route to `staleWhileRevalidate` and post a `{type:"api-updated"}` message to clients so they re-render (`web-js-state-and-render`).
- **Large media**: do not cache video or audio through `cache.put`; range requests (`Range:` header) fail from the cache. Let them hit the network or store files deliberately in IndexedDB (`web-pwa-storage`).
- **Cross-origin assets** (a CDN font): responses are `opaque` with status 0 and cannot be inspected; precache them only with `mode: "cors"` on a server that sends `Access-Control-Allow-Origin`, or self-host (`web-perf-fonts`).

## Pitfalls

- `cache.addAll` fails the whole install if one URL 404s, which is correct (a half-cached shell is worse) but means a typo in the precache list bricks the update silently. Watch the Console for the install error during development.
- Never precache `sw.js` itself or cache it with a long `Cache-Control`; the browser must be able to byte-compare the new one. `updateViaCache: "none"` also stops the HTTP cache from feeding the import graph.
- `clients.claim()` plus `skipWaiting()` on install means a tab can switch workers mid-session and load a new hashed CSS against old HTML. The pattern above waits; the "update available" flow is in `web-pwa-update-flow`.
- Caching `POST` or anything with `Authorization` is a data leak on shared devices; the `method !== "GET"` guard is doing real work.
- `caches.match(req)` ignores `Vary` by default and respects the query string. For images with cache-busting params, match with `{ ignoreSearch: true }`.
- Testing with "Update on reload" ticked hides lifecycle bugs. Untick it before testing the install and update paths (`web-pwa-testing-and-audit`).

## Related skills

- `web-perf-caching-and-service-worker`
- `web-pwa-update-flow`
- `web-pwa-offline-forms`
- `web-pwa-storage`
- `web-design-empty-and-error-states`
- `web-ship-static-hosting`
