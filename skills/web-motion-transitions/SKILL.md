---
name: web-motion-transitions
description: Add CSS transitions with Tailwind (transition-*, duration-*, ease-*, delay-*) that animate only transform and opacity, with the right easing and durations and a reduced-motion fallback. Use whenever a user wants something to "fade", "slide", "ease in", "animate smoothly", "feel less abrupt", or asks what to animate and how long it should take.
---

# CSS transitions: what, how long, which curve

A transition interpolates a property between two states the browser already knows (hover, focus, a toggled class). It is the cheapest motion you can ship: no JS, no timers, and when you limit it to `transform` and `opacity` it runs on the compositor thread and never triggers layout or paint. Animating `width`, `height`, `top`, `margin` or `box-shadow` re-lays out or repaints every frame and stutters on mid-range phones. The rules below are about picking properties, durations and curves so motion reads as "responsive", not "slow".

## Pattern

A card that lifts and a disclosure panel that fades/slides, both transform/opacity only, both silent under reduced motion.

```html
<article class="group rounded-xl border border-zinc-200 bg-white p-6 shadow-sm
                motion-safe:transition-[transform,box-shadow] motion-safe:duration-200 motion-safe:ease-out
                hover:-translate-y-1 hover:shadow-lg focus-within:-translate-y-1 focus-within:shadow-lg
                dark:border-zinc-700 dark:bg-zinc-900">
  <h3 class="text-lg font-semibold">Card title</h3>
  <p class="mt-2 text-zinc-600 dark:text-zinc-400">Short description.</p>
  <a href="/more" class="mt-4 inline-flex items-center gap-1 font-medium text-blue-600
                          focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
    Read more
    <svg class="size-4 motion-safe:transition-transform motion-safe:duration-150 group-hover:translate-x-0.5"
         viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <path d="M3 8h10M9 4l4 4-4 4"/>
    </svg>
  </a>
</article>

<button type="button" id="toggle" aria-expanded="false" aria-controls="panel"
        class="mt-6 rounded-md bg-zinc-900 px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2">
  Show details
</button>
<div id="panel" hidden
     class="mt-3 rounded-md bg-zinc-100 p-4 dark:bg-zinc-800
            data-[state=closed]:-translate-y-1 data-[state=closed]:opacity-0
            data-[state=open]:translate-y-0 data-[state=open]:opacity-100
            motion-safe:transition-[transform,opacity] motion-safe:duration-200 motion-safe:ease-out">
  Details content. Still readable with JS off because <code>hidden</code> is the only gate.
</div>
```

```js
const toggle = document.querySelector('#toggle');
const panel = document.querySelector('#panel');

function openPanel() {
  panel.hidden = false;
  panel.dataset.state = 'closed';
  requestAnimationFrame(() => requestAnimationFrame(() => (panel.dataset.state = 'open')));
  toggle.setAttribute('aria-expanded', 'true');
  toggle.textContent = 'Hide details';
}

function closePanel() {
  panel.dataset.state = 'closed';
  const finish = () => { panel.hidden = true; };
  // transitionend never fires under reduced motion (no transition), so hide immediately then.
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) finish();
  else panel.addEventListener('transitionend', finish, { once: true });
  toggle.setAttribute('aria-expanded', 'false');
  toggle.textContent = 'Show details';
}

toggle.addEventListener('click', () => (panel.hidden ? openPanel() : closePanel()));
```

Why these values: `150-200 ms` for hover and small state changes, `250-350 ms` for things that move across the screen, never more than `500 ms` for UI. `ease-out` for things entering or responding to the user (fast start, settles gently); `ease-in` only for things leaving; `ease-in-out` for things that move from A to B and stay visible. The double `requestAnimationFrame` gives the browser one painted frame in the "closed" state so the transition has a start value.

## Variations

- **Custom curves in `@theme`**: `@theme { --ease-snappy: cubic-bezier(0.2, 0, 0, 1); --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); }` then `ease-snappy` / `ease-spring`. Use the overshoot curve sparingly and only on transform.
- **Transition only what changes**: `transition-[transform,opacity]` beats `transition-all`, which also animates `color`, `border` and anything else that flips and makes the whole element feel sluggish.
- **Delay for sequencing**: `delay-75` on a child icon so it moves a beat after its parent. Keep total (duration + delay) under ~400 ms.
- **Asymmetric timing**: enter at `duration-200`, leave at `duration-150`: `data-[state=closed]:duration-150`. Exits should be faster than entries.
- **Color transitions** are fine for hover tints (`transition-colors duration-150`); they repaint but the area is small. Avoid on page-sized backgrounds.

## Pitfalls

- `transition` from `display:none` does nothing: the start state has no computed value. Use the `hidden` + `data-state` + double-rAF pattern above, or `@starting-style` (Chrome 117+, Safari 17.5+, Firefox 129+) with `transition-behavior: allow-discrete` where support allows.
- `transition-all` plus a `height: auto` change is not animatable. For expand/collapse, animate `grid-template-rows: 0fr -> 1fr` on a wrapper (see `web-ui-accordion`) or use `interpolate-size: allow-keywords` (Chrome 129+ only, progressive).
- Forgetting `motion-safe:` means users who asked for reduced motion still get the lift. `motion-safe:transition-*` is the whole story for transitions; nothing else needed.
- A `transform` on the card creates a stacking context; absolutely positioned dropdowns inside it may clip under neighbours. Move the dropdown out or give the card `z-10` on hover.
- `will-change: transform` on everything wastes GPU memory. Add it only to an element you measured as janky, and only while it animates.
- `transitionend` fires once per transitioned property and bubbles from children; guard with `{ once: true }` and check `e.target === panel` when the panel has transitioning children.

## Related skills

- `web-motion-reduced-motion`
- `web-motion-hover-microinteractions`
- `web-motion-keyframes`
- `web-ui-accordion`
- `web-ui-buttons`
