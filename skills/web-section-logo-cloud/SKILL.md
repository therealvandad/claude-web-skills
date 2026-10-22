---
name: web-section-logo-cloud
description: Build a customer logo strip: a row of grayscale SVG logos that wraps on phones, plus a marquee variant that pauses on hover and focus and stops under reduced motion, in Tailwind v4. Use whenever a user asks for a logo cloud, logo bar, "trusted by", "as seen in", press or partner logos, or "the company logos under the hero".
---

# Logo cloud

A logo strip is social proof with no copy: the reader scans five or six marks and decides whether these are companies like theirs. It fails when logos differ in visual weight (one in full colour, one tiny), when the row overflows on a phone, or when a marquee cannot be stopped. Normalise every logo to a fixed height and a single ink colour, make it a real list, and let it wrap by default; animate only as a deliberate variant.

## Pattern

```html
<section class="py-12 sm:py-16" aria-labelledby="logos-heading">
  <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
    <h2 id="logos-heading" class="text-center font-mono text-xs uppercase tracking-widest text-stone-500">
      Payroll for 1,900 companies, including
    </h2>

    <ul role="list" class="mt-8 flex flex-wrap items-center justify-center gap-x-10 gap-y-6 sm:gap-x-14">
      <li>
        <img src="/logos/brakspear-haulage.svg" width="140" height="32" alt="Brakspear Haulage"
             class="h-7 w-auto opacity-70 grayscale transition hover:opacity-100 hover:grayscale-0 dark:invert sm:h-8" loading="lazy">
      </li>
      <li>
        <img src="/logos/oriel-dental.svg" width="120" height="32" alt="Oriel Dental Group"
             class="h-7 w-auto opacity-70 grayscale transition hover:opacity-100 hover:grayscale-0 dark:invert sm:h-8" loading="lazy">
      </li>
      <li>
        <img src="/logos/fenwick-and-lowe.svg" width="160" height="32" alt="Fenwick & Lowe Solicitors"
             class="h-7 w-auto opacity-70 grayscale transition hover:opacity-100 hover:grayscale-0 dark:invert sm:h-8" loading="lazy">
      </li>
      <li>
        <img src="/logos/tyne-print.svg" width="110" height="32" alt="Tyne Print Works"
             class="h-7 w-auto opacity-70 grayscale transition hover:opacity-100 hover:grayscale-0 dark:invert sm:h-8" loading="lazy">
      </li>
      <li>
        <img src="/logos/castlegate-brewing.svg" width="150" height="32" alt="Castlegate Brewing"
             class="h-7 w-auto opacity-70 grayscale transition hover:opacity-100 hover:grayscale-0 dark:invert sm:h-8" loading="lazy">
      </li>
      <li>
        <img src="/logos/mersey-scaffold.svg" width="130" height="32" alt="Mersey Scaffold Ltd"
             class="h-7 w-auto opacity-70 grayscale transition hover:opacity-100 hover:grayscale-0 dark:invert sm:h-8" loading="lazy">
      </li>
    </ul>
  </div>
</section>
```

Marquee variant. The track is duplicated once so the loop is seamless; the copy is `aria-hidden` so screen readers hear each name once.

```html
<div class="group relative overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]"
     data-marquee>
  <ul role="list" class="flex w-max items-center gap-14 motion-safe:animate-[marquee_40s_linear_infinite] group-hover:[animation-play-state:paused] group-focus-within:[animation-play-state:paused]">
    <li><a href="/customers/brakspear" class="block rounded focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-stone-900"><img src="/logos/brakspear-haulage.svg" width="140" height="32" alt="Brakspear Haulage" class="h-8 w-auto grayscale"></a></li>
    <!-- remaining logos -->
  </ul>
  <ul role="list" aria-hidden="true" class="absolute top-0 left-full flex w-max items-center gap-14 pl-14 motion-safe:animate-[marquee_40s_linear_infinite] group-hover:[animation-play-state:paused] group-focus-within:[animation-play-state:paused]">
    <!-- exact copy of the first list -->
  </ul>
</div>
```

```css
@keyframes marquee {
  to { transform: translateX(-100%); }
}
```

```js
// Give the marquee a visible stop control; CSS already pauses on hover and keyboard focus.
document.querySelectorAll('[data-marquee]').forEach((wrap) => {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'mt-3 text-xs text-stone-500 underline underline-offset-4';
  btn.textContent = 'Pause logos';
  btn.setAttribute('aria-pressed', 'false');
  btn.addEventListener('click', () => {
    const paused = btn.getAttribute('aria-pressed') === 'true';
    wrap.querySelectorAll('ul').forEach((ul) => (ul.style.animationPlayState = paused ? 'running' : 'paused'));
    btn.setAttribute('aria-pressed', String(!paused));
    btn.textContent = paused ? 'Pause logos' : 'Play logos';
  });
  wrap.after(btn);
});
```

Why these choices:

- A fixed `h-7`/`h-8` with `w-auto` is the only normalisation that works across wordmarks and square marks; `width`/`height` attributes still reserve space before the SVG loads.
- `grayscale opacity-70` turns six brands into one texture; `hover:grayscale-0` is a reward, not the default, so the section does not fight the page's accent.
- `dark:invert` is correct only for single-colour dark logos. For multi-colour marks, ship a second file and swap with `<picture>` and `media="(prefers-color-scheme: dark)"`.
- `motion-safe:animate-*` means the marquee never starts under `prefers-reduced-motion`; the static wrapping row is the fallback, not a frozen half-visible track.
- The heading is a real `<h2>` even though it is small; "trusted by" sections appear in landmark lists when they carry a heading.

## Variations

- **"As seen in" press row**: same markup with publication wordmarks, a left-aligned heading, and `justify-start`. Press logos go in a `<ul>` of links to the actual articles, with `rel="noopener"` and the publication in `alt`.
- **Bordered strip**: wrap the `<ul>` in `border-y border-stone-200 py-8` with no heading, placed directly under the hero. Logos `h-6` only; it is a divider that happens to carry proof.
- **Two rows on phones**: `grid grid-cols-3 gap-8 sm:flex` with `place-items-center` so six logos sit as 3x2 instead of a ragged wrap.
- **With a count link**: after the list, `<a href="/customers" class="mt-6 block text-center text-sm underline">See all 1,900 customers</a>`. Specific count, real page.

## Pitfalls

- PNG logos at different resolutions look mismatched and blur on retina screens. Ask for SVG; if only PNG exists, export at 2x and set `height` in CSS, not the attribute alone.
- A marquee that only pauses on hover cannot be stopped on touch devices or by keyboard users; the button above and `group-focus-within` cover both, and `motion-safe:` covers users who asked for no motion.
- Marquee items that are links in both copies produce duplicate tab stops. Keep links only in the first list; the `aria-hidden` copy must have no focusable elements, so strip `<a>` from it or add `tabindex="-1"`.
- `mask-image` fades the edges but also hides the first logo on short tracks. Ensure the track is wider than the container, or drop the mask below `sm:`.
- Logos with white backgrounds baked in look like stickers on dark sections. Ask for transparent files; `mix-blend-multiply` on light backgrounds hides a white box but not on dark ones.
- Eight or more logos in one row shrink to illegible on tablets. Six per row is the ceiling; split into two rows or use the marquee.

## Related skills

- `web-motion-counters-and-tickers`
- `web-motion-reduced-motion`
- `web-a11y-images-and-media`
- `web-perf-images`
- `web-layout-landing-page`
- `web-layout-testimonials`
