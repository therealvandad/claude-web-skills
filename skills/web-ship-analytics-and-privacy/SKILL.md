---
name: web-ship-analytics-and-privacy
description: Add privacy-respecting analytics to a static site - cookie-free tools (Plausible, Umami, GoatCounter, Cloudflare) that need no banner, an accessible consent dialog when cookies are used, custom event tracking, and a privacy page outline. Use when a user says "add analytics", "Google Analytics", "cookie banner", "GDPR", "consent", "track clicks" or "privacy policy".
---

# Analytics and privacy

Default to a cookie-free, aggregate analytics tool: it answers "how many visitors, from where, which pages" without identifying anyone, so no consent banner is required under GDPR/ePrivacy and the page stays fast (one script under 2 KB, loaded `defer`). Reach for Google Analytics only if someone needs its reports, and then you owe users a real consent dialog that blocks the script until they opt in. Either way, publish a short privacy page that says exactly what is collected.

## Pattern

Cookie-free analytics, one tag, no banner. The snippet is the same shape for every provider:

```html
<!-- Plausible (hosted or self-hosted). Umami: <script defer src="https://umami.example.com/script.js" data-website-id="..."></script> -->
<script defer data-domain="example.com" src="https://plausible.io/js/script.js"></script>
```

Track an event without a library: name the action in a data attribute and delegate one listener.

```html
<a href="/pricing" data-event="cta-click" data-prop-location="hero" class="rounded-lg bg-brand px-5 py-3 font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">See pricing</a>
```

```js
// js/analytics.js - provider-agnostic wrapper; swap the body of track() when changing tools
export function track(name, props = {}) {
  window.plausible?.(name, { props });            // Plausible
  // window.umami?.track(name, props);            // Umami
  // window.goatcounter?.count({ path: name });   // GoatCounter
}
document.addEventListener("click", e => {
  const el = e.target.closest("[data-event]");
  if (!el) return;
  const props = Object.fromEntries(Object.entries(el.dataset).filter(([k]) => k.startsWith("prop")).map(([k, v]) => [k.slice(4).toLowerCase(), v]));
  track(el.dataset.event, props);
});
```

If you must use a cookie-setting tool (GA4, Meta Pixel), gate it behind consent. Native `<dialog>`, no library, stores the choice in `localStorage`, and loads the script only after "Accept":

```html
<dialog id="consent" class="fixed inset-x-4 bottom-4 m-0 w-auto max-w-md rounded-xl border border-gray-200 bg-white p-5 shadow-lg backdrop:bg-transparent sm:inset-x-auto sm:right-4" aria-labelledby="consent-title">
  <form method="dialog">
    <h2 id="consent-title" class="text-base font-semibold">Analytics cookies</h2>
    <p class="mt-1 text-sm text-gray-600">We would like to use Google Analytics to understand how the site is used. No cookies are set unless you accept. <a href="/privacy" class="underline">Privacy policy</a></p>
    <div class="mt-4 flex gap-2">
      <button value="accept" class="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">Accept</button>
      <button value="reject" class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand">Reject</button>
    </div>
  </form>
</dialog>
<script type="module">
  const KEY = "consent.analytics.v1", dialog = document.getElementById("consent");
  const loadGA = () => {
    const s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX";
    document.head.append(s);
    window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date()); gtag("config", "G-XXXXXXX", { anonymize_ip: true });
  };
  let choice = null; try { choice = localStorage.getItem(KEY); } catch {}
  if (choice === "accept") loadGA();
  else if (choice !== "reject") { dialog.show(); dialog.addEventListener("close", () => { try { localStorage.setItem(KEY, dialog.returnValue); } catch {} if (dialog.returnValue === "accept") loadGA(); }); }
</script>
```

`dialog.show()` (not `showModal()`) keeps the rest of the page usable; a consent prompt must not trap the user. Give the dialog a "Reject" button as prominent as "Accept"; pre-ticked or buried refusal is not valid consent.

## Variations

- **Zero third parties**: Cloudflare Web Analytics (free, cookie-free, works on any host via a beacon snippet) or GoatCounter (open source, free for personal use, a 3 KB script). Both need no consent banner.
- **Self-hosted**: Umami or Plausible CE in Docker on a small VPS; the script is first-party, which also sidesteps ad blockers that block analytics domains.
- **Server logs only**: Netlify Analytics and Cloudflare's built-in traffic stats need no script at all; counts are approximate but client-side cost is zero.
- **Re-open consent**: a footer link `<button data-consent-open>Cookie settings</button>` that clears the stored key and calls `dialog.show()` again; required so users can withdraw consent.

## Pitfalls

- A consent banner for a cookie-free tool is unnecessary clutter and hurts CLS and LCP; do not add one "to be safe". Read the provider's data policy to confirm it uses no cookies or fingerprinting.
- Loading GA before consent and "deleting cookies later" is not compliant. The script must not load at all until the user accepts.
- Banners that push the page down cause layout shift; keep them `fixed` at the bottom and reserve nothing in the flow.
- `localStorage` throws in some private modes; always wrap in `try/catch` and treat failure as "not decided".
- Ad blockers block most analytics domains; expect 20-40 percent under-counting and never make site functionality depend on the analytics script having loaded (`window.plausible?.()`).
- A privacy page needs, at minimum: who operates the site, which tool is used and what it collects (page URL, referrer, country, device class), whether cookies are set, how long data is kept, and a contact address. Link it from the footer on every page (see `web-layout-footer`).
- Do not put personal data in event properties or URLs (`?email=...`); analytics providers store them and that becomes a data breach.

## Related skills

- `web-ui-modal-dialog`
- `web-perf-css-and-js-loading`
- `web-js-storage`
- `web-layout-footer`
- `web-ship-launch-checklist`
