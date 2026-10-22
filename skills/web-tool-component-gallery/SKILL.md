---
name: web-tool-component-gallery
description: Scan a folder of HTML pages with scripts/component_gallery.py and render every header, footer and top-level section as a living style guide, each in its own iframe with a width toggle and a copy button. Use when a user says "style guide of my components", "show me every section", "component library from my pages" or "find duplicate sections".
---

# Component gallery

A site built page by page ends up with the same section copied four times with small differences. Nobody sees that while reading one file at a time. The gallery pulls every header, footer and top-level `<section>` out of every page, drops exact duplicates, and shows each one rendered, at the widths people actually use. That is a style guide generated from the real site, not a hand-drawn one that drifts from it. Standard library only (Python 3.10+); open the output in a browser, no server needed.

## Pattern

```bash
python <skill-dir>/scripts/component_gallery.py demo-site/ --out gallery.html
```

Output, and exit code 0 (1 if nothing was found, 2 for a bad folder):

```
component gallery: 4 page(s) scanned, 24 components found, 16 unique after dedup
gallery: C:\...\gallery.html
```

On the demo site, 24 components across four pages collapse to 16 because `index.html` is a copy of `before.html`.

**What it extracts.** From every page: the `<header>` and `<footer>` that are not inside a section, article, nav or similar, plus every `<section>` that is not nested in another section, article, header or footer. Nested pieces (cards, list items) stay inside their parent.

**What each card shows.** A label (the first heading, or `Site header` / `Site footer`, or the id), the tag and `file:line`, and "also in" with the other files that contain identical markup. Buttons switch the preview to 375, 768, 1280 or Fit; the top bar sets all cards at once or filters by source file. Copy HTML puts the component markup on the clipboard. A collapsed Source block shows the same markup. Each preview is an `<iframe srcdoc>` that carries the source page's whole `<head>` (Tailwind script, `@theme` block, fonts, stylesheets) plus the wrappers the component sat in, so it renders as on the real page.

**What to do with it.**

1. Run it, open the report, scroll once. Tell the user how many components and how many unique ones there are.
2. Components that appear twice with a small difference (not listed as "also in" because they are not identical) are the real finding: near-duplicates should become one shared partial. Compare their source blocks and propose one version (see `web-craft-code-structure`).
3. A card that looks broken at 375 is a responsive bug in that section; fix it with the matching layout skill.
4. A card that looks unlike its neighbours (other radius, other button) is drift: continue with `web-craft-consistency-audit`.
5. Use Copy HTML when the user asks to reuse a section on a new page; paste, then change the copy.

## Variations

- **One site area.** Point it at a subfolder (`src/pages/`) to gallery only those pages.
- **Gallery per branch.** Run it on two checkouts into two files and open them side by side.
- **Design review.** Send the single HTML file to a reviewer; it works from `file://`, and the Tailwind CDN script needs a network connection to render.
- **Sections only.** Use the All files filter, then pick a page button to hide the rest.

## Pitfalls

- Pages that build sections with JavaScript have nothing to extract; run it on the pre-rendered output.
- Previews load the page's `<head>`, so a Tailwind CDN script or Google Fonts need a network connection. Offline, the cards render unstyled.
- Links inside previews are disabled on purpose, so a click cannot navigate the frame away.
- Preview height follows the content after load; a section that animates in may be measured short, then grow. Reload the report if one looks cut off.
- Only exact duplicates (same markup apart from whitespace) are merged. A section with different text is a different component here.
- Do not write the gallery into the site folder: it would be scanned on the next run and could ship.

## Related skills

- `web-craft-code-structure`
- `web-craft-consistency-audit`
- `web-design-ui-polish-checklist`
- `web-design-tokens-to-tailwind`
- `web-tool-site-audit`
- `web-tool-screenshot-diff`
