---
name: web-section-steps-timeline
description: Build a "how it works" steps section or timeline: numbered horizontal steps with CSS connecting lines that stack vertically on phones, plus a dated vertical timeline for history or roadmap pages, as an ordered list in Tailwind v4. Use whenever a user asks for "steps", "how it works", "the process", "timeline", "our story", "roadmap", or "1-2-3 section".
---

# Steps and timeline

A steps section explains a sequence, so the markup is an `<ol>`: screen readers announce "list, 3 items" and "1 of 3", which is the whole point. The connecting line is drawn in CSS with a pseudo-element on each item rather than an absolutely positioned bar across the row, so it survives wrapping, uneven text heights, and the switch from horizontal to vertical at the breakpoint. Numbers do the work icons usually fail at: they say where you are.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="steps-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <div class="max-w-xl">
      <p class="font-mono text-xs uppercase tracking-widest text-stone-500">How a repair works</p>
      <h2 id="steps-heading" class="mt-3 text-3xl font-semibold tracking-tight text-balance text-stone-900 sm:text-4xl dark:text-stone-100">
        Post the watch, get a quote, decide. Nothing is done without your yes.
      </h2>
    </div>

    <ol class="mt-12 grid gap-10 md:grid-cols-3 md:gap-8" role="list">
      <li class="relative flex gap-5 md:block md:pt-10
                 before:absolute before:top-4 before:left-[1.1875rem] before:h-[calc(100%+2.5rem)] before:w-px before:bg-stone-300
                 last:before:hidden md:before:top-0 md:before:left-0 md:before:h-px md:before:w-[calc(100%+2rem)] md:last:before:block md:last:before:w-full
                 dark:before:bg-stone-700">
        <span class="relative z-10 flex size-10 shrink-0 items-center justify-center rounded-full border border-stone-300 bg-white font-mono text-sm text-stone-900 md:absolute md:-top-5 md:left-0 dark:border-stone-700 dark:bg-stone-950 dark:text-stone-100"
              aria-hidden="true">01</span>
        <div class="md:mt-2">
          <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Post it in the box we send</h3>
          <p class="mt-2 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
            Order a free padded mailer. It is insured to 5,000 pounds and tracked both ways. Most arrive at the Clerkenwell workshop next day.
          </p>
        </div>
      </li>

      <li class="relative flex gap-5 md:block md:pt-10
                 before:absolute before:top-4 before:left-[1.1875rem] before:h-[calc(100%+2.5rem)] before:w-px before:bg-stone-300
                 last:before:hidden md:before:top-0 md:before:left-0 md:before:h-px md:before:w-[calc(100%+2rem)] md:last:before:block md:last:before:w-full
                 dark:before:bg-stone-700">
        <span class="relative z-10 flex size-10 shrink-0 items-center justify-center rounded-full border border-stone-300 bg-white font-mono text-sm text-stone-900 md:absolute md:-top-5 md:left-0 dark:border-stone-700 dark:bg-stone-950 dark:text-stone-100"
              aria-hidden="true">02</span>
        <div class="md:mt-2">
          <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">We inspect and quote within 3 days</h3>
          <p class="mt-2 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
            A watchmaker opens the case, lists what is worn, and emails a fixed price with photos. Inspection is free if you decline.
          </p>
        </div>
      </li>

      <li class="relative flex gap-5 md:block md:pt-10
                 before:absolute before:top-4 before:left-[1.1875rem] before:h-[calc(100%+2.5rem)] before:w-px before:bg-stone-300
                 last:before:hidden md:before:top-0 md:before:left-0 md:before:h-px md:before:w-[calc(100%+2rem)] md:last:before:block md:last:before:w-full
                 dark:before:bg-stone-700">
        <span class="relative z-10 flex size-10 shrink-0 items-center justify-center rounded-full border border-stone-300 bg-white font-mono text-sm text-stone-900 md:absolute md:-top-5 md:left-0 dark:border-stone-700 dark:bg-stone-950 dark:text-stone-100"
              aria-hidden="true">03</span>
        <div class="md:mt-2">
          <h3 class="text-base font-semibold text-stone-900 dark:text-stone-100">Approve, and it is back in 2 to 6 weeks</h3>
          <p class="mt-2 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
            Pay on completion. Every service carries a 24-month guarantee on the work done, in writing with the invoice.
          </p>
        </div>
      </li>
    </ol>
  </div>
