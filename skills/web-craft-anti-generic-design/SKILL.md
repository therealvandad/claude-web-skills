---
name: web-craft-anti-generic-design
description: Spot and replace the tells of an AI-generated page (gradient headline text, purple-to-blue palette, glass cards, blurred blobs, emoji icons, three identical cards under a centred heading) with concrete Tailwind v4 alternatives. Use whenever a user says a page "looks generic", "looks AI generated", "looks like a template", "vibe coded", or wants it to "look designed, professional, premium or real".
---

# Anti-generic design

A page looks "vibe-coded" when every decision is the default: the first font, the first accent colour, the first layout a model reaches for. None of those choices carry information about *this* product, so the reader's brain files the page as "template" before reading a word. The fix is not more decoration. It is replacing each default with a choice that could only belong to this site: a typeface with a voice, one accent that means "click here", copy with a real noun in it, and a layout that puts the most important thing in the most important place instead of centring everything.

## Pattern

The before block stacks every tell at once. The after block is the same hero and feature section with each tell replaced.

```html
<!-- BEFORE: every default at once -->
<section class="relative overflow-hidden bg-gray-50 py-24">
  <div class="absolute -top-40 left-1/2 size-[40rem] -translate-x-1/2 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 opacity-30 blur-3xl"></div>
  <div class="relative mx-auto max-w-7xl px-6 text-center">
    <p class="text-sm font-semibold uppercase tracking-wider text-indigo-600">✨ Introducing Acme</p>
    <h1 class="mt-4 bg-gradient-to-r from-purple-500 to-blue-500 bg-clip-text text-5xl font-bold tracking-tight text-transparent">
      Supercharge your workflow 🚀
    </h1>
    <p class="mx-auto mt-6 max-w-2xl text-lg text-gray-600">Seamlessly unlock effortless productivity, built for the modern team.</p>
    <a href="#" class="mt-8 inline-block rounded-2xl bg-indigo-600 px-6 py-3 font-semibold text-white shadow-lg">Get Started</a>
    <div class="mt-20 grid gap-8 md:grid-cols-3">
      <div class="rounded-2xl border border-white/20 bg-white/30 p-8 shadow-lg backdrop-blur-lg">
        <div class="flex size-12 items-center justify-center rounded-xl bg-indigo-100 text-2xl">⚡</div>
        <h3 class="mt-4 font-bold">Lightning fast</h3>
        <p class="mt-2 text-gray-600">Blazing speed for all your needs.</p>
      </div>
      <!-- two more cards identical to the one above -->
    </div>
  </div>
</section>
```

```css
/* AFTER, step 1: give the page a voice. One display face, one text face, one mono for labels. */
@theme {
  --font-display: "Instrument Serif", "Iowan Old Style", Georgia, serif;
  --font-sans: "Geist", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
}
```

```html
<!-- AFTER, step 2: asymmetric grid, left-aligned measure, a claim with a noun in it, a real artefact instead of a fake dashboard, numbered facts instead of icon cards -->
<section class="bg-stone-50 text-stone-900">
  <div class="mx-auto grid max-w-6xl gap-10 px-6 py-20 lg:grid-cols-[1.2fr_0.8fr] lg:py-28">
    <div class="max-w-xl">
      <p class="font-mono text-xs uppercase tracking-widest text-stone-500">Invoicing for hourly freelancers</p>
      <h1 class="mt-4 font-display text-5xl font-normal leading-[1.05] text-balance sm:text-6xl">
        Send the invoice before you close the laptop.
      </h1>
      <p class="mt-6 text-lg leading-relaxed text-stone-600">
        Log hours as you work. When the job ends, Ledger drafts the invoice from the log, you check two numbers, and it goes out. Clients pay by card or bank transfer.
      </p>
      <div class="mt-8 flex flex-wrap items-center gap-4">
        <a href="/signup" class="rounded-md bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stone-900">Start a free account</a>
        <a href="/sample-invoice.pdf" class="text-sm font-medium text-stone-700 underline underline-offset-4 hover:text-stone-900">See a sample invoice (PDF)</a>
      </div>
    </div>
    <figure class="self-end">
      <img src="/img/invoice-0412.webp" width="880" height="1100" alt="A finished invoice: 14.5 hours at 90 euros an hour, due in 14 days" class="w-full border border-stone-300">
      <figcaption class="mt-2 font-mono text-xs text-stone-500">Invoice #0412, exactly as the client sees it.</figcaption>
    </figure>
  </div>

  <dl class="mx-auto grid max-w-6xl gap-x-12 gap-y-10 border-t border-stone-300 px-6 py-16 sm:grid-cols-3">
    <div>
      <dt class="font-mono text-xs text-stone-500">01</dt>
      <dd class="mt-2 font-medium">Hours become line items</dd>
      <dd class="mt-1 text-sm leading-relaxed text-stone-600">Every logged block is a row with a date, a note and a total. Nothing to retype.</dd>
    </div>
    <div>
      <dt class="font-mono text-xs text-stone-500">02</dt>
      <dd class="mt-2 font-medium">Paid in 9 days on average</dd>
      <dd class="mt-1 text-sm leading-relaxed text-stone-600">A pay button in the email, not a PDF to print. Median across last quarter's invoices.</dd>
    </div>
    <div>
      <dt class="font-mono text-xs text-stone-500">03</dt>
      <dd class="mt-2 font-medium">VAT handled per country</dd>
      <dd class="mt-1 text-sm leading-relaxed text-stone-600">Reverse charge, OSS and exempt clients are a dropdown; the right legal line is printed.</dd>
    </div>
  </dl>
</section>
```

