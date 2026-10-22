---
name: web-page-auth
description: 'Build login, sign up, forgot-password and reset-password pages in Tailwind v4: a centred card and a split-with-image variant, correct autocomplete attributes, an error banner wired to aria, and a "check your email" success state. Use whenever a user asks for a login page, sign in page, sign up page, registration form, password reset, "forgot password" or an auth screen.'
---

# Auth pages

Login, sign-up and reset are the one place where a centred card is right: there is a single task, nothing to read, and the user wants it in the middle of the screen. What makes these pages good is not the layout but the details: the right `autocomplete` tokens so password managers fill the fields, one `<h1>` that says which page this is, an error that is announced and sits above the fields, a success state for reset that tells the user what to do next, and `noindex` so Google never lists `/login`. Four pages share one shell; only the form body changes.

## Pattern

```html
<main id="main" class="flex min-h-dvh flex-col items-center justify-center bg-stone-50 px-4 py-12">
  <a href="/" class="mb-8 font-semibold">Ledgerline</a>

  <!-- Card: one column, fixed measure, no decoration -->
  <section aria-labelledby="auth-heading" class="w-full max-w-sm rounded-lg border border-stone-200 bg-white p-6 shadow-sm sm:p-8">
    <h1 id="auth-heading" class="text-2xl font-semibold tracking-tight">Sign in</h1>
    <p class="mt-1 text-sm text-stone-600">New here? <a href="/signup" class="font-medium underline underline-offset-4">Create an account</a></p>

    <!-- Error banner: present in the DOM, filled and shown on failure -->
    <div hidden role="alert" tabindex="-1" data-error class="mt-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"></div>

    <form action="/login" method="post" class="mt-6 space-y-5" novalidate data-auth-form>
      <div>
        <label for="email" class="block text-sm font-medium">Email</label>
        <input id="email" name="email" type="email" autocomplete="username" required inputmode="email" spellcheck="false" class="mt-1.5 w-full rounded-md border border-stone-300 px-3 py-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 aria-[invalid=true]:border-red-500">
      </div>
      <div>
        <div class="flex items-baseline justify-between">
          <label for="password" class="block text-sm font-medium">Password</label>
          <a href="/forgot" class="text-sm underline underline-offset-4">Forgot it?</a>
        </div>
        <input id="password" name="password" type="password" autocomplete="current-password" required class="mt-1.5 w-full rounded-md border border-stone-300 px-3 py-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900 aria-[invalid=true]:border-red-500">
      </div>
      <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="remember" class="size-4 rounded border-stone-300">Keep me signed in on this device</label>
      <button type="submit" class="w-full rounded-md bg-stone-900 px-4 py-2.5 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Sign in</button>
    </form>

    <div class="my-6 flex items-center gap-3 text-xs text-stone-500"><hr class="flex-1 border-stone-200"><span>or</span><hr class="flex-1 border-stone-200"></div>
    <a href="/auth/google" class="flex w-full items-center justify-center gap-2 rounded-md border border-stone-300 px-4 py-2.5 text-sm font-medium hover:bg-stone-50">Continue with Google</a>
  </section>

  <p class="mt-8 text-xs text-stone-500">By signing in you agree to the <a href="/terms" class="underline">terms</a> and <a href="/privacy" class="underline">privacy policy</a>.</p>
</main>
```

The other three form bodies, dropped into the same card:

```html
<!-- Sign up: name, email, new password with the rules in help text; no confirm field -->
<input id="name" name="name" autocomplete="name" required>
<input id="email" name="email" type="email" autocomplete="username" required>
<input id="password" name="password" type="password" autocomplete="new-password" required minlength="12" aria-describedby="pw-help">
<p id="pw-help" class="mt-1 text-sm text-stone-500">At least 12 characters. A sentence works well.</p>

<!-- Forgot: email only. The success state replaces the form and never confirms whether the address exists. -->
<form data-auth-form data-success="If there is an account for that address, a reset link is on its way. It works for 30 minutes.">
  <input id="email" name="email" type="email" autocomplete="username" required>
  <button type="submit">Email me a reset link</button>
</form>

<!-- Reset (from the emailed link): new password once, token hidden -->
<input type="hidden" name="token" value="...">
<input id="password" name="password" type="password" autocomplete="new-password" required minlength="12">
```

Submit with fetch, show the error above the fields, or swap in the success state:

```js
const form = document.querySelector('[data-auth-form]');
const error = document.querySelector('[data-error]');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const button = form.querySelector('button[type=submit]');
  button.disabled = true;
  try {
    const res = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
    if (res.ok) {
      if (form.dataset.success) form.replaceWith(Object.assign(document.createElement('p'), { role: 'status', tabIndex: -1, className: 'mt-6 text-sm', textContent: form.dataset.success })), document.querySelector('[role=status]').focus();
      else location.assign(new URLSearchParams(location.search).get('next') ?? '/app');
      return;
    }
    const { message = 'That email and password do not match.' } = await res.json().catch(() => ({}));
    error.textContent = message;
    error.hidden = false;
    error.focus();
    for (const input of form.querySelectorAll('input[type=email], input[type=password]')) input.setAttribute('aria-invalid', 'true');
  } catch {
    error.textContent = 'Could not reach the server. Check your connection and try again.';
    error.hidden = false;
    error.focus();
  } finally {
    button.disabled = false;
  }
});
```

Meta: `<meta name="robots" content="noindex">` on all four pages, `<title>Sign in · Ledgerline</title>`, no Open Graph needed. Validate the `next` parameter server-side to a same-origin path.

## Variations

- **Split with image**: `<main class="grid min-h-dvh lg:grid-cols-[0.9fr_1.1fr]">`, the card contents left-aligned in the first column (`max-w-sm` inside `px-8 py-12`), and an `<img class="hidden h-full w-full object-cover lg:block">` of the product, not a stock photo, in the second. The image column disappears below `lg`, so the first column must stand alone.
- **Magic link only**: drop the password field; the submit button says "Email me a sign-in link" and the success text replaces the form, same as forgot.
- **Two-factor step**: a second page with a single `<input inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}">` and "Use a backup code" link.
- **Show/hide password and a strength meter** on sign-up and reset come from `web-form-password-fields`; keep them off the login page.

## Pitfalls

- `autocomplete="email"` on the login email field stops many password managers from pairing it with the password; the token for the identifier is `username` even when it is an email.
- A "confirm password" field on sign-up doubles typing on phones and catches almost nothing; a show-password toggle catches more.
- Error text in red under the field without `role="alert"` is never announced; the banner above the form is, and moving focus to it puts the user where the fix starts.
- "No account with that email" on the forgot page leaks who has an account; the message is the same whether the address exists or not.
- `min-h-screen` leaves a scrollbar on iOS Safari because of the toolbars; `min-h-dvh` does not.
- Disabling the submit button until the form is valid hides the way to see the errors; keep it enabled and let `reportValidity()` explain.

## Related skills

- `web-form-password-fields`
- `web-form-validation`
- `web-form-submit-with-fetch`
- `web-form-input-states`
- `web-a11y-keyboard-and-focus`
- `web-seo-meta-tags`
