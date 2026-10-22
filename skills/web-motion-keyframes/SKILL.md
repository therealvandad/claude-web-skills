---
name: web-motion-keyframes
description: Write @keyframes animations and register them as Tailwind v4 utilities via @theme (--animate-*), with pulse, shake, bounce-in, and attention examples that animate transform/opacity and pause under reduced motion. Use whenever a user asks for a "looping animation", "keyframes", "animate-* class", "wiggle/shake/pulse/bounce", "custom animation", or something transitions cannot express.
---

# Keyframes and Tailwind `animate-*`

Transitions interpolate between two states; keyframes describe a timeline with as many stops as you like and can loop, alternate, or fire without any state change. Tailwind v4 ships `animate-spin`, `animate-ping`, `animate-pulse` and `animate-bounce`. Anything else you register once in `@theme` as `--animate-<name>` and then use as `animate-<name>` like any other utility (including with `motion-safe:`, `hover:` and `group-*` variants). Keep every keyframe to `transform`, `opacity` and occasionally `color`; the browser can run those off the main thread.

## Pattern

Register three reusable animations and apply them.

```css
@import "tailwindcss";

@theme {
  /* name: duration easing [delay] [iteration] [direction] [fill] keyframe-name */
  --animate-shake: shake 400ms cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
  --animate-bounce-in: bounce-in 500ms cubic-bezier(0.34, 1.56, 0.64, 1) both;
  --animate-fade-up: fade-up 400ms ease-out both;

  @keyframes shake {
    10%, 90% { transform: translateX(-1px); }
    20%, 80% { transform: translateX(2px); }
    30%, 50%, 70% { transform: translateX(-4px); }
    40%, 60% { transform: translateX(4px); }
  }
  @keyframes bounce-in {
    from { opacity: 0; transform: scale(0.8); }
    to   { opacity: 1; transform: scale(1); }
  }
  @keyframes fade-up {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
}
```

```html
<!-- Entrance: runs once on load, skipped (element simply visible) under reduced motion -->
<section class="motion-safe:animate-fade-up rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
  <h2 class="text-2xl font-bold">Welcome back</h2>
</section>

<!-- Attention: shake on invalid submit, retriggerable from JS -->
<form id="login" novalidate class="mt-6 space-y-3">
  <label class="block">
    <span class="text-sm font-medium">Email</span>
    <input type="email" name="email" required
           class="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2
                  aria-[invalid=true]:border-red-500 aria-[invalid=true]:motion-safe:animate-shake" />
  </label>
  <button class="rounded-md bg-blue-600 px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2">
    Sign in
  </button>
</form>

<!-- Notification dot: Tailwind built-in, runs forever, so stopped under reduced motion -->
<span class="relative inline-flex size-3">
  <span class="absolute inline-flex size-full rounded-full bg-red-400 opacity-75 motion-safe:animate-ping"></span>
  <span class="relative inline-flex size-3 rounded-full bg-red-500"></span>
</span>
```

```js
const form = document.querySelector('#login');
const email = form.elements.email;

form.addEventListener('submit', (e) => {
  if (email.checkValidity()) return;
  e.preventDefault();
  // Re-run an animation: remove the state, force a reflow, add it back.
  email.setAttribute('aria-invalid', 'false');
  void email.offsetWidth;
  email.setAttribute('aria-invalid', 'true');
  email.focus();
});
```

Why `both` fill-mode: the element holds the first keyframe before the delay and the last after it ends, so there is no flash of the final state before an entrance starts and no snap back after it finishes.

## Variations

- **Stagger children** with an inline delay: `style="animation-delay: calc(var(--i) * 80ms)"` and `--i` set per item; or in CSS `li:nth-child(n) { animation-delay: calc(var(--n) * 80ms) }`. Keep total stagger under ~600 ms.
- **Pause on hover** for decorative loops: `hover:[animation-play-state:paused]` on marquees and spinners users may want to read.
- **Infinite with alternate**: `--animate-float: float 3s ease-in-out infinite alternate;` with `@keyframes float { to { transform: translateY(-8px) } }` for a gentle hovering illustration.
- **Play once per page load only**: add `animation-iteration-count: 1` (the default) and avoid re-adding the class on re-render; keyframes restart every time the class is applied to a freshly created node.
- **Animate `color`/`background-color`** in a keyframe for a highlight flash (`@keyframes flash { from { background-color: var(--color-yellow-200) } }`): fine for small elements.

## Pitfalls

- Infinite animations are the single biggest reduced-motion offender. Always `motion-safe:animate-*` for loops; the fallback is a static element, which is what those users asked for.
- A keyframe that animates `height`, `width`, `top`/`left` or `box-shadow` forces layout or paint each frame. Reach for `transform: scale()`/`translate()` and `opacity`; fake a shadow change by cross-fading a pseudo-element.
- `@keyframes` placed outside `@theme` work too, but then the `animate-<name>` utility does not exist; you need `[animation:shake_400ms_both]` arbitrary syntax or a plain class. Put them in `@theme` so they are first-class.
- Replaying by toggling a class in the same tick does nothing; the reflow trick (`void el.offsetWidth`) or `el.getAnimations().forEach(a => a.cancel())` then re-adding is required.
- Tailwind v4 generates only utilities it sees in your markup. A class built dynamically in JS (`'animate-' + name`) is purged; write the full class name somewhere static or use `@source inline("animate-shake")`.
- `animate-bounce` and `animate-ping` run forever by default. On a list of 50 items that is 50 compositor layers; limit to one or two visible attention cues.

## Related skills

- `web-motion-transitions`
- `web-motion-reduced-motion`
- `web-motion-loading-and-progress`
- `web-motion-scroll-reveal`
- `web-css-variables-theming`
