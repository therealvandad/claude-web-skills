---
name: web-nav-dropdown-menu
description: Build an accessible dropdown menu button (trigger with aria-expanded, role="menu" of actions or a plain link list, Escape to close, ArrowUp/Down and Home/End navigation, typeahead, click-outside, focus restore) with Tailwind v4. Use when a user asks for a dropdown, menu button, "three dots" actions menu, user/avatar menu, context actions, or "options that appear when I click".
---

# Dropdown menu button

Two different things get called "dropdown": a **menu of actions** (Edit, Duplicate, Delete) and a **list of links** (account pages). Actions get `role="menu"` + `role="menuitem"` with full arrow-key handling; links get a plain `<ul>` of `<a>`s inside a disclosure, no menu roles. The pattern below is the action menu, which is the stricter contract; for links, keep the same open/close logic and drop the roles. The trigger is a `<button aria-haspopup="menu" aria-expanded>`, and focus moves into the menu on open and back to the button on close.

## Pattern

```html
<div data-menu class="relative inline-block text-left">
  <button type="button" id="row-actions-button" data-menu-button aria-haspopup="menu" aria-expanded="false" aria-controls="row-actions"
    class="inline-flex size-9 items-center justify-center rounded-md hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:hover:bg-gray-800">
    <span class="sr-only">Actions for "Q3 report"</span>
    <svg class="size-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><circle cx="4" cy="10" r="1.75"/><circle cx="10" cy="10" r="1.75"/><circle cx="16" cy="10" r="1.75"/></svg>
  </button>

  <div id="row-actions" role="menu" aria-labelledby="row-actions-button" data-menu-list hidden tabindex="-1"
    class="absolute right-0 z-20 mt-1 w-48 rounded-lg border border-gray-200 bg-white p-1 shadow-lg focus:outline-none dark:border-gray-800 dark:bg-gray-950">
    <button type="button" role="menuitem" tabindex="-1" data-action="edit"
      class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-gray-100 focus-visible:bg-gray-100 focus-visible:outline-none dark:hover:bg-gray-800 dark:focus-visible:bg-gray-800">Edit</button>
    <button type="button" role="menuitem" tabindex="-1" data-action="duplicate"
      class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-gray-100 focus-visible:bg-gray-100 focus-visible:outline-none dark:hover:bg-gray-800 dark:focus-visible:bg-gray-800">Duplicate</button>
    <div role="separator" class="my-1 border-t border-gray-200 dark:border-gray-800"></div>
    <button type="button" role="menuitem" tabindex="-1" data-action="delete"
      class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 focus-visible:bg-red-50 focus-visible:outline-none dark:text-red-400 dark:hover:bg-red-950 dark:focus-visible:bg-red-950">Delete</button>
  </div>
</div>
```

```js
// dropdown-menu.js: one init per [data-menu]; items fire a "menu:select" event with the action name
const initMenu = (root) => {
  const button = root.querySelector('[data-menu-button]');
  const list = root.querySelector('[data-menu-list]');
  const items = () => [...list.querySelectorAll('[role="menuitem"]:not([disabled])')];
  let typed = '', typeTimer;

  const open = (focusIndex = 0) => {
    list.hidden = false;
    button.setAttribute('aria-expanded', 'true');
    flip();
    const all = items();
    all[(focusIndex + all.length) % all.length]?.focus();
  };
  const close = (restoreFocus = true) => {
    if (list.hidden) return;
    list.hidden = true;
    button.setAttribute('aria-expanded', 'false');
    if (restoreFocus) button.focus();
  };
  // Open upward if there is no room below
  const flip = () => {
    const r = list.getBoundingClientRect();
    list.classList.toggle('bottom-full', r.bottom > window.innerHeight);
    list.classList.toggle('mb-1', r.bottom > window.innerHeight);
  };

  button.addEventListener('click', () => (list.hidden ? open() : close()));
  button.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); open(0); }
    if (e.key === 'ArrowUp') { e.preventDefault(); open(-1); }
  });
  list.addEventListener('keydown', (e) => {
    const all = items(), i = all.indexOf(document.activeElement);
    const go = (n) => { e.preventDefault(); all[(n + all.length) % all.length].focus(); };
    if (e.key === 'ArrowDown') return go(i + 1);
    if (e.key === 'ArrowUp') return go(i - 1);
    if (e.key === 'Home') return go(0);
    if (e.key === 'End') return go(all.length - 1);
    if (e.key === 'Escape') return close();
    if (e.key === 'Tab') return close(false); // let Tab move on naturally
    if (e.key.length === 1 && /\S/.test(e.key)) { // typeahead
      typed += e.key.toLowerCase(); clearTimeout(typeTimer); typeTimer = setTimeout(() => (typed = ''), 500);
      const hit = all.find((el) => el.textContent.trim().toLowerCase().startsWith(typed));
      hit?.focus();
    }
  });
  list.addEventListener('click', (e) => {
    const item = e.target.closest('[role="menuitem"]');
    if (!item) return;
    root.dispatchEvent(new CustomEvent('menu:select', { bubbles: true, detail: { action: item.dataset.action } }));
    close();
  });
  document.addEventListener('pointerdown', (e) => { if (!root.contains(e.target)) close(false); });
};
document.querySelectorAll('[data-menu]').forEach(initMenu);

// Usage
document.addEventListener('menu:select', (e) => console.log('action:', e.detail.action));
```

Items use `tabindex="-1"` and are focused programmatically, so the menu is one unit in the Tab order. `focus-visible:bg-*` with `outline-none` gives a clear highlighted row instead of a ring inside a ring.

## Variations

- **Link menu (account menu)**: remove `role="menu"`, `role="menuitem"` and `aria-haspopup`; keep `aria-expanded`, Escape and outside-click. Use `<a>` items with normal `tabindex`. Arrow keys are optional there.
- **Native alternative**: for a simple link list, `<details><summary>` works without JS; add `[&[open]>summary]:bg-gray-100` and a `document` click handler to close it.
- **Checkable items**: `role="menuitemcheckbox"` with `aria-checked`, toggled on select and the menu stays open.
- **Align left / full width on mobile**: swap `right-0` for `left-0`, or use `max-sm:fixed max-sm:inset-x-4 max-sm:bottom-4 max-sm:w-auto` for a bottom sheet feel.

## Pitfalls

- `role="menu"` requires arrow-key navigation; if you are not implementing it, do not add the role, a plain disclosure is more honest to assistive tech.
- Use `pointerdown` (not `click`) for outside detection so a click that opens another menu closes this one first and the visual state never shows two open.
- Never put the `hidden` list inside an `overflow-hidden` card: the menu gets clipped. Lift it or use `position: fixed` with computed coordinates.
- Destructive items (Delete) should still open a confirmation; the red color is a cue, not a safeguard.
- Each trigger needs a unique accessible name (`Actions for "Q3 report"`) when the menu repeats per row, or screen readers hear twenty identical "Actions" buttons.
- Avoid `hover`-to-open on menus; it is a tooltip behavior and breaks on touch.

## Related skills

- `web-nav-mega-menu`: large link panels in a header.
- `web-ui-tooltip-and-popover`: Popover API as an alternative positioning layer.
- `web-ui-modal-dialog`: confirmation after a destructive action.
- `web-a11y-aria-patterns`: menu vs disclosure semantics.
