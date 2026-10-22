---
name: web-theme-editorial
description: 'Drop a complete magazine look onto a site in Tailwind v4: Newsreader display serif with optical sizing, cream paper and oxblood accent in oklch, hairline rules, numbered sections, drop caps, a strict 65ch measure and no shadows. Use whenever a user says "make it look like a magazine", "editorial", "like a newspaper", "long-read", "journal", "publication feel" or "literary".'
---

# Editorial theme

A magazine page is built from four things: a serif with real optical sizes, a measure the eye can carry, rules instead of boxes, and ink on paper instead of colour. Nothing floats, nothing glows; hierarchy comes from size, italics and small numbered labels. Because every decision is typographic, the look survives any content, which is why it still reads as designed when a template would not.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..600;1,6..72,300..600&family=Public+Sans:wght@400;500&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Newsreader", "Iowan Old Style", Georgia, serif;
  --font-sans: "Public Sans", system-ui, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, monospace;

  /* Paper and ink, warmed toward hue 70. Accent is oxblood, used for links and one rule. */
  --color-paper:   oklch(97% 0.010 70);
  --color-paper-2: oklch(93% 0.014 70);
  --color-ink:     oklch(20% 0.015 60);
  --color-ink-2:   oklch(45% 0.015 60);
  --color-line:    oklch(82% 0.014 70);
  --color-accent:      oklch(42% 0.14 25);
  --color-accent-deep: oklch(34% 0.13 25);

  /* No radius and no shadows: an editorial page is flat. */
  --radius-*: initial;
  --radius-sm: 0;
  --shadow-*: initial;

  --text-display: clamp(2.75rem, 1.6rem + 4vw, 5.5rem);
  --text-display--line-height: 1.0;
  --text-display--letter-spacing: -0.005em;
  --text-title: clamp(1.75rem, 1.3rem + 1.4vw, 2.5rem);
  --text-title--line-height: 1.12;
  --text-deck: 1.375rem;
  --text-deck--line-height: 1.45;
  --text-body: 1.125rem;
  --text-body--line-height: 1.7;
  --text-label: 0.75rem;
  --text-label--line-height: 1;
  --text-label--letter-spacing: 0.14em;
}

@layer base {
  html { font-synthesis: none; }
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); }
  h1, h2, h3 { font-family: var(--font-display); font-weight: 400; font-optical-sizing: auto; text-wrap: balance; }
  h1 { font-variation-settings: "opsz" 72; }
  em { font-family: var(--font-display); font-style: italic; }
  a { color: var(--color-accent); text-decoration: underline; text-underline-offset: 0.18em; text-decoration-thickness: 1px; }
  a:hover { color: var(--color-accent-deep); text-decoration-thickness: 2px; }
  hr { border: 0; border-top: 1px solid var(--color-line); }
  :focus-visible { outline: 2px solid var(--color-ink); outline-offset: 3px; }
  ::selection { background: var(--color-paper-2); }
  .prose-editorial > p:first-of-type::first-letter {
    font-family: var(--font-display); font-weight: 500; float: left;
    font-size: 4.2em; line-height: 0.8; padding: 0.08em 0.1em 0 0;
  }
}
```

```html
<main class="mx-auto max-w-5xl px-6">
  <header class="border-b border-line py-14 lg:grid lg:grid-cols-[1fr_16rem] lg:gap-12">
    <div>
      <p class="font-mono text-label uppercase text-ink-2">No. 27 · Craft</p>
      <h1 class="mt-5 text-display text-ink">The last bindery on <em>Rue des Écoles</em></h1>
      <p class="mt-6 max-w-[38ch] font-display text-deck text-ink-2">Forty years of sewing signatures by hand, and what happens to the trade when its one apprentice leaves.</p>
    </div>
    <dl class="mt-10 border-t border-line pt-4 text-sm lg:mt-0 lg:self-end">
      <dt class="text-ink-2">Words</dt><dd>Hélène Marchetti</dd>
      <dt class="mt-3 text-ink-2">Photographs</dt><dd>Tomás Ríos</dd>
      <dt class="mt-3 text-ink-2">Reading time</dt><dd class="tabular-nums">14 min</dd>
    </dl>
  </header>

  <article class="prose-editorial mx-auto max-w-[65ch] py-14 text-body">
    <p>Marguerite Dupré opens at eight because the glue needs the morning's cold. By ten the shop smells of wheat paste and the radio is on.</p>
    <p class="mt-6">The order book is a real book. It has entries from 1987 that she can still read without her glasses.</p>
  </article>

  <section class="border-t border-line py-12">
    <h2 class="text-title">Elsewhere in this issue</h2>
    <ol class="mt-8 grid gap-x-10 gap-y-8 sm:grid-cols-3">
      <li class="border-t border-ink pt-4">
        <span class="font-mono text-label text-ink-2">01</span>
        <h3 class="mt-3 font-display text-2xl leading-tight"><a href="/issue-27/typecasting" class="text-ink no-underline hover:underline">Casting type in a kitchen</a></h3>
        <p class="mt-2 text-sm leading-6 text-ink-2">A Monotype caster, two phases of power and a very patient landlord.</p>
      </li>
      <li class="border-t border-ink pt-4">
        <span class="font-mono text-label text-ink-2">02</span>
        <h3 class="mt-3 font-display text-2xl leading-tight"><a href="/issue-27/paper" class="text-ink no-underline hover:underline">Why 90 gsm is the wrong question</a></h3>
        <p class="mt-2 text-sm leading-6 text-ink-2">Opacity, grain direction and the bulk number nobody prints on the ream.</p>
      </li>
      <li class="border-t border-ink pt-4">
        <span class="font-mono text-label text-ink-2">03</span>
        <h3 class="mt-3 font-display text-2xl leading-tight"><a href="/issue-27/letters" class="text-ink no-underline hover:underline">Letters</a></h3>
        <p class="mt-2 text-sm leading-6 text-ink-2">On our use of the word "artisan". You were right.</p>
      </li>
    </ol>
  </section>
