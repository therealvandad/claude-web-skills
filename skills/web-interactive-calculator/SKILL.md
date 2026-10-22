---
name: web-interactive-calculator
description: 'Build a live pricing calculator, quote estimator or product configurator in vanilla JS: form inputs drive an itemised total, money formatted with Intl, the configuration encoded in the URL for sharing, and a print-friendly summary. Use whenever a user asks for a "pricing calculator", "cost estimator", "quote builder", "configurator", "ROI calculator", or "how much will it cost widget".'
---

# Pricing calculator with live total

A calculator is a pure function `price(config)` plus a form that edits `config`. Keep the pricing rules in one plain object, compute the breakdown from the form on every `input` event, format with `Intl.NumberFormat` (never string concatenation), and mirror the config into the URL so a sales rep can send "here is your quote" as a link. The same markup prints as a clean summary with a few `print:` utilities.

## Pattern

```html
<form data-widget="calculator" class="mx-auto grid max-w-4xl gap-8 p-4 md:grid-cols-[1fr_20rem]" aria-labelledby="calc-title">
  <div class="space-y-6 print:hidden">
    <h1 id="calc-title" class="text-2xl font-semibold">Estimate your hosting bill</h1>
    <div>
      <label for="seats" class="text-sm font-medium">Team members: <output name="seats-out" for="seats">5</output></label>
      <input id="seats" name="seats" type="range" min="1" max="200" value="5" class="mt-2 w-full accent-indigo-600">
    </div>
    <div>
      <label for="storage" class="text-sm font-medium">Storage (GB)</label>
      <input id="storage" name="storage" type="number" min="10" max="5000" step="10" value="100" inputmode="numeric"
        class="mt-1 w-32 rounded-lg border border-gray-300 px-3 py-1.5 dark:border-gray-700 dark:bg-gray-900">
    </div>
    <fieldset>
      <legend class="text-sm font-medium">Plan</legend>
      <div class="mt-2 flex flex-wrap gap-2">
        <label class="cursor-pointer rounded-lg border px-3 py-1.5 text-sm has-[:checked]:border-indigo-600 has-[:checked]:bg-indigo-50 dark:has-[:checked]:bg-indigo-950"><input type="radio" name="plan" value="starter" class="sr-only" checked> Starter</label>
        <label class="cursor-pointer rounded-lg border px-3 py-1.5 text-sm has-[:checked]:border-indigo-600 has-[:checked]:bg-indigo-50 dark:has-[:checked]:bg-indigo-950"><input type="radio" name="plan" value="business" class="sr-only"> Business</label>
      </div>
    </fieldset>
    <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="yearly" class="accent-indigo-600"> Pay yearly (2 months free)</label>
    <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="support" class="accent-indigo-600"> Priority support (+$99/month)</label>
  </div>

  <aside aria-live="polite" aria-atomic="true" class="h-fit rounded-2xl border border-gray-200 p-5 md:sticky md:top-4 print:border-0 dark:border-gray-800">
    <h2 class="text-sm font-medium uppercase tracking-wide text-gray-500">Your estimate</h2>
    <dl data-js="lines" class="mt-3 space-y-1 text-sm"></dl>
    <p class="mt-4 flex items-baseline justify-between border-t pt-3 dark:border-gray-800">
      <span class="font-medium">Total</span>
      <strong data-js="total" class="text-2xl tabular-nums">$0.00</strong>
    </p>
    <p data-js="period" class="text-xs text-gray-500"></p>
    <div class="mt-4 flex gap-2 print:hidden">
      <button type="button" data-js="share" class="flex-1 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white">Copy link</button>
      <button type="button" data-js="print" class="rounded-lg border px-3 py-2 text-sm dark:border-gray-700">Print</button>
    </div>
    <p data-js="toast" role="status" class="mt-2 min-h-4 text-xs text-green-700 dark:text-green-400"></p>
  </aside>
</form>
```

