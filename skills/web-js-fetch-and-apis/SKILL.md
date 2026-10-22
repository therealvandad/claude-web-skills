---
name: web-js-fetch-and-apis
description: Write a reusable `api.js` wrapper around fetch with async/await, JSON parsing, typed errors, AbortController timeouts, cancellation, retries with backoff, and loading/error UI hooks. Use whenever a user says "call an API", "fetch data", "load JSON", "the request hangs", "retry on failure", "cancel the request", or "handle fetch errors" on a plain-JavaScript site.
---

# Fetch and APIs: a wrapper that fails loudly and gives up on time

`fetch()` has three traps that bite every project: it does **not** reject on HTTP 4xx/5xx, it has **no timeout**, and it throws different error shapes for network failure, abort and bad JSON. A 30-line wrapper fixes all three once so every call site can be a plain `try/await/catch`. Keep retries for idempotent reads only, and always give the user a visible state (loading, error, retry).

## Pattern

```html
<section data-js="users" aria-busy="false">
  <p data-js="status" role="status" class="text-sm text-gray-500"></p>
  <ul data-js="list" class="divide-y"></ul>
  <button type="button" data-js="retry" class="rounded bg-gray-900 px-3 py-1.5 text-white" hidden>Retry</button>
</section>
```

```js
// /js/api.js
export class HttpError extends Error {
  constructor(response, body) {
    super(`HTTP ${response.status} ${response.statusText}`.trim());
    this.name = 'HttpError';
    this.status = response.status;
    this.body = body;            // parsed JSON or text from the server, if any
  }
}

/**
 * request(url, { method, json, timeout, signal, retries, headers })
 * - throws HttpError for non-2xx, TimeoutError on timeout, AbortError if you cancel
 * - returns parsed JSON (or text if the response is not JSON, or null for 204)
 */
export async function request(url, { json, timeout = 10_000, signal, retries = 0, headers = {}, ...init } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(new DOMException('Timed out', 'TimeoutError')), timeout);
  signal?.addEventListener('abort', () => controller.abort(signal.reason), { once: true });

  const options = { ...init, headers: { Accept: 'application/json', ...headers }, signal: controller.signal };
  if (json !== undefined) {
    options.method ??= 'POST';
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(json);
  }

  try {
    const response = await fetch(url, options);
    const body = await parseBody(response);
    if (!response.ok) throw new HttpError(response, body);
    return body;
  } catch (error) {
    const retryable = retries > 0 && (options.method ?? 'GET') === 'GET'
      && (error.name === 'TypeError' || error.name === 'TimeoutError' || error.status >= 500);
    if (!retryable) throw error;
    await sleep(2 ** (3 - retries) * 300 + Math.random() * 200);   // 300ms, 600ms, 1200ms + jitter
    return request(url, { json, timeout, signal, retries: retries - 1, headers, ...init });
  } finally {
    clearTimeout(timer);
  }
}

async function parseBody(response) {
  if (response.status === 204) return null;
  const type = response.headers.get('content-type') ?? '';
  return type.includes('json') ? response.json() : response.text();
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
```

```js
// /js/users.js
import { request, HttpError } from './api.js';

const root = document.querySelector('[data-js="users"]');
const status = root.querySelector('[data-js="status"]');
const list = root.querySelector('[data-js="list"]');
const retry = root.querySelector('[data-js="retry"]');
let inflight;                                   // cancel a previous load if a new one starts

async function loadUsers() {
  inflight?.abort();
  inflight = new AbortController();
  root.setAttribute('aria-busy', 'true');
  status.textContent = 'Loading…';
  retry.hidden = true;
  try {
    const users = await request('/api/users', { signal: inflight.signal, retries: 2 });
    list.replaceChildren(...users.map((u) => Object.assign(document.createElement('li'), { textContent: u.name })));
    status.textContent = users.length ? '' : 'No users yet.';
  } catch (error) {
    if (error.name === 'AbortError') return;    // superseded, say nothing
    status.textContent = messageFor(error);
    retry.hidden = false;
    console.error(error);                       // keep the stack for debugging
  } finally {
    root.setAttribute('aria-busy', 'false');
  }
}

function messageFor(error) {
  if (error.name === 'TimeoutError') return 'The server took too long. Check your connection and try again.';
  if (error instanceof HttpError) return error.status === 404 ? 'Not found.' : `Server error (${error.status}).`;
  if (error.name === 'TypeError') return 'Network error. Are you offline?';
  return 'Something went wrong.';
}

retry.addEventListener('click', loadUsers);
loadUsers();
```

## Variations

- **Mutations**: `await request('/api/items', { json: { name } })` posts JSON; for `FormData` pass `{ method: 'POST', body: formData }` and omit `json` so the browser sets the multipart boundary. See `web-form-submit-with-fetch`.
- **Parallel loads**: `const [a, b] = await Promise.all([request('/a'), request('/b')])`; use `Promise.allSettled` when one failure must not sink the others.
- **Cancel on navigation**: pass `AbortSignal.any([inflight.signal, AbortSignal.timeout(5000)])` to combine user cancellation with a per-call deadline, or abort all in-flight requests on `pagehide`.
- **Auth**: inject headers once by wrapping: `const api = (url, o) => request(API_BASE + url, { ...o, headers: { Authorization: \`Bearer ${token}\`, ...o?.headers } })`.

## Pitfalls

- `response.ok` is only true for 200-299; forgetting to check it is the number one cause of "the data is undefined" bugs.
- Calling `response.json()` on an HTML error page throws a `SyntaxError` that hides the real status. Parse by `content-type` as above.
- Retrying POSTs can duplicate orders or emails. Retry only GET (or send an idempotency key the server honours).
- `AbortSignal.timeout()` exists but produces an error you cannot distinguish from user cancellation unless you check `error.name`; the wrapper passes a `TimeoutError` reason for that.
- CORS failures surface as a generic `TypeError: Failed to fetch` with no status. Look at the browser console, not your catch block, and fix the server's `Access-Control-Allow-Origin`.
- Never leave a request without a visible loading state and a `role="status"` message; silent failures are the worst UX.

## Related skills

- `web-form-submit-with-fetch`
- `web-js-errors-and-logging`
- `web-js-state-and-render`
- `web-ui-skeleton-and-loading`
- `web-design-empty-and-error-states`
