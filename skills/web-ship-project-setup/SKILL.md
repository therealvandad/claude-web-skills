---
name: web-ship-project-setup
description: Scaffold a plain HTML + Tailwind CSS v4 project - folder layout, `@tailwindcss/cli` install, `src/input.css` with `@import "tailwindcss"`, npm scripts for watch/build/serve that work on Windows and Unix, live reload, `.gitignore`, editor config. Use when a user says "start a new site", "set up Tailwind", "project structure", "how do I run this locally", or "npm scripts for a static site".
---

# Project setup

One folder of source, one folder of output, three npm scripts. Tailwind v4 needs no `tailwind.config.js` and no `content` array: the CLI scans every file in the project that is not gitignored, so `src/**/*.html` and `src/**/*.js` are picked up automatically. The only decision is whether HTML lives in `src/` and gets copied to `dist/` (clean, lets you hash assets later) or whether `dist/` is just the CSS output beside HTML at the root (simplest). This pattern uses `src/` + `dist/`.

## Pattern

```text
my-site/
  src/
    index.html
    about.html
    input.css          # Tailwind entry: @import, @theme, your CSS
    js/main.js
    img/  fonts/  icons/
  dist/                # build output, gitignored, this is what gets deployed
  scripts/copy.mjs
  package.json
  .gitignore
```

```bash
npm init -y
npm i -D tailwindcss @tailwindcss/cli serve concurrently
```

```css
/* src/input.css */
@import "tailwindcss";
@theme {
  --color-brand: oklch(0.55 0.2 260);
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
}
```

```json
{
  "scripts": {
    "copy": "node scripts/copy.mjs",
    "css": "tailwindcss -i src/input.css -o dist/output.css",
    "dev": "concurrently -k \"npm:css -- --watch\" \"npm:copy -- --watch\" \"serve dist -l 3000\"",
    "build": "npm run copy && npm run css -- --minify",
    "preview": "serve dist"
  }
}
```

```js
// scripts/copy.mjs - copies everything except input.css from src to dist; --watch keeps going
import { cp, watch } from "node:fs/promises";
const copy = () => cp("src", "dist", { recursive: true, filter: p => !p.endsWith("input.css") });
await copy();
if (process.argv.includes("--watch")) {
  console.log("watching src/");
  for await (const _ of watch("src", { recursive: true })) await copy();
}
```

```html
<!-- src/index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My site</title>
  <link rel="stylesheet" href="/output.css">
  <script type="module" src="/js/main.js"></script>
</head>
<body class="min-h-dvh bg-white font-sans text-gray-900 antialiased">
  <main class="mx-auto max-w-5xl px-4 py-12 sm:px-6">
    <h1 class="text-3xl font-bold text-brand">It works</h1>
  </main>
</body>
</html>
```

```gitignore
node_modules/
dist/
.DS_Store
Thumbs.db
.env
```

`npm run dev` starts the Tailwind watcher, the copier and a static server at `http://localhost:3000`. `npm run build` produces a deployable `dist/`. `npx` resolves `tailwindcss` to `node_modules/.bin/tailwindcss` on all platforms, so the scripts need no `./` prefixes or `cross-env`.

## Variations

- **Flat layout, no copying**: keep `index.html` at the root, put `input.css` in `src/`, output to `dist/output.css`, link `/dist/output.css`. Scripts shrink to `css` and `dev`. Fine for one-page sites; outgrows itself once you want hashing or a clean deploy folder.
- **Live reload in the browser**: `serve` does not reload. Use Vite as a dev server only (`npm i -D vite @tailwindcss/vite`, `vite.config.js` with the plugin, `npm run dev` = `vite`); the `@tailwindcss/vite` plugin replaces the CLI entirely and `vite build` emits hashed assets. Keep the HTML plain; no framework is involved.
- **Watch extra folders**: if templates live outside the project (or inside a gitignored folder) add `@source "../templates";` after the `@import` in `input.css`; the path is relative to the CSS file.
- **Prototype without Node**: a single HTML file with `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`; switch to the CLI before shipping.

## Pitfalls

- `dist/` must be gitignored, otherwise Tailwind scans its own output and the generated CSS grows every build.
- `tailwindcss` is the v4 engine; the CLI is a separate package `@tailwindcss/cli`. Installing only `tailwindcss` gives "command not found" on `npx tailwindcss`.
- Absolute paths (`/output.css`) work on a local server and on hosts that serve from the root; on GitHub Pages project sites (`user.github.io/repo/`) they break. Use relative paths (`./output.css`) or set a `<base href>` if you deploy there (see `web-ship-static-hosting`).
- On Windows, `fs.watch` with `recursive: true` works; on Linux it needs Node 20 or newer. Pin `"engines": { "node": ">=20" }`.
- `concurrently -k` kills all processes when one exits; without it a crashed watcher leaves the server running and the CSS silently stale.
- Do not open `index.html` by double-clicking (`file://`): ES modules and `fetch` are blocked there. Always use the dev server.
- An `.editorconfig` (`indent_style = space`, `indent_size = 2`, `end_of_line = lf`) prevents CRLF churn between Windows and Unix contributors.

## Related skills

- `web-ship-tailwind-production`
- `web-ship-static-hosting`
- `web-js-modules-and-structure`
- `web-css-variables-theming`
- `web-css-layers-and-organization`
