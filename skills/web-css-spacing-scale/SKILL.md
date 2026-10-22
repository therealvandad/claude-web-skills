---
name: web-css-spacing-scale
description: A consistent spacing system for a site: Tailwind v4's 4px scale, which steps to use inside components versus between sections, gap versus margin versus padding rules, and a vertical rhythm for page sections. Use whenever a user asks about spacing, padding, margins, "the gaps look uneven", "how much space between sections", or wants a design-system spacing scale.
---

# Spacing scale and rhythm

Inconsistent spacing is the fastest way to make a competent layout look amateur. The fix is not taste, it is a constraint: pick a small set of allowed values and a rule for which value goes where. Tailwind v4's scale is `--spacing: 0.25rem` multiplied by the number in the class (`p-4` = 1rem, `gap-6` = 1.5rem), so every utility already sits on a 4px grid. The job of this skill is to pick the *subset* you use and the *direction* the space is applied in.

## Pattern

Three tiers; each tier uses only three or four steps. Memorise the tiers, not 30 numbers.

| Tier | Steps | Used for |
|---|---|---|
| Inside a component | `1 2 3 4` (4 to 16px) | icon-to-label, input padding, chip padding, list item gaps |
| Between components | `4 6 8 12` (16 to 48px) | card padding, grid gap, form field stacks, card-to-card |
| Between sections | `16 24 32` (64 to 128px) | vertical padding of page sections, hero to features |

Three rules for *where* the space goes:

1. **Containers own spacing between their children** with `gap-*` (flex/grid) or `space-y-*` (plain block flow). Children do not carry outer margins, so a component drops into any parent without leaking space.
2. **Padding is for inside edges** (card, button, section). It belongs to the element that has the background or border.
3. **Margin is the exception**, used only for one-off pushes: `mt-auto` to pin a footer, `-mx-4` to bleed a child to the edges, `mt-2` under a heading inside prose.

```html
<!-- Section rhythm: every section gets the same vertical padding; the
     container inside owns the horizontal gutter and max width. -->
<section class="py-16 md:py-24">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <header class="max-w-2xl space-y-3">        <!-- between-components tier -->
      <h2 class="text-3xl font-bold">Features</h2>
      <p class="text-gray-600">Spacing between heading and intro is 12px.</p>
    </header>

    <ul class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3" role="list">
      <li class="rounded-xl border p-6">        <!-- card padding = grid gap -->
        <div class="flex items-center gap-2">    <!-- inside-component tier -->
          <svg class="size-5 shrink-0" aria-hidden="true"><!-- icon --></svg>
          <h3 class="font-semibold">Fast</h3>
        </div>
        <p class="mt-3 text-sm text-gray-600">Body text 12px under its title.</p>
      </li>
      <!-- more <li> -->
    </ul>
  </div>
</section>
```

Make the tiers nameable so they stay consistent across the codebase:

```css
@import "tailwindcss";

@theme {
  --spacing-section: 4rem;       /* py-section            */
  --spacing-section-lg: 6rem;    /* md:py-section-lg      */
  --spacing-gutter: 1rem;        /* px-gutter             */
  --spacing-stack: 1.5rem;       /* gap-stack, space-y-stack */
}
```

## Variations

- **Dense UIs (dashboards, tables)**: shift every tier down one step (`p-4` cards, `gap-4` grids, `py-8` sections). Keep the *ratios*, lower the base.
- **Marketing pages**: shift up (`py-24 lg:py-32` sections, `gap-8` grids) and let whitespace do the hierarchy.
- **Fluid section padding**: replace `py-16 md:py-24` with a `clamp()` token (see `web-css-fluid-typography`) so section rhythm scales smoothly too.
- **Optical adjustment**: icons and all-caps labels look low; nudge with `-mt-px` or `leading-none` rather than inventing a new spacing step.

## Pitfalls

- **Mixing `gap` and child margins** doubles the space in one direction and leaves it single in another. Pick one owner per axis.
- **`space-y-*` with `flex-wrap`, `grid` or hidden children** misbehaves (it relies on `> * + *` margins). Use `gap-*` on flex and grid; keep `space-y-*` for simple block stacks only.
- **Horizontal padding that does not match the header's**: the page gutter (`px-4 sm:px-6 lg:px-8`) must be identical in header, sections and footer, or edges jitter as you scroll. Put it in one container component or the `--spacing-gutter` token.
- **Arbitrary values (`mt-[13px]`)**: each one is a spacing step that exists nowhere else. If a mock asks for 13px, use 12 or 16; nobody can see the difference, everyone can see inconsistency.
- **Section padding on the inner container instead of the section**: backgrounds then stop at the max-width instead of bleeding full width. Padding vertical on `<section>`, horizontal gutter on the inner wrapper.
- **Collapsing margins surprise**: vertical margins between block siblings collapse, inside flex and grid they do not. One more reason to prefer `gap`.

## Related skills

- `web-css-fluid-typography` for fluid spacing tokens
- `web-layout-page-shell` for the gutter container pattern
- `web-layout-landing-page` for applying section rhythm across a full page
- `web-css-flexbox-patterns` and `web-css-responsive-grid` for `gap` in practice
- `web-design-ui-polish-checklist` for the final spacing audit
