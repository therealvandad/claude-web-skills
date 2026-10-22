---
name: web-css-sticky-and-fixed
description: Sticky headers, sidebars and table-of-contents, sticky table headers, fixed bottom bars that respect phone safe areas, and a z-index scale that stops stacking fights. Use whenever a user asks to "keep the header at the top", pin a sidebar while scrolling, make a floating button or cookie bar, or says "sticky isn't working" or "my modal is behind the header".
---

# Sticky and fixed positioning

`position: sticky` keeps an element in normal flow until its scroll container reaches the offset you set, then pins it, within its parent only. `position: fixed` removes an element from flow and pins it to the viewport. Sticky is almost always the better default: it never covers content it did not already occupy, it needs no spacer, and it releases at the end of its parent. Fixed is for things that live outside the page (toasts, a bottom action bar, a cookie banner). Both need a conscious z-index plan, defined once as tokens rather than invented per element.

## Pattern

```css
@import "tailwindcss";

@theme {
  /* z-header, z-sticky, z-dropdown, z-overlay, z-modal, z-toast */
  --z-index-header: 30;
  --z-index-sticky: 20;
  --z-index-dropdown: 40;
  --z-index-overlay: 50;
  --z-index-modal: 60;
  --z-index-toast: 70;
  --spacing-header: 4rem;      /* h-header, top-header, scroll-mt-header */
}
```

```html
<!-- 1. Sticky site header -->
<header class="sticky top-0 z-header h-header border-b bg-white/90 backdrop-blur dark:bg-gray-900/90">
  <div class="mx-auto flex h-full max-w-6xl items-center px-4">Site header</div>
</header>

<main class="mx-auto max-w-6xl px-4 lg:grid lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-8">
  <!-- 2. Sticky sidebar / table of contents: pins below the header, scrolls if taller -->
  <aside class="hidden lg:block">
    <nav class="sticky top-[calc(var(--spacing-header)+1rem)] max-h-[calc(100dvh-var(--spacing-header)-2rem)] overflow-y-auto" aria-label="On this page">
      <ul class="space-y-1 text-sm" role="list">
        <li><a href="#intro" class="block rounded px-2 py-1 hover:bg-gray-100">Intro</a></li>
        <li><a href="#usage" class="block rounded px-2 py-1 hover:bg-gray-100">Usage</a></li>
      </ul>
    </nav>
  </aside>

  <article class="prose">
    <h2 id="intro" class="scroll-mt-header">Intro</h2>   <!-- anchor lands below header -->
    <p>Long content…</p>

    <!-- 3. Sticky table header inside a scrollable table -->
    <div class="max-h-96 overflow-auto rounded-lg border">
      <table class="w-full border-collapse text-sm">
        <thead class="sticky top-0 z-sticky bg-gray-50 dark:bg-gray-800">
          <tr><th class="px-3 py-2 text-left">Name</th><th class="px-3 py-2 text-left">Status</th></tr>
        </thead>
        <tbody><tr><td class="px-3 py-2">Row</td><td class="px-3 py-2">Active</td></tr></tbody>
      </table>
    </div>
    <h2 id="usage" class="scroll-mt-header">Usage</h2>
  </article>
</main>

<!-- 4. Fixed bottom action bar with iPhone home-indicator safe area -->
<div class="fixed inset-x-0 bottom-0 z-overlay border-t bg-white p-4 pb-[max(1rem,env(safe-area-inset-bottom))] shadow-lg dark:bg-gray-900 sm:hidden">
  <button type="button" class="w-full rounded-lg bg-blue-600 py-3 font-medium text-white">Buy now</button>
</div>
<!-- Reserve space so the bar never hides the last content on mobile -->
<div class="h-24 sm:hidden" aria-hidden="true"></div>
```

Safe areas only apply when the viewport meta opts in: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`.

## Variations

- **Sticky section labels in long lists** (contacts, changelogs): `sticky top-header` on each group heading inside a scrolling list; later headings push earlier ones out naturally.
- **Sticky footer (always at bottom, not fixed)**: that is a layout job, not positioning: `min-h-dvh flex flex-col` with `flex-1` on `<main>` (see `web-layout-page-shell`).
- **Sticky on the horizontal axis**: `sticky left-0` on the first `<td>`/`<th>` of a wide table keeps the row label visible while scrolling sideways; give it a background.
- **Header that hides on scroll down**: keep it `sticky` and toggle `-translate-y-full` with JS; see `web-nav-sticky-header`.

## Pitfalls

- **Sticky "not working" is nearly always an ancestor with `overflow: hidden|auto|scroll`**, which becomes the scroll container and clips the sticky range. Remove the overflow, or put the sticky element inside that scroller on purpose (pattern 3).
- **Sticky element as tall as its parent cannot stick**: a sidebar in a grid cell stretches to the row height. Add `self-start` (`align-self: start`) to the sticky element or wrap it, as in pattern 2 where the `<nav>` sits inside the `<aside>`.
- **No `top-*` value means no sticking**: `sticky` alone does nothing; always pair with `top-0` (or `bottom-0`).
- **Covering anchors**: in-page links land under a sticky header. Set `scroll-mt-header` (`scroll-margin-top`) on targets or `scroll-pt-*` on `<html>`.
- **Fixed elements and `100vh`**: on mobile the URL bar makes `100vh` taller than the visible area, so bottom-fixed bars can sit off-screen. Use `bottom-0` with `inset-x-0`, and `dvh` for heights.
- **`transform`, `filter`, `backdrop-filter` or `contain` on an ancestor** turn `fixed` into "fixed relative to that ancestor". Keep fixed overlays as direct children of `<body>`, or use `<dialog>`/Popover API which render in the top layer and ignore z-index wars entirely.
- **z-index without a stacking context plan**: `z-50` on a dropdown loses to a sibling section with `relative z-10`? Not necessarily, but `isolate` on sections creates contexts that *do* trap z-index. Use the token scale and add `isolate` only where you want to contain stacking.

## Related skills

- `web-nav-sticky-header` for shrink/hide-on-scroll behaviour
- `web-nav-scroll-spy-toc` for the sticky table of contents with active highlighting
- `web-nav-anchor-and-smooth-scroll` for `scroll-margin-top` details
- `web-ui-data-table` for full sticky-header tables
- `web-ui-modal-dialog` and `web-ui-toast-notifications` for top-layer overlays
- `web-layout-page-shell` for the sticky-footer layout
