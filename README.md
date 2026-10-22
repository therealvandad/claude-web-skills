# web-skills

110 Claude Code skills for building web sites with **plain HTML, CSS, JavaScript and Tailwind CSS v4**.
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
python install.py --only layout nav form ui craft
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
