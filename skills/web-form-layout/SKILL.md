---
name: web-form-layout
description: 'Build the skeleton of an accessible form with Tailwind: fieldsets with legends, labels tied to inputs, help text, reserved error slots, required markers, responsive two-column rows and a sticky action bar. Use whenever a user asks for a contact form, signup form, settings page, checkout form, or says "lay out these fields", even before validation is mentioned.'
---

# Form layout

A form is read top to bottom by eyes, by tab key and by screen readers, so its structure must be the same for all three. Group related fields in `<fieldset>`, tie every `<label>` to its control with `for`/`id`, keep help text and error text in fixed slots so the layout does not jump, and stack everything in one column on mobile. Two columns only when both fields are short and related (first/last name, city/postcode).

## Pattern

```html
<form class="mx-auto max-w-xl space-y-8 p-4 sm:p-6" novalidate>
  <fieldset class="space-y-5">
    <legend class="text-lg font-semibold text-gray-900 dark:text-gray-100">Your details</legend>
    <p class="text-sm text-gray-600 dark:text-gray-400">Fields marked <span aria-hidden="true">*</span> are required.</p>

    <!-- Two short, related fields: one column on mobile, two from sm: -->
    <div class="grid gap-5 sm:grid-cols-2">
      <div class="space-y-1.5">
        <label for="first" class="block text-sm font-medium text-gray-800 dark:text-gray-200">
          First name <span class="text-red-600" aria-hidden="true">*</span>
        </label>
        <input id="first" name="first" type="text" required autocomplete="given-name"
          aria-describedby="first-error"
          class="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 shadow-sm
                 placeholder:text-gray-400 focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
                 aria-invalid:border-red-500 aria-invalid:ring-red-500 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100">
        <p id="first-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
      </div>
      <div class="space-y-1.5">
        <label for="last" class="block text-sm font-medium text-gray-800 dark:text-gray-200">
          Last name <span class="text-red-600" aria-hidden="true">*</span>
        </label>
        <input id="last" name="last" type="text" required autocomplete="family-name"
          aria-describedby="last-error" class="block w-full rounded-md border border-gray-300 px-3 py-2 ...">
        <p id="last-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
      </div>
    </div>

    <!-- Field with help text: help id comes first in aria-describedby, error id second -->
    <div class="space-y-1.5">
      <label for="email" class="block text-sm font-medium text-gray-800 dark:text-gray-200">
        Email <span class="text-red-600" aria-hidden="true">*</span>
      </label>
      <input id="email" name="email" type="email" required autocomplete="email" inputmode="email"
        aria-describedby="email-help email-error" class="block w-full rounded-md border border-gray-300 px-3 py-2 ...">
      <p id="email-help" class="text-sm text-gray-500 dark:text-gray-400">We only use this to reply to you.</p>
      <p id="email-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
    </div>

    <div class="space-y-1.5">
      <label for="message" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Message</label>
      <textarea id="message" name="message" rows="4" aria-describedby="message-error"
        class="block w-full resize-y rounded-md border border-gray-300 px-3 py-2 ..."></textarea>
      <p id="message-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
    </div>
  </fieldset>

  <!-- Action bar: full-width stacked buttons on mobile, right-aligned row from sm: -->
  <div class="flex flex-col-reverse gap-3 border-t border-gray-200 pt-6 sm:flex-row sm:justify-end dark:border-gray-700">
    <button type="button" class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-300 dark:hover:bg-gray-800">Cancel</button>
    <button type="submit" class="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">Send message</button>
  </div>
</form>
```

Pull the repeated input classes into one component class so the markup stays readable:

```css
@import "tailwindcss";
@layer components {
  .field-input {
    @apply block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 shadow-sm
           placeholder:text-gray-400 focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
           aria-invalid:border-red-500 aria-invalid:ring-red-500 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100;
  }
}
```

Why these choices: `text-base` (16px) on inputs stops iOS Safari zooming on focus; `min-h-5` on the error slot reserves the line so nothing shifts when a message appears; `aria-live="polite"` on that slot announces errors injected by JS; `flex-col-reverse` puts the primary button on top on mobile while the DOM order keeps it last for tab order; `autocomplete` tokens let browsers and password managers fill the form correctly.

## Variations

- **Horizontal labels on wide screens** (settings pages): `sm:grid sm:grid-cols-[12rem_1fr] sm:items-start sm:gap-x-6` on each field wrapper, label in column one, input + help + error in column two.
- **Sectioned long forms**: one `<fieldset>` per section, separated with `divide-y divide-gray-200` on the parent, each legend as an `h2`-sized heading; add a sticky action bar with `sticky bottom-0 bg-white/90 backdrop-blur py-4`.
- **Optional instead of required markers**: when most fields are required, mark the few optional ones with `<span class="font-normal text-gray-500">(optional)</span>` inside the label instead of asterisks everywhere.
- **Compact inline form** (newsletter, search): `flex flex-col gap-2 sm:flex-row`, label visually hidden with `sr-only` but still present.

## Pitfalls

- Placeholder is not a label. It disappears on typing and has poor contrast; always ship a visible `<label>` (or `sr-only` for one-field forms).
- Wrapping a label around an input without `for`/`id` works for clicks but breaks `aria-describedby` wiring and some assistive tech; use explicit `for` and `id`.
- `<legend>` must be the first child of `<fieldset>`; Tailwind's `space-y-*` on the fieldset is fine, but do not float or absolutely position the legend.
- Two-column rows on phones cause horizontal squeeze; always start with one column and add `sm:grid-cols-2` only for pairs of short fields.
- `aria-describedby` points to the help text and the error slot; if you later add a new paragraph, update the id list or screen readers will not read it.
- Keep the `novalidate` attribute only when you take over validation in JS (see `web-form-validation`); without JS, remove it so the browser validates.

## Related skills

- `web-form-validation`
- `web-form-input-states`
- `web-form-choices`
- `web-form-submit-with-fetch`
- `web-css-responsive-grid`
- `web-a11y-semantic-html`
