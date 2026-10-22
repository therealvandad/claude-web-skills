---
name: web-i18n-fonts-and-scripts
description: Choose fonts, fallbacks, subsets and per-script line height for Arabic, Hebrew, CJK, Devanagari, Thai and Cyrillic, using :lang() rules and Tailwind v4 @theme tokens. Use when a user says "Arabic font looks wrong", "Chinese characters", "font for Hindi", "tofu boxes", "font fallback for other languages" or "line height for Arabic".
---

# Fonts and line metrics per writing system

A Latin web font covers Latin and maybe Cyrillic; every other script falls through to whatever the OS has, which may be a mismatched weight, a different x-height, or nothing at all (empty boxes, "tofu"). Scripts also need different metrics: Arabic and Devanagari have tall ascenders and marks above and below the line, CJK glyphs are full-width squares that look large at Latin sizes, and Thai stacks vowels and tone marks. Declare a font stack per script, switch it by `lang` rather than by page, and set line height and size per script once in the base layer.

## Pattern

```css
/* src/input.css */
@import "tailwindcss";

/* Self-hosted subsets: the browser downloads a file only if the page contains a character in its range */
@font-face {
  font-family: "Noto Sans Arabic"; font-weight: 400 700; font-display: swap;
  src: url("/fonts/noto-sans-arabic-var.woff2") format("woff2");
  unicode-range: U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF;
}
@font-face {
  font-family: "Noto Sans Hebrew"; font-weight: 400 700; font-display: swap;
  src: url("/fonts/noto-sans-hebrew-var.woff2") format("woff2");
  unicode-range: U+0590-05FF, U+FB1D-FB4F;
}

@theme {
  --font-sans: "Inter", "Noto Sans Arabic", "Noto Sans Hebrew", system-ui, sans-serif;
  --font-arabic: "Noto Sans Arabic", "Geeza Pro", "Segoe UI", Tahoma, sans-serif;
  --font-hebrew: "Noto Sans Hebrew", "Arial Hebrew", "Segoe UI", Arial, sans-serif;
  --font-cjk-ja: "Hiragino Sans", "Yu Gothic UI", "Meiryo", "Noto Sans JP", sans-serif;
  --font-cjk-zh: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  --font-deva: "Noto Sans Devanagari", "Kohinoor Devanagari", "Nirmala UI", sans-serif;
}

@layer base {
  :lang(ar), :lang(fa), :lang(ur) { font-family: var(--font-arabic); line-height: 1.8; letter-spacing: 0 !important; }
  :lang(he) { font-family: var(--font-hebrew); line-height: 1.6; }
  :lang(ja) { font-family: var(--font-cjk-ja); line-height: 1.8; line-break: strict; font-style: normal; }
  :lang(zh) { font-family: var(--font-cjk-zh); line-height: 1.8; font-style: normal; }
  :lang(ko) { word-break: keep-all; line-height: 1.7; }      /* break between words, not syllables */
  :lang(hi), :lang(mr) { font-family: var(--font-deva); line-height: 1.9; }
  :lang(ar) :is(h1, h2, h3), :lang(hi) :is(h1, h2, h3) { line-height: 1.5; }
  :lang(ja) :is(p, li), :lang(zh) :is(p, li) { font-size: 0.9375em; }   /* full-width glyphs read large */
}
```

Mixed content keeps working because `lang` can sit on any element:

```html
<html lang="en">
<body class="font-sans text-base leading-relaxed text-gray-900 dark:bg-gray-950 dark:text-gray-100">
  <main class="mx-auto max-w-prose space-y-6 px-4 py-12">
    <h1 class="text-3xl font-bold tracking-tight">Opening hours</h1>
    <p>Monday to Friday, 9:00 to 18:00.</p>

    <!-- tracking-tight is neutralised by the :lang(ar) rule; Arabic letters must stay joined -->
    <section lang="ar" dir="rtl" class="space-y-2">
      <h2 class="text-2xl font-bold tracking-tight">ساعات العمل</h2>
      <p>من الاثنين إلى الجمعة، من الساعة ٩ صباحًا حتى ٦ مساءً.</p>
    </section>

    <section lang="he" dir="rtl"><p>ימים שני עד שישי, 9:00 עד 18:00.</p></section>
    <section lang="ja"><p>営業時間は月曜日から金曜日の9時から18時までです。</p></section>
    <section lang="hi"><p>सोमवार से शुक्रवार, सुबह 9 बजे से शाम 6 बजे तक।</p></section>
  </main>
</body>
</html>
```

Subset a large font to the characters you use (one-off, needs `pip install fonttools brotli`):

```bash
pyftsubset NotoSansJP-VF.ttf --text-file=dist/ja/all-text.txt --flavor=woff2 --output-file=public/fonts/noto-jp-subset.woff2
```

## Variations

- **Google Fonts instead of self-hosting**: `family=Noto+Sans+Arabic:wght@400..700&display=swap` already ships `unicode-range` slices, and for CJK it splits the font into about a hundred slices, so only used characters load. Add `&text=...` only for a logo or heading with fixed text.
- **Cyrillic and Greek**: most good Latin families (Inter, IBM Plex, Source Sans, Roboto) include them; check before adding a second family, and load the `cyrillic` subset explicitly when self-hosting, or Russian pages fall back mid-word.
- **System fonts only**: for CJK the OS fonts are excellent and a web font costs megabytes. A stack of named system fonts per platform (as in `--font-cjk-ja`) is often the best choice; web-load only a display face for headings.
- **Tailwind variant**: for one-off overrides add `@custom-variant lang-ar (&:lang(ar));` (`:lang()` matches every descendant too) and write `lang-ar:text-lg` instead of another base rule.

## Pitfalls

- `letter-spacing` breaks Arabic joining and looks wrong in Devanagari; `tracking-*`, `uppercase` and small caps are Latin-only effects. Guard them as above or apply them inside `:lang(en)` only.
- Do not set the same pixel size for every script. Arabic at 16 px reads like Latin at 13 px; bump body text one step (`:lang(ar) { font-size: 1.0625em }`) and check that buttons still fit.
- Never italicise CJK: there is no italic, the browser fakes a slant. `font-style: normal` on `em` inside `:lang(ja)`, and use bold or emphasis marks (`text-emphasis: filled dot`) instead.
- Chinese and Japanese share code points but draw them differently. `lang="ja"` versus `lang="zh-Hans"` picks the right regional glyphs from Noto CJK or system fonts; wrong `lang` shows Chinese forms to Japanese readers.
- A Latin font that lacks a glyph causes per-character fallback, so mixed-script lines get two baselines. Put the script font before `system-ui` in the stack and test a line with both scripts at once.
- Variable CJK fonts are 5 to 20 MB. Never `preload` them; preload only the Latin face for the LCP heading (`web-perf-fonts`).

## Related skills

- `web-i18n-rtl`
- `web-i18n-multilanguage-structure`
- `web-perf-fonts`
- `web-craft-typography-with-character`
- `web-design-typography-system`
