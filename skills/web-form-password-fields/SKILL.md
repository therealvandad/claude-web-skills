---
name: web-form-password-fields
description: Build password fields for login, signup and change-password forms with Tailwind and vanilla JS: a show/hide toggle, a live strength meter with requirement checklist, confirm-password matching via setCustomValidity, and the right autocomplete tokens so password managers work. Use whenever a user asks for a "password input", "eye icon to reveal password", "password strength bar", "confirm password", or "login/register form".
---

# Password fields

Three things make a password field good: it never fights the password manager (`autocomplete="current-password"` on login, `new-password` on signup and change forms, with a `username` field nearby even if hidden), it lets people see what they typed (a real `<button>` that flips `type` between `password` and `text`, with `aria-pressed` so its state is announced), and it tells them how to succeed before they fail (a strength meter plus a checklist that ticks as rules are met, rather than a red error after submit). Strength is estimated from length and character variety; length counts most, because "correct horse battery staple" beats "P@ss1".

## Pattern

```html
<form class="mx-auto max-w-md space-y-5 p-4" novalidate data-password-form>
  <!-- Username/email lets password managers pair the credential, even on change-password pages -->
  <div class="space-y-1.5">
    <label for="email" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Email</label>
    <input id="email" name="email" type="email" required autocomplete="username"
      class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 dark:bg-gray-900">
  </div>

  <div class="space-y-1.5">
    <label for="password" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Password</label>
    <div class="relative">
      <input id="password" name="password" type="password" required minlength="12" autocomplete="new-password"
        aria-describedby="password-rules password-error" spellcheck="false" autocapitalize="off"
        class="block w-full rounded-md border border-gray-300 py-2 pr-12 pl-3 text-base aria-invalid:border-red-500
               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 dark:bg-gray-900">
      <button type="button" data-toggle aria-controls="password" aria-pressed="false" aria-label="Show password"
        class="absolute inset-y-0 right-0 my-1 mr-1 rounded px-3 text-sm font-medium text-gray-600 hover:bg-gray-100
               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-300 dark:hover:bg-gray-800">Show</button>
    </div>

    <!-- Strength meter: a native <meter> so the value is exposed to assistive tech -->
    <div class="flex items-center gap-3">
      <meter id="password-meter" min="0" max="4" low="2" high="3" optimum="4" value="0" aria-label="Password strength"
        class="h-2 flex-1 [&::-webkit-meter-bar]:rounded-full [&::-webkit-meter-bar]:bg-gray-200
               [&::-webkit-meter-optimum-value]:bg-green-600 [&::-webkit-meter-suboptimum-value]:bg-yellow-500 [&::-webkit-meter-even-less-good-value]:bg-red-500
               dark:[&::-webkit-meter-bar]:bg-gray-700"></meter>
      <span class="w-16 text-xs text-gray-600 dark:text-gray-400" data-strength-label aria-live="polite"></span>
    </div>

    <ul id="password-rules" class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
      <li data-rule="length" class="flex items-center gap-2 data-[ok]:text-green-700 dark:data-[ok]:text-green-400"><span aria-hidden="true" class="w-4">•</span>At least 12 characters</li>
      <li data-rule="mixed" class="flex items-center gap-2 data-[ok]:text-green-700 dark:data-[ok]:text-green-400"><span aria-hidden="true" class="w-4">•</span>Upper and lower case letters</li>
      <li data-rule="number" class="flex items-center gap-2 data-[ok]:text-green-700 dark:data-[ok]:text-green-400"><span aria-hidden="true" class="w-4">•</span>A number or symbol</li>
    </ul>
    <p id="password-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>

  <div class="space-y-1.5">
    <label for="confirm" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Confirm password</label>
    <input id="confirm" name="confirm" type="password" required autocomplete="new-password" aria-describedby="confirm-error"
      class="block w-full rounded-md border border-gray-300 px-3 py-2 text-base aria-invalid:border-red-500
             focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:border-gray-600 dark:bg-gray-900">
    <p id="confirm-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  </div>

  <button type="submit" class="w-full rounded-md bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">Create account</button>
</form>
```

