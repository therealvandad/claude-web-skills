---
name: web-data-table-export
description: 'Add export to a data table: download the visible, sorted, filtered rows as a CSV file (correct quoting, UTF-8 BOM for Excel), copy them to the clipboard as tab-separated text, and a print stylesheet, in vanilla JS and Tailwind v4. Use whenever a user asks for "export to CSV", "download as Excel", "copy table", "print this table", or "export button".'
---

# Table export: CSV, clipboard, print

Users do not want your table, they want the numbers in their spreadsheet. Three affordances cover almost every request: a CSV download, a copy-to-clipboard that pastes into Sheets or Excel as cells, and a print view that strips navigation and buttons. All three read the same source of truth, the rows currently visible in their current order, so what the user sees is what they get. Raw values come from `data-value` when present so "€1,240.50" exports as `1240.5`.

## Pattern

```html
<div class="flex flex-wrap items-center gap-2 print:hidden">
  <button type="button" data-export="csv" data-table="orders" data-filename="orders-2026-10.csv"
    class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:border-gray-700 dark:hover:bg-gray-900">
    Download CSV</button>
  <button type="button" data-export="copy" data-table="orders"
    class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:border-gray-700 dark:hover:bg-gray-900">
    Copy to clipboard</button>
  <button type="button" data-export="print"
    class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:border-gray-700 dark:hover:bg-gray-900">
    Print</button>
  <output role="status" id="export-status" class="text-sm text-gray-500"></output>
</div>

<table id="orders" class="mt-3 w-full text-sm">
  <caption class="sr-only">Orders, October 2026</caption>
  <thead><tr><th scope="col">Invoice</th><th scope="col">Customer</th><th scope="col" class="text-right">Total</th><th scope="col">Date</th></tr></thead>
  <tbody>
    <tr><th scope="row">INV-2041</th><td>Marta Kowalczyk</td><td class="text-right tabular-nums" data-value="1240.5">€1,240.50</td><td data-value="2026-10-18">18 Oct 2026</td></tr>
    <tr><th scope="row">INV-2042</th><td>Søren "Sam" Lindqvist</td><td class="text-right tabular-nums" data-value="310">€310.00</td><td data-value="2026-10-20">20 Oct 2026</td></tr>
  </tbody>
</table>
```

```js
// Rows as arrays of raw strings: header row + every visible body row, in DOM (= sorted) order.
function tableToRows(table) {
  const cells = (tr) => [...tr.cells].map((c) => (c.dataset.value ?? c.textContent).trim());
  const head = [...table.tHead.rows].map(cells);
  const body = [...table.tBodies[0].rows].filter((r) => !r.hidden && r.offsetParent !== null).map(cells);
  return [...head, ...body];
}

const csvField = (v) => (/[",\r\n]/.test(v) ? `"${v.replaceAll('"', '""')}"` : v);
const toCSV = (rows) => '﻿' + rows.map((r) => r.map(csvField).join(',')).join('\r\n');
const toTSV = (rows) => rows.map((r) => r.map((v) => v.replaceAll(/[\t\r\n]/g, ' ')).join('\t')).join('\n');

function download(text, filename, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

const status = document.getElementById('export-status');
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-export]'); if (!btn) return;
  const table = document.getElementById(btn.dataset.table);
  const kind = btn.dataset.export;
  if (kind === 'print') { window.print(); return; }
  const rows = tableToRows(table);
  if (kind === 'csv') {
    download(toCSV(rows), btn.dataset.filename ?? 'export.csv', 'text/csv;charset=utf-8');
    status.textContent = `Downloaded ${rows.length - 1} rows.`;
  } else if (kind === 'copy') {
    try {
      await navigator.clipboard.writeText(toTSV(rows));
      status.textContent = `Copied ${rows.length - 1} rows.`;
    } catch { status.textContent = 'Copy failed. Select the table and press Ctrl+C.'; }
  }
});
```

```css
@media print {
  @page { margin: 1.5cm; }
  nav, header, footer, aside, .print\:hidden { display: none !important; }
  table { width: 100%; border-collapse: collapse; font-size: 10pt; }
  thead { display: table-header-group; }       /* repeat header on every page */
  tr { break-inside: avoid; }
  th, td { border-bottom: 1px solid #999; padding: 4pt 6pt; color: #000; }
  caption { caption-side: top; text-align: left; font-weight: 600; }
}
```

Why this shape: the CSV quoting rule is the whole of RFC 4180 that matters, quote any field containing a comma, quote or newline and double the inner quotes, which is what makes `Søren "Sam" Lindqvist` survive. The leading BOM (`﻿`) is what makes Excel on Windows open UTF-8 as UTF-8 instead of showing `SÃ¸ren`. CRLF line endings are the spec and what Excel expects. Copy uses tabs, which every spreadsheet pastes as cells. `r.hidden` and `offsetParent` together catch rows hidden by a filter either way. The `<output role="status">` tells screen reader users something happened; a download is otherwise silent.

## Variations

- **Export everything, not just visible rows**: pass `{ all: true }` and skip the `.filter`; label the button "Download all 1,204 rows" so the difference is explicit.
- **Server-side export** for more than a few thousand rows: the button becomes `<a href="/orders.csv?filter=..." download>` built from the current filter state; the browser handles the file and the JS above is not needed.
- **Semicolon CSV** for locales where Excel expects it (de, fr, nl): add `sep=;` as the first line or write `;` as the delimiter and `,` as decimal mark; ask the user rather than sniffing `navigator.language`.
- **Print only the table**: wrap page content in `<main>` and add `body > *:not(main) { display: none }` in the print block; or open the table alone in a new window and print that.

## Pitfalls

- Exporting `textContent` of formatted cells gives spreadsheets text, not numbers; `data-value` holds the raw number and ISO date, which is what you want sorted and summed on the other side.
- `navigator.clipboard` requires a secure context (HTTPS or localhost) and a user gesture; the `try/catch` fallback message covers HTTP and denied permission.
- Fields starting with `=`, `+`, `-` or `@` execute as formulas in Excel (CSV injection). If any cell can contain user input, prefix such values with a single quote or a tab before quoting.
- A `<thead>` with two header rows (grouped columns) exports two header lines; merge them into one before export.
- `window.print()` from inside an iframe or an artifact sandbox is blocked; it must be a real page and a real click.
- Dark mode in print wastes toner and sometimes prints white text on white; the print block forces `color: #000` and relies on no backgrounds. Add `print:bg-white` to the `<body>` if your dark theme sets a background.

## Related skills

- `web-ui-data-table`
- `web-data-fetch-and-cache`
- `web-data-number-formatting`
- `web-ui-toast-notifications`
- `web-js-dom-utilities`
