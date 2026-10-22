---
name: web-flow-explain-my-site
description: Explain a plain HTML + Tailwind site as one readable page. Run scripts/explain_site.py for a file map, per-page sections, assets and links, a page-to-page link table and a where-to-change-what table, then write a plain-English narrative on top. Use when a user says "explain this codebase", "how does my site work", "where do I change" or "give me a tour".
---

# Explain my site

Someone inherits a vibe-coded folder, or comes back to their own site after three months, and cannot tell what is a page, what is generated, or where the footer lives. Reading every file wastes your context and theirs. The script reads the files and produces the facts (what exists, what loads what, what links where, which line to edit); you add the part a script cannot, which is the plain-English story. Facts from the script, prose from you, never the other way round.

## Pattern

**1. Run the script. Write the report outside the site folder.** Standard library only; it never writes inside the folder it reads.

```bash
python <skill-dir>/scripts/explain_site.py ./demo-site --out ./explain.html
```

```
demo-site: 4 files, 4 pages, 60 links, 0 broken
  after.html     Driftwood: static hosting for people who write HTML  [9 sections, 2 assets, 12 links]
  before.html    Driftwood: ship your website in an afternoon  [14 sections, 1 assets, 23 links]
  compare.html   Driftwood: before and after the craft skills  [2 sections, 2 assets, 2 links]
  index.html     Driftwood: ship your website in an afternoon  [14 sections, 1 assets, 23 links]
  note: index.html is byte-identical to before.html
wrote ./explain.html
```

If the folder has `src/` with HTML, pages are read from `src/`; otherwise from the folder. `node_modules`, `dist`, `.git`, `build` and similar are skipped and named in the report. Exit code 2 means the folder or the narrative file does not exist.

**2. Read the output before you write anything.** `explain.html` has five parts:

| Part | What it tells you |
|---|---|
| File map | every file, its role (page, Tailwind source CSS, built CSS, script, config, workflow), size, line count, and a flag for byte-identical copies |
| Pages | per page: title, description, `h1`, language; a table of sections (element, id, heading, the author's comment, line); loaded assets (CDN, fonts, local files, inline scripts and styles, whether `output.css` is built later); every link with its destination |
| Links between pages | a matrix and an edge list, pages nothing links to, broken links and `#anchors`, external hosts |
| Where to change what | titles, descriptions, `@theme` tokens, navigation, header, footer, each section, behaviour, fonts, deploy and build settings, each with `file:line` |
| Plain-English tour | an empty slot until you fill it |

**3. Write the narrative on top of the output.** Plain English for someone who has never opened the folder, no jargon without a gloss. Cover, in this order: what the site is in one sentence; how a page is built (one HTML file per page, Tailwind classes on the elements, tokens in `@theme`); how styles reach the browser (Play CDN script, or CLI build into `output.css`); what the JavaScript does; the one or two things that surprise (the same navbar copied into every page, two identical files, a page nothing links to); and the three edits the owner is most likely to make, with `file:line` taken from the "Where to change what" table. Do not invent anything the report does not show; open a file only to check a claim.

**4. Put it into the page.** Save the prose as a text file (blank line starts a paragraph, a line beginning `## ` is a subheading) and run again. The text is escaped, so keep it plain.

```bash
python <skill-dir>/scripts/explain_site.py ./demo-site --out ./explain.html --narrative ./tour.txt --title "Driftwood"
```

Open `explain.html` in a browser and tell the user where it is. Summarise the three biggest findings in the chat too; do not make them open a file to learn the headline.

## Variations

- **Tailwind CLI site.** The report shows `src/input.css` as "Tailwind source CSS" with its token count, `output.css` as "written by the build step", and the `package.json` scripts, so the tour can say "edit `src/`, run `npm run build`".
- **Play CDN site.** The "How Tailwind runs" row says the script tag is in N pages, which is your cue to mention `web-ship-tailwind-production`.
- **Handover for a team.** Add a "Before you change anything" paragraph with the commands from `package.json` and the deploy workflow named in the report.
- **Cleanup next.** If the tour exposes copy-pasted headers, duplicate files or huge pages, finish by offering `web-craft-code-structure` rather than fixing things during an explanation.

## Pitfalls

- The script describes structure, not quality. It cannot say a design is good or a sentence is true; leave judgement to a review skill.
- Pages are found by `.html` files only. A site generated at build time from Markdown or partials shows its sources as plain files; say that the real pages appear after the build (`web-content-partials-build`).
- "Repeated in N files" for navigation and footer means the header is copied, not shared. Mention it as a cost, with the fix, but do not change it during an explanation.
- A link counted as broken is one that does not resolve from the page's folder. Root-relative links (`/about.html`) are resolved against the HTML root, so check hosting rules before calling them wrong.
- Never write `--out` inside the site folder; it would show up as a page on the next run and could be deployed.
- Keep the narrative short. A tour that is longer than the report it summarises will not be read.

## Related skills

- `web-craft-code-structure`
- `web-ship-project-setup`
- `web-content-partials-build`
- `web-flow-new-site`
- `web-craft-consistency-audit`
- `web-flow-ship-it`
