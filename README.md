# web-skills

207 Claude skills for building web sites with **plain HTML, CSS, JavaScript and Tailwind CSS v4**, plus 6 standalone skills.
No frameworks. Each skill is one folder with a `SKILL.md`: a short, copy-pasteable pattern, the
reasoning behind it, variations and pitfalls. Claude picks a skill automatically when a request
matches its description ("make me a pricing table", "the navbar breaks on mobile", "add dark mode").

## How to install

> [!IMPORTANT]
> **There are two different places to add skills, and they take different files.**
> **On claude.ai or the Claude desktop app, upload the PLUGIN zips on the Plugins page, not the Skills page.**
> **The Skills page accepts only one skill per zip and will reject these.**

### Option 1: claude.ai or the Claude desktop app (no coding)

1. **Download the three plugin zips** from the [latest release](https://github.com/therealvandad/claude-web-skills/releases/latest):
   - **`web-skills-design-plugin.zip`**: 100 skills for layouts, pages, sections, CSS, navigation, forms, UI, design, motion and craft
   - **`web-skills-build-plugin.zip`**: 107 skills for features, e-commerce, charts, themes, languages, PWA, email, tools and workflows
   - **`creator-tools-plugin.zip`**: 6 standalone skills (memory-brain, skill-brain, session-timeline, windows-tray-app, arduino-serial, readme-and-release)
2. **Go to [claude.ai/customize/plugins](https://claude.ai/customize/plugins)** (Customize, then **Plugins**).
3. **Click Add, then Upload plugin, and choose one zip.** Repeat for the other two.
4. **Turn on code execution** in your settings if it is off; skills need it.
5. **Do not unzip the files**, and **do not upload them on the Skills page**.

Only want some of them? Upload just the plugin you need. Every installed skill's description is read in each chat, so fewer skills keeps Claude quick.

### Option 2: Claude Code (terminal or the Code tab)

```bash
git clone https://github.com/therealvandad/claude-web-skills.git
cd claude-web-skills
python install.py
python claude-skills/install.py
```

**That copies every skill into `~/.claude/skills/`, so they work in every project. Start a new session to pick them up.**

Install only some groups, into one project, or remove them again:

```bash
python install.py --only layout page section nav form ui craft
python install.py --project C:\path	o\my-site
python install.py --uninstall
```

The folder is also a Claude Code plugin, so `claude --plugin-dir <this folder>` loads it without copying.

### Option 3: one single skill on the Skills page

The Skills page wants **one skill per zip, with the skill folder at the top**. Zip a single folder from `skills/` (for example `skills/web-layout-hero/`) **from its parent folder**, then upload it under **Customize, then Skills, then Upload a skill**.

### Rebuild the plugin zips yourself

```bash
python tools/build_plugins.py
```

This writes the three zips to `dist/`, each under the 200-file upload limit.

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

## Standalone skills

The `claude-skills/` folder holds six skills that are not about web sites: `memory-brain` (graph of your Claude memories), `skill-brain` (graph of
your installed skills), `session-timeline` (timeline of your Claude Code sessions), `windows-tray-app`,
`arduino-serial` and `readme-and-release`. Install them with:

```bash
python claude-skills/install.py
```

## Writing or changing skills

`CONVENTIONS.md` is the style guide every skill follows. After editing, run:

```bash
python tools/validate.py
```

It checks frontmatter, required sections, lengths, and that related-skill names exist.

## License

MIT. See [LICENSE](LICENSE).
