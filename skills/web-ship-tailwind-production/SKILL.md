---
name: web-ship-tailwind-production
description: Produce a minimal, minified production Tailwind CSS v4 build - `@tailwindcss/cli --minify`, how v4 automatic content detection works, when to add `@source`, safelisting dynamic classes with `@source inline()`, and checks that no class was dropped. Use when a user says "build for production", "my CSS is huge", "classes missing in production", "purge", "safelist", or "Tailwind content config".
---

# Tailwind v4 production build

Tailwind v4 generates only the utilities it finds in your source files, so "purging" is no longer a step: there is nothing to purge, only classes that were never generated because the scanner did not see them. The production build is the same CLI command with `--minify`; the real work is making sure every class the page needs is visible to the scanner as a complete string. A typical site lands at 10-30 KB gzipped.

## Pattern

```bash
npm i -D tailwindcss @tailwindcss/cli
npx @tailwindcss/cli -i src/input.css -o dist/output.css --minify
```

```json
{
  "scripts": {
    "css:dev": "tailwindcss -i src/input.css -o dist/output.css --watch",
    "css:build": "tailwindcss -i src/input.css -o dist/output.css --minify",
    "css:report": "node -e \"const z=require('zlib'),f=require('fs');const b=f.readFileSync('dist/output.css');console.log('raw',b.length,'gzip',z.gzipSync(b).length,'brotli',z.brotliCompressSync(b).length)\""
  }
}
```

Content detection in v4: the CLI scans every file under the current working directory, skipping anything in `.gitignore`, binary files, and `node_modules`. No `content: [...]` array exists. Adjust it only in CSS:

```css
/* src/input.css */
@import "tailwindcss";

/* Templates outside the scanned tree, or inside a gitignored folder (path relative to this file) */
@source "../../shared-templates";

/* Classes built at runtime that never appear as whole strings in source */
@source inline("bg-{red,green,amber}-{100,500} text-{red,green,amber}-800");

/* Stop scanning a noisy folder (large JSON fixtures, vendored code) */
@source not "../fixtures";

/* Turn off auto-detection entirely and list sources explicitly */
/* @import "tailwindcss" source(none); @source "../src"; */
```

Verify after building that nothing was lost. The quickest check is to grep the built CSS for a class you know is used only in one obscure place:

```bash
grep -c "\.sm\\\\:grid-cols-3" dist/output.css      # 1 = present, 0 = missing
```

A more thorough cross-platform check extracts every `class="..."` token from the HTML and reports those absent from the CSS (false positives are normal for non-Tailwind classes; look for real utilities in the list):

```js
// scripts/check-classes.mjs - node scripts/check-classes.mjs
import { readFileSync, readdirSync } from "node:fs";
const css = readFileSync("dist/output.css", "utf8");
const used = new Set();
for (const f of readdirSync("dist").filter(n => n.endsWith(".html")))
  for (const m of readFileSync(`dist/${f}`, "utf8").matchAll(/class="([^"]+)"/g))
    m[1].split(/\s+/).forEach(c => used.add(c));
const esc = c => c.replace(/[^a-zA-Z0-9-]/g, ch => "\\" + ch);
const missing = [...used].filter(c => c && !css.includes("." + esc(c)));
console.log(missing.length ? "not in CSS:\n" + missing.join("\n") : "all classes present");
```

## Variations

- **Vite instead of the CLI**: `@tailwindcss/vite` plugin; `vite build` minifies, hashes and rewrites links. Content detection and `@source` behave identically.
- **PostCSS pipeline** (you already run PostCSS for other reasons): `@tailwindcss/postcss` in `postcss.config.js`; no autoprefixer needed, v4 handles vendor prefixes and nesting itself.
- **Class toggle for dark mode**: add `@custom-variant dark (&:where(.dark, .dark *));` in `input.css`; it is part of the build input, not a config option.
- **Reduce size further**: drop unused theme namespaces, e.g. `@theme { --color-*: initial; --color-brand: ...; }` removes the whole default palette so only your tokens generate utilities (also stops autocomplete suggesting colors you do not use).

## Pitfalls

- Classes assembled in JS (`` `text-${color}-500` ``) are never generated. Write complete class names in a lookup object (`const tone = { ok: "text-green-600", bad: "text-red-600" }`) or add `@source inline(...)`.
- Classes that appear only in a gitignored file (generated HTML, a CMS export) are invisible to the scanner; add `@source` for that folder.
- The built CSS committed by mistake, or an old `output.css` in `src/`, gets scanned too and inflates the output; keep the output file in gitignored `dist/`.
- `--minify` only minifies; it does not change which classes are generated. If a class is missing in production but present in dev, the cause is the scanned files, not minification (typically the CI checkout differs from local, e.g. a build step that deletes `src/` before running Tailwind).
- `tailwind.config.js` from v3 is ignored in v4 unless you add `@config "./tailwind.config.js";` explicitly. Migrate theme values to `@theme` instead (`npx @tailwindcss/upgrade` automates most of it).
- Cross-platform scripts: avoid `rm -rf dist && ...` in `package.json`; use `node -e "require('fs').rmSync('dist',{recursive:true,force:true})"` or the `rimraf` package so Windows users can build.

## Related skills

- `web-ship-project-setup`
- `web-ship-static-hosting`
- `web-perf-css-and-js-loading`
- `web-css-variables-theming`
- `web-design-dark-mode`
