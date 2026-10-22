---
name: web-ecommerce-reviews
description: Build product reviews for a static shop in Tailwind v4: rating summary with per-star bars that filter the list, sorting, accessible stars, escaped review text and a review form with photo upload. Use whenever a user asks for "reviews", "ratings", "stars", "customer reviews", "write a review" or "rating breakdown".
---

# Product reviews

Reviews persuade because they are mixed. A summary that shows 54 five-star and 6 one-star reviews, a filter that lets people read the one-star ones first, and a line saying how reviews are collected do more for trust than a wall of praise. On a static site the reviews live in a JSON file per product (exported from your review inbox or written by a moderation step), the page computes the average and distribution from that data, and new reviews go to a form endpoint for checking before they appear. Treat every review as untrusted text: render with `textContent` or an escape function, never raw HTML.

## Pattern

```html
<section id="reviews" aria-labelledby="reviews-title" class="mt-16 grid gap-10 lg:grid-cols-[18rem_1fr]">
  <div>
    <h2 id="reviews-title" class="text-2xl font-semibold tracking-tight">Reviews</h2>
    <p class="mt-3"><span data-avg class="text-4xl font-semibold tabular-nums"></span> <span class="text-stone-600">out of 5, <span data-count></span> reviews</span></p>
    <ul role="list" data-bars class="mt-4 space-y-1"></ul>
    <p class="mt-4 text-xs text-stone-600">We email a review link 14 days after delivery; those reviews carry "Verified purchase". We publish every review that follows our <a href="/review-policy/" class="underline underline-offset-2">review rules</a>, critical ones included.</p>
    <a href="#write-review" class="mt-4 inline-block rounded-md border border-stone-900 px-4 py-2 text-sm font-medium hover:bg-stone-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Write a review</a>
  </div>
  <div>
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-stone-200 pb-3">
      <p data-showing aria-live="polite" class="text-sm text-stone-600"></p>
      <label class="text-sm">Sort by
        <select data-sort class="ml-1 rounded-md border border-stone-300 px-2 py-1 focus-visible:outline-2 focus-visible:outline-stone-900">
          <option value="new">Newest</option><option value="high">Highest rated</option><option value="low">Lowest rated</option><option value="photos">With photos first</option>
        </select>
      </label>
    </div>
    <ol role="list" data-list class="divide-y divide-stone-200"></ol>
  </div>
</section>
```

```js
// /js/reviews.js  — data: [{ id, rating, title, body, author: "Mareike K.", date: "2026-09-18", verified: true, photos: ["/img/r/412-1.webp"] }]
const reviews = await fetch('/data/reviews/soledad-480.json').then((r) => (r.ok ? r.json() : [])).catch(() => []);
const lang = document.documentElement.lang || 'en';
const one = new Intl.NumberFormat(lang, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const day = new Intl.DateTimeFormat(lang, { dateStyle: 'medium' });
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const $ = (s) => document.querySelector(`#reviews [data-${s}]`);
let stars = 0;                                                 // 0 = all
let sort = 'new';

const counts = [5, 4, 3, 2, 1].map((n) => [n, reviews.filter((r) => r.rating === n).length]);
const avg = reviews.reduce((s, r) => s + r.rating, 0) / (reviews.length || 1);
$('avg').textContent = one.format(avg);
$('count').textContent = reviews.length;
$('bars').innerHTML = counts.map(([n, c]) => `
  <li><button type="button" data-stars="${n}" aria-pressed="false" class="grid w-full grid-cols-[3.5rem_1fr_2.5rem] items-center gap-2 rounded px-1 py-0.5 text-sm hover:bg-stone-100 aria-pressed:bg-stone-200 focus-visible:outline-2 focus-visible:outline-stone-900">
    <span>${n} star${n > 1 ? 's' : ''}</span>
    <span aria-hidden="true" class="h-2 rounded-full bg-stone-200"><span class="block h-full rounded-full bg-amber-500" style="width:${(c / (reviews.length || 1)) * 100}%"></span></span>
    <span class="text-right tabular-nums">${c}<span class="sr-only"> reviews</span></span>
  </button></li>`).join('');

const order = { new: (a, b) => b.date.localeCompare(a.date), high: (a, b) => b.rating - a.rating, low: (a, b) => a.rating - b.rating, photos: (a, b) => (b.photos?.length ?? 0) - (a.photos?.length ?? 0) };

function item(r) {
  return `<li class="py-6"><article aria-labelledby="rv-${r.id}">
    <p class="text-amber-600"><span aria-hidden="true">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</span><span class="sr-only">Rated ${r.rating} out of 5</span></p>
    <h3 id="rv-${r.id}" class="mt-1 font-medium">${esc(r.title)}</h3>
    <p class="mt-1 text-sm text-stone-600">${esc(r.author)} · <time datetime="${esc(r.date)}">${day.format(new Date(r.date))}</time>${r.verified ? ' · Verified purchase' : ''}</p>
    <p class="mt-3 max-w-prose whitespace-pre-line">${esc(r.body)}</p>
    ${r.photos?.length ? `<ul role="list" class="mt-3 flex gap-2">${r.photos.map((src, i) => `<li><a href="${esc(src)}" class="block rounded focus-visible:outline-2 focus-visible:outline-stone-900"><img src="${esc(src)}" width="80" height="80" loading="lazy" alt="Photo ${i + 1} from ${esc(r.author)}" class="size-20 rounded object-cover"></a></li>`).join('')}</ul>` : ''}
  </article></li>`;
}

