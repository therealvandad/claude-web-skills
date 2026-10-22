---
name: web-i18n-rtl
description: Make a Tailwind v4 page work right-to-left for Arabic, Hebrew, Persian or Urdu - `dir="rtl"` on `html`, logical utilities (ms-/me-/ps-/pe-/start-/end-/text-start) instead of left/right, `rtl:` variants, which icons to mirror, and `bdi`/`dir="auto"` for mixed-direction text, numbers and phone numbers. Use when a user says "Arabic", "Hebrew", "RTL", "right to left", "the layout is mirrored wrong" or "bidi text".
---

# Right-to-left support

Setting `dir="rtl"` on `<html>` flips the layout engine: block flow, flex and grid order, text alignment, scrollbars and the start edge of everything. What it cannot flip is a class that says `left`. The work of RTL support is therefore mostly replacing physical utilities (`ml-4`, `pl-6`, `left-0`, `text-left`, `rounded-l-lg`) with logical ones (`ms-4`, `ps-6`, `start-0`, `text-start`, `rounded-s-lg`) that follow the writing direction automatically, then handling the few things that need judgement: directional icons, mixed-direction text and numbers.

## Pattern

One markup, two directions. The same header and card render correctly in English and in Arabic with no `rtl:` overrides except the arrow icon.

```html
<!doctype html>
<html lang="ar" dir="rtl">   <!-- English version: lang="en" dir="ltr"; nothing else changes -->
<body class="min-h-dvh bg-white font-sans text-gray-900">
  <header class="flex items-center gap-6 border-b border-gray-200 px-4 py-3">
    <a href="/ar/" class="text-lg font-bold">متجر النور</a>
    <nav aria-label="الرئيسية">
      <ul class="flex gap-6 text-sm">
        <li><a href="/ar/products.html" class="hover:underline">المنتجات</a></li>
        <li><a href="/ar/about.html" class="hover:underline">من نحن</a></li>
      </ul>
    </nav>
    <!-- ms-auto pushes to the far end: right in LTR, left in RTL -->
    <a href="/ar/cart.html" class="ms-auto rounded-md bg-gray-900 px-4 py-2 text-sm text-white">السلة (3)</a>
  </header>

  <main class="mx-auto max-w-2xl px-4 py-10">
    <article class="border-s-4 border-emerald-600 ps-5">
      <p class="text-xs uppercase tracking-normal text-gray-500">طلب رقم <span dir="ltr">#A-2041</span></p>
      <h1 class="mt-1 text-2xl font-bold text-start">تم شحن طلبك</h1>
      <p class="mt-3 leading-relaxed">
        سيصل الطرد إلى <bdi>Fatima Al-Sayed</bdi> خلال يومين. للاستفسار اتصل على
        <a href="tel:+97141234567" dir="ltr" class="whitespace-nowrap underline">+971 4 123 4567</a>.
      </p>
      <a href="/ar/orders/A-2041.html" class="mt-4 inline-flex items-center gap-2 text-emerald-700 hover:underline">
        تتبع الشحنة
        <!-- directional arrow: mirrored in RTL -->
        <svg class="size-4 rtl:-scale-x-100" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M3 8h10M9 4l4 4-4 4"/>
        </svg>
      </a>
    </article>

    <!-- user-generated text of unknown direction: let the browser decide per field -->
    <form class="mt-10 grid gap-3">
      <label for="note" class="text-sm font-medium">ملاحظة للسائق</label>
      <textarea id="note" dir="auto" rows="3" class="rounded-md border border-gray-300 p-3 text-start"></textarea>
      <button class="justify-self-start rounded-md bg-emerald-600 px-4 py-2 text-white">إرسال</button>
    </form>
  </main>
</body>
</html>
```

Pick the direction from the language in one place when the language is set at runtime:

```js
const RTL = new Set(['ar', 'he', 'fa', 'ur', 'ps', 'sd', 'ug', 'yi']);
export function setDocumentLanguage(lang) {
  document.documentElement.lang = lang;
  document.documentElement.dir = RTL.has(new Intl.Locale(lang).language) ? 'rtl' : 'ltr';
}
```

Physical to logical cheat sheet (Tailwind v4 ships all of these):

```text
ml-* mr-*        -> ms-* me-*          pl-* pr-*          -> ps-* pe-*
left-* right-*   -> start-* end-*      text-left/right    -> text-start/end
rounded-l-* r-*  -> rounded-s-* e-*    border-l-* r-*     -> border-s-* e-*
float-left       -> float-start        scroll-ml-*        -> scroll-ms-*
translate-x-full for a slide-in drawer -> translate-x-full rtl:-translate-x-full
```

## Variations

- **One page, both directions** (a bilingual contract, a comment thread): put `dir` on the section or `<article>` instead of `<html>`; logical utilities and `rtl:` variants resolve against the nearest `dir` ancestor, so a `dir="rtl"` block inside an LTR page just works.
- **Decorative mirroring**: a hero illustration with a figure "looking into" the text should flip: `<img class="rtl:-scale-x-100">`. Directional gradients too: `bg-linear-to-r rtl:bg-linear-to-l`.
- **Carousels and tabs**: `scrollLeft` is physical; in RTL it is 0 at the right edge and goes negative as you scroll. Avoid the arithmetic: move slides with `slide.scrollIntoView({ inline: 'start', behavior: 'smooth' })`, which is direction-aware, and find the current one with `getBoundingClientRect()`.
- **Hebrew** needs no extra work beyond `lang="he" dir="rtl"`; it has no joined letters, so `tracking-*` is harmless, but it shares the number and punctuation behaviour below.

## Pitfalls

- `dir` belongs on `<html>`, not `<body>`: only the root `dir` moves the scrollbar and makes `:dir(rtl)` match everything. Set `lang` alongside it; `dir` alone does not change fonts, hyphenation or screen-reader voice.
- Mirror only icons that encode direction of movement or reading: arrows, back/forward, "next" chevrons, indent, undo/redo, send. Do **not** mirror checkmarks, clocks, logos, media controls (play still points right), magnifiers or anything with text in it.
- Numbers, codes, phone numbers, URLs and email addresses are LTR runs. Wrap them in `<span dir="ltr">` or `<bdi>` so a leading `+` or trailing `!` does not jump to the wrong end. For a name or title inserted from data, `<bdi>` isolates it from the surrounding text's direction.
- `letter-spacing` breaks Arabic, which is a connected script. Never apply `tracking-tight` or `tracking-wide` on text that may be Arabic; see `web-i18n-fonts-and-scripts` for font and line-height rules.
- `text-left` on a form label or table cell is the most common leftover; grep for `-left`, `-right`, `pl-`, `pr-`, `ml-`, `mr-`, `left-`, `right-` and ask of each whether it means "start" or truly "left" (a map legend's compass does mean left).
- Shadows and `translate-x` in hover effects (`hover:translate-x-1` on an arrow link) move the wrong way: add `rtl:hover:-translate-x-1`.
- Test by typing `document.dir = 'rtl'` in the console on the English page: anything that looks wrong there is a physical class, not a translation problem.

## Related skills

- `web-i18n-multilanguage-structure`
- `web-i18n-fonts-and-scripts`
- `web-i18n-translation-strings`
- `web-i18n-dates-currency`
- `web-nav-responsive-navbar`
- `web-ui-carousel`
