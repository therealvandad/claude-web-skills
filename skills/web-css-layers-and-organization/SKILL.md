---
name: web-css-layers-and-organization
description: 'Organise site CSS around Tailwind v4 cascade layers: a file structure for input.css, how @layer components and @utility work, when @apply is a trap, and keeping third-party CSS from overriding utilities. Use whenever a user asks where to put custom CSS, how to structure stylesheets, about @layer or @apply, "my CSS isn''t overriding Tailwind", or wants a .btn class.'
---

# CSS layers and organisation

Tailwind v4 emits real CSS `@layer`s in a fixed order: `theme, base, components, utilities`. Later layers beat earlier ones regardless of specificity, and **unlayered CSS beats all layers**. That one fact explains almost every "why does my style win / lose" question. The organisational rule that follows: every line of project CSS goes into a named layer that matches its job, and the only unlayered CSS is third-party code you cannot control (and you then wrap it in a layer anyway with `@import … layer(…)`).

## Pattern

File structure: one entry file, small partials, no global dumping ground.

```
src/css/
  input.css        # entry: imports + layer declarations only
  theme.css        # @theme tokens (colours, fonts, spacing, radii)
  base.css         # @layer base: element defaults (see web-css-modern-reset)
  components/
    buttons.css    # @layer components: .btn, .btn-primary
    prose.css      # @layer components: .prose-article
  utilities.css    # @utility: custom single-purpose classes
  vendor.css       # @import of third-party CSS, forced into a layer
```

```css
/* src/css/input.css */
@import "tailwindcss";
@import "./theme.css";
@import "./base.css";
@import "./components/buttons.css";
@import "./components/prose.css";
@import "./utilities.css";
@import "./vendor.css";
@source "../../templates";         /* extra template dirs for class detection, if any */
```

```css
/* src/css/components/buttons.css: multi-property classes that templates reuse */
@layer components {
  .btn {
    display: inline-flex;
    align-items: center;
    gap: --spacing(2);                       /* v4 helper = 0.5rem */
    border-radius: var(--radius-md);
    padding: --spacing(2) --spacing(4);
    font-weight: 500;
    transition: background-color 150ms;
    &:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
    &:disabled { opacity: 0.5; pointer-events: none; }
  }
  .btn-primary {
    background: var(--color-accent);
    color: var(--color-accent-fg);
    &:hover { background: color-mix(in oklch, var(--color-accent), black 10%); }
  }
}
```

```css
/* src/css/utilities.css: single-purpose classes that should work with variants */
@utility content-grid {
  display: grid;
  grid-template-columns: minmax(1rem, 1fr) minmax(0, 70rem) minmax(1rem, 1fr);
  & > * { grid-column: 2; }
  & > .full-bleed { grid-column: 1 / -1; }
}
@utility scrollbar-none {
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}
/* Functional utility with a value: tab-4, tab-8 ... */
@utility tab-* {
  tab-size: --value(integer);
}
```

```css
/* src/css/vendor.css: third-party CSS cannot be allowed to be unlayered */
@import "some-lightbox/dist/lightbox.css" layer(components);
```

```html
<!-- Components layer class + utilities still override it, because utilities come later -->
<a href="/signup" class="btn btn-primary w-full sm:w-auto">Get started</a>
<main class="content-grid md:content-grid">
  <h1>Narrow by default</h1>
  <figure class="full-bleed"><img src="/img/wide.jpg" alt="" /></figure>
</main>
```

Why `@layer components` for `.btn` but `@utility` for `content-grid`: a component class is a bundle meant to be *overridden* by utilities in the template (`btn w-full`). A utility is meant to *be* the override and to work with `hover:`/`md:` variants; only `@utility` registers it with the variant engine.

## Variations

- **`@apply` with restraint**: fine inside `@layer components` for small, stable bundles (`.badge { @apply inline-flex rounded-full px-2 text-xs font-medium; }`) and for CMS content you cannot add classes to. Avoid it as a general pattern: it hides styles from the template, creates a second naming system, and `@apply` of variant classes (`hover:bg-x`) is awkward. Prefer plain CSS with `var(--color-*)` tokens, which is just as short.
- **Using theme tokens inside CSS**: `var(--color-brand-500)`, `var(--text-lg)`, `--spacing(4)`, `--alpha(var(--color-fg) / 60%)`. No `theme()` function needed in v4.
- **Custom variants** for project-wide states: `@custom-variant hocus (&:hover, &:focus-visible);` then `hocus:underline` in templates.
- **Legacy or CMS stylesheet you cannot edit**: import it into `layer(base)` so Tailwind utilities still win, then fix its remaining conflicts with a few targeted rules in `@layer components`.

## Pitfalls

- **Unlayered custom CSS wins over every utility**: a stray `.card { padding: 2rem }` outside `@layer` beats `p-4` in the template, even though `p-4` looks "more specific" to a human. Wrap it.
- **`@layer utilities { .foo {} }` from v3** no longer gets variants in v4; use `@utility foo {}`.
- **`@import` order is cascade order within the same layer**: components imported after `vendor.css` override it; before, they do not. Keep the import list deliberate.
- **Dynamic class names** (`` `bg-${color}-500` ``) are never generated because the build scans source text for complete class strings. Map to full names (`{ red: 'bg-red-500' }`) or move the variation into a CSS variable (`style="--c: …"` + `bg-(--c)`).
- **`@theme` inside a partial that is not imported from the entry** is invisible; every file must be reachable from `input.css`.
- **Deep nesting in component CSS** (`.card .body .title`) recreates specificity wars; keep component selectors flat and single-class, use `&` nesting only for states and pseudo-elements.
- **Putting everything in `@layer components`** turns the layer into a mini-framework nobody remembers; if a bundle is used on one page, it is template classes, not a component.

## Related skills

- `web-css-modern-reset` for the contents of `base.css`
- `web-css-variables-theming` for `theme.css` and semantic tokens
- `web-ship-project-setup` for the build command and folder layout
- `web-ship-tailwind-production` for content detection, `@source`, and minification
- `web-ui-buttons` for a full button system that can live in `buttons.css`
- `web-js-clean-code` for the data-attribute hook convention that keeps JS out of CSS class names
