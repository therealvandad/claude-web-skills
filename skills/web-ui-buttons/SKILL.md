---
name: web-ui-buttons
description: 'Build a button system with Tailwind v4: primary/secondary/outline/ghost/danger variants, three sizes, icon-only buttons with labels, a loading state, link-styled-as-button rules, and segmented button groups, defined once with @layer components. Use whenever a user asks for buttons, a CTA, button styles, icon buttons, a button group, toolbar, or "make the buttons consistent".'
---

# Buttons

Buttons are the most repeated component on any site, so define them once. A `.btn` base plus variant and size classes in `@layer components` gives consistent height, focus ring and disabled look everywhere, while still allowing utilities to override per instance. The rules that matter most: a `<button>` does things, an `<a>` goes places (style one like the other, never swap the elements); every button has a visible focus ring; icon-only buttons have a text name; loading buttons stay the same width and keep focus.

## Pattern

```css
/* input.css (or <style type="text/tailwindcss"> with the Play CDN) */
@import "tailwindcss";

@layer components {
  .btn {
    @apply inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold
           whitespace-nowrap select-none transition-colors motion-reduce:transition-none
           focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600
           disabled:pointer-events-none disabled:opacity-50 aria-disabled:pointer-events-none aria-disabled:opacity-50;
  }
  .btn-primary   { @apply bg-indigo-600 text-white hover:bg-indigo-500 active:bg-indigo-700; }
  .btn-secondary { @apply bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700; }
  .btn-outline   { @apply ring-1 ring-inset ring-gray-300 text-gray-900 hover:bg-gray-50 dark:ring-gray-700 dark:text-gray-100 dark:hover:bg-gray-900; }
  .btn-ghost     { @apply text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800; }
  .btn-danger    { @apply bg-red-600 text-white hover:bg-red-500 focus-visible:outline-red-600; }
  .btn-sm   { @apply px-3 py-1.5 text-xs rounded-md; }
  .btn-lg   { @apply px-6 py-3 text-base; }
  .btn-icon { @apply p-2 aspect-square; }   /* pair with .btn-sm or .btn-lg to size */
}
```

```html
<!-- Variants and sizes -->
<button type="button" class="btn btn-primary">Save changes</button>
<button type="button" class="btn btn-secondary">Cancel</button>
<button type="button" class="btn btn-outline btn-sm">Filter</button>
<button type="button" class="btn btn-ghost">Learn more</button>
<button type="button" class="btn btn-danger">Delete project</button>

<!-- With leading icon -->
<button type="button" class="btn btn-primary">
  <svg class="size-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z"/></svg>
  New item
</button>

<!-- Icon-only: visible icon, invisible name -->
<button type="button" class="btn btn-ghost btn-icon" aria-label="Settings">
  <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/></svg>
</button>

<!-- Link that looks like a button (navigation only) -->
<a href="/pricing" class="btn btn-outline">See pricing</a>

<!-- Loading state: same width, focus kept, announced -->
<button type="submit" class="btn btn-primary" data-loading-text="Saving…">
  <span data-label>Save changes</span>
</button>

<!-- Segmented group (single choice) = radios -->
<fieldset class="inline-flex rounded-lg bg-gray-100 p-1 dark:bg-gray-800">
  <legend class="sr-only">Billing period</legend>
  <label class="btn btn-sm cursor-pointer text-gray-600 has-[:checked]:bg-white has-[:checked]:text-gray-900 has-[:checked]:shadow-sm has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-indigo-600 dark:text-gray-400 dark:has-[:checked]:bg-gray-900 dark:has-[:checked]:text-gray-100">
    <input type="radio" name="period" value="monthly" class="sr-only" checked> Monthly
  </label>
  <label class="btn btn-sm cursor-pointer text-gray-600 has-[:checked]:bg-white has-[:checked]:text-gray-900 has-[:checked]:shadow-sm has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-indigo-600 dark:text-gray-400 dark:has-[:checked]:bg-gray-900 dark:has-[:checked]:text-gray-100">
    <input type="radio" name="period" value="yearly" class="sr-only"> Yearly
  </label>
</fieldset>

<!-- Toolbar of actions (buttons joined edge to edge) -->
<div role="group" aria-label="Text style" class="inline-flex -space-x-px">
  <button type="button" aria-pressed="true" class="btn btn-outline btn-icon rounded-r-none aria-pressed:bg-indigo-50 aria-pressed:text-indigo-700 dark:aria-pressed:bg-indigo-950"><b aria-hidden="true">B</b><span class="sr-only">Bold</span></button>
  <button type="button" aria-pressed="false" class="btn btn-outline btn-icon rounded-none aria-pressed:bg-indigo-50 aria-pressed:text-indigo-700"><i aria-hidden="true">I</i><span class="sr-only">Italic</span></button>
  <button type="button" aria-pressed="false" class="btn btn-outline btn-icon rounded-l-none aria-pressed:bg-indigo-50 aria-pressed:text-indigo-700"><u aria-hidden="true">U</u><span class="sr-only">Underline</span></button>
</div>
```

