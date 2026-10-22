---
name: web-craft-real-content
description: 'Design around real content, not placeholders: no lorem ipsum, "John Doe" or "Acme Inc"; believable data (varied names, specific numbers, real dates), real product screenshots not grey boxes, licensed photos, and layouts that survive 3-word or 14-word headlines. Use when a user says the demo "looks fake", "looks AI generated", "make it feel real" or "replace the placeholder text".'
---

# Real content

Placeholder content is the loudest tell of a generated page. "Jane Smith, CEO at Acme" with a grey circle avatar, "$1,000" prices, "Lorem ipsum dolor" under every heading, a `placehold.co/600x400` where the product should be: readers decode these instantly as "nobody has used this yet". Worse, placeholders hide layout bugs, because fake text is always the convenient length. Design with the real headline, the real 47-character customer name and the real screenshot from the start, and the layout earns its decisions.

## Pattern

Sample data that reads as real: specific, varied, internally consistent.

```js
// /js/data/sample.js: one source for every demo, so names and numbers agree across the page
export const customers = [
  { name: 'Priya Raghunathan', role: 'Head of Finance', company: 'Lumen Bikes', city: 'Leeds',
    quote: 'We closed September in two days. The previous record was nine.', since: '2024-03-11' },
  { name: 'Tomasz Wierzbicki', role: 'Co-founder', company: 'Fjord Print Co.', city: 'Gdańsk',
    quote: 'The bank feed catches duplicates before I even open the app.', since: '2025-01-27' },
  { name: 'Adaeze Okonkwo-Hale', role: 'Controller', company: 'Marrow & Rye', city: 'Austin',
    quote: 'I stopped exporting to spreadsheets. That alone is worth the fee.', since: '2023-11-02' },
];

export const invoices = [
  { id: 'INV-2026-0418', customer: 'Lumen Bikes',     amount: 1284.00, currency: 'GBP', due: '2026-11-04', status: 'open' },
  { id: 'INV-2026-0417', customer: 'Fjord Print Co.', amount: 9340.50, currency: 'PLN', due: '2026-10-29', status: 'paid' },
  { id: 'INV-2026-0416', customer: 'Marrow & Rye',    amount:  312.75, currency: 'USD', due: '2026-10-15', status: 'overdue' },
];

export const money = (n, currency) =>
  new Intl.NumberFormat('en-GB', { style: 'currency', currency, maximumFractionDigits: 2 }).format(n);
export const date = (iso) =>
  new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso));
```

```html
<!-- Testimonial that survives real content: long name, long company, long quote -->
<figure class="flex flex-col gap-5 rounded-lg bg-white p-6 ring-1 ring-black/5">
  <blockquote class="text-pretty text-lg leading-7 text-stone-800">
    “We closed September in two days. The previous record was nine.”
  </blockquote>
  <figcaption class="mt-auto flex items-center gap-3">
    <!-- A real photo by exact Unsplash id, sized, with the required credit in the alt or a caption -->
    <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=96&h=96&fit=crop&crop=faces&q=80"
         width="48" height="48" alt="" loading="lazy" class="size-12 rounded-full object-cover">
    <div class="min-w-0">
      <p class="truncate font-medium text-stone-900">Priya Raghunathan</p>
      <p class="truncate text-sm text-stone-500">Head of Finance, Lumen Bikes · Leeds</p>
    </div>
  </figcaption>
</figure>

<!-- Product "screenshot": the real UI, built in HTML, so it is sharp, themable and says what the product does -->
<div class="overflow-hidden rounded-lg bg-white ring-1 ring-black/10 shadow-xl shadow-stone-900/10" aria-label="Invoices screen">
  <div class="flex items-center gap-1.5 border-b border-stone-200/70 px-4 py-2.5">
    <span class="size-2.5 rounded-full bg-stone-300"></span><span class="size-2.5 rounded-full bg-stone-300"></span><span class="size-2.5 rounded-full bg-stone-300"></span>
    <span class="ml-3 font-mono text-xs text-stone-400">app.northwind.ledger/invoices</span>
  </div>
  <table class="w-full text-sm">
    <thead class="text-left text-xs uppercase tracking-wide text-stone-500">
      <tr class="border-b border-stone-200/70 *:px-4 *:py-2"><th>Invoice</th><th>Customer</th><th class="text-right">Amount</th><th>Due</th><th>Status</th></tr>
    </thead>
    <tbody class="divide-y divide-stone-200/70 *:*:px-4 *:*:py-2.5">
      <tr><td class="font-mono text-xs">INV-2026-0418</td><td>Lumen Bikes</td><td class="text-right tabular-nums">£1,284.00</td><td>4 Nov 2026</td><td><span class="rounded-sm bg-amber-50 px-1.5 py-0.5 text-xs text-amber-800">Open</span></td></tr>
      <tr><td class="font-mono text-xs">INV-2026-0416</td><td>Marrow &amp; Rye</td><td class="text-right tabular-nums">$312.75</td><td>15 Oct 2026</td><td><span class="rounded-sm bg-red-50 px-1.5 py-0.5 text-xs text-red-800">Overdue</span></td></tr>
    </tbody>
  </table>
</div>
```

