---
name: web-css-fluid-typography
description: Set up a fluid type scale with clamp() so headings and body text grow smoothly between phone and desktop, registered as Tailwind v4 @theme tokens (text-fluid-xl etc.), plus fluid section spacing. Use whenever a user wants text that "scales with the screen", headings too big on mobile, a type scale, or asks about clamp, responsive font sizes or fluid spacing.
---

# Fluid typography and spacing

Breakpoint-based sizes (`text-3xl md:text-5xl`) jump at one pixel and sit wrong at every width in between. `clamp(min, preferred, max)` lets a size slide between two bounds driven by viewport width, so a hero heading is 2rem on a phone, 4.5rem on a monitor, and exactly right everywhere else, with zero breakpoints. The one rule that matters: the preferred value must mix `vw` with `rem` (for example `2vw + 1rem`) so browser zoom and user font-size settings still work. A pure `vw` value cannot be zoomed and fails WCAG 1.4.4.

## Pattern

Compute each step from two anchor points: at 20rem (320px) and at 80rem (1280px) viewport. Slope = (max − min) / (80 − 20); intercept = min − slope × 20. Preferred = `intercept + (slope × 100)vw`. The tokens below are precomputed with a 1.2 ratio on mobile and 1.25 on desktop.

```css
@import "tailwindcss";

@theme {
  /* text-fluid-*  →  font-size + a sensible line-height */
  --text-fluid-sm:  clamp(0.875rem, 0.833rem + 0.21vw, 1rem);
  --text-fluid-sm--line-height: 1.5;
  --text-fluid-base: clamp(1rem, 0.917rem + 0.42vw, 1.25rem);
  --text-fluid-base--line-height: 1.6;
  --text-fluid-lg:  clamp(1.25rem, 1.125rem + 0.63vw, 1.625rem);
  --text-fluid-lg--line-height: 1.4;
  --text-fluid-xl:  clamp(1.5rem, 1.25rem + 1.25vw, 2.25rem);
  --text-fluid-xl--line-height: 1.25;
  --text-fluid-2xl: clamp(1.875rem, 1.458rem + 2.08vw, 3.125rem);
  --text-fluid-2xl--line-height: 1.15;
  --text-fluid-3xl: clamp(2.25rem, 1.5rem + 3.75vw, 4.5rem);
  --text-fluid-3xl--line-height: 1.05;

  /* fluid spacing for section padding and gaps: py-fluid-lg, gap-fluid-md ... */
  --spacing-fluid-sm: clamp(1rem, 0.667rem + 1.67vw, 2rem);
  --spacing-fluid-md: clamp(2rem, 1.333rem + 3.33vw, 4rem);
  --spacing-fluid-lg: clamp(3rem, 1.667rem + 6.67vw, 7rem);
}
```

```html
<section class="mx-auto max-w-5xl px-4 py-fluid-lg">
  <h1 class="text-balance text-fluid-3xl font-bold tracking-tight">
    Headings that fit every screen
  </h1>
  <p class="mt-fluid-sm max-w-prose text-pretty text-fluid-base text-gray-600 dark:text-gray-300">
    Body copy stays between 16px and 20px, with a measure capped at roughly 65 characters.
  </p>
  <div class="mt-fluid-md grid gap-fluid-sm sm:grid-cols-2">
    <article>
      <h2 class="text-fluid-xl font-semibold">Card heading</h2>
      <p class="mt-2 text-fluid-sm">Smaller supporting text.</p>
    </article>
  </div>
</section>
```

One-off without tokens: `text-[clamp(2rem,1.5rem+2.5vw,3.5rem)]` or `leading-[1.1]`. Letter-spacing tightens as size grows: `tracking-tight` on `fluid-2xl` and up.

## Variations

- **Container-relative type**: swap `vw` for `cqi` inside a `@container` parent (`clamp(1rem, 0.8rem + 1cqi, 1.5rem)`) so a card's heading scales with the card, not the window. See `web-css-container-queries`.
- **Narrower range for body text**: keep body between 1rem and 1.125rem; big swings in body size feel unstable. Spend the drama on display headings.
- **Fluid only above a breakpoint**: combine `text-2xl md:text-fluid-3xl` to freeze the phone size and start scaling from tablet up.
- **Line-height counter-scales**: large text needs tighter leading (1.05 to 1.15), small text looser (1.5 to 1.6). The `--line-height` companion tokens above bake this in.

## Pitfalls

- **Pure `vw` sizes** (`font-size: 5vw`) break zoom and user font preferences; always add a `rem` term. A quick check: Ctrl/Cmd + "+" should visibly enlarge the text.
- **Min larger than max** silently makes `clamp()` return min. Re-check the maths after editing one bound.
- **Forgetting `max-width` on paragraphs**: fluid size without a measure limit (`max-w-prose`, about 65ch) gives 200-character lines on wide monitors. Cap the measure, not just the font.
- **`vw` includes the scrollbar width on Windows**: text can be a hair bigger than intended near a breakpoint. Harmless for `clamp()`, but do not use `100vw` for widths.
- **Tailwind token naming**: the utility is `text-fluid-xl`, so the token must be `--text-fluid-xl`; a `--font-size-*` name does nothing in v4. Line-height companion is `--text-fluid-xl--line-height` (double dash).
- **`text-balance` on long paragraphs**: browsers only balance up to a few lines; use `text-pretty` for body copy and `text-balance` for headings.

## Related skills

- `web-design-typography-system` for fonts, weights and the full scale rationale
- `web-css-spacing-scale` for the non-fluid spacing system this complements
- `web-css-container-queries` for `cqi`-driven sizing
- `web-css-variables-theming` for how `@theme` tokens become utilities
- `web-layout-hero` for the usual home of a `text-fluid-3xl` heading
