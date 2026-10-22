---
name: web-page-product-detail
description: 'Build an e-commerce product page in Tailwind v4: breadcrumbs, an image gallery with thumbnail switching, a sticky buy box with price, variants as radio groups and add-to-cart, a specs table, reviews and related products, with Product JSON-LD. Use whenever a user asks for a product page, shop page, product detail, PDP, "item page" or a buy page.'
---

# Product detail page

A product page is a decision made in this order: is this the thing (images), what does it cost and can I have it in my size (buy box), is it any good (details, specs, reviews). The gallery and buy box share the first screen in a `1.1fr_0.9fr` split; the buy box sticks while the gallery scrolls so the price and button are always in reach. Everything below the fold is in reading order, left-aligned, with a specs `<table>` rather than a bullet soup. On phones the buy box collapses under the gallery and a slim bottom bar repeats price and button.

## Pattern

```html
<main id="main" class="mx-auto max-w-7xl px-4 pb-24 pt-6 sm:px-6 lg:px-8 lg:pb-16">
  <nav aria-label="Breadcrumb" class="text-sm text-stone-500">...web-nav-breadcrumbs: Home / Furniture / Side tables...</nav>

  <div class="mt-6 grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:gap-16">

    <!-- 1. Gallery: one large image, thumbnails as buttons. Column one in DOM and on screen. -->
    <section aria-label="Product images" data-gallery>
      <img src="/img/p/oak-side-table-1.webp" width="1200" height="1200" fetchpriority="high" alt="Oak side table, 45 cm, with a single drawer, on a pale floor" class="aspect-square w-full rounded-lg bg-stone-100 object-cover" data-gallery-main>
      <ul role="list" class="mt-3 grid grid-cols-5 gap-3">
        <li><button type="button" aria-pressed="true" data-src="/img/p/oak-side-table-1.webp" data-alt="Oak side table, 45 cm, with a single drawer, on a pale floor" class="block w-full rounded-md border-2 border-transparent aria-pressed:border-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900"><img src="/img/p/oak-side-table-1-thumb.webp" width="200" height="200" alt="Front view" class="aspect-square w-full rounded object-cover"></button></li>
        <li><button type="button" aria-pressed="false" data-src="/img/p/oak-side-table-2.webp" data-alt="Drawer open, showing dovetail joints" class="block w-full rounded-md border-2 border-transparent aria-pressed:border-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900"><img src="/img/p/oak-side-table-2-thumb.webp" width="200" height="200" loading="lazy" alt="Drawer open" class="aspect-square w-full rounded object-cover"></button></li>
        <li><button type="button" aria-pressed="false" data-src="/img/p/oak-side-table-3.webp" data-alt="Side table beside a grey sofa for scale" class="block w-full rounded-md border-2 border-transparent aria-pressed:border-stone-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900"><img src="/img/p/oak-side-table-3-thumb.webp" width="200" height="200" loading="lazy" alt="In a room" class="aspect-square w-full rounded object-cover"></button></li>
      </ul>
    </section>

    <!-- 2. Buy box: sticky from lg. Title, price, variants, button, delivery facts. -->
    <section aria-labelledby="product-title" class="lg:sticky lg:top-24 lg:self-start">
      <p class="text-sm text-stone-500">Hale Furniture</p>
      <h1 id="product-title" class="mt-1 text-3xl font-semibold tracking-tight">Oak side table, 45 cm</h1>
      <p class="mt-2 text-sm"><a href="#reviews" class="underline underline-offset-4">4.7 out of 5 · 128 reviews</a></p>
      <p class="mt-5 text-2xl font-semibold tabular-nums" data-price>£240</p>

      <form action="/cart/add" method="post" class="mt-6 space-y-6" data-buy>
        <fieldset>
          <legend class="text-sm font-medium">Finish</legend>
          <div class="mt-2 flex flex-wrap gap-2">
            <label class="cursor-pointer rounded-md border border-stone-300 px-3 py-2 text-sm has-checked:border-stone-900 has-checked:bg-stone-900 has-checked:text-white"><input type="radio" name="finish" value="natural" data-price="240" checked class="sr-only">Natural oil</label>
            <label class="cursor-pointer rounded-md border border-stone-300 px-3 py-2 text-sm has-checked:border-stone-900 has-checked:bg-stone-900 has-checked:text-white"><input type="radio" name="finish" value="black" data-price="260" class="sr-only">Black stain (+£20)</label>
          </div>
        </fieldset>
        <fieldset>
          <legend class="text-sm font-medium">Drawer</legend>
          <div class="mt-2 flex flex-wrap gap-2">
            <label class="cursor-pointer rounded-md border border-stone-300 px-3 py-2 text-sm has-checked:border-stone-900 has-checked:bg-stone-900 has-checked:text-white"><input type="radio" name="drawer" value="left" checked class="sr-only">Opens left</label>
            <label class="cursor-pointer rounded-md border border-stone-300 px-3 py-2 text-sm has-checked:border-stone-900 has-checked:bg-stone-900 has-checked:text-white"><input type="radio" name="drawer" value="right" class="sr-only">Opens right</label>
          </div>
        </fieldset>
        <input type="hidden" name="sku" value="HF-ST45">
        <button type="submit" class="w-full rounded-md bg-stone-900 px-5 py-3 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Add to basket</button>
      </form>

      <dl class="mt-6 grid grid-cols-[7rem_1fr] gap-y-2 border-t border-stone-200 pt-5 text-sm">
        <dt class="text-stone-500">Delivery</dt><dd>Free in the UK, 5 to 8 working days. Made to order in Sheffield.</dd>
        <dt class="text-stone-500">Returns</dt><dd>30 days, we collect.</dd>
        <dt class="text-stone-500">In stock</dt><dd>Ships <time datetime="2026-03-27">27 March</time></dd>
      </dl>
    </section>
  </div>

  <!-- 3. Details, specs, reviews: a narrow reading column at the left edge -->
  <section aria-labelledby="details-heading" class="mt-20 max-w-[65ch] border-t border-stone-200 pt-10">
    <h2 id="details-heading" class="text-2xl font-semibold tracking-tight">Details</h2>
    <p class="mt-4 leading-relaxed text-stone-700">Solid European oak from FSC-certified forests, 22 mm top, dovetailed drawer that runs on waxed wood, no plastic runners. Finished with hardwax oil you can re-apply yourself.</p>
  </section>

  <section aria-labelledby="specs-heading" class="mt-14 max-w-[65ch]">
    <h2 id="specs-heading" class="text-2xl font-semibold tracking-tight">Specifications</h2>
    <table class="mt-4 w-full text-sm">
      <tbody class="divide-y divide-stone-200">
        <tr><th scope="row" class="py-2 pr-4 text-left font-medium text-stone-500">Dimensions</th><td class="py-2">45 × 40 × 55 cm (W × D × H)</td></tr>
        <tr><th scope="row" class="py-2 pr-4 text-left font-medium text-stone-500">Weight</th><td class="py-2">9.4 kg</td></tr>
        <tr><th scope="row" class="py-2 pr-4 text-left font-medium text-stone-500">Material</th><td class="py-2">European oak, FSC C012345</td></tr>
        <tr><th scope="row" class="py-2 pr-4 text-left font-medium text-stone-500">Drawer</th><td class="py-2">38 × 32 × 9 cm internal</td></tr>
      </tbody>
    </table>
  </section>

  <section id="reviews" aria-labelledby="reviews-heading" class="mt-14 max-w-[65ch] scroll-mt-24">
    <h2 id="reviews-heading" class="text-2xl font-semibold tracking-tight">128 reviews, 4.7 average</h2>
    <ul role="list" class="mt-6 divide-y divide-stone-200">
      <li class="py-6">
        <p class="text-sm"><span aria-label="5 out of 5 stars">★★★★★</span> · Fatima K., Bristol · <time datetime="2026-02-11">11 Feb 2026</time></p>
        <p class="mt-2 text-stone-700">Heavier than it looks in the photos, which is what I wanted. The drawer sticks slightly in damp weather; a bit of candle wax sorted it.</p>
      </li>
    </ul>
    <nav aria-label="Reviews pagination" class="mt-6 text-sm">...web-nav-pagination...</nav>
  </section>

  <!-- 4. Related -->
  <section aria-labelledby="related-heading" class="mt-20 border-t border-stone-200 pt-10">
    <h2 id="related-heading" class="text-2xl font-semibold tracking-tight">Goes with</h2>
    <ul role="list" class="mt-6 grid grid-cols-2 gap-6 lg:grid-cols-4">...web-layout-card-grid...</ul>
  </section>

  <!-- 5. Mobile bar: price and button repeated, fixed bottom, gone from lg -->
  <div class="fixed inset-x-0 bottom-0 flex items-center justify-between gap-4 border-t border-stone-200 bg-white px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] lg:hidden">
    <p class="font-semibold tabular-nums" data-price>£240</p>
    <button type="submit" form="buy-form" class="rounded-md bg-stone-900 px-5 py-2.5 text-sm font-medium text-white">Add to basket</button>
  </div>
</main>
```

