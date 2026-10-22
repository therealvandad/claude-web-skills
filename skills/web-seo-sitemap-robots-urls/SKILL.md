---
name: web-seo-sitemap-robots-urls
description: Generate sitemap.xml (and a sitemap index), write a correct robots.txt, define clean URL conventions (lowercase, hyphens, one trailing-slash rule, no query noise), and set up 301 redirects and canonical host rules for Netlify, Cloudflare Pages or Vercel. Use when a user asks for "sitemap", "robots.txt", "URL structure", "trailing slash", "redirect old URLs", "www vs non-www", or "pages not indexed".
---

# Sitemap, robots.txt and URLs

Crawlers discover pages by following links and reading sitemaps, decide what to fetch by reading
`robots.txt`, and treat every distinct URL as a distinct page. So a site that serves the same
content at `/About`, `/about`, `/about/` and `/about?ref=nav` has four competing pages, and a
`robots.txt` that blocks `/assets/` stops Google from rendering your CSS. Fix the three together:
one canonical URL shape, a sitemap that lists only those URLs, and a `robots.txt` that blocks
only what should never be fetched.

## Pattern

URL rules, applied everywhere (links, canonical, sitemap, redirects):

- lowercase, words separated by hyphens: `/blog/why-we-charge-per-seat`
- one host: `https://www.acme.com` (or apex; pick one and redirect the other)
- one trailing-slash policy: with slash for directories (`/blog/`), without for pages, or no
  slashes at all; be consistent and let the host redirect the other form
- no file extensions (`/about`, not `/about.html`), no session or tracking params in internal links
- stable: a URL is a promise; when it must change, 301 it forever

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://www.acme.com/</loc>
    <lastmod>2026-10-15</lastmod>
  </url>
  <url>
    <loc>https://www.acme.com/pricing</loc>
    <lastmod>2026-10-01</lastmod>
  </url>
  <url>
    <loc>https://www.acme.com/blog/why-we-charge-per-seat</loc>
    <lastmod>2026-10-15T14:30:00+00:00</lastmod>
    <image:image><image:loc>https://www.acme.com/og/per-seat.png</image:loc></image:image>
  </url>
</urlset>
```

```text
# /robots.txt
User-agent: *
Disallow: /admin/
Disallow: /search
Disallow: /*?sort=
Allow: /

Sitemap: https://www.acme.com/sitemap.xml
```

Generate the sitemap from the file tree in a static site; a short Node script is enough and runs
in the build step:

```js
// scripts/sitemap.mjs — run with: node scripts/sitemap.mjs
import { readdir, stat, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';

const SITE = 'https://www.acme.com';
const ROOT = 'dist';
const SKIP = /^(404|admin\/|search)/;

async function* htmlFiles(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) yield* htmlFiles(path);
    else if (entry.name.endsWith('.html')) yield path;
  }
}

const urls = [];
for await (const file of htmlFiles(ROOT)) {
  const rel = relative(ROOT, file).replaceAll('\\', '/');
  if (SKIP.test(rel)) continue;
  const route = rel === 'index.html' ? '/' : '/' + rel.replace(/\/index\.html$/, '').replace(/\.html$/, '');
  const lastmod = (await stat(file)).mtime.toISOString().slice(0, 10);
  urls.push(`  <url><loc>${SITE}${route}</loc><lastmod>${lastmod}</lastmod></url>`);
}
const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`;
await writeFile(join(ROOT, 'sitemap.xml'), xml);
console.log(`sitemap: ${urls.length} urls`);
```

Redirects, host by host (301 permanent unless noted):

```text
# Netlify: _redirects (in publish dir)
https://acme.com/*  https://www.acme.com/:splat  301!
/old-pricing        /pricing                     301
/blog/2024/*        /blog/:splat                 301

# Cloudflare Pages: _redirects, same syntax; host redirect via a Bulk Redirect or Page Rule instead
```

```json
// Vercel: vercel.json
{ "trailingSlash": false,
  "redirects": [
    { "source": "/old-pricing", "destination": "/pricing", "permanent": true },
    { "source": "/blog/2024/:slug", "destination": "/blog/:slug", "permanent": true }
  ] }
```

Why `lastmod` and nothing else: Google ignores `<changefreq>` and `<priority>`; it does use an
accurate `lastmod` to decide what to recrawl, and penalises nothing if it is omitted but learns to
distrust it if every page claims "today". Use the real content date, not the build time, when you
have it.

## Variations

- **Large sites (>50,000 URLs or >50 MB)**: split into several files and list them in a
  `<sitemapindex>` at `/sitemap.xml`; each child file follows the same `urlset` shape.
- **Multilingual**: add `xmlns:xhtml` and `<xhtml:link rel="alternate" hreflang="de" href="..."/>`
  entries inside each `<url>`, mirroring the `<link hreflang>` tags in the head.
- **Blocking AI crawlers**: separate `User-agent: GPTBot`, `ClaudeBot`, `CCBot` blocks with
  `Disallow: /`. This is a policy choice, not an SEO one; it does not affect Google.
- **Staging**: serve `X-Robots-Tag: noindex` from the host config, or password-protect. Do not
  rely on `robots.txt` to hide a site; it is public and does not prevent indexing of linked URLs.

## Pitfalls

- `Disallow` for CSS, JS or image folders. Google renders pages; blocked assets mean a broken
  render and "mobile usability" errors. Only block admin, API, and faceted-URL spaces.
- Using `robots.txt` to remove pages from the index. Blocked pages can still be indexed from
  external links, with no snippet. Use `<meta name="robots" content="noindex">` and let the
  crawler fetch it; after it drops, you may block.
- Sitemaps that list redirecting, `noindex`, 404 or non-canonical URLs. Every entry should return
  200 and canonicalize to itself; Search Console reports anything else as "excluded".
- Redirect chains (`http` to `https` to `www` to trailing slash: three hops). Collapse to one
  redirect that lands on the final form; test with `curl -IL`.
- Case-sensitive hosts: `/About` and `/about` are different files on Linux hosts. Keep all file
  names lowercase and redirect uppercase requests if legacy links exist.
- Changing the trailing-slash setting after launch without redirects; every inbound link to the
  old form now 404s or duplicates. Decide once, before the first deploy.

## Related skills

- `web-seo-meta-tags`
- `web-seo-content-structure`
- `web-ship-static-hosting`
- `web-ship-launch-checklist`
- `web-ship-project-setup`
- `web-js-router-and-urls`
