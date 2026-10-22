---
name: web-layout-footer
description: Build a site footer with multi-column link groups, a short newsletter signup form, social icon links and a bottom legal row (copyright, privacy, terms), responsive and accessible with Tailwind v4. Use whenever a user asks for a footer, "bottom of the page", site links, a newsletter box, social links or a copyright line.
---

# Footer

The footer is the page's safety net: whatever the visitor did not find above, they look for here. Structure it as named navigation groups (so screen readers list them as landmarks), make the newsletter form a real form that works without JavaScript, and keep the legal row small but present. Columns collapse to two on phones, not one, because footer links are short and a single column makes the footer absurdly tall.

## Pattern

```html
<footer class="border-t border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950">
  <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">

    <div class="grid gap-10 lg:grid-cols-12 lg:gap-8">

      <!-- Brand + newsletter -->
      <div class="lg:col-span-4">
        <a href="/" class="inline-flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
          <svg class="size-6 text-blue-600" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="12" r="10"/></svg>
          Site name
        </a>
        <p class="mt-3 max-w-xs text-sm text-gray-600 dark:text-gray-400">Fast, simple websites for people who would rather be building something else.</p>

        <form class="mt-6" action="/api/subscribe" method="post">
          <label for="footer-email" class="block text-sm font-medium text-gray-900 dark:text-white">Get the monthly newsletter</label>
          <div class="mt-2 flex max-w-sm gap-2">
            <input id="footer-email" name="email" type="email" autocomplete="email" required placeholder="you@example.com"
                   class="min-w-0 flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-600 focus:outline-2 focus:outline-blue-600 dark:border-gray-700 dark:bg-gray-900 dark:text-white">
            <button type="submit" class="shrink-0 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">Subscribe</button>
          </div>
          <p class="mt-2 text-xs text-gray-500">No spam. Unsubscribe any time.</p>
        </form>
      </div>

      <!-- Link columns -->
      <div class="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:col-span-8">
        <nav aria-labelledby="footer-product">
          <h2 id="footer-product" class="text-sm font-semibold text-gray-900 dark:text-white">Product</h2>
          <ul role="list" class="mt-4 space-y-3 text-sm">
            <li><a href="/features" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Features</a></li>
            <li><a href="/pricing" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Pricing</a></li>
            <li><a href="/changelog" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Changelog</a></li>
          </ul>
        </nav>
        <nav aria-labelledby="footer-company">
          <h2 id="footer-company" class="text-sm font-semibold text-gray-900 dark:text-white">Company</h2>
          <ul role="list" class="mt-4 space-y-3 text-sm">
            <li><a href="/about" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">About</a></li>
            <li><a href="/blog" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Blog</a></li>
            <li><a href="/contact" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Contact</a></li>
          </ul>
        </nav>
        <nav aria-labelledby="footer-support" class="col-span-2 sm:col-span-1">
          <h2 id="footer-support" class="text-sm font-semibold text-gray-900 dark:text-white">Support</h2>
          <ul role="list" class="mt-4 space-y-3 text-sm">
            <li><a href="/docs" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Docs</a></li>
            <li><a href="/status" class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">Status</a></li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Legal row -->
    <div class="mt-12 flex flex-col-reverse items-center gap-6 border-t border-gray-200 pt-8 sm:flex-row sm:justify-between dark:border-gray-800">
      <p class="text-xs text-gray-500">&copy; <span id="year">2026</span> Site name. All rights reserved.</p>
      <ul role="list" class="flex gap-5">
        <li>
          <a href="https://github.com/example" class="text-gray-500 hover:text-gray-900 dark:hover:text-white">
            <span class="sr-only">GitHub</span>
            <svg class="size-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.3-3.4-1.3-.4-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.6-1.4-2.2-.2-4.6-1.1-4.6-5a3.9 3.9 0 0 1 1-2.7 3.6 3.6 0 0 1 .1-2.7s.9-.3 2.8 1a9.5 9.5 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1a3.6 3.6 0 0 1 .1 2.7 3.9 3.9 0 0 1 1 2.7c0 3.9-2.4 4.8-4.6 5 .4.3.7.9.7 1.9v2.8c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/></svg>
          </a>
        </li>
        <li>
          <a href="https://bsky.app/profile/example" class="text-gray-500 hover:text-gray-900 dark:hover:text-white">
            <span class="sr-only">Bluesky</span>
            <svg class="size-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 10.8c-1-2-3.8-5.7-6.4-7.5C3.2 1.5 2 1.8 1.2 2.2.3 2.6 0 4 0 4.8c0 .8.5 6.8.8 7.8.7 2 2.9 2.8 5 2.5-3.2.5-6.1 1.7-2.3 5.9 4.1 4.3 5.6-1 6.5-3.6.9 2.7 2.3 7.9 6.5 3.6 3.8-4.2 1-5.4-2.3-5.9 2.1.2 4.3-.5 5-2.5.3-1 .8-7 .8-7.8 0-.8-.3-2.2-1.2-2.6-.8-.4-2-.7-4.4 1.1C15.8 5.1 13 8.8 12 10.8z"/></svg>
          </a>
        </li>
      </ul>
      <ul role="list" class="flex gap-5 text-xs text-gray-500">
        <li><a href="/privacy" class="hover:text-gray-900 dark:hover:text-white">Privacy</a></li>
        <li><a href="/terms" class="hover:text-gray-900 dark:hover:text-white">Terms</a></li>
      </ul>
    </div>
  </div>
</footer>
```

