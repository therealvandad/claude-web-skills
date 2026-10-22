---
name: web-ui-tooltip-and-popover
description: Build tooltips (hover/focus hints) and popovers (click-to-open panels) with the native Popover API and CSS anchor positioning, with a small JS fallback for placement. Use whenever a user asks for a tooltip, hint, help bubble, info icon, popover, popup panel, hover card, or "show details on click" without a library.
---

# Tooltips and popovers

Two different things: a **tooltip** is a short label that appears on hover/focus and is referenced by `aria-describedby`; a **popover** is a panel the user opens on click, may contain controls, and closes on Escape or outside click. The Popover API (`popover` attribute, `popovertarget`) gives both the top-layer rendering, light-dismiss and toggling for free. CSS anchor positioning places them next to the trigger; a tiny JS fallback covers browsers without it.

## Pattern

```html
<!-- 1. Tooltip: hover + focus, pure CSS, no top layer needed -->
<span class="relative inline-block [&:hover>[role=tooltip]]:visible [&:hover>[role=tooltip]]:opacity-100
             [&:focus-within>[role=tooltip]]:visible [&:focus-within>[role=tooltip]]:opacity-100">
  <button type="button" aria-describedby="tip-save"
    class="rounded-md p-2 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:hover:bg-gray-800">
    <svg class="size-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M3 4.75A2.75 2.75 0 0 1 5.75 2h6.69c.73 0 1.43.29 1.94.8l2.82 2.82c.51.51.8 1.21.8 1.94v7.69A2.75 2.75 0 0 1 15.25 18H5.75A2.75 2.75 0 0 1 3 15.25V4.75Z"/></svg>
    <span class="sr-only">Save</span>
  </button>
  <span id="tip-save" role="tooltip"
    class="invisible absolute left-1/2 top-full z-10 mt-2 w-max max-w-48 -translate-x-1/2 rounded-md bg-gray-900 px-2 py-1 text-xs text-white opacity-0
           transition-opacity delay-300 duration-150 motion-reduce:transition-none dark:bg-gray-100 dark:text-gray-900">
    Save (Ctrl+S)
  </span>
</span>

<!-- 2. Popover: click to open, light-dismiss, top layer, anchored to its button -->
<button type="button" id="share-btn" popovertarget="share-pop"
  class="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:border-gray-700 dark:hover:bg-gray-900"
  style="anchor-name: --share">
  Share
</button>

<div id="share-pop" popover aria-labelledby="share-title"
  class="m-0 w-72 rounded-xl border border-gray-200 bg-white p-4 shadow-xl dark:border-gray-700 dark:bg-gray-900
         opacity-0 open:opacity-100 starting:open:opacity-0 transition-[opacity,overlay,display] duration-150 transition-discrete motion-reduce:transition-none"
  style="position-anchor: --share; inset: auto; top: anchor(bottom); left: anchor(left); margin-top: .5rem; position-try-fallbacks: flip-block, flip-inline;">
  <h3 id="share-title" class="text-sm font-semibold">Share this page</h3>
  <label for="share-url" class="mt-3 block text-xs text-gray-500">Link</label>
  <div class="mt-1 flex gap-2">
    <input id="share-url" readonly value="https://example.com/p/42" class="min-w-0 flex-1 rounded-md border border-gray-300 px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-800">
    <button type="button" data-copy="#share-url" class="rounded-md bg-indigo-600 px-3 py-1 text-sm font-medium text-white hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Copy</button>
  </div>
</div>
```

```js
// Fallback placement for browsers without CSS anchor positioning
if (!CSS.supports('position-anchor: --x')) {
  document.querySelectorAll('[popover]').forEach((pop) => {
    pop.addEventListener('toggle', (e) => {
      if (e.newState !== 'open') return;
      const btn = document.querySelector(`[popovertarget="${pop.id}"]`);
      const r = btn.getBoundingClientRect(), pr = pop.getBoundingClientRect();
      let top = r.bottom + 8, left = r.left;
      if (top + pr.height > innerHeight) top = r.top - pr.height - 8;   // flip up
      if (left + pr.width > innerWidth) left = innerWidth - pr.width - 8; // keep on screen
      Object.assign(pop.style, { position: 'fixed', top: `${Math.max(8, top)}px`, left: `${Math.max(8, left)}px` });
    });
  });
}

// Copy button inside the popover
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-copy]');
  if (!btn) return;
  await navigator.clipboard.writeText(document.querySelector(btn.dataset.copy).value);
  btn.textContent = 'Copied';
  setTimeout(() => (btn.textContent = 'Copy'), 1500);
});
```

Why this shape: the tooltip never goes in the top layer because it must stay tied to hover/focus of its trigger and be referenced by `aria-describedby`; `focus-within` makes it keyboard-reachable and the 300 ms delay stops flicker. The popover uses `popover` (auto mode) so Escape and outside clicks close it and only one is open at a time; `popovertarget` wires the button with correct `aria-expanded` automatically. The `m-0; inset: auto` reset undoes the UA's centered placement so the anchor rules take over.

## Variations

- **Manual popover** (stays open while others open, no light dismiss): `popover="manual"` and add an explicit close button with `popovertarget="id" popovertargetaction="hide"`.
- **Hover card** (rich preview on hover): use the popover markup but open it from `mouseenter`/`focus` with a 300 ms timer via `pop.showPopover()`, and close on `mouseleave`/`blur`. Keep it `popover="manual"` so moving the mouse into the card does not dismiss it.
- **Info icon with tooltip**: trigger is `<button type="button" aria-label="More about pricing" aria-describedby="tip-x">` with a `?` icon; never use a bare `<span>` as a trigger, it cannot receive focus.
- **Placement above / right**: change `top: anchor(bottom)` to `bottom: anchor(top)` or `left: anchor(right)`; `position-try-fallbacks` keeps it on screen.

## Pitfalls

- `title=""` is not a tooltip solution: it has a long delay, no styling, and never shows on keyboard focus or touch.
- A tooltip trigger must be focusable. Icons wrapped in `<span>` or `<div>` show the tooltip to mouse users only.
- Do not put links or buttons inside a tooltip; users cannot move the mouse into it without losing hover. Anything interactive is a popover.
- Popovers are in the top layer, so `z-index` on ancestors has no effect and `overflow: hidden` parents do not clip them; this is a feature, but it also means `position: absolute` relative to a parent will not work without anchor positioning.
- Touch devices have no hover: make every tooltip's content also available elsewhere (visible label, `aria-label`), and prefer a tap-to-open popover for essential info.
- A `toggle` event listener with `e.newState` requires the Popover API; the fallback above only runs when anchor positioning is missing but the API exists. For browsers without the API at all (very old), the panel renders inline; keep that acceptable by placing the popover HTML right after its trigger.

## Related skills

- `web-ui-modal-dialog`
- `web-nav-dropdown-menu`
- `web-a11y-aria-patterns`
- `web-a11y-keyboard-and-focus`
- `web-motion-transitions`
