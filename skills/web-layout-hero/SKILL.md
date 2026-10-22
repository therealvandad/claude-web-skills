---
name: web-layout-hero
description: Build a hero section (headline, subcopy, one or two call-to-action buttons, optional image or illustration) with Tailwind v4, in centered, split or background-image variants. Use whenever a user asks for a landing page top, a banner, a "first screen", "above the fold", a page intro or a big headline area, even if they never say "hero".
---

# Hero section

The hero is the one section every visitor sees, so it must load fast, read in two seconds and put the primary action within thumb reach on a phone. The pattern below is a split hero (text left, image right) that collapses to a single column on small screens. Keep the headline short, make the primary button the only strong-colored element, and let the image be optional so the layout still works without it.

## Pattern

```html
<section class="relative overflow-hidden bg-white dark:bg-gray-950">
  <div class="mx-auto grid max-w-7xl items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:gap-16 lg:px-8 lg:py-28">

    <div class="max-w-2xl">
      <p class="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 px-3 py-1 text-xs font-medium text-gray-600 dark:border-gray-700 dark:text-gray-300">
        <span class="size-1.5 rounded-full bg-emerald-500" aria-hidden="true"></span>
        Now in public beta
      </p>

      <h1 class="text-4xl font-bold tracking-tight text-balance text-gray-900 sm:text-5xl lg:text-6xl dark:text-white">
        Ship your website in an afternoon
      </h1>

      <p class="mt-6 text-lg text-pretty text-gray-600 dark:text-gray-400">
        One HTML file, Tailwind, no build step. Everything you need to publish a fast,
        accessible site without learning a framework first.
      </p>

      <div class="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
        <a href="#get-started"
           class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-5 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
          Get started
        </a>
        <a href="#demo"
           class="inline-flex items-center justify-center rounded-lg px-5 py-3 text-base font-semibold text-gray-900 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:text-white dark:hover:bg-gray-800">
          Watch the demo <span aria-hidden="true" class="ml-1">&rarr;</span>
        </a>
      </div>

      <p class="mt-6 text-sm text-gray-500">No credit card. Free for personal sites.</p>
    </div>

    <div class="relative">
      <img src="/img/hero.webp" width="1200" height="900" alt="Screenshot of the editor with a page preview"
           class="w-full rounded-xl shadow-2xl ring-1 ring-gray-900/10 dark:ring-white/10"
           fetchpriority="high" decoding="async">
    </div>

  </div>
</section>
```

Why these choices:

- `grid lg:grid-cols-2 items-center`: single column until `lg`, so on tablets the image sits under the text at full width instead of being squeezed beside it.
- `text-balance` on the headline avoids a one-word orphan line; `text-pretty` on the paragraph does the same for body copy.
- Buttons stack (`flex-col`) on phones so each is full-width and easy to tap, then sit in a row from `sm`.
- `fetchpriority="high"` plus explicit `width`/`height` make the hero image the LCP element without layout shift. Never lazy-load it.
- Only one filled button: two strong colors compete and the eye picks neither.

## Variations

- **Centered hero (no image)**: drop the image column and the grid; use `mx-auto max-w-3xl text-center` on the text block and `justify-center` on the button row. Best for product launches and waitlists.
- **Background image or gradient**: add `bg-[url('/img/bg.webp')] bg-cover bg-center` to the section, overlay with an absolutely positioned `<div class="absolute inset-0 bg-gray-900/70" aria-hidden="true">`, give the content `relative` and switch text to white. Check contrast against the darkest and lightest parts of the photo.
- **Image first on mobile**: add `order-first lg:order-none` to the image wrapper when the visual sells the product better than the words.
- **Illustration instead of screenshot**: inline SVG in the image column so it picks up `currentColor` and dark mode; keep it under 20 KB.

## Pitfalls

- `h-screen` heroes trap users: on short laptop screens the CTA ends up below the fold, and on phones the browser chrome makes it jump. Use generous `py-*` padding and let content set the height; if you want full-screen, use `min-h-dvh` and still keep the CTA near the top.
- A missing `width`/`height` on the image shifts the whole page down once it loads (CLS). Always set them, even with `w-full` in CSS.
- Headlines over about 8 words wrap into three lines at `text-6xl` on a 13-inch laptop. Shorten the copy or drop a size step.
- Secondary links styled as plain text next to a big button look clickable only after hover; give them the same padding and a visible hover background so their hit area matches.
- Gradient text (`bg-clip-text text-transparent`) breaks text selection highlighting and fails contrast checks on the lighter gradient stops. Use it on one word at most.
- Autoplaying background video needs `muted playsinline`, a poster image, and must be swapped for the poster when `prefers-reduced-motion` is set.

## Related skills

- `web-layout-landing-page`
- `web-layout-split-section`
- `web-ui-buttons`
- `web-perf-images`
- `web-design-images`
- `web-css-fluid-typography`
- `web-a11y-color-contrast`
