---
name: web-theme-corporate-clean
description: Drop a trustworthy B2B look onto a site in Tailwind v4: IBM Plex Sans and Plex Mono, a muted steel blue that is not Tailwind's blue-600, cool tinted greys, small radii, dense tables with tabular numbers and one overlay shadow. Use whenever a user says "corporate", "enterprise", "B2B", "SaaS dashboard", "professional", "trustworthy", "fintech", "admin panel" or "clean and serious".
---

# Corporate clean theme

Business software earns trust by being predictable: the same blue means "you can click this" everywhere, numbers line up, statuses read without colour, and nothing moves that does not need to. The usual failure is Tailwind's default `blue-600` on `gray-50` with `shadow-lg` cards, which looks like every starter kit. Shift the hue, drop the chroma, tint the greys toward it, and spend the design effort on density and alignment instead of decoration.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-sans: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;

  /* Cool neutrals tinted toward hue 245. */
  --color-paper:   oklch(99% 0.003 245);
  --color-paper-2: oklch(96.5% 0.006 245);   /* page chrome, table header */
  --color-ink:     oklch(23% 0.020 250);
  --color-ink-2:   oklch(47% 0.020 250);
  --color-line:    oklch(90% 0.008 245);      /* dividers between rows */
  --color-line-strong: oklch(62% 0.015 250);  /* input borders: 3.5:1, meets non-text contrast */

  /* Steel blue at chroma 0.13, not 0.24: Tailwind's blue-600 sits at hue 263. */
  --color-accent:      oklch(48% 0.13 245);
  --color-accent-deep: oklch(40% 0.12 248);
  --color-accent-tint: oklch(95% 0.025 245);

  --color-ok:  oklch(45% 0.11 155);  --color-ok-tint:  oklch(95% 0.04 155);
  --color-warn: oklch(48% 0.10 70);  --color-warn-tint: oklch(95% 0.05 85);
  --color-bad: oklch(48% 0.16 25);   --color-bad-tint: oklch(95% 0.03 25);

  --radius-*: initial;
  --radius-sm: 0.1875rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --shadow-*: initial;
  --shadow-overlay: 0 1px 2px oklch(23% 0.02 250 / 0.08), 0 8px 24px oklch(23% 0.02 250 / 0.12);

  --text-display: clamp(2rem, 1.6rem + 1.6vw, 3rem);
  --text-display--line-height: 1.1;
  --text-display--letter-spacing: -0.02em;
  --text-title: 1.25rem;
  --text-title--line-height: 1.3;
  --text-body: 0.9375rem;
  --text-body--line-height: 1.55;
  --text-table: 0.875rem;
  --text-table--line-height: 1.4;
  --text-label: 0.75rem;
  --text-label--line-height: 1.2;
}

