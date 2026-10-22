---
name: web-css-aspect-ratio-media
description: 'Keep images, videos and embeds at a fixed shape with aspect-ratio and object-fit in Tailwind v4: uniform card thumbnails, cover and contain modes, responsive YouTube/Vimeo iframes, avatars, and background-style image fills. Use whenever a user says images are "different sizes", thumbnails look stretched or squished, a video embed won''t resize, or asks about aspect ratio, object-fit, or responsive iframes.'
---

# Aspect ratio and media fitting

Images arrive in every shape; layouts need one. The modern answer is two properties: `aspect-ratio` on the box (it reserves the shape *before* the image loads, so nothing jumps) and `object-fit` on the media (it decides how the pixels fill that box). This replaces the old padding-bottom hack entirely. Always ship `width` and `height` attributes too: browsers use them to compute the ratio for the initial layout, which is what prevents Cumulative Layout Shift.

## Pattern

```html
<!-- 1. Card thumbnail: fixed 16:9 box, image fills and crops -->
<figure class="overflow-hidden rounded-xl">
  <img
    src="/img/post.jpg" alt="Hikers on a ridge at sunrise"
    width="1200" height="800" loading="lazy" decoding="async"
    class="aspect-video w-full object-cover"
  />
</figure>

<!-- 2. Product image: whole image visible, letterboxed on a neutral background -->
<div class="aspect-square rounded-lg bg-gray-100 p-4 dark:bg-gray-800">
  <img src="/img/shoe.png" alt="Trail Runner 3, side view" width="800" height="600"
       class="size-full object-contain" />
</div>

<!-- 3. Avatar: square, round, cropped to the face region (top center) -->
<img src="/img/avatar.jpg" alt="" width="96" height="96"
     class="size-12 rounded-full object-cover object-top" />

<!-- 4. Responsive video embed: iframe keeps 16:9 at any width -->
<div class="aspect-video w-full overflow-hidden rounded-xl bg-black">
  <iframe
    class="size-full"
    src="https://www.youtube-nocookie.com/embed/VIDEO_ID"
    title="Product walkthrough (3 min)"
    loading="lazy"
    allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
    referrerpolicy="strict-origin-when-cross-origin"></iframe>
</div>

<!-- 5. Native video: poster shows at the right shape before playback -->
<video class="aspect-video w-full rounded-xl object-cover" controls preload="metadata"
       poster="/img/poster.jpg" width="1280" height="720">
  <source src="/video/demo.webm" type="video/webm" />
  <source src="/video/demo.mp4" type="video/mp4" />
  <track kind="captions" src="/video/demo.en.vtt" srclang="en" label="English" default />
</video>

<!-- 6. Hero media with text over it (image as element, not CSS background) -->
<section class="relative isolate aspect-[21/9] min-h-80 overflow-hidden">
  <img src="/img/hero.jpg" alt="" width="2100" height="900" fetchpriority="high"
       class="absolute inset-0 -z-10 size-full object-cover" />
  <div class="absolute inset-0 -z-10 bg-black/40" aria-hidden="true"></div>
  <h1 class="p-8 text-4xl font-bold text-white">Text over the image</h1>
</section>
```

Tailwind ratio classes: `aspect-square` (1/1), `aspect-video` (16/9), `aspect-auto`, arbitrary `aspect-[4/3]`, `aspect-[3/4]` for portrait. Fit classes: `object-cover`, `object-contain`, `object-fill` (avoid), `object-none`, `object-scale-down`. Position: `object-top`, `object-center`, `object-[30%_20%]`.

## Variations

- **Named ratio tokens**: `@theme { --aspect-photo: 3 / 2; --aspect-portrait: 4 / 5; }` gives `aspect-photo` and `aspect-portrait` classes, so ratios stay consistent across the site.
- **Ratio only on narrow screens**: `aspect-[4/3] md:aspect-auto md:h-full` lets a split-section image follow its text column's height on desktop but keep a fixed shape when stacked on mobile.
- **Focal point per image**: when crops cut off faces, set `object-position` from a data attribute: `style="object-position: 70% 30%"` on that one `<img>`.
- **Gallery with mixed orientations**: `aspect-square object-cover` on every tile gives a clean grid; use `object-contain` with a background when the full artwork matters (galleries, product shots).

## Pitfalls

- **Missing `width`/`height` attributes** means the browser cannot reserve space until the image loads, even with `aspect-ratio` in CSS in some cases of `height: auto` overrides. Always set both; CSS `w-full` still controls the rendered size.
- **`aspect-ratio` is ignored when both width and height are explicitly set** (for example `h-64 w-full`). Set one dimension and let the ratio compute the other.
- **`object-cover` crops silently**: important text or faces at the edges disappear. Check crops on a phone-width viewport and adjust `object-position`.
- **Iframes without `title`** fail accessibility checks; every embed needs a descriptive `title`.
- **Autoplaying video** must be `muted` and should respect `prefers-reduced-motion`; use a poster with a play button under `motion-reduce:` and only autoplay under `motion-safe:` via JS.
- **CSS `background-image` for content images** loses alt text, lazy loading, `srcset` and `fetchpriority`. Use a positioned `<img>` with `object-cover` (pattern 6) and keep backgrounds for pure decoration.
- **Rounded corners not clipping**: the wrapper needs `overflow-hidden` or the `<img>` itself needs the `rounded-*` class.

## Related skills

- `web-design-images` for `<picture>`, `srcset` and formats
- `web-perf-images` for lazy loading, `fetchpriority` and avoiding CLS
- `web-a11y-images-and-media` for alt text, captions and transcripts
- `web-layout-card-grid` for thumbnails inside equal-height cards
- `web-layout-split-section` for media/text columns
- `web-ui-carousel` for scroll-snap galleries built on these boxes
