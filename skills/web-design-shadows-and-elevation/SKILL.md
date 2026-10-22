---
name: web-design-shadows-and-elevation
description: Define an elevation system in Tailwind v4: a shadow scale in `@theme` built from layered, tinted shadows, which level each component uses (card, dropdown, modal), hover lift, and the dark-mode replacement (surface steps and rings). Use whenever a user asks for shadows, "make the cards pop", depth, elevation, floating, or says shadows look muddy or vanish in dark mode.
---

# Shadows and elevation

Elevation tells the eye what is above what: a card sits on the page, a dropdown floats over the card, a modal floats over everything. One shadow value cannot express that, and a single big blur looks like a smudge. Realistic shadows are a stack of two or three layers (a tight contact shadow plus a soft ambient one), tinted toward the surface color instead of pure black, and they scale together: higher elevation means a larger offset and blur, and a lighter ambient layer. Encode the levels in `@theme` and components only name their level.

## Pattern

```css
@import "tailwindcss";

/* Tint: shadows are the page color darkened, not black. oklch lightness 25%, hue of the brand.
   Kept outside @theme so it does not generate a stray `shadow-color` utility. */
:root { --shadow-color: 25% 0.02 275; }

@theme {
  /* Level 1: resting cards. Contact + small ambient. */
  --shadow-sm:
    0 1px 2px oklch(var(--shadow-color) / 0.06),
    0 1px 3px oklch(var(--shadow-color) / 0.08);
  /* Level 2: hovered cards, inputs with focus, popovers. */
  --shadow-md:
    0 1px 2px oklch(var(--shadow-color) / 0.06),
    0 4px 8px -2px oklch(var(--shadow-color) / 0.10);
  /* Level 3: dropdowns, tooltips, toasts. */
  --shadow-lg:
    0 1px 2px oklch(var(--shadow-color) / 0.05),
    0 8px 16px -4px oklch(var(--shadow-color) / 0.12),
    0 20px 32px -12px oklch(var(--shadow-color) / 0.14);
  /* Level 4: modals, command palettes. */
  --shadow-xl:
    0 2px 4px oklch(var(--shadow-color) / 0.05),
    0 16px 32px -8px oklch(var(--shadow-color) / 0.16),
    0 40px 64px -16px oklch(var(--shadow-color) / 0.20);
  /* Inset: pressed buttons, wells. */
  --shadow-inner: inset 0 2px 4px oklch(var(--shadow-color) / 0.08);
}

/* Dark mode: shadows barely show, so elevation becomes a lighter surface plus a hairline ring. */
@layer base {
  .dark {
    --shadow-sm: 0 0 0 1px oklch(100% 0 0 / 0.06);
    --shadow-md: 0 0 0 1px oklch(100% 0 0 / 0.08), 0 4px 12px oklch(0% 0 0 / 0.5);
    --shadow-lg: 0 0 0 1px oklch(100% 0 0 / 0.10), 0 12px 32px oklch(0% 0 0 / 0.6);
    --shadow-xl: 0 0 0 1px oklch(100% 0 0 / 0.12), 0 24px 64px oklch(0% 0 0 / 0.7);
  }
}
```

```html
<!-- Level 1 at rest, level 2 on hover: the lift is the shadow change plus a 2px translate. -->
<article class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-950/5
                motion-safe:transition-[box-shadow,transform] motion-safe:duration-200
                hover:-translate-y-0.5 hover:shadow-md
                dark:bg-gray-900 dark:ring-0">
  <h3 class="font-semibold text-gray-900 dark:text-gray-100">Starter</h3>
  <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Resting card: shadow-sm + a 5% ring to define the edge.</p>
</article>

<!-- Level 3: a dropdown panel. Larger radius goes with larger shadow. -->
<div role="menu" class="mt-2 w-56 rounded-xl bg-white p-1.5 shadow-lg ring-1 ring-gray-950/5 dark:bg-gray-800 dark:ring-0">
  <button role="menuitem" class="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700">Rename</button>
  <button role="menuitem" class="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700">Duplicate</button>
</div>

<!-- Level 4: a modal, with a backdrop that carries most of the separation. -->
<dialog class="rounded-2xl bg-white p-8 shadow-xl backdrop:bg-gray-950/40 backdrop:backdrop-blur-sm dark:bg-gray-900">
  <h2 class="text-lg font-semibold">Delete project?</h2>
</dialog>
```

The `ring-1 ring-gray-950/5` on light surfaces is deliberate: on a white page a light shadow alone leaves the card edge undefined; a 5% hairline fixes it without reading as a border.

## Variations

- **Flat / brutalist.** Replace shadows with `border-2 border-gray-950` and an offset solid shadow: `--shadow-md: 4px 4px 0 0 oklch(20% 0 0);`. Hover: `hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_0_...]`.
- **Colored glow for the primary CTA.** `shadow-lg shadow-indigo-500/30` uses the Tailwind color opacity syntax to tint only that element; keep it to one element per screen.
- **Surface steps instead of shadows (dark UIs, dashboards).** Page `gray-950`, card `gray-900`, popover `gray-800`, modal `gray-800` + backdrop. Each level is one step lighter; no shadow needed.
- **Extend the scale.** Add `--shadow-2xl` for full-screen overlays, or `--shadow-xs` (`0 1px 1px / 0.05`) for table rows and chips.

## Pitfalls

- A single `0 10px 30px rgba(0,0,0,.3)` looks like a grey halo; at least two layers (tight + diffuse) and alpha under 0.2 per layer read as light, not dirt.
- Overriding `--shadow-md` in `@theme` removes Tailwind's default but keeps the `shadow-md` utility name, so existing markup keeps working; renaming to `--shadow-card` would require changing classes.
- Animating `box-shadow` on many elements at once is slow (it repaints). For lists, animate `transform` only, or move the shadow onto a `::after` pseudo-element and animate its `opacity`.
- Shadows on elements with `overflow-hidden` parents get clipped; add padding to the parent or move `overflow-hidden` to an inner wrapper.
- In dark mode a light shadow disappears entirely; forgetting the `.dark` override leaves cards floating with no edge. The ring or surface-step approach is not optional.
- `shadow-*` and `ring-*` both use `box-shadow`; Tailwind composes them with variables so they coexist, but an arbitrary `shadow-[...]` value will wipe the ring unless you include it.

## Related skills

- `web-design-dark-mode`
- `web-design-borders-radius-dividers`
- `web-ui-cards`
- `web-motion-hover-microinteractions`
- `web-ui-modal-dialog`
