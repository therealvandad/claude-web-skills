---
name: web-ui-badges-chips-tags
description: 'Build badges, chips and tags with Tailwind: colour-coded status badges with a dot, notification count bubbles, removable filter chips with keyboard support, selectable tag toggles, and a tag input. Use whenever a user asks for a badge, label, pill, status indicator, tag, chip, "new" marker, unread count, or removable filter tokens.'
---

# Badges, chips and tags

Same shape, three jobs. A **badge** is read-only status or a count ("Paid", "3"). A **tag** labels content and often links to a listing. A **chip** is an interactive token the user can select or remove (active filters, recipients). The styling is a shared `inline-flex` pill; the semantics differ: badges are `<span>`, tags are `<a>`, chips are `<button>`s or checkboxes. Colour must never be the only signal, so every status badge carries text and most carry a dot or icon.

## Pattern

```html
<!-- Shared base via a tiny component layer so variants stay in sync.
     In production put this in your input CSS; with the Play CDN use type="text/tailwindcss". -->
<style type="text/tailwindcss">
  @layer components {
    .badge { @apply inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset whitespace-nowrap; }
  }
</style>

<!-- 1. Status badges: colour + text + dot -->
<span class="badge bg-green-50 text-green-700 ring-green-600/20 dark:bg-green-500/10 dark:text-green-400 dark:ring-green-500/30">
  <span class="size-1.5 rounded-full bg-current" aria-hidden="true"></span> Active
</span>
<span class="badge bg-amber-50 text-amber-700 ring-amber-600/20 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/30">
  <span class="size-1.5 rounded-full bg-current" aria-hidden="true"></span> Pending
</span>
<span class="badge bg-red-50 text-red-700 ring-red-600/20 dark:bg-red-500/10 dark:text-red-400 dark:ring-red-500/30">
  <span class="size-1.5 rounded-full bg-current" aria-hidden="true"></span> Failed
</span>
<span class="badge bg-gray-50 text-gray-600 ring-gray-500/20 dark:bg-gray-400/10 dark:text-gray-400 dark:ring-gray-400/20">Draft</span>

<!-- 2. Count bubble on an icon button -->
<button type="button" class="relative rounded-lg p-2 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:hover:bg-gray-800">
  <svg class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M14.86 17.08A2.99 2.99 0 0 1 9.14 17.08M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/></svg>
  <span class="sr-only">Notifications,</span>
  <span class="absolute -right-0.5 -top-0.5 min-w-5 rounded-full bg-red-600 px-1 text-center text-[11px] font-bold leading-5 text-white ring-2 ring-white dark:ring-gray-950">12</span>
  <span class="sr-only">unread</span>
</button>

<!-- 3. Tags: links to listings -->
<ul class="flex flex-wrap gap-2" aria-label="Tags">
  <li><a href="/tag/css" class="badge bg-gray-100 text-gray-700 ring-transparent hover:bg-gray-200 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">#css</a></li>
  <li><a href="/tag/tailwind" class="badge bg-gray-100 text-gray-700 ring-transparent hover:bg-gray-200 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">#tailwind</a></li>
</ul>

<!-- 4. Removable chips (active filters) -->
<ul id="filters" class="flex flex-wrap gap-2" aria-label="Active filters">
  <li class="badge bg-indigo-50 text-indigo-700 ring-indigo-600/20 py-1 pr-1 dark:bg-indigo-500/10 dark:text-indigo-300 dark:ring-indigo-500/30">
    Size: M
    <button type="button" data-remove aria-label="Remove filter Size: M"
      class="-mr-0.5 rounded-full p-0.5 hover:bg-indigo-600/20 focus-visible:outline-2 focus-visible:outline-indigo-600">
      <svg class="size-3.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/></svg>
    </button>
  </li>
</ul>

<!-- 5. Selectable chips (toggle filters) = styled checkboxes -->
<fieldset class="flex flex-wrap gap-2">
  <legend class="sr-only">Categories</legend>
  <label class="badge cursor-pointer bg-white text-gray-700 ring-gray-300 has-[:checked]:bg-indigo-600 has-[:checked]:text-white has-[:checked]:ring-indigo-600 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-indigo-600 dark:bg-gray-900 dark:text-gray-300 dark:ring-gray-700">
    <input type="checkbox" name="cat" value="design" class="sr-only"> Design
  </label>
  <label class="badge cursor-pointer bg-white text-gray-700 ring-gray-300 has-[:checked]:bg-indigo-600 has-[:checked]:text-white has-[:checked]:ring-indigo-600 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-indigo-600 dark:bg-gray-900 dark:text-gray-300 dark:ring-gray-700">
    <input type="checkbox" name="cat" value="dev" class="sr-only"> Development
  </label>
</fieldset>
```

```js
// Removable chips: remove, keep focus somewhere sensible, announce
const filters = document.getElementById('filters');
filters.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-remove]'); if (!btn) return;
  const chip = btn.closest('li');
  const next = chip.nextElementSibling?.querySelector('[data-remove]') ?? chip.previousElementSibling?.querySelector('[data-remove]');
  chip.remove();
  (next ?? document.getElementById('filter')).focus();   // fall back to the filter input
  filters.dispatchEvent(new CustomEvent('filters:change', { bubbles: true }));
});
```

Why this shape: `ring-1 ring-inset` instead of `border` keeps the pill the same size with or without an outline. `bg-current` on the dot inherits the text colour so each variant needs one colour decision. The count bubble has `sr-only` text around it because "12" alone means nothing to a screen reader. Selectable chips are real checkboxes styled through `has-[:checked]`, so form submission, keyboard and screen readers work with zero JS.

## Variations

- **Sizes**: small `px-2 py-px text-[11px]`, large `px-3 py-1 text-sm`. Keep the dot proportional (`size-2`).
- **Square badges** for codes and versions: `rounded-md font-mono` (`v2.1.0`, `GET`).
- **Dismissible with Backspace**: in a tag input, listen for `keydown` on the text field; if the field is empty and the key is `Backspace`, remove the last chip.
- **Live count updates**: set `textContent` and, if the badge matters (unread messages), wrap it in a `aria-live="polite"` region so changes are announced; cap display at `99+`.
- **Tag input**: a `<div class="flex flex-wrap gap-1 rounded-lg border p-1 focus-within:ring-2">` containing chips plus an `<input class="min-w-24 flex-1 border-0 focus:ring-0">`; on Enter or comma, create a chip from the value and clear the input.

## Pitfalls

- Colour alone fails WCAG 1.4.1; "Active" in green and "Failed" in red must still read correctly in greyscale, which the text and dot guarantee.
- Pastel badge text (`text-green-700` on `bg-green-50`) passes contrast; `text-green-500` on white does not. Check every variant in both themes.
- A chip's remove button must have an accessible name that includes the chip label ("Remove filter Size: M"), not just "Remove".
- Do not put the remove `<button>` inside an `<a>` tag; interactive content cannot nest. A removable tag that also links needs two sibling elements.
- `whitespace-nowrap` prevents ugly wrapped pills; if labels can be long, add `max-w-40 truncate` and a `title` or tooltip.
- Removing a chip without moving focus drops keyboard users at the top of the page; the JS moves focus to a neighbour or the input.

## Related skills

- `web-ui-buttons`
- `web-ui-data-table`
- `web-form-choices`
- `web-a11y-color-contrast`
- `web-css-layers-and-organization`