function render() {
  const list = reviews.filter((r) => !stars || r.rating === stars).sort(order[sort]);
  $('list').innerHTML = list.map(item).join('');
  $('showing').textContent = stars ? `Showing ${list.length} ${stars}-star review${list.length === 1 ? '' : 's'}` : `Showing all ${list.length} reviews`;
  document.querySelectorAll('#reviews [data-stars]').forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.stars) === stars)));
}

$('bars').addEventListener('click', (e) => {
  const b = e.target.closest('[data-stars]');
  if (b) { const n = Number(b.dataset.stars); stars = stars === n ? 0 : n; render(); }   // second click clears
});
$('sort').addEventListener('change', (e) => { sort = e.target.value; render(); });
render();
```

The form posts to a form endpoint (a function, Netlify Forms, Formspree) and lands in moderation, never straight on the page:

```html
<form id="write-review" action="/api/reviews" method="post" enctype="multipart/form-data" class="mt-12 max-w-xl space-y-5">
  <h3 class="text-xl font-semibold">Review Finca La Soledad, 480 g</h3>
  <fieldset>
    <legend class="text-sm font-medium">Your rating</legend>
    <div class="mt-2 flex flex-wrap gap-2">
      <!-- Repeat for 4 Good, 3 Okay, 2 Poor, 1 Bad -->
      <label class="cursor-pointer rounded-md border border-stone-300 px-3 py-1.5 text-sm has-checked:border-stone-900 has-checked:bg-stone-900 has-checked:text-white has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-stone-900"><input type="radio" name="rating" value="5" required class="sr-only">★★★★★ <span>Excellent</span></label>
    </div>
  </fieldset>
  <p><label for="rv-title" class="block text-sm font-medium">Headline</label><input id="rv-title" name="title" required maxlength="80" class="mt-1 w-full rounded-md border border-stone-300 px-3 py-2"></p>
  <p><label for="rv-body" class="block text-sm font-medium">Your review</label><textarea id="rv-body" name="body" required minlength="20" rows="5" class="mt-1 w-full rounded-md border border-stone-300 px-3 py-2"></textarea></p>
  <p><label for="rv-photos" class="block text-sm font-medium">Photos (optional, up to 3, JPEG or PNG)</label><input id="rv-photos" name="photos" type="file" accept="image/jpeg,image/png,image/webp" multiple class="mt-1 block text-sm file:mr-3 file:rounded-md file:border-0 file:bg-stone-100 file:px-3 file:py-2"></p>
  <p class="text-xs text-stone-600">We show your first name and last initial. Reviews appear after we check them, usually within two working days.</p>
  <button class="rounded-md bg-stone-900 px-5 py-2.5 font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Send review</button>
</form>
```

## Variations

- **Shop replies**: add `reply: { body, date }` to a review and render it indented under the review as "Reply from Rösterei Lindner"; answering a 2-star review publicly is often the most persuasive thing on the page.
- **Rich results**: add `aggregateRating` and a few `review` objects to the Product JSON-LD from the same data, only when those reviews are visible on the page; see `web-seo-structured-data`.
- **Long lists**: render the first 10 and a "Show 10 more" button that appends and moves focus to the first new review heading; see `web-nav-pagination`.
- **Variant-aware**: store `variant: "dripper-02-charcoal"` and show "Bought: Charcoal, 02" under the author line; filter chips per variant help with fit and colour questions.

## Pitfalls

- In the EU, a shop that shows reviews must say whether and how it checks they come from real buyers, and fake, bought or selectively hidden reviews are banned commercial practice. The policy line under the summary is not decoration.
- `innerHTML` with raw review text is a stored XSS hole the day someone writes `<img onerror>`; escape every field, including author and photo URLs.
- Star glyphs read as "black star black star…" in screen readers: hide them with `aria-hidden` and give "Rated 4 out of 5" as text.
- Bars without numbers fail anyone who cannot judge widths; keep the count beside each bar and make the whole row the button so it has a real accessible name.
- Phone photos are 4 to 12 MB and carry GPS in EXIF. Resize and re-encode client side through a canvas before upload (which strips metadata) and cap files at 3; see `web-form-file-upload`.
- Hard-coding "4.8 from 312 reviews" in the buy box drifts from the list; compute both from the same JSON at build or load time.

## Related skills

- `web-page-product-detail`
- `web-form-file-upload`
- `web-form-choices`
- `web-seo-structured-data`
- `web-a11y-aria-patterns`
- `web-ecommerce-trust-and-conversion`
- `web-layout-testimonials`
