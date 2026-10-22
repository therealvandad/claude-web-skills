---
name: web-js-modules-and-structure
description: Organise a static site's JavaScript as native ES modules - folder layout, one entry script per page, feature modules initialised from data attributes, an import map, no bundler. Use whenever a user asks "how should I structure my JS files", "import/export in the browser", "script type=module", "import map", or "do I need webpack/Vite for this".
---

# ES modules and file structure, no bundler required

Every evergreen browser runs ES modules natively, so a Tailwind static site needs no bundler for its JavaScript: `<script type="module">` is deferred by default, strict-mode, scoped (no accidental globals), and `import`s are cached per URL. The structure that scales from one page to fifty: **one entry file per page** that imports **feature modules**, each feature discovering its own HTML via a `data-*` attribute and doing nothing when that markup is absent. Shared helpers live in `lib/`. A bundler becomes worthwhile only when you have dozens of modules on one page (request waterfall) or need npm packages that are not ESM-ready.

## Pattern

```
/
├─ index.html
├─ pricing.html
├─ css/  input.css → output.css          (Tailwind CLI, see web-ship-project-setup)
└─ js/
   ├─ pages/
   │  ├─ home.js                          entry: imports the features this page uses
   │  └─ pricing.js
   ├─ features/
   │  ├─ navbar.js                        export function initNavbar(root) {...}
   │  ├─ pricing-toggle.js
   │  └─ newsletter-form.js
   └─ lib/
      ├─ dom.js                           $, $$, on, create
      ├─ api.js                           request()
      └─ storage.js
```

```html
<!-- index.html -->
<script type="importmap">
  { "imports": { "lib/": "/js/lib/", "features/": "/js/features/" } }
</script>
<script type="module" src="/js/pages/home.js"></script>
<!-- modulepreload shortens the import waterfall for modules you know this page needs -->
<link rel="modulepreload" href="/js/features/navbar.js">
<link rel="modulepreload" href="/js/lib/dom.js">

<header data-feature="navbar">…</header>
<form data-feature="newsletter">…</form>
```

```js
// /js/pages/home.js  (entry: wire features to markup, nothing else)
import { initNavbar } from 'features/navbar.js';
import { initNewsletter } from 'features/newsletter-form.js';

mount('navbar', initNavbar);
mount('newsletter', initNewsletter);

/** Run init for every element carrying data-feature="name"; one failure must not stop the others. */
function mount(name, init) {
  for (const root of document.querySelectorAll(`[data-feature="${name}"]`)) {
    try { init(root); root.dataset.featureReady = ''; }
    catch (error) { console.error(`feature "${name}" failed`, error); }
  }
}
```

```js
// /js/features/newsletter-form.js  (feature: pure function of its root element)
import { request } from 'lib/api.js';
import { $ } from 'lib/dom.js';

export function initNewsletter(root) {
  const status = $('[data-js="status"]', root);
  root.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      await request(root.action, { method: 'POST', body: new FormData(root) });
      status.textContent = 'Thanks, check your inbox.';
    } catch {
      status.textContent = 'Could not subscribe. Try again.';
    }
  });
}
```

```js
// Lazy feature: load the code only when its markup is present (big widgets, rarely used pages)
if (document.querySelector('[data-feature="map"]')) {
  const { initMap } = await import('features/map.js');     // top-level await works in modules
  mount('map', initMap);
}
```

## Variations

- **Small sites (1-5 pages)**: skip `pages/`; a single `/js/main.js` entry that mounts every feature is fine because features no-op when their markup is missing.
- **Shared layout script**: put navbar/theme/analytics in `js/site.js` and load it on every page with its own `<script type="module">`; page entries load only page-specific features. Modules are evaluated once even if imported by both.
- **Constants and config**: `export const config = Object.freeze({ apiBase: '/api' })` in `lib/config.js`; no globals, and the frozen object stops accidental mutation.
- **When you do adopt a bundler** (Vite is the natural choice with Tailwind), keep this exact layout; Vite consumes native ESM entries and the import map becomes `resolve.alias`.

## Pitfalls

- `file://` blocks module imports (CORS). Always serve over HTTP: `npx serve`, `python -m http.server`, or the Tailwind CLI's companion dev server.
- Import paths must be real URLs: include the `.js` extension and start with `/`, `./`, `../` or an import-map key. Bare `import x from 'lodash'` fails without a map entry.
- Module scripts run after parsing, so `DOMContentLoaded` has usually already fired by the time an `async` import resolves; query the DOM directly instead of waiting for it.
- Module scripts are not visible to inline `onclick="..."` attributes; use `addEventListener` inside the module or `window.myApp = {...}` deliberately for one exported object.
- Deep import chains (page → feature → lib → lib) each cost a round trip before execution; `modulepreload` the known ones or merge tiny helpers into one `lib/dom.js`.
- Cache-busting: browsers cache modules by URL. For production add a hash or version query (`/js/pages/home.js?v=3`) or set proper cache headers; see `web-perf-caching-and-service-worker`.

## Related skills

- `web-ship-project-setup`
- `web-perf-css-and-js-loading`
- `web-js-dom-utilities`
- `web-js-clean-code`
- `web-js-web-components`
