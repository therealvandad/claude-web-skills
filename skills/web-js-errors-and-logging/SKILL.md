---
name: web-js-errors-and-logging
description: Set up error handling for a plain-JavaScript site - where to try/catch, custom error classes, global `error` and `unhandledrejection` handlers, a user-facing error banner, a `log` helper with levels and a reporting endpoint. Use whenever a user says "the page silently breaks", "catch all errors", "show an error message", "log errors to a server", or "remove console.logs before launch".
---

# Errors and logging: fail visibly, log usefully

An uncaught error in a module stops that module cold while the rest of the page looks fine, so users see a dead button and you see nothing. The strategy: **catch at boundaries** (event handlers, fetch calls, feature init), not around every line; **rethrow or wrap** with context where you cannot handle; register **global handlers** as the last net that shows a generic message and reports the stack; and route all output through a tiny `log` module so production can silence `debug` and ship `error` to an endpoint without touching call sites.

## Pattern

```html
<!-- generic error UI, present in the HTML so the global handler never has to build markup -->
<div data-js="error-banner" role="alert" hidden
     class="fixed inset-x-0 top-0 z-50 flex items-center justify-between gap-4 bg-red-600 px-4 py-2 text-white">
  <span data-js="error-message">Something went wrong.</span>
  <button type="button" data-js="error-dismiss" class="rounded px-2 py-1 hover:bg-red-700 focus-visible:outline-2">Dismiss</button>
</div>
```

```js
// /js/lib/log.js
const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };
const isProd = location.hostname !== 'localhost' && !location.hostname.endsWith('.test');
let threshold = LEVELS[isProd ? 'warn' : 'debug'];
const REPORT_URL = '/api/client-errors';       // set to null to disable reporting
const seen = new Set();                          // dedupe identical reports per page load

export const log = Object.fromEntries(Object.keys(LEVELS).map((level) => [level, (...args) => emit(level, args)]));
export const setLogLevel = (level) => { threshold = LEVELS[level]; };

function emit(level, args) {
  if (LEVELS[level] < threshold) return;
  console[level === 'debug' ? 'log' : level](`[${level}]`, ...args);
  if (level === 'error' && REPORT_URL) report(args);
}

function report(args) {
  const error = args.find((a) => a instanceof Error);
  const payload = {
    message: error?.message ?? args.map(String).join(' '),
    name: error?.name,
    stack: error?.stack?.slice(0, 2000),
    url: location.href,
    ua: navigator.userAgent,
    at: new Date().toISOString(),
  };
  const key = payload.name + payload.message;
  if (seen.has(key)) return;
  seen.add(key);
  try {
    navigator.sendBeacon?.(REPORT_URL, new Blob([JSON.stringify(payload)], { type: 'application/json' }));
  } catch { /* reporting must never throw */ }
}
```

```js
// /js/lib/errors.js
import { log } from './log.js';

/** Errors with a message safe to show users; everything else shows a generic one. */
export class UserFacingError extends Error {
  constructor(message, { cause } = {}) { super(message, { cause }); this.name = 'UserFacingError'; }
}

const banner = document.querySelector('[data-js="error-banner"]');
export function showError(error, fallback = 'Something went wrong. Please try again.') {
  log.error(error);
  if (!banner) return;
  banner.querySelector('[data-js="error-message"]').textContent =
    error instanceof UserFacingError ? error.message : fallback;
  banner.hidden = false;
  banner.querySelector('[data-js="error-dismiss"]').focus();
}
banner?.querySelector('[data-js="error-dismiss"]').addEventListener('click', () => { banner.hidden = true; });

/** Last net: anything that escaped a boundary. Register once, early. */
export function installGlobalHandlers() {
  window.addEventListener('error', (event) => {
    if (event.target !== window) {                                 // <img>/<script> load failures
      log.warn('resource failed', event.target.src ?? event.target.href); return;
    }
    showError(event.error ?? new Error(event.message));
  }, true);
  window.addEventListener('unhandledrejection', (event) => {
    event.preventDefault();                                        // keep the console clean; we log it
    showError(event.reason instanceof Error ? event.reason : new Error(String(event.reason)));
  });
}

/** Wrap an async handler so a thrown error becomes UI instead of an unhandled rejection. */
export const guarded = (fn) => async (...args) => {
  try { return await fn(...args); } catch (error) { showError(error); }
};
```

```js
// usage at a boundary
import { guarded, UserFacingError } from './lib/errors.js';
import { request, HttpError } from './lib/api.js';

form.addEventListener('submit', guarded(async (event) => {
  event.preventDefault();
  try {
    await request(form.action, { method: 'POST', body: new FormData(form) });
  } catch (error) {
    if (error instanceof HttpError && error.status === 409)
      throw new UserFacingError('That email is already registered.', { cause: error });
    throw error;                                                   // generic banner + report
  }
}));
```

## Variations

- **Inline instead of banner**: for forms, write the message into the field's `aria-describedby` element (see `web-form-validation`) and reserve the banner for errors with no natural home.
- **Offline**: listen to `window` `offline`/`online` and show a persistent, non-red notice; a `TypeError` from fetch while `!navigator.onLine` should say "You're offline", not "Something went wrong".
- **Feature isolation**: wrap each feature's `init(root)` in try/catch at the entry (see `web-js-modules-and-structure`) so one broken widget does not kill the page.
- **Reporting services**: the `report()` payload shape is close to what Sentry-style endpoints accept; swap `REPORT_URL` or add a sampling rate (`Math.random() < 0.1`) on busy sites.

## Pitfalls

- Empty `catch {}` blocks hide bugs for months. At minimum `log.warn` with context; swallow only when the fallback behaviour is genuinely correct (the reporting beacon above).
- `catch (e) { throw new Error('failed') }` destroys the original stack. Use `new Error('context', { cause: e })` and log `error.cause`.
- Global handlers receive minified or cross-origin scripts as "Script error." with no stack; serve your own scripts with `crossorigin="anonymous"` and matching CORS headers to get real messages.
- Showing `error.message` to users leaks internals ("Cannot read properties of undefined"). Only `UserFacingError` messages are displayed; everything else gets the generic text.
- `console.log` left in production leaks data and slows hot paths. Route through `log.debug` (silenced in prod) and grep for raw `console.` before launch (`web-ship-launch-checklist`).
- Never `alert()` for errors: it blocks the thread, cannot be styled, and is suppressed in some embedded contexts.

## Related skills

- `web-js-fetch-and-apis`
- `web-form-validation`
- `web-design-empty-and-error-states`
- `web-ui-toast-notifications`
- `web-ship-launch-checklist`
