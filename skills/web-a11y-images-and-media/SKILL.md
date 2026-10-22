---
name: web-a11y-images-and-media
description: Write correct alt text (informative, decorative, functional, complex images), figure captions, accessible inline SVG, and video/audio with captions, transcripts, keyboard controls and no autoplay for reduced-motion users. Use when a user asks "what alt text", "alt for a logo", "decorative image", "add captions to video", "background video accessibility", or "audio description", or an audit flags WCAG 1.1.1 or 1.2.x.
---

# Images and media

An image without usable alt text is a hole in the content for anyone using a screen reader, and
a video without captions excludes deaf users and everyone on a muted phone. WCAG 2.2 SC 1.1.1
(Non-text Content) and 1.2.1 to 1.2.5 (Time-based Media) set the bar: every image gets an
accessible name that conveys its purpose, or is explicitly marked decorative; every video gets
captions, and prerecorded video gets a transcript or audio description. The decision is about
*purpose in context*, not about what the pixels show.

## Pattern

```html
<!-- 1. Informative: describe what matters here, not every detail. No "image of". -->
<img src="/img/chart-q3.png" width="800" height="450"
     alt="Revenue grew from $1.2M in July to $1.9M in September, with August flat."
     class="w-full rounded-lg">

<!-- 2. Decorative: empty alt, so screen readers skip it. Never omit the attribute. -->
<img src="/img/divider-wave.svg" alt="" width="1200" height="40" class="w-full">

<!-- 3. Functional (inside a link or button): alt names the action, not the picture. -->
<a href="/" class="inline-block focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
  <img src="/img/logo.svg" alt="Acme home" width="120" height="32">
</a>

<!-- 4. Complex image: short alt plus a long description nearby. -->
<figure class="my-8">
  <img src="/img/architecture.png" width="1200" height="700"
       alt="System architecture diagram, described below."
       aria-describedby="arch-desc" class="w-full">
  <figcaption id="arch-desc" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
    Browser sends requests to the edge cache; misses go to the API, which reads from Postgres and
    writes events to the queue consumed by the mailer.
  </figcaption>
</figure>

<!-- 5. Inline SVG: role=img + title for meaningful, aria-hidden for decorative icons. -->
<svg role="img" aria-labelledby="warn-t" class="size-6 text-amber-700" viewBox="0 0 24 24" fill="currentColor">
  <title id="warn-t">Warning</title>
  <path d="M12 2 1 21h22L12 2zm1 14h-2v2h2v-2zm0-6h-2v5h2v-5z"/>
</svg>
<button type="button" class="inline-flex items-center gap-2 rounded-md border px-3 py-2">
  <svg aria-hidden="true" class="size-4" viewBox="0 0 24 24" fill="currentColor"><path d="M5 20h14v-2H5v2zm7-18-5 5h3v6h4V7h3l-5-5z"/></svg>
  Upload
</button>

<!-- 6. Video: native controls, captions track, poster, transcript. No autoplay with sound. -->
<figure>
  <video controls preload="metadata" poster="/video/intro-poster.jpg" width="1280" height="720"
         class="w-full rounded-lg bg-black">
    <source src="/video/intro.webm" type="video/webm">
    <source src="/video/intro.mp4" type="video/mp4">
    <track kind="captions" src="/video/intro.en.vtt" srclang="en" label="English" default>
    <track kind="descriptions" src="/video/intro.en.desc.vtt" srclang="en" label="Audio descriptions">
  </video>
  <figcaption class="mt-2 text-sm">
    Product tour, 2 min. <a href="/video/intro-transcript.html" class="underline">Read the transcript</a>
  </figcaption>
</figure>
```

```html
<!-- 7. Ambient background video: muted, no controls, paused for reduced motion, with a pause button. -->
<div class="relative">
  <video autoplay muted loop playsinline aria-hidden="true" class="h-96 w-full object-cover motion-reduce:hidden"
         src="/video/loop.mp4"></video>
  <img src="/video/loop-poster.jpg" alt="" class="hidden h-96 w-full object-cover motion-reduce:block">
  <button type="button" data-pause aria-pressed="false" class="absolute right-4 bottom-4 rounded-full bg-black/70 px-3 py-1 text-white">Pause</button>
</div>
```

```js
const bg = document.querySelector('video[aria-hidden]');
document.querySelector('[data-pause]').addEventListener('click', (e) => {
  const paused = bg.paused ? (bg.play(), false) : (bg.pause(), true);
  e.currentTarget.setAttribute('aria-pressed', String(paused));
  e.currentTarget.textContent = paused ? 'Play' : 'Pause';
});
```

Alt text test: cover the image and read the page; does the alt supply what was lost? If the
surrounding text already says it, the image is probably decorative. A caption (`<figcaption>`)
is visible to everyone and does not replace alt; the alt must still stand alone.

## Variations

- **Product photos**: alt names the product and the view ("Blue canvas tote, front, with zipped
  inner pocket"); the price and name live in text next to it, not in alt.
- **Avatars**: `alt="Jane Doe"` if the name is not adjacent, `alt=""` if it is right there.
- **Icon fonts or CSS background images** cannot carry alt. Use inline SVG or `<img>` for anything
  meaningful; backgrounds are decorative by definition.
- **Audio only** (podcast): `<audio controls>` plus a full transcript on the page (SC 1.2.1).

## Pitfalls

- `alt="image"`, `alt="photo.jpg"`, or stuffing keywords. Screen readers already say "image";
  the alt should be the content. Keep it under ~150 characters; longer goes in `figcaption` or text.
- Omitting `alt` entirely: screen readers then read the filename. `alt=""` is the decorative
  marker, not a missing attribute.
- Text baked into images (banners with headlines). Put the text in HTML; if unavoidable, the alt
  must repeat the full text verbatim (SC 1.4.5).
- Autoplaying video with sound, or motion that cannot be paused: SC 1.4.2 and 2.2.2 require a
  pause/stop within three seconds. Also honour `prefers-reduced-motion` (`motion-reduce:` above).
- Captions files burned into the video only, or YouTube auto-captions never corrected. `<track
  kind="captions">` must include relevant sound effects, not just dialogue.
- Custom video players built from divs: keyboard users cannot reach them. Native `controls` are
  accessible out of the box; style with `::-webkit-media-controls` only if you must.

## Related skills

- `web-design-images`
- `web-design-icons`
- `web-perf-images`
- `web-css-aspect-ratio-media`
- `web-motion-reduced-motion`
- `web-seo-content-structure`
