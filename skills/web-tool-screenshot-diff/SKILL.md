---
name: web-tool-screenshot-diff
description: Screenshot two pages (files or URLs) in headless Chrome or Edge at 375, 768 and 1280 px with scripts/screenshot_diff.py, then write a side-by-side page with a changed-pixel percentage and a red diff image. Use when a user says "what changed visually", "before and after", "did my CSS change break anything" or "compare staging to production".
---

# Screenshot diff

Code diffs do not show what a reader sees. A one-line spacing change can shift every section below it, and a dependency bump can change fonts nobody touched. This skill renders A and B in a real browser at phone, tablet and desktop widths, compares them pixel by pixel with Pillow, and writes one page with both screenshots and a diff. It needs Pillow (`pip install pillow`) and Chrome or Edge. It looks for Chrome in `C:\Program Files\Google\Chrome\Application\chrome.exe`, then Edge in `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`, then `chrome`, `msedge` or `chromium` on PATH.

## Pattern

Make the "before" copy first (a copy of the file, a git stash, or the production URL), then change the page, then run:

```bash
python <skill-dir>/scripts/screenshot_diff.py demo-site/before.html demo-site/after.html --out diff.html
```

Output and exit code (0 normally; 1 only with `--fail-above` when a width exceeds it; the script exits with a message when no browser is found or a screenshot fails):

```
screenshot diff: demo-site/before.html  vs  demo-site/after.html  (browser: chrome.exe)
      375 px   90.12% changed  (743,489 of 825,000 pixels)
      768 px   92.32% changed  (1,559,902 of 1,689,600 pixels)
     1280 px   82.56% changed  (2,325,030 of 2,816,000 pixels)
report: C:\...\diff.html
```

Those numbers are a complete redesign. Identical pages give `0.00%`. The PNGs are saved next to the report in `<out stem>-shots/`, so keep the folder with the report.

**Reading the report.** A table gives the percentage per width. Each width has three images: A, B, and a diff where unchanged areas are faded and changed pixels are red. A pixel counts as changed when any colour channel differs by more than `--threshold` (default 10 of 255), which ignores anti-aliasing noise. Each shot is the top 2200 px of the page; content below that is not compared.

**What to do with each result.**

- **0.00 to 0.05%**: unchanged. Say so and stop.
- **Small, scattered red** (under about 5%): intended edits, or font hinting. Confirm the red areas match what the user changed.
- **A red band that starts at one point and continues to the bottom**: something above it changed height and pushed the rest down. Find the first changed element and check its spacing or line wrap.
- **Red at 375 but not at 1280**: a responsive regression. Open the B screenshot at that width and fix the breakpoint classes.
- **Everything red**: a theme, font or background change, or a different page. Check both inputs were the pages you meant, and that fonts loaded.
- When the change was unintended, name the likely cause and fix it. When intended, tell the user the percentage per width and which sections moved.

## Variations

- **Two environments.** `python screenshot_diff.py https://staging.example.com https://example.com --widths 375,1280`.
- **Gate a refactor.** The CSS or markup should change nothing visible: `--fail-above 0.5` returns exit code 1 if any width differs by more than 0.5%.
- **Dark mode check.** `--scheme dark` renders both pages with a dark colour scheme; the default `light` pins the browser to light, so results do not depend on the OS theme. `--scheme system` follows the OS.
- **Stricter or looser.** `--threshold 3` catches faint colour shifts; `--threshold 30` ignores them.

## Pitfalls

- Animated, randomised or time-based content (carousels, "posted 3 minutes ago", ads) always differs. Mask it or accept a baseline of a few percent.
- Web fonts and the Tailwind CDN script must load: the script gives the page a virtual 8-second budget, but a blocked network gives fallback fonts and a false diff. Compare like with like.
- Sticky headers and scroll-triggered reveals appear in their top-of-page state only; sections hidden until scroll may be blank in both shots.
- A page taller than 2200 px is cut off; changes below that are invisible to the percentage.
- The script uses a throwaway browser profile, so an open Chrome window does not interfere; do not point `--out` into the site folder.
- A percentage is not a verdict. Look at the diff image before telling the user a change is safe.

## Related skills

- `web-tool-site-audit`
- `web-tool-component-gallery`
- `web-craft-self-review`
- `web-design-ui-polish-checklist`
- `web-ship-launch-checklist`
