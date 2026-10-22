---
name: web-page-about-team
description: 'Build an "about us" or team page in Tailwind v4: an origin story with real dates and numbers, a sticky-heading values list, a team grid, a timeline, a press row and a contact row. Use whenever a user asks for an about page, about us, "our story", company page, team page, "meet the team" or who-we-are page.'
---

# About and team page

An about page is read by three people: a prospective customer checking you are real, a candidate checking who they would work with, and a journalist looking for a fact. Order the page for them: who you are in one sentence, the origin with dates and numbers, what you believe (as a list with a sticky heading, not icon cards), the people, the timeline, press, and how to reach you. Everything aligns to one left edge; the only centred thing on the page is nothing.

## Pattern

```html
<main id="main" class="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">

  <!-- 1. Who we are: one sentence, one photo, 1.2/0.8 -->
  <header class="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
    <div class="max-w-[40rem]">
      <h1 class="text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl">We make the scheduling software behind 2,300 independent pharmacies.</h1>
      <p class="mt-5 text-lg leading-relaxed text-stone-600">Lundqvist Health started in 2017 when two pharmacists in Malmö got tired of a paper rota. Today 41 people in Malmö, Leeds and Porto look after it.</p>
    </div>
    <img src="/img/about/malmo-office.webp" width="1000" height="750" alt="The Malmö office, a converted pharmacy with the original counter" class="aspect-[4/3] w-full rounded-lg object-cover">
  </header>

  <!-- 2. Numbers: four figures, left-aligned under a hairline -->
  <dl class="mt-20 grid grid-cols-2 gap-8 border-t border-stone-200 pt-8 lg:grid-cols-4">
    <div><dt class="text-sm text-stone-500">Pharmacies</dt><dd class="mt-1 text-3xl font-semibold tabular-nums">2,312</dd></div>
    <div><dt class="text-sm text-stone-500">Shifts scheduled</dt><dd class="mt-1 text-3xl font-semibold tabular-nums">4.8M</dd></div>
    <div><dt class="text-sm text-stone-500">People</dt><dd class="mt-1 text-3xl font-semibold tabular-nums">41</dd></div>
    <div><dt class="text-sm text-stone-500">Founded</dt><dd class="mt-1 text-3xl font-semibold tabular-nums">2017</dd></div>
  </dl>

  <!-- 3. Values: sticky heading beside a numbered list. Sentences, not nouns. -->
  <section aria-labelledby="values-heading" class="mt-24 grid gap-10 border-t border-stone-200 pt-12 lg:grid-cols-[1fr_2fr]">
    <h2 id="values-heading" class="text-3xl font-semibold tracking-tight lg:sticky lg:top-24 lg:self-start">How we work</h2>
    <ol class="divide-y divide-stone-200">
      <li class="grid gap-4 py-8 sm:grid-cols-[4rem_1fr]">
        <span class="font-mono text-sm text-stone-500">01</span>
        <div><h3 class="font-semibold">A pharmacist answers support</h3><p class="mt-1 max-w-[55ch] text-stone-600">Every support shift has at least one registered pharmacist on it. Median first reply: 11 minutes.</p></div>
      </li>
      <li class="grid gap-4 py-8 sm:grid-cols-[4rem_1fr]">
        <span class="font-mono text-sm text-stone-500">02</span>
        <div><h3 class="font-semibold">No feature ships without a rota test</h3><p class="mt-1 max-w-[55ch] text-stone-600">Three partner pharmacies run every release for a week before anyone else sees it.</p></div>
      </li>
      <li class="grid gap-4 py-8 sm:grid-cols-[4rem_1fr]">
        <span class="font-mono text-sm text-stone-500">03</span>
        <div><h3 class="font-semibold">We publish our uptime and our prices</h3><p class="mt-1 max-w-[55ch] text-stone-600">Both are on the site. Last year: 99.97% and no price change.</p></div>
      </li>
    </ol>
  </section>

  <!-- 4. Team: photo, name, role. Leadership first, then alphabetical. -->
  <section aria-labelledby="team-heading" class="mt-24 border-t border-stone-200 pt-12">
    <div class="max-w-[40rem]">
      <h2 id="team-heading" class="text-3xl font-semibold tracking-tight">The people</h2>
      <p class="mt-3 text-stone-600">41 of us. These are the ones who agreed to a photo.</p>
    </div>
    <ul role="list" class="mt-10 grid grid-cols-2 gap-x-6 gap-y-10 sm:grid-cols-3 lg:grid-cols-4">
      <li>
        <img src="/img/team/ingrid-lundqvist.webp" width="400" height="500" loading="lazy" alt="" class="aspect-[4/5] w-full rounded-lg object-cover">
        <h3 class="mt-3 font-medium">Ingrid Lundqvist</h3>
        <p class="text-sm text-stone-600">Co-founder, CEO · Malmö</p>
      </li>
      <li>
        <img src="/img/team/dayo-adeyemi.webp" width="400" height="500" loading="lazy" alt="" class="aspect-[4/5] w-full rounded-lg object-cover">
        <h3 class="mt-3 font-medium">Dayo Adeyemi</h3>
        <p class="text-sm text-stone-600">Head of engineering · Leeds</p>
      </li>
      <li>...</li>
    </ul>
    <p class="mt-10"><a href="/careers" class="font-medium underline underline-offset-4">Four open roles in Porto and remote</a></p>
  </section>

  <!-- 5. Timeline: year column, event column -->
  <section aria-labelledby="timeline-heading" class="mt-24 grid gap-10 border-t border-stone-200 pt-12 lg:grid-cols-[1fr_2fr]">
    <h2 id="timeline-heading" class="text-3xl font-semibold tracking-tight lg:sticky lg:top-24 lg:self-start">Since 2017</h2>
    <ol class="divide-y divide-stone-200">
      <li class="grid grid-cols-[5rem_1fr] gap-4 py-5"><time class="font-mono text-sm text-stone-500">2017</time><p>First rota live at Apoteket Söder, Malmö.</p></li>
      <li class="grid grid-cols-[5rem_1fr] gap-4 py-5"><time class="font-mono text-sm text-stone-500">2019</time><p>100 pharmacies. Leeds office opens with three people.</p></li>
      <li class="grid grid-cols-[5rem_1fr] gap-4 py-5"><time class="font-mono text-sm text-stone-500">2023</time><p>NHS Scotland framework. 1,000th pharmacy.</p></li>
      <li class="grid grid-cols-[5rem_1fr] gap-4 py-5"><time class="font-mono text-sm text-stone-500">2026</time><p>Porto office. 2,300 pharmacies, 41 people.</p></li>
    </ol>
  </section>

  <!-- 6. Press and contact: one row, two columns -->
  <section aria-labelledby="press-heading" class="mt-24 grid gap-10 border-t border-stone-200 pt-12 lg:grid-cols-[1fr_2fr]">
    <h2 id="press-heading" class="text-3xl font-semibold tracking-tight">Press</h2>
    <div class="max-w-[55ch]">
      <ul class="space-y-2 text-stone-600">
        <li><a href="https://example.com/article" class="underline underline-offset-4">Pharmacy Business, Feb 2026</a>: "The rota tool that pharmacists actually like"</li>
        <li><a href="/press/lundqvist-press-kit.zip" class="underline underline-offset-4">Press kit</a> (logos, founder photos, 2.1 MB)</li>
      </ul>
      <p class="mt-6">Journalists: <a href="mailto:press@lundqvist.health" class="underline underline-offset-4">press@lundqvist.health</a>, answered within one working day.</p>
    </div>
  </section>
</main>
```

