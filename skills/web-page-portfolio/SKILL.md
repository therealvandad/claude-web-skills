---
name: web-page-portfolio
description: 'Build a portfolio site in Tailwind v4: a project index with a mixed-size work grid and an availability line, plus a case study page with a facts column, problem/process/outcome sections, full-bleed images and a next-project link. Use whenever a user asks for a portfolio, personal site, design or dev portfolio, case study page, "my work" page or project showcase.'
---

# Portfolio and case study pages

A portfolio is judged in ten seconds on the index and in two minutes on one case study. The index needs a name, what you do, whether you are available, and the work, with the strongest project given the most space (one tile spans two columns; the rest do not). The case study is a story with facts up front: a header with the title and a facts column, then the problem, the process, the outcome, each with one image that is allowed to break the container, then the next project so the reader never hits a dead end.

## Pattern

Index page:

```html
<main id="main" class="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
  <header class="max-w-[36rem]">
    <h1 class="text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl">Tomasz Wierzbicki designs checkout flows and the systems behind them.</h1>
    <p class="mt-5 text-lg text-stone-600">Eight years, three payment companies, one grocery app. Based in Kraków, working with teams in CET ± 4.</p>
    <p class="mt-4 inline-flex items-center gap-2 text-sm"><span class="size-2 rounded-full bg-emerald-500"></span>Available from June 2026 · <a href="mailto:hello@wierzbicki.design" class="underline underline-offset-4">hello@wierzbicki.design</a></p>
  </header>

  <!-- Work grid: first tile spans both columns, the rest alternate. Nothing is equal-sized. -->
  <section aria-labelledby="work-heading" class="mt-20">
    <h2 id="work-heading" class="font-mono text-xs uppercase tracking-wide text-stone-500">Selected work, 2021 to 2026</h2>
    <ul role="list" class="mt-6 grid gap-x-8 gap-y-14 sm:grid-cols-2">
      <li class="sm:col-span-2">
        <a href="/work/bolt-checkout" class="group block">
          <img src="/img/work/bolt-cover.webp" width="1600" height="900" alt="Bolt Food checkout on a phone, tip step highlighted" class="aspect-video w-full rounded-lg object-cover">
          <h3 class="mt-4 text-xl font-semibold group-hover:underline group-hover:underline-offset-4">Bolt Food checkout</h3>
          <p class="mt-1 text-stone-600">One-page checkout; drop-off down from 31% to 19%</p>
        </a>
      </li>
      <li>
        <a href="/work/stripe-radar-rules" class="group block">
          <img src="/img/work/radar-cover.webp" width="800" height="600" loading="lazy" alt="Radar rule builder with a three-condition rule" class="aspect-[4/3] w-full rounded-lg object-cover">
          <h3 class="mt-4 text-xl font-semibold group-hover:underline group-hover:underline-offset-4">Radar rule builder</h3>
          <p class="mt-1 text-stone-600">Plain-language fraud rules for non-engineers</p>
        </a>
      </li>
      <li class="sm:translate-y-12">...third project, offset to break the baseline...</li>
    </ul>
  </section>
</main>
```

Case study page:

