---
name: web-form-select-and-combobox
description: Style a native <select> with Tailwind (custom chevron, consistent height, dark mode) and build an accessible custom combobox with type-to-filter, arrow-key navigation, aria-activedescendant and a hidden input for the chosen value. Use whenever a user asks for a "dropdown", "select box", "searchable select", "autocomplete select", "country picker", or complains the default select looks wrong.
---

# Select and combobox

Reach for the native `<select>` first: it is keyboard-complete, works on every phone with the OS picker, and only needs its chevron and border restyled. Build a custom combobox only when the list is long enough to need filtering (countries, products, users). The custom version follows the WAI-ARIA combobox pattern: an `<input role="combobox">` controls a `<ul role="listbox">`, focus never leaves the input, and the highlighted option is announced through `aria-activedescendant`. The selected value is mirrored into a hidden input so the form posts a real id, not display text.

## Pattern

```html
<!-- 1. Native select: restyled, still native -->
<div class="space-y-1.5">
  <label for="plan" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Plan</label>
  <select id="plan" name="plan"
    class="block w-full appearance-none rounded-md border border-gray-300 bg-white py-2 pr-10 pl-3 text-base text-gray-900 shadow-sm
           bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 fill=%22none%22 viewBox=%220 0 20 20%22><path stroke=%22%236b7280%22 stroke-linecap=%22round%22 stroke-width=%221.5%22 d=%22m6 8 4 4 4-4%22/></svg>')]
           bg-[length:1.25rem] bg-[position:right_0.75rem_center] bg-no-repeat
           focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
           disabled:bg-gray-50 disabled:text-gray-500 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100">
    <option value="" disabled selected>Choose a plan</option>
    <option value="free">Free</option>
    <option value="pro">Pro</option>
    <option value="team">Team</option>
  </select>
</div>

<!-- 2. Custom combobox with filtering -->
<div class="relative space-y-1.5" data-combobox>
  <label for="country" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Country</label>
  <input id="country" type="text" role="combobox" autocomplete="off" aria-autocomplete="list"
    aria-expanded="false" aria-controls="country-list" aria-haspopup="listbox" placeholder="Start typing…"
    class="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 shadow-sm
           focus-visible:border-blue-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
           dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100">
  <input type="hidden" name="country" data-value>
  <ul id="country-list" role="listbox" aria-label="Countries" hidden
    class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md border border-gray-200 bg-white py-1 text-base shadow-lg
           dark:border-gray-700 dark:bg-gray-900">
    <li role="option" id="country-de" data-value="DE" class="cursor-default px-3 py-2 aria-selected:bg-blue-600 aria-selected:text-white">Germany</li>
    <li role="option" id="country-fr" data-value="FR" class="cursor-default px-3 py-2 aria-selected:bg-blue-600 aria-selected:text-white">France</li>
    <li role="option" id="country-jp" data-value="JP" class="cursor-default px-3 py-2 aria-selected:bg-blue-600 aria-selected:text-white">Japan</li>
    <!-- more options -->
  </ul>
  <p class="sr-only" aria-live="polite" data-count></p>
</div>
```

