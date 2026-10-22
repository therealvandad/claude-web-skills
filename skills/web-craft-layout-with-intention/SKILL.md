---
name: web-craft-layout-with-intention
description: Lay out pages that do not read as a template: asymmetric grids (lg:grid-cols-[1.2fr_0.8fr]), left-aligned headings with a measure, full-bleed images, sticky and offset columns, sections of different heights, editorial numbering, in Tailwind v4. Use whenever a user says the layout "looks like a template", "everything is centred", "too symmetrical", "boring layout", or wants a page that feels designed.
---

# Layout with intention

The template layout is a stack of identical sections: `max-w-7xl mx-auto text-center`, heading, paragraph, row of three cards, repeat with the background toggled to `gray-50`. It reads as generic because nothing in it was decided; every section has the same width, height, alignment and weight, so the eye has no reason to stop anywhere. A designed page has hierarchy: it aligns to a left edge, gives the most important element the most space, lets one image break the container, and changes shape from section to section. The tools are ordinary grid classes used with asymmetry on purpose.

## Pattern

One content grid gives every section the same left edge while letting any child go full-bleed without `100vw` hacks.

```css
@import "tailwindcss";

@utility content-grid {
  display: grid;
  grid-template-columns:
    [full-start] minmax(1.5rem, 1fr)
    [content-start] min(72rem, 100% - 3rem) [content-end]
    minmax(1.5rem, 1fr) [full-end];
  & > * { grid-column: content; }
  & > .full-bleed { grid-column: full; }
}
```

```html
<main class="content-grid bg-stone-50 text-stone-900">

  <!-- 1. Hero: 1.2/0.8 split, left-aligned, the image is the heavy element and sits on the right edge -->
  <section class="grid gap-10 py-20 lg:grid-cols-[1.2fr_0.8fr] lg:items-end lg:py-32">
    <div>
      <h1 class="max-w-[18ch] text-5xl font-medium leading-[1.05] text-balance sm:text-6xl">Maps for the parts of the city the bus does not reach.</h1>
      <p class="mt-6 max-w-[55ch] text-lg leading-relaxed text-stone-600">Walking routes, lit at night, rated by people who live there. Twelve neighbourhoods so far.</p>
    </div>
    <img src="/img/route-hackney.webp" width="900" height="1100" alt="A printed route card for Hackney Wick" class="w-full lg:translate-y-12">
  </section>

  <!-- 2. Full-bleed band: the image spans the viewport, the caption snaps back to the content column -->
  <figure class="full-bleed">
    <img src="/img/night-walk.webp" width="2400" height="1000" alt="A lit footpath along the canal at dusk" class="aspect-[12/5] w-full object-cover">
  </figure>
  <figcaption class="py-3 font-mono text-xs text-stone-500">Regent's Canal, 21:40. Rated 4.6 for lighting by 212 walkers.</figcaption>

  <!-- 3. Sticky heading beside a scrolling list: 1/2 split, numbers instead of icons -->
  <section class="grid gap-10 border-t border-stone-300 py-24 lg:grid-cols-[1fr_2fr]">
    <h2 class="text-3xl font-medium leading-tight lg:sticky lg:top-24 lg:self-start">How a route gets onto the map</h2>
    <ol class="divide-y divide-stone-300">
      <li class="grid gap-4 py-8 sm:grid-cols-[4rem_1fr]">
        <span class="font-mono text-sm text-stone-500">01</span>
        <div><h3 class="font-medium">Someone walks it twice</h3><p class="mt-1 max-w-[55ch] text-stone-600">Once in daylight, once after dark, with the phone recording the path.</p></div>
      </li>
      <li class="grid gap-4 py-8 sm:grid-cols-[4rem_1fr]">
        <span class="font-mono text-sm text-stone-500">02</span>
        <div><h3 class="font-medium">Three neighbours rate it</h3><p class="mt-1 max-w-[55ch] text-stone-600">Lighting, surface, how busy it felt. Below 3.5 on lighting and it stays a draft.</p></div>
      </li>
      <li class="grid gap-4 py-8 sm:grid-cols-[4rem_1fr]">
        <span class="font-mono text-sm text-stone-500">03</span>
        <div><h3 class="font-medium">It is printed</h3><p class="mt-1 max-w-[55ch] text-stone-600">Route cards go to the library and the two cafés at either end.</p></div>
      </li>
    </ol>
  </section>

  <!-- 4. The one centred moment: a short dark section at a different scale -->
  <section class="full-bleed bg-stone-900 px-6 py-28 text-center text-stone-100">
    <p class="mx-auto max-w-[24ch] text-4xl font-medium leading-tight text-balance sm:text-5xl">4,100 routes walked. 61 printed.</p>
    <a href="/neighbourhoods" class="mt-8 inline-block rounded-md bg-stone-100 px-5 py-3 text-sm font-medium text-stone-900">Find your neighbourhood</a>
  </section>

</main>
```

Why these choices:

- **One left edge.** Every section's text starts at the same x. Centring is reserved for section 4, so it registers as an event.
- **Unequal columns.** `1.2fr_0.8fr` and `1fr_2fr` say which side matters. Equal halves say nothing.
- **Measure, not container width.** Headings `max-w-[18ch]`, paragraphs `max-w-[55ch]`; the container is 72rem but the text never is.
- **Different heights and surfaces.** `py-20`, an image band with no padding, `py-24`, `py-28` dark. The rhythm is uneven on purpose; alternating white and `gray-50` is the template rhythm.
- **Offset.** `lg:translate-y-12` on the hero image breaks the baseline between columns; a tiny stagger reads as placed, not poured.
- **Numbers as structure.** `01 02 03` in mono give the list an editorial spine and remove the need for icons.

## Variations

- **Two-column long read**: `lg:grid-cols-[minmax(0,1fr)_18rem]` with a sticky table of contents in the narrow column; body text `max-w-[65ch]`.
- **Overlap instead of offset**: `lg:-mt-24 relative z-10` on a card or image so it rides up into the previous section; give the previous section `pb-32` so nothing is covered.
- **Breakout, not full-bleed**: add `& > .breakout { grid-column: full; width: min(88rem, 100%); justify-self: center; }` to the utility for images wider than the text but not edge-to-edge.
- **App or dashboard**: the same ideas at smaller scale: a `[16rem_1fr]` sidebar split, one wide chart and two narrow stats (`lg:grid-cols-[2fr_1fr_1fr]`), never four equal tiles.

## Pitfalls

- `w-screen` / `100vw` for full-bleed adds a horizontal scrollbar on Windows because the scrollbar width is counted. The named-line grid above never needs it.
- Asymmetric `fr` columns blow out when a child has a long unbreakable string (URLs, code); add `min-w-0` to the grid children.
- `lg:sticky` on a grid child does nothing without `self-start`: a stretched child is already as tall as the row, so it has nowhere to stick.
- Visual reordering (`order-*`, `lg:col-start-2`) must not change reading order for keyboard and screen reader users; keep the DOM in reading order and offset visually.
- Every section stacks to one column on phones; check that the "interesting" offset (`translate-y-12`) is removed below `lg` or it just creates a gap.
- A full-bleed image without `width`/`height` shifts the whole page when it loads; set them and `aspect-*` so the band reserves its space.

## Related skills

- `web-css-responsive-grid`
- `web-css-spacing-scale`
- `web-layout-split-section`
- `web-layout-landing-page`
- `web-css-sticky-and-fixed`
- `web-craft-anti-generic-design`
- `web-craft-finishing-details`