```js
// Loading state helper
const SPINNER = '<svg class="size-4 animate-spin motion-reduce:animate-none" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/></svg>';
export function setLoading(btn, loading) {
  const label = btn.querySelector('[data-label]');
  if (loading) {
    btn.style.minWidth = `${btn.offsetWidth}px`;           // no width jump
    btn.setAttribute('aria-disabled', 'true');             // not `disabled`: focus stays, screen reader still finds it
    btn.dataset.originalText = label.textContent;
    label.innerHTML = `${SPINNER}<span class="sr-only">${btn.dataset.loadingText ?? 'Loading'}</span>`;
    label.classList.add('inline-flex', 'items-center');
  } else {
    btn.removeAttribute('aria-disabled');
    btn.style.minWidth = '';
    label.textContent = btn.dataset.originalText;
  }
}
// Guard clicks while aria-disabled (pointer-events-none covers mouse; this covers keyboard)
document.addEventListener('click', (e) => {
  if (e.target.closest('[aria-disabled="true"]')) e.preventDefault();
}, true);
```

Why this shape: `@apply` inside `@layer components` keeps the classes overridable by utilities (`class="btn btn-primary w-full"` works because utilities come later in the cascade). `focus-visible` rings show for keyboard users only. `aria-disabled` is used for the loading state because `disabled` removes the button from the tab order, dropping keyboard focus to the document body mid-submit. Toggle buttons use `aria-pressed`, exclusive choices use radios; both are real native state.

## Variations

- **Full-width on mobile**: `class="btn btn-primary w-full sm:w-auto"`; stack CTAs with `flex-col-reverse sm:flex-row` so the primary ends up last in DOM but first on mobile.
- **Theme tokens**: replace `indigo-600` with `bg-brand` after defining `@theme { --color-brand: oklch(55% 0.2 270); }` so one line restyles every button.
- **Rounded pill**: add `rounded-full` on the instance; `.btn-icon` pills become perfect circles.
- **Destructive confirm**: `.btn-danger` only for the final confirmation, inside a `web-ui-modal-dialog`; the opener stays `.btn-outline` with red text so one stray click cannot delete.

## Pitfalls

- A `<button>` inside a `<form>` defaults to `type="submit"`; always write `type="button"` unless it submits.
- `<div onclick>` and `<a href="#">` as buttons are not keyboard-operable or announced as buttons; use `<button>`. Style an `<a>` with `.btn` only when it navigates.
- `opacity-50` disabled buttons often fail contrast; that is acceptable per WCAG for disabled controls, but keep enough contrast that the label is still readable.
- Minimum tap target is 24 px (WCAG 2.5.8) and ideally 44 px; `.btn-sm` icon buttons at `p-1.5` with a 16 px icon are 28 px, add spacing between them or bump the size on touch layouts.
- `@apply` with variants (`hover:`, `dark:`) works in v4, but you cannot `@apply` a class defined in another `@layer components` rule; compose from utilities only.
- Never remove the focus outline without replacing it; the base class supplies it, so do not add `focus:outline-none` per instance.

## Related skills

- `web-ui-badges-chips-tags`
- `web-ui-skeleton-and-loading`
- `web-form-submit-with-fetch`
- `web-css-layers-and-organization`
- `web-motion-hover-microinteractions`
