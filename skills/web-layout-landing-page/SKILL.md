---
name: web-layout-landing-page
description: 'Compose a complete marketing landing page in Tailwind v4: section order (hero, logos, features, how it works, testimonials, pricing, FAQ, final CTA, footer), vertical spacing rhythm, alternating backgrounds and where to repeat the call to action. Use whenever a user asks for a landing page, marketing site, product page, homepage, "one-pager", launch page or "a full page for my app".'
---

# Landing page composition

A landing page is an argument: promise, proof, details, objections answered, ask. Each section is simple on its own; what makes the page feel professional is consistent rhythm (same vertical padding, same container, same heading scale) and a CTA that reappears exactly when the reader is ready. This skill is the skeleton and the rules; pull the individual sections from the related skills.

## Pattern

```html
<body class="flex min-h-full flex-col bg-white text-gray-900 antialiased dark:bg-gray-950 dark:text-gray-100">

  <header>...navbar (web-nav-responsive-navbar)...</header>

  <main id="main" class="flex-1">

    <!-- 1. Hero: promise + primary CTA. Light background. -->
    <section class="py-16 sm:py-24 lg:py-32">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">...web-layout-hero...</div>
    </section>

    <!-- 2. Logo strip: instant credibility, no heading needed. -->
    <section class="border-y border-gray-200 bg-gray-50 py-10 dark:border-gray-800 dark:bg-gray-900" aria-label="Used by">
      <ul role="list" class="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-x-12 gap-y-6 px-4 opacity-70 grayscale sm:px-6 lg:px-8">
        <li><img src="/img/logos/a.svg" alt="Acme" height="28" class="h-7 w-auto"></li>
        <li><img src="/img/logos/b.svg" alt="Globex" height="28" class="h-7 w-auto"></li>
      </ul>
    </section>

    <!-- 3. Features: what you get. -->
    <section id="features" class="py-16 sm:py-24" aria-labelledby="features-heading">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">...web-layout-feature-grid...</div>
    </section>

    <!-- 4. How it works / product detail: alternating media + text. Tinted background. -->
    <section class="bg-gray-50 py-16 sm:py-24 dark:bg-gray-900" aria-labelledby="how-heading">
      <div class="mx-auto max-w-7xl space-y-24 px-4 sm:px-6 lg:px-8">...web-layout-split-section x2-3...</div>
    </section>

    <!-- 5. Proof: testimonials or numbers. -->
    <section class="py-16 sm:py-24" aria-labelledby="testimonials-heading">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">...web-layout-testimonials...</div>
    </section>

    <!-- 6. Pricing (if self-serve). Tinted. -->
    <section id="pricing" class="bg-gray-50 py-16 sm:py-24 dark:bg-gray-900" aria-labelledby="pricing-heading">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">...web-layout-pricing-table...</div>
    </section>

    <!-- 7. FAQ: objections. Narrow container, native accordion. -->
    <section id="faq" class="py-16 sm:py-24" aria-labelledby="faq-heading">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h2 id="faq-heading" class="text-3xl font-bold tracking-tight sm:text-4xl">Questions</h2>
        <div class="mt-10 divide-y divide-gray-200 dark:divide-gray-800">...web-ui-accordion...</div>
      </div>
    </section>

    <!-- 8. Final CTA: the ask, high contrast. -->
    <section class="bg-blue-600 py-16 text-white sm:py-24" aria-labelledby="cta-heading">
      <div class="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 id="cta-heading" class="text-3xl font-bold tracking-tight text-balance sm:text-4xl">Ready to ship your site?</h2>
        <p class="mt-4 text-lg text-blue-100">Free to start. No credit card.</p>
        <a href="/signup" class="mt-8 inline-flex rounded-lg bg-white px-6 py-3 text-base font-semibold text-blue-700 shadow-sm hover:bg-blue-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">Get started</a>
      </div>
    </section>

  </main>

  <footer>...web-layout-footer...</footer>
</body>
```

The rules behind the order:

- **Promise, proof, detail, objections, ask.** Hero makes the claim, logos and testimonials back it, features and how-it-works explain, FAQ removes doubt, final CTA asks. Do not put pricing before features: readers need to know what they are paying for.
- **One rhythm**: every section is `py-16 sm:py-24` (the hero may go to `lg:py-32`). Inside a section, heading block then `mt-12 lg:mt-16` before the content. Never mix `py-20` here and `py-14` there.
- **Alternate backgrounds, never twice in a row**: white, tinted, white, tinted. The tint separates sections without divider lines. The final CTA breaks the pattern deliberately with brand color.
- **Headings**: one `<h1>` in the hero; every other section heading is `<h2>` at `text-3xl sm:text-4xl`; cards use `<h3>`. Same size each time.
- **CTA cadence**: hero, after pricing (inside the cards), final section. Three asks, same wording ("Get started"), same destination. Add a navbar CTA for pages longer than four sections.
- **Section ids** (`#features`, `#pricing`, `#faq`) make the navbar links work and give you anchors for ads.

## Variations

- **Waitlist / pre-launch**: hero with email form, one feature grid, final CTA. Three sections total; skip logos, pricing and FAQ you cannot back up yet.
- **Long-form / sales letter**: `max-w-3xl` for all text sections, split sections become full-width images between paragraphs, pricing repeated twice.
- **Dark landing page**: invert the alternation (`bg-gray-950` / `bg-gray-900`), use `text-gray-300` for body and keep the final CTA on brand color; check contrast of muted text (gray-400 on gray-950 passes, gray-500 does not).
- **App or SaaS with login**: add a slim top "Sign in" link in the navbar and make the hero CTA "Start free trial" with a secondary "See demo" that scrolls to `#how`.

## Pitfalls

- Fifteen sections do not convert better than seven; each extra section before the ask is attrition. Cut anything that does not promise, prove, explain or answer.
- Different container widths per section (`max-w-6xl` here, `max-w-7xl` there) make edges jitter as the user scrolls. Pick one and only narrow for text-only sections (FAQ, final CTA).
- Lazy-loading everything, including the hero image, delays LCP. Lazy-load images below the fold only; mark the hero image `fetchpriority="high"`.
- Scroll-reveal animations on every section feel like a slideshow and hide content from users with JS off. Reveal at most the feature cards and respect `prefers-reduced-motion`.
- Sticky navbar + anchor links without `scroll-pt-*` on `<html>` scroll section headings under the bar.
- A logo strip in color is louder than the hero. `grayscale opacity-70` keeps it a background signal; restore color on `hover:` if desired.

## Related skills

- `web-layout-page-shell`
- `web-layout-hero`
- `web-layout-feature-grid`
- `web-layout-split-section`
- `web-layout-testimonials`
- `web-layout-pricing-table`
- `web-layout-footer`
- `web-ui-accordion`
- `web-nav-responsive-navbar`
- `web-css-spacing-scale`
- `web-seo-meta-tags`
