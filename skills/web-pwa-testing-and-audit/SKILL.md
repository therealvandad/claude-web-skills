---
name: web-pwa-testing-and-audit
description: Test and audit a PWA - a dependency-free installability script (Lighthouse dropped its PWA category), a Playwright offline test, HTTPS for phones on the LAN, Android and iOS remote debugging, and unsticking stale clients. Use when a user says "test my PWA", "PWA audit", "debug service worker", "not installable", "works on desktop not phone" or "stuck on old version".
---

# Testing and auditing a PWA

A PWA fails in places a normal site does not: on a real phone, after install, offline, and on the second deploy. Desktop DevTools with "Update on reload" ticked hides most of those bugs. Lighthouse used to cover installability, but Lighthouse 12 (2024) removed the PWA category, so the checks now come from a small script, DevTools' Manifest panel, one automated offline test and a short manual run on real devices.

## Pattern

A no-dependency audit for any URL (Node 18+):

```js
// scripts/pwa-check.mjs - node scripts/pwa-check.mjs https://your-site.example
const base = new URL(process.argv[2] ?? "http://localhost:8080/");
const fails = [];
const check = (ok, msg) => { console.log(`${ok ? "PASS" : "FAIL"}  ${msg}`); if (!ok) fails.push(msg); };

const html = await (await fetch(base)).text();
check(base.protocol === "https:" || ["localhost", "127.0.0.1"].includes(base.hostname), "served over HTTPS");
const href = html.match(/<link[^>]+rel=["']manifest["'][^>]*>/i)?.[0].match(/href=["']([^"']+)/)?.[1];
check(Boolean(href), '<link rel="manifest"> in the page');
if (href) {
  const mUrl = new URL(href, base);
  const m = await (await fetch(mUrl)).json();
  const icons = m.icons ?? [];
  const sizes = icons.flatMap((i) => i.sizes?.split(" ") ?? []);
  check(Boolean(m.name || m.short_name), "manifest name or short_name");
  check(Boolean(m.id), "manifest id (stable app identity)");
  check(Boolean(m.start_url) && new URL(m.start_url, mUrl).origin === base.origin, "start_url on the same origin");
  check(["standalone", "fullscreen", "minimal-ui"].includes(m.display) || Boolean(m.display_override), "app-like display");
  check(sizes.includes("192x192") && sizes.includes("512x512"), "icons at 192 and 512");
  check(icons.some((i) => i.purpose?.includes("maskable")), "a maskable icon");
}
const swPath = html.match(/serviceWorker\.register\(\s*["']([^"']+)/)?.[1] ?? "/sw.js";
const sw = await fetch(new URL(swPath, base));
check(sw.ok && /javascript/.test(sw.headers.get("content-type") ?? ""), `${swPath} served as JavaScript`);
const cc = sw.headers.get("cache-control") ?? "none";
check(/no-cache|no-store|max-age=0\b/.test(cc), `${swPath} not long-cached (Cache-Control: ${cc})`);
check((await fetch(new URL("/offline.html", base))).ok, "/offline.html exists");
process.exitCode = fails.length ? 1 : 0;
```

An automated offline test with pinned Playwright:

```js
// tests/offline.spec.js
// npm i -D @playwright/test@1.49.1 && npx playwright install chromium && npx playwright test
import { test, expect } from "@playwright/test";
const ORIGIN = "http://localhost:8080";

test("app opens offline after the first visit", async ({ page, context }) => {
  await page.goto(ORIGIN + "/");
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();                                    // now controlled by the worker
  await context.setOffline(true);
  await page.reload();
  await expect(page.locator("main")).toBeVisible();
  // Also proves the network is really off for the worker: an uncached page must show the offline page
  await page.goto(ORIGIN + "/never-visited");
  await expect(page.getByRole("heading", { name: /offline/i })).toBeVisible();
});
```

Manual pass before each release, on real devices:

- **Android Chrome**: install from the menu, open from the home screen, check icon and splash, switch to airplane mode and relaunch. Debug from desktop at `chrome://inspect` with USB debugging on.
- **iOS Safari**: Share > Add to Home Screen, launch offline. The home-screen app has storage separate from Safari tabs. Debug with a Mac: Settings > Apps > Safari > Advanced > Web Inspector on the phone, then Safari's Develop menu. Without a Mac, use a cloud real-device service.
- **Desktop Chrome or Edge**: install, check the window title and `display`, test file handlers and shortcuts, uninstall from the app menu.
- **Update path**: deploy a changed build with the app open, confirm the toast from `web-pwa-update-flow` appears, reload, check the new version is served offline too.
- **Firefox and Safari desktop**: no install-prompt event exists; confirm the site works fully as a website with the same worker.

## Variations

- **Phone on the local network**: service workers need HTTPS, and `http://192.168.x.x` is not a secure context. For Android use `adb reverse tcp:8080 tcp:8080` and open `http://localhost:8080` on the phone; for iOS run an HTTPS tunnel (`cloudflared tunnel --url http://localhost:8080`) or a local CA with `mkcert` installed on the device.
- **Performance and accessibility**: still run Lighthouse for those: `npx lighthouse@12.2.1 https://your-site.example --only-categories=performance,accessibility,best-practices --view` (`web-perf-web-vitals`).
- **CI**: run `pwa-check.mjs` against the preview deploy URL and fail the build on a non-zero exit code; run the Playwright test against a local `npx serve@14.2.4 dist`.

## Pitfalls

- Where to look per browser: Chrome/Edge DevTools > Application (Manifest with installability errors, Service workers, Storage, Background services) and `chrome://serviceworker-internals`; Firefox `about:debugging#/runtime/this-firefox`; Safari Develop > Service Workers.
- Untick "Update on reload" and "Bypass for network" before testing install and update; they skip the waiting phase that real users hit.
- A client stuck on an old worker: send `Clear-Site-Data: "cache", "storage"` from a `/reset` URL and link support users to it, or ship the kill-switch worker from `web-perf-caching-and-service-worker`. Hard refresh does not remove a service worker.
- GitHub Pages sends `max-age=600` for every file, so the `sw.js` header check fails there. That is acceptable with `updateViaCache: "none"`, which makes the browser ignore the HTTP cache for the worker script.
- Chrome's install criteria change over time and differ from Edge and Samsung Internet. Trust the Manifest panel's "Installability" messages over blog checklists.
- Testing only in an incognito window hides persistence and quota problems: storage there is tiny and wiped on close.

## Related skills

- `web-pwa-manifest`
- `web-pwa-service-worker-offline`
- `web-pwa-update-flow`
- `web-perf-caching-and-service-worker`
- `web-perf-web-vitals`
- `web-ship-launch-checklist`
