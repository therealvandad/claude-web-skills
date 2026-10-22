---
name: web-interactive-countdown-timers
description: Build a countdown to a date, a pomodoro timer and a stopwatch with laps from one small module, using wall-clock timestamps so they stay accurate in background tabs, Intl-formatted spoken durations and quiet screen reader announcements. Use whenever a user asks for a "countdown", "launch timer", "days until", "pomodoro", "stopwatch" or "timer".
---

# Countdown, pomodoro and stopwatch

Never count ticks. `setInterval` is throttled to once a second or slower in background tabs, so a timer that subtracts one per tick drifts and stalls. Store a timestamp instead (the target date, the end time, or the start time), recompute from `Date.now()` on every tick, and redraw immediately when the tab becomes visible again. One shared ticker does that for all three widgets, and each widget is just a formatting function.

## Pattern

```html
<section data-timer="countdown" data-target="2026-12-04T09:00:00+01:00" class="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
  <h2 class="text-sm font-medium text-gray-600 dark:text-gray-400">Frontend Nord doors open in</h2>
  <time data-js="out" role="timer" aria-label="Time until doors open" class="mt-2 flex gap-4 text-3xl font-semibold tabular-nums">
    <span><b data-part="days">00</b><small class="ml-1 text-sm font-normal">d</small></span>
    <span><b data-part="hours">00</b><small class="ml-1 text-sm font-normal">h</small></span>
    <span><b data-part="minutes">00</b><small class="ml-1 text-sm font-normal">m</small></span>
    <span><b data-part="seconds">00</b><small class="ml-1 text-sm font-normal">s</small></span>
  </time>
  <p data-js="status" aria-live="polite" class="sr-only"></p>
</section>

<section data-timer="pomodoro" class="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
  <h2 data-js="mode" class="text-sm font-medium">Focus, 25 minutes</h2>
  <p data-js="out" role="timer" class="mt-2 text-5xl font-semibold tabular-nums">25:00</p>
  <button data-action="toggle" type="button" class="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Start</button>
  <button data-action="reset" type="button" class="mt-3 rounded-lg px-4 py-2 underline">Reset</button>
  <p data-js="status" aria-live="polite" class="sr-only"></p>
</section>

<section data-timer="stopwatch" class="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
  <p data-js="out" role="timer" class="text-5xl font-semibold tabular-nums">00:00.00</p>
  <div class="mt-3 flex gap-2">
    <button data-action="toggle" type="button" class="rounded-lg bg-indigo-600 px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Start</button>
    <button data-action="lap" type="button" class="rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-700">Lap</button>
    <button data-action="reset" type="button" class="rounded-lg px-4 py-2 underline">Reset</button>
  </div>
  <ol data-js="laps" class="mt-3 list-inside list-decimal text-sm tabular-nums"></ol>
</section>
```

