---
name: web-flow-new-site
description: Scaffold a new plain HTML + Tailwind v4 site. Ask four questions first (what, for whom, which pages, which tone), then run scripts/new_site.py to write pages, a tone-matched @theme, package.json, README and a GitHub Pages workflow. Use when a user says "new website", "start a new site", "build me a site", "scaffold a project" or "set up a landing page".
---

# New site

A blank folder invites the generic default: gray palette, Inter, three identical cards. This workflow removes the blank page. Ask four short questions, then let `scripts/new_site.py` write a working project whose palette, fonts and copy already match the answers, with the pack's craft rules built in (one hue, three radii, numbered eyebrows, skip link, real-sounding content). You then spend your time replacing placeholder copy with the user's facts instead of fighting a template.

## Pattern

**1. Ask four questions, in one message, before writing anything.** Offer a default for each so the user can answer "you choose".

1. **What is it?** One sentence: what the site is about and what a visitor should do (buy, book, read, sign up). Decides `--kind`: `landing`, `blog`, `portfolio`, `docs` or `shop`.
2. **For whom?** The one person you are writing to (a café owner, a hiring manager, a developer on a deadline). Sets the vocabulary of every sentence you write afterwards.
3. **Which pages?** From `home about contact pricing blog docs work shop faq`, or any other word for a plain page. Default per kind: landing `home,about,pricing,contact`; blog `home,about,contact`; portfolio `home,work,about,contact`; docs `home,docs,about`; shop `home,shop,about,contact`.
4. **Which tone?** `editorial` (warm serif, terracotta), `swiss` (neutral grotesque, one red), `corporate` (calm blue, serif headings), `playful` (amber, chunky display face), `terminal` (dark, mono, phosphor green). Show the one-line descriptions and recommend one.

**2. Run the script.** Standard library only. `--out` must not already contain `src/`; add `--force` to overwrite.

```bash
python <skill-dir>/scripts/new_site.py --name "Ember Roasters" --kind landing --pages home,about,contact --tone editorial --out ./ember
```

It writes `src/index.html`, `src/about.html`, `src/contact.html`, `src/404.html`, `src/input.css`, `src/js/main.js`, `scripts/copy.mjs`, `package.json`, `.gitignore`, `.editorconfig`, `README.md` and `.github/workflows/deploy.yml`, and prints each file with its line count.

**3. Install and build once to prove it works.**

```bash
cd ember
npm install       # @tailwindcss/cli, serve, concurrently; creates package-lock.json
npm run build     # copies src/ to dist/ and writes dist/output.css (about 19 KB)
npm run dev       # watcher + http://localhost:3000
```

**4. Make it theirs, in this order.** The scaffold's copy is believable but invented for the name: the city, the launch date and the numbers are placeholders. Rewrite the hero first using the user's real facts, replace the grey figure panels with real photos, then wire the forms (they show a notice and send nothing). The generated `README.md` lists the skill to read for every section.

**5. Hand over to the next workflow.** When it reads right, run `web-flow-ship-it`.

## Variations

- **Tone is the only styling switch.** `src/input.css` holds one `--hue` and every colour token is `oklch(... var(--hue))`. Changing the number recolours the whole site; a different tone changes fonts, radii and weight too, so switch tone by scaffolding again into a new folder rather than editing five files by hand.
- **Kind decides home sections.** `blog` gets posts and a newsletter, `portfolio` gets work and a contact form, `docs` gets a quickstart and guides, `shop` gets a product grid. These page names get their own layout: `about`, `contact`, `pricing`, `blog`, `docs` (sidebar shell), `work`, `shop`, `faq`. Any other word gets a plain prose page.
- **Existing project.** Scaffold into a scratch folder and copy only `src/input.css` and the sections you want. Never run the script with `--force` over real work.
- **Play CDN prototype.** For a throwaway demo skip the CLI and load the Play CDN script `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4`; the scaffold is for sites that will be deployed.

## Pitfalls

- Do not skip the questions to "save a turn". A tone chosen by the script's default is a tone nobody chose, and the copy is written around the name only.
- The scaffold is a starting point, not a finished site. Shipping it untouched leaves invented details (a city, a date, "2 people") in public. Grep for them before `web-flow-ship-it`.
- Pages that are not in the list are not linked: the navbar and footer only point to pages that exist, so a missing `pricing` page falls back to the contact link instead of a dead URL. Add the page, then re-link by hand.
- `npm run build` needs Node 20 or newer. If `npm install` is blocked, the `src/` files still open in a browser only after a build, because `output.css` does not exist until Tailwind has run.
- Keep the generated `package-lock.json`; the deploy workflow runs `npm ci` and fails without it.
- The contact address (`hello@<slug>.example`) is a placeholder and the forms post nowhere. Replace both before the site goes live.

## Related skills

- `web-flow-ship-it`
- `web-ship-project-setup`
- `web-layout-landing-page`
- `web-craft-real-content`
- `web-craft-copy-that-sounds-human`
- `web-craft-color-with-restraint`
- `web-craft-typography-with-character`
- `web-css-modern-reset`