No JavaScript is needed. For animated numbers see `web-motion-counters-and-tickers`; keep the static value in the HTML.

Meta: `Organization` JSON-LD (name, url, logo, foundingDate, address, sameAs) and, for founders who are public, `Person` entries, via `web-seo-structured-data`. `og:image` is the office or team photo, not the logo.

## Variations

- **Solo or two-person studio**: drop the numbers and timeline, make the team section a `lg:grid-cols-[0.8fr_1.2fr]` portrait beside a longer bio, keep values as three sentences.
- **Team with bios**: each `<li>` becomes a `<details>` with the photo, name and role in `<summary>` and a short bio inside (see `web-ui-accordion`); or link each name to a profile page.
- **Big team (80+)**: show leadership only, then a `grid-cols-3 sm:grid-cols-6` strip of small portraits with `aria-hidden` and a "see all 112 people" link.
- **Dark story section**: give the values section `full-bleed bg-stone-900 text-stone-100` from the `content-grid` utility so the page changes surface once.

## Pitfalls

- Values as three icon cards ("Integrity, Innovation, Impact") say nothing; a value is a sentence with a verb and ideally a number.
- Photos in different styles (one studio, one phone selfie, one cropped from a group) break the grid harder than any class can fix; crop all to `4/5` and shoot against the same wall.
- "Founded by industry veterans" and "passionate team" are the copy equivalents of lorem ipsum; dates, places and counts are what readers believe (see `web-craft-copy-that-sounds-human`).
- A team grid of `rounded-full` avatars at 96px reads as a social widget; portrait rectangles at card width read as people.
- `lg:sticky` headings need `lg:self-start`; otherwise the row stretches them and nothing sticks.
- The alt text on team photos is empty because the name is adjacent text; do not repeat "Photo of Ingrid Lundqvist".

## Related skills

- `web-craft-layout-with-intention`
- `web-craft-copy-that-sounds-human`
- `web-craft-real-content`
- `web-layout-testimonials`
- `web-motion-counters-and-tickers`
- `web-seo-structured-data`
- `web-page-contact`
