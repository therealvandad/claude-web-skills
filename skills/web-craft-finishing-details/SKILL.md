---
name: web-craft-finishing-details
description: 'Add the handmade finishing details to a Tailwind page: hairline borders, numbered section eyebrows, sparing small-caps labels, 4% grain, baseline-aligned columns, one icon stroke width, a radius hierarchy, a brand focus ring and a real footer colophon. Use when a user says the page "looks vibe coded", "looks AI generated", "feels unfinished", or wants it "polished" or "professional".'
---

# Finishing details

A generated page is recognisable by what is missing, not by what is wrong: every border is `border-gray-200` at full strength, every corner is `rounded-lg`, icons come from three libraries at three stroke widths, the footer says "© 2026 All rights reserved" and nothing else. Handmade pages carry small, deliberate decisions in the places nobody is asked to look. Each detail below is cheap on its own; together they are the difference between "a layout" and "a design". Pick six, apply them everywhere, and do not add a seventh until the first six are consistent.

## Pattern

```css
/* input.css: tokens the details below depend on */
@import "tailwindcss";
@theme {
  --font-display: "Fraunces", ui-serif, Georgia, serif;
  --font-sans: "Geist", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "Geist Mono", ui-monospace, monospace;
  --color-ink: oklch(22% 0.01 60);
  --color-line: oklch(90% 0.01 60);
  --color-accent: oklch(55% 0.17 35);
  --radius-sm: 4px;   /* chips, inputs, tags */
  --radius-md: 8px;   /* buttons, inner panels */
  --radius-lg: 14px;  /* cards, dialogs: lg = md + padding */
}
/* Visible focus in the brand colour, once, for everything */
@layer base {
  :focus-visible { outline: 2px solid var(--color-accent); outline-offset: 3px; border-radius: var(--radius-sm); }
}
/* Grain: feTurbulence baked into a data URI, 4% opacity, no request, no image file */
@utility grain {
  position: relative;
  &::after {
    content: ""; position: absolute; inset: 0; pointer-events: none; opacity: 0.04; mix-blend-mode: multiply;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }
}
```

```html
<section class="grain border-t border-line/70 bg-stone-50 py-20 text-ink">
  <div class="mx-auto grid max-w-6xl gap-10 px-4 sm:px-6 lg:grid-cols-[1fr_2fr] lg:px-8">

    <!-- Numbered eyebrow in mono: cheap, specific, impossible to get from a template -->
    <div>
      <p class="font-mono text-xs text-stone-500 tabular-nums">01 / Overview</p>
      <h2 class="mt-3 font-display text-4xl font-medium tracking-tight text-balance">Ledgers that close themselves</h2>
    </div>

    <!-- Baseline alignment: both columns share one text size + leading, so lines sit on the same grid -->
    <div class="grid gap-8 text-[17px] leading-7 sm:grid-cols-2">
      <p class="text-stone-700">Every transaction is matched to its bank line within the hour. Unmatched ones go to a single queue, not an email thread.</p>
      <p class="text-stone-700">Month end took 11 days at Northwind Freight. It now takes 2, and the controller signs off from her phone.</p>
    </div>

    <!-- Hairline card: ring-1 ring-black/5 reads as a line, border-gray-200 reads as a box -->
    <article class="rounded-lg bg-white p-6 ring-1 ring-black/5 lg:col-start-2">
      <!-- Small-caps label: once per card at most, never on headings -->
      <p class="text-xs font-medium uppercase tracking-widest text-stone-500">Reconciliation</p>
      <div class="mt-4 flex items-center gap-3">
        <!-- One stroke width for every icon on the site: 1.5 -->
        <svg class="size-5 shrink-0 text-accent" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
        </svg>
        <p class="text-lg font-medium">1,284 lines matched</p>
      </div>
      <!-- Inner element uses the next radius down: 14px card, 8px button -->
      <a href="/queue" class="mt-6 inline-flex rounded-md bg-ink px-3.5 py-2 text-sm text-white hover:bg-stone-800">Open the queue</a>
    </article>
  </div>
</section>

<footer class="border-t border-line/70 py-10 text-sm text-stone-500">
  <div class="mx-auto flex max-w-6xl flex-wrap justify-between gap-4 px-4 sm:px-6 lg:px-8">
    <p>Northwind Ledger · Rotterdam · <a class="underline underline-offset-2 hover:text-ink" href="/changelog">v2.14, 18 Oct 2026</a></p>
    <!-- Colophon: a real sentence about how the site was made. Templates never have one. -->
    <p>Set in Fraunces and Geist. Built with plain HTML and Tailwind. No tracking.</p>
  </div>
</footer>
```

## Variations

- **Hairlines on dark.** `ring-1 ring-white/10` and `border-white/10`; at 70% opacity a hairline reads as a line, at 100% it reads as a box. Never `border-gray-700` on `bg-gray-900`, it is too close to a 1990s table.
- **Numbering across the page.** Give every top-level section its eyebrow (`01 / Overview`, `02 / Pricing`, `03 / Team`) and repeat the numbers in a sticky side index or the footer; the page then has a spine. Use `tabular-nums` so `09` and `10` line up.
- **Grain only on tinted surfaces.** On pure white it reads as dirt; on `bg-stone-50`, `bg-amber-50` or a dark hero it reads as paper or film. Keep opacity between 0.03 and 0.05 and `mix-blend-mode: multiply` (light) or `screen` (dark).
- **Focus ring per surface.** The base rule covers 95%; on a dark hero add `[&_:focus-visible]:outline-white` to the section so the ring stays visible.

## Pitfalls

- Small-caps labels on everything (nav, headings, buttons, cards) is the new gradient text; the technique works because it is rare. One per section, never on a `<h1>`-`<h3>`.
- Mixing icon sets mixes stroke widths (Heroicons 1.5, Lucide 2, Feather 2, Phosphor 1.5 to 2). Pick one set, set `stroke-width` explicitly on every `<svg>` and use one or two sizes (`size-4` inline, `size-5` in cards).
- Nested radii that do not follow `outer = inner + padding` look slightly wrong without anyone knowing why: a `rounded-2xl` card with `rounded-2xl` buttons inside. Three steps (4 / 8 / 14 px) is enough for a whole site.
- Baseline alignment breaks the moment two adjacent columns use different `leading-*`; pick one `text-size/leading` pair for body copy and never override it inside a grid.
- The `feTurbulence` data URI must be URL-encoded (`%3C`, `%23`) or it silently fails in some browsers; keep the tile at 120 to 200 px so it does not visibly repeat.
- A colophon with fake claims ("Carbon neutral", "Trusted by 10,000 teams") undoes the effect; write only what is true: fonts, stack, location, version, date.

## Related skills

- `web-design-borders-radius-dividers`
- `web-design-icons`
- `web-design-typography-system`
- `web-a11y-keyboard-and-focus`
- `web-craft-anti-generic-design`
- `web-craft-consistency-audit`
