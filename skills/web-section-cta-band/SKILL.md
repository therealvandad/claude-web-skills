---
name: web-section-cta-band
description: Build a final call-to-action band: one headline, one primary button, a quieter secondary link and a reassurance line, in dark, brand-colour and bordered variants with Tailwind v4. Use whenever a user asks for a "call to action section", "CTA band", "get started section", "final pitch before the footer", or "the big coloured block with a button".
---

# CTA band

The CTA band is the last thing before the footer and the only section with a single job: get a click. Everything that is not the headline, the button, or the one sentence that removes the reader's last objection is noise. Keep it one accent (the button), one measure of text, and a layout that puts the button where a thumb lands on a phone.

## Pattern

```html
<section class="bg-stone-900 text-stone-100" aria-labelledby="cta-heading">
  <div class="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-16 sm:px-6 sm:py-20 lg:flex-row lg:items-center lg:justify-between lg:px-8 lg:py-24">

    <div class="max-w-2xl">
      <h2 id="cta-heading" class="text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
        Get a fixed quote for your loft conversion by Friday.
      </h2>
      <p class="mt-4 text-lg text-pretty text-stone-400">
        Send three photos and a rough floor size. Marlow Lofts, Reading, replies with a priced plan within two working days.
      </p>
    </div>

    <div class="flex shrink-0 flex-col items-start gap-4 sm:flex-row sm:items-center lg:flex-col lg:items-end">
      <a href="/quote"
         class="inline-flex w-full items-center justify-center rounded-md bg-amber-400 px-6 py-3.5 text-base font-semibold text-stone-950 hover:bg-amber-300 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-amber-400 sm:w-auto">
        Request a quote
      </a>
      <a href="/recent-work" class="text-sm font-medium text-stone-300 underline underline-offset-4 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-amber-400">
        See 14 recent conversions
      </a>
    </div>
  </div>

  <p class="mx-auto max-w-6xl border-t border-stone-800 px-4 py-4 font-mono text-xs text-stone-500 sm:px-6 lg:px-8">
    No deposit until drawings are approved. Quotes valid for 60 days.
  </p>
</section>
```

Why these choices:

- `lg:flex-row lg:justify-between` puts copy left and action right on desktop; on phones the stack keeps the button directly under the copy where the thumb is, and `w-full sm:w-auto` makes it a full-width tap target there.
- One primary (`bg-amber-400`) and one text link. A second filled button halves the click rate on the first; a second link costs nothing.
- The reassurance line is separated by a hairline, in mono, small. It answers "what if I regret this" without competing with the headline.
- The headline is a specific promise with a deadline and a noun. "Ready to get started?" asks the reader to do the work of imagining the benefit; see `web-craft-copy-that-sounds-human`.
- `aria-labelledby` makes it a named region so "jump to Get a fixed quote" works in a screen-reader landmark list.

## Variations

- **Brand colour band**: `bg-amber-400 text-stone-950` with the button inverted to `bg-stone-950 text-white hover:bg-stone-800`. Secondary link `text-stone-800`. Use when the page above is mostly neutral; do not use after a dark hero or the page ends in two heavy slabs.
- **Bordered, light**: `bg-white` with `rounded-lg border border-stone-300 p-8 sm:p-12` on the inner container and the band inside the normal page padding. Reads as a card inviting a decision; good inside long documentation pages.
- **With a short form**: replace the button group with a one-field email form from `web-section-newsletter-signup`; keep the headline about what the email gets them ("Get the price list"), not "Subscribe".
- **Centred, compact**: `text-center`, `max-w-xl mx-auto`, `py-12`, button only. Use between content sections as a mid-page nudge, never as the final band (the final one deserves the full layout).

## Pitfalls

- Two filled buttons of equal weight ("Start free" and "Book a demo") split attention and both lose. Pick one action; demote the other to a text link.
- A dark band directly after a dark footer, or a dark hero at the top and a dark band at the bottom with white in between, bookends the page like a template. Vary the surface: if the hero is dark, make the band bordered-light or brand-coloured.
- `bg-gradient-to-r from-purple-600 to-blue-600` is the universal CTA-band tell; use one flat colour with enough contrast for the button on it (check amber-on-stone at 4.5:1 or better).
- A full-width button with `w-full` on desktop stretches to 1,100px and looks like a banner ad. `sm:w-auto` restores a button.
- The reassurance line disappears if it is `text-stone-600` on `bg-stone-900` (fails contrast). `text-stone-500` on stone-900 is the floor; verify with `web-a11y-color-contrast`.
- Linking the button to `#` or a modal that is not built yet ships a dead end. Point it at a real page, even a plain form page.

## Related skills

- `web-layout-hero`
- `web-layout-landing-page`
- `web-section-newsletter-signup`
- `web-ui-buttons`
- `web-craft-copy-that-sounds-human`
- `web-a11y-color-contrast`
