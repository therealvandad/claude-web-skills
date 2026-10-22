---
name: web-flow-design-from-screenshot
description: Turn a screenshot of a site you admire into a Tailwind v4 @theme block with scripts/palette_from_image.py (Pillow), plus a type scale and spacing rhythm read by eye. Borrow the mood only, never the content, layout or logo. Use when a user says "make it look like this screenshot", "match this site's style", "I like this design" or "use these colors".
---

# Design from a screenshot

A screenshot is a fast way to say "this feeling" when words fail. The risk is copying: the same headline order, the same layout, the same logo treatment is plagiarism and makes a worse site, because the structure was built for someone else's content. So extract only the transferable mood: a restrained palette, how loose or tight the type is, how much air sits between sections. Leave everything else behind.

**Borrow the mood only. Never the content, the layout or the logo.** Do not reuse their words, their section order, their grid, their images, their icons or their brand mark, and do not name the source site in the code or copy.

## Pattern

**1. Look first, then run the script.** Open the image and write down in plain words what it feels like (warm, dense, quiet, loud, technical). That sentence is the brief; the numbers below serve it.

```bash
python <skill-dir>/scripts/palette_from_image.py shot.png --count 8 --out theme.css
```

Needs Pillow (`python -m pip install pillow`). It quantizes the image, merges near-duplicate colours, converts sRGB to OKLCH, and prints the share of the screen each colour covers. Then it picks four roles: `paper` (largest area), `ink` (best lightness contrast against paper, synthesized when nothing reaches 7:1), `accent` (the most saturated colour with a visible share) and `line`, plus derived `paper-2`, `ink-2`, `accent-deep` and `accent-tint`. It reports contrast ratios and writes `theme.css` and `theme.html` (a swatch preview with the roles applied). Without `--out` it writes `palette-preview.html` into the current folder, so run it from a scratch folder, not the site.

```css
/* Palette borrowed from shot.png: mood only. Re-check every pair with web-a11y-color-contrast. */
@theme {
  --color-paper:        oklch(96.3% 0.012 79.8);
  --color-ink:          oklch(23.8% 0.010 67.3);
  --color-ink-2:        oklch(48.8% 0.010 67.3);
  --color-line:         oklch(92.2% 0.018 78.2);
  --color-accent:       oklch(47.8% 0.074 43.8);
  --color-accent-deep:  oklch(47.8% 0.074 43.8);
  --color-accent-tint:  oklch(92.3% 0.042 43.8);
}
```

The token names match `web-flow-new-site`, so the block pastes straight into `src/input.css` in place of that file's colour tokens.

**2. Judge the result against the image, not the numbers.** Open `theme.html` beside the screenshot. If the accent is the wrong colour (a photo's sky beat the button), pick the right swatch from the printed list and edit the one line. Keep one accent; extra hues are for state only (`web-craft-color-with-restraint`).

**3. Read the type and rhythm by eye.** The script does not measure these. Answer four questions and write each as a token or a rule:

- **Heading to body ratio.** Roughly 3x, 4x or 6x? Set `--text-display` and `--text-title` to match, as a `clamp()` pair.
- **Weight and case.** Light serif headings, bold grotesque, small-caps labels? Name a real font pairing from `web-craft-typography-with-character`; never copy a proprietary font, pick the nearest open one.
- **Section spacing.** Estimate the vertical gap between sections as a multiple of the body size (about 8x is airy, 4x is dense) and use one `py-*` step for every section.
- **Corners and lines.** Square, 4px, 12px or pill? Hairline borders or none? Set three `--radius-*` tokens.

**4. Build with your own content and structure.** Write the page for the user's real material using `web-flow-new-site` or an existing page. Then compare side by side: it should feel related to the screenshot and look nothing like it.

## Variations

- **Dark screenshot.** The script handles it: paper comes out dark, ink is synthesized light and `accent-deep` is lightened until it passes 4.5:1. Add `dark:` pairs only if the site also needs a light mode (`web-design-dark-mode`).
- **Photo or illustration instead of a UI.** Use `--count 5`. Photo palettes are muddy; take paper and accent, then choose ink by hand.
- **Several references.** Run the script on each, then take paper from one, the accent from another and the type from a third. Mixing three is how you avoid resembling any one.
- **Brand colour given.** Skip the extraction for the accent, set `--color-accent` yourself and keep the script's neutrals so they tint toward it.

## Pitfalls

- Copying the layout "because it matched the palette". Match the mood, then lay the page out for your content (`web-craft-layout-with-intention`).
- Trusting the palette for accessibility. Quantized colours often miss 4.5:1 for small text; the script prints ratios, but still check every text and background pair with `web-a11y-color-contrast`.
- Screenshots with a browser frame, a cookie banner or an ad skew the largest-area colour. Crop to the page first.
- A tiny or heavily compressed image gives noisy colours. Use a full-width capture of at least 1200 px.
- `accent-deep` equals `accent` when the accent already passes 4.5:1 on paper; that is correct, not a bug.
- Reusing a logo, an icon set or a photo from the screenshot. Those are the owner's work; draw or license your own.

## Related skills

- `web-craft-color-with-restraint`
- `web-craft-typography-with-character`
- `web-a11y-color-contrast`
- `web-design-tokens-to-tailwind`
- `web-design-color-system`
- `web-craft-layout-with-intention`
- `web-flow-new-site`
