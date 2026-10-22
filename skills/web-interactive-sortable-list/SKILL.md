---
name: web-interactive-sortable-list
description: Build a reorderable list with drag handles, native drag and drop for the mouse, a Space-then-arrow-keys grab mode for the keyboard, live region announcements ("moved to position 2 of 5") and localStorage persistence, no library. Use whenever a user asks to "reorder items", "sortable list", "drag to rearrange", "priority list", "rank these" or "drag handle".
---

# Sortable list with keyboard reorder

Drag and drop is a mouse-only gesture, so the list needs a second way in. Put a real `<button>` handle on each row: pressing Space "grabs" the row, Arrow keys move it, Space or Enter drops it, Escape puts it back. Both input methods call one `move(id, toIndex)` that updates an array, saves it, repaints and announces the result. The array is the truth; the DOM is rebuilt from it, so order never drifts between what is shown, saved and spoken.

## Pattern

```html
<section data-widget="sortable" data-key="launch-checklist" class="mx-auto max-w-md p-4" aria-labelledby="sort-title">
  <h2 id="sort-title" class="text-lg font-semibold">Launch checklist, in order</h2>
  <p id="sort-help" class="mt-1 text-sm text-gray-600 dark:text-gray-400">Drag the handle, or press Space on it, then use the arrow keys. Space drops, Escape cancels.</p>
  <ol data-js="list" class="mt-4 space-y-2"></ol>
  <button data-js="reset" type="button" class="mt-4 text-sm underline focus-visible:outline-2 focus-visible:outline-indigo-600">Reset order</button>
  <p data-js="live" role="status" aria-live="assertive" class="sr-only"></p>
  <template data-js="row">
    <li class="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-3 shadow-sm has-[[aria-pressed=true]]:border-indigo-600 has-[[aria-pressed=true]]:ring-2 has-[[aria-pressed=true]]:ring-indigo-600/30 dark:border-gray-700 dark:bg-gray-800">
      <button data-js="handle" type="button" aria-pressed="false" aria-describedby="sort-help"
        class="cursor-grab touch-none rounded p-1 text-gray-500 hover:text-gray-900 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:hover:text-white">
        <svg aria-hidden="true" viewBox="0 0 16 16" class="size-5 fill-current"><path d="M5 3h2v2H5zm4 0h2v2H9zM5 7h2v2H5zm4 0h2v2H9zm-4 4h2v2H5zm4 0h2v2H9z"/></svg>
      </button>
      <span data-js="label" class="flex-1 text-sm"></span>
      <span data-js="pos" class="text-xs tabular-nums text-gray-500"></span>
    </li>
  </template>
</section>
```

