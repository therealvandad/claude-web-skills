---
name: web-nav-responsive-navbar
description: Build a responsive top navigation bar (logo, links, CTA button, hamburger toggle that opens an accessible mobile menu) with Tailwind v4 and a few lines of vanilla JS. Use whenever a user asks for a navbar, header menu, top bar, site navigation, "hamburger menu", "mobile menu", or "the links at the top of the page".
---

# Responsive navbar with accessible hamburger menu

The navbar is the first interactive thing on every page, so it has to work with a thumb, a mouse and a keyboard. The pattern below renders the links inline from `md:` up and collapses them into a toggled panel below that. The toggle is a real `<button>` with `aria-expanded` and `aria-controls`, the panel closes on Escape and on outside click, and focus returns to the button so keyboard users never get lost. No JS is needed for the desktop state: the HTML is fully usable before the script runs.

## Pattern

```html
<header class="sticky top-0 z-40 border-b border-gray-200 bg-white/90 backdrop-blur dark:border-gray-800 dark:bg-gray-950/90">
  <nav aria-label="Main" class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
    <a href="/" class="flex items-center gap-2 text-lg font-bold tracking-tight focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
      <svg class="size-7 text-blue-600" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="12" r="10"/></svg>
      Acme
    </a>

    <!-- Toggle: visible only below md -->
    <button type="button" data-nav-toggle aria-expanded="false" aria-controls="site-menu"
      class="inline-flex size-10 items-center justify-center rounded-md hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 md:hidden dark:hover:bg-gray-800">
      <span class="sr-only">Open menu</span>
      <svg data-icon="open" class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
      <svg data-icon="close" class="hidden size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>

    <!-- Menu: panel below md, inline row from md up -->
    <div id="site-menu" data-nav-menu
      class="absolute inset-x-0 top-full hidden border-b border-gray-200 bg-white p-4 shadow-lg md:static md:flex md:items-center md:gap-6 md:border-0 md:bg-transparent md:p-0 md:shadow-none dark:border-gray-800 dark:bg-gray-950">
      <ul class="flex flex-col gap-1 md:flex-row md:gap-1">
        <li><a href="/features" class="block rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-blue-600 aria-[current=page]:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white" aria-current="page">Features</a></li>
        <li><a href="/pricing" class="block rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white">Pricing</a></li>
        <li><a href="/docs" class="block rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white">Docs</a></li>
      </ul>
      <a href="/signup" class="mt-3 block rounded-md bg-blue-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-blue-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 md:mt-0">Get started</a>
    </div>
  </nav>
</header>
```

```js
// navbar.js: toggle, Escape, outside click, reset on resize
const initNavbar = (root = document) => {
  const toggle = root.querySelector('[data-nav-toggle]');
  const menu = root.querySelector('[data-nav-menu]');
  if (!toggle || !menu) return;
  const icons = { open: toggle.querySelector('[data-icon="open"]'), close: toggle.querySelector('[data-icon="close"]') };
  const label = toggle.querySelector('.sr-only');

  const setOpen = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('hidden', !open);
    icons.open.classList.toggle('hidden', open);
    icons.close.classList.toggle('hidden', !open);
    label.textContent = open ? 'Close menu' : 'Open menu';
  };
  const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';

  toggle.addEventListener('click', () => setOpen(!isOpen()));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen()) { setOpen(false); toggle.focus(); }
  });
  document.addEventListener('click', (e) => {
    if (isOpen() && !menu.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
  });
  // Close when crossing the md breakpoint so the desktop row is never stuck "hidden"
  const mq = window.matchMedia('(min-width: 48rem)');
  mq.addEventListener('change', () => { if (mq.matches) setOpen(false); });
};
initNavbar();
```

Why it works: `hidden` on the panel is only in effect below `md`; `md:flex` wins above it, so the links are always visible on desktop even if the script never runs. The `absolute top-full` panel drops from the header (which is the positioning context via `sticky`) and covers content instead of pushing it, which avoids layout jumps.

## Variations

- **Push instead of overlay**: replace `absolute inset-x-0 top-full` with nothing and keep `md:static`; the panel then expands the header and pushes page content down. Good for short menus, bad for long ones.
- **Full-screen mobile menu**: use `fixed inset-0 top-14 overflow-y-auto` on the panel and add `document.body.classList.toggle('overflow-hidden', open)` in `setOpen` to lock scroll.
- **Animated panel**: add `transition-[opacity,translate] duration-200 motion-reduce:transition-none` and toggle `opacity-0 -translate-y-2` plus `invisible` rather than `hidden`, so it can fade. Keep `inert` on the hidden state so links are not tabbable: `menu.toggleAttribute('inert', !open)`.
- **Class-based dark mode**: add `@custom-variant dark (&:where(.dark, .dark *));` to your CSS and the `dark:` classes above work with a `.dark` toggle on `<html>`.

## Pitfalls

- A `<div>` with an `onclick` is not a toggle. Use `<button type="button">` so Space/Enter work and screen readers announce the `aria-expanded` state.
- Never hide the panel with `display:none` on desktop by accident: `hidden md:flex` is correct, `md:block hidden` is wrong order-independent but easy to break when someone adds `flex`. Test by disabling JS.
- `backdrop-blur` on a `sticky` header plus `overflow-hidden` on an ancestor kills stickiness. Keep the header a direct child of `<body>` or of a wrapper without overflow clipping.
- If links are icon-only on mobile, give them `sr-only` text. Hover styles alone are not an affordance for touch.
- `aria-current="page"` marks the active link; set it server-side or with `location.pathname` on load, not with a `.active` class alone.
- Outside-click handlers fire on the toggle itself; the `!toggle.contains(e.target)` check prevents close-then-reopen flicker.

## Related skills

- `web-nav-sticky-header`: shrink or hide this header on scroll.
- `web-nav-dropdown-menu`: nested menus inside the link list.
- `web-nav-mega-menu`: large multi-column panels per top-level item.
- `web-a11y-keyboard-and-focus`: focus management rules used here.
- `web-layout-page-shell`: where this header sits in the page skeleton.
