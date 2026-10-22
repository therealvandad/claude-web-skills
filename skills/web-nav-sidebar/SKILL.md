---
name: web-nav-sidebar
description: Build a vertical sidebar navigation with grouped sections, icons, active-link state, collapsible groups and a collapse-to-icons mode persisted in localStorage, plus an off-canvas drawer on mobile. Use when a user asks for a sidebar, side nav, left menu, docs navigation, admin/dashboard menu, or "navigation down the side".
---

# Sidebar navigation

Sidebars carry many links, so structure matters more than styling: group links under headings, mark the current page with `aria-current`, and let users collapse groups they do not need. On desktop the sidebar can shrink to an icon rail (labels hidden, tooltips via `title`); on mobile it becomes an off-canvas drawer opened by a button. The groups use native `<details>` so they work without JS; the script only adds the rail toggle, the drawer, and persistence.

## Pattern

```html
<div class="flex min-h-dvh">
  <!-- Backdrop for the mobile drawer -->
  <div data-sidebar-backdrop hidden class="fixed inset-0 z-30 bg-black/40 lg:hidden"></div>

  <aside data-sidebar
    class="group/side fixed inset-y-0 left-0 z-40 flex w-64 -translate-x-full flex-col border-r border-gray-200 bg-white transition-[translate,width] duration-200 motion-reduce:transition-none data-[open]:translate-x-0 lg:static lg:translate-x-0 lg:data-[collapsed]:w-16 dark:border-gray-800 dark:bg-gray-950">
    <div class="flex h-14 items-center justify-between px-3">
      <a href="/" class="truncate font-bold group-data-[collapsed]/side:sr-only">Acme Admin</a>
      <button type="button" data-sidebar-collapse aria-pressed="false" title="Collapse sidebar"
        class="hidden size-8 items-center justify-center rounded-md hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 lg:inline-flex dark:hover:bg-gray-800">
        <span class="sr-only">Collapse sidebar</span>
        <svg class="size-5 transition-transform motion-reduce:transition-none group-data-[collapsed]/side:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
    </div>

    <nav aria-label="Sidebar" class="flex-1 overflow-y-auto px-2 py-2">
      <details open class="mb-2">
        <summary class="cursor-pointer list-none px-2 py-1 text-xs font-semibold uppercase tracking-wide text-gray-500 group-data-[collapsed]/side:sr-only [&::-webkit-details-marker]:hidden">Overview</summary>
        <ul class="mt-1 space-y-0.5">
          <li><a href="/dashboard" aria-current="page" title="Dashboard"
            class="flex items-center gap-3 rounded-md px-2 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 aria-[current=page]:bg-blue-50 aria-[current=page]:text-blue-700 dark:text-gray-300 dark:hover:bg-gray-800 dark:aria-[current=page]:bg-blue-950 dark:aria-[current=page]:text-blue-300">
            <svg class="size-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
            <span class="truncate group-data-[collapsed]/side:sr-only">Dashboard</span></a></li>
          <li><a href="/reports" title="Reports"
            class="flex items-center gap-3 rounded-md px-2 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 dark:text-gray-300 dark:hover:bg-gray-800">
            <svg class="size-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 20V10m6 10V4m6 16v-7m4 7H2"/></svg>
            <span class="truncate group-data-[collapsed]/side:sr-only">Reports</span></a></li>
        </ul>
      </details>
      <details class="mb-2">
        <summary class="cursor-pointer list-none px-2 py-1 text-xs font-semibold uppercase tracking-wide text-gray-500 group-data-[collapsed]/side:sr-only [&::-webkit-details-marker]:hidden">Settings</summary>
        <ul class="mt-1 space-y-0.5">
          <li><a href="/settings/team" title="Team" class="flex items-center gap-3 rounded-md px-2 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 dark:text-gray-300 dark:hover:bg-gray-800">
            <svg class="size-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0M17 11a4 4 0 1 0 0-8"/></svg>
            <span class="truncate group-data-[collapsed]/side:sr-only">Team</span></a></li>
        </ul>
      </details>
    </nav>
  </aside>

  <div class="flex min-w-0 flex-1 flex-col">
    <header class="flex h-14 items-center gap-3 border-b border-gray-200 px-4 dark:border-gray-800">
      <button type="button" data-sidebar-open aria-controls="sidebar" aria-expanded="false" class="rounded-md p-2 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-blue-600 lg:hidden dark:hover:bg-gray-800">
        <span class="sr-only">Open navigation</span>
        <svg class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
      <h1 class="text-lg font-semibold">Dashboard</h1>
    </header>
    <main class="flex-1 p-4 sm:p-6">…</main>
  </div>
</div>
```

