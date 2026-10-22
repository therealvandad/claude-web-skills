---
name: web-form-submit-with-fetch
description: Submit any HTML form with fetch instead of a page reload: FormData, a loading button state, accessible success and error messages, server field errors mapped to inline slots, a honeypot and timing check against bots, and double-submit protection. Use whenever a user says "submit without refreshing", "ajax form", "send to my API", "thank-you message", or "stop spam submissions".
---

# Submit a form with fetch

Keep `action` and `method` on the form so it works before the script loads, then intercept `submit`, build `FormData(form)` (which already includes files and the clicked submit button when passed as the second argument), and `fetch` it. Everything after that is about honesty with the user: disable the button and say "Sending…" so a slow network does not trigger a second click, show a success message in place of the form or a specific error above it, and put server-side field errors into the same per-field slots client validation uses. Bots are handled quietly: a hidden honeypot field that humans never see and a timestamp that rejects submissions filled in under two seconds.

## Pattern

```html
<form id="contact" action="/api/contact" method="post" class="mx-auto max-w-md space-y-5 p-4" novalidate data-fetch-form>
  <!-- Honeypot: hidden from humans, left in the DOM for bots. Not display:none, which some bots detect. -->
  <div class="absolute -left-[9999px] top-auto h-px w-px overflow-hidden" aria-hidden="true">
    <label for="website">Leave this field empty</label>
    <input id="website" name="website" type="text" tabindex="-1" autocomplete="off">
  </div>
  <input type="hidden" name="started_at" data-started>

  <div class="space-y-1.5">
    <label for="email" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Email</label>
    <input id="email" name="email" type="email" required autocomplete="email" aria-describedby="email-error"
      class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base aria-invalid:border-red-500
             focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 dark:bg-gray-900">
    <p id="email-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>
  <div class="space-y-1.5">
    <label for="message" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Message</label>
    <textarea id="message" name="message" rows="4" required minlength="10" aria-describedby="message-error"
      class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base aria-invalid:border-red-500
             focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 dark:bg-gray-900"></textarea>
    <p id="message-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>

  <!-- One status region for form-level success/error. role=status is polite, role=alert is assertive. -->
  <p data-status tabindex="-1" class="hidden rounded-md px-3 py-2 text-sm
     data-[kind=error]:block data-[kind=error]:bg-red-50 data-[kind=error]:text-red-800
     data-[kind=success]:block data-[kind=success]:bg-green-50 data-[kind=success]:text-green-800"></p>

  <button type="submit" class="inline-flex w-full items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-2 font-semibold text-white
    hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
    disabled:cursor-wait disabled:opacity-70">
    <svg class="hidden size-4 animate-spin motion-reduce:animate-none group-aria-busy:block" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" class="opacity-25"/>
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
    </svg>
    <span data-label>Send message</span>
  </button>
</form>
```

```js
function initFetchForm(form) {
  const button = form.querySelector('button[type=submit]');
  const label = button.querySelector('[data-label]');
  const status = form.querySelector('[data-status]');
  const idleText = label.textContent;
  form.querySelector('[data-started]').value = String(Date.now());

  function setStatus(kind, text) {
    status.dataset.kind = kind;
    status.setAttribute('role', kind === 'error' ? 'alert' : 'status');
    status.textContent = text;
    status.focus();
  }
  function setFieldErrors(errors = {}) {
    for (const field of form.querySelectorAll('input, textarea, select')) {
      const slot = document.getElementById(`${field.id}-error`);
      const msg = errors[field.name];
      if (slot) slot.textContent = msg || '';
      field.toggleAttribute('aria-invalid', Boolean(msg));
    }
    const first = form.querySelector('[aria-invalid]');
    first?.focus();
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (form.classList.contains('is-submitting')) return;             // double-submit guard
    if (!form.checkValidity()) { form.reportValidity(); return; }      // or use web-form-validation's handler
    if (form.website.value) { setStatus('success', 'Thanks!'); return; } // honeypot tripped: pretend it worked
    if (Date.now() - Number(form.started_at.value) < 2000) { setStatus('error', 'Please take a moment and try again.'); return; }

    form.classList.add('is-submitting');
    button.disabled = true;
    button.setAttribute('aria-busy', 'true');
    label.textContent = 'Sending…';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);

    try {
      const res = await fetch(form.action, {
        method: form.method,
        body: new FormData(form, e.submitter),
        headers: { Accept: 'application/json' },
        signal: controller.signal,
      });
      const data = res.headers.get('content-type')?.includes('json') ? await res.json() : {};
      if (res.status === 422 || res.status === 400) { setFieldErrors(data.errors); setStatus('error', data.message || 'Please check the highlighted fields.'); return; }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setFieldErrors({});
      form.reset();
      form.querySelector('[data-started]').value = String(Date.now());
      setStatus('success', data.message || 'Thanks, your message was sent.');
    } catch (err) {
      setStatus('error', err.name === 'AbortError' ? 'The request timed out. Please try again.' : 'Something went wrong. Please try again.');
    } finally {
      clearTimeout(timeout);
      form.classList.remove('is-submitting');
      button.disabled = false;
      button.removeAttribute('aria-busy');
      label.textContent = idleText;
    }
  });
}

document.querySelectorAll('[data-fetch-form]').forEach(initFetchForm);
```

Why these choices: `new FormData(form, e.submitter)` posts exactly what a native submit would, including the clicked button's name/value and files, with the right multipart encoding and no manual `Content-Type` header (setting one breaks the boundary). The status element gets its `role` at message time: errors interrupt (`alert`), success waits its turn (`status`); focusing it also moves sighted keyboard users to it. The honeypot is moved off-screen rather than `display:none` because many bots skip hidden fields but fill off-screen ones, and `aria-hidden` plus `tabindex="-1"` keeps humans out. Fake success for bots gives them nothing to learn from. The `is-submitting` class is the guard, not `disabled`, because some browsers fire a second submit before the disabled state applies.

## Variations

- **Replace the form with a thank-you card**: on success, `form.replaceWith(successCard)` where the card has `tabindex="-1"` and is focused; keep a "Send another" button that re-renders.
- **JSON body instead of FormData** when the API expects it: `body: JSON.stringify(Object.fromEntries(new FormData(form)))` with `'Content-Type': 'application/json'`; drop this for file fields.
- **Optimistic UI** for low-stakes actions (newsletter): show success immediately, then revert and show the error only if the fetch fails.
- **Redirect after success** (a login form): on `res.ok`, `location.assign(data.redirect || form.dataset.redirect)` instead of showing a message.

## Pitfalls

- Setting `Content-Type: multipart/form-data` manually omits the boundary and the server receives nothing; let `fetch` set it from `FormData`.
- `disabled` on the button before the browser reads `e.submitter` is fine, but `disabled` fields are excluded from `FormData`; never disable inputs during submit, use `readonly` or an overlay.
- Showing "Something went wrong" for a 422 hides the field errors the server took the trouble to send; branch on status before the generic catch.
- A `role="alert"` element that is always in the DOM with changing text works; creating a new alert element on each error often is not announced. Reuse one node.
- Honeypots must not have `autocomplete` enabled or `name="email"`-style names; browsers autofill them and real users get silently dropped. Use a nonsense name and `autocomplete="off"`.
- Reset the `started_at` timestamp after success, or a second legitimate submission a minute later is fine but a quick retry after a network error is rejected as a bot.

## Related skills

- `web-form-validation`
- `web-form-layout`
- `web-form-file-upload`
- `web-js-fetch-and-apis`
- `web-ui-toast-notifications`
- `web-design-empty-and-error-states`
