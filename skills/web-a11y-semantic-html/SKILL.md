---
name: web-a11y-semantic-html
description: 'Write or fix page markup with the right HTML elements: landmarks (header, nav, main, footer), a heading outline, real lists, button versus link, native form and disclosure elements. Use whenever a user asks to "make it semantic", "fix the div soup", "is this accessible", "screen reader friendly", "proper HTML structure", or reviews markup before adding ARIA.'
---

# Semantic HTML first

Native elements carry a role, a name, keyboard behaviour and focus handling for free. A `<button>` is
tabbable, activates on Enter and Space, and announces as "button" with zero attributes; a `<div
onclick>` needs `role`, `tabindex`, a keydown handler and still gets it subtly wrong. Screen readers
also navigate *by* semantics: landmark list, headings list, links list, form controls list. If the
page is divs, those lists are empty and the user has to read linearly. WCAG 2.2 SC 1.3.1 (Info and
Relationships) and 4.1.2 (Name, Role, Value) are mostly satisfied by picking the right element.

## Pattern

```html
<body class="min-h-dvh flex flex-col bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
  <header class="border-b border-gray-200 dark:border-gray-800">
    <nav aria-label="Main" class="mx-auto flex max-w-6xl items-center gap-6 p-4">
      <a href="/" class="font-semibold">Acme</a>
      <ul class="flex gap-4">
        <li><a href="/docs" class="hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">Docs</a></li>
        <li><a href="/pricing" aria-current="page" class="font-medium">Pricing</a></li>
      </ul>
      <button type="button" class="ml-auto rounded-md bg-blue-600 px-3 py-1.5 text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
        Open menu
      </button>
    </nav>
  </header>

  <main id="main" class="mx-auto w-full max-w-6xl flex-1 p-4">
    <h1 class="text-3xl font-bold">Pricing</h1>

    <section aria-labelledby="plans-heading" class="mt-8">
      <h2 id="plans-heading" class="text-xl font-semibold">Plans</h2>
      <ul class="mt-4 grid gap-4 sm:grid-cols-2">
        <li class="rounded-lg border p-4">
          <h3 class="font-semibold">Starter</h3>
          <p>For side projects. <strong>Free</strong> forever.</p>
          <a href="/signup?plan=starter" class="mt-2 inline-block underline">Start free</a>
        </li>
        <li class="rounded-lg border p-4">
          <h3 class="font-semibold">Team</h3>
          <p><data value="29">$29</data> per seat, monthly.</p>
          <a href="/signup?plan=team" class="mt-2 inline-block underline">Start trial</a>
        </li>
      </ul>
    </section>

    <article class="mt-12">
      <h2 class="text-xl font-semibold">Why we charge per seat</h2>
      <p>Published <time datetime="2026-10-01">1 October 2026</time>.</p>
      <details class="mt-4 rounded-md border p-3">
        <summary class="cursor-pointer font-medium">Show the full breakdown</summary>
        <p class="mt-2">Seats map to people who log in at least once a month.</p>
      </details>
    </article>

    <aside aria-label="Related" class="mt-12 border-t pt-4">
      <h2 class="font-semibold">See also</h2>
      <ul class="list-inside list-disc"><li><a href="/faq" class="underline">FAQ</a></li></ul>
    </aside>
  </main>

  <footer class="border-t p-4 text-sm">
    <p>&copy; 2026 Acme. <a href="/privacy" class="underline">Privacy</a></p>
  </footer>
</body>
```

Decisions baked in:

- **One `<main>`**, one `<h1>`, exactly one `<header>` and `<footer>` as direct `body` children so
  they map to the `banner` and `contentinfo` landmarks (inside `<article>` or `<section>` they do not).
- **`<nav aria-label>`** when there is more than one nav; the label is what the landmark list shows.
- **`<section aria-labelledby>`** turns a plain section into a `region` landmark. A `<section>`
  without an accessible name is just a div, which is fine for purely visual grouping.
- **`<a>` navigates, `<button>` acts.** Changes the URL: link. Opens a menu, submits, toggles: button.
  Always `type="button"` on buttons outside forms so a stray form wrapper cannot submit them.
- **`<ul>`/`<ol>`** for anything that is a set; screen readers announce "list, 2 items" so users know
  the size before reading.
- **`<details>/<summary>`** is a free accessible disclosure with keyboard support and no JS.
- **`<time datetime>`**, `<data value>`, `<strong>`, `<em>`, `<abbr title>` carry meaning that a
  styled `<span>` loses.

## Variations

- **Blog post page**: `<main><article><h1>…</h1><p><time>…</time></p>…</article></main>`; put author
  and tags inside `<header>` within the article, comments in a `<section aria-labelledby>`.
- **Multiple articles on one page** (feed): each card is an `<article>` with its own `<h2>`; the
  page `<h1>` names the feed.
- **Form pages**: `<form>` with `<fieldset><legend>` per group, `<label for>` on every control, and a
  `<button type="submit">`; see `web-form-layout`.
- **Tabular data**: a real `<table>` with `<caption>`, `<thead>`, `<th scope="col|row">`; never a
  grid of divs for data that has rows and columns.

## Pitfalls

- `<div class="button">` or `<a href="#" onclick>` for actions: not keyboard operable, wrong role,
  and `href="#"` scrolls to top. Use `<button type="button">`.
- Skipping heading levels (h1 then h3) or choosing headings by font size. Pick the level by outline,
  then style with Tailwind (`text-sm font-semibold` on an `<h2>` is fine).
- Nesting landmarks you do not mean: a `<header>` inside `<main>` is not a banner; a `<nav>` around
  three footer links is noise. Use `<nav>` for real navigation blocks only.
- Using `<section>` as a styled div everywhere. It only earns a role with a name; otherwise it is
  neutral. That is acceptable, but do not expect it to help navigation.
- Replacing semantics with Tailwind: `list-none` keeps list semantics in most browsers, but Safari
  drops list role when `list-style: none` is set; add `role="list"` on the `<ul>` if the list
  matters to announce.
- `<br>` to create spacing or fake paragraphs, `<b>`/`<i>` where `<strong>`/`<em>` is meant,
  `<table>` for layout. All three confuse the reading order or the meaning.

## Related skills

- `web-a11y-aria-patterns`
- `web-a11y-skip-links-and-landmarks`
- `web-a11y-keyboard-and-focus`
- `web-seo-content-structure`
- `web-layout-page-shell`
- `web-form-layout`
