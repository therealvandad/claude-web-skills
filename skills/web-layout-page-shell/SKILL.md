---
name: web-layout-page-shell
description: Build the base page skeleton (header, main, footer) with a footer that sticks to the bottom on short pages, a centered max-width container and responsive side padding, using Tailwind v4. Use whenever a user starts a new page or site, asks for a "page template", "boilerplate", "layout wrapper", "container", "sticky footer" or "basic HTML structure".
---

# Page shell

Every page needs the same three things before any section is designed: a document that fills the viewport so the footer never floats mid-screen, one container that centers content and caps line length, and side padding that grows with the screen. Get this right once and every later section (hero, grid, footer) just drops into `<main>`.

## Pattern

```html
<!doctype html>
<html lang="en" class="h-full scroll-smooth motion-reduce:scroll-auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Site name</title>
  <link rel="stylesheet" href="/dist/output.css">
</head>
<body class="flex min-h-full flex-col bg-white text-gray-900 antialiased dark:bg-gray-950 dark:text-gray-100">

  <a href="#main" class="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:ring-2 focus:ring-blue-600">
    Skip to content
  </a>

  <header class="border-b border-gray-200 dark:border-gray-800">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <a href="/" class="text-lg font-semibold">Site name</a>
      <nav aria-label="Main">
        <ul class="flex gap-6 text-sm">
          <li><a href="/about" class="hover:text-blue-600">About</a></li>
          <li><a href="/contact" class="hover:text-blue-600">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main id="main" class="flex-1">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">Page title</h1>
      <p class="mt-4 max-w-prose text-gray-600 dark:text-gray-400">Content goes here.</p>
    </div>
  </main>

  <footer class="border-t border-gray-200 dark:border-gray-800">
    <div class="mx-auto max-w-7xl px-4 py-8 text-sm text-gray-500 sm:px-6 lg:px-8">
      &copy; 2026 Site name
    </div>
  </footer>

</body>
</html>
```

Why it works:

- `html.h-full` + `body.min-h-full flex flex-col` + `main.flex-1`: the body is at least viewport height and `<main>` absorbs the spare space, pushing the footer to the bottom. No `100vh` on body, so mobile browser chrome does not cause overflow.
- `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8` is the container. Repeat it inside each full-bleed region (header, main, footer) instead of wrapping the whole body, so backgrounds and borders can span edge to edge.
- The skip link is the first focusable element; `sr-only` hides it until keyboard focus reveals it.

To avoid repeating the container classes, define it once in your CSS:

```css
@import "tailwindcss";

@utility container-x {
  margin-inline: auto;
  max-width: var(--container-7xl);
  padding-inline: --spacing(4);
  @media (width >= 40rem) { padding-inline: --spacing(6); }
  @media (width >= 64rem) { padding-inline: --spacing(8); }
}
```

Then use `class="container-x"`. (Tailwind's built-in `container` utility in v4 is unpadded and uncentered by default; a custom `@utility` is clearer than overriding it.)

## Variations

- **Narrow reading layout**: swap `max-w-7xl` for `max-w-3xl` on `<main>` only (blogs, docs). Keep the header and footer at `max-w-7xl` so they visually anchor the page.
- **Full-bleed sections inside main**: give a `<section>` its own background (`bg-gray-50`) and put the container `<div>` inside it. The outer section spans the viewport; the inner div stays centered.
- **Sticky header**: add `sticky top-0 z-40 bg-white/90 backdrop-blur dark:bg-gray-950/90` to `<header>`, then add `scroll-pt-20` to `<html>` so anchor targets are not hidden under it.
- **Safe areas on notched phones**: add `pb-[env(safe-area-inset-bottom)]` to the footer and `viewport-fit=cover` to the viewport meta tag.

## Pitfalls

- Do not use `h-screen` or `min-h-screen` on `<body>`: on iOS Safari `100vh` is taller than the visible area and the footer gets cut off. `h-full` on `html` plus `min-h-full` on body avoids this. If you must use viewport units, use `min-h-dvh`.
- `flex-1` on `<main>` needs the parent to actually be a flex column. Forgetting `flex flex-col` on `<body>` silently breaks the sticky footer.
- Side padding must live on the container, not on `<body>`: body padding prevents any section from reaching the viewport edge.
- Set `lang` on `<html>` and the viewport meta tag; without the latter Tailwind's responsive breakpoints never fire on phones.
- Put one `<h1>` per page inside `<main>`; the site name in the header is a link, not a heading.
- Content wider than the viewport (a long URL, a code block, a wide table) causes horizontal scroll on phones. Wrap such content in `overflow-x-auto` and give prose `break-words`.

## Related skills

- `web-layout-landing-page`
- `web-layout-footer`
- `web-nav-responsive-navbar`
- `web-nav-sticky-header`
- `web-a11y-skip-links-and-landmarks`
- `web-css-spacing-scale`
- `web-ship-project-setup`
