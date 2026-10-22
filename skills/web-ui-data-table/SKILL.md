---
name: web-ui-data-table
description: Build a responsive data table with Tailwind: sticky header, sortable columns with aria-sort, a live filter box, zebra rows, right-aligned numbers, horizontal scroll or stacked-card layout on mobile, all in vanilla JS. Use whenever a user asks for a table, data grid, list of records, sortable or filterable table, "table that works on mobile", or a results list.
---

# Data table

Real `<table>` markup is the only way screen readers can read a grid by row and column, and sorting a table client-side is thirty lines of JS. The design questions are: how the header stays visible while scrolling, how numbers align, and what happens at 375 px. The default answer for mobile is horizontal scroll inside a bounded container (data stays comparable); the stacked-card variant is for short tables where each row is a self-contained record.

## Pattern

```html
<section aria-labelledby="orders-title" class="mx-auto max-w-5xl px-4">
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <h2 id="orders-title" class="text-lg font-semibold">Orders</h2>
    <label class="relative block">
      <span class="sr-only">Filter orders</span>
      <input id="filter" type="search" placeholder="Filter…" autocomplete="off"
        class="w-full rounded-lg border border-gray-300 py-2 pl-3 pr-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 sm:w-64 dark:border-gray-700 dark:bg-gray-900">
    </label>
  </div>

  <div class="mt-4 max-h-[70vh] overflow-auto rounded-xl border border-gray-200 dark:border-gray-800">
    <table id="orders" class="w-full min-w-[40rem] border-collapse text-sm">
      <caption class="sr-only">Orders, sortable by column. <span id="count"></span></caption>
      <thead class="sticky top-0 z-10 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-600 dark:bg-gray-900 dark:text-gray-400">
        <tr>
          <th scope="col" aria-sort="none" class="px-4 py-3 font-semibold">
            <button type="button" data-sort="text" class="group inline-flex items-center gap-1 rounded focus-visible:outline-2 focus-visible:outline-indigo-600">
              Customer <span aria-hidden="true" class="text-gray-400 group-aria-[sort=ascending]:text-gray-900">↕</span>
            </button>
          </th>
          <th scope="col" aria-sort="none" class="px-4 py-3 font-semibold"><button type="button" data-sort="text" class="inline-flex items-center gap-1 rounded focus-visible:outline-2 focus-visible:outline-indigo-600">Status <span aria-hidden="true">↕</span></button></th>
          <th scope="col" aria-sort="none" class="px-4 py-3 text-right font-semibold"><button type="button" data-sort="number" class="inline-flex items-center gap-1 rounded focus-visible:outline-2 focus-visible:outline-indigo-600">Total <span aria-hidden="true">↕</span></button></th>
          <th scope="col" aria-sort="none" class="px-4 py-3 font-semibold"><button type="button" data-sort="date" class="inline-flex items-center gap-1 rounded focus-visible:outline-2 focus-visible:outline-indigo-600">Date <span aria-hidden="true">↕</span></button></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200 dark:divide-gray-800 [&>tr:nth-child(even)]:bg-gray-50/60 dark:[&>tr:nth-child(even)]:bg-gray-900/40">
        <tr class="hover:bg-indigo-50/50 dark:hover:bg-indigo-950/30">
          <th scope="row" class="px-4 py-3 font-medium">Ada Lovelace</th>
          <td class="px-4 py-3"><span class="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/40 dark:text-green-300">Paid</span></td>
          <td class="px-4 py-3 text-right tabular-nums" data-value="1240.5">$1,240.50</td>
          <td class="px-4 py-3 tabular-nums" data-value="2026-10-18"><time datetime="2026-10-18">18 Oct 2026</time></td>
        </tr>
        <tr class="hover:bg-indigo-50/50 dark:hover:bg-indigo-950/30">
          <th scope="row" class="px-4 py-3 font-medium">Grace Hopper</th>
          <td class="px-4 py-3"><span class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">Pending</span></td>
          <td class="px-4 py-3 text-right tabular-nums" data-value="310">$310.00</td>
          <td class="px-4 py-3 tabular-nums" data-value="2026-10-20"><time datetime="2026-10-20">20 Oct 2026</time></td>
        </tr>
      </tbody>
    </table>
  </div>
  <p id="empty" hidden class="mt-4 text-center text-sm text-gray-500">No orders match your filter.</p>
</section>
```

