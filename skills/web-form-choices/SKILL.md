---
name: web-form-choices
description: Style checkboxes, radio buttons, toggle switches, selectable cards and segmented controls with Tailwind while keeping the native input underneath, grouped in fieldsets with legends and full keyboard support. Use whenever a user asks for "checkboxes", "radio buttons", "a toggle", "on/off switch", "pick one of these options", "choice cards", "segmented control" or "pill selector" in a form or settings page.
---

# Choices: checkboxes, radios, switches, segmented controls

Every choice control in this skill is a native `<input type="checkbox">` or `<input type="radio">`. That is what gives you Space to toggle, arrow keys to move between radios, form submission, `required`, and screen-reader semantics for free. Styling happens on the input itself with `appearance-none` plus `checked:` variants, or on a wrapping `<label>` with `has-[:checked]:` for card and segmented looks. Groups live in a `<fieldset>` whose `<legend>` is the question, because a bare list of radios with no legend reads as "radio button, Pro, 2 of 3" with no idea what is being chosen.

## Pattern

```css
@import "tailwindcss";
@layer components {
  .check {
    @apply size-4 shrink-0 appearance-none rounded border border-gray-400 bg-white
           checked:border-blue-600 checked:bg-blue-600
           checked:bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 16%22 fill=%22none%22 stroke=%22white%22 stroke-width=%222.5%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22><path d=%22m3.5 8.5 3 3 6-7%22/></svg>')]
           bg-center bg-no-repeat
           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
           disabled:cursor-not-allowed disabled:opacity-50
           dark:border-gray-500 dark:bg-gray-900 dark:focus-visible:ring-offset-gray-900;
  }
  .radio { @apply check rounded-full checked:bg-none checked:shadow-[inset_0_0_0_3px_white] dark:checked:shadow-[inset_0_0_0_3px_theme(--color-gray-900)]; }
}
```

```html
<!-- Checkboxes: pick any -->
<fieldset class="space-y-3">
  <legend class="text-sm font-medium text-gray-800 dark:text-gray-200">Notify me about</legend>
  <label class="flex items-start gap-3 text-sm text-gray-700 dark:text-gray-300">
    <input type="checkbox" name="notify" value="comments" class="check mt-0.5" checked>
    <span>Comments <span class="block text-gray-500">When someone replies to you</span></span>
  </label>
  <label class="flex items-start gap-3 text-sm text-gray-700 dark:text-gray-300">
    <input type="checkbox" name="notify" value="mentions" class="check mt-0.5">
    <span>Mentions</span>
  </label>
</fieldset>

<!-- Radios: pick one, required -->
<fieldset class="space-y-3">
  <legend class="text-sm font-medium text-gray-800 dark:text-gray-200">Billing period</legend>
  <label class="flex items-center gap-3 text-sm"><input type="radio" name="period" value="monthly" class="radio" required> Monthly</label>
  <label class="flex items-center gap-3 text-sm"><input type="radio" name="period" value="yearly" class="radio"> Yearly <span class="text-green-700">(save 20%)</span></label>
</fieldset>

<!-- Switch: a checkbox with role=switch, immediate effect -->
<label class="flex items-center justify-between gap-4 text-sm">
  <span class="font-medium text-gray-800 dark:text-gray-200">Dark mode</span>
  <input type="checkbox" role="switch" name="dark" class="peer sr-only">
  <span aria-hidden="true"
    class="relative h-6 w-11 shrink-0 rounded-full bg-gray-300 transition-colors
           after:absolute after:top-0.5 after:left-0.5 after:size-5 after:rounded-full after:bg-white after:shadow after:transition-transform
           peer-checked:bg-blue-600 peer-checked:after:translate-x-5
           peer-focus-visible:ring-2 peer-focus-visible:ring-blue-500 peer-focus-visible:ring-offset-2
           motion-reduce:transition-none motion-reduce:after:transition-none dark:bg-gray-600"></span>
</label>

<!-- Choice cards: radios styled as selectable boxes -->
<fieldset>
  <legend class="mb-3 text-sm font-medium text-gray-800 dark:text-gray-200">Plan</legend>
  <div class="grid gap-3 sm:grid-cols-3">
    <label class="cursor-pointer rounded-lg border border-gray-300 p-4 transition-colors
                  has-[:checked]:border-blue-600 has-[:checked]:bg-blue-50 has-[:checked]:ring-1 has-[:checked]:ring-blue-600
                  has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-blue-500 dark:border-gray-600 dark:has-[:checked]:bg-blue-950">
      <input type="radio" name="plan" value="free" class="sr-only" checked>
      <span class="block font-semibold text-gray-900 dark:text-gray-100">Free</span>
      <span class="block text-sm text-gray-500">1 project</span>
    </label>
    <!-- repeat for Pro, Team -->
  </div>
</fieldset>

<!-- Segmented control: radios styled as a connected button row -->
<fieldset>
  <legend class="sr-only">View</legend>
  <div class="inline-flex rounded-md border border-gray-300 p-0.5 dark:border-gray-600">
    <label class="cursor-pointer rounded px-3 py-1.5 text-sm font-medium text-gray-600 has-[:checked]:bg-blue-600 has-[:checked]:text-white
                  has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-blue-500 dark:text-gray-300">
      <input type="radio" name="view" value="list" class="sr-only" checked>List</label>
    <label class="cursor-pointer rounded px-3 py-1.5 text-sm font-medium text-gray-600 has-[:checked]:bg-blue-600 has-[:checked]:text-white
                  has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-blue-500 dark:text-gray-300">
      <input type="radio" name="view" value="grid" class="sr-only">Grid</label>
  </div>
</fieldset>
```