```js
// /js/calculator.js
const PRICES = { plans: { starter: 12, business: 29 }, storagePerGB: 0.08, includedGB: 50, support: 99, yearlyMonths: 10 };
const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

export function price(c) {                                 // pure: config -> { lines, total, period }
  const lines = [
    { label: `${c.seats} × ${c.plan} seat`, amount: c.seats * PRICES.plans[c.plan] },
    { label: `${Math.max(0, c.storage - PRICES.includedGB)} GB extra storage`, amount: Math.max(0, c.storage - PRICES.includedGB) * PRICES.storagePerGB },
  ];
  if (c.support) lines.push({ label: 'Priority support', amount: PRICES.support });
  const monthly = lines.reduce((s, l) => s + l.amount, 0);
  const total = c.yearly ? monthly * PRICES.yearlyMonths : monthly;
  return { lines, total, period: c.yearly ? `per year, billed once (saves ${money.format(monthly * 2)})` : 'per month' };
}

function readConfig(form) {
  const d = new FormData(form);
  return { seats: Number(d.get('seats')), storage: Math.max(10, Number(d.get('storage')) || 10), plan: d.get('plan'), yearly: d.has('yearly'), support: d.has('support') };
}
function applyUrlToForm(form) {                             // ?seats=40&storage=500&plan=business&yearly=1
  const p = new URLSearchParams(location.search);
  for (const [key, value] of p) {
    const el = form.elements[key];
    if (!el) continue;
    if (el instanceof RadioNodeList) el.value = value;
    else if (el.type === 'checkbox') el.checked = value === '1';
    else el.value = value;
  }
}
function configToUrl(c) {
  const p = new URLSearchParams({ seats: c.seats, storage: c.storage, plan: c.plan });
  if (c.yearly) p.set('yearly', '1');
  if (c.support) p.set('support', '1');
  return `${location.origin}${location.pathname}?${p}`;
}

export function initCalculator(form) {
  const lines = form.querySelector('[data-js="lines"]');
  const total = form.querySelector('[data-js="total"]');
  const period = form.querySelector('[data-js="period"]');
  const toast = form.querySelector('[data-js="toast"]');

  function render() {
    const config = readConfig(form);
    const quote = price(config);
    form.elements['seats-out'].value = config.seats;
    lines.replaceChildren(...quote.lines.map(({ label, amount }) => {
      const row = document.createElement('div');
      row.className = 'flex justify-between gap-4';
      row.innerHTML = `<dt class="text-gray-600 dark:text-gray-400"></dt><dd class="tabular-nums"></dd>`;
      row.children[0].textContent = label; row.children[1].textContent = money.format(amount);
      return row;
    }));
    total.textContent = money.format(quote.total);
    period.textContent = quote.period;
    history.replaceState(null, '', configToUrl(config));  // URL always mirrors the form
  }
  async function share() {
    try { await navigator.clipboard.writeText(location.href); toast.textContent = 'Link copied.'; }
    catch { toast.textContent = location.href; }         // clipboard blocked: show it to copy by hand
    setTimeout(() => { toast.textContent = ''; }, 3000);
  }

  form.addEventListener('input', render);
  form.addEventListener('submit', (e) => e.preventDefault());
  form.querySelector('[data-js="share"]').addEventListener('click', share);
  form.querySelector('[data-js="print"]').addEventListener('click', () => window.print());
  applyUrlToForm(form);
  render();
  return () => form.removeEventListener('input', render);
}

document.querySelectorAll('[data-widget="calculator"]').forEach(initCalculator);
```

Why this shape: `price()` is exported and has no DOM access, so the sales team's spreadsheet numbers can be checked against it in a unit test. The summary `<aside>` is `aria-live` with `aria-atomic`, so a screen reader hears the whole new total once per change instead of one fragment per line. `replaceState`, not `pushState`: a slider drag must not create fifty history entries.

## Variations

- **Currency and locale switch**: keep amounts in integer cents, pass `currency` to a fresh `Intl.NumberFormat` on change, and convert with a rates object; see `web-layout-pricing-table` for the plan cards that usually sit above a calculator.
- **Tiered pricing**: express tiers as `[{ upTo: 10, each: 12 }, { upTo: 50, each: 10 }, { upTo: Infinity, each: 8 }]` and compute per band in `price()`; show the band in the line label ("11-50 seats × $10").
- **Comparison against a competitor or "current spend"**: add a `currentSpend` number input and render a "You save $X / year" line, green when positive, hidden when zero.
- **Lead capture**: a "Email me this quote" button opens a `web-ui-modal-dialog` with a single email field and posts `configToUrl(config)` to your form endpoint.

## Pitfalls

- Floating point: `0.08 * 3` is `0.24000000000000002`. Format only at the edge with `Intl`, and if totals must match an invoice exactly, do the arithmetic in integer cents.
- Reading `input.value` gives strings; `'5' * 12` works by accident but `'5' + 12` is `'512'`. Convert once in `readConfig` and nowhere else.
- A `number` input can hold `''`, `-3` or `1e9`; clamp in `readConfig`, not just with `min`/`max` attributes, because the URL can inject anything.
- `navigator.clipboard` needs HTTPS and a user gesture, and is undefined inside some in-app browsers; always fall back to showing the URL.
- Use `tabular-nums` on every amount so the total does not jitter sideways as digits change.
- Do not put `aria-live` on the whole form; only the summary should announce, and only after the user stops typing (an `input` burst is fine because `polite` coalesces, but a `role="alert"` would interrupt).

## Related skills

- `web-layout-pricing-table`
- `web-js-state-and-render`
- `web-js-router-and-urls`
- `web-form-input-states`
- `web-ui-modal-dialog`
- `web-motion-counters-and-tickers`