```js
function initCombobox(root) {
  const input = root.querySelector('[role=combobox]');
  const list = root.querySelector('[role=listbox]');
  const hidden = root.querySelector('[data-value]');
  const count = root.querySelector('[data-count]');
  const options = [...list.querySelectorAll('[role=option]')];
  let active = -1;

  const visible = () => options.filter((o) => !o.hidden);

  function open(isOpen) {
    list.hidden = !isOpen;
    input.setAttribute('aria-expanded', String(isOpen));
    if (!isOpen) highlight(-1);
  }
  function highlight(i) {
    options.forEach((o) => o.removeAttribute('aria-selected'));
    active = i;
    const opt = visible()[i];
    if (opt) { opt.setAttribute('aria-selected', 'true'); opt.scrollIntoView({ block: 'nearest' }); }
    input.setAttribute('aria-activedescendant', opt ? opt.id : '');
  }
  function filter() {
    const q = input.value.trim().toLowerCase();
    options.forEach((o) => { o.hidden = q !== '' && !o.textContent.toLowerCase().includes(q); });
    const n = visible().length;
    count.textContent = `${n} ${n === 1 ? 'result' : 'results'} available`;
    hidden.value = '';                                   // typing invalidates the previous choice
    open(n > 0);
    highlight(-1);
  }
  function choose(opt) {
    input.value = opt.textContent;
    hidden.value = opt.dataset.value;
    open(false);
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  input.addEventListener('input', filter);
  input.addEventListener('focus', () => { if (input.value === '') { options.forEach((o) => (o.hidden = false)); open(true); } });
  input.addEventListener('keydown', (e) => {
    const n = visible().length;
    if (e.key === 'ArrowDown') { e.preventDefault(); if (list.hidden) open(true); highlight((active + 1) % n); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); highlight((active - 1 + n) % n); }
    else if (e.key === 'Home' && !list.hidden) { e.preventDefault(); highlight(0); }
    else if (e.key === 'End' && !list.hidden) { e.preventDefault(); highlight(n - 1); }
    else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); choose(visible()[active]); }
    else if (e.key === 'Escape') { open(false); if (list.hidden) input.value = ''; }
    else if (e.key === 'Tab') open(false);
  });
  list.addEventListener('mousedown', (e) => e.preventDefault());        // keep focus in the input
  list.addEventListener('click', (e) => { const opt = e.target.closest('[role=option]'); if (opt) choose(opt); });
  document.addEventListener('click', (e) => { if (!root.contains(e.target)) open(false); });
}

document.querySelectorAll('[data-combobox]').forEach(initCombobox);
```

Why these choices: `appearance-none` strips the OS chevron so one SVG data-URI background gives every browser the same arrow; `pr-10` leaves room for it. In the combobox, `aria-activedescendant` lets the input keep DOM focus (so typing never stops) while screen readers follow the highlighted option. `mousedown` + `preventDefault` on the list stops the input from blurring before `click` fires. The `sr-only` live region announces result counts, which is the only way a screen-reader user knows filtering happened. The hidden input is cleared on every keystroke so a half-edited label cannot submit a stale id.

## Variations

- **Multiple selection**: keep chosen items as removable chips above the input (see `web-ui-badges-chips-tags`), add `aria-multiselectable="true"` to the listbox, and append one `<input type="hidden" name="tags[]">` per chip.
- **Remote data**: replace the static `<li>`s with a debounced `fetch` on `input` (see `web-form-search-suggestions`), render options with `document.createElement`, and show a "Searching…" option with `aria-disabled="true"` while loading.
- **Grouped options**: in the native select use `<optgroup label="Europe">`; in the custom list wrap options in `<li role="group" aria-labelledby="grp-eu">` with a non-selectable heading `<div id="grp-eu" class="px-3 py-1 text-xs font-semibold uppercase text-gray-500">`.
- **Allow free text**: skip the hidden input, submit the combobox value itself, and let unmatched entries through; announce "No matches, press Enter to use your text".

## Pitfalls

- A `<div>` that looks like a select but has no `role`, no keyboard handling and no hidden input is the most common accessibility failure in forms. Either keep the native element or implement the full pattern above.
- The first `<option>` of a required native select must be `value=""` or `required` never fails; `disabled selected` on it keeps the placeholder from being chosen.
- Native `<select>` text cannot be restyled on iOS (the picker is OS-owned); do not promise pixel-identical options.
- `max-h-60 overflow-auto` on the list needs `scrollIntoView({ block: 'nearest' })` on highlight, or arrow keys move the highlight out of view.
- Position the list with `absolute` inside a `relative` wrapper, not `fixed`; inside a scrolling panel add `z-10` and check the parent does not have `overflow-hidden` clipping it.
- Do not open the list on page load or on every focus of a filled field; it covers the next field and confuses tab order.

## Related skills

- `web-form-layout`
- `web-form-search-suggestions`
- `web-form-choices`
- `web-nav-dropdown-menu`
- `web-ui-badges-chips-tags`
- `web-a11y-aria-patterns`
