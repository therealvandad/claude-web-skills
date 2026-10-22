---
name: web-section-before-after-slider
description: 'Build a before-and-after image comparison slider: two stacked images, a native <input type="range"> driving clip-path so it is draggable, keyboard-operable and screen-reader labelled with no library, in Tailwind v4. Use whenever a user asks for a "before and after slider", "image comparison", "reveal slider", "drag to compare", "renovation before/after", or "photo retouching comparison".'
---

# Before and after slider

The honest way to compare two photos is to stack them and let the reader slide a divider. Every custom-drag implementation ends up reinventing pointer capture, touch handling and keyboard support; a transparent `<input type="range">` laid over the figure already does all of that. Its value drives a CSS variable that sets `clip-path` on the top image and positions the handle. The two `<img>` elements stay real images with real `alt`, so the comparison is still meaningful with the script off (both are visible, stacked).

## Pattern

```html
<section class="py-16 sm:py-24" aria-labelledby="compare-heading">
  <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
    <div class="max-w-xl">
      <p class="font-mono text-xs uppercase tracking-widest text-stone-500">Pennine Stone Restoration, Hebden Bridge</p>
      <h2 id="compare-heading" class="mt-3 text-3xl font-semibold tracking-tight text-balance text-stone-900 sm:text-4xl dark:text-stone-100">
        A 1904 millstone-grit facade, cleaned and repointed in eleven days
      </h2>
    </div>

    <figure class="mt-10">
      <div class="group relative aspect-[3/2] w-full overflow-hidden rounded-lg border border-stone-300 select-none [--pos:50%] dark:border-stone-700" data-compare>
        <img src="/img/facade-after.webp" width="1500" height="1000" alt="The same facade after cleaning: pale sandstone, fresh lime pointing, new lead flashing"
             class="absolute inset-0 h-full w-full object-cover" draggable="false">
        <img src="/img/facade-before.webp" width="1500" height="1000" alt="Terrace facade before work: soot-blackened stone, cracked cement pointing, a missing lintel corner"
             class="absolute inset-0 h-full w-full object-cover [clip-path:inset(0_calc(100%-var(--pos))_0_0)]" draggable="false">

        <!-- Divider and handle, purely visual -->
        <div class="pointer-events-none absolute inset-y-0 w-0.5 -translate-x-1/2 bg-white shadow-[0_0_0_1px_rgba(0,0,0,0.25)]" style="left: var(--pos)" aria-hidden="true">
          <span class="absolute top-1/2 left-1/2 flex size-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border border-stone-300 bg-white text-stone-900 shadow-md group-focus-within:outline-2 group-focus-within:outline-offset-2 group-focus-within:outline-stone-900">
            <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6-5 6 5 6M15 6l5 6-5 6"/></svg>
          </span>
        </div>

        <span class="pointer-events-none absolute top-3 left-3 rounded bg-stone-950/70 px-2 py-1 font-mono text-xs text-white" aria-hidden="true">Before</span>
        <span class="pointer-events-none absolute top-3 right-3 rounded bg-stone-950/70 px-2 py-1 font-mono text-xs text-white" aria-hidden="true">After</span>

        <!-- The control: full-size, invisible, native. -->
        <label for="compare-range" class="sr-only">Comparison position: percentage of the before photo shown</label>
        <input id="compare-range" type="range" min="0" max="100" value="50" step="1"
               class="absolute inset-0 h-full w-full cursor-ew-resize appearance-none bg-transparent opacity-0 focus-visible:opacity-0"
               aria-valuetext="50% before, 50% after" data-compare-range>
      </div>
      <figcaption class="mt-3 font-mono text-xs text-stone-500">
        Drag the handle or use the arrow keys. 14 Birchcliffe Road, March 2025. Photographs taken from the same tripod position.
      </figcaption>
    </figure>
  </div>
</section>
```

```js
document.querySelectorAll('[data-compare]').forEach((box) => {
  const range = box.querySelector('[data-compare-range]');
  const update = () => {
    const v = Number(range.value);
    box.style.setProperty('--pos', `${v}%`);
    range.setAttribute('aria-valuetext', `${v}% before, ${100 - v}% after`);
  };
  range.addEventListener('input', update);
  update();
});
```

Why these choices:

- The `<input type="range">` is stretched over the whole figure at `opacity-0`. Mouse drag, touch drag, tap-to-jump, arrow keys, Home, End and Page Up/Down all work because the browser implements them; nothing to write.
- `aria-valuetext` turns "50" into "50% before, 50% after" for screen readers, and the `sr-only` label explains what the slider controls.
- `clip-path: inset(0 calc(100% - var(--pos)) 0 0)` clips the before image from the right, so it occupies the left `--pos` percent. Both images stay full-size underneath; only the paint is clipped, so nothing resizes or reflows.
- `group-focus-within:outline-*` on the visible handle gives a focus ring where the eye is, since the real input is invisible.
- `aspect-[3/2]` plus `width`/`height` on both images reserves the box before load; the two photos must share the same aspect ratio and framing to compare honestly.
- `select-none` and `draggable="false"` stop the browser from starting a native image drag mid-slide.

## Variations

- **Vertical reveal**: use `clip-path: inset(0 0 calc(100% - var(--pos)) 0)` for a top-to-bottom wipe, rotate the range with `[writing-mode:vertical-lr]` and `direction: rtl` so up means more, and move the handle on `top`.
- **Labels that follow the handle**: place "Before" at `right: calc(100% - var(--pos) + 0.75rem)` and "After" at `left: calc(var(--pos) + 0.75rem)` so they never sit under the divider; hide whichever label has less than 20% of space.
- **Multiple comparisons in a grid**: the script already loops over every `[data-compare]`; put each `<figure>` in a `<ul role="list">` with `sm:grid-cols-2` and give each range a unique `id` and label.
- **Dark**: borders `stone-700`, handle `bg-stone-900 text-white border-stone-600`, labels unchanged (they already sit on a dark chip).

## Pitfalls

- Hover-only handles or a divider that appears on `mouseenter` are invisible on touch; the handle is always visible here, and the 40px target meets the minimum touch size.
- Images with different crops or lens positions make the "after" look like a different building. Shoot from a tripod or align in an editor before shipping.
- `opacity-0` on the input also hides the native focus ring, so the `group-focus-within` ring on the handle is mandatory, not polish.
- Missing `width`/`height` on the images or a missing `aspect-*` on the box collapses the figure to zero height until load, then jumps the whole page.
- Setting `--pos` with `transition` for smoothness makes the handle lag behind the pointer; leave it untransitioned, or transition only on keyboard input.
- Putting the "before" image on top with `width` changes instead of `clip-path` squashes the photo as it reveals; clip, never resize.

## Related skills

- `web-css-aspect-ratio-media`
- `web-a11y-keyboard-and-focus`
- `web-a11y-images-and-media`
- `web-design-images`
- `web-perf-images`
- `web-section-gallery-masonry`
