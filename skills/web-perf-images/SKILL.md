---
name: web-perf-images
description: Produce fast-loading images - compressed WebP/AVIF with fallbacks, lazy loading, fetchpriority on the hero, explicit width/height to kill layout shift - plus a one-command conversion script. Use whenever a user says images are slow, "optimize images", "my Lighthouse score is bad because of images", "layout shift", "lazy load", "convert to WebP", or asks how big an image should be.
---

# Image performance

Images are usually 50 to 80 percent of a page's bytes and the most common LCP element. Four moves fix most of it: ship modern formats at the right pixel size, tell the browser the dimensions so it reserves space (no CLS), load the one above-the-fold image first (`fetchpriority="high"`), and defer everything else (`loading="lazy"`). Everything here is plain HTML plus one small Node script; no runtime library.

## Pattern

The hero image (LCP candidate) and a below-the-fold image, done correctly:

```html
<!-- Hero: eager, high priority, modern formats, explicit size -->
<picture>
  <source type="image/avif" srcset="/img/hero-800.avif 800w, /img/hero-1600.avif 1600w" sizes="100vw">
  <source type="image/webp" srcset="/img/hero-800.webp 800w, /img/hero-1600.webp 1600w" sizes="100vw">
  <img src="/img/hero-1600.jpg" alt="Team working at a long table" width="1600" height="900"
       fetchpriority="high" decoding="async" class="h-auto w-full object-cover">
</picture>

<!-- Everything below the fold: lazy, async decode, still sized -->
<img src="/img/card-1.webp" alt="" width="640" height="400" loading="lazy" decoding="async"
     class="aspect-[8/5] h-auto w-full rounded-lg object-cover">
```

`width`/`height` give the intrinsic ratio; `h-auto w-full` lets CSS scale it while the ratio reserves space. Add a `<link>` in `<head>` so the hero starts downloading before the parser reaches it:

```html
<link rel="preload" as="image" href="/img/hero-1600.avif" type="image/avif"
      imagesrcset="/img/hero-800.avif 800w, /img/hero-1600.avif 1600w" imagesizes="100vw">
```

Generate the sizes and formats once with `sharp` (dev dependency only; runs on Windows and Unix):

```bash
npm i -D sharp
```

```js
// scripts/images.mjs - node scripts/images.mjs
import sharp from "sharp";
import { readdir, mkdir } from "node:fs/promises";
import path from "node:path";

const SRC = "src/img", OUT = "dist/img", WIDTHS = [800, 1600];
await mkdir(OUT, { recursive: true });
for (const file of await readdir(SRC)) {
  if (!/\.(jpe?g|png)$/i.test(file)) continue;
  const base = path.parse(file).name;
  for (const w of WIDTHS) {
    const img = sharp(path.join(SRC, file)).resize({ width: w, withoutEnlargement: true });
    await img.clone().avif({ quality: 50 }).toFile(`${OUT}/${base}-${w}.avif`);
    await img.clone().webp({ quality: 75 }).toFile(`${OUT}/${base}-${w}.webp`);
    await img.clone().jpeg({ quality: 80, mozjpeg: true }).toFile(`${OUT}/${base}-${w}.jpg`);
  }
}
```

```json
{ "scripts": { "images": "node scripts/images.mjs" } }
```

## Variations

- **Fixed-width images (avatars, thumbnails)**: skip `sizes`, use density descriptors: `srcset="a.webp 1x, a@2x.webp 2x"`. Export at exactly 1x and 2x of the rendered CSS size, never larger.
- **Grid of cards**: set `sizes` to the real rendered width, e.g. `sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"`; the browser then picks the smallest sufficient file.
- **Background images**: CSS backgrounds cannot be lazy or `srcset`; prefer an absolutely positioned `<img>` with `object-cover` inside a `relative` box so all the attributes above still apply.
- **SVG for logos and icons**: no conversion needed; minify with `npx svgo -f src/icons -o dist/icons` and inline the ones used above the fold.

## Pitfalls

- Missing `width`/`height` is the number one CLS cause. Always set them, even on lazy images; `h-auto` keeps them responsive. For images whose ratio you do not know at build time, wrap in a box with `aspect-video` or `aspect-[4/3]`.
- Never put `loading="lazy"` on the hero or anything in the first viewport; it delays LCP by a full round trip. Lazy-load only what is below the fold.
- `fetchpriority="high"` on more than one image cancels its benefit. One per page.
- AVIF encoding is slow and large images at high quality can be bigger than WebP; keep AVIF quality around 45-55 and check file sizes (`ls -l dist/img`).
- Uploading a 4000px photo and shrinking it with CSS wastes bytes and decode time. The largest `srcset` candidate should be about 2x the widest rendered CSS width, no more.
- `decoding="async"` is safe everywhere except when the image is needed in the same frame as text that references it (rare); default to it.
- `<img>` elements with `alt=""` are decorative and skipped by screen readers; content images need real alt text (see `web-a11y-images-and-media`).

## Related skills

- `web-design-images` (art direction, placeholders, `<picture>` in depth)
- `web-css-aspect-ratio-media`
- `web-perf-web-vitals`
- `web-perf-caching-and-service-worker`
- `web-a11y-images-and-media`
