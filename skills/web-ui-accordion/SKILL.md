---
name: web-ui-accordion
description: Build an accordion or FAQ list with native <details>/<summary>: styled headers with a rotating chevron, one-open-at-a-time via the `name` attribute, smooth open/close animation, deep-linkable items. Use whenever a user asks for an accordion, FAQ, collapsible sections, expandable panels, "show more" toggles, or a disclosure widget.
---

# Accordion with `<details>` and `<summary>`

`<details>` is a complete disclosure widget: keyboard toggling (Enter/Space), the expanded state announced to screen readers, find-in-page that opens closed items, and no JavaScript. Tailwind's `open:` variant styles the expanded state, and the HTML `name` attribute (2023+) turns a group into an exclusive accordion where opening one closes the rest. The only thing worth scripting is a height animation, because browsers still cannot transition `display`.

## Pattern

```html
<section aria-labelledby="faq-title" class="mx-auto max-w-2xl px-4 py-12">
  <h2 id="faq-title" class="text-2xl font-bold tracking-tight">Frequently asked questions</h2>

  <div class="mt-6 divide-y divide-gray-200 rounded-xl border border-gray-200 dark:divide-gray-800 dark:border-gray-800">

    <details name="faq" id="faq-pricing" class="group" open>
      <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 font-medium
                      hover:bg-gray-50 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-indigo-600
                      dark:hover:bg-gray-900 [&::-webkit-details-marker]:hidden">
        <span>How does pricing work?</span>
        <svg class="size-5 shrink-0 text-gray-500 transition-transform duration-200 motion-reduce:transition-none group-open:rotate-180"
             viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.17l3.71-3.94a.75.75 0 1 1 1.08 1.04l-4.25 4.5a.75.75 0 0 1-1.08 0l-4.25-4.5a.75.75 0 0 1 .02-1.06Z" clip-rule="evenodd"/>
        </svg>
      </summary>
      <div class="px-5 pb-5 text-gray-600 dark:text-gray-400">
        <p>You pay per seat, billed monthly. Annual plans get two months free.</p>
      </div>
    </details>

    <details name="faq" id="faq-cancel" class="group">
      <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-indigo-600 dark:hover:bg-gray-900 [&::-webkit-details-marker]:hidden">
        <span>Can I cancel at any time?</span>
        <svg class="size-5 shrink-0 text-gray-500 transition-transform duration-200 motion-reduce:transition-none group-open:rotate-180" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.17l3.71-3.94a.75.75 0 1 1 1.08 1.04l-4.25 4.5a.75.75 0 0 1-1.08 0l-4.25-4.5a.75.75 0 0 1 .02-1.06Z" clip-rule="evenodd"/></svg>
      </summary>
      <div class="px-5 pb-5 text-gray-600 dark:text-gray-400">
        <p>Yes. Cancel from Settings and you keep access until the end of the billing period.</p>
      </div>
    </details>

  </div>
</section>
```

```css
/* Height animation using the ::details-content pseudo (Chrome 131+, Safari 18.4+); older browsers just snap. */
details::details-content {
  block-size: 0;
  overflow: hidden;
  transition: block-size .25s ease, content-visibility .25s allow-discrete;
}
details[open]::details-content { block-size: auto; }
@supports (interpolate-size: allow-keywords) {
  :root { interpolate-size: allow-keywords; }  /* lets 0 -> auto animate */
}
@media (prefers-reduced-motion: reduce) {
  details::details-content { transition: none; }
}
```

```js
// Optional: open the item named in the URL hash (#faq-cancel) and scroll to it
function openFromHash() {
  const target = document.getElementById(location.hash.slice(1));
  const details = target?.closest('details');
  if (details) { details.open = true; details.scrollIntoView({ block: 'start' }); }
}
addEventListener('hashchange', openFromHash);
openFromHash();
```

Why this shape: `name="faq"` on every `<details>` gives the exclusive behaviour natively; drop it when several items should stay open together. `list-none` plus the `::-webkit-details-marker` rule removes the default triangle so the chevron is the only indicator, and `group-open:rotate-180` flips it. The focus ring uses a negative offset so it stays inside the rounded container.

## Variations

- **Allow multiple open**: remove `name`. Add an "Expand all" button: `details.forEach(d => d.open = true)` (works only without `name`).
- **Flat list (no border)**: drop the wrapper border and use `border-b` on each `details`; good inside sidebars or settings pages.
- **Heading inside summary**: wrap the text in `<h3 class="text-base font-medium">` so the FAQ shows up in the document outline; the `<summary>` stays the interactive element.
- **Icon on the left, plus/minus**: put two SVGs in the summary and toggle with `group-open:hidden` / `hidden group-open:block`.
- **FAQ rich result**: pair with `web-seo-structured-data` and emit `FAQPage` JSON-LD from the same questions.

## Pitfalls

- Do not put interactive elements (links, buttons) inside `<summary>`; the whole summary is one button and nested controls confuse keyboard users. Put links in the content panel.
- `cursor-pointer` is not the default on `<summary>`; add it. Also make the whole row clickable by padding the summary, not the `details`.
- Animating `max-height` to a magic number causes a delayed snap when content is taller; prefer the `::details-content` transition above and accept an instant toggle on older browsers.
- `display: flex` on `<summary>` removes the marker in Chromium but not in Safari; keep the explicit `[&::-webkit-details-marker]:hidden` rule.
- Exclusive mode via `name` means the user cannot compare two answers side by side; for documentation-style FAQs allow multiple open.
- A `details` that is `open` by default and immediately closed by the `name` group (two items both `open`) will keep only the last one; set `open` on exactly one.

## Related skills

- `web-nav-tabs`
- `web-seo-structured-data`
- `web-motion-transitions`
- `web-a11y-semantic-html`
- `web-nav-sidebar`