```js
// sidebar.js: mobile drawer + desktop rail collapse with persistence
const side = document.querySelector('[data-sidebar]');
const backdrop = document.querySelector('[data-sidebar-backdrop]');
const openBtn = document.querySelector('[data-sidebar-open]');
const collapseBtn = document.querySelector('[data-sidebar-collapse]');

const setDrawer = (open) => {
  side.toggleAttribute('data-open', open);
  backdrop.hidden = !open;
  openBtn.setAttribute('aria-expanded', String(open));
  document.body.classList.toggle('overflow-hidden', open);
  if (open) side.querySelector('a, button')?.focus(); else openBtn.focus();
};
openBtn.addEventListener('click', () => setDrawer(true));
backdrop.addEventListener('click', () => setDrawer(false));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && side.hasAttribute('data-open')) setDrawer(false); });

const setCollapsed = (collapsed) => {
  side.toggleAttribute('data-collapsed', collapsed);
  collapseBtn.setAttribute('aria-pressed', String(collapsed));
  collapseBtn.title = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
  try { localStorage.setItem('sidebar:collapsed', String(collapsed)); } catch {}
};
collapseBtn.addEventListener('click', () => setCollapsed(!side.hasAttribute('data-collapsed')));
try { if (localStorage.getItem('sidebar:collapsed') === 'true') setCollapsed(true); } catch {}
```

The collapsed rail keeps labels in the DOM as `sr-only`, so screen readers still hear "Dashboard", while sighted users get the `title` tooltip. `group-data-[collapsed]/side:` is Tailwind's named-group variant reacting to the `data-collapsed` attribute on the `<aside>`.

## Variations

- **Mark the active link on load**: `document.querySelectorAll('[data-sidebar] a').forEach(a => { if (a.pathname === location.pathname) a.setAttribute('aria-current', 'page'); })`.
- **Nested sub-items**: nest a second `<ul class="ml-7 border-l border-gray-200 pl-2">` inside the `<li>`; keep depth at two levels, deeper trees belong in a tree view.
- **No rail, just hide**: drop the collapse button and rely on the mobile drawer up to `xl:` for content-heavy apps.
- **Resizable width**: store width in a CSS variable `--sidebar-w` set from a drag handle; use `w-[var(--sidebar-w)]`.

## Pitfalls

- Put the sidebar's `<nav>` inside `<aside>` and give it `aria-label`; the page also has a main `<nav>` and screen readers need to tell them apart.
- `overflow-y-auto` belongs on the `<nav>`, not the `<aside>`, so the header and collapse button stay put while links scroll.
- `-translate-x-full lg:translate-x-0` must be paired with `lg:static`, otherwise on desktop the fixed sidebar overlaps content.
- Add `inert` to the drawer while it is closed on mobile (`side.inert = !open && !desktop.matches`) so its links are skipped by Tab when off-screen.
- Do not hide the collapsed `<summary>` with `hidden`: that removes the group's expand control; `sr-only` keeps it reachable.
- Persisting the collapsed state means first paint shows the wide sidebar then snaps; read localStorage in an inline `<script>` in `<head>` and set the attribute on `<html>` if the flash is noticeable.

## Related skills

- `web-layout-dashboard-sidebar`: full app shell this sidebar fits into.
- `web-nav-responsive-navbar`: horizontal counterpart.
- `web-ui-accordion`: `<details>` group behavior in depth.
- `web-js-storage`: safe localStorage helpers.
