---
name: web-section-comparison-table
description: Build a feature comparison table: a real <table> with scoped headers, a sticky first column that scrolls horizontally on phones, check and dash cells with text equivalents, and a highlighted recommended column, in Tailwind v4. Use whenever a user asks to "compare plans", tiers, products or competitors, or says "comparison table", "feature matrix", or "us vs them".
---

# Comparison table

A comparison table answers "does the plan I am looking at include the thing I need". That is a two-dimensional lookup, which is exactly what `<table>` with `<th scope="row">` and `<th scope="col">` gives screen readers: focus a cell and hear "Priority support, Studio, included". A grid of `<div>`s loses that. The hard part is phones: four columns never fit at 375px, so the table scrolls horizontally inside a wrapper while the feature-name column stays pinned.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="compare-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <h2 id="compare-heading" class="text-3xl font-semibold tracking-tight text-balance text-stone-900 sm:text-4xl dark:text-stone-100">
      What each Fieldbook plan includes
    </h2>
    <p class="mt-3 max-w-xl text-stone-600 dark:text-stone-400">Prices per site per month, billed yearly. Switch plans any time; the difference is pro-rated.</p>

    <div class="mt-10 overflow-x-auto rounded-lg border border-stone-300 dark:border-stone-700" role="region" aria-labelledby="compare-heading" tabindex="0">
      <table class="w-full min-w-[40rem] border-collapse text-sm">
        <caption class="sr-only">Feature comparison of the Solo, Studio and Practice plans</caption>
        <thead>
          <tr class="border-b border-stone-300 dark:border-stone-700">
            <th scope="col" class="sticky left-0 z-10 bg-white p-4 text-left font-medium text-stone-500 dark:bg-stone-950">Feature</th>
            <th scope="col" class="p-4 text-left">
              <span class="block text-base font-semibold text-stone-900 dark:text-stone-100">Solo</span>
              <span class="block font-normal text-stone-500">19 pounds</span>
            </th>
            <th scope="col" class="bg-stone-50 p-4 text-left dark:bg-stone-900">
              <span class="block text-base font-semibold text-stone-900 dark:text-stone-100">Studio <span class="ml-1 rounded-full border border-stone-900 px-2 py-0.5 font-mono text-[0.65rem] uppercase tracking-wide dark:border-stone-100">Most chosen</span></span>
              <span class="block font-normal text-stone-500">49 pounds</span>
            </th>
            <th scope="col" class="p-4 text-left">
              <span class="block text-base font-semibold text-stone-900 dark:text-stone-100">Practice</span>
              <span class="block font-normal text-stone-500">140 pounds</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-stone-200 dark:divide-stone-800">
          <tr>
            <th scope="row" class="sticky left-0 z-10 bg-white p-4 text-left font-medium text-stone-900 dark:bg-stone-950 dark:text-stone-100">Site diaries</th>
            <td class="p-4 text-stone-700 dark:text-stone-300">1 site</td>
            <td class="bg-stone-50 p-4 text-stone-700 dark:bg-stone-900 dark:text-stone-300">Up to 8 sites</td>
            <td class="p-4 text-stone-700 dark:text-stone-300">Unlimited</td>
          </tr>
          <tr>
            <th scope="row" class="sticky left-0 z-10 bg-white p-4 text-left font-medium text-stone-900 dark:bg-stone-950 dark:text-stone-100">Snagging lists with photos</th>
            <td class="p-4"><svg class="size-5 text-stone-900 dark:text-stone-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span class="sr-only">Included</span></td>
            <td class="bg-stone-50 p-4 dark:bg-stone-900"><svg class="size-5 text-stone-900 dark:text-stone-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span class="sr-only">Included</span></td>
            <td class="p-4"><svg class="size-5 text-stone-900 dark:text-stone-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span class="sr-only">Included</span></td>
          </tr>
          <tr>
            <th scope="row" class="sticky left-0 z-10 bg-white p-4 text-left font-medium text-stone-900 dark:bg-stone-950 dark:text-stone-100">Export to CAD (DXF)</th>
            <td class="p-4 text-stone-400" aria-label="Not included">&mdash;</td>
            <td class="bg-stone-50 p-4 dark:bg-stone-900"><svg class="size-5 text-stone-900 dark:text-stone-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span class="sr-only">Included</span></td>
            <td class="p-4"><svg class="size-5 text-stone-900 dark:text-stone-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span class="sr-only">Included</span></td>
          </tr>
          <tr>
            <th scope="row" class="sticky left-0 z-10 bg-white p-4 text-left font-medium text-stone-900 dark:bg-stone-950 dark:text-stone-100">Phone support</th>
            <td class="p-4 text-stone-400" aria-label="Not included">&mdash;</td>
            <td class="bg-stone-50 p-4 text-stone-700 dark:bg-stone-900 dark:text-stone-300">Weekdays 9 to 5</td>
            <td class="p-4 text-stone-700 dark:text-stone-300">Weekdays, 1-hour callback</td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="border-t border-stone-300 dark:border-stone-700">
            <td class="sticky left-0 z-10 bg-white p-4 dark:bg-stone-950"></td>
            <td class="p-4"><a href="/signup?plan=solo" class="font-medium underline underline-offset-4">Choose Solo</a></td>
            <td class="bg-stone-50 p-4 dark:bg-stone-900"><a href="/signup?plan=studio" class="inline-block rounded-md bg-stone-900 px-4 py-2 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 dark:bg-stone-100 dark:text-stone-900">Choose Studio</a></td>
            <td class="p-4"><a href="/signup?plan=practice" class="font-medium underline underline-offset-4">Choose Practice</a></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</section>
