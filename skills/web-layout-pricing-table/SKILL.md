---
name: web-layout-pricing-table
description: Build a pricing section with two to four plan cards, a highlighted "recommended" plan, feature checklists and a monthly/yearly billing toggle driven by a few lines of vanilla JS, in Tailwind v4. Use whenever a user asks for pricing, plans, tiers, subscription options, "compare plans", or a "choose your plan" page.
---

# Pricing table

Pricing pages convert when the recommended plan is obvious, the price is the biggest number on the card, and switching billing period does not reflow the layout. Build the cards as a list, mark the featured plan with a ring and a badge instead of a different layout, and store both prices in `data-*` attributes so the toggle is pure JS with no template logic.

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="pricing-heading">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

    <div class="mx-auto max-w-2xl text-center">
      <h2 id="pricing-heading" class="text-3xl font-bold tracking-tight text-balance text-gray-900 sm:text-4xl dark:text-white">Simple pricing</h2>
      <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">Start free, upgrade when you need to.</p>
    </div>

    <!-- Billing toggle: a real switch, keyboard operable -->
    <div class="mt-8 flex items-center justify-center gap-3 text-sm font-medium">
      <span id="label-monthly" class="text-gray-900 dark:text-white">Monthly</span>
      <button id="billing-toggle" type="button" role="switch" aria-checked="false" aria-label="Bill yearly"
              class="relative inline-flex h-6 w-11 shrink-0 rounded-full bg-gray-300 transition-colors aria-checked:bg-blue-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:bg-gray-700">
        <span class="pointer-events-none absolute top-0.5 left-0.5 size-5 rounded-full bg-white shadow transition-transform motion-reduce:transition-none in-aria-checked:translate-x-5"></span>
      </button>
      <span id="label-yearly" class="text-gray-500">Yearly <span class="ml-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">save 20%</span></span>
    </div>

    <ul role="list" class="mt-12 grid gap-6 lg:grid-cols-3 lg:items-stretch">

      <li class="flex flex-col rounded-2xl p-8 ring-1 ring-gray-200 dark:ring-gray-800">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Starter</h3>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">For a personal site.</p>
        <p class="mt-6 flex items-baseline gap-1">
          <span class="text-4xl font-bold tracking-tight text-gray-900 tabular-nums dark:text-white" data-price data-monthly="0" data-yearly="0">$0</span>
          <span class="text-sm text-gray-500" data-period>/month</span>
        </p>
        <ul role="list" class="mt-8 space-y-3 text-sm text-gray-600 dark:text-gray-400">
          <li class="flex gap-3"><svg class="size-5 shrink-0 text-blue-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>1 site</li>
          <li class="flex gap-3"><svg class="size-5 shrink-0 text-blue-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>Community support</li>
        </ul>
        <a href="/signup?plan=starter" class="mt-auto block rounded-lg px-4 py-2.5 text-center text-sm font-semibold text-blue-600 ring-1 ring-blue-200 ring-inset hover:ring-blue-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">Get started</a>
      </li>

      <li class="relative flex flex-col rounded-2xl bg-gray-900 p-8 ring-2 ring-blue-600 lg:-my-4 lg:py-12 dark:bg-gray-950">
        <p class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold text-white">Most popular</p>
        <h3 class="text-lg font-semibold text-white">Pro</h3>
        <p class="mt-1 text-sm text-gray-400">For freelancers and small teams.</p>
        <p class="mt-6 flex items-baseline gap-1">
          <span class="text-4xl font-bold tracking-tight text-white tabular-nums" data-price data-monthly="15" data-yearly="12">$15</span>
          <span class="text-sm text-gray-400" data-period>/month</span>
        </p>
        <ul role="list" class="mt-8 space-y-3 text-sm text-gray-300">
          <li class="flex gap-3"><svg class="size-5 shrink-0 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>10 sites</li>
          <li class="flex gap-3"><svg class="size-5 shrink-0 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>Custom domains</li>
          <li class="flex gap-3"><svg class="size-5 shrink-0 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0z" clip-rule="evenodd"/></svg>Email support</li>
        </ul>
        <a href="/signup?plan=pro" class="mt-auto block rounded-lg bg-blue-600 px-4 py-2.5 text-center text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">Start free trial</a>
      </li>

      <!-- third plan: copy the Starter card, change data-monthly / data-yearly -->

    </ul>
    <p class="mt-6 text-center text-xs text-gray-500" aria-live="polite" id="billing-note">Billed monthly.</p>
  </div>
</section>

<script type="module">
  const toggle = document.getElementById('billing-toggle');
  const note = document.getElementById('billing-note');
  const fmt = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

  function render(yearly) {
    toggle.setAttribute('aria-checked', String(yearly));
    document.getElementById('label-monthly').classList.toggle('text-gray-500', yearly);
    document.getElementById('label-yearly').classList.toggle('text-gray-500', !yearly);
    for (const el of document.querySelectorAll('[data-price]')) {
      el.textContent = fmt.format(Number(yearly ? el.dataset.yearly : el.dataset.monthly));
    }
    note.textContent = yearly ? 'Billed yearly as one payment.' : 'Billed monthly.';
  }

  toggle.addEventListener('click', () => render(toggle.getAttribute('aria-checked') !== 'true'));
</script>
```

Why these choices:

- `role="switch"` + `aria-checked` on a real `<button>`: it is keyboard operable for free, and Tailwind's `aria-checked:` and `in-aria-checked:` variants style both the track and the knob from that one attribute, so CSS and state never disagree.
- Prices live in `data-monthly` / `data-yearly`; the monthly number is rendered in the HTML so the page is correct before JS runs.
- `tabular-nums` keeps the price width stable when the digits change; `flex flex-col` + `mt-auto` on the button pins every CTA to the same baseline regardless of feature count.
- The featured plan is the same card with `ring-2`, a dark background and `lg:-my-4 lg:py-12` so it pokes out above and below its neighbours on desktop only.
- `aria-live="polite"` on the billing note announces the period change to screen-reader users without reading every price.

## Variations

- **Two plans**: `sm:grid-cols-2 max-w-4xl mx-auto`; no need for the negative margin trick, just the ring and badge.
- **Four plans**: `sm:grid-cols-2 xl:grid-cols-4`, shrink padding to `p-6` and price to `text-3xl`; move the long feature list to a comparison table below (see `web-ui-data-table`).
- **Show the yearly total**: add a second `data-*` pair and a `<span data-total>` line like "$144 billed yearly", filled in `render()`.
- **Enterprise "Contact us" card**: replace the price with `<span class="text-4xl font-bold">Custom</span>` and skip `data-price` so the toggle ignores it.

## Pitfalls

- Styling the toggle with `peer-checked:` on a hidden checkbox breaks when the label text is on both sides; a `<button role="switch">` is simpler and announced correctly.
- Animating the price change (fade, slide) makes the number unreadable for a moment on every toggle. Swap instantly; animate only the switch knob.
- `-my-4` on the featured card at every breakpoint pushes it into the previous section on phones. Scope it to `lg:` as shown.
- A list of 12 features per card makes the cards tall and pushes the buttons out of view. Cap at 5 to 6 and link to a full comparison.
- Do not rely on color alone for the featured plan: the "Most popular" badge is required for colorblind users and for anyone on a monochrome display.
- Strike-through "was $20" prices need visually-hidden text (`<span class="sr-only">Previously</span>`) or screen readers read two prices with no context.

## Related skills

- `web-layout-landing-page`
- `web-ui-data-table`
- `web-ui-buttons`
- `web-form-choices`
- `web-js-state-and-render`
- `web-ui-badges-chips-tags`
