---
name: web-ui-skeleton-and-loading
description: 'Build loading states with Tailwind: skeleton screens that mirror the final layout, an accessible spinner, determinate and indeterminate progress bars, aria-busy/aria-live announcements, and a swap-in pattern for fetched content. Use whenever a user asks for a skeleton, placeholder, shimmer, spinner, loader, "loading..." state, progress bar, or wants to avoid layout jump while data loads.'
---

# Skeletons, spinners and progress

Pick the loading indicator by what you know. If you know the **shape** of the incoming content (a list of cards, a profile), render a skeleton with the same dimensions so nothing jumps when data arrives. If you only know **that** something is happening, use a spinner. If you know **how far** along it is, use a determinate progress bar. In every case the region must tell assistive tech it is busy (`aria-busy`) and announce when it is done, without flashing an indicator for a 50 ms request.

## Pattern

```html
<!-- 1. Skeleton: same box sizes as the real card -->
<section id="posts" aria-busy="true" aria-live="polite" class="mx-auto grid max-w-5xl gap-6 px-4 sm:grid-cols-2 lg:grid-cols-3">
  <template id="skeleton-card">
    <div class="overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-800" aria-hidden="true">
      <div class="aspect-video w-full animate-pulse bg-gray-200 motion-reduce:animate-none dark:bg-gray-800"></div>
      <div class="space-y-3 p-5">
        <div class="h-3 w-20 animate-pulse rounded bg-gray-200 motion-reduce:animate-none dark:bg-gray-800"></div>
        <div class="h-5 w-4/5 animate-pulse rounded bg-gray-200 motion-reduce:animate-none dark:bg-gray-800"></div>
        <div class="h-4 w-full animate-pulse rounded bg-gray-200 motion-reduce:animate-none dark:bg-gray-800"></div>
        <div class="h-4 w-2/3 animate-pulse rounded bg-gray-200 motion-reduce:animate-none dark:bg-gray-800"></div>
      </div>
    </div>
  </template>
  <p class="sr-only" data-status>Loading posts</p>
</section>

<!-- 2. Spinner: pure CSS, inherits colour, labelled -->
<span role="status" class="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
  <svg class="size-5 animate-spin motion-reduce:animate-none" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/>
  </svg>
  Saving…
</span>

<!-- 3. Determinate progress: native element, styled -->
<label for="upload" class="block text-sm font-medium">Uploading photo.jpg</label>
<progress id="upload" value="42" max="100"
  class="mt-1 h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-indigo-600 [&::-moz-progress-bar]:bg-indigo-600 dark:[&::-webkit-progress-bar]:bg-gray-800">42%</progress>

<!-- 4. Indeterminate bar (unknown duration) -->
<div role="progressbar" aria-label="Loading" class="relative h-1 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800">
  <div class="absolute inset-y-0 w-1/3 rounded-full bg-indigo-600 motion-safe:animate-[slide_1.2s_ease-in-out_infinite] motion-reduce:w-full motion-reduce:opacity-60"></div>
</div>
```

```css
@keyframes slide { from { left: -33% } to { left: 100% } }
```

```js
// Swap-in pattern: show skeletons only if loading takes longer than 150 ms, then replace with real content
async function loadPosts(section, fetchPosts, renderPost) {
  const tpl = document.getElementById('skeleton-card');
  const status = section.querySelector('[data-status]');
  const showSkeleton = setTimeout(() => {
    for (let i = 0; i < 6; i++) section.append(tpl.content.cloneNode(true));
  }, 150);

  try {
    const posts = await fetchPosts();
    clearTimeout(showSkeleton);
    section.querySelectorAll('[aria-hidden="true"]').forEach((el) => el.remove());
    section.append(...posts.map(renderPost));
    status.textContent = `${posts.length} posts loaded`;
  } catch (err) {
    clearTimeout(showSkeleton);
    section.querySelectorAll('[aria-hidden="true"]').forEach((el) => el.remove());
    status.textContent = 'Could not load posts';
    section.insertAdjacentHTML('beforeend', '<p class="col-span-full text-center text-sm text-red-600">Could not load posts. <button type="button" class="underline" onclick="location.reload()">Retry</button></p>');
  } finally {
    section.setAttribute('aria-busy', 'false');
  }
}
// loadPosts(document.getElementById('posts'), () => fetch('/api/posts').then(r => r.json()), renderPost);
```

Why this shape: skeleton blocks are `aria-hidden` because they carry no information; the single `sr-only` status line inside the `aria-live` region does the announcing, once on start and once on finish. `aria-busy="true"` tells screen readers to hold off reading the region until it settles. The 150 ms delay avoids a skeleton flash on fast responses, which reads as more jank than no indicator at all. `<progress>` is used for determinate progress because it has the role, value and accessible name built in.

## Variations

- **Shimmer instead of pulse**: `bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%] motion-safe:animate-[shimmer_1.5s_infinite]` with `@keyframes shimmer { to { background-position: -200% 0 } }`.
- **Button loading state**: see `web-ui-buttons`; keep the button width stable by swapping the label for a spinner inside a fixed-width span, and set `aria-disabled="true"` rather than `disabled` so focus is not lost.
- **Full-page loading**: a centred spinner in `<main aria-busy="true">` is fine for an initial app load; for navigation between views prefer a thin top progress bar (variation 4 fixed at `top-0`) so the old content stays visible.
- **Text skeletons**: for paragraphs use widths that vary (`w-full`, `w-11/12`, `w-3/4`) so the block reads as text, and match `h-4` to the body line height.

## Pitfalls

- A skeleton that does not match the final layout causes exactly the layout shift it was meant to prevent. Copy the real component's classes and replace content with blocks.
- `animate-pulse` and `animate-spin` run forever; add `motion-reduce:animate-none` and make sure a static state still looks like loading (the grey blocks do, a frozen spinner does not; pair it with text).
- Do not set `aria-live` on an element that gets replaced; the region must persist across the swap. The pattern keeps the live attribute on the section and the status text inside it.
- `role="status"` has an implicit `aria-live="polite"`; do not add `role="alert"` to loading messages or every page load will interrupt the user.
- Indeterminate `<div role="progressbar">` needs `aria-label` and, if it gets a value later, `aria-valuenow`/`aria-valuemin`/`aria-valuemax`; prefer `<progress>` as soon as you can report a number.
- Spinners inherit `currentColor`; on a coloured button make sure the spinner has enough contrast against it.

## Related skills

- `web-motion-loading-and-progress`
- `web-ui-buttons`
- `web-js-fetch-and-apis`
- `web-design-empty-and-error-states`
- `web-perf-web-vitals`
