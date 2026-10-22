---
name: web-seo-meta-tags
description: 'Produce the complete head for a page: title and meta description, canonical, viewport, robots, Open Graph and Twitter card tags, favicon set with web manifest, theme-color, hreflang. Use when a user asks for "meta tags", "SEO head", "social preview", "link preview looks wrong", "og:image", "favicon", "canonical", or sets up a new page or site.'
---

# Meta tags and the `<head>`

Search engines read the `<head>` to decide what to show in results; chat apps and social networks
read it to render link previews. A missing `<title>` costs rankings and clicks, a missing `og:image`
makes every share look broken, a wrong `canonical` can de-index the page. The set below is the
current minimum that works for Google, Bing, iMessage, Slack, LinkedIn, X and Bluesky; most of it
is static per site and only four values change per page: title, description, canonical, image.

## Pattern

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- Per page: title 50-60 chars, brand last; description 120-160 chars, a real sentence -->
  <title>Pricing: plans from free to enterprise | Acme</title>
  <meta name="description" content="Compare Acme plans. Start free, upgrade to Team at $29 per seat, or talk to us about enterprise SSO and audit logs.">
  <link rel="canonical" href="https://www.acme.com/pricing">

  <!-- Indexing control: omit entirely for normal pages; set only on pages you want hidden -->
  <!-- <meta name="robots" content="noindex, follow"> -->

  <!-- Open Graph: used by Facebook, LinkedIn, Slack, iMessage, WhatsApp, Discord -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Acme">
  <meta property="og:title" content="Pricing: plans from free to enterprise">
  <meta property="og:description" content="Start free, upgrade to Team at $29 per seat, or talk to us about enterprise.">
  <meta property="og:url" content="https://www.acme.com/pricing">
  <meta property="og:image" content="https://www.acme.com/og/pricing.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Acme pricing: Free, Team, Enterprise">
  <meta property="og:locale" content="en_US">

  <!-- Twitter/X: falls back to og:* for anything missing, so only the card type is required -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@acme">

  <!-- Icons: one SVG for modern browsers, one 32px ICO fallback, one 180px PNG for iOS -->
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0a0a0a" media="(prefers-color-scheme: dark)">

  <!-- Alternate languages, when the page exists in several (self-reference included) -->
  <link rel="alternate" hreflang="en" href="https://www.acme.com/pricing">
  <link rel="alternate" hreflang="de" href="https://www.acme.com/de/preise">
  <link rel="alternate" hreflang="x-default" href="https://www.acme.com/pricing">

  <link rel="stylesheet" href="/dist/output.css">
</head>
```

```json
{
  "name": "Acme",
  "short_name": "Acme",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone",
  "start_url": "/"
}
```

Decisions behind the values:

- **Title**: the primary phrase first, brand after a separator; Google rewrites titles it finds
  padded or duplicated across pages, so make each unique and honest.
- **Description** is not a ranking factor but is the snippet shown ~70% of the time; write it as
  the ad copy for the click. No quotes, no keyword lists.
- **Canonical** is absolute, matches the final URL exactly (scheme, host, trailing slash, no
  tracking params), and is self-referencing on the canonical page itself.
- **og:image** 1200 x 630 PNG or JPEG under 1 MB, absolute URL, text large enough to read at
  300px wide. One image per page beats a generic logo.
- **viewport** without `maximum-scale` or `user-scalable=no`: those block pinch zoom and fail
  WCAG 1.4.4.

## Variations

- **Articles**: `og:type="article"` plus `article:published_time`, `article:modified_time`,
  `article:author`; pair with `Article` JSON-LD from `web-seo-structured-data`.
- **Products**: `og:type="product"`, `product:price:amount`, `product:price:currency` help
  Pinterest and Facebook; the JSON-LD `Product` schema matters more for Google.
- **Paginated or filtered listings**: canonical to the clean URL (`/shop?page=2` canonicalizes to
  itself, `/shop?sort=price` canonicalizes to `/shop`). Use `noindex` on internal search results.
- **Staging / preview sites**: `<meta name="robots" content="noindex, nofollow">` sitewide, or
  better, the `X-Robots-Tag: noindex` header so it cannot be forgotten in a template.

## Pitfalls

- Relative URLs in `canonical`, `og:url`, `og:image`. Many scrapers do not resolve them; always
  absolute with `https://`.
- Same title and description on every page (template default never overridden). Search Console
  flags it; users cannot tell results apart.
- `og:image` behind authentication, blocked by `robots.txt`, or served with a hotlink-protection
  rule. Scrapers fetch it anonymously; test with the Facebook Sharing Debugger or `curl -A facebookexternalhit`.
- Cached previews: Slack, LinkedIn and Facebook cache for days. After changing `og:*`, bust the
  cache with their debug tools or by adding a query string to `og:image`.
- Multiple `<title>` elements or a `<title>` injected by JS after load. Crawlers may read the first
  or the empty one. Render the real title server-side or in static HTML.
- Forgetting `charset` first: it must appear in the first 1024 bytes so the browser does not
  re-parse. Put it as the first child of `<head>`.

## Related skills

- `web-seo-structured-data`
- `web-seo-sitemap-robots-urls`
- `web-seo-content-structure`
- `web-ship-launch-checklist`
- `web-design-dark-mode`
- `web-perf-css-and-js-loading`
