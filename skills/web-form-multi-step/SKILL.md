---
name: web-form-multi-step
description: Build a multi-step form (wizard) with Tailwind and vanilla JS: fieldsets as steps, a progress indicator with aria-current, Back/Next buttons that validate only the current step, one state object that survives navigation, a review step, and focus management. Use whenever a user asks for a "wizard", "step-by-step form", "onboarding flow", "checkout steps", or "split this long form into pages".
---

# Multi-step form

Keep every step inside one `<form>` and show one `<fieldset>` at a time. That gives you a single submit, native constraint validation per step (`fieldset.querySelectorAll` plus `checkValidity`), and no state to shuttle between pages. Hidden steps still submit, so the final payload is complete without any merging. Collect values into one object with `FormData` whenever a step is left, so a review step, a "save draft" to `sessionStorage`, or a summary sidebar reads from the same source. Move focus to the new step's heading on each change; without that, keyboard and screen-reader users are left on a button that no longer exists.

## Pattern

```html
<form id="wizard" class="mx-auto max-w-xl space-y-8 p-4" novalidate data-wizard>
  <!-- Progress: an ordered list, current step marked with aria-current -->
  <ol class="flex gap-2 text-sm" aria-label="Progress" data-progress>
    <li class="flex-1 border-t-4 border-blue-600 pt-2 font-medium text-blue-700 dark:text-blue-400" aria-current="step">1. Account</li>
    <li class="flex-1 border-t-4 border-gray-200 pt-2 text-gray-500 dark:border-gray-700">2. Profile</li>
    <li class="flex-1 border-t-4 border-gray-200 pt-2 text-gray-500 dark:border-gray-700">3. Review</li>
  </ol>
  <p class="sr-only" aria-live="polite" data-announce></p>

  <fieldset class="space-y-5" data-step>
    <legend class="text-lg font-semibold text-gray-900 dark:text-gray-100" tabindex="-1">Account</legend>
    <div class="space-y-1.5">
      <label for="email" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Email</label>
      <input id="email" name="email" type="email" required autocomplete="email" aria-describedby="email-error"
        class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base aria-invalid:border-red-500 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">
      <p id="email-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
    </div>
  </fieldset>

  <fieldset class="space-y-5" data-step hidden>
    <legend class="text-lg font-semibold text-gray-900 dark:text-gray-100" tabindex="-1">Profile</legend>
    <div class="space-y-1.5">
      <label for="name" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Display name</label>
      <input id="name" name="name" type="text" required minlength="2" aria-describedby="name-error"
        class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base aria-invalid:border-red-500 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none">
      <p id="name-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
    </div>
  </fieldset>

  <fieldset class="space-y-5" data-step hidden>
    <legend class="text-lg font-semibold text-gray-900 dark:text-gray-100" tabindex="-1">Review</legend>
    <dl class="divide-y divide-gray-200 rounded-md border border-gray-200 text-sm dark:divide-gray-700 dark:border-gray-700" data-review></dl>
  </fieldset>

  <div class="flex justify-between gap-3 border-t border-gray-200 pt-6 dark:border-gray-700">
    <button type="button" data-back class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:invisible dark:text-gray-300">Back</button>
    <button type="button" data-next class="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">Next</button>
    <button type="submit" data-submit hidden class="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">Create account</button>
  </div>
</form>
```

