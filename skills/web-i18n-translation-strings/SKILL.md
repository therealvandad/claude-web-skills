---
name: web-i18n-translation-strings
description: Keep UI text in one JSON file per language and translate it with a 30-line t() that does {name} interpolation, Intl.PluralRules plurals and English fallback, plus data-i18n attributes for static markup, no library. Use when a user says "translate the buttons", "strings file", "i18n JSON", "t() function", "pluralise", "1 item vs 2 items" or "how do I store translations".
---

# Translation strings and a tiny t()

Text hard-coded in templates and scripts cannot be handed to a translator, and string concatenation (`'You have ' + n + ' items'`) cannot be translated at all because word order and plural forms differ by language. Move every user-visible string into a flat JSON file per language keyed by meaning, interpolate named placeholders, and pick plural forms with `Intl.PluralRules` so Arabic gets its six forms and English its two from the same code. That covers what most static sites need; reach for a library (ICU MessageFormat) only for gender and nested selects.

## Pattern

```text
i18n/en.json   i18n/de.json   i18n/ar.json   js/i18n.js
```

```json
{
  "cart.title": "Your cart",
  "cart.greeting": "Hi {name}, welcome back.",
  "cart.items": { "one": "{count} item", "other": "{count} items" },
  "cart.checkout": "Check out"
}
```

```json
{
  "cart.title": "Warenkorb",
  "cart.greeting": "Hallo {name}, schön, dass du wieder da bist.",
  "cart.items": { "one": "{count} Artikel", "other": "{count} Artikel" },
  "cart.checkout": "Zur Kasse"
}
```

```json
{
  "cart.title": "سلة التسوق",
  "cart.greeting": "مرحبًا {name}، أهلًا بعودتك.",
  "cart.items": {
    "zero": "لا توجد منتجات", "one": "منتج واحد", "two": "منتجان",
    "few": "{count} منتجات", "many": "{count} منتجًا", "other": "{count} منتج"
  },
  "cart.checkout": "إتمام الشراء"
}
```

```js
// js/i18n.js
const lang = document.documentElement.lang || 'en';
const load = async l => (await fetch(`/i18n/${l}.json`)).json();
const [messages, fallback] = await Promise.all([load(lang), lang === 'en' ? null : load('en')]);
const plural = new Intl.PluralRules(lang);
const number = new Intl.NumberFormat(lang);

export function t(key, vars = {}) {
  let msg = messages[key] ?? fallback?.[key];
  if (msg === undefined) { console.warn(`i18n: missing "${key}" (${lang})`); return key; }
  if (typeof msg === 'object') msg = msg[plural.select(vars.count)] ?? msg.other;
  return msg.replace(/\{(\w+)\}/g, (_, name) =>
    name in vars ? (typeof vars[name] === 'number' ? number.format(vars[name]) : String(vars[name])) : `{${name}}`);
}

// Static markup: <h1 data-i18n="cart.title">Your cart</h1>
export function translatePage(root = document) {
  for (const el of root.querySelectorAll('[data-i18n]')) el.textContent = t(el.dataset.i18n);
  for (const el of root.querySelectorAll('[data-i18n-attr]')) {          // data-i18n-attr="aria-label:cart.title"
    for (const pair of el.dataset.i18nAttr.split(';')) {
      const [attr, key] = pair.split(':');
      el.setAttribute(attr.trim(), t(key.trim()));
    }
  }
}
translatePage();
```

```html
<h1 data-i18n="cart.title" class="text-2xl font-bold">Your cart</h1>
<p id="count" class="text-sm text-gray-600 dark:text-gray-400" aria-live="polite"></p>
<button data-i18n="cart.checkout" class="rounded-md bg-gray-900 px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2">Check out</button>
<script type="module">
  import { t } from '/js/i18n.js';
  document.querySelector('#count').textContent = t('cart.items', { count: 3 });
  // en "3 items" · de "3 Artikel" · ar "3 منتجات" (few) · ar count 11 -> "11 منتجًا" (many)
</script>
```

## Variations

- **Build time instead of runtime**: for pages that never change after load, replace `data-i18n` keys while writing `dist/<lang>/` in the build (`web-content-partials-build`). No flash of English, no fetch, and search engines see the translated text. Keep the runtime `t()` for strings created by JavaScript (toasts, validation messages, counts).
- **Nested files**: if translators prefer `{ "cart": { "title": "..." } }`, flatten once on load so `t()` stays one lookup: `const flat = (o, p = '') => Object.entries(o).flatMap(([k, v]) => typeof v === 'object' && !('other' in v) ? flat(v, `${p}${k}.`) : [[p + k, v]]);` then `Object.fromEntries(flat(json))`.
- **Rich text**: keep HTML out of strings. Split around the link (`"terms.before": "I accept the "`, `"terms.link": "terms"`) or use a placeholder the code fills with a DOM node, so translators cannot break markup and you never assign untrusted text to `innerHTML`.
- **Ordinals**: `new Intl.PluralRules('en', { type: 'ordinal' })` returns `one/two/few/other` for 1st/2nd/3rd/4th; key the forms the same way (`"place": { "one": "{count}st", "two": "{count}nd", ... }`).

## Pitfalls

- Keys by meaning (`cart.checkout`), not by English text (`"Check out"`): the same English word often needs two translations ("Open" a file vs "Open" status).
- Every language needs `other`; `t()` falls back to it, but a missing `few` in Arabic silently shows the wrong grammar. Lint with a script that checks each plural object has every category from `new Intl.PluralRules(lang).resolvedOptions().pluralCategories`.
- Do not build sentences from fragments (`t('you_have') + count + t('items')`); word order differs. One key per full sentence with placeholders.
- Translations run 30 to 40 percent longer in German and Finnish. Leave room: no fixed widths on buttons, allow wrapping, test with the longest language.
- Top-level `await` in the module blocks only that module; keep the English text in the HTML so the page is readable before and if the JSON fails.
- Set `lang` (and `dir` for Arabic/Hebrew) on `<html>` before translating, or screen readers will read Arabic text with an English voice (`web-i18n-rtl`).

## Related skills

- `web-i18n-dates-currency`
- `web-i18n-multilanguage-structure`
- `web-i18n-rtl`
- `web-content-partials-build`
- `web-js-fetch-and-apis`