</main>
```

What this theme does: serif display at weight 400 with `opsz` 72, sans body at 18px and 1.7 leading inside a 65ch measure, hairline `line` rules between every block, a heavier `ink` rule above each list item, numbered labels in mono small caps, italics for emphasis, one drop cap per article, accent only on links.

What it never does: shadows, border radius, gradients, coloured section backgrounds beyond `paper-2`, bold headings, icons in squares, more than two type families, centred body text, a hero image bleeding under the headline.

## Variations

- **Dark reading mode**: `--color-paper: oklch(18% 0.012 60)`, `--color-ink: oklch(92% 0.010 70)`, `--color-line: oklch(32% 0.012 60)`, accent to `oklch(72% 0.12 25)`. Override in `.dark` or a media query, not inside `@theme` (see `web-design-dark-mode`).
- **Two-column body on wide screens**: `lg:columns-2 lg:gap-12` on the article with `[column-rule:1px_solid_var(--color-line)]`; keep each column under 65ch and never split a heading (`break-after-avoid`).
- **Photo-led issue**: images get `grayscale-[15%] contrast-[1.05]`, a `figcaption` in `font-mono text-label`, and a full-bleed wrapper `w-screen max-w-none -mx-[calc(50vw-50%)]` at most once per page.
- **Cooler paper** for news rather than craft: hue 250 at the same chroma, accent stays oxblood so links remain the one warm thing.

## Pitfalls

- Newsreader at body sizes below 16px loses its hairlines on 1x screens; body stays in Public Sans, the serif is for 18px+ and headings.
- `::first-letter` drop caps misalign when the paragraph starts with a quotation mark; strip the mark or set `.prose-editorial > p:first-of-type { text-indent: 0 }` and open with a word.
- `ink-2` at 45% on `paper-2` at 93% is 5.0:1; lighten either and it drops under 4.5:1. Check with `web-a11y-color-contrast` after changing the hue.
- `text-balance` on the deck paragraph fights the 38ch measure; use `text-pretty` on anything longer than two lines.
- Resetting `--shadow-*` removes `shadow-sm` from dialogs too; give the dialog a 1px `line` border and a `paper-2` backdrop instead.
- Hairline rules on every element turn into a grid; one rule per boundary, and only between things that are genuinely different.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-color-with-restraint`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-design-tokens-to-tailwind`
- `web-theme-switcher`
- `web-page-blog-post`
