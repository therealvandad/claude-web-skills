---
name: web-motion-hover-microinteractions
description: 'Add subtle hover and focus microinteractions with Tailwind: card lift, link underline that grows, icon nudge on buttons, press-down on active, image zoom in a frame, all transform/opacity-only with motion-safe variants and touch-safe fallbacks. Use whenever a user says "make buttons feel alive", "hover effect", "animated underline", "arrow that moves", "cards should pop", or wants polish on interactive elements.'
---

# Hover microinteractions

A microinteraction answers "did that react to me?" in under 200 ms, then gets out of the way. The constraints that keep them tasteful: move only a few pixels, scale by at most 1.05, animate transform/opacity so hover never causes layout, give focus the same treatment as hover (keyboard users deserve the same feedback), and remember that touch screens have no hover at all, so nothing important may be revealed only on hover.

## Pattern

Five patterns in one block; copy the one you need.

```html
<!-- 1. Button: press down on :active, icon nudge on hover/focus -->
<button type="button"
        class="group inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white
               motion-safe:transition-[transform,background-color] motion-safe:duration-150 motion-safe:ease-out
               hover:bg-blue-700 active:scale-[0.97]
               focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
  Continue
  <svg class="size-4 motion-safe:transition-transform motion-safe:duration-150
              group-hover:translate-x-0.5 group-focus-visible:translate-x-0.5"
       viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path d="M3 8h10M9 4l4 4-4 4"/>
  </svg>
</button>

<!-- 2. Link: underline grows from the left, using a scaled pseudo-element (no layout) -->
<a href="/docs"
   class="relative inline-block font-medium text-zinc-900 no-underline dark:text-zinc-100
          after:absolute after:inset-x-0 after:-bottom-0.5 after:h-0.5 after:bg-current
          after:origin-left after:scale-x-0 motion-safe:after:transition-transform motion-safe:after:duration-200
          hover:after:scale-x-100 focus-visible:after:scale-x-100
          focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-current">
  Documentation
</a>

<!-- 3. Card: lift + shadow, with a zooming image kept inside its frame -->
<a href="/post" class="group block overflow-hidden rounded-xl border bg-white shadow-sm
                       motion-safe:transition-[transform,box-shadow] motion-safe:duration-200
                       hover:-translate-y-1 hover:shadow-lg focus-visible:-translate-y-1 focus-visible:shadow-lg
                       focus-visible:outline-2 focus-visible:outline-offset-2 dark:bg-zinc-900">
  <div class="aspect-video overflow-hidden">
    <img src="cover.jpg" alt=""
         class="size-full object-cover motion-safe:transition-transform motion-safe:duration-500 motion-safe:ease-out
                group-hover:scale-105 group-focus-visible:scale-105" />
  </div>
  <div class="p-4">
    <h3 class="font-semibold">Post title</h3>
    <p class="mt-1 text-sm text-zinc-600 dark:text-zinc-400">Excerpt text.</p>
  </div>
</a>

<!-- 4. Icon button: background fades in, icon rotates (e.g. settings cog) -->
<button type="button" aria-label="Settings"
        class="group rounded-full p-2 motion-safe:transition-colors hover:bg-zinc-100 focus-visible:bg-zinc-100
               focus-visible:outline-2 focus-visible:outline-offset-2 dark:hover:bg-zinc-800">
  <svg class="size-5 motion-safe:transition-transform motion-safe:duration-300 group-hover:rotate-45"
       viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/>
  </svg>
</button>

<!-- 5. Reveal-on-hover actions, but ALSO visible on focus and on touch devices -->
<li class="group relative flex items-center justify-between rounded-md p-3 hover:bg-zinc-50 dark:hover:bg-zinc-800">
  <span>Item name</span>
  <button type="button"
          class="rounded px-2 py-1 text-sm motion-safe:transition-opacity
                 opacity-100 [@media(hover:hover)]:opacity-0
                 [@media(hover:hover)]:group-hover:opacity-100 [@media(hover:hover)]:focus-visible:opacity-100
                 focus-visible:outline-2">
    Edit
  </button>
</li>
```

Why `active:scale-[0.97]` and not `0.9`: a 3% press reads as tactile; 10% reads as the button running away. Why the underline is a scaled pseudo-element: `text-decoration` and `border-bottom` cannot animate width without layout; `scale-x` can.

## Variations

- **Hover-only media query**: Tailwind v4's `hover:` already targets `@media (hover: hover)`, so sticky hover states on touch are avoided by default. Use `[@media(hover:none)]:` for explicit touch alternatives.
- **Magnetic/tilt effects** need JS (`pointermove` updating `--x`/`--y` custom properties on the element, applied via `transform: rotateX(var(--ry)) rotateY(var(--rx))`). Cap at 6-8 degrees and disable under reduced motion.
- **Group-hover on a whole row** (`group` + `group-hover:`) so hovering anywhere in a list item nudges its arrow; combine with `group-focus-within:` so keyboard focus inside does the same.
- **Dark mode**: shadows are nearly invisible on dark backgrounds; swap the lift cue for a border or ring: `dark:hover:ring-1 dark:hover:ring-zinc-600`.

## Pitfalls

- Hover that scales a card without `overflow-hidden` on the image wrapper lets the image bleed over rounded corners; clip the frame, zoom the image inside it.
- `hover:scale-105` on grid items overlaps neighbours; add `hover:z-10` and `relative` or use `-translate-y-1` instead of scale.
- Anything revealed only on hover is unreachable by keyboard and invisible on phones. Pair every `group-hover:` with `group-focus-within:` / `focus-visible:` and make it visible by default where `hover: none`.
- Transitioning `box-shadow` repaints; acceptable on a handful of cards, not on 200 table rows. For long lists use `hover:bg-*` only.
- Do not animate `outline` for focus rings; users need the ring instantly. Keep `focus-visible:outline-*` untransitioned.
- Layered `transition-all` on parent and child doubles up timing and makes the nudge feel late; transition only the listed properties on each element.

## Related skills

- `web-motion-transitions`
- `web-motion-reduced-motion`
- `web-ui-buttons`
- `web-ui-cards`
- `web-design-shadows-and-elevation`
