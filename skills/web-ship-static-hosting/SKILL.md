---
name: web-ship-static-hosting
description: Deploy a built static site (`dist/`) to GitHub Pages, Netlify, Cloudflare Pages or Vercel - the exact config files (`deploy.yml`, `netlify.toml`, `_redirects`, `_headers`, `wrangler.jsonc`, `vercel.json`), custom domains, redirects, the 404 page, each host's gotchas. Use when a user says "deploy", "put it online", "host my site", "go live", "GitHub Pages", "Netlify", "Cloudflare Pages" or "Vercel".
---

# Static hosting

All four hosts do the same job: run `npm run build`, publish `dist/`, serve it from a CDN over HTTPS. Pick GitHub Pages when the repo is already there and you need nothing fancy; Netlify or Cloudflare Pages when you want form handling, redirects and headers from plain text files; Vercel when the rest of your work is there. The `dist/` layout from `web-ship-project-setup` deploys unchanged to all of them.

## Pattern

**GitHub Pages** (Actions build, no `gh-pages` branch needed; enable Settings > Pages > Source: GitHub Actions):

```yaml
# .github/workflows/deploy.yml
name: Deploy
on: { push: { branches: [main] } }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: { name: github-pages }
    steps:
      - id: d
        uses: actions/deploy-pages@v4
```

Project sites live at `https://user.github.io/repo/`; use relative asset paths (`./output.css`) or a custom domain (add a `CNAME` file containing the domain to `src/` so it is copied to `dist/`). `404.html` at the root is served automatically for missing paths.

**Netlify**:

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"
[[redirects]]
  from = "/old-page"
  to = "/new-page"
  status = 301
```

`dist/_redirects` (one rule per line: `/blog/* /articles/:splat 301`) and `dist/_headers` are also honoured; `404.html` in `dist/` is the not-found page. `netlify.toml` must sit at the repo root.

**Cloudflare Pages** (dashboard: build command `npm run build`, output `dist`; or the CLI):

```bash
npm i -D wrangler
npx wrangler pages deploy dist --project-name my-site
```

Reads the same `_redirects` and `_headers` files as Netlify. `404.html` is used as the not-found page. For Git integration you need no config file; for CLI-only deploys keep a `wrangler.jsonc` with `{ "name": "my-site", "pages_build_output_dir": "dist" }`.

**Vercel**:

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "cleanUrls": true,
  "trailingSlash": false,
  "redirects": [{ "source": "/old-page", "destination": "/new-page", "permanent": true }],
  "headers": [{ "source": "/(.*)\\.(css|js|woff2)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] }]
}
```

`npx vercel --prod` deploys from the terminal. `cleanUrls` serves `about.html` at `/about`.

Test the production build locally before pushing, on any OS:

```bash
npm run build && npx serve dist
```

## Variations

- **Clean URLs everywhere**: Netlify and Cloudflare serve `/about` from `about.html` by default; GitHub Pages does not (use `about/index.html` folders instead); Vercel needs `cleanUrls: true`. The folder-per-page layout works on all four.
- **Preview deploys per pull request**: Netlify, Cloudflare and Vercel do this out of the box once Git-connected; on GitHub Pages use a second workflow that deploys to a separate branch or skip it.
- **Custom domain**: add a `CNAME` (apex: `A`/`ALIAS`) record pointing at the host; all four issue a free TLS certificate. Set `www` to redirect to apex (or the reverse) in the host dashboard so there is one canonical URL for `web-seo-meta-tags`.
- **Forms without a backend**: Netlify Forms (`<form netlify>`), Cloudflare Pages Functions or a third-party endpoint (see `web-form-submit-with-fetch`).

## Pitfalls

- `dist/` is gitignored, so the host must run the build; pushing a prebuilt folder only works on GitHub Pages with the old branch method and goes stale fast.
- `npm ci` requires a committed `package-lock.json`; without it the CI build fails with a misleading error.
- GitHub Pages serves everything with `Cache-Control: max-age=600` and allows no custom headers, redirects or server-side rewrites. Need them? Pick another host or put Cloudflare in front.
- Case matters on every host (`Logo.png` is not `logo.png`), while Windows file systems hide this locally. Keep filenames lowercase.
- Netlify's `_redirects` and `_headers` must end up inside the publish folder (`dist/`), not the repo root; put them in `src/` so the copy step moves them.
- A `404.html` that links assets with relative paths breaks on nested missing URLs (`/a/b/c`); use absolute asset paths in the 404 page.
- Trailing-slash behaviour differs per host and splits SEO signals; pick one style, set it in the host config, and use the same form in `sitemap.xml` and canonical tags.

## Related skills

- `web-ship-project-setup`
- `web-ship-tailwind-production`
- `web-perf-caching-and-service-worker`
- `web-seo-sitemap-robots-urls`
- `web-seo-meta-tags`
- `web-ship-launch-checklist`
