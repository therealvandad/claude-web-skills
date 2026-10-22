---
name: web-perf-fonts
description: 'Set up fast web fonts - self-hosted woff2, subsetting, `font-display: swap`, preload of the one critical file, variable fonts, and a `size-adjust` fallback that prevents text jumping - wired into Tailwind v4 `@theme`. Use when a user asks to "add a Google Font", says fonts flash or jump, "FOUT", "font loading is slow", or wants to self-host fonts.'
---

# Font performance

Fonts block text rendering and shift layout when the fallback is a different width. Self-host (no third-party DNS and connection), ship only woff2, subset to the characters you use, preload the one body-text file, and tune a local fallback with `size-adjust` so the swap is invisible. Prefer one variable font over four static weights; it is one request instead of four.

## Pattern

Download the variable woff2 (for Google Fonts, the `google-webfonts-helper` site or the `fontsource` npm package give you files; `npm i @fontsource-variable/inter` puts them in `node_modules/@fontsource-variable/inter/files/`). Copy to `src/fonts/`, then:

```css
/* src/input.css */
@import "tailwindcss";

@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-latin-wght.woff2") format("woff2");
  font-weight: 100 900;          /* variable range */
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+2000-206F, U+2074, U+20AC, U+2122, U+2212, U+FEFF, U+FFFD;
}

/* Fallback tuned to match Inter's metrics so the swap does not reflow */
@font-face {
  font-family: "Inter Fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}

@theme {
  --font-sans: "Inter", "Inter Fallback", ui-sans-serif, system-ui, sans-serif;
}
```

Preload only the file used for above-the-fold body text, in `<head>` before the stylesheet:

```html
<link rel="preload" href="/fonts/inter-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/dist/output.css">
```

`crossorigin` is required even for same-origin fonts; without it the preload is fetched twice. Tailwind's `font-sans` utility now uses the stack from `@theme`, so `<body class="font-sans">` is all the markup needs.

Subset a font you already have (removes glyphs you never render; typical 300 KB to 40 KB):

```bash
pip install fonttools brotli
pyftsubset src/fonts/Inter.ttf --output-file=src/fonts/inter-latin-wght.woff2 --flavor=woff2 --layout-features="*" --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+2000-206F,U+20AC,U+2122"
```

Get the override numbers for your fallback from the font's metrics (`npx fontaine` or the `@capsizecss/metrics` package publishes them for common fonts); the values above are Inter vs Arial.

## Variations

- **Static weights**: one `@font-face` per weight with `font-weight: 400` / `700`; only preload the 400. Never load more than three weights, and use `font-synthesis: none` on `body` if you ship 400 only, so the browser does not fake bold.
- **Display font for headings only**: skip the preload (it is not needed for first paint), keep `font-display: swap`, and give it its own `--font-display` token: `@theme { --font-display: "Fraunces", Georgia, serif; }` then use `font-display` as the utility.
- **Icon or logo font that must not swap**: `font-display: optional` renders the fallback if the font is not cached within about 100 ms and never swaps; the second visit uses the cached file. Good for brand fonts where a flash is worse than a one-visit fallback.
- **Google Fonts hosted (prototype only)**: `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` plus the stylesheet link with `&display=swap`. Move to self-hosting before launch; it saves two connections and ~200 ms.

## Pitfalls

- Preloading every weight delays everything else. Preload one file, the one whose text is in the first viewport.
- Fonts referenced from CSS resolve relative to the CSS file. If `output.css` lives in `dist/`, write absolute paths (`/fonts/...`) and make sure the build copies `src/fonts` to `dist/fonts` (see `web-ship-project-setup`).
- Forgetting `unicode-range` on a Latin subset is harmless, but forgetting to actually subset means the browser downloads Cyrillic and Greek you never use.
- Serve woff2 with `Cache-Control: public, max-age=31536000, immutable` and a hashed or versioned filename; fonts rarely change and should never be re-downloaded.
- `font-display: swap` without a metric-matched fallback causes CLS in the text itself. Either ship the `size-adjust` fallback or accept a small shift; do not use `block`, which hides text for up to 3 s.
- Hosting providers may not send the `font/woff2` MIME type by default; check the response header in devtools, since a wrong type can prevent caching on some CDNs.

## Related skills

- `web-design-typography-system`
- `web-perf-web-vitals`
- `web-perf-caching-and-service-worker`
- `web-perf-css-and-js-loading`
- `web-ship-project-setup`
