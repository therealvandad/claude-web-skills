---
name: web-a11y-aria-patterns
description: 'Add ARIA correctly to custom widgets: when it is needed, the roles and states that matter (aria-expanded, aria-controls, aria-current, aria-live, aria-label vs aria-labelledby, aria-hidden), and how not to break native semantics. Use when a user asks "what aria do I need", "add aria labels", "screen reader announces wrong thing", or builds a toggle, menu, tab, or live status.'
---

# ARIA patterns

ARIA only changes what assistive technology is told; it adds no keyboard behaviour, no focus, no
styling. The first rule of ARIA is to not use it when a native element already does the job
(`<button>`, `<a href>`, `<details>`, `<dialog>`, `<input type=checkbox>`). The second rule is that
wrong ARIA is worse than none: a `role="button"` with no keydown handler, or `aria-hidden` on a
focusable element, actively lies to the user. Use ARIA for three things: naming, state, and live
announcements. Everything else is a custom widget you should think twice about.

## Pattern

The disclosure toggle is the smallest complete pattern, and it covers the attributes you will reuse
in menus, accordions and mobile navs.

```html
<nav aria-label="Main">
  <button type="button"
          id="menu-toggle"
          aria-expanded="false"
          aria-controls="menu"
          class="rounded-md p-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
    <svg aria-hidden="true" class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M4 6h16M4 12h16M4 18h16"/>
    </svg>
    <span class="sr-only">Menu</span>
  </button>

  <ul id="menu" hidden class="mt-2 flex flex-col gap-2">
    <li><a href="/docs">Docs</a></li>
    <li><a href="/pricing" aria-current="page">Pricing</a></li>
  </ul>
</nav>

<p id="status" role="status" aria-live="polite" class="sr-only"></p>
```

```js
const toggle = document.querySelector('#menu-toggle');
const menu = document.querySelector('#menu');
const status = document.querySelector('#status');

function setOpen(open) {
  toggle.setAttribute('aria-expanded', String(open));
  menu.hidden = !open;
  status.textContent = open ? 'Menu opened' : 'Menu closed';
}

toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
menu.addEventListener('keydown', (e) => { if (e.key === 'Escape') { setOpen(false); toggle.focus(); } });
```

What each attribute does:

- **`aria-expanded`** on the control (never on the panel) tells the user the button toggles
  something and its current state. Keep it a string `"true"`/`"false"`.
- **`aria-controls`** links control to panel; some screen readers offer a jump. Low value, cheap.
- **`aria-current="page"`** marks the current nav link; also `step`, `date`, `location`, `true`.
- **`aria-hidden="true"` on decorative SVG** plus a visually hidden text label (Tailwind `sr-only`)
  gives the icon button a name. Alternatively `aria-label="Menu"` on the button; prefer visible or
  `sr-only` text because it gets translated and copied, `aria-label` does not.
- **`role="status"`** (implicit `aria-live="polite"`) is a region that exists on page load, empty;
  you fill it later and the new text is announced without moving focus. Use `role="alert"`
  (assertive) only for errors that block the user.

Naming rules: `aria-labelledby="id"` reuses visible text (best), `aria-label` sets hidden text
(fine for icon buttons and landmarks), `aria-describedby` adds secondary help or error text, and
`title` is not a reliable name. Visible label text must be contained in the accessible name
(WCAG 2.2 SC 2.5.3) so voice-control users can say what they see.

## Variations

- **Accordion**: same `aria-expanded`/`aria-controls` per header button, or just use
  `<details name="faq">` and skip ARIA entirely (see `web-ui-accordion`).
- **Tabs**: `role="tablist"` on the container, `role="tab"` + `aria-selected` + `aria-controls`
  on buttons, `role="tabpanel"` + `aria-labelledby` on panels, roving `tabindex` with arrow keys.
  Only worth it when panels really are tabs; otherwise use links to sections.
- **Menu button**: `aria-haspopup="menu"` + `aria-expanded` on the button, `role="menu"` /
  `role="menuitem"` on items, arrow-key navigation. For a nav dropdown of links do **not** use
  menu roles: a plain list of links with `aria-expanded` on the toggle is correct and simpler.
- **Toggle switch**: `<button role="switch" aria-checked="true">` when there is no form value;
  `<input type="checkbox" role="switch">` when there is.

## Pitfalls

- Adding a role to an element that already has it (`<button role="button">`, `<nav role="navigation">`).
  Harmless but noise; and `<a role="button">` without `href` loses keyboard focus entirely.
- Overriding native semantics: `<h2 role="button">`, `<ul role="tablist">` with `<li>` children.
  Child roles must match (`tab` inside `tablist`, `option` inside `listbox`) or the widget breaks.
- `aria-hidden="true"` on anything that contains focusable content; the element is still tabbable
  but silent. Use `inert` or `hidden` instead to remove it from both.
- `aria-label` on a `<div>` or `<span>`: generic elements have no role, so most screen readers
  ignore the label. Put names on landmarks, widgets, images and form controls.
- Injecting a live region into the DOM at the moment you need it; it will not announce. Render it
  empty on load and update `textContent` later. Do not make big containers `aria-live`.
- Relying on `aria-disabled` without blocking the action in JS, or `disabled` on a control users
  need to reach to read its error. `aria-disabled="true"` keeps it focusable; your handler must
  ignore clicks.
- Writing ARIA states as booleans in JS (`el.ariaExpanded = true` works in modern browsers, but
  `setAttribute('aria-expanded', 'true')` is the safe form).

## Related skills

- `web-a11y-semantic-html`
- `web-a11y-keyboard-and-focus`
- `web-nav-dropdown-menu`
- `web-nav-tabs`
- `web-ui-toast-notifications`
- `web-ui-modal-dialog`