```js
// /js/sortable.js
const SEED = [
  { id: 'a', label: 'Fix broken links on the pricing page' },
  { id: 'b', label: 'Compress hero image to under 150 KB' },
  { id: 'c', label: 'Add Open Graph tags to every template' },
  { id: 'd', label: 'Submit sitemap.xml to Search Console' },
  { id: 'e', label: 'Test checkout on a real phone' },
];

export function initSortable(root) {
  const $ = (n) => root.querySelector(`[data-js="${n}"]`);
  const list = $('list'), live = $('live'), tpl = $('row');
  const key = `sortable:${root.dataset.key}:v1`;
  const ac = new AbortController(), { signal } = ac;
  let items = restore(), grabbed = null, before = null, dragId = null, marker = null;

  function restore() {                               // saved ids first, unknown ids appended
    try {
      const ids = JSON.parse(localStorage.getItem(key));
      if (Array.isArray(ids)) return [...ids.map((i) => SEED.find((s) => s.id === i)).filter(Boolean), ...SEED.filter((s) => !ids.includes(s.id))];
    } catch { /* private mode or bad JSON: use the seed */ }
    return [...SEED];
  }
  const save = () => { try { localStorage.setItem(key, JSON.stringify(items.map((i) => i.id))); } catch { /* quota */ } };
  const say = (msg) => { live.textContent = ''; requestAnimationFrame(() => { live.textContent = msg; }); };

  function render(focusId) {
    list.replaceChildren(...items.map((item, i) => {
      const li = tpl.content.firstElementChild.cloneNode(true);
      li.dataset.id = item.id;
      li.querySelector('[data-js="label"]').textContent = item.label;
      li.querySelector('[data-js="pos"]').textContent = `${i + 1}/${items.length}`;
      const h = li.querySelector('[data-js="handle"]');
      h.setAttribute('aria-label', `Reorder: ${item.label}`);
      h.setAttribute('aria-pressed', String(item.id === grabbed));
      return li;
    }));
    if (focusId) list.querySelector(`[data-id="${focusId}"] [data-js="handle"]`)?.focus();
  }
  function move(id, to) {
    const from = items.findIndex((i) => i.id === id);
    to = Math.max(0, Math.min(items.length - 1, to));
    if (from === to) return;
    const [item] = items.splice(from, 1);
    items.splice(to, 0, item);
    save(); render(id);
    say(`${item.label} moved to position ${to + 1} of ${items.length}.`);
  }

  // keyboard: Space grabs, arrows move, Space/Enter drops, Escape cancels
  list.addEventListener('keydown', (e) => {
    const handle = e.target.closest('[data-js="handle"]');
    if (!handle) return;
    const id = handle.closest('li').dataset.id, at = items.findIndex((i) => i.id === id);
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      grabbed = grabbed === id ? null : id;
      before = grabbed ? items.map((i) => i.id) : null;
      handle.setAttribute('aria-pressed', String(grabbed === id));
      say(grabbed ? `Grabbed ${items[at].label}, position ${at + 1} of ${items.length}. Use arrow keys.` : `Dropped at position ${at + 1}.`);
    } else if (grabbed === id && ['ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key)) {
      e.preventDefault();
      move(id, { ArrowUp: at - 1, ArrowDown: at + 1, Home: 0, End: items.length - 1 }[e.key]);
    } else if (grabbed === id && e.key === 'Escape') {
      items = before.map((i) => items.find((x) => x.id === i)); grabbed = null;
      save(); render(id); say('Reorder cancelled.');
    }
  }, { signal });

  // mouse and pen: only the handle starts a drag, so text stays selectable
  list.addEventListener('pointerdown', (e) => { if (e.target.closest('[data-js="handle"]')) e.target.closest('li').draggable = true; }, { signal });
  list.addEventListener('dragstart', (e) => { dragId = e.target.closest('li').dataset.id; e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', dragId); e.target.classList.add('opacity-50'); }, { signal });
  list.addEventListener('dragover', (e) => {
    if (!dragId) return;
    e.preventDefault();
    marker?.classList.remove('ring-2', 'ring-indigo-500');
    marker = rows(e.clientY).next; marker?.classList.add('ring-2', 'ring-indigo-500');
  }, { signal });
  list.addEventListener('drop', (e) => { e.preventDefault(); move(dragId, rows(e.clientY).index); }, { signal });
  list.addEventListener('dragend', () => { dragId = null; marker = null; render(); }, { signal });
  function rows(y) {                                 // insertion index among the other rows
    const others = [...list.children].filter((li) => li.dataset.id !== dragId);
    const i = others.findIndex((li) => { const r = li.getBoundingClientRect(); return y < r.top + r.height / 2; });
    return { index: i === -1 ? others.length : i, next: others[i] };
  }
  $('reset').addEventListener('click', () => { items = [...SEED]; save(); render(); say('Order reset.'); }, { signal });

  render();
  return () => ac.abort();
}

document.querySelectorAll('[data-widget="sortable"]').forEach(initSortable);
```

## Variations

- **Items from the page**: replace `SEED` with `JSON.parse(root.querySelector('script[type="application/json"]').textContent)`, or read existing `<li>` elements for progressive enhancement.
- **Save to a server**: after `save()`, `fetch('/api/order', { method: 'PATCH', body: JSON.stringify(ids) })`; on failure restore the previous array and announce it. See `web-js-fetch-and-apis`.
- **Pointer-based drag for touch**: HTML5 drag does not fire on most phones. Add "Move up / Move down" buttons per row (call `move(id, at ± 1)`), or use `pointermove` with `setPointerCapture` and `touch-action: none` on the handle, which is already in the markup.
- **Ranked voting**: show `pos` as a large number and cap the list at 3 with the rest in an "unranked" second list; moving between lists needs only a `listId` on each item.

## Pitfalls

- Without `preventDefault()` in `dragover`, `drop` never fires. Do not re-render during `dragover`, or the dragged node is destroyed and the drag ends.
- Firefox will not start a drag unless `setData` is called in `dragstart`.
- Keep focus on the moved row's handle after every keyboard move (`render(id)` does this), or the next arrow press goes nowhere.
- The live region needs to change text to be read; clearing it first, then setting it next frame, makes identical consecutive messages announce again.
- Use `aria-pressed` on the handle for the grabbed state rather than the deprecated `aria-grabbed`. Do not add `role="listbox"` or drag-drop roles; a plain `<ol>` with buttons is the best-supported pattern.
- Mind the `has-[[aria-pressed=true]]` utility: it needs Tailwind v4; on older builds use a JS-toggled class.

## Related skills

- `web-interactive-kanban`
- `web-js-state-and-render`
- `web-js-storage`
- `web-a11y-keyboard-and-focus`
- `web-a11y-aria-patterns`
- `web-ui-data-table`
