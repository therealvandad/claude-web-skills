---
name: web-motion-loading-and-progress
description: Build animated loading indicators: a CSS spinner, an indeterminate progress bar, a determinate bar driven by JS, and a skeleton shimmer, all with aria-busy / role=progressbar / live regions and a calm reduced-motion version. Use whenever a user asks for a "spinner", "loading animation", "progress bar", "shimmer", "skeleton loader", "loading state", or "something while fetching".
---

# Loading and progress motion

A loading indicator exists to say "still working, not frozen". The motion should be continuous and low-contrast so it reassures instead of demanding attention, and it must be announced to assistive tech, because a spinning SVG means nothing to a screen reader. Every pattern here animates only `transform` or `background-position`/`opacity`, loops with `motion-safe:`, and under reduced motion degrades to a static or very slow indicator rather than disappearing (a loading state that vanishes is a bug, not a courtesy).

## Pattern

```css
@import "tailwindcss";

@theme {
  --animate-indeterminate: indeterminate 1.4s cubic-bezier(0.65, 0.05, 0.36, 1) infinite;
  --animate-shimmer: shimmer 1.6s linear infinite;

  @keyframes indeterminate {
    0%   { transform: translateX(-100%) scaleX(0.4); }
    50%  { transform: translateX(50%)   scaleX(0.6); }
    100% { transform: translateX(250%)  scaleX(0.4); }
  }
  @keyframes shimmer {
    from { background-position: 200% 0; }
    to   { background-position: -200% 0; }
  }
}
```

```html
<!-- 1. Spinner: Tailwind's animate-spin, text comes from a visually-hidden label -->
<div role="status" class="inline-flex items-center gap-2 text-sm text-zinc-600">
  <svg class="size-5 motion-safe:animate-spin motion-reduce:opacity-60" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
    <path class="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
  </svg>
  <span>Loading results…</span>
</div>

<!-- 2. Indeterminate bar: a sliding segment, width unknown -->
<div role="progressbar" aria-label="Uploading" aria-valuetext="Uploading, please wait"
     class="h-1.5 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700">
  <div class="h-full w-1/3 origin-left rounded-full bg-blue-600
              motion-safe:animate-indeterminate motion-reduce:w-full motion-reduce:opacity-50"></div>
</div>

<!-- 3. Determinate bar: JS sets --progress and aria-valuenow -->
<div id="upload" role="progressbar" aria-label="Upload" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"
     class="h-2 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700" style="--progress: 0">
  <div class="h-full origin-left rounded-full bg-blue-600 motion-safe:transition-transform motion-safe:duration-300 motion-safe:ease-out"
       style="transform: scaleX(calc(var(--progress) / 100))"></div>
</div>
<p id="upload-status" class="sr-only" aria-live="polite"></p>

<!-- 4. Skeleton shimmer: gradient sweeps across a gray block -->
<div aria-busy="true" aria-label="Loading article" class="space-y-3">
  <div class="h-6 w-2/3 rounded skeleton"></div>
  <div class="h-4 w-full rounded skeleton"></div>
  <div class="h-4 w-5/6 rounded skeleton"></div>
</div>
```

```css
.skeleton {
  background-color: var(--color-zinc-200);
  @variant dark { background-color: var(--color-zinc-700); }
  @media (prefers-reduced-motion: no-preference) {
    background-image: linear-gradient(90deg, transparent 0%, rgb(255 255 255 / 0.5) 50%, transparent 100%);
    background-size: 200% 100%;
    animation: var(--animate-shimmer);
  }
}
```

```js
const bar = document.querySelector('#upload');
const status = document.querySelector('#upload-status');
let lastAnnounced = -1;

function setProgress(percent) {
  const p = Math.max(0, Math.min(100, Math.round(percent)));
  bar.style.setProperty('--progress', p);
  bar.setAttribute('aria-valuenow', p);
  // Announce at 25% steps only; a live region updated every frame is unusable.
  if (p === 100 || Math.floor(p / 25) > Math.floor(lastAnnounced / 25)) {
    status.textContent = p === 100 ? 'Upload complete' : `Upload ${p}% complete`;
    lastAnnounced = p;
  }
}
// setProgress(42);
```

Why `scaleX` for the determinate fill instead of `width`: width triggers layout on every update; a transform does not, and the 300 ms transition smooths jumpy network progress events.

## Variations

- **Button loading state**: `aria-busy="true"` and `disabled` on the button, swap the icon for the spinner, keep the label ("Saving…") so the width does not jump. See `web-ui-buttons`.
- **Delay showing the spinner** by ~300 ms (`setTimeout` before adding it, cleared on completion) so fast responses never flash a loader.
- **Top-of-page progress line** (like GitHub): fixed `h-0.5` bar at `top-0` using the indeterminate animation, `z-50`, removed when the fetch resolves.
- **Circular progress**: an SVG circle with `stroke-dasharray` = circumference and `stroke-dashoffset` driven by `--progress`; animate the dashoffset with `transition-[stroke-dashoffset]`.

## Pitfalls

- `role="status"` and `aria-live` regions must exist in the DOM *before* their text changes; inject the region on page load, then fill it, or screen readers miss the first announcement.
- A skeleton that does not match the final layout's heights causes a layout shift when content arrives (CLS). Give skeleton blocks the same dimensions as the real content and reserve image aspect ratios.
- `animate-spin` on a large or blurred element costs a repaint each frame; keep spinners small (16-32 px) and solid.
- Never leave `aria-busy="true"` set after loading finishes; screen readers may suppress the region's content while it is busy.
- Reduced motion does not mean "no indicator". A static partial bar, a dimmed spinner, or text ("Loading…") still has to tell the user something is happening.
- An indeterminate bar that never resolves reads as a hang. Pair it with a timeout and an error state (`web-design-empty-and-error-states`).

## Related skills

- `web-ui-skeleton-and-loading`
- `web-motion-keyframes`
- `web-motion-reduced-motion`
- `web-form-submit-with-fetch`
- `web-ui-buttons`
