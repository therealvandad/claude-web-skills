---
name: web-theme-pastel-playful
description: 'Apply a soft, friendly look in Tailwind v4: Gabarito and Figtree fonts, cream paper with plum ink, four pastel background surfaces, a raspberry accent, big radii and no shadows. Use whenever a user says "cute", "playful", "friendly", "pastel", "soft colours", "for kids", "approachable" or "not so corporate".'
---

# Pastel playful theme

Playful does not mean careless. The look holds together because of one strict rule: pastels are surfaces, never text. Text is always the same deep plum ink, so contrast passes on every card regardless of its tint, and the page stays legible while feeling light. Rounded geometry, a display face with soft terminals and generous padding do the rest; no shadows, no gradients, no emoji doing the work an illustration should.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gabarito:wght@500..800&family=Figtree:wght@400;500;600&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-display: "Gabarito", "Avenir Next Rounded", "Nunito", sans-serif;
  --font-sans: "Figtree", system-ui, sans-serif;

  --color-paper:   oklch(98% 0.012 80);
  --color-ink:     oklch(28% 0.045 300);   /* deep plum, never black */
  --color-ink-2:   oklch(48% 0.04 300);
  --color-line:    oklch(88% 0.025 300);

  /* Pastel surfaces, all 92 to 95% lightness so ink passes on every one. */
  --color-peach:  oklch(93% 0.05 50);
  --color-mint:   oklch(93% 0.06 160);
  --color-lilac:  oklch(92% 0.05 300);
  --color-butter: oklch(95% 0.07 95);

  --color-accent:      oklch(52% 0.17 20);  /* raspberry: buttons, links, focus */
  --color-accent-deep: oklch(44% 0.16 20);

  --radius-sm: 0.5rem;
  --radius-md: 0.875rem;
  --radius-lg: 1.25rem;
  --radius-xl: 2rem;
  --shadow-*: initial;
  --shadow-lift: 0 2px 0 0 var(--color-line);  /* a flat "sticker" edge, only on pressables */

  --text-display: clamp(2.5rem, 1.4rem + 4vw, 5rem);
  --text-display--line-height: 1.02;
  --text-display--letter-spacing: -0.02em;
  --text-title: clamp(1.5rem, 1.2rem + 1vw, 2rem);
  --text-title--line-height: 1.2;
  --text-body: 1.0625rem;
  --text-body--line-height: 1.6;
  --text-label: 0.8125rem;
  --text-label--line-height: 1.2;
}

@layer base {
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); }
  h1, h2, h3 { font-family: var(--font-display); font-weight: 700; text-wrap: balance; }
  a { color: var(--color-accent); text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 3px; text-decoration-color: color-mix(in oklch, var(--color-accent) 40%, transparent); }
  a:hover { text-decoration-color: currentColor; }
  :focus-visible { outline: 3px solid var(--color-accent); outline-offset: 3px; border-radius: var(--radius-sm); }
  ::selection { background: var(--color-butter); }
  button, [type="submit"] { font-family: var(--font-display); font-weight: 600; }
}
```

```html
<main class="mx-auto max-w-6xl px-6">
  <header class="flex items-center justify-between py-5">
    <a href="/" class="font-display text-2xl font-bold text-ink no-underline">Pebble</a>
    <nav class="flex items-center gap-6 text-label font-medium">
      <a href="/how" class="text-ink no-underline hover:text-accent">How it works</a>
      <a href="/pricing" class="text-ink no-underline hover:text-accent">Pricing</a>
      <a href="/start" class="rounded-md bg-accent px-4 py-2 text-paper no-underline shadow-lift hover:bg-accent-deep">Try it free</a>
    </nav>
  </header>

  <section class="grid items-center gap-10 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:py-24">
    <div>
      <p class="inline-block rounded-md bg-butter px-3 py-1 text-label font-medium">For classrooms of 6 to 11 year olds</p>
      <h1 class="mt-5 text-display">Pocket money, with a plan</h1>
      <p class="mt-5 max-w-[46ch] text-body text-ink-2">Kids set a goal, see it fill up each week, and learn why the trampoline takes longer than the comic. Parents approve from their phone in one tap.</p>
      <a href="/start" class="mt-8 inline-block rounded-lg bg-accent px-6 py-3.5 font-display text-lg font-semibold text-paper no-underline shadow-lift hover:bg-accent-deep">Set up a child's goal</a>
    </div>
    <figure class="rounded-xl bg-mint p-6 sm:p-10">
      <img src="/img/goal-trampoline.svg" width="640" height="480" alt="A goal card for a trampoline: 48 of 120 euros saved, about 9 weeks to go" class="mx-auto w-full max-w-sm rounded-lg">
    </figure>
  </section>

  <ul class="grid gap-5 pb-20 sm:grid-cols-3">
    <li class="rounded-lg bg-peach p-6">
      <p class="font-display text-4xl font-bold tabular-nums">9 wk</p>
      <h2 class="mt-3 text-title">Goals you can see</h2>
      <p class="mt-2 text-ink-2">Each goal is a jar that fills. Children can tell when they are halfway.</p>
    </li>
    <li class="rounded-lg bg-lilac p-6">
      <p class="font-display text-4xl font-bold tabular-nums">1 tap</p>
      <h2 class="mt-3 text-title">Parents stay in charge</h2>
      <p class="mt-2 text-ink-2">Every payment waits for a thumbs-up on your phone. Nothing leaves without you.</p>
    </li>
    <li class="rounded-lg bg-butter p-6">
      <p class="font-display text-4xl font-bold tabular-nums">0 €</p>
      <h2 class="mt-3 text-title">Free for families</h2>
      <p class="mt-2 text-ink-2">Schools pay, families never do. No card needed to start.</p>
    </li>
  </ul>
