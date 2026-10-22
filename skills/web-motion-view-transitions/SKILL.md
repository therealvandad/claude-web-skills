---
name: web-motion-view-transitions
description: 'Use the View Transitions API for same-document DOM changes (document.startViewTransition) and cross-document multi-page navigations (@view-transition { navigation: auto }), with view-transition-name for shared-element morphs, browser-support notes and a graceful fallback. Use whenever a user asks for "smooth page transitions", "shared element animation", "morph this card into the detail page", "animate list reorder", or "View Transitions".'
---

# View Transitions

The browser snapshots the old state, you change the DOM (or navigate), it snapshots the new state, then it cross-fades the two, and any element with a matching `view-transition-name` on both sides is animated from its old box to its new box. You get a shared-element "hero morph" between pages with a few lines of CSS and no library. Support (as of 2026): same-document in Chrome/Edge 111+, Safari 18+, Firefox 144+; cross-document (MPA) in Chrome/Edge 126+, Safari 18.2+, Firefox 148+. The fallback is free: without support the DOM just changes or the page just loads, so always write it as an enhancement.

## Pattern

**Cross-document (plain multi-page site).** Opt in on every page and name the elements that should morph.

```css
/* Both pages must include this; it only applies to same-origin navigations. */
@view-transition { navigation: auto; }

/* Default root crossfade is 0.25s; tune it, and respect reduced motion. */
::view-transition-old(root),
::view-transition-new(root) { animation-duration: 300ms; }

@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important; }
}
```

```html
<!-- list.html -->
<a href="/posts/launch.html" class="block rounded-xl border p-4 focus-visible:outline-2 focus-visible:outline-offset-2">
  <img src="/img/launch.jpg" alt="" class="aspect-video w-full rounded-lg object-cover"
       style="view-transition-name: post-launch-image" />
  <h2 class="mt-3 text-lg font-semibold" style="view-transition-name: post-launch-title">Our launch</h2>
</a>

<!-- posts/launch.html: the same names on the matching elements -->
<article>
  <img src="/img/launch.jpg" alt="Launch party" class="aspect-[2/1] w-full object-cover"
       style="view-transition-name: post-launch-image" />
  <h1 class="mt-6 text-4xl font-bold" style="view-transition-name: post-launch-title">Our launch</h1>
</article>
```

**Same-document (JS-driven UI: filter a list, swap a tab, reorder).** Wrap the DOM mutation; everything else stays identical.

```js
function updateDom(fn) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!document.startViewTransition || reduce) { fn(); return; }
  document.startViewTransition(fn);
}

// Example: sort cards; each card has a stable, unique view-transition-name.
document.querySelector('#sort').addEventListener('change', (e) => {
  const grid = document.querySelector('#grid');
  const cards = [...grid.children];
  cards.sort((a, b) => (e.target.value === 'az'
    ? a.dataset.title.localeCompare(b.dataset.title)
    : b.dataset.title.localeCompare(a.dataset.title)));
  updateDom(() => grid.replaceChildren(...cards));
});
```

```html
<ul id="grid" class="grid gap-4 sm:grid-cols-3">
  <li data-title="Alpha" style="view-transition-name: card-alpha" class="rounded-lg border p-4">Alpha</li>
  <li data-title="Beta"  style="view-transition-name: card-beta"  class="rounded-lg border p-4">Beta</li>
</ul>
```

Why inline `style` for names: each name must be unique on the page at the moment of the snapshot, so a per-item name usually comes from the data (`post-${slug}`), which is easiest to emit inline from a template.

## Variations

- **Slide instead of crossfade**: `::view-transition-old(root) { animation: 250ms ease-in both slide-out }` and `::view-transition-new(root) { animation: 250ms ease-out both slide-in }` with keyframes that `translateX(-30px)` / `translateX(30px)`. Keep it to transform/opacity.
- **Direction-aware (back vs forward)**: in cross-document, read `navigation.activation.navigationType` in a `pageswap` / `pagereveal` listener, set `document.documentElement.dataset.dir = 'back'`, and target `html[data-dir=back]::view-transition-new(root)`.
- **Exclude a persistent header** from the crossfade: give it `view-transition-name: header`; it then stays still while the rest fades.
- **`view-transition-class`** (Chrome 125+, Safari 18.2+): style groups of named elements at once: `.card { view-transition-class: card }` then `::view-transition-group(.card) { animation-duration: 400ms }`.

## Pitfalls

- Duplicate `view-transition-name` values abort the transition silently (same-document throws in the promise, cross-document just skips). Names must be unique across the whole page, including elements hidden by `opacity: 0` (use `display: none` or `view-transition-name: none` for hidden ones).
- Cross-document transitions require both pages to be same-origin, both to declare `@view-transition { navigation: auto }`, and the navigation to be a normal link/`location` change, not a reload or cross-origin hop.
- The snapshot freezes the page: during the transition pointer events are blocked and the old frame is a static image. Keep durations short (200-400 ms) and never run one while the user is typing.
- The morph animates the element's *box*; the old and new snapshots are stretched to fit it while crossfading. A thumbnail morphing into a hero with a different aspect ratio looks smeared. Keep the aspect ratio identical on both pages (`aspect-video` on both) or accept a plain crossfade for that element.
- Fixed/sticky elements with a name get snapshotted at their on-screen position; a long page jump can produce a weird flight path. Name them so they stay in place or leave them in the root crossfade.
- Firefox older than 144 ignores all of this; test that the site is fine with zero animation, which it will be if you only added names and the `@view-transition` rule.

## Related skills

- `web-motion-page-transitions`
- `web-motion-reduced-motion`
- `web-motion-keyframes`
- `web-js-router-and-urls`
- `web-nav-tabs`