Why these choices:

- Each link group is its own `<nav aria-labelledby>`, so assistive tech lists "Product navigation", "Company navigation" as separate landmarks instead of one anonymous blob. The group titles are `<h2>` because the footer sits outside `<main>` and starts a new outline branch.
- Link columns use `grid-cols-2` at the smallest size: short link lists fit two abreast on a 360 px phone and halve the footer height.
- The newsletter input has a visible `<label>`, `type="email"`, `autocomplete="email"` and `required`, so the browser validates and autofills without JS. Enhance with `web-form-submit-with-fetch` later.
- Social links are icon-only, so each carries an `sr-only` name and the SVG is `aria-hidden`.
- `flex-col-reverse` puts the social icons above the copyright on phones (more useful) and `sm:flex-row` restores the conventional order.

## Variations

- **Minimal footer**: keep only the legal row; set `py-8` and drop the big grid. Right for one-page sites and app pages.
- **Dark footer on a light site**: `bg-gray-900 text-gray-400` with headings `text-white`, links `hover:text-white`; this also makes the footer visually "close" the page.
- **Four link columns**: `grid-cols-2 sm:grid-cols-4` and move the brand block to its own full-width row above (`lg:col-span-12`).
- **Current year by JS**: `document.getElementById('year').textContent = new Date().getFullYear();` in a `type="module"` script; keep the hard-coded year as the no-JS fallback.

## Pitfalls

- A footer that is not inside the sticky-footer flex column (see `web-layout-page-shell`) floats mid-screen on short pages.
- Icon-only links without an accessible name are read as "link" or the raw SVG path. The `sr-only` span is mandatory.
- `text-xs` links at `text-gray-400` on white fail contrast (about 2.5:1). Use `gray-500` or darker for anything readable; AA for small text is 4.5:1.
- Opening social links with `target="_blank"` without telling the user is surprising; if you do, add `rel="noopener"` and an `sr-only` "(opens in new tab)".
- A newsletter form that only "works" via JS leaves non-JS users with a dead button. Always set `action` and `method`.
- Footer link lists with 15 links per column are not navigation, they are a sitemap. Cap at about 6 per column and link to a sitemap page.

## Related skills

- `web-layout-page-shell`
- `web-form-submit-with-fetch`
- `web-form-layout`
- `web-design-icons`
- `web-a11y-skip-links-and-landmarks`
- `web-a11y-color-contrast`