## Variations

- **Credible screenshot, three ways.** (1) Render the real app and capture it at 2x (`npx playwright screenshot --viewport-size=1280,800 --device-scale-factor=2 http://localhost:3000/invoices shot.png`). (2) Build the key screen in HTML as above and ship it live: it is sharper than any PNG and updates with the brand. (3) If you must use an image, capture your own HTML mock, never a stock "dashboard" render.
- **Photos.** Unsplash by a specific photo id with `?w=&h=&fit=crop&q=80`, chosen for the subject (a person at a desk in a bike shop, not "business team high-five"). Unsplash licence allows commercial use without attribution, but credit in a caption anyway when the photo is a person. Never `source.unsplash.com/random` or `picsum.photos`: a different image per load is a bug, not a feature.
- **Headline length.** Write the real one, then test the layout with a 3-word version ("Ledgers that close") and a 14-word version. Hero headings: `text-balance max-w-[20ch]` so neither leaves an orphan. If the 14-word one breaks the split layout, the grid needs `items-start`, not a shorter headline.
- **Numbers.** Stats blocks use the actual metric and precision: "2,184 invoices matched", "11 d → 2 d", "99.2% uptime over 90 days", never "10,000+ users" or "99.99%". If there is no real number yet, drop the stats block; an empty claim reads worse than no claim.

## Pitfalls

- Names from one culture, or the AI defaults (Sarah Johnson, Michael Chen, Emily Davis, Alex Rivera) are as recognisable as John Doe. Mix origins, lengths, double-barrelled surnames, and give each person a city and a specific role title.
- Round numbers ("$1,000", "500 customers", "50% faster") read as invented; real data has `$1,284`, `487`, `38%`. Format with `Intl.NumberFormat`, show currency, use `tabular-nums` in tables.
- Grey rectangle "screenshots" and `bg-gray-200 aspect-video` boxes announce that the product does not exist. Either show the product or restructure the section so it needs no image (a feature list, a quote, a diagram in SVG).
- Lorem ipsum hides overflow bugs: Latin words are 5 to 7 letters and never contain a 34-character URL or a German compound noun. Test with the real strings, including the longest one from the database.
- Fake logos ("Logoipsum", grey wordmarks) in a "trusted by" row are the worst case: an unverifiable claim rendered in placeholder form. No logo row until there are at least four real, permitted logos.
- Sample data that disagrees with itself (a testimonial from "Lumen Bikes" and an invoice to "Lumen Bicycles", a date in 2023 on a product launched in 2025) is noticed by exactly the careful readers you want. Keep one data module and import from it.

## Related skills

- `web-craft-copy-that-sounds-human`
- `web-craft-anti-generic-design`
- `web-layout-testimonials`
- `web-design-images`
- `web-ui-data-table`
- `web-design-empty-and-error-states`
