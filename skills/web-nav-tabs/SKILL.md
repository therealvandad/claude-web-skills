---
name: web-nav-tabs
description: Build accessible tabs (tablist/tab/tabpanel roles, roving tabindex, Left/Right/Home/End keys, automatic or manual activation) that sync the active tab to the URL hash so tabs are linkable and survive reload, styled with Tailwind v4. Use when a user asks for tabs, tabbed content, "switch between panels", a segmented view, or "tabs like in the settings page".
---

# Tabs with keyboard support and URL hash sync

Tabs are one of the few widgets where ARIA roles are genuinely required: `role="tablist"`, `role="tab"` and `role="tabpanel"` tell assistive tech that the buttons switch panels rather than navigate. The keyboard contract is one Tab stop for the whole list (roving `tabindex`), arrow keys to move between tabs, and Tab from a tab goes into its panel. Syncing the active tab to `location.hash` makes tabs deep-linkable and lets the back button work. Without JS, all panels render stacked with their headings, so the content is still readable.

## Pattern

```html
<div data-tabs class="w-full">
  <div role="tablist" aria-label="Account settings"
    class="flex gap-1 overflow-x-auto border-b border-gray-200 dark:border-gray-800">
    <button type="button" role="tab" id="tab-profile" aria-controls="panel-profile" aria-selected="true" tabindex="0"
      class="-mb-px whitespace-nowrap border-b-2 border-transparent px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-blue-600 aria-selected:border-blue-600 aria-selected:text-blue-600 dark:text-gray-400 dark:hover:text-white">
      Profile</button>
    <button type="button" role="tab" id="tab-security" aria-controls="panel-security" aria-selected="false" tabindex="-1"
      class="-mb-px whitespace-nowrap border-b-2 border-transparent px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-blue-600 aria-selected:border-blue-600 aria-selected:text-blue-600 dark:text-gray-400 dark:hover:text-white">
      Security</button>
    <button type="button" role="tab" id="tab-billing" aria-controls="panel-billing" aria-selected="false" tabindex="-1"
      class="-mb-px whitespace-nowrap border-b-2 border-transparent px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-blue-600 aria-selected:border-blue-600 aria-selected:text-blue-600 dark:text-gray-400 dark:hover:text-white">
      Billing</button>
  </div>

  <div role="tabpanel" id="panel-profile" aria-labelledby="tab-profile" tabindex="0" class="py-4 focus-visible:outline-2 focus-visible:outline-blue-600">
    <h2 class="text-lg font-semibold">Profile</h2>
    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Name, avatar, bio.</p>
  </div>
  <div role="tabpanel" id="panel-security" aria-labelledby="tab-security" tabindex="0" hidden class="py-4 focus-visible:outline-2 focus-visible:outline-blue-600">
    <h2 class="text-lg font-semibold">Security</h2>
    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Password, two-factor, sessions.</p>
  </div>
  <div role="tabpanel" id="panel-billing" aria-labelledby="tab-billing" tabindex="0" hidden class="py-4 focus-visible:outline-2 focus-visible:outline-blue-600">
    <h2 class="text-lg font-semibold">Billing</h2>
    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Plan, invoices, payment method.</p>
  </div>
</div>
```

```js
// tabs.js: roving tabindex, arrow keys, hash sync. Activation is automatic (focus = select).
const initTabs = (root) => {
  const tabs = [...root.querySelectorAll('[role="tab"]')];
  const panels = tabs.map((t) => document.getElementById(t.getAttribute('aria-controls')));

  const select = (tab, { focus = true, pushHash = true } = {}) => {
    tabs.forEach((t, i) => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      panels[i].hidden = !on;
    });
    if (focus) tab.focus();
    const id = tab.getAttribute('aria-controls');
    if (pushHash && location.hash !== `#${id}`) history.replaceState(null, '', `#${id}`);
  };

  tabs.forEach((tab) => tab.addEventListener('click', () => select(tab)));
  root.querySelector('[role="tablist"]').addEventListener('keydown', (e) => {
    const i = tabs.indexOf(document.activeElement);
    if (i === -1) return;
    const map = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 };
    if (!(e.key in map)) return;
    e.preventDefault();
    select(tabs[(map[e.key] + tabs.length) % tabs.length]);
  });

  const fromHash = () => {
    const tab = tabs.find((t) => `#${t.getAttribute('aria-controls')}` === location.hash);
    if (tab) select(tab, { focus: false, pushHash: false });
  };
  window.addEventListener('hashchange', fromHash);
  fromHash();
};
document.querySelectorAll('[data-tabs]').forEach(initTabs);
```

`history.replaceState` keeps the hash current without polluting history on every click; the `hashchange` listener handles pasted links and back/forward when another script pushes state. `tabindex="0"` on panels lets keyboard users reach panel content that has no focusable elements.

## Variations

- **Manual activation** (select on Enter/Space, arrows only move focus): in the keydown handler call `tabs[next].focus()` instead of `select(...)`, and add `if (e.key === 'Enter' || e.key === ' ') select(tabs[i])`. Use when switching loads data or is slow.
- **Pill style**: on the tablist use `rounded-lg bg-gray-100 p-1 dark:bg-gray-800`, on tabs `rounded-md aria-selected:bg-white aria-selected:shadow-sm dark:aria-selected:bg-gray-950` and drop the border classes.
- **Vertical tabs**: `aria-orientation="vertical"` on the tablist, `flex-col`, and map ArrowUp/ArrowDown instead of Left/Right.
- **Push history instead of replace**: use `history.pushState` when tabs represent distinct "pages" the user expects Back to undo.

## Pitfalls

- The `-mb-px` on tabs overlaps the tablist's bottom border so the active underline sits on it; if you change the border width, change the negative margin to match.
- Only the selected tab may have `tabindex="0"`; if all tabs are tabbable, Tab walks through every one and the arrow keys look redundant.
- `hidden` panels are also hidden from assistive tech; do not use `opacity-0` or `h-0` to hide panels or screen readers will read all of them.
- On narrow screens many tabs overflow: `overflow-x-auto` on the tablist is there for that, but add `scroll-smooth` and keep labels short. Consider a `<select>` under `sm:` if there are more than five tabs.
- Do not use tabs for navigation between pages; those are links in a `<nav>` styled like tabs, with `aria-current="page"` and no `role="tab"`.
- Hash sync conflicts with in-page anchors that share an id; namespace panel ids (`panel-...`).

## Related skills

- `web-ui-accordion`: for mobile-friendly stacked disclosure instead of tabs.
- `web-js-router-and-urls`: hash and History API patterns.
- `web-a11y-keyboard-and-focus`: roving tabindex explained.
- `web-a11y-aria-patterns`: when roles are required.