```js
// A switch applies immediately; a checkbox waits for submit. Wire switches to their effect on change.
document.querySelectorAll('input[role=switch]').forEach((sw) => {
  sw.addEventListener('change', () => document.documentElement.classList.toggle('dark', sw.checked));
});
```

Why these choices: `appearance-none` + `checked:bg-[url(...)]` draws the tick with no extra element, so the input stays the clickable, focusable thing. `sr-only` (not `hidden`) on card and switch inputs keeps them in the tab order; `has-[:checked]` and `peer-checked` paint the visual from the real state. `role="switch"` changes the announcement from "checked" to "on" and tells users the change is immediate. Radios in a group are one tab stop with arrow keys moving selection, which is exactly what a segmented control should do, so no custom key handling is needed.

## Variations

- **Quick native styling** without `appearance-none`: `accent-blue-600 size-4` on any checkbox or radio recolors the OS control. Less control, zero risk.
- **Indeterminate "select all"** for tables: set `master.indeterminate = true` from JS when some rows are checked and add `indeterminate:bg-[url(...)]` with a dash icon.
- **Checkbox list with descriptions in a bordered stack**: wrap labels in `divide-y divide-gray-200 rounded-md border border-gray-200` and give each `p-4`.
- **Switch with text labels** ("Off" / "On") for settings pages: put `<span class="text-sm text-gray-500 peer-checked:hidden">Off</span>` and the mirrored `hidden peer-checked:inline` span after the input.

## Pitfalls

- A `<div>` with `onclick` toggling a class is not a checkbox: no keyboard, no form value, no screen-reader state. Always keep the input.
- `hidden` or `display:none` on the input removes it from the tab order; use `sr-only` for visually hidden inputs.
- Clickable area: the whole `<label>` toggles the input, so make labels `flex` with padding instead of putting the text in a sibling `<span>` outside the label.
- `required` on a radio group means "one in the group", but on a checkbox it means "this one must be checked" (fine for terms acceptance, wrong for "pick at least one"; validate that in JS).
- `has-[:checked]` targets any checked descendant; do not nest a second input (like a quantity field) inside a choice card, or it will light up the card.
- Switch thumb animation uses `translate-x`, not `left`, so it runs on the compositor; keep `motion-reduce:transition-none`.

## Related skills

- `web-form-layout`
- `web-form-validation`
- `web-form-input-states`
- `web-design-dark-mode`
- `web-ui-buttons`
- `web-a11y-aria-patterns`
