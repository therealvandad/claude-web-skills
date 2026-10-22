---
name: web-craft-consistency-audit
description: Audit a Tailwind page for drift (distinct rounded-*, shadow-*, p-*, gap-*, text sizes, button variants), run scripts/vibe_check.py to count and flag generic tells, then fix by defining the allowed set as @theme tokens and replacing outliers. Use when a user says the site "looks inconsistent", "looks vibe coded", "looks AI generated" or "the spacing is all over the place".
---

# Consistency audit

Drift is how a page ends up with seven corner radii, five shadows, four button styles and eleven text sizes without anyone choosing any of them: each section was built on a different day, or by a different prompt, and each picked a plausible value. A reader cannot name the problem but feels it as "cheap". The audit is mechanical: count the distinct values in each family, decide the allowed set (usually three or four), make the set the only thing that exists as a token, then replace every outlier. Do the counting with the script, the deciding with your eyes, and the replacing with search-and-replace.

## Pattern

**1. Run the script first.** It ships with this skill and has no dependencies.

```bash
python <skill-dir>/scripts/vibe_check.py index.html          # one file
python <skill-dir>/scripts/vibe_check.py src/                 # every .html under a folder
python <skill-dir>/scripts/vibe_check.py src/ --json          # machine-readable
```

```
src/index.html  (1842 lines)  verdict: GENERIC
  - generic marketing words: 9  [seamless×3, unlock×2, elevate×2, effortless×1, robust×1]
  - purple/indigo/pink gradient backgrounds: 2
  - inline style= attributes: 7
  - long class strings repeated 3+ times (copy-pasted components): 2  [6× 'rounded-xl border border-gray-200 bg-white p-6 shadow-sm…']
  - nearly every section is centred: 7/8
  - style drift: too many distinct values: 3  [radius, shadow, text-size]
  drift: radius 7 distinct, shadow 5 distinct, padding 14 distinct, gap 8 distinct, text-size 11 distinct
```

Exit code 1 means the verdict is "generic", so `python vibe_check.py src/ && npm run build` gates a build. The thresholds it uses: more than 4 radii, 3 shadows, 12 paddings, 6 gaps or 8 text sizes is drift. Do not rewrite the script; if a check is wrong for this project, say so and move on.

**2. Read each finding against the page.** The script counts; it cannot see. For every family it flagged, open the page and answer: which of these values are *decisions* (hero heading, card radius) and which are *accidents* (one `rounded-2xl` on a badge that should match the other badges)? Also count by hand what the script does not: button variants (`grep -o 'class="[^"]*\bpx-[0-9.]* py-[0-9.]*[^"]*"' | sort | uniq -c`), icon sizes (`size-4`/`size-5`/`size-6`/`w-5 h-5`), and heading sizes per level (`<h2` followed by `text-*`).

**3. Define the allowed set as tokens.** The allowed set is small, and nothing outside it should be reachable by a plausible class name.

```css
/* input.css: three radii, three shadows, one button, one card. Everything else is an outlier by definition. */
@import "tailwindcss";
@theme {
  --radius-sm: 4px;  --radius-md: 8px;  --radius-lg: 14px;
  --shadow-sm: 0 1px 2px oklch(0% 0 0 / 6%);
  --shadow-md: 0 4px 12px -2px oklch(0% 0 0 / 10%), 0 1px 2px oklch(0% 0 0 / 6%);
  --shadow-lg: 0 20px 40px -12px oklch(0% 0 0 / 18%);
  --text-display: 3rem;   --text-display--line-height: 1.05;
  --text-h2: 1.875rem;    --text-h2--line-height: 1.15;
  --text-h3: 1.25rem;     --text-h3--line-height: 1.3;
}
@utility card { @apply rounded-lg bg-white p-6 ring-1 ring-black/5; }
@utility btn  { @apply inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-medium; }
@utility btn-primary { @apply btn bg-ink text-white hover:bg-stone-800; }
@utility btn-ghost   { @apply btn text-ink hover:bg-stone-100; }
```

**4. Replace outliers.** Mechanical, family by family, then re-run the script.

```bash
# radius: collapse 7 values to 3 (xl/2xl/3xl → lg; sm/none stay; md stays)
sed -i -E 's/\brounded-(xl|2xl|3xl)\b/rounded-lg/g' src/**/*.html
# shadow: anything bigger than lg is lg
sed -i -E 's/\bshadow-(xl|2xl)\b/shadow-lg/g' src/**/*.html
# gaps between siblings: 3/5/7 are the accidents, 4/6/8 are the scale
sed -i -E 's/\bgap-(3|5)\b/gap-4/g; s/\bgap-7\b/gap-6/g' src/**/*.html
python <skill-dir>/scripts/vibe_check.py src/
```

Then by hand, since these need judgment: every `<h2>` gets `text-h2`, every `<h3>` gets `text-h3`, every button gets `btn-primary` or `btn-ghost` and loses its pasted string, every icon gets one of two sizes.

## Variations

- **Dashboard pages.** Allowed sets are tighter still: one radius (`rounded-md`), one shadow (dropdowns only), two text sizes (`text-sm` for everything, `text-xs` for meta). Tables and forms drift fastest; audit them separately.
- **Marketing pages.** Allow one deliberate exception per family (a `rounded-full` pill in the hero, one `shadow-lg` on the product screenshot) and write it down in a comment at the top of `input.css`, so the next audit does not "fix" it.
- **Multi-page sites.** Run the script on the folder and compare the `drift` block per file in `--json`; a page whose counts are double the others was built separately and needs the pass first.
- **Gate in CI.** `python scripts/vibe_check.py dist/ || exit 1` after the build. Pair with `web-ship-launch-checklist`.

## Pitfalls

- Fixing drift by adding more tokens ("we use 2xl on cards and xl on inputs and lg on buttons and md on badges") is drift with names. Three radii cover a whole site: small controls, buttons, containers.
- `sed` across HTML will also hit class strings inside `<code>` samples, comments and JS template literals; review the diff before committing, and never run the replacements on `dist/`.
- The script's "generic words" list is for visible copy; a word in an `alt` or a `<code>` block is not a problem. Read the finding, do not blindly delete words.
- Distinct `p-*` counts are naturally high (padding on buttons, cards, sections, inputs all differ); the 12 threshold is deliberately loose. Worry about `gap-*` and `rounded-*` first, they are the visible ones.
- The verdict is a heuristic: a clean page with eight `<section>`s that are all centred will be marked "mixed". Use the findings, not the label, in the conversation with the user.
- Collapsing text sizes without checking line-heights produces headings that are now the right size and the wrong leading; use the `--text-*--line-height` pair in `@theme` so size and leading travel together.

## Related skills

- `web-css-spacing-scale`
- `web-design-borders-radius-dividers`
- `web-design-shadows-and-elevation`
- `web-design-typography-system`
- `web-craft-code-structure`
- `web-craft-anti-generic-design`
- `web-craft-self-review`