</section>
```

Why these choices:

- Below `md:` each `<li>` is a row (number left, text right) and `before:` draws a vertical hairline from the badge down into the gap, hidden on the last item. At `md:` the same pseudo-element rotates into a horizontal hairline along the top of the row, extending across the `gap-8` so the segments join.
- The number badge is `aria-hidden` because the `<ol>` already numbers the items for assistive tech; printing "01" twice is noise.
- `font-mono` badges with a hairline border, not a filled accent circle: the accent stays reserved for the page's action.
- The badge has an opaque background so it visually sits on top of the line where they cross.

Dated vertical timeline variant (history, roadmap, changelog):

```html
<ol class="relative mt-10 border-l border-stone-300 pl-8 dark:border-stone-700" role="list">
  <li class="relative pb-10 last:pb-0">
    <span class="absolute top-1 -left-[2.3125rem] size-3 rounded-full border-2 border-stone-900 bg-white dark:border-stone-100 dark:bg-stone-950" aria-hidden="true"></span>
    <time datetime="2019-03" class="font-mono text-xs text-stone-500">March 2019</time>
    <h3 class="mt-1 font-semibold text-stone-900 dark:text-stone-100">Opened the Clerkenwell bench</h3>
    <p class="mt-1 text-sm text-stone-600 dark:text-stone-400">One watchmaker, a lathe bought at auction, and a waiting list of eleven.</p>
  </li>
  <li class="relative pb-10 last:pb-0">
    <span class="absolute top-1 -left-[2.3125rem] size-3 rounded-full border-2 border-stone-900 bg-white dark:border-stone-100 dark:bg-stone-950" aria-hidden="true"></span>
    <time datetime="2023-09" class="font-mono text-xs text-stone-500">September 2023</time>
    <h3 class="mt-1 font-semibold text-stone-900 dark:text-stone-100">Accredited for Omega co-axial service</h3>
    <p class="mt-1 text-sm text-stone-600 dark:text-stone-400">Parts account opened; turnaround on calibre 8500 fell from nine weeks to four.</p>
  </li>
</ol>
```

## Variations

- **Current step highlighted** (checkout, onboarding): add `aria-current="step"` to the active `<li>` and style it with `[&[aria-current]_span]:bg-stone-900 [&[aria-current]_span]:text-white`; completed steps get a small check SVG in the badge.
- **Alternating timeline** on desktop: `md:grid md:grid-cols-[1fr_auto_1fr]` with the line in the middle column and items alternating `md:col-start-1 md:text-right` and `md:col-start-3`. Only worth it for six or more entries.
- **Four steps**: `md:grid-cols-2 lg:grid-cols-4`; at `md:` the line joins pairs, which still reads correctly because the numbers carry the order.
- **Compact, no section header**: drop the heading block and use `text-sm` throughout as an inline "how it works" inside a pricing or product page.

## Pitfalls

- An absolutely positioned bar across the whole row breaks the moment a title wraps to two lines on one card. Per-item pseudo-elements (as above) never misalign.
- A `<div>` grid with "1, 2, 3" as text loses the sequence for screen readers. It must be an `<ol>`; Preflight strips the markers, so `role="list"` keeps the list semantics in Safari.
- Dates written as plain text are not machine-readable. Wrap them in `<time datetime="2023-09">` so they can be parsed and so the mono styling is consistent.
- Connecting lines in the accent colour make the section look like a progress bar at 100%. Use the hairline neutral; reserve the accent for the current step only.
- Steps that are not really sequential ("Fast", "Secure", "Friendly") should not be numbered; that is a feature grid.
- Badge text `01` in a proportional font jitters in width between items. `font-mono` or `tabular-nums` keeps the circles identical.

## Related skills

- `web-layout-feature-grid`
- `web-form-multi-step`
- `web-craft-finishing-details`
- `web-motion-scroll-reveal`
- `web-css-responsive-grid`
- `web-a11y-aria-patterns`
