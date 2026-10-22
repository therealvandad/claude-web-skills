---
name: web-layout-feature-grid
description: 'Build a "features" or "benefits" section: a section heading plus a responsive grid of cards, each with an icon, title and short text, in Tailwind v4. Use whenever a user asks for a features section, "why us", "what you get", benefits, services, a three-column icon list, or "the part under the hero that explains the product".'
---

# Feature grid

A feature grid answers "what does this do for me?" in a glance. The grid must stay readable at every width: one column on phones, two on tablets, three on desktops, and the items should be a real list so screen readers announce "list, 6 items". Icons are inline SVG so they inherit color and scale with text.

## Pattern

```html
<section class="bg-gray-50 py-16 sm:py-24 dark:bg-gray-900" aria-labelledby="features-heading">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

    <div class="mx-auto max-w-2xl text-center">
      <p class="text-sm font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400">Everything included</p>
      <h2 id="features-heading" class="mt-2 text-3xl font-bold tracking-tight text-balance text-gray-900 sm:text-4xl dark:text-white">
        Built for people who ship
      </h2>
      <p class="mt-4 text-lg text-pretty text-gray-600 dark:text-gray-400">
        No plugins to install, no dashboard to learn. Just the parts that matter.
      </p>
    </div>

    <ul role="list" class="mt-12 grid gap-6 sm:grid-cols-2 lg:mt-16 lg:grid-cols-3 lg:gap-8">

      <li class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-950 dark:ring-gray-800">
        <div class="flex size-10 items-center justify-center rounded-lg bg-blue-600 text-white">
          <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
        </div>
        <h3 class="mt-4 text-base font-semibold text-gray-900 dark:text-white">Instant deploys</h3>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Push to your branch and the site is live in seconds, with a preview URL for every change.
        </p>
      </li>

      <li class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-950 dark:ring-gray-800">
        <div class="flex size-10 items-center justify-center rounded-lg bg-blue-600 text-white">
          <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <h3 class="mt-4 text-base font-semibold text-gray-900 dark:text-white">Secure by default</h3>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          HTTPS, security headers and form spam protection are on from the first request.
        </p>
      </li>

      <!-- repeat <li> for each feature; 3 or 6 items fill a 3-column grid cleanly -->

    </ul>
  </div>
</section>
```

Why these choices:

- `<ul role="list">`: Tailwind's Preflight removes list bullets, and Safari then drops list semantics; `role="list"` restores them.
- `grid gap-6 sm:grid-cols-2 lg:grid-cols-3`: grid items stretch to equal height automatically, so cards with different text lengths still align.
- `aria-labelledby` on the section turns it into a named region that screen-reader users can jump to.
- The icon sits in a fixed `size-10` box; the SVG uses `currentColor` so changing `text-white` recolors it.
- Section heading is an `<h2>`, cards use `<h3>`: the outline stays correct when the section is dropped under the page's `<h1>`.

## Variations

- **Borderless list style**: remove `rounded-2xl bg-white shadow-sm ring-1` and use `gap-x-8 gap-y-12`; put the icon and heading on one row with `flex items-center gap-3`. Lighter feel for text-heavy feature sets.
- **Two-column with large icons**: `sm:grid-cols-2` only, icon box `size-12`, text `text-base`. Use for 4 features where 3 columns would leave an orphan.
- **Numbered steps**: replace the icon box with `<span class="text-2xl font-bold text-blue-600">01</span>`; good for "how it works" sections.
- **Bento layout**: on `lg:` let one card span two columns (`lg:col-span-2`) and hold a screenshot; keep the rest single-column.

## Pitfalls

- Five or seven items in a three-column grid leave a lonely card on the last row. Pick counts of 3, 6 or 9, or make the last card `sm:col-span-2 lg:col-span-1` and center it deliberately.
- Icons from a font or `<img>` cannot change color in dark mode. Use inline SVG with `fill="none" stroke="currentColor"` or `fill="currentColor"`.
- Long feature titles wrap differently per card and break the visual rhythm. Keep titles to three words or set `min-h-[2lh]` on the `<h3>` if they must vary.
- `hover:` lift effects on non-clickable cards lie to users. Only animate cards that are links; if the whole card is clickable, use `web-ui-cards` for the accessible clickable-card pattern.
- Centered body text in cards is hard to read beyond two lines. Left-align text inside cards even if the section header is centered.
- Giving every card a different accent color turns the section into a rainbow. One accent color, or a muted gray icon box with a single colored one for the headline feature.

## Related skills

- `web-layout-card-grid`
- `web-layout-landing-page`
- `web-ui-cards`
- `web-design-icons`
- `web-css-responsive-grid`
- `web-motion-scroll-reveal`
