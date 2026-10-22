---
name: web-ui-modal-dialog
description: 'Build an accessible modal with the native dialog element: open/close buttons, backdrop, Escape and click-outside close, focus restore, body scroll lock, Tailwind styling. Use whenever a user asks for a modal, popup, dialog, overlay, lightbox, confirm box, "are you sure" prompt, or a form that opens on top of the page.'
---

# Modal dialog with `<dialog>`

The native `<dialog>` element gives you a top-layer overlay, `::backdrop`, Escape-to-close, focus trapping (inert page behind it) and the `dialog` role for free when opened with `showModal()`. Hand-rolled modals with `position: fixed` and a focus-trap script re-implement all of that badly. The only things left to add are click-outside closing, scroll lock, focus restore, and styling.

## Pattern

```html
<button type="button" data-open="dlg-signup"
  class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
  Sign up
</button>

<dialog id="dlg-signup" aria-labelledby="dlg-signup-title"
  class="m-auto w-[calc(100%-2rem)] max-w-md rounded-2xl bg-white p-0 text-gray-900 shadow-xl
         backdrop:bg-gray-900/60 backdrop:backdrop-blur-sm
         open:motion-safe:animate-[dlg-in_.2s_ease-out] dark:bg-gray-900 dark:text-gray-100">
  <form method="dialog" class="p-6 sm:p-8">
    <div class="flex items-start justify-between gap-4">
      <h2 id="dlg-signup-title" class="text-lg font-semibold">Create your account</h2>
      <button type="submit" value="cancel" aria-label="Close"
        class="-m-2 rounded-full p-2 text-gray-500 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:hover:bg-gray-800">
        <svg class="size-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/></svg>
      </button>
    </div>
    <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">We only need an email to get started.</p>

    <label class="mt-5 block text-sm font-medium" for="dlg-email">Email</label>
    <input id="dlg-email" name="email" type="email" required autocomplete="email"
      class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-gray-700 dark:bg-gray-800">

    <div class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
      <button type="submit" value="cancel" formnovalidate
        class="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:text-gray-300 dark:hover:bg-gray-800">Cancel</button>
      <button type="submit" value="confirm"
        class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Continue</button>
    </div>
  </form>
</dialog>
```

```css
@keyframes dlg-in { from { opacity: 0; transform: translateY(8px) scale(.98) } }
/* lock page scroll while any modal is open */
body:has(dialog[open]:modal) { overflow: hidden; }
```

```js
function setupDialogs() {
  // Openers: any element with data-open="<dialog id>"
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-open]');
    if (!opener) return;
    const dlg = document.getElementById(opener.dataset.open);
    if (!(dlg instanceof HTMLDialogElement)) return;
    dlg._opener = opener; // remembered so focus can return on close
    dlg.showModal();
  });

  document.querySelectorAll('dialog').forEach((dlg) => {
    // Click on the backdrop (outside the dialog's box) closes it
    dlg.addEventListener('click', (e) => {
      const r = dlg.getBoundingClientRect();
      const inside = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
      if (!inside) dlg.close('cancel');
    });
    // Restore focus to the opener and report the result
    dlg.addEventListener('close', () => {
      dlg._opener?.focus();
      if (dlg.returnValue === 'confirm') dlg.dispatchEvent(new CustomEvent('dialog:confirm', { bubbles: true }));
    });
  });
}
setupDialogs();

// Example consumer
document.getElementById('dlg-signup').addEventListener('dialog:confirm', (e) => {
  const email = new FormData(e.target.querySelector('form')).get('email');
  console.log('signup', email);
});
```

Why this shape: `method="dialog"` makes every submit button close the dialog and set `returnValue`, so Cancel and Close need no JS. `formnovalidate` on Cancel lets users leave without filling required fields. `m-auto` centers because the top layer gives the dialog `position: fixed` with `inset: 0`; `p-0` resets the UA padding so the inner form controls spacing.

## Variations

- **Confirm dialog**: reuse the pattern without inputs; listen for `close` and check `dlg.returnValue === 'confirm'`. For destructive actions make the confirm button red (`bg-red-600`) and put initial focus on Cancel with `autofocus`.
- **Full-screen sheet on mobile**: `class="m-0 h-dvh max-h-none w-full max-w-none rounded-none sm:m-auto sm:h-auto sm:max-w-md sm:rounded-2xl"`.
- **Bottom sheet**: `class="mb-0 mt-auto w-full max-w-none rounded-t-2xl sm:m-auto sm:max-w-md sm:rounded-2xl"` with a slide-up keyframe.
- **Non-modal (`dlg.show()`)**: no backdrop, no inert page, no Escape. Use for persistent side panels; remember to add your own close button and consider `web-ui-tooltip-and-popover` instead.
- **Closing animation**: add `transition-discrete` + `starting:` styles (Tailwind v4 supports `@starting-style` via `starting:`), e.g. `class="opacity-0 open:opacity-100 starting:open:opacity-0 transition-[opacity,overlay,display] duration-200 transition-discrete"`.

## Pitfalls

- Always open with `showModal()`, never `show()` or the `open` attribute, if you want a modal: only `showModal()` puts it in the top layer, traps focus and makes the rest of the page inert.
- `::backdrop` does not inherit CSS custom properties from `:root` in older browsers; use plain color values in `backdrop:` utilities.
- The backdrop-click check uses the dialog's bounding rect, so it keeps working with `p-0` and edge-to-edge children. It only becomes moot in the full-screen variant, where there is no outside to click; keep the visible Close button there.
- Put a real heading inside and point `aria-labelledby` at it; screen readers announce the title when the dialog opens.
- `autofocus` on an input inside the dialog controls initial focus; without it, the browser focuses the first focusable element, which may be the close button. For long content with no controls, give the content container `tabindex="-1"` and `autofocus`.
- Animating `display` requires `transition-discrete` (v4) or `@starting-style`; a plain `transition-opacity` on open will not run because the element goes from `display:none`.
- Nested dialogs work (each `showModal()` stacks in the top layer), but Escape closes only the topmost; do not rely on this for complex flows.

## Related skills

- `web-a11y-keyboard-and-focus`
- `web-ui-buttons`
- `web-form-validation`
- `web-ui-tooltip-and-popover`
- `web-motion-transitions`
