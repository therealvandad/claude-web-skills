---
name: web-layout-testimonials
description: Build a testimonials section: quote cards with avatar, name and role in a responsive grid or masonry "quote wall", plus an optional horizontal scroll-snap scroller, in Tailwind v4 with no libraries. Use whenever a user asks for testimonials, customer quotes, reviews, "what people say", social proof, a logo-and-quote strip or a "wall of love".
---

# Testimonials

Social proof works only if it looks real: actual names, roles, faces, and quotes short enough to read in passing. Mark quotes up with `<figure>` / `<blockquote>` / `<figcaption>` so they carry meaning without ARIA, keep every card the same visual weight, and never let the layout depend on JavaScript. The scroller variation uses CSS scroll-snap, so it works with touch, trackpad and keyboard before any script loads.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="testimonials-heading">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

    <div class="mx-auto max-w-2xl text-center">
      <h2 id="testimonials-heading" class="text-3xl font-bold tracking-tight text-balance text-gray-900 sm:text-4xl dark:text-white">
        Loved by small teams
      </h2>
      <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">Here is what customers say after their first month.</p>
    </div>

    <ul role="list" class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">

      <li>
        <figure class="flex h-full flex-col justify-between rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
          <blockquote class="text-base text-gray-700 dark:text-gray-300">
            <p>“We replaced a page builder and two plugins with a single HTML file. The site is faster and I finally understand it.”</p>
          </blockquote>
          <figcaption class="mt-6 flex items-center gap-3">
            <img src="/img/avatars/maria.jpg" width="40" height="40" alt="" loading="lazy"
                 class="size-10 rounded-full object-cover ring-1 ring-gray-200 dark:ring-gray-700">
            <div class="text-sm">
              <p class="font-semibold text-gray-900 dark:text-white">Maria Chen</p>
              <p class="text-gray-500">Founder, Lumen Studio</p>
            </div>
          </figcaption>
        </figure>
      </li>

      <li>
        <figure class="flex h-full flex-col justify-between rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
          <blockquote class="text-base text-gray-700 dark:text-gray-300">
            <p>“Support answered in twenty minutes on a Sunday. That alone was worth the switch.”</p>
          </blockquote>
          <figcaption class="mt-6 flex items-center gap-3">
            <span class="flex size-10 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700" aria-hidden="true">JO</span>
            <div class="text-sm">
              <p class="font-semibold text-gray-900 dark:text-white">Jonah Okafor</p>
              <p class="text-gray-500">Developer, freelance</p>
            </div>
          </figcaption>
        </figure>
      </li>

      <!-- more <li><figure> cards; 3 or 6 fill the grid -->

    </ul>
  </div>
</section>
```

Why these choices:

- `<figure>` wraps quote and attribution; `<blockquote>` holds only the quoted words; `<figcaption>` names the author. Screen readers announce the structure correctly and no ARIA is needed.
- `h-full flex flex-col justify-between` makes the attribution sit on the same baseline in every card even when quotes differ in length (the `<li>` grid cells are already equal height).
- Avatars get `alt=""` because the name is right beside them; a decorative initials badge is the fallback for people without a photo.
- Curly quotes are typed in the copy, not generated with CSS pseudo-elements, so they are copied and read aloud with the quote.

## Variations

- **Masonry quote wall**: swap `grid` for `columns-1 sm:columns-2 lg:columns-3 gap-6` and give each `<li>` `mb-6 break-inside-avoid`. Quotes of mixed length pack naturally; order becomes column-first, so put the strongest quotes first.
- **Horizontal scroller**: replace the `<ul>` classes with `mt-12 flex snap-x snap-mandatory gap-6 overflow-x-auto scroll-px-4 pb-4 [scrollbar-width:thin]` and give each `<li>` `w-[85%] shrink-0 snap-start sm:w-[45%] lg:w-[31%]`. Add `tabindex="0"` and `aria-label="Testimonials, scroll horizontally"` to the list so keyboard users can scroll it. Optional prev/next buttons call `list.scrollBy({ left: list.clientWidth * 0.9, behavior: 'smooth' })`.
- **Single featured quote**: one `<figure>` centered at `max-w-3xl`, quote at `text-2xl sm:text-3xl font-medium`, avatar `size-14`. Use for one strong endorsement from a recognisable name.
- **With company logos**: add a `<img class="h-6 w-auto" alt="Lumen Studio">` of the company's logo at the top of the card and drop the role text.

## Pitfalls

- Star ratings drawn with five SVGs are read as "image image image image image". Add `<p class="sr-only">Rated 5 out of 5</p>` beside them or put `role="img" aria-label="5 out of 5 stars"` on the wrapper.
- A scroller with `overflow-x-auto` hides content from keyboard users unless the list is focusable (`tabindex="0"`) or every card contains a focusable link.
- Auto-scrolling marquees must stop on hover, on focus, and entirely under `prefers-reduced-motion`; a CSS `animation` with `motion-reduce:animate-none` handles the last case.
- Avatars without `width`/`height` cause the card to jump when images load; set both and use `object-cover` for non-square photos.
- Quotes longer than about 40 words turn the grid into a wall of text. Trim to the strongest sentence or two; link "Read the full story" if needed.
- Masonry `columns-*` reorders content visually; do not use it when the quotes have a meaningful sequence or when numbered.

## Related skills

- `web-layout-card-grid`
- `web-layout-landing-page`
- `web-ui-carousel`
- `web-motion-counters-and-tickers`
- `web-design-images`
- `web-a11y-images-and-media`