```js
// /js/timers.js
const pad = (n) => String(n).padStart(2, '0');
const clock = (ms, cs = false) => `${pad(Math.floor(ms / 60000))}:${pad(Math.floor(ms / 1000) % 60)}${cs ? '.' + pad(Math.floor(ms % 1000 / 10)) : ''}`;
const spoken = (n, unit, lang) => new Intl.NumberFormat(lang, { style: 'unit', unit, unitDisplay: 'long' }).format(n);

function createTicker(fn, every = 250) {            // ticks only while wanted AND the tab is visible
  let id = 0, wanted = false;
  const tick = () => fn(Date.now());
  const sync = () => { clearInterval(id); id = 0; if (wanted && !document.hidden) { tick(); id = setInterval(tick, every); } };
  document.addEventListener('visibilitychange', sync);   // redraw from the clock the moment the tab returns
  return { start() { wanted = true; sync(); }, stop() { wanted = false; sync(); },
           destroy() { wanted = false; sync(); document.removeEventListener('visibilitychange', sync); } };
}

const kinds = {
  countdown(root, $) {
    const target = Date.parse(root.dataset.target), lang = document.documentElement.lang || 'en';
    let lastKey = null;
    const t = createTicker((now) => {
      const s = Math.floor(Math.max(0, target - now) / 1000);
      const p = { days: Math.floor(s / 86400), hours: Math.floor(s % 86400 / 3600), minutes: Math.floor(s % 3600 / 60), seconds: s % 60 };
      for (const k in p) root.querySelector(`[data-part="${k}"]`).textContent = pad(p[k]);
      $('out').dateTime = `P${p.days}DT${p.hours}H${p.minutes}M${p.seconds}S`;
      const key = s === 0 ? 'done' : p.days ? `d${p.days}` : p.hours ? `h${p.hours}` : `m${p.minutes}`;
      if (key !== lastKey) {                         // announce on day, hour or minute change only, not every second
        if (lastKey) $('status').textContent = s === 0 ? 'The doors are open.' : p.days ? spoken(p.days, 'day', lang) + ' left' : p.hours ? spoken(p.hours, 'hour', lang) + ' left' : spoken(p.minutes, 'minute', lang) + ' left';
        lastKey = key;
      }
      if (s === 0) t.stop();
    });
    t.start();
    return t.destroy;
  },
  pomodoro(root, $) {
    const lengths = { Focus: 25 * 60000, Break: 5 * 60000 }, original = document.title;
    let mode = 'Focus', left = lengths.Focus, endAt = 0, running = false;
    const show = (ms) => { $('out').textContent = clock(ms); document.title = running ? `${clock(ms)} ${mode}` : original; };
    const t = createTicker((now) => { const rem = Math.max(0, endAt - now); show(rem); if (rem === 0) finish(); });
    function finish() {
      t.stop(); running = false;
      const done = mode; mode = mode === 'Focus' ? 'Break' : 'Focus'; left = lengths[mode];
      $('mode').textContent = `${mode}, ${left / 60000} minutes`; show(left);
      root.querySelector('[data-action="toggle"]').textContent = `Start ${mode.toLowerCase()}`;
      $('status').textContent = `${done} finished. ${mode} is next.`;
    }
    root.addEventListener('click', (e) => {
      const act = e.target.closest('[data-action]')?.dataset.action;
      if (act === 'toggle') {
        running = !running;
        if (running) { endAt = Date.now() + left; t.start(); } else { left = Math.max(0, endAt - Date.now()); t.stop(); show(left); }
        e.target.textContent = running ? 'Pause' : 'Resume';
      } else if (act === 'reset') { t.stop(); running = false; mode = 'Focus'; left = lengths.Focus; show(left); $('mode').textContent = 'Focus, 25 minutes'; root.querySelector('[data-action="toggle"]').textContent = 'Start'; }
    });
    return () => { t.destroy(); document.title = original; };
  },
  stopwatch(root, $) {
    let base = 0, startedAt = 0;                     // elapsed = banked time + time since the last start
    const elapsed = (now = Date.now()) => base + (startedAt ? now - startedAt : 0);
    const t = createTicker((now) => { $('out').textContent = clock(elapsed(now), true); }, 50);
    root.addEventListener('click', (e) => {
      const act = e.target.closest('[data-action]')?.dataset.action;
      if (act === 'toggle') {
        if (startedAt) { base = elapsed(); startedAt = 0; t.stop(); } else { startedAt = Date.now(); t.start(); }
        e.target.textContent = startedAt ? 'Stop' : 'Resume';
      } else if (act === 'lap' && elapsed() > 0) {
        const li = document.createElement('li'); li.textContent = clock(elapsed(), true); $('laps').prepend(li);
      } else if (act === 'reset') { base = startedAt = 0; t.stop(); $('out').textContent = clock(0, true); $('laps').replaceChildren(); root.querySelector('[data-action="toggle"]').textContent = 'Start'; }
    });
    return t.destroy;
  },
};

export function initTimers() {
  return [...document.querySelectorAll('[data-timer]')].map((root) =>
    kinds[root.dataset.timer](root, (n) => root.querySelector(`[data-js="${n}"]`)));
}
const cleanups = initTimers();                       // call each entry to tear down: cleanups.forEach((c) => c())
```

## Variations

- **Real Intl durations**: where `Intl.DurationFormat` exists (Chrome 129+, Safari 18+, Firefox 136+), `new Intl.DurationFormat(lang, { style: 'long' }).format({ days: 3, hours: 4 })` replaces the `NumberFormat` helper; feature-check with `typeof Intl.DurationFormat === 'function'`.
- **Recurring target**: compute the next occurrence (next Friday 17:00) in the user's zone with `Temporal` or a small helper, then reuse `data-target`; see `web-data-number-formatting` for locale output.
- **Alert at the end**: ask `Notification.requestPermission()` only on a button click, not on load; also set a `setTimeout` for `endAt - now`, which still fires in a hidden tab.
- **Progress ring**: map `rem / total` onto `stroke-dashoffset`; see `web-data-donut-and-progress`.

## Pitfalls

- A date without an offset (`2026-12-04T09:00`) is parsed in the visitor's zone, so the event "opens" at different moments. Always write the offset or `Z`.
- `role="timer"` has implicit `aria-live="off"`, which is right: a live region updating every second is unusable. Announce milestones in a separate polite `status`, as above.
- Keep `tabular-nums` on every changing number, or the layout jitters as digits change width.
- Pausing a pomodoro must bank the remaining time (`left`) before stopping; restarting from the original length is the classic bug.
- Do not run `requestAnimationFrame` for a seconds display; 60 redraws a second burn battery for no visible gain. The stopwatch's 50 ms interval is the most you need.
- Countdown targets can be edited in devtools; never use one to gate a sale or an embargo.

## Related skills

- `web-motion-counters-and-tickers`
- `web-motion-reduced-motion`
- `web-data-number-formatting`
- `web-data-donut-and-progress`
- `web-a11y-aria-patterns`
- `web-js-events-debounce-throttle`
