---
name: web-pwa-update-flow
description: Ship PWA updates safely - detect a waiting service worker, show an accessible "new version available" toast, send SKIP_WAITING on click and reload every tab once on controllerchange, plus periodic update checks for long-lived tabs. Use when a user says "users see the old version", "update available", "refresh to update", "skipWaiting", "new service worker not activating" or "PWA won't update".
---

# Service worker update flow

A new service worker installs in the background and then waits: it only takes over when every tab using the old one is closed. A standalone PWA is rarely closed, so without a flow users run last month's version. Calling `skipWaiting()` unconditionally fixes that but swaps the worker under a running page, which can then load new hashed CSS or JS against old HTML. The middle path: let the new worker wait, tell the user, and switch plus reload only when they say so. Every browser with service workers supports this flow; nothing here needs a fallback beyond "no service worker, no toast".

## Pattern

The worker side is one listener (already in `web-pwa-service-worker-offline`). It must be in the new worker, because that is the one that receives the message:

```js
// sw.js - no skipWaiting() in install
self.addEventListener("message", (e) => { if (e.data?.type === "SKIP_WAITING") self.skipWaiting(); });
```

```html
<div id="update-toast" hidden
  class="fixed inset-x-4 bottom-[max(1rem,env(safe-area-inset-bottom))] z-50 mx-auto flex max-w-md flex-wrap items-center gap-3 rounded-lg bg-slate-900 p-4 text-sm text-white shadow-lg sm:inset-x-auto sm:right-4 dark:bg-slate-100 dark:text-slate-900">
  <p class="flex-1" data-msg></p>
  <button type="button" data-reload class="rounded-md bg-white px-3 py-1.5 font-medium text-slate-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white dark:bg-slate-900 dark:text-white dark:focus-visible:outline-slate-900">Reload</button>
  <button type="button" data-later class="rounded-md px-3 py-1.5 underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-current">Later</button>
</div>
<p id="update-live" role="status" class="sr-only"></p>
<script type="module">
  import { registerWithUpdates } from "/js/sw-update.js";
  registerWithUpdates();
</script>
```

```js
// /js/sw-update.js
const toast = document.querySelector("#update-toast");
const live = document.querySelector("#update-live");
let waiting = null;

export async function registerWithUpdates(url = "/sw.js") {
  if (!("serviceWorker" in navigator)) return;
  const hadController = Boolean(navigator.serviceWorker.controller); // false on the very first visit
  const reg = await navigator.serviceWorker.register(url, { updateViaCache: "none" });

  if (reg.waiting && hadController) show(reg.waiting);   // downloaded during an earlier visit
  reg.addEventListener("updatefound", () => {
    const sw = reg.installing;
    sw?.addEventListener("statechange", () => {
      // "installed" with an existing controller means update; without one it is the first install
      if (sw.state === "installed" && navigator.serviceWorker.controller) show(sw);
    });
  });

  let reloading = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadController || reloading) return;             // first install claiming the page: no reload
    reloading = true;
    location.reload();                                   // fires in every tab: all move to the new version
  });

  let lastCheck = Date.now();                            // long-lived tabs: check at most hourly on focus
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible" || Date.now() - lastCheck < 3_600_000) return;
    lastCheck = Date.now();
    reg.update().catch(() => {});                        // offline: try again next time
  });
}

function show(worker) {
  waiting = worker;
  toast.querySelector("[data-msg]").textContent = "A new version is available.";
  live.textContent = "A new version is available. Reload to update.";
  toast.hidden = false;
}

toast.querySelector("[data-reload]").addEventListener("click", () => {
  waiting?.postMessage({ type: "SKIP_WAITING" });       // worker activates, controllerchange reloads
});
toast.querySelector("[data-later]").addEventListener("click", () => { toast.hidden = true; });
```

"Later" keeps the worker waiting; it activates on its own once all tabs close, and the toast appears again on the next load because `reg.waiting` is set.

## Variations

- **Update on next navigation**: if the user dismissed the toast and the page has no unsaved input, intercept the next same-origin link click, send `SKIP_WAITING`, and let `controllerchange` reload to the link's URL (`location.href = link.href` instead of `reload()`).
- **Protect unsaved work in other tabs**: `controllerchange` reloads every tab. In tabs with a dirty form, show the toast ("Updated in another tab, reload when ready") instead of reloading; see `web-form-input-states`.
- **Show the version**: answer `{ type: "GET_VERSION" }` in the worker via `e.ports[0].postMessage(VERSION)` (page side: `new MessageChannel()`), and print "v1.4 to v1.5" plus a changelog link in the toast.
- **Forced security fix**: for one release, call `self.skipWaiting()` in `install`; the reload listener above still moves every open tab to it.

## Pitfalls

- `sw.js` served with a long `Cache-Control`, or cached by a CDN, means the browser never sees the new bytes. Send `Cache-Control: no-cache` for `sw.js` and keep `updateViaCache: "none"` (`web-perf-caching-and-service-worker`).
- Update detection is a byte comparison of `sw.js` and its `importScripts`. If only assets changed but `sw.js` did not, no update is found; inject a build hash or precache list into it on every deploy.
- Without the `reloading` flag, or with DevTools "Update on reload" ticked, you get reload loops. Test the flow with that box unticked.
- The first deploy that adds this flow must already contain the `SKIP_WAITING` listener, or the button in that release does nothing; users will pick it up when tabs close.
- A live region that is hidden when its text changes may not be announced, so the announcement goes to a separate always-present `role="status"` element. Do not auto-dismiss the toast or move focus to it.
- Never reload without asking while the user is typing; a mid-edit reload loses input and trust.

## Related skills

- `web-pwa-service-worker-offline`
- `web-perf-caching-and-service-worker`
- `web-ui-toast-notifications`
- `web-css-sticky-and-fixed`
- `web-pwa-testing-and-audit`
