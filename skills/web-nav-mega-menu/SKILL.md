---
name: web-nav-mega-menu
description: Build a mega menu, a large multi-column panel (grouped links, descriptions, icons, featured card) that opens from a top-level nav item, with click-to-open, hover intent on desktop, full keyboard support and a stacked accordion on mobile. Use when a user asks for a mega menu, "dropdown with columns", a products/solutions menu, or a big header menu like Stripe's or Apple's.
---

# Mega menu

A mega menu is a disclosure, not a `role="menu"`: it contains ordinary links, so the right semantics are a `<button aria-expanded>` controlling a panel of `<ul>`s. Open on click (works for touch, keyboard and mouse alike), optionally also on hover with a short intent delay so the panel does not flash while the cursor crosses the bar. On small screens the same panel renders inline as an accordion inside the mobile nav, so there is one DOM and one source of truth for the links.

## Pattern

```html
<nav aria-label="Main" class="relative mx-auto max-w-6xl px-4">
  <ul class="flex flex-col md:flex-row md:items-center md:gap-2">
    <li data-mega class="md:static">
      <button type="button" data-mega-toggle aria-expanded="false" aria-controls="mega-products"
        class="flex w-full items-center justify-between gap-1 rounded-md px-3 py-2 text-sm font-medium hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 md:w-auto dark:hover:bg-gray-800">
        Products
        <svg class="size-4 transition-transform motion-reduce:transition-none [[aria-expanded=true]>&]:rotate-180" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M5.5 7.5 10 12l4.5-4.5"/></svg>
      </button>

      <div id="mega-products" data-mega-panel hidden
        class="md:absolute md:inset-x-0 md:top-full md:mt-2 md:rounded-xl md:border md:border-gray-200 md:bg-white md:p-6 md:shadow-xl dark:md:border-gray-800 dark:md:bg-gray-950">
        <div class="grid gap-6 pl-3 md:grid-cols-[2fr_2fr_1.5fr] md:pl-0">
          <section>
            <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Build</h3>
            <ul class="space-y-1">
              <li><a href="/editor" class="group block rounded-md p-2 hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-blue-600 dark:hover:bg-gray-900">
                <span class="block text-sm font-medium group-hover:text-blue-600">Editor</span>
                <span class="block text-xs text-gray-500">Design pages visually.</span></a></li>
              <li><a href="/cms" class="group block rounded-md p-2 hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-blue-600 dark:hover:bg-gray-900">
                <span class="block text-sm font-medium group-hover:text-blue-600">CMS</span>
                <span class="block text-xs text-gray-500">Structured content.</span></a></li>
            </ul>
          </section>
          <section>
            <h3 class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Ship</h3>
            <ul class="space-y-1">
              <li><a href="/hosting" class="block rounded-md p-2 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-blue-600 dark:hover:bg-gray-900">Hosting</a></li>
              <li><a href="/analytics" class="block rounded-md p-2 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-blue-600 dark:hover:bg-gray-900">Analytics</a></li>
            </ul>
          </section>
          <a href="/launch" class="hidden rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 p-4 text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 md:block">
            <span class="block text-sm font-semibold">New: Launch 2.0</span>
            <span class="mt-1 block text-xs text-blue-100">See what changed</span>
          </a>
        </div>
      </div>
    </li>
    <li><a href="/pricing" class="block rounded-md px-3 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800">Pricing</a></li>
  </ul>
</nav>
```

```js
// mega-menu.js: click + hover intent on desktop, one open at a time, Escape, outside click
const HOVER_DELAY = 120;
const desktop = window.matchMedia('(min-width: 48rem)');

const initMegaMenus = () => {
  const items = [...document.querySelectorAll('[data-mega]')];
  const closeAll = (except) => items.forEach((it) => it !== except && setOpen(it, false));
  const setOpen = (item, open) => {
    item.querySelector('[data-mega-toggle]').setAttribute('aria-expanded', String(open));
    item.querySelector('[data-mega-panel]').hidden = !open;
  };
  const isOpen = (item) => !item.querySelector('[data-mega-panel]').hidden;

  items.forEach((item) => {
    const toggle = item.querySelector('[data-mega-toggle]');
    let timer;
    toggle.addEventListener('click', () => { const next = !isOpen(item); closeAll(); setOpen(item, next); });
    // Hover intent only with a fine pointer on desktop
    item.addEventListener('pointerenter', (e) => {
      if (!desktop.matches || e.pointerType !== 'mouse') return;
      timer = setTimeout(() => { closeAll(item); setOpen(item, true); }, HOVER_DELAY);
    });
    item.addEventListener('pointerleave', (e) => {
      clearTimeout(timer);
      if (desktop.matches && e.pointerType === 'mouse') setOpen(item, false);
    });
    item.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && isOpen(item)) { setOpen(item, false); toggle.focus(); }
    });
    // Close when Tab leaves the item entirely
    item.addEventListener('focusout', (e) => {
      if (!item.contains(e.relatedTarget)) setOpen(item, false);
    });
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('[data-mega]')) closeAll(); });
  desktop.addEventListener('change', () => closeAll());
};
initMegaMenus();
```

The `md:static` on the `<li>` plus `md:absolute md:inset-x-0` on the panel makes the panel span the full width of the `<nav>` (which is `relative`), not just the width of the trigger. Below `md` the panel is simply a block in flow, so it works as an accordion inside the mobile drawer.

## Variations

- **Panel as wide as the trigger**: drop `md:static` from the `<li>` (make it `md:relative`) and replace `md:inset-x-0` with `md:left-0 md:w-[40rem]`.
- **Hover-only on desktop, click on touch**: keep both; the `pointerType` check already ignores touch and pen for hover. Do not remove the click handler, keyboard users rely on it.
- **Fade in**: swap `hidden` for `invisible opacity-0` toggles plus `transition duration-150 motion-reduce:transition-none`, and set `panel.inert = !open` so hidden links are skipped by Tab.
- **Arrow-key column navigation**: optional; collect `panel.querySelectorAll('a')` and move focus on ArrowDown/ArrowUp. Tab order already works, so only add this if the panel is very large.

## Pitfalls

- Do not use `role="menu"` / `role="menuitem"`: those are for application menus of actions and change how screen readers announce and navigate the links.
- Hover-only menus are unusable on touch and with keyboards, and a panel that opens on hover must also close on `pointerleave` or it traps the viewport.
- Without the `focusout` close, a panel stays open after the user Tabs past it and visually hides the content below the header.
- `inset-x-0` positions relative to the nearest positioned ancestor. If the panel is narrower than expected, an intermediate element has `relative` on it.
- Tall panels on short laptops: add `md:max-h-[calc(100vh-6rem)] md:overflow-y-auto` to the panel.
- Place the featured card last in DOM order; visual position via grid columns is fine, but reading order should go links first.

## Related skills

- `web-nav-responsive-navbar`: the bar this menu lives in.
- `web-nav-dropdown-menu`: for small single-column menus and action menus.
- `web-a11y-aria-patterns`: disclosure vs menu semantics.
- `web-motion-transitions`: fade/scale the panel.
