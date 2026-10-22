---
name: web-motion-page-transitions
description: Implement fade/slide transitions between pages (multi-page site) and between panels/views in one document (tabs, steps, SPA-style swaps), with the exit/enter choreography, focus moved to the new content, and reduced-motion handling. Use whenever a user asks for "page transitions", "fade between pages", "slide to the next step", "animate switching views/tabs", or a site that "doesn't feel like it hard-reloads".
---

# Page and panel transitions

Transitions between views hide the jolt of content replacement and tell the user *where* they went (forward slides left, back slides right). Two layers matter more than the animation: the sequencing (old leaves, then new enters, or both overlap briefly) and focus management (keyboard and screen-reader users must land on the new content, not be left on a removed button). Where the View Transitions API is available it is the simplest route for both cases; the patterns here use it when present and fall back to CSS classes, so they work everywhere today.

## Pattern

**Between panels in one document** (step wizard, settings sections, client-side router views).

```html
<nav aria-label="Sections" class="flex gap-2">
  <button type="button" data-view="overview" aria-current="page"
          class="rounded-md px-3 py-1.5 aria-[current=page]:bg-zinc-900 aria-[current=page]:text-white
                 focus-visible:outline-2 focus-visible:outline-offset-2">Overview</button>
  <button type="button" data-view="billing"
          class="rounded-md px-3 py-1.5 aria-[current=page]:bg-zinc-900 aria-[current=page]:text-white
                 focus-visible:outline-2 focus-visible:outline-offset-2">Billing</button>
</nav>

<div class="relative mt-6 overflow-x-clip">
  <section id="overview" data-panel tabindex="-1" class="panel">
    <h2 class="text-xl font-semibold">Overview</h2>
  </section>
  <section id="billing" data-panel tabindex="-1" hidden class="panel">
    <h2 class="text-xl font-semibold">Billing</h2>
  </section>
</div>
```

```css
@media (prefers-reduced-motion: no-preference) {
  .panel { transition: opacity 200ms ease-out, transform 200ms ease-out; }
  .panel.is-leaving { opacity: 0; transform: translateX(calc(var(--dir, 1) * -24px)); }
  .panel.is-entering { opacity: 0; transform: translateX(calc(var(--dir, 1) * 24px)); }
}
```

```js
const nav = document.querySelector('nav[aria-label="Sections"]');
const order = [...nav.querySelectorAll('[data-view]')].map((b) => b.dataset.view);
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
let current = 'overview';
let busy = false;

function finishSwap(from, to) {
  from.hidden = true;
  to.hidden = false;
  to.focus({ preventScroll: true });        // announce + place keyboard focus on new view
}

async function show(id) {
  if (busy || id === current) return;
  const from = document.getElementById(current);
  const to = document.getElementById(id);
  const dir = order.indexOf(id) > order.indexOf(current) ? 1 : -1;
  nav.querySelectorAll('[data-view]').forEach((b) => {
    if (b.dataset.view === id) b.setAttribute('aria-current', 'page');
    else b.removeAttribute('aria-current');
  });
  current = id;

  if (reduce.matches) { finishSwap(from, to); return; }

  if (document.startViewTransition) {          // modern path: browser does exit/enter
    document.documentElement.style.setProperty('--dir', dir);
    await document.startViewTransition(() => finishSwap(from, to)).finished;
    return;
  }

  busy = true;                                  // class-based path
  from.style.setProperty('--dir', dir); to.style.setProperty('--dir', dir);
  from.classList.add('is-leaving');
  await new Promise((r) => from.addEventListener('transitionend', r, { once: true }));
  from.classList.remove('is-leaving');
  to.classList.add('is-entering');
  finishSwap(from, to);
  requestAnimationFrame(() => requestAnimationFrame(() => to.classList.remove('is-entering')));
  busy = false;
}

nav.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-view]');
  if (btn) show(btn.dataset.view);
});
```

**Between pages of a multi-page site**: opt into cross-document View Transitions and style the root crossfade as a slide; no JS, and browsers without support just load the page.

```css
@view-transition { navigation: auto; }
@media (prefers-reduced-motion: no-preference) {
  ::view-transition-old(root) { animation: 180ms ease-in both fade-out-left; }
  ::view-transition-new(root) { animation: 220ms ease-out both fade-in-right; }
  @keyframes fade-out-left { to { opacity: 0; transform: translateX(-16px); } }
  @keyframes fade-in-right { from { opacity: 0; transform: translateX(16px); } }
}
```

Why exit faster than enter (180 vs 220 ms): the user has already decided to leave; lingering on the old view feels like lag. Why `tabindex="-1"` and `focus()` on the new panel: it moves the reading cursor and keyboard focus to the new content without adding the panel to the tab order.

## Variations

- **Overlap instead of sequence**: stack panels with `absolute inset-0` and run leave and enter at the same time for a snappier feel; give the container a fixed `min-h` so the page does not collapse mid-swap.
- **Direction from history**: in a router, pass `dir = -1` for `popstate` (back) so the view slides the opposite way (`web-js-router-and-urls`).
- **Fade only** (`transform: none` in the leaving/entering rules) is safer for content-heavy views and for users who find lateral motion disorienting; the slide variant suits short steps.
- **Preserve scroll position** per panel: store `panel.scrollTop` before hiding and restore after `finishSwap` when panels scroll internally.

## Pitfalls

- Hidden panels still exist in the DOM. Use the `hidden` attribute (not just `opacity-0`) so their links and inputs are not reachable by Tab or read by screen readers.
- A `transitionend` wait never resolves if the transition did not run (element already at the target state, or motion reduced). The code guards with the `reduce` check; also keep a `setTimeout` safety net of duration + 50 ms if panels can be swapped during load.
- Rapid double clicks mid-animation leave two panels visible; the `busy` flag serialises them. With View Transitions, a new `startViewTransition` call skips the running one automatically.
- Do not move focus to the panel's heading with `scrollIntoView` on every switch; `preventScroll: true` keeps the viewport still, which is what users expect from a tab-like switch.
- Cross-document transitions only run for same-origin navigations with the rule on *both* pages; a missing rule on the destination gives a plain load with no error.
- Full-page slide on large screens moves a lot of pixels; keep offsets small (16-24 px) and durations under 250 ms.

## Related skills

- `web-motion-view-transitions`
- `web-motion-reduced-motion`
- `web-nav-tabs`
- `web-form-multi-step`
- `web-js-router-and-urls`
- `web-a11y-keyboard-and-focus`
