---
name: web-tool-site-audit
description: Audit a folder of HTML pages or a live URL with scripts/site_audit.py to get one report on broken links, image alt and weight, inline contrast, meta tags, heading outline, unlabeled form fields and a vibe check. Use when a user says "audit my site", "check my site before I ship", "find broken links" or "what is wrong with this site".
---

# Site audit

A manual review misses the boring failures: a link to a page that was renamed, an image with no alt, a form field with only a placeholder, a page with no `<h1>`. `site_audit.py` finds those mechanically across every page, writes one HTML report, and exits non-zero when there are errors, so it also works as a deploy gate. It uses only the standard library (Python 3.10+) and reuses `vibe_check.py` from `web-craft-consistency-audit`, which it finds relative to its own path, so keep the pack's `skills/` folder together.

## Pattern

Run it on the site folder (or a URL) and write the report somewhere outside the site, so the report is never audited or deployed.

```bash
python <skill-dir>/scripts/site_audit.py demo-site/ --out audit.html
python <skill-dir>/scripts/site_audit.py https://example.com --max-pages 30 --out audit.html
python <skill-dir>/scripts/site_audit.py dist/ --json > findings.json   # JSON on stdout, summary on stderr
```

Terminal output, then the exit code (0 clean, 1 at least one error, 2 bad arguments):

```
site audit: 4 pages from demo-site
  after.html    score 100   0 errors   0 warnings    20 KB  vibe: clean
  compare.html  score  87   1 errors   1 warnings    52 KB  vibe: clean
errors:
  compare.html  [headings] no <h1>; every page needs exactly one
report: C:\...\audit.html
```

**Reading the report.** The top table lists each page with a score (100, minus 10 per error, minus 3 per warning), counts, weight and the vibe verdict. Below it, one table per page lists findings sorted error, warning, info, each with its check name and a line number where one exists. Open the report only if the terminal summary is not enough; the summary already lists every error.

**What to do with each finding.**

- `links`, `files` (error): a broken link, missing anchor id or missing file. Fix the `href` or restore the file; if the target was renamed, search the whole site for the old name.
- `images` (error: no `alt`): write real alt text (see `web-a11y-images-and-media`); `alt=""` is correct only for decoration. Warnings for missing `width`/`height` mean layout shift: add the intrinsic size. Over 300 KB: resize and compress (see `web-perf-images`).
- `contrast` (error under 3:1, warning under 4.5:1): change the inline colours using `web-a11y-color-contrast`. Only inline `style=""` colours are measured; Tailwind classes are not, so check those by eye.
- `title`, `description`, `viewport`, `lang`, `canonical`: add the missing tag, once per page. See `web-seo-meta-tags`. Canonical is info only: add it before launch.
- `headings`: one `<h1>`, no skipped levels, no empty headings. Fix the markup (see `web-a11y-semantic-html`), not the font size.
- `forms` (error): every input needs a `<label>`, wrapping or `for=`, or an `aria-label`. A placeholder is not a label.
- `vibe` and `weight` (warning/info): context. A GENERIC verdict means run `web-craft-consistency-audit`; do not "fix" these inside the audit.

After fixing, re-run the same command and confirm the error count fell. Report remaining warnings to the user instead of silently fixing them all.

## Variations

- **One file.** Pass a single `.html` path; links to other files are still resolved from its folder.
- **Live URL.** The crawl follows same-origin links from the start page up to `--max-pages` (default 20), checks status codes with HEAD, and measures same-origin images and CSS. External links and third-party scripts are not fetched.
- **CI gate.** `python site_audit.py dist/ --out audit.html || exit 1`, then upload `audit.html` as a build artifact. Pair with `web-ship-launch-checklist`.
- **Before and after a redesign.** Audit both versions and compare the scores; for the visual side use `web-tool-screenshot-diff`.

## Pitfalls

- Do not write the report into the folder being audited: the next run would audit it, and it would ship.
- A score of 100 only means these checks passed. It does not cover keyboard use, real contrast on Tailwind-styled text, or whether the copy is any good.
- Pages built by JavaScript at runtime have no static `<h1>` or labels for the script to see; audit the rendered output or the pre-render folder.
- Root-relative links (`/about`) resolve against the folder you passed, so audit the folder that is deployed (`dist/`), not the project root.
- Clean URLs work: `/about` matches `about.html`, and a folder link matches its `index.html`.
- In URL mode `/` and `/index.html` are audited as two pages; ignore the duplicate rows.

## Related skills

- `web-craft-consistency-audit`
- `web-a11y-semantic-html`
- `web-a11y-color-contrast`
- `web-a11y-images-and-media`
- `web-seo-meta-tags`
- `web-perf-images`
- `web-ship-launch-checklist`
- `web-tool-screenshot-diff`
