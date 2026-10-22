---
name: web-pwa-install-prompt
description: Add a custom "Install app" button driven by `beforeinstallprompt` (Chromium only), with the iOS "Add to Home Screen" instructions as a fallback, detection of already-installed state, and a dismissal that stays remembered. Use when a user says "install button", "add to home screen", "install banner", "prompt users to install the PWA" or "the install popup does not show".
---

# Custom install prompt

Chromium fires `beforeinstallprompt` when the manifest and install criteria are satisfied; you stash the event, show your own button at a sensible moment, and call `prompt()` from a click. Firefox desktop and every browser on iOS never fire it: iOS installs only through Safari's Share sheet (and, since iOS 16.4, through the menu of other browsers), so the same component must switch to short written instructions there. Ask after the user has done something useful, never on first paint, and remember a "no" for a couple of weeks.

## Pattern

```html
<div data-install hidden class="fixed inset-x-4 bottom-4 z-40 mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-4 shadow-lg sm:inset-x-auto sm:right-6 dark:border-slate-700 dark:bg-slate-900"
     role="region" aria-label="Install app">
  <div class="flex items-start gap-3">
    <img src="/icons/icon-192.png" alt="" width="48" height="48" class="size-12 rounded-lg">
    <div class="min-w-0 flex-1">
      <p class="font-semibold text-slate-900 dark:text-slate-50">Install Fieldbook</p>
      <p data-install-copy class="mt-0.5 text-sm text-slate-600 dark:text-slate-300">Opens full screen and keeps working without signal.</p>
      <ol data-install-ios hidden class="mt-2 list-decimal space-y-1 pl-4 text-sm text-slate-600 dark:text-slate-300">
        <li>Tap the <span class="font-medium">Share</span> button in Safari's toolbar.</li>
        <li>Scroll and tap <span class="font-medium">Add to Home Screen</span>.</li>
        <li>Tap <span class="font-medium">Add</span>.</li>
      </ol>
    </div>
    <button data-install-dismiss type="button" aria-label="Not now" class="rounded-md p-1 text-slate-500 hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 dark:hover:bg-slate-800">&times;</button>
  </div>
  <button data-install-go type="button" class="mt-3 w-full rounded-lg bg-teal-700 px-4 py-2 font-medium text-white hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600">Install</button>
</div>
```

```js
// /js/install.js
import { local } from './storage.js';                     // web-js-storage

const panel = document.querySelector('[data-install]');
const go = panel.querySelector('[data-install-go]');
const iosSteps = panel.querySelector('[data-install-ios]');
const DISMISS_KEY = 'install-dismissed';
const DISMISS_TTL = 14 * 24 * 60 * 60 * 1000;             // ask again after two weeks
let deferredPrompt = null;

const isStandalone = () => matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
const isIOS = () => /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
const engaged = () => (local.read('visits', 0) >= 2);    // bumped in main.js on each load

function show(mode) {
  if (isStandalone() || local.read(DISMISS_KEY) || !engaged()) return;
  iosSteps.hidden = mode !== 'ios';
  go.hidden = mode === 'ios';                              // iOS has no programmatic install
  panel.hidden = false;
}

window.addEventListener('beforeinstallprompt', (e) => {   // Chromium only
  e.preventDefault();                                      // stop the mini-infobar; we show our own UI
  deferredPrompt = e;
  show('native');
});

go.addEventListener('click', async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();                                 // must run inside a user gesture
  const { outcome } = await deferredPrompt.userChoice;     // 'accepted' | 'dismissed'
  deferredPrompt = null;
  panel.hidden = true;
  if (outcome === 'dismissed') local.write(DISMISS_KEY, true, { ttl: DISMISS_TTL });
});

panel.querySelector('[data-install-dismiss]').addEventListener('click', () => {
  panel.hidden = true;
  local.write(DISMISS_KEY, true, { ttl: DISMISS_TTL });
});

window.addEventListener('appinstalled', () => {
  panel.hidden = true;
  local.remove(DISMISS_KEY);
  // analytics hook here (web-ship-analytics-and-privacy)
});

if (isIOS() && !isStandalone()) show('ios');               // Safari and iOS browsers: manual steps
```

Count visits in your main module so `engaged()` has something to read: `local.write('visits', local.read('visits', 0) + 1)`.

## Variations

- **Inline button in a settings page instead of a banner**: keep the button `hidden` until `beforeinstallprompt` fires, then reveal it; no dismissal logic needed because the user went looking for it.
- **Trigger after a success moment**: call `show('native')` from the handler that saves the user's first note or completes checkout, rather than on load. Keep `deferredPrompt` around; the event fires once per page load and stays valid until used.
- **Desktop Chrome and Edge**: the same event fires on desktop; the banner reads oddly there, so swap the copy to "Install as an app" and position it top-right.
- **Detect the launch surface** for analytics with `start_url` query parameters set in `web-pwa-manifest` (`?source=pwa`), rather than sniffing `display-mode` on every page.

## Pitfalls

- `prompt()` outside a user gesture rejects, and it can be called only once per event. After `userChoice` resolves, discard the event; the browser will fire a new one on a later load if criteria are still met.
- If the event never fires on Chromium, the manifest is the problem, not this script: check DevTools > Application > Manifest > Installability for the stated reason (`web-pwa-manifest`).
- Chromium also hides the prompt after the user dismissed it from the native UI a few times, with a cooldown of up to several months. Treat an absent event as "not now", not as a bug.
- iPadOS Safari reports a Mac user agent; the `maxTouchPoints` check above is what catches it.
- The banner is a `region`, not a `dialog`: do not trap focus or block scrolling for a suggestion. Keep it dismissible with a real button, and never cover the page's primary action on small screens (`web-css-sticky-and-fixed` for safe-area padding).
- Do not test installability in an Incognito window or with "Bypass for network" ticked; both suppress the event.

## Related skills

- `web-pwa-manifest`
- `web-pwa-app-icons-splash`
- `web-js-storage`
- `web-ui-toast-notifications`
- `web-css-sticky-and-fixed`
- `web-ship-analytics-and-privacy`