```js
function initTable(table, filterInput) {
  const tbody = table.tBodies[0];
  const rows = [...tbody.rows];
  const count = document.getElementById('count'), empty = document.getElementById('empty');

  const cellValue = (row, i, type) => {
    const cell = row.cells[i];
    const raw = cell.dataset.value ?? cell.textContent.trim();
    return type === 'number' ? parseFloat(raw) || 0 : type === 'date' ? Date.parse(raw) : raw.toLowerCase();
  };

  table.tHead.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-sort]'); if (!btn) return;
    const th = btn.closest('th'), i = th.cellIndex, type = btn.dataset.sort;
    const dir = th.getAttribute('aria-sort') === 'ascending' ? 'descending' : 'ascending';
    table.tHead.querySelectorAll('th').forEach((h) => h.setAttribute('aria-sort', 'none'));
    th.setAttribute('aria-sort', dir);
    const sorted = [...rows].sort((a, b) => {
      const va = cellValue(a, i, type), vb = cellValue(b, i, type);
      const cmp = typeof va === 'string' ? va.localeCompare(vb) : va - vb;
      return dir === 'ascending' ? cmp : -cmp;
    });
    tbody.append(...sorted); // moving nodes preserves event listeners
  });

  filterInput.addEventListener('input', () => {
    const q = filterInput.value.trim().toLowerCase();
    let visible = 0;
    rows.forEach((r) => { const show = !q || r.textContent.toLowerCase().includes(q); r.hidden = !show; visible += show; });
    count.textContent = `${visible} of ${rows.length} shown.`;
    empty.hidden = visible > 0;
  });
  count.textContent = `${rows.length} rows.`;
}
initTable(document.getElementById('orders'), document.getElementById('filter'));
```

Why this shape: `data-value` carries the machine-sortable value so formatted currency and dates sort correctly; `tabular-nums` keeps digits aligned in columns; `sticky top-0` on `<thead>` works because the scroll container is the wrapper `div`, not the page. `aria-sort` on the `<th>` (not the button) is what screen readers read, and the first-column `<th scope="row">` lets them announce the customer before each cell.

## Variations

- **Stacked cards on mobile** (short tables): on the `<table>` use `block md:table`, on `thead` `sr-only md:not-sr-only` (plus `md:table-header-group`), on rows `block md:table-row mb-4 rounded-lg border p-3`, on cells `flex justify-between md:table-cell before:content-[attr(data-label)] before:font-medium md:before:content-none`, and give each `<td data-label="Total">`.
- **Row selection**: add a first column of `<input type="checkbox" aria-label="Select Ada Lovelace">` with a header "select all" checkbox; style selected rows with `has-[:checked]:bg-indigo-50`.
- **Pagination**: slice `rows` into pages of 25 and render only that slice; see `web-nav-pagination`. For more than ~500 rows, sort and filter on the server.
- **Dense or comfortable**: switch `py-3` to `py-1.5` for data-heavy admin views; keep at least 44 px tall rows when rows are tappable.

## Pitfalls

- Never build a table out of `<div>`s with `role="grid"` for static data; you lose row/column navigation in screen readers and gain nothing.
- `sticky` headers fail silently if any ancestor between the `thead` and the scroll container has `overflow: hidden`, or if the table is not inside its own scrolling box.
- Sorting the text of formatted cells ("$1,240.50", "18 Oct") gives wrong order; always sort on `data-value` or a parsed value.
- `min-w-[40rem]` plus `overflow-auto` is what makes the mobile scroll work; without a min width the columns crush into unreadable slivers.
- Filtering with `r.hidden` leaves zebra stripes based on DOM position, so two adjacent visible rows can share a colour. `:nth-child` cannot skip hidden rows; if it matters, move hidden rows to the end (`tbody.append(...hiddenRows)`) or stripe with a class toggled in the filter loop.
- Put `<caption>` in every table; it is the accessible name. `sr-only` keeps it out of the visual layout when the heading is elsewhere.

## Related skills

- `web-nav-pagination`
- `web-ui-badges-chips-tags`
- `web-form-search-suggestions`
- `web-css-sticky-and-fixed`
- `web-js-state-and-render`