Give the form `id="buy-form"` so the mobile bar's button submits it. Thumbnail switching and the variant price:

```js
const gallery = document.querySelector('[data-gallery]');
const main = gallery.querySelector('[data-gallery-main]');
gallery.addEventListener('click', (event) => {
  const thumb = event.target.closest('button[data-src]');
  if (!thumb) return;
  main.src = thumb.dataset.src;
  main.alt = thumb.dataset.alt;
  for (const b of gallery.querySelectorAll('button[data-src]')) b.setAttribute('aria-pressed', String(b === thumb));
});

const form = document.querySelector('[data-buy]');
form.addEventListener('change', () => {
  const chosen = form.querySelector('input[name=finish]:checked');
  const price = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(chosen.dataset.price);
  for (const el of document.querySelectorAll('[data-price]')) el.textContent = price;
});
```

Meta: `Product` JSON-LD with `name`, `image` (all gallery URLs), `sku`, `brand`, `offers` (`price`, `priceCurrency`, `availability`, `url`) and `aggregateRating`, via `web-seo-structured-data`. `og:image` is the first gallery image.

## Variations

- **Swatches instead of text chips**: colour variants as `size-8 rounded-full` labels with `has-checked:ring-2 has-checked:ring-offset-2`; keep the colour name in `sr-only` text inside the label.
- **Out of stock variant**: add `disabled` to the radio and `has-disabled:line-through has-disabled:opacity-50` to its label; show "Email me when back" under the button instead of hiding it.
- **Digital or single-variant product**: drop the fieldsets; the buy box is title, price, one paragraph, button, and the gallery can become a single `aspect-video` screenshot.
- **Long description**: put Details, Specs and Reviews into `web-nav-tabs` only when each is longer than a screen; stacked sections are easier to find and better for search.

## Pitfalls

- Thumbnails as `<div onclick>` are unreachable by keyboard and screen readers; they are `<button>`s with `aria-pressed`.
- Swapping `main.src` without `width`/`height` on the image causes a layout jump when the new image has a different ratio; serve all gallery images at the same ratio.
- The sticky buy box overlaps the footer on short pages if it is taller than the viewport; cap it with `lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto`.
- The fixed mobile bar covers the last content unless `<main>` has bottom padding (`pb-24`) and the bar respects `env(safe-area-inset-bottom)`.
- Price updated only in one place leaves the mobile bar stale; both `[data-price]` elements are updated by the same loop.
- Reviews with five identical five-star quotes and first-name-only authors read as fake; show the distribution and keep the 3-star review with the damp-drawer note.

## Related skills

- `web-nav-breadcrumbs`
- `web-form-choices`
- `web-ui-data-table`
- `web-nav-pagination`
- `web-layout-card-grid`
- `web-seo-structured-data`
- `web-css-sticky-and-fixed`
- `web-css-aspect-ratio-media`