@layer base {
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); font-size: var(--text-body); line-height: 1.55; }
  h1, h2, h3 { font-weight: 600; letter-spacing: -0.01em; text-wrap: balance; }
  table { font-variant-numeric: tabular-nums; }
  th { font-weight: 500; text-align: left; color: var(--color-ink-2); }
  a { color: var(--color-accent); text-underline-offset: 2px; }
  a:hover { color: var(--color-accent-deep); }
  :focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
  input, select { border: 1px solid var(--color-line-strong); border-radius: var(--radius-md); background: var(--color-paper); }
}
```

```html
<section class="mx-auto max-w-6xl px-4 py-10 sm:px-6">
  <div class="flex flex-wrap items-end gap-4">
    <div>
      <h2 class="text-title">Invoices</h2>
      <p class="text-ink-2">Halvard Logistics · Q3 2026 · 4 of 128 shown</p>
    </div>
    <label class="ml-auto text-label text-ink-2">Status
      <select class="mt-1 block h-9 px-2 text-table text-ink"><option>All</option><option>Overdue</option></select>
    </label>
    <button class="h-9 rounded-md bg-accent px-4 text-table font-medium text-paper hover:bg-accent-deep">New invoice</button>
  </div>
  <div class="mt-6 overflow-x-auto rounded-lg border border-line">
    <table class="w-full min-w-[40rem] text-table">
      <thead class="bg-paper-2"><tr class="border-b border-line">
        <th class="px-4 py-2.5">Number</th><th class="px-4 py-2.5">Customer</th><th class="px-4 py-2.5">Due</th><th class="px-4 py-2.5 text-right">Amount</th><th class="px-4 py-2.5">Status</th>
      </tr></thead>
      <tbody class="divide-y divide-line">
        <tr class="hover:bg-accent-tint"><td class="px-4 py-2.5 font-mono"><a href="/invoices/INV-30412">INV-30412</a></td><td class="px-4 py-2.5">Brennan Cold Storage</td><td class="px-4 py-2.5">14 Oct</td><td class="px-4 py-2.5 text-right">€18,240.00</td><td class="px-4 py-2.5"><span class="rounded-sm bg-bad-tint px-1.5 py-0.5 text-label font-medium text-bad">Overdue 8 d</span></td></tr>
        <tr class="hover:bg-accent-tint"><td class="px-4 py-2.5 font-mono"><a href="/invoices/INV-30418">INV-30418</a></td><td class="px-4 py-2.5">Okafor Maritime</td><td class="px-4 py-2.5">29 Oct</td><td class="px-4 py-2.5 text-right">€4,975.50</td><td class="px-4 py-2.5"><span class="rounded-sm bg-warn-tint px-1.5 py-0.5 text-label font-medium text-warn">Due in 7 d</span></td></tr>
        <tr class="hover:bg-accent-tint"><td class="px-4 py-2.5 font-mono"><a href="/invoices/INV-30425">INV-30425</a></td><td class="px-4 py-2.5">Vestergaard Agri</td><td class="px-4 py-2.5">2 Oct</td><td class="px-4 py-2.5 text-right">€61,300.00</td><td class="px-4 py-2.5"><span class="rounded-sm bg-ok-tint px-1.5 py-0.5 text-label font-medium text-ok">Paid</span></td></tr>
        <tr class="hover:bg-accent-tint"><td class="px-4 py-2.5 font-mono"><a href="/invoices/INV-30431">INV-30431</a></td><td class="px-4 py-2.5">Lindqvist &amp; Ruiz</td><td class="px-4 py-2.5">6 Nov</td><td class="px-4 py-2.5 text-right">€742.10</td><td class="px-4 py-2.5"><span class="rounded-sm bg-paper-2 px-1.5 py-0.5 text-label font-medium text-ink-2">Draft</span></td></tr>
      </tbody>
    </table>
  </div>
</section>
```

What this theme does: one family in three weights (400 body, 500 labels and buttons, 600 headings), mono only for IDs and codes, tabular numbers right-aligned in every table, 40px row height with 1px dividers and no zebra, status as a word on a tint (never colour alone), blue only on the primary button, links, focus and hover rows, radii from 3px on chips to 8px on containers, one `shadow-overlay` for menus and dialogs and nothing else.

What it never does: Tailwind's `blue-600` or `indigo-*`, gradients, cards with `shadow-lg`, illustrations of people at laptops, more than one primary button per view, centred tables, icons without labels in toolbars, hero headlines over 48px, status dots without text, grey text below 4.5:1 for "subtle" metadata.

## Variations

- **Brand hue**: keep the lightness and chroma, change only the hue. Teal at `190`, slate-indigo at `265` with chroma `0.10`; re-run contrast for `accent` on `paper` after any change.
- **Dark mode**: `paper` to `oklch(19% 0.012 250)`, `paper-2` to `oklch(23% 0.014 250)`, `ink` to `oklch(94% 0.006 245)`, `accent` to `oklch(72% 0.11 245)`; `text-paper` on the button still passes because paper is now the dark value. Override under `.dark` (see `web-design-dark-mode`).
- **Comfortable density**: a `[data-density="comfortable"]` wrapper that sets `--text-table: 0.9375rem` and swaps `py-2.5` for `py-3.5`; let users choose, do not guess.
- **Marketing pages**: same tokens, `text-display` for the one hero headline, product screenshots in a `rounded-lg border border-line` frame instead of floating with a shadow.

## Pitfalls

- `line` at 90% is fine for row dividers but fails 3:1 as an input border; inputs and checkboxes use `line-strong`.
- Row hover with `bg-accent-tint` must not be the only selected state; selected rows also need a checkbox or `aria-selected` plus a left border.
- `overflow-x-auto` around the table with `min-w-[40rem]` is what keeps phones working; without it the page scrolls sideways.
- Tabular numbers only right-align properly with the same decimal count; format with `Intl.NumberFormat` and `minimumFractionDigits: 2`.
- Warn amber at the usual 70% lightness is 2.3:1 as text; this theme darkens it to 48% so "Due in 7 d" passes on its tint.
- `--shadow-*: initial` removes `shadow-sm` from third-party widgets styled with Tailwind; give them `shadow-overlay` or a border.

## Related skills

- `web-craft-color-with-restraint`
- `web-ui-data-table`
- `web-ui-badges-chips-tags`
- `web-layout-dashboard-sidebar`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-theme-switcher`
