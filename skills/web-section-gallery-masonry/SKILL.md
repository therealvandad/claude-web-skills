---
name: web-section-gallery-masonry
description: 'Build an image gallery section: CSS-columns masonry or a grid with spans, lazy-loaded figures with captions, and a native dialog lightbox with keyboard navigation and no library, in Tailwind v4. Use whenever a user asks for a "gallery", "masonry", "photo grid", "portfolio images", "lightbox", "click to enlarge", or "Pinterest-style layout".'
---

# Gallery with masonry and lightbox

A gallery is a list of figures: each image has a caption and a reason to be there. CSS `columns` gives a masonry look with zero JavaScript, at the cost of top-to-bottom reading order per column; a grid with spans keeps row order but needs you to choose which images are tall. Either way, every `<img>` needs `width`, `height`, `loading="lazy"` and real `alt`, and the lightbox is a `<dialog>` so focus, Escape and the backdrop come for free.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="gallery-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <h2 id="gallery-heading" class="text-3xl font-semibold tracking-tight text-stone-900 sm:text-4xl dark:text-stone-100">
        Garden rooms built in 2025
      </h2>
      <p class="font-mono text-xs text-stone-500">22 projects, Surrey and Hampshire</p>
    </div>

    <ul role="list" class="mt-10 columns-1 gap-4 sm:columns-2 lg:columns-3 [&>li]:mb-4 [&>li]:break-inside-avoid" data-gallery>
      <li>
        <figure>
          <button type="button" class="group block w-full rounded-lg focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-stone-900"
                  data-full="/img/gardens/farnham-oak-1600.webp" aria-label="Enlarge: Oak-clad studio in Farnham">
            <img src="/img/gardens/farnham-oak-800.webp" width="800" height="1000" alt="Oak-clad garden studio with a full-height glazed door, lawn in front"
                 class="w-full rounded-lg border border-stone-200 transition group-hover:opacity-90 dark:border-stone-800" loading="lazy" decoding="async">
          </button>
          <figcaption class="mt-2 font-mono text-xs text-stone-500">Farnham, 4 by 3 metres, oak cladding</figcaption>
        </figure>
      </li>
      <li>
        <figure>
          <button type="button" class="group block w-full rounded-lg focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-stone-900"
                  data-full="/img/gardens/alton-office-1600.webp" aria-label="Enlarge: Home office in Alton">
            <img src="/img/gardens/alton-office-800.webp" width="800" height="600" alt="Black-stained timber office with a desk visible through the window at dusk"
                 class="w-full rounded-lg border border-stone-200 transition group-hover:opacity-90 dark:border-stone-800" loading="lazy" decoding="async">
          </button>
          <figcaption class="mt-2 font-mono text-xs text-stone-500">Alton, 3 by 2.5 metres, home office</figcaption>
        </figure>
      </li>
      <!-- more <li> figures; mixed portrait and landscape heights make the masonry -->
    </ul>
  </div>

  <dialog class="m-auto max-h-[100dvh] w-full max-w-5xl bg-transparent p-4 backdrop:bg-stone-950/90 open:flex open:flex-col open:items-center" data-lightbox>
    <div class="flex w-full items-center justify-between text-sm text-stone-300">
      <p data-lightbox-caption></p>
      <button type="button" class="rounded px-2 py-1 hover:text-white focus-visible:outline-2 focus-visible:outline-white" data-lightbox-close>Close (Esc)</button>
    </div>
    <img src="" alt="" class="mt-3 max-h-[80dvh] w-auto max-w-full rounded-lg" data-lightbox-img>
    <div class="mt-3 flex gap-6 text-sm text-stone-300">
      <button type="button" class="rounded px-2 py-1 hover:text-white focus-visible:outline-2 focus-visible:outline-white" data-lightbox-prev>Previous</button>
      <button type="button" class="rounded px-2 py-1 hover:text-white focus-visible:outline-2 focus-visible:outline-white" data-lightbox-next>Next</button>
    </div>
  </dialog>
