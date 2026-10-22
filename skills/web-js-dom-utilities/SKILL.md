---
name: web-js-dom-utilities
description: Write a tiny `dom.js` helper module ($, $$, on with delegation, create, data-attribute hooks) for plain-JavaScript pages, instead of jQuery or a framework. Use whenever a user asks "how do I select elements", "querySelector helper", "jQuery without jQuery", "create elements in JS", "event delegation", or wants to tidy repetitive DOM code on a static site.
---

# DOM utilities: the 40 lines you actually need

Vanilla DOM is verbose enough that people reach for jQuery or a framework out of habit. For a static site, a single `dom.js` module with four or five named helpers removes 90% of that friction while staying debuggable: every helper is a thin wrapper over a standard API, so nothing is hidden. The rule: helpers shorten *calls*, they never introduce *concepts* (no virtual DOM, no reactivity, no plugin system). If you find yourself writing a component lifecycle, stop and read `web-js-state-and-render` or `web-js-web-components`.

## Pattern

HTML hooks use `data-*` attributes, never classes (classes are for styling and get renamed; `data-js` is a contract).

```html
<ul data-js="todo-list">
  <li data-id="1">Buy milk <button type="button" data-action="remove">×</button></li>
  <li data-id="2">Walk dog <button type="button" data-action="remove">×</button></li>
</ul>
<script type="module" src="/js/main.js"></script>
```

```js
// /js/dom.js  (ES module, no globals)

/** First match, or null. Scope defaults to document. */
export const $ = (selector, scope = document) => scope.querySelector(selector);

/** All matches as a real Array (so .map/.filter work). */
export const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

/**
 * Add a listener. With `selector`, delegate: the handler runs only when the
 * event target (or an ancestor inside `root`) matches. Returns an unsubscribe.
 */
export function on(root, type, selectorOrHandler, maybeHandler, options) {
  const delegated = typeof selectorOrHandler === 'string';
  const handler = delegated ? maybeHandler : selectorOrHandler;
  const listener = delegated
    ? (event) => {
        const match = event.target.closest(selectorOrHandler);
        if (match && root.contains(match)) handler.call(match, event, match);
      }
    : handler;
  root.addEventListener(type, listener, options);
  return () => root.removeEventListener(type, listener, options);
}

/**
 * create('button', { class: 'btn', dataset: { action: 'save' }, onClick: fn }, 'Save')
 * Children: strings become text nodes (safe), nodes are appended as-is.
 */
export function create(tag, props = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value == null || value === false) continue;
    if (key === 'dataset') Object.assign(el.dataset, value);
    else if (key === 'style' && typeof value === 'object') Object.assign(el.style, value);
    else if (key.startsWith('on') && typeof value === 'function')
      el.addEventListener(key.slice(2).toLowerCase(), value);
    else if (key in el && key !== 'class') el[key] = value;     // value, checked, textContent...
    else el.setAttribute(key, value === true ? '' : value);      // class, aria-*, role
  }
  el.append(...children.filter((c) => c != null && c !== false));
  return el;
}

/** Escape text for the rare case you must build an HTML string. */
export const escapeHtml = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
```

```js
// /js/main.js
import { $, $$, on, create } from './dom.js';

const list = $('[data-js="todo-list"]');
if (list) {                                              // page may not have this widget
  const off = on(list, 'click', '[data-action="remove"]', (event, button) => {
    button.closest('li')?.remove();
  });

  const item = create('li', { dataset: { id: 3 } }, 'Write docs ',
    create('button', { type: 'button', dataset: { action: 'remove' }, 'aria-label': 'Remove' }, '×'));
  list.append(item);

  // call off() if the widget is ever torn down (e.g. in a SPA panel)
  window.addEventListener('pagehide', off, { once: true });
}
```

## Variations

- **Scoped widgets**: initialise every instance with `$$('[data-widget="tabs"]').forEach(initTabs)` and pass the root element in; keep each widget's `$`/`on` calls scoped to that root so two copies on one page don't collide.
- **Show/hide**: toggle the native `hidden` attribute (`el.hidden = !el.hidden`) rather than classes; Tailwind Preflight respects it and screen readers follow along. For animated hide, see `web-motion-transitions`.
- **Ready check**: with `<script type="module">` the DOM is already parsed when your code runs, so `DOMContentLoaded` is unnecessary. Only add it for classic inline scripts in `<head>`.
- **Templates**: for repeated markup, author it once in `<template data-js="row">` and clone with `template.content.cloneNode(true)`; it keeps HTML in HTML and avoids `innerHTML` string building.

## Pitfalls

- `innerHTML` with user or API data is an XSS hole. Use `textContent`, `create()`, or `escapeHtml()` when a string is unavoidable.
- Delegation only works for events that bubble. `focus`, `blur`, `mouseenter`, `load` do not; use `focusin`/`focusout`/`mouseover` or attach directly.
- `querySelectorAll` returns a static `NodeList`, not an Array, which is why `$$` wraps it in `Array.from`. Live `HTMLCollection`s from `getElementsByClassName` mutate under your feet during loops.
- Do not rebuild jQuery: no chaining, no `$.ajax`, no animation helpers. Each added feature is code every page pays to download and you to maintain.
- Never query with Tailwind utility classes (`.flex.gap-4`); they change whenever the design does. Query `data-*` attributes or ids.
- `in el` checks catch properties like `value` and `checked`, but SVG elements and `class` must go through `setAttribute`; that is why `class` is special-cased.

## Related skills

- `web-js-events-debounce-throttle`
- `web-js-state-and-render`
- `web-js-modules-and-structure`
- `web-js-clean-code`
- `web-js-web-components`
