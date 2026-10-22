---
name: web-ui-toast-notifications
description: Build a toast notification system: a stacked corner region, a `toast()` function with success/error/info variants, auto-dismiss with pause on hover, close button, screen-reader announcements via aria-live, and a queue cap. Use whenever a user asks for toasts, snackbars, "saved" messages, flash messages, alerts that disappear, or notification popups.
---

# Toast notifications

A toast is a short, non-blocking status message that appears in a corner and leaves on its own. The hard parts are not visual: making sure screen readers hear it (a live region that exists before the message arrives), not burying the user under ten toasts, letting them pause and dismiss, and never hiding something they must act on. One pre-rendered container plus a small `toast()` function covers all of it.

## Pattern

```html
<!-- Place once, near the end of <body>. It exists on load so assistive tech registers the live region. -->
<div id="toast-region" aria-live="polite" aria-atomic="false"
  class="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col items-center gap-2 sm:inset-x-auto sm:right-4 sm:items-end">
</div>

<template id="toast-template">
  <div role="status" data-toast
    class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl border bg-white p-4 text-sm text-gray-900 shadow-lg
           motion-safe:animate-[toast-in_.25s_ease-out] data-[closing]:motion-safe:animate-[toast-out_.2s_ease-in_forwards]
           dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
    <span data-icon class="mt-0.5 size-5 shrink-0" aria-hidden="true"></span>
    <p data-message class="flex-1 leading-5"></p>
    <button type="button" data-close aria-label="Dismiss"
      class="-m-1 rounded-md p-1 text-gray-500 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:hover:bg-gray-800">
      <svg class="size-4" viewBox="0 0 20 20" fill="currentColor"><path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/></svg>
    </button>
  </div>
</template>
```

```css
@keyframes toast-in  { from { opacity: 0; transform: translateY(12px) } }
@keyframes toast-out { to   { opacity: 0; transform: translateY(8px) } }
```

```js
const ICONS = {
  success: '<svg viewBox="0 0 20 20" fill="currentColor" class="text-green-600"><path fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.86-9.9a.75.75 0 1 0-1.22-.88l-2.96 4.1-1.33-1.33a.75.75 0 0 0-1.06 1.06l1.96 1.96a.75.75 0 0 0 1.14-.09l3.47-4.82Z" clip-rule="evenodd"/></svg>',
  error:   '<svg viewBox="0 0 20 20" fill="currentColor" class="text-red-600"><path fill-rule="evenodd" d="M18 10A8 8 0 1 1 2 10a8 8 0 0 1 16 0Zm-8-5a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5A.75.75 0 0 1 10 5Zm0 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd"/></svg>',
  info:    '<svg viewBox="0 0 20 20" fill="currentColor" class="text-indigo-600"><path fill-rule="evenodd" d="M18 10A8 8 0 1 1 2 10a8 8 0 0 1 16 0Zm-7-4a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM9 9a.75.75 0 0 0 0 1.5h.25v2.75a.75.75 0 0 0 1.5 0V9.75A.75.75 0 0 0 10 9H9Z" clip-rule="evenodd"/></svg>',
};
const MAX_VISIBLE = 4;
const region = document.getElementById('toast-region');
const template = document.getElementById('toast-template');

export function toast(message, { type = 'info', duration = 5000 } = {}) {
  const el = template.content.firstElementChild.cloneNode(true);
  el.querySelector('[data-message]').textContent = message;   // textContent: never inject HTML from data
  el.querySelector('[data-icon]').innerHTML = ICONS[type] ?? ICONS.info;
  if (type === 'error') { el.setAttribute('role', 'alert'); duration = Math.max(duration, 8000); }

  let remaining = duration, startedAt = Date.now(), timer;
  const start = () => { startedAt = Date.now(); timer = setTimeout(dismiss, remaining); };
  const pause = () => { clearTimeout(timer); remaining -= Date.now() - startedAt; };
  function dismiss() {
    clearTimeout(timer);
    el.dataset.closing = '';
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    reduce ? el.remove() : el.addEventListener('animationend', () => el.remove(), { once: true });
  }

  el.querySelector('[data-close]').addEventListener('click', dismiss);
  el.addEventListener('mouseenter', pause);
  el.addEventListener('mouseleave', start);
  el.addEventListener('focusin', pause);
  el.addEventListener('focusout', start);

  // Queue cap: drop the oldest when too many are showing
  while (region.querySelectorAll('[data-toast]').length >= MAX_VISIBLE) region.firstElementChild.remove();
  region.append(el);
  start();
  return { dismiss };
}

// Usage
// toast('Changes saved', { type: 'success' });
// toast('Could not reach the server', { type: 'error' });
```

Why this shape: the region is in the DOM at page load with `aria-live` so screen readers announce later insertions; a region injected together with its first message is often not read. Errors switch to `role="alert"` (assertive) and stay longer. Hover and keyboard focus pause the timer, satisfying WCAG 2.2.1 "timing adjustable" without disabling auto-dismiss.

## Variations

- **Top-right stack**: swap `bottom-4` for `top-4` and flip the keyframes to slide down. Keep toasts away from the primary navigation on mobile.
- **With an action** ("Undo"): add `<button data-action>` inside the template, pass `{ action: { label, onClick } }`, and bump `duration` to 10 s. Anything undoable belongs here; anything requiring a decision belongs in `web-ui-modal-dialog`.
- **Progress bar**: add `<div class="absolute inset-x-0 bottom-0 h-0.5 origin-left bg-current motion-safe:animate-[shrink_var(--d)_linear_forwards]">` and set `el.style.setProperty('--d', duration + 'ms')`; pause with `animation-play-state: paused` on hover.
- **Coloured variants**: `border-l-4 border-green-500` / `border-red-500` instead of icons when space is tight; keep the icon for colour-blind users where possible.

## Pitfalls

- Do not create the live region on demand. It must be rendered before the first message, and `aria-live` must be on the container, not on each toast.
- Never put the only path to a critical action in a toast; it disappears, and screen-reader users cannot reach it after it is gone. Use `role="alert"` for errors and keep a persistent record (form error, banner) for anything that matters.
- `innerHTML` with user-supplied text is an XSS hole; the pattern uses `textContent` for the message and `innerHTML` only for hardcoded icons.
- `pointer-events-none` on the region keeps it from blocking clicks on the page underneath; the toasts themselves re-enable pointer events.
- Many stacked toasts push each other around; the cap and the `gap-2` column are deliberate. If you need a history, build a notification panel instead.
- A toast that is removed on `animationend` never leaves if the animation is disabled by `prefers-reduced-motion`; the code checks the media query and removes immediately in that case.

## Related skills

- `web-ui-modal-dialog`
- `web-form-submit-with-fetch`
- `web-js-errors-and-logging`
- `web-motion-keyframes`
- `web-a11y-aria-patterns`
