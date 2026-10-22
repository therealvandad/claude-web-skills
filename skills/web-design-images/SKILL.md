---
name: web-design-images
description: 'Mark up responsive images the right way: `picture` with AVIF/WebP fallbacks, `srcset`/`sizes` for resolution switching, art direction per breakpoint, `width`/`height` to prevent layout shift, blurred or color placeholders, and Tailwind `object-*`/`aspect-*` containers. Use whenever a user adds a photo, hero image, thumbnail, avatar, or asks why images look blurry, load slowly, or jump the layout.'
---

# Images

An `<img>` tag with one JPEG sends a 2000px file to a 360px phone and shifts the layout when it lands. Three attributes fix nearly all of it: `srcset` + `sizes` let the browser pick the right width, `width` + `height` reserve the box before the file arrives, and `<picture>` offers modern formats (AVIF is ~50% smaller than JPEG) with a safe fallback. Tailwind handles the presentation side: the container's aspect ratio and how the image fills it.

## Pattern

```html
<!-- 1. Content image: resolution switching. The browser picks from srcset using sizes. -->
<figure class="mx-auto max-w-3xl">
  <picture>
    <source type="image/avif"
            srcset="/img/harbor-480.avif 480w, /img/harbor-960.avif 960w, /img/harbor-1440.avif 1440w"
            sizes="(min-width: 48rem) 48rem, 100vw">
    <source type="image/webp"
            srcset="/img/harbor-480.webp 480w, /img/harbor-960.webp 960w, /img/harbor-1440.webp 1440w"
            sizes="(min-width: 48rem) 48rem, 100vw">
    <img src="/img/harbor-960.jpg"
         srcset="/img/harbor-480.jpg 480w, /img/harbor-960.jpg 960w, /img/harbor-1440.jpg 1440w"
         sizes="(min-width: 48rem) 48rem, 100vw"
         width="1440" height="960" loading="lazy" decoding="async"
         alt="Fishing boats moored in Reykjavik harbor at dusk"
         class="h-auto w-full rounded-xl bg-gray-200 dark:bg-gray-800">
  </picture>
  <figcaption class="mt-2 text-sm text-gray-500">Reykjavik, October.</figcaption>
</figure>

<!-- 2. Art direction: a different crop on small screens (square portrait), wide landscape on large. -->
<picture>
  <source media="(min-width: 64rem)" srcset="/img/team-wide.avif" type="image/avif" width="1600" height="600">
  <source media="(min-width: 64rem)" srcset="/img/team-wide.jpg" width="1600" height="600">
  <img src="/img/team-square.jpg" width="800" height="800" alt="The four founders in the workshop"
       class="aspect-square w-full object-cover lg:aspect-[8/3]" fetchpriority="high">
</picture>

<!-- 3. Fixed-ratio card thumbnail: the box is sized by the container, the image fills it. -->
<a href="/post/1" class="group block overflow-hidden rounded-lg">
  <img src="/img/post-1-640.webp" srcset="/img/post-1-640.webp 640w, /img/post-1-1280.webp 1280w"
       sizes="(min-width: 64rem) 20rem, (min-width: 40rem) 50vw, 100vw"
       width="1280" height="720" loading="lazy" alt=""
       class="aspect-video w-full object-cover transition-transform duration-300 motion-safe:group-hover:scale-105">
</a>

<!-- 4. Avatar: object-cover centers on faces well enough; a fallback initial behind it covers 404s. -->
<span class="relative inline-flex size-10 items-center justify-center rounded-full bg-indigo-100 font-medium text-indigo-700">
  AK
  <img src="/avatars/ak.jpg" width="80" height="80" alt="" loading="lazy"
       class="absolute inset-0 size-full rounded-full object-cover" onerror="this.remove()">
</span>
```

`sizes` is the part people skip: it tells the browser how wide the image will *render* so it can choose a file before CSS loads. Write it as the breakpoints in the layout, largest first, ending in a `100vw` default. Width descriptors (`960w`) beat density descriptors (`2x`) because they adapt to both viewport and DPR.

## Variations

- **Above-the-fold hero.** Drop `loading="lazy"`, add `fetchpriority="high"` and a `<link rel="preload" as="image" imagesrcset="..." imagesizes="...">` in `<head>` so the LCP image starts downloading before the parser reaches it.
- **Blur-up placeholder.** Inline a 20px-wide base64 version as a CSS background on the wrapper (`style="background-image:url(data:...)"` with `bg-cover blur-sm`) and remove the blur in the `load` event; or just set `bg-gray-200` on the `<img>` for a cheap color placeholder.
- **Background images.** Only for purely decorative textures: `bg-[url(/img/grain.png)] bg-cover bg-center`. Anything with meaning must be an `<img>` so it gets `alt`, lazy loading and `srcset`.
- **Full-bleed in a constrained column.** `w-screen max-w-none relative left-1/2 -translate-x-1/2` breaks the image out of `max-w-prose` without touching the parent.

## Pitfalls

- Omitting `width` and `height` is the main cause of CLS; the values are the file's intrinsic pixels, and `class="h-auto w-full"` keeps the ratio while the box scales.
- `loading="lazy"` on the first visible image delays LCP by a full round trip; lazy-load only what is below the fold.
- `object-cover` crops from the center; for portraits set `object-[50%_20%]` (or `object-top`) so heads are not cut off.
- A `<source>` without `type` for AVIF forces browsers that cannot decode it to download and fail; always set `type` on format sources.
- `sizes="100vw"` on a 320px thumbnail makes phones fetch the 1440w file. Match `sizes` to the real rendered width of each slot.
- Empty `alt=""` is correct for decorative images only; a thumbnail inside a link whose text is the title can be `alt=""`, but a standalone photo needs a real description. See `web-a11y-images-and-media`.

## Related skills

- `web-perf-images`
- `web-css-aspect-ratio-media`
- `web-a11y-images-and-media`
- `web-layout-card-grid`
- `web-perf-web-vitals`
