---
name: web-craft-code-structure
description: 'Restructure a vibe-coded site without a framework: a huge index.html becomes src/ partials and a 20-line build script, pasted class strings become @utility components, magic values become @theme tokens, inline onclick/style become data-* hooks in ES modules, dead code goes. Use when a user says "the file is huge", "clean up this HTML" or "this code looks AI generated".'
---

# Code structure that does not look vibe-coded

Generated sites share a shape: a single 2,000-line `index.html`, the same `flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow` pasted nine times, `onclick="toggleMenu()"` next to `style="margin-top: 37px"`, ids like `div1` and `section3`, a `<script>` at the top of `<body>` that queries elements that do not exist yet, forty `console.log('here')`, and 300 lines commented out "just in case". Each one is a decision deferred; together they make the site unmaintainable and visibly careless. None of them needs React to fix. The cure is three moves: **partials** for repetition in markup, **tokens and `@utility`** for repetition in classes, **modules on `data-*` hooks** for behaviour.

## Pattern

Before: everything in one file, every value a one-off.

```html
<body>
  <script>function toggleMenu(){document.getElementById('div4').style.display='block'}</script>
  <nav id="div1" style="padding: 18px 37px; border-bottom: 1px solid #e5e7eb">
    <button onclick="toggleMenu()" class="rounded-xl border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium shadow-sm hover:shadow-md transition-shadow">Menu</button>
  </nav>
  <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">…</div>
  <div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">…</div>
  <!-- <div class="old-card">…150 lines…</div> -->
  <script>console.log('loaded'); /* …900 more lines… */</script>
</body>
```

After: a `src/` layout where every file has one job.

```
src/
  partials/   header.html  footer.html  card-plan.html
  pages/      index.html   pricing.html         # use <!-- @include partials/header.html -->
  css/        input.css                         # @theme tokens + @utility components
  js/         main.js  features/menu.js  features/pricing-toggle.js
build.mjs                                       # 20 lines, no dependencies
dist/                                           # output, never edited by hand
```

```js
// build.mjs: resolve <!-- @include path --> recursively, copy js, run Tailwind. node build.mjs
import { readFileSync, writeFileSync, mkdirSync, readdirSync, cpSync } from 'node:fs';
import { execSync } from 'node:child_process';

const INCLUDE = /<!--\s*@include\s+(\S+)\s*-->/g;
const render = (file) =>
  readFileSync(`src/${file}`, 'utf8').replace(INCLUDE, (_, path) => render(path));

mkdirSync('dist', { recursive: true });
for (const page of readdirSync('src/pages')) writeFileSync(`dist/${page}`, render(`pages/${page}`));
cpSync('src/js', 'dist/js', { recursive: true });
execSync('npx @tailwindcss/cli -i src/css/input.css -o dist/css/site.css --minify', { stdio: 'inherit' });
```

```css
/* src/css/input.css: the 120-character string becomes one word, the magic numbers become tokens */
@import "tailwindcss";
@theme {
  --spacing-gutter: 2.25rem;              /* was padding: 37px */
  --color-line: oklch(92% 0.005 80);      /* was #e5e7eb repeated 23 times */
  --radius-card: 0.875rem;
}
@utility card {
  @apply rounded-card bg-white p-6 ring-1 ring-black/5 motion-safe:transition-shadow hover:shadow-md;
}
@utility btn-secondary {
  @apply inline-flex items-center rounded-md border border-line bg-white px-4 py-2 text-sm font-medium hover:bg-stone-50;
}
```

```html
<!-- src/pages/index.html -->
<!-- @include partials/header.html -->
<main class="mx-auto max-w-6xl px-gutter">
  <section data-feature="pricing" class="grid gap-6 md:grid-cols-3">
    <!-- @include partials/card-plan.html -->
  </section>
</main>
<!-- @include partials/footer.html -->
<script type="module" src="/js/main.js"></script>   <!-- modules are deferred: DOM is ready, no load listener -->
```

```js
// src/js/main.js: one entry, one module per feature, mounted by hook, nothing global
import { initMenu } from './features/menu.js';
import { initPricingToggle } from './features/pricing-toggle.js';

const features = { menu: initMenu, pricing: initPricingToggle };
for (const root of document.querySelectorAll('[data-feature]')) {
  features[root.dataset.feature]?.(root);
}
```

```js
// src/js/features/menu.js: replaces onclick="toggleMenu()" and style.display
export function initMenu(root) {
  const button = root.querySelector('[data-js="toggle"]');
  const panel = root.querySelector('[data-js="panel"]');
  if (!button || !panel) return;
  button.addEventListener('click', () => {
    const open = panel.toggleAttribute('hidden') === false;
    button.setAttribute('aria-expanded', String(open));
  });
}
```

## Variations

- **Python instead of Node.** Same idea in 12 lines: `re.sub(r'<!--\s*@include\s+(\S+)\s*-->', lambda m: render(m[1]), src)` over `src/pages/*.html`, then `subprocess.run(['npx', '@tailwindcss/cli', ...])`. Pick whichever runtime the project already has.
- **Server-side includes.** Netlify, Apache (`Options +Includes`) and nginx (`ssi on;`) resolve `<!--#include virtual="/partials/header.html" -->` at request time, so no build step; the cost is that the partial boundaries are invisible to a local `file://` preview.
- **Partials with slots.** Keep the build script dumb; when a partial needs different text per page, make it a `<template>` plus a four-line JS `cloneNode` fill, or render the varying part in the page and include only the shared chrome.
- **When `@utility` is wrong.** Only promote a class string once it appears three or more times unchanged. Two cards with slightly different padding are two cards, not a component with a variant prop.

## Pitfalls

- `@apply` inside `@utility` is for the five or six true components (card, btn, input, badge). Thirty `@utility` rules recreate Bootstrap and lose the point of utilities; see `web-css-layers-and-organization`.
- A `<script>` without `type="module"` or `defer` at the top of `<body>` runs before the elements below it exist; `getElementById` returns `null` and the fix is not a `setTimeout`. Modules are deferred by definition.
- Commented-out blocks are not a backup, they are noise that confuses the next search. Delete them; git has the history. Same for `console.log`: keep errors (`console.error` in a `catch`), remove traces.
- Ids are for `<label for>`, anchors and ARIA relationships; `id="div3"` on a section is none of those. Sections get `id="pricing"` so `/#pricing` works, and behaviour hooks go on `data-js`.
- `style="margin-top: 37px"` usually patches a missing `gap`, `leading` or `shrink-0`; find the cause before replacing it with `mt-[37px]`, which is the same bug in a Tailwind costume.
- The build script must not grow: once it needs frontmatter, loops or a data file, that is a static-site generator and Eleventy or Astro will do it better than 200 lines of your own.

## Related skills

- `web-js-modules-and-structure`
- `web-js-clean-code`
- `web-css-layers-and-organization`
- `web-css-variables-theming`
- `web-ship-project-setup`
- `web-craft-consistency-audit`
