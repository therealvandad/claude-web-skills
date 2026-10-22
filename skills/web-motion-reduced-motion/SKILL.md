---
name: web-motion-reduced-motion
description: Set up a site-wide prefers-reduced-motion strategy: Tailwind motion-safe:/motion-reduce: variants, a global CSS safety net, the JS matchMedia check, a persisted "reduce motion" toggle, and rules for what to remove versus keep. Use whenever a user mentions "reduced motion", "accessible animations", "users who get motion sick", "turn off animations setting", or wants existing animations made accessible.
---

# Reduced motion strategy

`prefers-reduced-motion: reduce` is an OS-level setting people enable because animation makes them dizzy, nauseous, distracted, or because their device is slow. It does not mean "no motion ever": it means remove *non-essential* movement, especially large translations, parallax, zooms, auto-playing loops and anything that moves while the user is reading. Crossfades and tiny state changes are fine. The reliable approach has three layers: write each animation as opt-in with `motion-safe:` (so forgetting is safe), add a global safety net for anything that slipped through, and keep JS-driven motion behind one `matchMedia` check.

## Pattern

**Layer 1, per element (Tailwind):** every animating utility is prefixed; the unprefixed state is the still state.

```html
<div class="rounded-xl bg-white p-6 shadow
            motion-safe:transition-transform motion-safe:duration-200 motion-safe:hover:-translate-y-1
            motion-reduce:hover:shadow-lg">
  Lifts on hover, or gains a shadow instead when motion is reduced.
</div>

<img src="hero.gif" alt="Product tour" class="motion-reduce:hidden" />
<img src="hero-still.png" alt="Product tour" class="hidden motion-reduce:block" />
```

**Layer 2, global safety net** (in your main CSS): shortens, rather than disables, so `transitionend`/`animationend` still fire and JS that waits on them does not hang.

```css
@import "tailwindcss";

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Opt-in class toggle so users can override the OS setting on your site. */
@custom-variant motion-safe (&:where(html:not(.reduce-motion) *));
@custom-variant motion-reduce (&:where(html.reduce-motion *));
```

Note: the two `@custom-variant` lines *replace* Tailwind's media-query based variants with a class-based pair. Only add them if you ship the toggle below; otherwise keep the defaults.

**Layer 3, JS and the toggle:** one helper, one persisted preference, initial value from the OS.

```html
<label class="inline-flex items-center gap-2">
  <input id="motion-toggle" type="checkbox" class="size-4 accent-blue-600" />
  <span>Reduce motion</span>
</label>
```

```js
const KEY = 'reduce-motion';
const osPref = matchMedia('(prefers-reduced-motion: reduce)');
const root = document.documentElement;
const toggle = document.querySelector('#motion-toggle');

function current() {
  const stored = localStorage.getItem(KEY);          // 'true' | 'false' | null
  return stored === null ? osPref.matches : stored === 'true';
}

function apply(reduce) {
  root.classList.toggle('reduce-motion', reduce);
  if (toggle) toggle.checked = reduce;
}

export function prefersReducedMotion() {              // import this in every script that animates
  return root.classList.contains('reduce-motion');
}

apply(current());
osPref.addEventListener('change', () => { if (localStorage.getItem(KEY) === null) apply(osPref.matches); });
toggle?.addEventListener('change', () => { localStorage.setItem(KEY, String(toggle.checked)); apply(toggle.checked); });
```

Put the `apply(current())` call in an inline `<script>` in `<head>` (duplicating the three lines that read storage) so the class is set before first paint and there is no flash of animated content.

## Variations

- **No toggle, OS only**: skip the `@custom-variant` lines and the storage code; use `matchMedia('(prefers-reduced-motion: reduce)').matches` directly in JS. This is the default for most sites.
- **Keep fades, drop movement**: instead of removing an animation, give the reduced variant a crossfade: `motion-reduce:transition-opacity` with `motion-safe:transition-[opacity,transform]`.
- **Autoplaying video**: `video.autoplay` should be off when reduced; set `autoplay` from JS only when `!prefersReducedMotion()`, keep the poster image.
- **Smooth scroll**: `scroll-smooth` on `<html>` should be `motion-safe:scroll-smooth` (`web-nav-anchor-and-smooth-scroll`).

## Pitfalls

- `animation: none !important` in the safety net breaks any JS awaiting `animationend`; the 0.01 ms trick ends the animation in one frame instead and the event still fires.
- The safety net does not catch Web Animations API calls (`el.animate()`) or JS-driven `requestAnimationFrame` loops; those must check the preference themselves.
- Reduced motion is not "disable everything": loading spinners, progress indicators and focus rings must remain. A frozen spinner looks like a crash; dim it or slow it instead (`web-motion-loading-and-progress`).
- `motion-reduce:` and `motion-safe:` are complementary, not opposites of "nothing": a class with neither prefix applies in both modes. Write the still state unprefixed and the motion state with `motion-safe:`.
- Testing: Chrome DevTools > Rendering > "Emulate CSS media feature prefers-reduced-motion", macOS Accessibility > Display > Reduce motion, Windows Settings > Accessibility > Visual effects > Animation effects. Test both states before shipping.
- Scroll-driven animations and `scroll-behavior: smooth` count as motion; `animation-duration` overrides do not stop a scroll timeline, so gate those in their own `@media` block (`web-motion-parallax-and-scroll-driven`).

## Related skills

- `web-motion-transitions`
- `web-motion-keyframes`
- `web-motion-scroll-reveal`
- `web-motion-parallax-and-scroll-driven`
- `web-a11y-images-and-media`
- `web-js-storage`
