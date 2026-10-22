---
name: web-ship-launch-checklist
description: Run a pre-launch checklist for a static site, each item with the command or devtools step that verifies it - 404 page, favicons, social previews, forms, broken links, valid HTML, accessibility, Lighthouse, caching, HTTPS, legal pages. Use when a user says "ready to launch", "go live checklist", "before I publish", "QA my site" or "final checks".
---

# Launch checklist

A launch fails on boring things: a form that posts nowhere, a share preview with no image, a 404 that shows the host's default page. Every item below says how to check it, mostly from the terminal against the production build (`npm run build && npx serve dist`, then the deployed URL once it exists). Work through it top to bottom; the first group blocks launch, the rest are "fix this week".

## Pattern

Install the checkers once, then run them against the built site:

```bash
npm i -D html-validate linkinspector pa11y lighthouse
npx serve dist -l 3000
```

```json
{
  "scripts": {
    "check:html": "html-validate \"dist/**/*.html\"",
    "check:links": "linkinspector http://localhost:3000 --recursive",
    "check:a11y": "pa11y http://localhost:3000 --standard WCAG2AA",
    "check:lh": "lighthouse http://localhost:3000 --form-factor=mobile --output=html --output-path=lh.html --quiet",
    "check": "npm run check:html && npm run check:links && npm run check:a11y"
  }
}
```

**Blocks launch**

- [ ] **404 page exists and is served**: `curl -s -o /dev/null -w "%{http_code}" https://example.com/nope` prints `404` and the body is your page, not the host's. Needs `404.html` in `dist/` (see `web-ship-static-hosting`).
- [ ] **HTTPS and one canonical host**: `curl -sI http://example.com | grep -i location` redirects to `https://`; `www` and apex both land on the chosen one with a `301`.
- [ ] **Every form works**: submit each one on the production URL with a real email; confirm the success state, the error state (submit empty), and that the message arrives. Check the spam folder.
- [ ] **No broken links or images**: `npm run check:links` reports zero failures; also check external links (`--external` flag, slower).
- [ ] **Title and description on every page**: `grep -L "<meta name=\"description\"" dist/*.html` prints nothing; titles are unique: `grep -h "<title>" dist/*.html | sort | uniq -d` prints nothing.
- [ ] **Social preview**: paste the URL into opengraph.xyz or the LinkedIn Post Inspector; image shows at 1200x630, title and description are right (`web-seo-meta-tags`).
- [ ] **Favicons**: `/favicon.ico` (32 px), `/icon.svg`, `/apple-touch-icon.png` (180 px) all return 200 (`curl -sI https://example.com/apple-touch-icon.png | head -1`); the tab icon shows in a private window.
- [ ] **Placeholder content gone**: `grep -ril "lorem ipsum\|TODO\|example.com\|XXXX" dist/` prints nothing (adjust `example.com` if that is your real domain).
- [ ] **Mobile layout**: devtools device toolbar at 360 px wide, no horizontal scroll (`document.documentElement.scrollWidth > innerWidth` in the console is `false`), tap targets at least 44 px.

**Fix before announcing**

- [ ] **Lighthouse mobile 90+ in all four categories**: `npm run check:lh`, open `lh.html`. Fix LCP and CLS first (`web-perf-web-vitals`).
- [ ] **Valid HTML**: `npm run check:html` is clean; it catches unclosed tags, duplicate IDs and invalid nesting that break screen readers and styling.
- [ ] **Accessibility**: `npm run check:a11y` is clean; then tab through every page with the keyboard: every interactive element reachable, visible focus ring, no trap. Run with a screen reader once (NVDA on Windows, VoiceOver on macOS).
- [ ] **Images sized and compressed**: devtools Network panel, filter Img, sort by size; nothing over 200 KB above the fold, every `<img>` has `width`/`height` (`web-perf-images`).
- [ ] **Caching headers**: `curl -sI https://example.com/output.<hash>.css | grep -i cache-control` shows `max-age=31536000, immutable`; the HTML shows `max-age=0` or similar (`web-perf-caching-and-service-worker`).
- [ ] **Compression on**: `curl -sI -H "Accept-Encoding: br, gzip" https://example.com | grep -i content-encoding` shows `br` or `gzip`.
- [ ] **robots.txt and sitemap**: `/robots.txt` returns 200 and does not `Disallow: /` (a common leftover from staging); `/sitemap.xml` lists every public page with the canonical URL form (`web-seo-sitemap-robots-urls`). Submit the sitemap in Google Search Console.
- [ ] **Analytics receiving data**: open the site in a private window, see the visit appear in the dashboard; no consent banner unless a cookie-setting tool is used (`web-ship-analytics-and-privacy`).
- [ ] **Privacy page and imprint/contact**: linked from the footer on every page: `grep -L "/privacy" dist/*.html` prints nothing.
- [ ] **Console clean**: devtools Console on each page shows no errors or 404s (red lines); mixed-content warnings mean an `http://` asset URL somewhere.
- [ ] **Dark mode and reduced motion**: devtools Rendering panel, emulate `prefers-color-scheme: dark` and `prefers-reduced-motion: reduce`; nothing unreadable, nothing still animating.
- [ ] **Print**: Ctrl+P / Cmd+P on the main content pages; navigation and buttons hidden (`print:hidden`), text black on white.

## Variations

- **Automate the blocking group in CI**: put `npm run check` in the deploy workflow before the publish step (`web-ship-static-hosting`) so a broken link or invalid HTML fails the build rather than going live.
- **Relaunch or redesign**: add a redirect map for every old URL (`curl -sI https://example.com/old-path | head -1` is `301`), and compare the old sitemap with the new one so no indexed page becomes a 404.
- **Multi-language sites**: add `hreflang` checks: each page links its alternates, and `lang` on `<html>` matches the content.
- **Post-launch (day 2)**: check Search Console for crawl errors and Core Web Vitals field data after a week; set a reminder.

## Pitfalls

- Testing only on `localhost` misses host-level problems: redirects, headers, the 404 page and case-sensitive paths all behave differently in production. Repeat the blocking group on the live URL.
- `linkinspector` and `pa11y` need the site served over HTTP; opening `dist/index.html` as a file gives false errors for absolute paths.
- A `noindex` meta tag or `Disallow: /` left over from the staging site is the most common "we launched and Google ignores us" cause; grep for both.
- Lighthouse numbers on a laptop with devtools open are optimistic; run it from the CLI or in an incognito window.
- Forms often work locally and fail live because the endpoint, CORS or host-specific attribute (`netlify`, `data-netlify`) was never configured for the production domain. Submit one for real.
- Do not launch on a Friday afternoon; nobody is around to fix the thing the checklist missed.

## Related skills

- `web-ship-static-hosting`
- `web-seo-meta-tags`
- `web-seo-sitemap-robots-urls`
- `web-perf-web-vitals`
- `web-ship-analytics-and-privacy`
- `web-design-empty-and-error-states`
- `web-a11y-keyboard-and-focus`
