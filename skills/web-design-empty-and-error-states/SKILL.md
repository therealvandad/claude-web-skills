---
name: web-design-empty-and-error-states
description: Build the non-happy-path screens with Tailwind: empty state (no data, no search results), inline and full-page errors, offline banner and 404 page, each with icon, clear copy and one primary action. Use whenever a user asks for a "no results" message, a 404 page, an error page, "what to show when the list is empty", or an offline notice.
---

# Empty and error states

Every list, search and fetch has four outcomes: data, nothing, failure, and no network. Designers ship the first; users meet the other three in their first session. A good state answers three questions in order: what happened, why or what it means, and what to do now, with exactly one primary action. The visual pattern is the same for all four (icon, heading, one sentence, button), so build it once and change the words.

## Pattern

```html
<!-- 1. Empty state (no data yet). Centered, bounded width, dashed container signals "this fills up". -->
<section class="flex min-h-80 flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 p-8 text-center dark:border-gray-700"
         aria-labelledby="empty-title">
  <span class="flex size-12 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-300">
    <svg class="size-6" aria-hidden="true"><use href="#i-folder-plus"/></svg>
  </span>
  <h2 id="empty-title" class="mt-4 text-base font-semibold text-gray-900 dark:text-gray-100">No projects yet</h2>
  <p class="mt-1 max-w-xs text-sm text-gray-600 dark:text-gray-400">
    Projects keep your files, tasks and people in one place. Create your first one to get started.
  </p>
  <a href="/projects/new" class="mt-5 inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
    <svg class="size-4" aria-hidden="true"><use href="#i-plus"/></svg> New project
  </a>
</section>

<!-- 2. No search results: echo the query, offer the way out. role=status so the change is announced. -->
<div role="status" class="py-12 text-center">
  <p class="font-medium text-gray-900 dark:text-gray-100">No results for "<span data-query>quarterly repot</span>"</p>
  <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Check the spelling or try fewer words.</p>
  <button type="button" data-clear class="mt-4 text-sm font-medium text-indigo-600 hover:underline">Clear search</button>
</div>

<!-- 3. Inline fetch error: stays where the content would be, keeps the rest of the page usable. -->
<div role="alert" class="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm dark:border-red-900 dark:bg-red-950">
  <svg class="mt-0.5 size-5 shrink-0 text-red-600" aria-hidden="true"><use href="#i-alert"/></svg>
  <div class="flex-1">
    <p class="font-medium text-red-800 dark:text-red-200">Could not load your invoices</p>
    <p class="mt-0.5 text-red-700 dark:text-red-300">The server did not respond. Your data is safe.</p>
  </div>
  <button type="button" data-retry class="rounded-md px-2 py-1 font-medium text-red-800 hover:bg-red-100 dark:text-red-200 dark:hover:bg-red-900">Retry</button>
</div>

<!-- 4. Offline banner: fixed at the top, shown/hidden by the online/offline events. -->
<div id="offline" hidden role="status" class="fixed inset-x-0 top-0 z-50 bg-amber-500 px-4 py-2 text-center text-sm font-medium text-amber-950">
  You are offline. Changes will sync when the connection returns.
</div>

<!-- 5. 404 page: a full page, but still has the site header and a way home. -->
<main class="mx-auto flex min-h-[70vh] max-w-xl flex-col items-center justify-center px-4 text-center">
  <p class="text-sm font-semibold text-indigo-600">404</p>
  <h1 class="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl dark:text-gray-50">Page not found</h1>
  <p class="mt-3 text-gray-600 dark:text-gray-400">The link may be old, or the page was moved. Nothing you did caused this.</p>
  <div class="mt-6 flex flex-wrap justify-center gap-3">
    <a href="/" class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">Go to homepage</a>
    <a href="/search" class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800">Search the site</a>
  </div>
</main>
```

```js
const banner = document.getElementById('offline');
const sync = () => { banner.hidden = navigator.onLine; };
addEventListener('online', sync);
addEventListener('offline', sync);
sync();
```

Copy rules: heading says *what* in plain words ("No projects yet", not "Empty"); body says *why* or *what it means* in one sentence; the button says the verb ("New project", "Retry", "Clear search"). Never blame the user, never show raw error codes as the headline, and keep the 404 page on the normal layout so navigation still works.

## Variations

- **First-run vs filtered empty.** A brand-new account gets the inviting version above; a list emptied by filters gets the compact "no results" version with a "Clear filters" link. Decide which one to show from whether any filter is active.
- **Skeleton to empty.** Render the skeleton while fetching, then swap to the empty state only after the response; never show "No items" during loading. See `web-ui-skeleton-and-loading`.
- **Error with details.** Add a `<details class="mt-2 text-xs">` with the request id for support, collapsed by default.
- **Illustrated.** Replace the icon circle with an SVG illustration at `max-w-48`; keep it decorative (`aria-hidden`) and `dark:opacity-80`.

## Pitfalls

- A 404 served with HTTP 200 looks fine but poisons search indexes; the server must return a real 404 status (see `web-ship-static-hosting` for per-host config).
- `role="alert"` interrupts screen readers; use it for errors only. Empty and offline states use `role="status"` (polite).
- Centering with `min-h-screen` inside a page that already has a header pushes the footer off screen; use `min-h-[60vh]` or a flex column on the page shell.
- An empty state with three buttons is a menu, not a state. One primary action; a second only as a text link.
- Retry buttons that re-run a failed request instantly can hammer a struggling server; disable the button and show "Retrying..." for at least a second.
- Hard-coding the user's query into HTML via `innerHTML` is an XSS hole; set it with `textContent`.

## Related skills

- `web-ui-skeleton-and-loading`
- `web-js-errors-and-logging`
- `web-js-fetch-and-apis`
- `web-ship-launch-checklist`
- `web-ui-toast-notifications`
