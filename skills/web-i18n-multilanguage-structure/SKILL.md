---
name: web-i18n-multilanguage-structure
description: 'Structure a static site in multiple languages: one folder per language (/en/, /de/, /ar/), correct `lang` and `dir` per page, reciprocal hreflang and x-default links, a switcher that keeps the current page, a root language redirect and sitemap alternates. Use when a user says "translate the site", "multiple languages", "add German/Arabic", "hreflang", "language switcher" or "which URL structure for languages".'
---

# Multi-language site structure

Search engines and browsers need to know three things: which language each page is in (`<html lang>`), where the same page lives in other languages (`hreflang`), and which one to show when nothing matches (`x-default`). The simplest structure that gives all three on a static host is a folder per language with identical file names inside, so `/de/about.html` is always the German `/en/about.html`. That symmetry is what lets a switcher, a build script and a sitemap generator compute every alternate URL from the current path instead of a lookup table.

## Pattern

```text
dist/
  index.html            # no content: redirects to the best language, lists all of them for no-JS
  en/  index.html  about.html  pricing.html
  de/  index.html  about.html  pricing.html
  ar/  index.html  about.html  pricing.html
  js/lang-switch.js
  sitemap.xml
```

Every page declares its own language and links to all of its siblings with absolute URLs:

```html
<!-- dist/de/about.html -->
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Über uns · Beispiel GmbH</title>
  <link rel="canonical" href="https://example.com/de/about.html">
  <link rel="alternate" hreflang="en" href="https://example.com/en/about.html">
  <link rel="alternate" hreflang="de" href="https://example.com/de/about.html">
  <link rel="alternate" hreflang="ar" href="https://example.com/ar/about.html">
  <link rel="alternate" hreflang="x-default" href="https://example.com/en/about.html">
</head>
```

The Arabic page is identical except `<html lang="ar" dir="rtl">` and a title such as `من نحن · شركة المثال`. The switcher is one `<nav>` per page; each link names its language in that language, carries its own `lang` so screen readers switch voice, and the script rewrites the `href`s so the user lands on the same page, not the home page:

```html
<nav aria-label="Language" class="text-sm">
  <ul class="flex flex-wrap gap-4">
    <li><a data-lang="en" lang="en" hreflang="en" href="/en/" class="underline-offset-4 hover:underline aria-[current]:font-semibold aria-[current]:no-underline">English</a></li>
    <li><a data-lang="de" lang="de" hreflang="de" href="/de/" class="underline-offset-4 hover:underline aria-[current]:font-semibold aria-[current]:no-underline">Deutsch</a></li>
    <li><a data-lang="ar" lang="ar" hreflang="ar" dir="rtl" href="/ar/" class="underline-offset-4 hover:underline aria-[current]:font-semibold aria-[current]:no-underline">العربية</a></li>
  </ul>
</nav>
<script type="module" src="/js/lang-switch.js"></script>
```

```js
// js/lang-switch.js - "/de/about.html?plan=pro#faq" -> "/ar/about.html?plan=pro#faq"
const [, current, ...rest] = location.pathname.split('/');
const tail = rest.join('/') + location.search + location.hash;
for (const link of document.querySelectorAll('a[data-lang]')) {
  const lang = link.dataset.lang;
  link.href = `/${lang}/${tail}`;
  if (lang === current) link.setAttribute('aria-current', 'page');
  link.addEventListener('click', () => localStorage.setItem('lang', lang)); // explicit choice beats browser guess
}
```

The root `index.html` picks a language once, from a remembered choice or `navigator.languages`, and falls back to plain links when scripts are off:

```html
<!-- dist/index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Example</title>
  <link rel="alternate" hreflang="x-default" href="https://example.com/en/">
  <script>
    const LANGS = ['en', 'de', 'ar'];
    const saved = localStorage.getItem('lang');
    const guess = navigator.languages.map(tag => new Intl.Locale(tag).language).find(l => LANGS.includes(l));
    location.replace(`/${LANGS.includes(saved) ? saved : guess ?? 'en'}/${location.search}${location.hash}`);
  </script>
  <noscript><meta http-equiv="refresh" content="0; url=/en/"></noscript>
</head>
<body>
  <ul><li><a href="/en/" lang="en">English</a></li><li><a href="/de/" lang="de">Deutsch</a></li><li><a href="/ar/" lang="ar" dir="rtl">العربية</a></li></ul>
</body>
</html>
```

In `sitemap.xml`, list every language version of every page and repeat the alternates inside each `<url>`:

```xml
<url>
  <loc>https://example.com/de/about.html</loc>
  <xhtml:link rel="alternate" hreflang="en" href="https://example.com/en/about.html"/>
  <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/about.html"/>
  <xhtml:link rel="alternate" hreflang="ar" href="https://example.com/ar/about.html"/>
  <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/en/about.html"/>
</url>
```

(`urlset` needs `xmlns:xhtml="http://www.w3.org/1999/xhtml"`.)

## Variations

- **Generate the folders instead of hand-copying.** Keep one `src/pages/about.html` with `{{ t:about.title }}` placeholders and loop over `i18n/*.json` in the build: `for lang in LANGS: write(f"dist/{lang}/about.html", re.sub(r"\{\{\s*t:([\w.]+)\s*\}\}", lambda m: strings[lang][m[1]], tpl))`, injecting `lang`, `dir` and the hreflang block from the same loop. String files and plural handling are in `web-i18n-translation-strings`; the build loop fits in `web-content-partials-build`.
- **Regional variants.** `hreflang="en-GB"` and `hreflang="en-US"` are valid; folder names follow (`/en-gb/`). Always add a plain `hreflang="en"` too, or users with `en-AU` get `x-default`.
- **Server-side negotiation** when the host supports it: Netlify `_redirects` with `/  /de/  302  Language=de`, Cloudflare/nginx on `Accept-Language`. Keep the client script as the fallback and never redirect anything except the root.
- **Translated slugs** (`/de/ueber-uns.html`): the symmetric trick breaks, so emit `data-alt-en="/en/about.html"` attributes on the switcher links at build time and read those instead of rewriting the path.

## Pitfalls

- hreflang must be **reciprocal and absolute**: every page lists itself and all siblings with full `https://` URLs. A one-sided link is ignored by Google.
- Do not redirect on IP or country; language is not location. Do not redirect inner pages at all: a shared `/de/pricing.html` link must open the German page for everyone.
- `<html lang>` drives hyphenation, quotation marks, font selection and screen-reader voice. Set it per page to the real language, with `dir="rtl"` for Arabic, Hebrew, Persian and Urdu (`web-i18n-rtl`).
- Flags are countries, not languages: Arabic is spoken in 22 states, Spanish on two continents. Use the language's own name (an endonym) as the label.
- Fully untranslated pages should not exist under `/de/`; link to `/en/` from the switcher with `hreflang="en"` instead of serving English at a German URL, otherwise the canonical and hreflang contradict each other.
- `Intl.Locale('de-CH').language` is `'de'`; using `navigator.language.slice(0, 2)` fails for three-letter tags like `fil` and for `zh-Hant`.
- Tailwind scans `dist/**` only if it is not gitignored; keep the source in `src/` and generated folders in `dist/`, and add `@source` if templates live elsewhere (`web-ship-project-setup`).

## Related skills

- `web-i18n-translation-strings`
- `web-i18n-rtl`
- `web-i18n-fonts-and-scripts`
- `web-seo-sitemap-robots-urls`
- `web-seo-meta-tags`
- `web-content-partials-build`
- `web-ship-project-setup`