</main>
```

What this theme does: plum ink on every surface, four pastels rotated across cards (never two of the same side by side), the raspberry only on buttons, links and focus, a 2px flat edge under pressable things instead of a shadow, radii from `md` on controls to `xl` on illustration frames, numbers in the display face as the "icon".

What it never does: pastel or white text on a pastel surface, pure black, drop shadows or glows, gradients, emoji as icons, rainbow order (peach, mint, lilac, butter is a palette, not a spectrum, so skip one when three are needed), `rounded-full` on rectangles, more than one accent, bouncing animations.

## Variations

- **Illustration-led**: every pastel panel is a frame for an SVG with a transparent background; set the SVG's own strokes to `currentColor` so they pick up `text-ink` and stay in the family.
- **Dark mode that stays soft**: `paper oklch(22% 0.03 300)`, `ink oklch(94% 0.015 80)`, pastels drop to 32% lightness at chroma 0.06 (`oklch(32% 0.06 50)` and so on) so they become tinted dusk surfaces; accent to `oklch(74% 0.14 20)`. Override in `.dark`, not `@theme`.
- **Grown-up version** for a wellness or stationery brand: keep ink and accent, use only `peach` and `butter`, add `--radius-md: 0.5rem`; the look turns quiet without a new palette.
- **Sticker buttons**: `border-2 border-ink shadow-[3px_3px_0_0_var(--color-ink)]` on the primary button alone, for a zine-ish edge; never on cards too.

## Pitfalls

- Pastels at 92 to 95% are indistinguishable from the paper on cheap screens unless chroma is at least 0.05; below that use a border instead.
- `ink-2` at 48% passes 5.2:1 on the darkest pastel (`lilac`, 92%) but would fail at 55%; do not lighten secondary text to make it "softer".
- The raspberry at 52% carries white text at 5.2:1; a lighter "pink" button fails. If the brand wants pink, use it as a surface with ink text.
- Gabarito has no italic; `font-synthesis: none` plus `em { font-weight: 600 }` gives honest emphasis instead of a slanted fake.
- Radii must nest: a `rounded-lg` card holding a `rounded-lg` image looks wrong at the corners; the inner radius is the outer minus the padding (here `rounded-xl` frame, `rounded-lg` image at `p-6`).
- Big friendly type at `text-display` wraps to four lines on phones; keep headlines under seven words or lower the clamp ceiling.

## Related skills

- `web-craft-color-with-restraint`
- `web-craft-typography-with-character`
- `web-design-borders-radius-dividers`
- `web-css-variables-theming`
- `web-design-dark-mode`
- `web-design-tokens-to-tailwind`
- `web-theme-switcher`
