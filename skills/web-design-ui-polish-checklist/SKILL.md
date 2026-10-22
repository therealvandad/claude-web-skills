---
name: web-design-ui-polish-checklist
description: 'Run a final visual-polish pass over a Tailwind page: a checklist for alignment, spacing, type, color and contrast, hover/focus/active states, text wrapping and truncation, images, responsive edges and dark mode, each item with a class-level fix. Use whenever a user says the page "looks off", "feels unfinished", asks to polish, refine, tidy up, or review the UI before shipping.'
---

# UI polish checklist

Polish is the last 10% that makes a page feel designed: consistent gaps, nothing jittering on hover, no orphaned words, every state present. Work through the list in order (structure before surface), fix each item with the class named, and stop when the whole list is green. Most items take one class; the value of the list is not forgetting any.

## Pattern

```html
<!-- Reference card that passes every item below; use it to compare against yours. -->
<article class="relative flex flex-col gap-4 rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-950/5
                motion-safe:transition-shadow hover:shadow-md dark:bg-gray-900 dark:ring-white/10
                has-[a:focus-visible]:ring-2 has-[a:focus-visible]:ring-indigo-600">
  <img src="/img/cover-800.webp" width="800" height="450" alt="" loading="lazy"
       class="aspect-video w-full rounded-md bg-gray-100 object-cover dark:bg-gray-800">
  <div class="flex items-start justify-between gap-3">
    <h3 class="text-pretty text-lg font-semibold leading-snug text-gray-900 dark:text-gray-100">
      <!-- Link covers the whole card; its focus ring is drawn on the card via has-[] above. -->
      <a href="/post/1" class="after:absolute after:inset-0 focus-visible:outline-none">Designing for the slow path</a>
    </h3>
    <span class="shrink-0 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 tabular-nums dark:bg-indigo-950 dark:text-indigo-300">8 min</span>
  </div>
  <p class="line-clamp-3 text-sm leading-relaxed text-gray-600 dark:text-gray-400">
    Three-line clamp with a visible end; the full text is in the DOM for screen readers and search.
  </p>
  <p class="mt-auto truncate text-xs text-gray-500" title="Ada Lovelace · Engineering · 14 Oct 2026">Ada Lovelace · Engineering · 14 Oct 2026</p>
</article>
```

### 1. Alignment and spacing
- Every gap on one scale: `gap-4` / `gap-6` / `gap-8`, section `py-16 sm:py-24`. Ad-hoc `mt-[13px]` means a token is missing. See `web-css-spacing-scale`.
- Siblings use `gap-*` or `space-y-*` on the parent, not margins on each child; the last child then has no trailing gap.
- Text aligns to text, not to icons: in a row with an icon, `items-start` plus `mt-0.5` on the icon lines up with the cap height.
- Equal-height cards: parent `grid`, card `flex flex-col`, and `mt-auto` on the footer row.
- Optical alignment: a left-aligned heading above a bordered box sits flush; a `rounded-full` button next to square ones needs `px-4` not `px-3` to look the same width.

### 2. Type
- Headings `text-balance`, paragraphs `text-pretty` (no single-word last lines).
- Line length `max-w-prose` (65ch) on any running text wider than a card.
- Numbers in tables and prices `tabular-nums` so columns do not wobble.
- Headings `tracking-tight` from `text-2xl` up; small caps labels `uppercase tracking-wide text-xs font-medium`.
- Links in body text `underline underline-offset-2 decoration-gray-400 hover:decoration-current`, not color alone.

### 3. Color and contrast
- Body text at least 4.5:1: `text-gray-700` on white, `text-gray-300` on `gray-950`. Placeholder `placeholder:text-gray-400` minimum.
- No pure black on pure white: `text-gray-900` on `bg-gray-50` or `bg-white`.
- One accent for all interactive elements; status colors (`green/amber/red`) only for status.
- Disabled is `disabled:opacity-50 disabled:cursor-not-allowed`, not a lighter custom grey that fails contrast anyway.

