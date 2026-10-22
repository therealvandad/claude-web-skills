---
name: web-layout-dashboard-sidebar
description: Build an app shell with a collapsible left sidebar, a top bar and a scrolling content area, using Tailwind v4 and a few lines of vanilla JS for the mobile drawer. Use whenever a user asks for a dashboard, admin panel, app layout, "sidebar navigation", settings page, back-office or any logged-in screen with a side menu.
---

# Dashboard sidebar shell

App screens differ from marketing pages: the chrome (sidebar, top bar) stays put and only the content scrolls. On desktop the sidebar is a fixed-width column; on phones it becomes an off-canvas drawer opened from the top bar. Use the native `<dialog>` for the drawer so focus trapping, Escape and the backdrop are handled by the browser, and keep the desktop sidebar as plain markup that needs no JS at all.

## Pattern

```html
<body class="h-dvh overflow-hidden bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
<div class="flex h-full">

  <!-- Desktop sidebar: hidden on mobile, static column from lg -->
  <aside class="hidden w-64 shrink-0 flex-col border-r border-gray-200 bg-white lg:flex dark:border-gray-800 dark:bg-gray-900" aria-label="Sidebar">
    <div class="flex h-16 items-center px-6 text-lg font-semibold">Acme</div>
    <nav class="flex-1 overflow-y-auto px-3 py-2" aria-label="Main">
      <ul role="list" class="space-y-1 text-sm font-medium">
        <li><a href="/app" aria-current="page" class="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100 aria-[current=page]:bg-blue-50 aria-[current=page]:text-blue-700 dark:text-gray-300 dark:hover:bg-gray-800 dark:aria-[current=page]:bg-blue-950 dark:aria-[current=page]:text-blue-300">
          <svg class="size-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 12 12 3l9 9M5 10v10h14V10"/></svg>
          Overview
        </a></li>
        <li><a href="/app/projects" class="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800">
          <svg class="size-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18"/></svg>
          Projects
        </a></li>
        <li><a href="/app/settings" class="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800">
          <svg class="size-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>
          Settings
        </a></li>
      </ul>
    </nav>
    <div class="border-t border-gray-200 p-4 text-sm dark:border-gray-800">
      <a href="/app/account" class="flex items-center gap-3 rounded-md px-2 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-800">
        <img src="/img/me.jpg" width="32" height="32" alt="" class="size-8 rounded-full">
        <span class="truncate">Ada Lovelace</span>
      </a>
    </div>
  </aside>

  <!-- Main column -->
  <div class="flex min-w-0 flex-1 flex-col">
    <header class="flex h-16 shrink-0 items-center gap-4 border-b border-gray-200 bg-white px-4 sm:px-6 dark:border-gray-800 dark:bg-gray-900">
      <button type="button" id="open-sidebar" class="-ml-2 rounded-md p-2 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 lg:hidden dark:hover:bg-gray-800" aria-label="Open navigation">
        <svg class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
      <h1 class="text-base font-semibold">Overview</h1>
      <div class="ml-auto flex items-center gap-2">
        <button type="button" class="rounded-md p-2 hover:bg-gray-100 dark:hover:bg-gray-800" aria-label="Notifications">
          <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0"/></svg>
        </button>
      </div>
    </header>

    <main id="main" class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <div class="mx-auto max-w-6xl">
        <!-- page content -->
      </div>
    </main>
  </div>
</div>

<!-- Mobile drawer: native dialog, same nav markup -->
<dialog id="sidebar-drawer" class="m-0 h-dvh max-h-none w-72 max-w-[85vw] bg-white p-0 backdrop:bg-gray-900/50 lg:hidden dark:bg-gray-900" aria-label="Navigation">
  <div class="flex h-16 items-center justify-between px-4">
    <span class="text-lg font-semibold">Acme</span>
    <button type="button" id="close-sidebar" class="rounded-md p-2 hover:bg-gray-100 dark:hover:bg-gray-800" aria-label="Close navigation">
      <svg class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
    </button>
  </div>
  <!-- paste the same <nav> as the desktop sidebar here -->
</dialog>

<script type="module">
  const drawer = document.getElementById('sidebar-drawer');
  document.getElementById('open-sidebar').addEventListener('click', () => drawer.showModal());
  document.getElementById('close-sidebar').addEventListener('click', () => drawer.close());
  drawer.addEventListener('click', (e) => { if (e.target === drawer) drawer.close(); }); // backdrop click
  drawer.addEventListener('click', (e) => { if (e.target.closest('a')) drawer.close(); }); // navigated
  matchMedia('(min-width: 64rem)').addEventListener('change', (e) => { if (e.matches) drawer.close(); });
</script>
</body>
```

Why these choices:

- `body.h-dvh overflow-hidden` + `main.overflow-y-auto`: only the content scrolls; sidebar and top bar never move. `dvh` tracks the real visible height on mobile browsers.
- `min-w-0` on the main column lets wide tables and long strings shrink instead of pushing the sidebar off screen.
- `aria-current="page"` is both the accessibility signal and the style hook (`aria-[current=page]:`), so the active state cannot drift out of sync.
- `<dialog>.showModal()` gives a focus trap, Escape-to-close, inert background and a `::backdrop` for free. `m-0` resets the dialog's default centering so it docks left.
- The `matchMedia` listener closes the drawer if the viewport grows past `lg`, so a rotated tablet never shows both sidebars.

## Variations

- **Collapsible desktop sidebar (icons only)**: toggle a `data-collapsed` attribute on the `<aside>` and use `data-collapsed:w-16` plus `data-collapsed:[&_span]:sr-only` (or `[&_.label]:hidden`) on the link labels. Persist the choice in `localStorage` and add `title` attributes so collapsed icons still have a tooltip.
- **Sidebar sections**: wrap groups in `<div>` with a `<p class="px-3 pt-4 pb-1 text-xs font-semibold uppercase text-gray-500">Workspace</p>` heading; use `<p>`, not `<h2>`, inside a nav to keep the outline clean.
- **Right-side drawer** (filters, details): same `<dialog>` with `ml-auto` instead of `m-0`.
- **Top bar breadcrumbs**: replace the `<h1>` with `web-nav-breadcrumbs`; keep an `sr-only` `<h1>` so the page still has one.

## Pitfalls

- Using `h-screen` instead of `h-dvh` leaves the bottom of the content hidden behind the mobile browser toolbar.
- Forgetting `overflow-y-auto` on `<main>` (or putting it on `<body>`) means the sidebar scrolls away with the content.
- A long sidebar nav with no `overflow-y-auto` of its own gets cut off on short laptop screens; the `nav.flex-1 overflow-y-auto` wrapper handles it.
- Dialogs are not styled by Preflight's `:where` reset in the same way as divs: always set `max-h-none` and `m-0`, or the drawer sits centered with a 100 px gap at the bottom.
- Do not render the drawer as `hidden` + `fixed` div with your own focus trap; the native dialog is less code and more correct. Browsers without `<dialog>` are below 1 percent and get the always-visible desktop nav at `lg:` anyway.
- A top bar that contains the only `<h1>` but is `lg:hidden` leaves desktop pages without a heading. Keep the `<h1>` visible at all sizes.

## Related skills

- `web-nav-sidebar`
- `web-nav-responsive-navbar`
- `web-ui-modal-dialog`
- `web-ui-data-table`
- `web-css-sticky-and-fixed`
- `web-js-storage`
