---
name: web-a11y-keyboard-and-focus
description: Make every interaction work from the keyboard: logical tab order, visible focus-visible rings in Tailwind, focus trapping in dialogs and drawers, restoring focus on close, moving focus after dynamic changes, and WCAG 2.2 "focus not obscured". Use when a user says "can't tab to it", "focus ring", "focus trap", "keyboard navigation", "focus outline removed", or "where does focus go".
---

# Keyboard and focus management

Keyboard users (screen reader users, switch users, power users, anyone with a broken trackpad)
experience a page as a sequence of focus stops. Three things must be true: everything operable is
reachable with Tab/Shift+Tab (WCAG 2.1.1), the current stop is visible (2.4.7, strengthened in 2.2
by 2.4.11 Focus Not Obscured), and focus never gets lost: when content opens, closes or is
removed, you move focus deliberately. Native elements give you reachability for free; the
visibility and the moves are your job.

## Pattern

Global focus styling plus a drawer that traps focus and gives it back.

```css
@import "tailwindcss";

@layer base {
  /* One ring for everything, only for keyboard-initiated focus */
  :focus-visible {
    outline: 2px solid var(--color-blue-600);
    outline-offset: 2px;
    border-radius: 2px;
  }
  /* Keep headings reachable by programmatic focus without a ring */
  [tabindex="-1"]:focus { outline: none; }
}
```

```html
<button type="button" id="open-drawer" aria-expanded="false" aria-controls="drawer"
        class="rounded-md bg-blue-600 px-3 py-2 text-white">Filters</button>

<div id="drawer" hidden
     class="fixed inset-y-0 right-0 w-80 max-w-full overflow-y-auto bg-white p-4 shadow-xl dark:bg-gray-900">
  <h2 id="drawer-title" tabindex="-1" class="text-lg font-semibold">Filters</h2>
  <label class="mt-4 block">Minimum price <input type="number" class="mt-1 w-full rounded border p-2"></label>
  <button type="button" data-close class="mt-4 rounded-md border px-3 py-2">Close</button>
</div>
```

```js
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';
const opener = document.querySelector('#open-drawer');
const drawer = document.querySelector('#drawer');
let lastFocused = null;

function openDrawer() {
  lastFocused = document.activeElement;
  drawer.hidden = false;
  opener.setAttribute('aria-expanded', 'true');
  document.querySelector('main').inert = true;      // nothing behind is reachable or clickable
  drawer.querySelector('#drawer-title').focus();     // announce the title, then Tab lands on first control
}

function closeDrawer() {
  drawer.hidden = true;
  opener.setAttribute('aria-expanded', 'false');
  document.querySelector('main').inert = false;
  (lastFocused ?? opener).focus();                   // return focus where the user came from
}

function trapTab(e) {
  if (e.key !== 'Tab') return;
  const items = [...drawer.querySelectorAll(FOCUSABLE)];
  const first = items[0], last = items.at(-1);
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}

opener.addEventListener('click', openDrawer);
drawer.addEventListener('click', (e) => { if (e.target.closest('[data-close]')) closeDrawer(); });
drawer.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); trapTab(e); });
```

Why this shape:

- `:focus-visible` (Tailwind `focus-visible:`) shows the ring for keyboard focus and hides it for
  mouse clicks, so designers stop asking you to remove outlines. Never `outline-none` without a
  `focus-visible:` replacement.
- `inert` on the rest of the page is the modern focus trap; the Tab loop is a fallback for
  content inside the drawer. For a modal, `<dialog>.showModal()` does both natively.
- `tabindex="-1"` on the heading lets you focus it programmatically without adding a tab stop.
- Focus restore is explicit; browsers will otherwise drop focus to `<body>` when the focused
  element is hidden, which resets the reading position to the top.

## Variations

- **Modal dialog**: use `<dialog>` and `showModal()`; browsers trap focus, handle Escape and make
  the rest inert. Still restore focus on `close` (see `web-ui-modal-dialog`).
- **Single-page content swap** (router, tab panel, "load more"): after replacing content, focus the
  new region's heading (`tabindex="-1"`) or the first new item, and announce via a live region.
- **Skip to results** after a search or filter: focus the results heading so the user does not
  Tab through the whole form again.
- **Roving tabindex** for composite widgets (tabs, toolbars, menus): one item has `tabindex="0"`,
  the rest `-1`, arrow keys move both focus and the `0`. Tab leaves the widget in one stop.

## Pitfalls

- Positive `tabindex` values (`tabindex="3"`). They jump ahead of everything else and make order
  unmaintainable. Fix DOM order instead; CSS `order` and `flex-row-reverse` also break the
  match between visual and tab order (WCAG 2.4.3).
- Sticky headers and cookie banners covering the focused element. WCAG 2.2 SC 2.4.11 requires
  focus not be fully hidden; add `scroll-padding-top` on `html` equal to the header height.
- Click handlers on non-focusable elements (`div`, `span`, `li`). Replace with `<button>`; if you
  truly cannot, add `tabindex="0"`, `role`, and a keydown handler for Enter and Space.
- Opening a panel without moving focus into it, or closing one and leaving focus on a now-hidden
  element. Both strand screen reader users.
- Focus styles that fail contrast: the ring needs 3:1 against adjacent colors (SC 1.4.11). A 2px
  offset ring in a strong color is reliable on both light and dark backgrounds.
- Keyboard traps you did not intend: custom widgets that `preventDefault()` on Tab without
  looping, or an `iframe` with no way out. Always test with Tab, Shift+Tab, Escape, arrows.

## Related skills

- `web-ui-modal-dialog`
- `web-a11y-aria-patterns`
- `web-a11y-skip-links-and-landmarks`
- `web-nav-tabs`
- `web-nav-dropdown-menu`
- `web-css-modern-reset`
