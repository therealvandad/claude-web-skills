---
name: web-form-validation
description: 'Add inline, accessible validation to HTML forms using the browser''s constraint validation API plus a vanilla JS layer: per-field error messages under the input, aria-invalid and aria-describedby wiring, validate-on-blur then re-validate-on-input, focus the first bad field on submit. Use whenever a user says "validate this form", "show errors", "required fields", "check the email", or "the form submits empty".'
---

# Form validation

Let the browser do the checking and do the *showing* yourself. `required`, `type="email"`, `minlength`, `pattern` and `min`/`max` give you free, localized, well-tested rules through `input.validity` and `input.validationMessage`; the native bubbles, however, are unstyleable, show one error at a time and vanish on scroll. So keep the attributes, add `novalidate` to the form, and render each field's message into the error slot that `web-form-layout` already reserved. Timing matters as much as copy: validate on `blur` (not while the user is still typing), then once a field has been marked invalid re-check on every `input` so the error clears the moment it is fixed.

## Pattern

```html
<form id="signup" class="mx-auto max-w-md space-y-5 p-4" novalidate>
  <div class="space-y-1.5">
    <label for="email" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Email</label>
    <input id="email" name="email" type="email" required autocomplete="email" inputmode="email"
      aria-describedby="email-error"
      data-msg-value-missing="Enter your email address."
      data-msg-type-mismatch="That does not look like an email address."
      class="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 shadow-sm
             focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
             aria-invalid:border-red-500 aria-invalid:ring-1 aria-invalid:ring-red-500
             dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100">
    <p id="email-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>

  <div class="space-y-1.5">
    <label for="username" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Username</label>
    <input id="username" name="username" type="text" required minlength="3" maxlength="20" pattern="[a-z0-9_]+"
      autocomplete="username" aria-describedby="username-help username-error"
      data-msg-too-short="Use at least 3 characters."
      data-msg-pattern-mismatch="Lowercase letters, numbers and underscores only."
      class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base ... aria-invalid:border-red-500">
    <p id="username-help" class="text-sm text-gray-500 dark:text-gray-400">3 to 20 characters, no spaces.</p>
    <p id="username-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>

  <div class="space-y-1.5">
    <label for="age" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Age</label>
    <input id="age" name="age" type="number" min="18" max="120" inputmode="numeric" aria-describedby="age-error"
      data-msg-range-underflow="You must be 18 or older."
      class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base ... aria-invalid:border-red-500">
    <p id="age-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>

  <p id="form-status" class="text-sm text-red-600" role="alert" tabindex="-1"></p>
  <button type="submit" class="w-full rounded-md bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">Create account</button>
</form>
```

```js
// validate.js — attaches to any <form novalidate data-validate> or a passed form element
const VALIDITY_KEYS = ['valueMissing', 'typeMismatch', 'patternMismatch', 'tooShort', 'tooLong',
  'rangeUnderflow', 'rangeOverflow', 'stepMismatch', 'badInput'];

function messageFor(field) {
  if (field.validity.valid) return '';
  const key = VALIDITY_KEYS.find((k) => field.validity[k]);          // first failing constraint
  const custom = key && field.dataset[`msg${key[0].toUpperCase()}${key.slice(1)}`];
  return custom || field.validationMessage;                           // fall back to the browser's text
}

function showError(field, message) {
  const slot = document.getElementById(`${field.id}-error`);
  if (slot) slot.textContent = message;
  if (message) field.setAttribute('aria-invalid', 'true');
  else field.removeAttribute('aria-invalid');
}

function validateField(field) {
  field.setCustomValidity('');                                        // clear any previous custom rule
  field.dispatchEvent(new CustomEvent('validate', { bubbles: true })); // hook for cross-field rules
  const message = messageFor(field);
  showError(field, message);
  return !message;
}

export function initValidation(form) {
  const fields = () => [...form.elements].filter((el) => el.willValidate && el.id);

  form.addEventListener('focusout', (e) => {
    if (fields().includes(e.target)) validateField(e.target);
  });
  form.addEventListener('input', (e) => {
    if (e.target.getAttribute('aria-invalid') === 'true') validateField(e.target); // live re-check only once flagged
  });
  form.addEventListener('submit', (e) => {
    const invalid = fields().filter((f) => !validateField(f));
    const status = form.querySelector('#form-status');
    if (invalid.length === 0) { if (status) status.textContent = ''; return; }
    e.preventDefault();
    if (status) status.textContent = `Please fix ${invalid.length} ${invalid.length === 1 ? 'field' : 'fields'} below.`;
    invalid[0].focus({ preventScroll: false });
  });
}

document.querySelectorAll('form[novalidate]').forEach(initValidation);
```

Why these choices: `focusout` bubbles (`blur` does not), so one listener on the form covers every field. `validity` flags map to `data-msg-*` attributes so copy lives in the HTML next to the rule, not in a JS lookup table. The `validate` custom event lets other code (a password-confirm check, an async username lookup) call `field.setCustomValidity('...')` before the message is read, without editing this file. `role="alert"` on the summary line announces the count once; the per-field `aria-live="polite"` slots announce individual fixes without shouting.

## Variations

- **Cross-field rule** (confirm password, end date after start date): `form.addEventListener('validate', (e) => { if (e.target.id === 'confirm' && e.target.value !== form.password.value) e.target.setCustomValidity('Passwords do not match.'); })`. Also re-validate the dependent field when the source changes.
- **Async check** (username taken): on `focusout`, `fetch` the API, then `setCustomValidity` and call `showError`; keep `aria-busy="true"` on the field while waiting and never block typing.
- **Success state**: in `showError`, toggle `data-valid` on the wrapper and style with `has-[[data-valid]]:` or add a green check icon via `aria-invalid:hidden` / `[&[aria-invalid=false]]:` classes. Only show it for fields that were previously invalid.
- **Error summary list** for long forms: instead of a count, render `<ul>` of `<a href="#field-id">` links in the `role="alert"` block so keyboard users can jump to each problem.

## Pitfalls

- Forgetting `novalidate` means the native bubble fires first and your `submit` handler never runs for invalid forms. Forgetting it in the other direction (no JS loaded) means no validation at all; if the script is optional, add the attribute from JS: `form.noValidate = true`.
- `aria-invalid="true"` must be removed, not set to `"false"`, once the field is fixed, or Tailwind's `aria-invalid:` variant stays on (it matches the attribute being present and `true`, but screen readers vary on `"false"`).
- Validating on every keystroke from the start makes users read "Enter your email" while they are typing the first letter. Blur first, live only after the field is flagged.
- `type="email"` accepts `a@b`; if you need a TLD, add `pattern="[^@\s]+@[^@\s]+\.[^@\s]+"` and a matching `data-msg-pattern-mismatch`. Do not try to validate email with a stricter regex; you will reject real addresses.
- `setCustomValidity` sticks: clear it with an empty string before re-checking native constraints, or a fixed field stays invalid forever.
- Never rely on this alone: the server must validate again. Client-side rules are for the user's benefit, not security.

## Related skills

- `web-form-layout`
- `web-form-input-states`
- `web-form-password-fields`
- `web-form-submit-with-fetch`
- `web-form-multi-step`
- `web-a11y-aria-patterns`
