# web-skills

207 Claude Code skills for building web sites with **plain HTML, CSS, JavaScript and Tailwind CSS v4**.
No frameworks. Each skill is one folder with a `SKILL.md`: a short, copy-pasteable pattern, the
reasoning behind it, variations and pitfalls. Claude picks a skill automatically when a request
matches its description ("make me a pricing table", "the navbar breaks on mobile", "add dark mode").

## Groups

| Prefix | What | Count |
|---|---|---|
| `web-layout-*` | page shells, hero, features, pricing, testimonials, footer, dashboard, landing page, card grids, split sections | 10 |
| `web-css-*` | grid, flexbox, container queries, fluid type, spacing, aspect ratio, sticky, variables and `@theme`, reset, layers | 10 |
| `web-nav-*` | navbar, mega menu, sidebar, breadcrumbs, tabs, pagination, dropdowns, sticky header, scroll spy, anchors | 10 |
| `web-form-*` | layout, validation, input states, select and combobox, file upload, multi-step, search, choices, fetch submit, passwords | 10 |
| `web-ui-*` | dialog, toasts, accordion, tooltip and popover, carousel, data table, cards, badges, skeletons, buttons | 10 |
| `web-design-*` | typography, color, dark mode, icons, images, shadows, borders, empty states, tokens to Tailwind, polish checklist | 10 |
| `web-motion-*` | transitions, keyframes, scroll reveal, view transitions, hover, loading, scroll-driven, page transitions, reduced motion, counters | 10 |
| `web-a11y-*`, `web-seo-*` | semantics, ARIA, keyboard and focus, contrast, skip links, media; meta tags, structured data, sitemap and robots, content structure | 10 |
| `web-perf-*`, `web-ship-*` | images, fonts, CSS and JS loading, web vitals, caching; project setup, Tailwind production build, static hosting, analytics, launch checklist | 10 |
| `web-js-*` | DOM utilities, fetch, state and render, storage, events, modules, web components, errors, clean code, router and URLs | 10 |
| `web-page-*` | whole pages: blog post, blog index, portfolio and case study, about and team, contact, product detail, docs, login and signup, help centre, 404 and legal | 10 |
| `web-section-*` | reusable sections: stats band, logo cloud, CTA band, steps and timeline, comparison table, bento grid, gallery and lightbox, team grid, newsletter, before/after slider | 10 |
| `web-interactive-*` | app-like features with no framework: live search, URL-synced filters, calculators, kanban, markdown editor, quiz, sortable lists, timers, Leaflet map, command palette | 10 |
| `web-ecommerce-*` | shop on a static site: cart, catalogue filters, Stripe checkout in test mode, wishlist, order status, promo codes, variants and stock, reviews, shipping and tax, honest trust signals | 10 |
| `web-data-*` | charts without a library: SVG bar and line charts, sparklines, donuts, KPI dashboard, table export, calendar heatmap, number formatting, fetch and cache, chart accessibility | 10 |
| `web-theme-*` | ready-made looks: editorial, Swiss, brutalist, terminal, pastel, luxury, corporate, nature, retro, and a theme switcher | 10 |
| `web-i18n-*`, `web-content-*` | languages, RTL, locale formatting, translation strings, fonts per script; Markdown pipeline, static blog generator, partials build, image pipeline, sitemap and feeds | 10 |
| `web-pwa-*` | installable apps: manifest, offline service worker, install prompt, push, icons and splash, offline forms, update flow, share and files, IndexedDB, testing | 10 |
| `web-email-*` | HTML email that survives Outlook: table layout, type and buttons, images, dark mode, responsive, Outlook fixes, transactional and newsletter templates, deliverability, plain text | 10 |
| `web-tool-*` | runnable tools: a full site audit report, a component gallery from your own pages, headless screenshot diffs at three widths | 3 |
| `web-flow-*` | workflows: scaffold a new site, ship it (validate, build, commit, deploy), a theme from a screenshot, an explainer page for a codebase | 4 |
| `web-craft-*` | not looking vibe-coded: anti-generic design, typography with character, human copy, intentional layout, colour restraint, finishing details, real content, code structure, a consistency audit with `vibe_check.py`, a self-review ritual | 10 |

The full list with one-line summaries is in [SKILL-LIST.md](SKILL-LIST.md).

## Install

Get the pack:

```bash
git clone https://github.com/therealvandad/claude-web-skills.git
cd claude-web-skills
```

Everything, for every project on this machine:

```bash
python install.py
```

Only some groups (the skill list is loaded into every Claude session, so fewer skills means less
context used):

```bash
python install.py --only layout page section nav form ui craft tool
```

Into one project only:

```bash
python install.py --project C:\path\to\my-site
```

Remove:

```bash
python install.py --uninstall
```

The folder is also a valid Claude Code plugin (`.claude-plugin/plugin.json`), so it can be loaded
with `claude --plugin-dir <this folder>` without copying anything.

## Writing or changing skills

`CONVENTIONS.md` is the style guide every skill follows. After editing, run:

```bash
python tools/validate.py
```

It checks frontmatter, required sections, lengths, and that related-skill names exist.

## License

MIT. See [LICENSE](LICENSE).