```

Why these choices:

- The scroll wrapper has `role="region"`, a label and `tabindex="0"` so keyboard users can focus it and scroll with arrow keys; without `tabindex` an overflow container is unreachable from the keyboard.
- `sticky left-0` on the row headers with an opaque `bg-white` keeps feature names visible while plan columns scroll under them. The background is mandatory; a transparent sticky cell lets scrolled content show through.
- Check icons are `aria-hidden` with an `sr-only` "Included"; the dash cell carries `aria-label="Not included"`. A bare check mark or em dash is announced as nothing or "em dash".
- The recommended column is a tinted surface (`bg-stone-50`) plus a label in the header and a filled button in the footer. No accent-coloured column; the one accent is the button.
- `min-w-[40rem]` forces horizontal scroll on phones instead of crushing four columns to one word per line.

## Variations

- **Mobile card fallback**: hide the table below `md:` (`hidden md:block`) and render one `<section>` per plan as a `<dl>` of feature and value pairs, with a `<select>` to pick the plan. More work, but better when the table has 15+ rows.
- **Us versus competitors**: first column stays features, other columns are product names; keep your own column tinted and put a source line under the table ("Compared against public pricing pages, 4 March 2026").
- **Grouped rows**: insert `<tr><th scope="colgroup" colspan="4" class="bg-stone-100 p-3 font-mono text-xs uppercase tracking-widest">Reporting</th></tr>` between groups so long tables have landmarks.
- **Dark**: `bg-stone-950` on sticky cells, `bg-stone-900` on the highlighted column, borders `stone-800`. Check icons stay neutral, not green.

## Pitfalls

- Sticky first column on iOS Safari flickers or lags when the cell has no explicit background or when `overflow-x` is on the `<table>` instead of a wrapper `<div>`. Keep the wrapper and the opaque background.
- `border-collapse` breaks `sticky` in some Safari versions; if the pinned column slides, switch to `border-separate border-spacing-0` and draw borders on cells.
- Colouring checks green and dashes red adds a second and third hue to the page and fails for colour-blind readers. Shape (check versus dash) plus the text equivalent carries the meaning.
- A highlighted column that differs by colour only is lost on a greyscale print and under forced-colours mode. The "Most chosen" label is the real signal; the tint is a bonus.
- Padding of `p-4` in 30 rows makes a 2,000px table. Use `py-3` for dense tables and group rows so the eye has rest stops.
- Hover-highlighting rows is useful on desktop but does nothing on touch; never put the only link to a plan inside a hover state.

## Related skills

- `web-ui-data-table`
- `web-layout-pricing-table`
- `web-css-sticky-and-fixed`
- `web-a11y-semantic-html`
- `web-a11y-color-contrast`
- `web-design-icons`
