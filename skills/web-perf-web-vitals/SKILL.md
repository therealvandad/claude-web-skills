---
name: web-perf-web-vitals
description: Measure and fix Core Web Vitals (LCP, INP, CLS) on a static site - what each metric means, measuring with Lighthouse, devtools, PageSpeed Insights and a tiny field script, and the usual fixes by payoff. Use when a user says "Lighthouse score", "PageSpeed", "Core Web Vitals", "my site is slow", "layout shift", "LCP is bad", or "input delay".
---

# Core Web Vitals

Google reports three field metrics and ranks on them: **LCP** (Largest Contentful Paint, when the biggest above-the-fold element rendered; good under 2.5 s), **INP** (Interaction to Next Paint, the slowest click/tap/key response over the visit; good under 200 ms), and **CLS** (Cumulative Layout Shift, how much content jumped; good under 0.1). Lab tools (Lighthouse) are for finding problems; field data (real users, via the Chrome UX Report or your own beacon) is what counts. Fix in the order LCP, CLS, INP: for a static site the first two are usually the whole story.

## Pattern

Measure in the lab, from the terminal (works on Windows and Unix; no global install):

```bash
npx lighthouse https://example.com --preset=desktop --output=html --output-path=./lighthouse.html --only-categories=performance
npx lighthouse https://example.com --form-factor=mobile --throttling-method=simulate --output=json --output-path=./lh.json
node -e "const r=require('./lh.json').audits;for(const k of ['largest-contentful-paint','cumulative-layout-shift','total-blocking-time'])console.log(k,r[k].displayValue)"
```

Mobile with throttling is the number that matters; desktop is flattering. Then confirm what the LCP element actually is: in Chrome devtools, Performance panel, record a reload, click the LCP marker in the Timings track. CLS sources appear in the Layout Shifts track. For INP, use the Performance panel's Interactions track or the "Web Vitals" extension.

Field measurement with no library, sending to whatever endpoint you own:

```html
<script type="module">
  // Reports LCP, CLS and INP once per page view using PerformanceObserver.
  const send = (name, value) => navigator.sendBeacon?.("/vitals", JSON.stringify({ name, value, url: location.pathname }));
  new PerformanceObserver(l => { const e = l.getEntries().at(-1); if (e) send("LCP", e.startTime); })
    .observe({ type: "largest-contentful-paint", buffered: true });
  let cls = 0;
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) cls += e.value; })
    .observe({ type: "layout-shift", buffered: true });
  let inp = 0;
  new PerformanceObserver(l => { for (const e of l.getEntries()) inp = Math.max(inp, e.duration); })
    .observe({ type: "event", durationThreshold: 40, buffered: true });
  addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") { send("CLS", cls); send("INP", inp); } });
</script>
```

The usual fixes, by metric:

| Metric | Cause | Fix |
| --- | --- | --- |
| LCP | hero image discovered late / lazy | `fetchpriority="high"`, `<link rel="preload" as="image">`, never `loading="lazy"` on it (`web-perf-images`) |
| LCP | slow server / no CDN / no compression | static host with CDN, Brotli on; check `content-encoding: br` in devtools |
| LCP | render-blocking script or big CSS | `type="module"`, one small stylesheet (`web-perf-css-and-js-loading`) |
| LCP | web font delays headline | preload one woff2, `font-display: swap` (`web-perf-fonts`) |
| CLS | images without dimensions | `width`/`height` on every `<img>`, `aspect-*` boxes for embeds |
| CLS | font swap changes line wraps | metric-matched fallback with `size-adjust` |
| CLS | content injected above existing content (banners, ads) | reserve space with `min-h-*`; insert below the fold or in a fixed overlay |
| CLS | animating `top`/`height` | animate `transform`/`opacity` only (`web-motion-transitions`) |
| INP | long tasks in click handlers | do the visible update first, then `setTimeout(work, 0)` or `scheduler.yield()` for the rest |
| INP | heavy third-party scripts | load `async`, drop what you do not need, defer to idle |
| INP | giant DOM (> 1500 nodes) | paginate lists, `content-visibility: auto` on off-screen sections |

## Variations

- **Deep page sections**: `<section class="[content-visibility:auto] [contain-intrinsic-size:auto_600px]">` skips rendering work for off-screen content and helps both LCP and INP on long pages.
- **CI gate**: `npm i -D @lhci/cli`, then `npx lhci autorun --collect.staticDistDir=dist --assert.preset=lighthouse:recommended` fails the build when scores regress. Configure thresholds in `lighthouserc.json`.
- **No backend for the beacon**: send to your analytics provider's custom-event endpoint instead, or log to `console.table` during development and skip the beacon.
- **Google's field data**: paste the URL into PageSpeed Insights; the top section ("Discover what your real users are experiencing") is CrUX data and is what Search Console uses. If it says "no data", the site has too little traffic and lab numbers are all you have.

## Pitfalls

- Lighthouse scores vary run to run by 5-10 points; run three times and compare medians, or use `--throttling-method=simulate` consistently.
- Running Lighthouse against `localhost` or a dev server with the Play CDN measures the wrong thing. Build for production and test the deployed URL or a `npx serve dist` of the built output.
- A `score of 100` on desktop with 60 on mobile is normal; optimize for mobile.
- Hiding CLS by making the shifting element `position: absolute` or animating it in still counts if it moves other content. Reserve space instead.
- The `event` PerformanceObserver entry type needs `durationThreshold`; the default 104 ms hides most interactions.
- Cookie banners are a classic CLS and LCP killer: render them as a fixed-position overlay that does not push content, and do not make them the largest element in the viewport.

## Related skills

- `web-perf-images`
- `web-perf-fonts`
- `web-perf-css-and-js-loading`
- `web-perf-caching-and-service-worker`
- `web-ship-launch-checklist`
- `web-motion-transitions`