```js
const RULES = {
  length: (v) => v.length >= 12,
  mixed:  (v) => /[a-z]/.test(v) && /[A-Z]/.test(v),
  number: (v) => /[\d\W_]/.test(v),
};
const LABELS = ['', 'Weak', 'Fair', 'Good', 'Strong'];

function score(value) {
  if (!value) return 0;
  let s = Object.values(RULES).filter((test) => test(value)).length;   // 0–3 from the rules
  if (value.length >= 16) s += 1;                                      // length bonus
  if (/^(.)\1+$/.test(value) || /^(0123|1234|abcd|qwer|pass)/i.test(value)) s = Math.min(s, 1);
  return Math.min(s, 4);
}

function initPasswordForm(form) {
  const password = form.querySelector('#password');
  const confirm = form.querySelector('#confirm');
  const meter = form.querySelector('#password-meter');
  const strengthLabel = form.querySelector('[data-strength-label]');

  // Show/hide toggles: work for any input the button's aria-controls points at
  form.querySelectorAll('[data-toggle]').forEach((btn) => {
    const input = document.getElementById(btn.getAttribute('aria-controls'));
    btn.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.setAttribute('aria-pressed', String(show));
      btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
      btn.textContent = show ? 'Hide' : 'Show';
      input.focus({ preventScroll: true });
    });
  });

  function updateStrength() {
    const v = password.value;
    for (const [name, test] of Object.entries(RULES)) {
      form.querySelector(`[data-rule="${name}"]`).toggleAttribute('data-ok', test(v));
    }
    const s = score(v);
    meter.value = s;
    strengthLabel.textContent = LABELS[s];
    password.setCustomValidity(v && !Object.values(RULES).every((t) => t(v)) ? 'Password does not meet all the requirements.' : '');
  }

  function updateMatch() {
    const mismatch = confirm.value !== '' && confirm.value !== password.value;
    confirm.setCustomValidity(mismatch ? 'Passwords do not match.' : '');
    confirm.toggleAttribute('aria-invalid', mismatch);
    document.getElementById('confirm-error').textContent = mismatch ? 'Passwords do not match.' : '';
  }

  password.addEventListener('input', () => { updateStrength(); updateMatch(); });
  confirm.addEventListener('input', updateMatch);
  form.addEventListener('submit', (e) => {
    updateStrength(); updateMatch();
    if (!form.checkValidity()) {
      e.preventDefault();
      password.toggleAttribute('aria-invalid', !password.validity.valid);
      document.getElementById('password-error').textContent = password.validationMessage;
      form.querySelector(':invalid')?.focus();
    }
  });
  form.addEventListener('submit', () => { if (password.type === 'text') password.type = 'password'; }); // never post from a visible field
}

document.querySelectorAll('[data-password-form]').forEach(initPasswordForm);
```

Why these choices: `<meter>` carries min/max/value semantics natively, so the strength is a real value to assistive tech, with the text label as a polite announcement. `setCustomValidity` makes the checklist and the match rule part of constraint validation, so `checkValidity()` and `web-form-validation` see them without extra code. The toggle is a `<button type="button">` (never a link or icon span) with `aria-pressed`, and focus returns to the input so the user keeps typing. `spellcheck="false"` and `autocapitalize="off"` stop mobile keyboards mangling the value when it is revealed.

## Variations

- **Login form**: one field with `autocomplete="current-password"`, no meter, no checklist, keep the show/hide toggle and add a "Forgot password?" link next to the label (`flex justify-between`).
- **Change password**: three fields; the current one uses `autocomplete="current-password"`, the new and confirm fields use `new-password`; also reject a new password equal to the current one via `setCustomValidity`.
- **Icon toggle**: replace the text with an inline eye / eye-off SVG pair and swap with `hidden` + `[aria-pressed=true]:` variants; keep `aria-label` since the icon has no text.
- **Caps Lock warning**: on `keyup`, if `e.getModifierState('CapsLock')`, show a small `role="status"` line "Caps Lock is on" under the field.

## Pitfalls

- `maxlength` under 64 or banning paste blocks password managers and long passphrases; allow up to at least 64 characters and never intercept `paste`.
- Forbidding specific characters ("no spaces or symbols") is a sign the server does not hash correctly; hash with bcrypt/argon2 and accept anything.
- Strength meters that require exactly one uppercase, one digit and one symbol push people to "Password1!"; weight length, show the checklist as guidance, and let a long simple passphrase pass.
- `type="text"` while revealed means the browser may save the value in form history on some engines; flip it back to `password` before submit (done above).
- Confirm field errors must re-run when the *first* field changes, or fixing the original password leaves a stale mismatch message.
- Do not autofocus the password field on page load; it steals focus from the heading and breaks screen-reader orientation. Autofocus the username at most.

## Related skills

- `web-form-validation`
- `web-form-input-states`
- `web-form-layout`
- `web-form-submit-with-fetch`
- `web-ui-buttons`
- `web-a11y-aria-patterns`