Each tell, why it reads as generic, and the replacement:

- **Gradient headline text** (`bg-clip-text text-transparent from-purple-500 to-blue-500`): it is the one trick every template does, it fails contrast at the light stop and breaks text selection. Replace with a display face at `font-normal` and a solid ink colour; if you need emphasis, italicise one word.
- **Purple/indigo-to-blue everywhere, decorative blurred blobs**: Tailwind's default accent plus free "atmosphere" that says nothing. One accent, tinted neutrals (`stone`, `zinc`, or `oklch` neutrals with a hint of the accent hue), no blob. See `web-craft-color-with-restraint`.
- **Glass cards** (`bg-white/30 backdrop-blur-lg border-white/20`): expensive to paint, unreadable over busy backgrounds, and meaningless on a flat page. Use a hairline border (`border border-stone-300`) or no box at all.
- **Centred eyebrow + centred heading + centred paragraph + three icon cards**: it is the shape of every landing-page generator. Left-align with a `max-w-xl` measure, use an asymmetric grid, and present facts as a numbered `<dl>` or a list, not three identical boxes.
- **Emoji as icons, ✨ 🚀 ⚡ in headings and buttons**: they render differently on every OS and signal "no icon set was chosen". Use inline SVG from one icon set at one stroke weight, or a number, or nothing.
- **Icon in a coloured square above each card title**: pure template furniture. Replace with the editorial number (`01`, `02`) or a small inline SVG beside the title.
- **`rounded-2xl` and `shadow-lg` on everything**: radius and shadow lose meaning when universal. Pick `rounded-md` for controls, `rounded-lg` for images, and reserve shadow for things that float (menus, dialogs).
- **Fake dashboard made of grey rectangles**: a placeholder pretending to be a product. Show a real screenshot, a real document, a real photo, or just the text.
- **"Get Started" / "Learn More"**: label what happens: "Start a free account", "See a sample invoice (PDF)". See `web-craft-copy-that-sounds-human`.

## Variations

- **Dark variant**: `bg-stone-950 text-stone-100`, borders `border-stone-800`, the primary button inverts to `bg-stone-100 text-stone-900`. Keep the single accent; do not add a glow.
- **Keep a gradient where it earns it**: one soft wash in the same hue (`from-stone-100 to-stone-50`) as a section background is fine. The rule is one hue, no transparency text, never on headings.
- **Three cards are allowed** when the three things are genuinely parallel (plans, tiers). Then make them a real `<ul>` of plans, with one visibly different, and drop the icon squares.
- **No display serif available** (strict brand sans): keep one family and get contrast from weight and size instead: `font-medium text-6xl leading-none` next to `text-sm font-mono` labels.

## Pitfalls

- Swapping fonts alone does not fix the page; the layout and copy tells remain. Do all four: type, colour, copy, layout.
- Removing every decoration leaves a page that looks unfinished rather than designed. Keep one strong element per screen: a large number, a real photo, a long headline.
- `text-balance` on a heading over about six lines does nothing; shorten the heading instead.
- Replacing `rounded-2xl` with sharp corners everywhere is its own template ("brutalist"). Pick a radius scale and use two steps of it.
- A real screenshot needs `width`/`height` and a descriptive `alt`; a blurry upscaled one looks worse than the fake dashboard did.
- Over-correcting the copy into cleverness ("Invoices, but make it fashion") is as hollow as "Supercharge". Specific beats witty.

## Related skills

- `web-craft-typography-with-character`
- `web-craft-copy-that-sounds-human`
- `web-craft-layout-with-intention`
- `web-craft-color-with-restraint`
- `web-craft-finishing-details`
- `web-craft-real-content`
- `web-layout-hero`
- `web-layout-feature-grid`
- `web-design-icons`
