---
name: web-perf-caching-and-service-worker
description: Set up HTTP caching for a static site - long-lived immutable hashed assets, short-lived HTML, the exact `_headers` / `vercel.json` / `netlify.toml` / `.htaccess` rules - and a minimal offline-capable service worker with a safe update strategy. Use when a user asks about "cache headers", "cache busting", "users see the old version", "make it work offline", "PWA", or "service worker".
---

# Caching and a minimal service worker

Correct caching makes the second page view nearly free and makes deploys safe at the same time: HTML is cached for seconds (so a deploy shows up), everything HTML links to carries a content hash in its filename and is cached for a year as `immutable`. A service worker is optional; add one only for offline support or an installable app, and keep it small, because a buggy service worker is the one thing a user cannot hard-refresh away.

## Pattern

Hash the built assets at build time so filenames change when content changes (cross-platform Node, no bundler):

```js
// scripts/hash.mjs - node scripts/hash.mjs  (run after the Tailwind build)
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, renameSync, readdirSync } from "node:fs";
const hashed = {};
for (const f of ["dist/output.css", "dist/js/main.js"]) {
  const h = createHash("sha256").update(readFileSync(f)).digest("hex").slice(0, 8);
  const out = f.replace(/(\.\w+)$/, `.${h}$1`);
  renameSync(f, out); hashed[f.replace("dist", "")] = out.replace("dist", "");
}
for (const page of readdirSync("dist").filter(n => n.endsWith(".html"))) {
  let html = readFileSync(`dist/${page}`, "utf8");
  for (const [from, to] of Object.entries(hashed)) html = html.replaceAll(from, to);
  writeFileSync(`dist/${page}`, html);
}
```

Headers per host (HTML short, hashed assets forever):

```text
# Netlify and Cloudflare Pages: dist/_headers
/*
  Cache-Control: public, max-age=0, must-revalidate
/*.css
  Cache-Control: public, max-age=31536000, immutable
/js/*
  Cache-Control: public, max-age=31536000, immutable
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=2592000
```

```json
// Vercel: vercel.json
{ "headers": [
  { "source": "/(.*)\\.html", "headers": [{ "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }] },
  { "source": "/(.*)\\.(css|js|woff2)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] }
] }
```

GitHub Pages does not allow custom headers (it sends `max-age=600` for everything); hashed filenames still give correct behaviour there. Apache: `<FilesMatch "\.(css|js|woff2)$"> Header set Cache-Control "public, max-age=31536000, immutable" </FilesMatch>` in `.htaccess`.

A minimal service worker: precache the shell, network-first for HTML, cache-first for hashed assets, offline fallback page.

```js
// sw.js (must live at the site root so its scope covers the whole site)
const VERSION = "v3"; // bump on every deploy; the hash script can inject this
const SHELL = ["/", "/offline.html", "/dist/output.css"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const { request } = e;
  if (request.method !== "GET" || !request.url.startsWith(self.location.origin)) return;
  if (request.mode === "navigate") {
    e.respondWith(fetch(request).catch(() => caches.match("/offline.html")));
    return;
  }
  e.respondWith(caches.match(request).then(hit => hit ?? fetch(request).then(res => {
    if (res.ok && /\.(css|js|woff2|png|webp|avif|svg)$/.test(new URL(request.url).pathname)) {
      const copy = res.clone(); caches.open(VERSION).then(c => c.put(request, copy));
    }
    return res;
  })));
});
```

```html
<script type="module">
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js");
</script>
```

## Variations

- **No offline needed**: skip the service worker entirely; HTTP caching plus hashed filenames gives 90 percent of the benefit with zero update risk.
- **Installable PWA**: add `manifest.webmanifest` (`name`, `start_url`, `display: "standalone"`, 192 and 512 px icons) and `<link rel="manifest" href="/manifest.webmanifest">`; the service worker above already satisfies the install criteria.
- **Stale-while-revalidate for images**: `Cache-Control: public, max-age=86400, stale-while-revalidate=604800` serves the cached copy instantly and refreshes in the background; use it for assets without hashes.
- **Show an "update available" toast**: listen for `navigator.serviceWorker.addEventListener("controllerchange", ...)` and offer a reload instead of the silent `skipWaiting()` above, see `web-ui-toast-notifications`.

## Pitfalls

- Caching HTML for a long time is how "I deployed but users still see the old site" happens. HTML: `max-age=0, must-revalidate`. Only hashed files get `immutable`.
- A hashed filename without `immutable` still works, but the browser may revalidate on reload; `immutable` skips even that.
- `sw.js` itself must never be cached long (`max-age=0`); the browser checks it on each navigation and byte-compares to detect updates.
- A service worker that caches HTML cache-first will serve stale pages forever. Keep navigations network-first.
- Registering the service worker at `/js/sw.js` limits its scope to `/js/`; keep it at the root.
- To remove a service worker in production, deploy one whose fetch handler is empty and which calls `self.registration.unregister()` in `activate`; simply deleting the file leaves the old worker running on every client for up to 24 h.
- Devtools "Disable cache" also bypasses the service worker only if "Bypass for network" is ticked; when debugging, use the Application panel to see what is actually cached.

## Related skills

- `web-ship-static-hosting`
- `web-ship-tailwind-production`
- `web-perf-css-and-js-loading`
- `web-perf-web-vitals`
- `web-design-empty-and-error-states` (the offline page)
- `web-ui-toast-notifications`