### 4. States
- Hover on every clickable: `hover:bg-gray-100` or `hover:shadow-md`, inside `motion-safe:transition-colors duration-150`.
- Focus visible on everything tabbable: `focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600`; never `outline-none` without it.
- Active press feel: `active:scale-[0.98]` or `active:bg-gray-200` on buttons.
- `aria-current="page"` on the current nav link and style it: `aria-[current=page]:font-semibold aria-[current=page]:text-indigo-600`.
- Loading, empty, error states exist for every fetch (see `web-design-empty-and-error-states`).

### 5. Wrapping and truncation
- Long single-line values (emails, URLs, file names) `truncate` with a `title` or visible full text elsewhere; multi-line `line-clamp-2`/`-3`.
- `truncate` needs a constrained width: the parent must have `min-w-0` inside flex/grid or the text will not clip.
- User-generated strings `break-words` (or `wrap-anywhere` in Tailwind v4.1+) so a 60-character token cannot blow out a card.
- Badges and buttons `whitespace-nowrap shrink-0` so they never wrap mid-label.
- Labels with counts: `tabular-nums` and `min-w-[2ch]` on the number so "9" and "10" do not shift the row.

### 6. Images and media
- `width`/`height` on every `<img>`; `aspect-*` + `object-cover` on anything in a card.
- Background behind images (`bg-gray-100`) so the slot is visible before load and if the image 404s.
- Avatars `rounded-full object-cover` with a fallback initial behind them.

### 7. Responsive edges
- Horizontal padding on the outermost container `px-4 sm:px-6 lg:px-8`; nothing touches the viewport edge at 360px.
- No horizontal scrollbar: check for `w-screen`, fixed-width tables (`overflow-x-auto` wrapper) and long words (`break-words`).
- Tap targets at least 44px on touch: `min-h-11` on buttons, `py-3` on list rows.
- Sticky header plus in-page anchors: `scroll-mt-20` on targets.

### 8. Dark mode
- Every `bg-white` has a `dark:` pair; every `ring-gray-200` becomes `dark:ring-white/10`; shadows `dark:shadow-none`.
- Images with white backgrounds get `dark:brightness-90` or a dark variant; logos with black strokes get a second asset.
- Test with `color-scheme: dark` on `<html>` so form controls flip too.

## Variations

- **Dashboard pass.** Add: table rows `even:bg-gray-50`, sticky `thead` with `bg-white/95 backdrop-blur`, consistent column alignment (`text-right tabular-nums` for numbers).
- **Marketing pass.** Add: section rhythm (`py-20 sm:py-28`), one CTA style across the page, hero image `fetchpriority="high"`, consistent max width (`max-w-6xl`) on every section.
- **Form pass.** Add: labels above inputs, `min-h-5` error slots so nothing jumps, `autocomplete` on every field, submit button full width on mobile (`w-full sm:w-auto`).

## Pitfalls

- Fixing spacing with one-off arbitrary values (`mt-[7px]`) hides the real problem: a missing line-height or an icon without `shrink-0`. Find the cause.
- `transition-all` animates layout properties and causes jank; name the property: `transition-colors`, `transition-shadow`, `transition-transform`.
- `line-clamp` hides text visually only; it stays readable to screen readers, which is good, but do not clamp content that has no other way to be read in full.
- `hover:` styles that change size (`hover:p-5`) shift neighbours; change `transform`, `shadow` or color only.
- Adding `dark:` classes by hand to hundreds of elements is error-prone; if the pass finds more than a dozen misses, switch to semantic tokens (`bg-surface`, `text-fg`) from `web-design-color-system`.
- Checking polish only at desktop width; most misses (edge padding, truncation, tap targets) only appear at 360px.

## Related skills

- `web-css-spacing-scale`
- `web-design-typography-system`
- `web-a11y-color-contrast`
- `web-a11y-keyboard-and-focus`
- `web-design-dark-mode`
- `web-ship-launch-checklist`