```js
function initWizard(form) {
  const steps = [...form.querySelectorAll('[data-step]')];
  const progress = [...form.querySelectorAll('[data-progress] li')];
  const announce = form.querySelector('[data-announce]');
  const back = form.querySelector('[data-back]');
  const next = form.querySelector('[data-next]');
  const submit = form.querySelector('[data-submit]');
  const review = form.querySelector('[data-review]');
  const state = {};                                   // single source of truth for all entered values
  let current = 0;

  function collect() {
    for (const [k, v] of new FormData(form)) if (!(v instanceof File)) state[k] = v;
    try { sessionStorage.setItem('wizard', JSON.stringify(state)); } catch { /* storage unavailable */ }
  }

  function validateStep(i) {
    let firstBad = null;
    for (const field of steps[i].querySelectorAll('input, select, textarea')) {
      const ok = field.checkValidity();
      field.toggleAttribute('aria-invalid', !ok);
      const slot = document.getElementById(`${field.id}-error`);
      if (slot) slot.textContent = ok ? '' : field.validationMessage;
      if (!ok && !firstBad) firstBad = field;
    }
    firstBad?.focus();
    return !firstBad;
  }

  function renderReview() {
    review.replaceChildren(...Object.entries(state).flatMap(([k, v]) => {
      const dt = Object.assign(document.createElement('dt'), { textContent: k, className: 'px-3 pt-2 font-medium capitalize text-gray-600 dark:text-gray-400' });
      const dd = Object.assign(document.createElement('dd'), { textContent: v, className: 'px-3 pb-2 text-gray-900 dark:text-gray-100' });
      return [dt, dd];
    }));
  }

  function show(i) {
    current = i;
    steps.forEach((s, j) => { s.hidden = j !== i; });
    progress.forEach((li, j) => {
      li.toggleAttribute('aria-current', j === i);
      li.classList.toggle('border-blue-600', j <= i);
      li.classList.toggle('border-gray-200', j > i);
    });
    back.disabled = i === 0;
    next.hidden = i === steps.length - 1;
    submit.hidden = i !== steps.length - 1;
    if (i === steps.length - 1) renderReview();
    announce.textContent = `Step ${i + 1} of ${steps.length}: ${steps[i].querySelector('legend').textContent}`;
    steps[i].querySelector('legend').focus();
  }

  next.addEventListener('click', () => { if (validateStep(current)) { collect(); show(current + 1); } });
  back.addEventListener('click', () => { collect(); show(current - 1); });
  form.addEventListener('submit', (e) => { if (!validateStep(current)) e.preventDefault(); else collect(); });
  form.addEventListener('keydown', (e) => {                 // Enter in a field advances instead of submitting early
    if (e.key === 'Enter' && e.target.matches('input') && !next.hidden) { e.preventDefault(); next.click(); }
  });

  try { Object.assign(state, JSON.parse(sessionStorage.getItem('wizard') || '{}')); } catch { /* ignore bad JSON */ }
  for (const [k, v] of Object.entries(state)) if (form.elements[k]) form.elements[k].value = v;
  show(0);
}

document.querySelectorAll('[data-wizard]').forEach(initWizard);
```

Why these choices: `fieldset[hidden]` elements are not focusable and are skipped by validation and tab order, yet their values still submit. `checkValidity()` per field (not `form.checkValidity()`) scopes errors to the visible step. `legend` with `tabindex="-1"` is a focus target that announces the step name; the live region adds the count. `disabled:invisible` on Back keeps the Next button in the same place on step one.

## Variations

- **Clickable progress** to revisit completed steps: render `<button type="button">` inside each `<li>`, enable only for indexes below `current`, and call `show(j)` after `collect()`.
- **URL per step** (`#step-2`) so refresh and the browser Back button work: call `history.pushState` in `show()` and listen for `popstate`; see `web-js-router-and-urls`.
- **Conditional steps** (skip "Billing" when "same as shipping" is checked): give each fieldset a `data-skip-if="field=value"` attribute and have `show()` jump over any fieldset whose condition matches `state`.
- **Animated transition** between steps: add `motion-safe:animate-[fade-in_200ms_ease-out]` to the fieldset on show; never animate `height`, let the page reflow.

## Pitfalls

- Pressing Enter in a text field submits the whole form from step one; intercept it (done above) or users post half-filled forms.
- `display:none` steps are still in `FormData`, which is what you want, but `required` fields in them are also *not* validated by the browser on submit (hidden fields are barred from constraint validation). Validate each step as you leave it.
- Do not clone fields or build separate forms per step; you will fight state merging and lose autocomplete.
- A progress bar that is only color (blue vs gray) fails for color-blind users; the numbers and `aria-current` carry the meaning.
- Clearing `sessionStorage` after a successful submit matters: otherwise the next visitor on a shared device sees the previous email.
- Files (`<input type="file">`) cannot be stored in `sessionStorage` or restored into an input; keep them in the live form only and show their names in the review step from `form.elements`.

## Related skills

- `web-form-layout`
- `web-form-validation`
- `web-form-submit-with-fetch`
- `web-js-state-and-render`
- `web-js-storage`
- `web-a11y-keyboard-and-focus`