```html
<main id="main" class="content-grid">  <!-- utility from web-craft-layout-with-intention -->
  <article class="py-16 lg:py-24">

    <!-- 1. Header: title and summary left, facts right. Facts stick while the summary scrolls. -->
    <header class="grid gap-10 lg:grid-cols-[minmax(0,1fr)_16rem] lg:gap-16">
      <div class="max-w-[40rem]">
        <p class="font-mono text-xs uppercase tracking-wide text-stone-500">Case study 01</p>
        <h1 class="mt-3 text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl">Bolt Food checkout</h1>
        <p class="mt-5 text-xl leading-relaxed text-stone-600">Four screens became one. Checkout drop-off fell from 31% to 19% across 14 markets in the first quarter after launch.</p>
      </div>
      <dl class="grid grid-cols-2 gap-x-6 gap-y-4 text-sm lg:sticky lg:top-24 lg:block lg:space-y-4 lg:self-start lg:border-l lg:border-stone-200 lg:pl-5">
        <div><dt class="text-stone-500">Role</dt><dd class="font-medium">Lead product designer</dd></div>
        <div><dt class="text-stone-500">Team</dt><dd class="font-medium">2 designers, 6 engineers, 1 PM</dd></div>
        <div><dt class="text-stone-500">Year</dt><dd class="font-medium">2024 to 2025</dd></div>
        <div><dt class="text-stone-500">Outcome</dt><dd class="font-medium">−12 pts drop-off</dd></div>
      </dl>
    </header>

    <!-- 2. Lead image breaks the container -->
    <figure class="full-bleed mt-14">
      <img src="/img/work/bolt-hero.webp" width="2400" height="1200" alt="Six phone screens showing the checkout from cart to confirmation" class="aspect-[2/1] w-full object-cover">
    </figure>

    <!-- 3. Problem / process / outcome: numbered, same measure, one figure each -->
    <section aria-labelledby="problem" class="mt-20 grid gap-8 lg:grid-cols-[8rem_minmax(0,1fr)]">
      <h2 id="problem" class="font-mono text-sm text-stone-500 lg:sticky lg:top-24 lg:self-start">01 Problem</h2>
      <div class="max-w-[62ch] text-lg leading-relaxed">
        <p>Checkout was four screens because four teams owned four steps. Users abandoned most often on the tip screen: 11% of all sessions ended there.</p>
      </div>
    </section>
    <section aria-labelledby="process" class="mt-16 grid gap-8 lg:grid-cols-[8rem_minmax(0,1fr)]">
      <h2 id="process" class="font-mono text-sm text-stone-500 lg:sticky lg:top-24 lg:self-start">02 Process</h2>
      <div class="max-w-[62ch] text-lg leading-relaxed">
        <p>Nine rounds of usability tests in Tallinn, Warsaw and Lagos, 46 participants. The tip step moved below the order button after round three.</p>
        <figure class="mt-8 -mx-4 sm:mx-0 lg:-mr-24"><img src="/img/work/bolt-tests.webp" width="1400" height="900" loading="lazy" alt="Annotated test findings board" class="w-full rounded-lg"><figcaption class="mt-2 text-sm text-stone-500">Findings board after round six.</figcaption></figure>
      </div>
    </section>
    <section aria-labelledby="outcome" class="mt-16 grid gap-8 lg:grid-cols-[8rem_minmax(0,1fr)]">
      <h2 id="outcome" class="font-mono text-sm text-stone-500 lg:sticky lg:top-24 lg:self-start">03 Outcome</h2>
      <div class="max-w-[62ch] text-lg leading-relaxed"><p>Drop-off 31% to 19%. Average tip up 8%. Support tickets about "where is my order" down by a third because the confirmation now shows the courier.</p></div>
    </section>

    <!-- 4. Next project: never a dead end -->
    <nav aria-label="Next project" class="mt-24 border-t border-stone-200 pt-8">
      <a href="/work/stripe-radar-rules" class="group block">
        <p class="font-mono text-xs uppercase tracking-wide text-stone-500">Next</p>
        <p class="mt-2 text-2xl font-semibold group-hover:underline group-hover:underline-offset-4">Radar rule builder →</p>
      </a>
    </nav>
  </article>
</main>
```

No JavaScript is required. Add `web-motion-view-transitions` for a cross-document fade between index and case study, and `web-ui-modal-dialog` if a figure needs a lightbox.

Meta: the index gets `Person` JSON-LD (name, jobTitle, url, sameAs); each case study is a `CreativeWork` with `about` and `dateCreated`. `og:image` on a case study is its lead image.

## Variations

- **Developer portfolio**: swap the facts list for "Stack", "Repo", "Live" entries, and replace the process figure with a code block or a before/after metric table.
- **Photography or illustration**: the index grid becomes `sm:grid-cols-3` with `aspect-square` tiles and no text; the case study is images with one paragraph each.
- **One-page portfolio**: index header, three case-study summaries as `lg:grid-cols-[1.3fr_1fr]` split sections, contact row. Link to full case studies only when they exist.
- **Dark**: `bg-stone-950 text-stone-100`, facts column `border-stone-800`, images keep their own colour; do not tint them.

## Pitfalls

- A grid of equal tiles with hover overlays reads as a template; the two-column spanning first tile and the `sm:translate-y-12` offset are what make it look chosen.
- Case studies that start with the process bury the result; the number the hiring manager wants is in the header facts.
- Writing "Client: Confidential" on every project means nothing can be verified; use the real sector ("A UK grocery delivery app") and real numbers.
- Full-bleed images without `width`/`height` push the facts column around while loading.
- `lg:sticky` on the `<dl>` only works with `lg:self-start`; without it the column stretches and never sticks.
- The hover underline on the whole card link is the only hover state needed; zoom-on-hover images cause layout jank at the row edges.

## Related skills

- `web-craft-layout-with-intention`
- `web-layout-card-grid`
- `web-css-aspect-ratio-media`
- `web-motion-view-transitions`
- `web-seo-structured-data`
- `web-craft-real-content`
- `web-page-about-team`
