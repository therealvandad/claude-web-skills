---
name: web-layout-split-section
description: Build two-column media-and-text sections that alternate sides (image left, then image right) on desktop and stack with the image first on mobile, using Tailwind v4 grid. Use whenever a user asks for "image next to text", a zig-zag or alternating layout, "how it works" steps with screenshots, product detail blocks, about-page sections or a feature walkthrough.
---

# Split section (alternating media + text)

The split section is the workhorse of product and about pages: one idea, one picture, side by side. Alternating the image side keeps a long page from feeling like a table. Do the alternation with CSS (`lg:order-*` or `:nth-child` via `even:`), not by reordering the HTML, so the source order stays "image, then text" for every block and reads correctly on phones and screen readers.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="how-heading">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

    <h2 id="how-heading" class="sr-only">How it works</h2>

    <div class="space-y-20 lg:space-y-32">

      <!-- Block 1: image left, text right (default order) -->
      <article class="grid items-center gap-10 lg:grid-cols-2 lg:gap-16">
        <div class="relative">
          <img src="/img/step-1.webp" width="1200" height="900" alt="The editor showing a page with three sections and a live preview"
               loading="lazy" decoding="async"
               class="w-full rounded-2xl shadow-lg ring-1 ring-gray-900/10 dark:ring-white/10">
        </div>
        <div class="max-w-xl">
          <p class="text-sm font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400">Step 1</p>
          <h3 class="mt-2 text-2xl font-bold tracking-tight text-balance text-gray-900 sm:text-3xl dark:text-white">Write plain HTML</h3>
          <p class="mt-4 text-lg text-pretty text-gray-600 dark:text-gray-400">
            Start from a single file. No install, no config. Open it in a browser and you are already looking at your site.
          </p>
          <ul role="list" class="mt-6 space-y-3 text-gray-700 dark:text-gray-300">
            <li class="flex gap-3">
              <svg class="mt-1 size-5 shrink-0 text-blue-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>
              <span>Works offline, forever</span>
            </li>
            <li class="flex gap-3">
              <svg class="mt-1 size-5 shrink-0 text-blue-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>
              <span>Every editor already understands it</span>
            </li>
          </ul>
          <a href="/docs/start" class="mt-8 inline-flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
            Read the guide <span aria-hidden="true">&rarr;</span>
          </a>
        </div>
      </article>

      <!-- Block 2: same markup, image flips to the right on lg -->
      <article class="grid items-center gap-10 lg:grid-cols-2 lg:gap-16">
        <div class="relative lg:order-last">
          <img src="/img/step-2.webp" width="1200" height="900" alt="Terminal running the Tailwind CLI with a watch flag"
               loading="lazy" decoding="async"
               class="w-full rounded-2xl shadow-lg ring-1 ring-gray-900/10 dark:ring-white/10">
        </div>
        <div class="max-w-xl lg:justify-self-end">
          <p class="text-sm font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400">Step 2</p>
          <h3 class="mt-2 text-2xl font-bold tracking-tight text-balance text-gray-900 sm:text-3xl dark:text-white">Add Tailwind</h3>
          <p class="mt-4 text-lg text-pretty text-gray-600 dark:text-gray-400">
            One CLI command watches your files and writes a tiny CSS file with only the classes you used.
          </p>
        </div>
      </article>

    </div>
  </div>
</section>
```

Why these choices:

- Source order is always image then text. On phones the image appears above its text (a visual lead-in); on `lg` the grid places them side by side and `lg:order-last` on the image wrapper flips alternate blocks.
- `items-center` vertically centers the shorter column; `max-w-xl` on the text column keeps line length readable even in a half-width column on a wide screen.
- `lg:justify-self-end` on the flipped block's text pulls it toward the image so the gap between columns stays `gap-16`, not `gap-16` plus leftover width.
- Each block is an `<article>` with its own `<h3>` under the section's `<h2>` (visually hidden here because the eyebrows carry the labels), so the outline is intact.
- Images are `loading="lazy"` because split sections live below the hero; the sizes attributes prevent layout shift.

Automatic alternation without per-block classes:

```html
<div class="space-y-20 lg:space-y-32 [&>article:nth-child(even)>div:first-child]:lg:order-last [&>article:nth-child(even)>div:last-child]:lg:justify-self-end">
```

Use this when blocks come from a CMS loop and you cannot vary classes per item.

## Variations

- **Text wider than image**: `lg:grid-cols-5` with `lg:col-span-3` on text and `lg:col-span-2` on the image for screenshot-light content.
- **Image bleeds to the edge**: remove the container's horizontal padding for the image column and add `lg:-mr-8 xl:-mr-[calc((100vw-80rem)/2)]` to the right-side image wrapper, with `overflow-hidden` on the section. Dramatic; use once per page.
- **Video or code instead of image**: replace `<img>` with a `<pre>` block or a `<video muted playsinline loop>` with a poster; keep `aspect-video` on the wrapper so layout does not depend on media load.
- **Sticky image, scrolling steps**: on `lg`, `lg:sticky lg:top-24 self-start` on the image column and three text blocks in the other column; the image swaps via `web-nav-scroll-spy-toc` logic.

## Pitfalls

- Setting `order-last` without the `lg:` prefix flips the image under the text on phones too, which removes the visual lead-in and reads oddly. Scope ordering to the breakpoint where columns exist.
- Visual reordering never changes tab order; the text's link is still tabbed after the image. That is fine here, but do not put interactive controls in the image column of flipped blocks.
- `items-center` with a very tall image and a short paragraph leaves the text floating in whitespace. Use `items-start` and add `lg:pt-8` to the text for tall portraits.
- `md:grid-cols-2` is too early: at 768 px each column is about 340 px, and screenshots become unreadable. Split at `lg` unless the images are simple illustrations.
- Decorative screenshots with long `alt` text slow screen-reader users through "how it works". Describe what the image shows in one short sentence or use `alt=""` when the text already says it.
- Three or more consecutive splits with the same tinted background blur together; add the section's `space-y-*` rather than per-block padding so vertical rhythm is consistent, and vary the eyebrow or step number.

## Related skills

- `web-layout-hero`
- `web-layout-landing-page`
- `web-layout-feature-grid`
- `web-css-responsive-grid`
- `web-css-aspect-ratio-media`
- `web-motion-scroll-reveal`
- `web-design-images`