</section>
```

```js
const gallery = document.querySelector('[data-gallery]');
const dialog = document.querySelector('[data-lightbox]');
const img = dialog.querySelector('[data-lightbox-img]');
const caption = dialog.querySelector('[data-lightbox-caption]');
const triggers = [...gallery.querySelectorAll('button[data-full]')];
let index = 0;

function show(i) {
  index = (i + triggers.length) % triggers.length;
  const btn = triggers[index];
  const thumb = btn.querySelector('img');
  img.src = btn.dataset.full;
  img.alt = thumb.alt;
  caption.textContent = `${index + 1} of ${triggers.length}. ${btn.closest('figure').querySelector('figcaption')?.textContent ?? ''}`;
}

triggers.forEach((btn, i) => btn.addEventListener('click', () => { show(i); dialog.showModal(); }));
dialog.querySelector('[data-lightbox-close]').addEventListener('click', () => dialog.close());
dialog.querySelector('[data-lightbox-prev]').addEventListener('click', () => show(index - 1));
dialog.querySelector('[data-lightbox-next]').addEventListener('click', () => show(index + 1));
dialog.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') show(index - 1);
  if (e.key === 'ArrowRight') show(index + 1);
});
dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); }); // backdrop click
dialog.addEventListener('close', () => { img.src = ''; triggers[index].focus(); });
```

Why these choices:

- `columns-*` with `break-inside-avoid` is the masonry: the browser flows items top-to-bottom, column by column, and never splits a figure. Mixed aspect ratios produce the staggered look.
- Each thumbnail is wrapped in a `<button>` because clicking opens an in-page dialog, not a navigation; `aria-label` says what the button does and which image.
- `showModal()` traps focus, handles Escape and renders the `::backdrop`; the `close` event returns focus to the thumbnail the user came from.
- Two sizes per image: 800px thumbnails lazy-loaded in the grid, 1600px only fetched when enlarged. Set `srcset` on the thumbnail for retina as in `web-perf-images`.
- Captions are inside `<figure>` so the thumbnail and the sentence under it are one unit for assistive tech and for the lightbox caption lookup.

## Variations

- **Grid with spans instead of columns** (reading order preserved): `grid grid-cols-2 gap-4 sm:grid-cols-4 auto-rows-[8rem] grid-flow-dense` and give portrait images `row-span-2`, wide ones `col-span-2`, with `object-cover h-full w-full` on each `<img>`. Needs a known orientation per image.
- **Fixed-shape tiles**: all `aspect-square object-cover`; simplest, no masonry, reads in order. Good for product photos where cropping is acceptable.
- **No lightbox**: make each thumbnail an `<a href="/projects/farnham">` to a project page instead of a `<button>`; drop the dialog. Better for portfolios where each image has a story.
- **Filter row**: a `<div role="group" aria-label="Filter by type">` of toggle buttons above the list that sets `hidden` on non-matching `<li>`; keep the count in the heading in sync ("8 of 22").

## Pitfalls

- CSS columns read top-to-bottom then across, so a screen reader or keyboard user visits items in an order that does not match the visual rows. Acceptable for a photo set; for a dated or numbered sequence use the grid variant.
- Missing `width`/`height` on thumbnails makes columns reflow as each image loads, and items jump between columns. Dimensions are not optional in masonry.
- A `<div onclick>` thumbnail cannot be focused or activated by keyboard; it must be a `<button>` or `<a>`.
- Opening a 4 MB original in the lightbox on a phone stalls for seconds. Serve a 1600px `data-full` and consider swapping `src` after a `loading` state.
- `break-inside-avoid` on the `<figure>` instead of the `<li>` lets the `<li>` margin split across columns and leaves odd gaps; put both the margin and the break rule on the `<li>` as above.
- Hover-only zoom or caption reveal hides the caption from touch users; keep captions visible and use hover only for the subtle opacity change.

## Related skills

- `web-ui-modal-dialog`
- `web-perf-images`
- `web-design-images`
- `web-css-aspect-ratio-media`
- `web-a11y-images-and-media`
- `web-ui-carousel`
