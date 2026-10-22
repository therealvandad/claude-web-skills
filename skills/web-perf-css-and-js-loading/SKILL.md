---
name: web-perf-css-and-js-loading
description: Produce a `<head>` and script setup that never blocks rendering - one small Tailwind CSS file, critical CSS when it pays off, `type="module"` scripts, per-page entries, preconnect/preload hints, a size budget check. Use when a user says "render blocking", "eliminate render-blocking resources", "scripts slow my page", "where do I put the script tag", or "critical CSS".
---

# CSS and JS loading

The browser cannot paint until every stylesheet in `<head>` has arrived, and a classic `<script>` stops HTML parsing dead. For a static Tailwind site the fix is mostly ordering and attributes: one small CSS file (Tailwind v4 output for a typical site is 10-30 KB gzipped, so one file beats splitting), scripts as modules at the end of `<head>`, and resource hints only for things that genuinely load early. Inline critical CSS only when measurement shows the stylesheet request is the LCP bottleneck.

## Pattern

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Acme</title>

  <!-- 1. Hints for origins used in the first viewport only -->
  <link rel="preconnect" href="https://api.example.com">
  <link rel="preload" href="/fonts/inter-wght.woff2" as="font" type="font/woff2" crossorigin>

  <!-- 2. The one stylesheet; it is small, keep it blocking so there is no FOUC -->
  <link rel="stylesheet" href="/dist/output.css">

  <!-- 3. Scripts: modules are deferred by default and run in order after parsing -->
  <script type="module" src="/js/main.js"></script>
  <script type="module" src="/js/pages/home.js"></script>

  <!-- 4. Third-party, non-critical: async so it never blocks -->
  <script async src="https://plausible.io/js/script.js" data-domain="example.com"></script>
</head>
```

```js
// js/main.js - site-wide, tiny. Page-specific work lives in js/pages/*.js
import { initMenu } from "./menu.js";
initMenu(document.querySelector("[data-menu]"));

// Load heavy, rarely-used code only on demand
document.querySelector("[data-open-map]")?.addEventListener("click", async () => {
  const { showMap } = await import("./map.js");
  showMap();
}, { once: true });
```

Non-critical CSS (a print stylesheet, a rarely used page section) can load without blocking:

```html
<link rel="stylesheet" href="/dist/print.css" media="print">
<link rel="stylesheet" href="/dist/gallery.css" media="print" onload="this.media='all'">
```

Keep an eye on sizes with a script that fails CI when the budget is exceeded (works in Git Bash and Unix; use `node -e` so it is cross-platform):

```json
{
  "scripts": {
    "build:css": "tailwindcss -i src/input.css -o dist/output.css --minify",
    "check:size": "node -e \"const s=require('fs').statSync('dist/output.css').size;console.log('css',s,'bytes');if(s>60000)process.exit(1)\""
  }
}
```

## Variations

- **Inline critical CSS**: only for very large pages on slow networks. Extract the rules for the first viewport (the `critical` npm package does this: `npx critical index.html --inline --base dist > dist/index.html`), put them in a `<style>` block, and load the full sheet with the `media="print" onload` trick. Measure before and after; with a 20 KB stylesheet on HTTP/2 the gain is often zero.
- **No module support needed**: `type="module"` is supported by every browser since 2018; there is no reason to ship `nomodule` fallbacks any more.
- **Script must run before first paint** (theme class from `localStorage` to avoid a dark-mode flash): the one legitimate blocking inline script. Keep it under ten lines and place it before the stylesheet link, see `web-design-dark-mode`.
- **Multi-page sites**: one shared `main.js` plus one `pages/<name>.js` per page keeps each page's JS to what it uses; no bundler needed (see `web-js-modules-and-structure`). Add `<link rel="modulepreload" href="/js/menu.js">` for modules imported by `main.js` so the browser does not discover them one hop late.

## Pitfalls

- `defer` and `async` are ignored on inline scripts; move the code into a file or keep it tiny.
- `async` scripts run as soon as they arrive, in any order; never use `async` for code that other code depends on. Use `type="module"` (ordered, deferred) for your own code and `async` only for independent third-party snippets.
- A `<link rel="preload">` for something not used within a few seconds triggers a console warning and wastes bandwidth. Preload the font and the LCP image at most; let normal discovery handle the rest.
- `preconnect` to more than three or four origins costs more than it saves; each opens a socket and TLS handshake.
- Loading Tailwind via the Play CDN (`@tailwindcss/browser`) in production is render-blocking JS that compiles CSS on the client; it is for prototypes only. Build with `@tailwindcss/cli` (see `web-ship-tailwind-production`).
- Splitting CSS per page sounds efficient but loses the cross-page cache; one hashed, long-cached file is faster for the second page view.
- A huge inline `<style>` block is re-downloaded with every HTML page and cannot be cached; cap critical CSS at about 10 KB.

## Related skills

- `web-ship-tailwind-production`
- `web-js-modules-and-structure`
- `web-perf-fonts`
- `web-perf-web-vitals`
- `web-perf-caching-and-service-worker`
- `web-design-dark-mode`
