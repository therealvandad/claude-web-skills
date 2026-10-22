---
name: web-js-web-components
description: Build reusable widgets as custom elements (`my-counter`, `copy-button`, `toggle-panel`) with vanilla JavaScript, light DOM so Tailwind classes apply, attributes as the API, events out, and proper cleanup; with the shadow DOM variant when style isolation is wanted. Use whenever a user says "reusable component without React", "custom element", "web component", "same widget on many pages", or "encapsulate this behaviour".
---

# Web components: reusable widgets the browser understands

A custom element gives you what a framework component gives you (markup, behaviour and lifecycle bundled under one tag) with zero dependencies, and it works in any HTML file including CMS-generated pages. For a Tailwind site use **light DOM**: the element wraps server-rendered children, enhances them, and your utility classes keep working because there is no style boundary. Reach for **shadow DOM** only when you need true style isolation (an embeddable widget dropped into unknown pages). Attributes are the public API; `CustomEvent`s are the output.

## Pattern

Copy-to-clipboard button: the HTML works before JS loads (the code is visible and selectable); the element adds the button behaviour.

```html
<copy-text label="Copy command" class="block rounded-lg border bg-gray-50 p-3">
  <pre class="overflow-x-auto text-sm"><code>npm create vite@latest</code></pre>
</copy-text>

<script type="module" src="/js/elements/copy-text.js"></script>
```

```js
// /js/elements/copy-text.js
class CopyText extends HTMLElement {
  static observedAttributes = ['label'];
  #controller;                              // private: listener cleanup
  #button;
  #timer;

  connectedCallback() {
    if (this.#button) return;               // guard: connected twice (moved in DOM)
    if (!navigator.clipboard) return;       // progressive enhancement: no API, no button
    this.#button = Object.assign(document.createElement('button'), {
      type: 'button',
      className: 'mt-2 rounded bg-gray-900 px-2 py-1 text-xs text-white focus-visible:outline-2',
      textContent: this.getAttribute('label') ?? 'Copy',
    });
    this.#button.setAttribute('aria-live', 'polite');
    this.append(this.#button);

    this.#controller = new AbortController();
    this.#button.addEventListener('click', () => this.copy(), { signal: this.#controller.signal });
  }

  disconnectedCallback() {
    this.#controller?.abort();
    clearTimeout(this.#timer);
  }

  attributeChangedCallback(name, _old, value) {
    if (name === 'label' && this.#button) this.#button.textContent = value ?? 'Copy';
  }

  /** Public method; also usable from outside: el.copy() */
  async copy() {
    const text = this.querySelector('code, pre')?.textContent ?? this.textContent;
    try {
      await navigator.clipboard.writeText(text.trim());
      this.#flash('Copied');
      this.dispatchEvent(new CustomEvent('copy-text:copied', { bubbles: true, detail: { text } }));
    } catch (error) {
      this.#flash('Copy failed');
      this.dispatchEvent(new CustomEvent('copy-text:error', { bubbles: true, detail: { error } }));
    }
  }

  #flash(message) {
    const original = this.getAttribute('label') ?? 'Copy';
    this.#button.textContent = message;
    clearTimeout(this.#timer);
    this.#timer = setTimeout(() => { this.#button.textContent = original; }, 1500);
  }
}

if (!customElements.get('copy-text')) customElements.define('copy-text', CopyText);
```

```js
// consumer: listen like any DOM event
document.addEventListener('copy-text:copied', (e) => console.log('copied', e.detail.text));
```

```css
/* avoid layout shift / FOUC before the element upgrades */
copy-text:not(:defined) button { display: none; }
```

## Variations

- **Properties for rich data**: attributes are strings; for arrays/objects expose a property (`set items(v) { this.#items = v; this.#render(); }`) and reflect simple scalars to attributes (`get open() { return this.hasAttribute('open'); }`).
- **Shadow DOM for isolation**: in `constructor()` call `this.attachShadow({ mode: 'open' })`, put a `<style>` + markup inside, and use `<slot>` for children. Tailwind utilities do not cross the boundary; either inline a small stylesheet or import your built CSS inside the shadow with `<link rel="stylesheet" href="/css/output.css">` (cached, so cheap).
- **Form participation** (a custom input that submits with the form): `static formAssociated = true` plus `this.#internals = this.attachInternals()` and `this.#internals.setFormValue(value)`.
- **Declarative instances** from a `<template>`: in `connectedCallback`, `this.append(template.content.cloneNode(true))`; keep the template in the HTML so content stays editable without touching JS.

## Pitfalls

- Tag names need a hyphen (`copy-text`, never `copytext`) and `define` throws if called twice, hence the `customElements.get` guard when the module may load more than once.
- Do not touch children or attributes in the `constructor`; they may not exist yet when the parser upgrades the element. Do it in `connectedCallback`.
- `connectedCallback` runs again if the element is moved; guard against re-creating buttons or listeners, and undo everything in `disconnectedCallback` or you leak timers and handlers.
- A custom element is `display: inline` by default. Add `class="block"` (or a `:host { display: block }` rule in shadow DOM) or layouts break.
- Shadow DOM hides content from page-level CSS *and* from `document.querySelector`, and screen readers see `aria-labelledby` references only inside the same root. Light DOM avoids all three issues.
- `bubbles: true` is not the default for `CustomEvent`; without it, delegated `document` listeners never hear your event. Add `composed: true` as well if it must escape a shadow root.

## Related skills

- `web-js-state-and-render`
- `web-js-modules-and-structure`
- `web-ui-buttons`
- `web-a11y-aria-patterns`
- `web-js-dom-utilities`
