---
name: web-form-input-states
description: 'Style every state of a text input with Tailwind: default, hover, focus ring, disabled, readonly, invalid, valid, loading (async check) and a floating label that lifts on focus or content. Use whenever a user asks to "style the inputs", wants a "floating label", "material style input", "disabled look", "input with spinner", or asks why the focus ring is missing.'
---

# Input states

An input communicates through its border, ring and label long before any error text appears. Define the states once as a component class driven by native pseudo-classes (`:focus-visible`, `:disabled`, `:read-only`, `:placeholder-shown`, `:user-invalid`) and ARIA attributes (`aria-invalid`, `aria-busy`), so JavaScript only ever toggles attributes and never touches class lists. The floating label is pure CSS: it sits inside the box and lifts when the field has focus or content, which needs the `placeholder-shown` trick (a placeholder of a single space) because CSS cannot detect "has a value" any other way.

## Pattern

```css
@import "tailwindcss";

@layer components {
  .field {
    @apply block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 shadow-sm
           transition-[border-color,box-shadow] duration-150
           placeholder:text-gray-400
           hover:border-gray-400
           focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40
           disabled:cursor-not-allowed disabled:border-gray-200 disabled:bg-gray-50 disabled:text-gray-500
           read-only:bg-gray-50 read-only:text-gray-700 read-only:focus-visible:ring-0 read-only:focus-visible:border-gray-300
           aria-invalid:border-red-500 aria-invalid:focus-visible:ring-red-500/40
           aria-busy:bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%236b7280%22 stroke-width=%223%22><circle cx=%2212%22 cy=%2212%22 r=%229%22 stroke-opacity=%22.25%22/><path d=%22M21 12a9 9 0 0 0-9-9%22/></svg>')]
           aria-busy:bg-[length:1.25rem] aria-busy:bg-[position:right_0.75rem_center] aria-busy:bg-no-repeat aria-busy:pr-10
           dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 dark:hover:border-gray-500
           dark:disabled:bg-gray-800 dark:read-only:bg-gray-800;
  }
  .field[data-valid="true"] { @apply border-green-600 focus-visible:ring-green-500/40; }
}

/* Spin the aria-busy icon, but not for people who asked for less motion */
@media (prefers-reduced-motion: no-preference) {
  .field[aria-busy="true"] { animation: field-busy 1s linear infinite; }
  @keyframes field-busy { to { background-position: right 0.75rem center; } }
}
```

```html
<!-- Standard label above -->
<div class="space-y-1.5">
  <label for="company" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Company</label>
  <input id="company" name="company" type="text" class="field" placeholder="Acme Ltd" autocomplete="organization">
</div>

<!-- Disabled and readonly: different meanings, different looks -->
<input type="text" class="field" value="Not available on this plan" disabled aria-describedby="plan-note">
<input type="text" class="field" value="ACC-20931" readonly aria-describedby="acc-note">

<!-- Async-checked field: JS sets aria-busy while a fetch runs -->
<input id="handle" name="handle" type="text" class="field" aria-describedby="handle-error">
<p id="handle-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>

<!-- Floating label: label sits in the box, lifts on focus or when a value exists -->
<div class="relative">
  <input id="fl-email" name="email" type="email" placeholder=" " autocomplete="email"
    class="peer field pt-5 pb-1.5 placeholder-transparent">
  <label for="fl-email"
    class="pointer-events-none absolute top-1.5 left-3 text-xs text-gray-500 transition-all duration-150
           peer-placeholder-shown:top-3 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400
           peer-focus-visible:top-1.5 peer-focus-visible:text-xs peer-focus-visible:text-blue-600
           motion-reduce:transition-none dark:text-gray-400">Email</label>
</div>
```

```js
// Mark a field busy during an async check, then valid or invalid
async function checkHandle(input) {
  input.setAttribute('aria-busy', 'true');
  try {
    const res = await fetch(`/api/handles/${encodeURIComponent(input.value)}`);
    const taken = (await res.json()).taken;
    input.toggleAttribute('aria-invalid', taken);
    input.dataset.valid = String(!taken);
    document.getElementById('handle-error').textContent = taken ? 'That handle is taken.' : '';
  } finally {
    input.removeAttribute('aria-busy');
  }
}
document.getElementById('handle')?.addEventListener('change', (e) => checkHandle(e.target));
```

Why these choices: `focus-visible` rather than `focus` keeps the ring for keyboard and pointer alike on text inputs (browsers always show it for typed fields) while letting you reuse the class on buttons without a mouse-click ring. The ring uses `/40` alpha so it reads as a halo over any background. `readonly` keeps full contrast because the value is meant to be read and copied; `disabled` drops contrast because the value is irrelevant right now. The busy spinner is a background image so no extra DOM is needed and `aria-busy` tells assistive tech the field is updating.

## Variations

- **Sizes**: `.field-sm` with `px-2.5 py-1.5 text-sm` and `.field-lg` with `px-4 py-3 text-lg`; keep 16px minimum on mobile (`text-base sm:text-sm`) to avoid iOS zoom.
- **Leading icon or prefix** (`$`, `https://`): wrap in `relative`, put the adornment `absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500`, and give the input `pl-9`. For a prefix that is part of the value (currency), use `<span>` in a flex container with `rounded-l-md border-r-0` on the span and `rounded-l-none` on the input.
- **Native `:user-invalid`** instead of `aria-invalid` when you are not using JS: `user-invalid:border-red-500` only fires after the user has interacted, unlike `:invalid` which is red on page load.
- **Underline style** (minimal forms): swap `rounded-md border` for `rounded-none border-0 border-b-2 px-0 focus-visible:ring-0 focus-visible:border-blue-500`.

## Pitfalls

- `disabled` inputs are skipped by Tab and not submitted; `readonly` are focusable and submitted. Do not use `disabled` for "you cannot change this" data you still need to post.
- The floating label needs `placeholder=" "` (a space) and `placeholder-transparent`; an empty placeholder makes `:placeholder-shown` never match and the label never drops into the box.
- Floating labels break with browser autofill in some engines until the user interacts; add `[&:-webkit-autofill]:pt-5` styling or prefer labels-above for login forms.
- Do not remove `outline` without replacing it with a ring: `focus-visible:outline-none` must always sit next to `focus-visible:ring-*`.
- `transition-all` on the input animates `background-color` during autofill and can flash; transition only `border-color` and `box-shadow`.
- Gray-on-gray disabled text often fails contrast; keep it at `text-gray-500` on `bg-gray-50` or lighter (4.6:1), not `text-gray-400`.

## Related skills

- `web-form-layout`
- `web-form-validation`
- `web-form-password-fields`
- `web-ui-skeleton-and-loading`
- `web-a11y-keyboard-and-focus`
- `web-css-layers-and-organization`
