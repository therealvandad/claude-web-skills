---
name: web-section-team-grid
description: Build a team section or people grid: photo, name, role and one or two social links per person, as a responsive list with hover and focus states, plus a compact list variant for large teams, in Tailwind v4. Use whenever a user asks for a "team section", "meet the team", "our people", "staff directory", "founders", or "author bios".
---

# Team grid

A team section is a list of people, so it is a `<ul>` of cards, each with a real photo at a fixed shape, a name that is the only heading, a role in plain text, and links that go somewhere specific. It looks designed when the photos are consistent (same crop, same background treatment) and the text is restrained; it looks like a template when every card has a gradient avatar ring and three social icons nobody clicks.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="team-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <div class="max-w-xl">
      <p class="font-mono text-xs uppercase tracking-widest text-stone-500">Ashworth Veterinary, Harrogate</p>
      <h2 id="team-heading" class="mt-3 text-3xl font-semibold tracking-tight text-balance text-stone-900 sm:text-4xl dark:text-stone-100">
        Nine people, two of whom will know your dog's name by the second visit
      </h2>
    </div>

    <ul role="list" class="mt-12 grid grid-cols-2 gap-x-6 gap-y-10 sm:grid-cols-3 lg:grid-cols-4">
      <li>
        <figure>
          <img src="/img/team/r-ashworth.webp" width="480" height="600" alt="Rachel Ashworth"
               class="aspect-[4/5] w-full rounded-lg object-cover grayscale-[30%]" loading="lazy">
          <figcaption class="mt-4">
            <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Rachel Ashworth</h3>
            <p class="text-sm text-stone-600 dark:text-stone-400">Clinical director, orthopaedics</p>
            <p class="mt-1 font-mono text-xs text-stone-500">Since 2008</p>
          </figcaption>
        </figure>
        <ul role="list" class="mt-3 flex gap-3" aria-label="Rachel Ashworth, links">
          <li>
            <a href="mailto:rachel@ashworthvets.co.uk" class="inline-flex rounded p-1 text-stone-500 hover:text-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 dark:hover:text-stone-100">
              <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
              <span class="sr-only">Email Rachel Ashworth</span>
            </a>
          </li>
          <li>
            <a href="https://www.linkedin.com/in/rachel-ashworth-vet" rel="noopener" class="inline-flex rounded p-1 text-stone-500 hover:text-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 dark:hover:text-stone-100">
              <svg class="size-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM10 9h3.8v1.7h.1c.5-1 1.8-2 3.7-2 4 0 4.7 2.6 4.7 6V21h-4v-5.3c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V21h-4z"/></svg>
              <span class="sr-only">Rachel Ashworth on LinkedIn</span>
            </a>
          </li>
        </ul>
      </li>

      <li>
        <figure>
          <img src="/img/team/d-mbeki.webp" width="480" height="600" alt="Daniel Mbeki"
               class="aspect-[4/5] w-full rounded-lg object-cover grayscale-[30%]" loading="lazy">
          <figcaption class="mt-4">
            <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Daniel Mbeki</h3>
            <p class="text-sm text-stone-600 dark:text-stone-400">Veterinary surgeon, small animal medicine</p>
            <p class="mt-1 font-mono text-xs text-stone-500">Since 2016</p>
          </figcaption>
        </figure>
        <ul role="list" class="mt-3 flex gap-3" aria-label="Daniel Mbeki, links">
          <li>
            <a href="mailto:daniel@ashworthvets.co.uk" class="inline-flex rounded p-1 text-stone-500 hover:text-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 dark:hover:text-stone-100">
              <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
              <span class="sr-only">Email Daniel Mbeki</span>
            </a>
          </li>
        </ul>
      </li>

      <!-- repeat <li> per person; 8 fills two rows of four cleanly -->
    </ul>
  </div>
</section>
```

Why these choices:

- `aspect-[4/5] object-cover` forces every photo to the same portrait shape regardless of the source file, and `width`/`height` reserve space before load. One crop ratio is what makes the grid look like one team.
- `grayscale-[30%]` is a light unifying treatment for photos taken on different days and cameras; full greyscale reads as a memorial wall, so stop short.
- The name is the `<h3>`; role and tenure are paragraphs. One heading per person keeps the outline honest.
- Links carry `sr-only` text with the person's name, so a screen-reader link list reads "Email Rachel Ashworth" rather than eight bare "Email" links.
- Two columns on phones (`grid-cols-2`), not one: portrait photos in a single column become a very long scroll for a nine-person team.

## Variations

- **Compact list for 20+ people**: `<ul class="divide-y divide-stone-200">` with each `<li class="flex items-center gap-4 py-4">`, a `size-12 rounded-full object-cover` photo, name and role inline, and a single link. Sortable by department with a `<h3>` per group.
- **Round avatars, centred**: `aspect-square rounded-full` with `text-center` under each; use only for small teams (3 to 4) where the section is short and the faces are the content.
- **With a short bio**: add `<p class="mt-2 text-sm leading-relaxed">` of two sentences inside the `<figcaption>`, and widen to `sm:grid-cols-2 lg:grid-cols-3` so the text has a measure.
- **Dark**: section `bg-stone-950`, photos keep `grayscale-[30%]`, text `stone-100`/`stone-400`, link icons `stone-400 hover:text-white`.

## Pitfalls

- Mixed photo sources (one studio headshot, one phone selfie, one with a busy background) are the first thing a visitor notices. Insist on a consistent shoot, or crop tight to faces and apply the same `grayscale` and `contrast` filters to all.
- A gradient ring or `ring-4 ring-purple-500` around avatars is a template tell. A hairline `border border-stone-200` at most, or nothing.
- Icons from three different sets (one outline, one solid, one 24px, one 20px) look messy in a row; pick one set and one stroke width as in `web-design-icons`.
- `hover:` revealing the role or links hides them from touch users; keep all text and links visible, and use hover only for colour.
- Linking a name to a dead `#` profile page is worse than no link. If there is no bio page, the name is text.
- Placeholder people ("Jane Doe, CEO") and stock portraits are immediately recognisable; use the real team or ship the section later. See `web-craft-real-content`.

## Related skills

- `web-layout-testimonials`
- `web-layout-card-grid`
- `web-css-aspect-ratio-media`
- `web-design-icons`
- `web-design-images`
- `web-craft-real-content`
