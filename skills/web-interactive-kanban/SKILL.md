---
name: web-interactive-kanban
description: Build a kanban board (To do / Doing / Done columns) with native HTML drag and drop, a keyboard "move" menu for every card, live announcements, add-card forms and localStorage persistence, no library. Use whenever a user asks for a "kanban", "trello-like board", "drag cards between columns", "task board", "drag and drop list", or "project board on a static page".
---

# Kanban board with native drag and drop

The DOM must not be the source of truth for a board: a dropped card that is moved with `appendChild` but never recorded is lost on reload and invisible to keyboard users. Keep `{ columns: [{ id, title, cards: [...] }] }` in a store, let drag events and keyboard moves call one `moveCard(cardId, toColumn, index)` action, and re-render the columns from state. Native `dragstart`/`dragover`/`drop` is enough for mouse and pen; a per-card "Move" button that pops a column list is what makes the board usable from a keyboard and on touch screens, where HTML5 drag does not fire.

## Pattern

```html
<section data-widget="kanban" aria-labelledby="board-title" class="p-4">
  <h1 id="board-title" class="text-xl font-semibold">Website relaunch</h1>
  <p data-js="announce" class="sr-only" aria-live="assertive"></p>
  <div data-js="columns" class="mt-4 grid gap-4 md:grid-cols-3"></div>

<template data-js="column-tpl">
  <section class="flex flex-col rounded-xl bg-gray-100 p-3 dark:bg-gray-900" data-column>
    <h2 class="flex items-center justify-between text-sm font-semibold"><span data-js="title"></span><span data-js="count" class="rounded-full bg-white px-2 text-xs dark:bg-gray-800"></span></h2>
    <ul data-js="cards" class="mt-3 min-h-16 flex-1 space-y-2" aria-labelledby=""></ul>
    <form data-js="add" class="mt-3 flex gap-2">
      <input name="title" required placeholder="Add a card" aria-label="New card title" class="min-w-0 flex-1 rounded-md border border-gray-300 px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950">
      <button class="rounded-md bg-gray-900 px-2 text-sm text-white dark:bg-gray-200 dark:text-gray-900">Add</button>
    </form>
  </section>
</template>
<template data-js="card-tpl">
  <li draggable="true" data-card class="group cursor-grab rounded-lg border border-gray-200 bg-white p-3 text-sm shadow-sm active:cursor-grabbing aria-grabbed:opacity-50 dark:border-gray-700 dark:bg-gray-800">
    <p data-js="title"></p>
    <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
      <span data-js="meta"></span>
      <select data-js="move" aria-label="Move card to column" class="rounded border border-gray-300 bg-transparent px-1 py-0.5 dark:border-gray-700">
        <option value="">Move to…</option>
      </select>
    </div>
  </li>
</template>
</section>
```

```js
// /js/kanban.js
import { createStore } from './store.js';     // see web-js-state-and-render

const KEY = 'kanban:v1';
const seed = { columns: [
  { id: 'todo', title: 'To do', cards: [{ id: 'c1', title: 'Write pricing page copy', owner: 'Priya' }, { id: 'c2', title: 'Compress hero images', owner: 'Tomás' }] },
  { id: 'doing', title: 'Doing', cards: [{ id: 'c3', title: 'Migrate blog to new layout', owner: 'Priya' }] },
  { id: 'done', title: 'Done', cards: [{ id: 'c4', title: 'Set up Plausible analytics', owner: 'Ana' }] },
] };

export function initKanban(root) {
  const store = createStore(JSON.parse(localStorage.getItem(KEY) ?? 'null') ?? seed);
  const host = root.querySelector('[data-js="columns"]');
  const announce = root.querySelector('[data-js="announce"]');
  const colTpl = root.querySelector('[data-js="column-tpl"]');
  const cardTpl = root.querySelector('[data-js="card-tpl"]');
  let dragging = null;                        // card id during a drag

  // --- actions ---
  const findCard = (s, id) => s.columns.flatMap((c) => c.cards).find((c) => c.id === id);
  const moveCard = (id, toId, index) => store.set((s) => {
    const card = findCard(s, id);
    const columns = s.columns.map((c) => ({ ...c, cards: c.cards.filter((x) => x.id !== id) }));
    const to = columns.find((c) => c.id === toId);
    to.cards.splice(index ?? to.cards.length, 0, card);
    announce.textContent = `${card.title} moved to ${to.title}, position ${(index ?? to.cards.length - 1) + 1} of ${to.cards.length}.`;
    return { columns };
  });
  const addCard = (colId, title) => store.set((s) => ({ columns: s.columns.map((c) =>
    c.id === colId ? { ...c, cards: [...c.cards, { id: crypto.randomUUID(), title, owner: 'You' }] } : c) }));

  // --- render ---
  function render(state) {
    host.replaceChildren(...state.columns.map((col) => renderColumn(col, state.columns)));
  }
  function renderColumn(col, all) {
    const el = colTpl.content.firstElementChild.cloneNode(true);
    el.dataset.column = col.id;
    el.querySelector('[data-js="title"]').textContent = col.title;
    el.querySelector('[data-js="title"]').id = `col-${col.id}`;
    el.querySelector('[data-js="count"]').textContent = col.cards.length;
    const list = el.querySelector('[data-js="cards"]');
    list.setAttribute('aria-labelledby', `col-${col.id}`);
    list.append(...col.cards.map((card) => renderCard(card, col, all)));
    el.querySelector('[data-js="add"]').addEventListener('submit', (e) => {
      e.preventDefault(); const f = new FormData(e.target); addCard(col.id, f.get('title').trim()); e.target.reset();
    });
    list.addEventListener('dragover', (e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; list.classList.add('ring-2', 'ring-indigo-400'); });
    list.addEventListener('dragleave', () => list.classList.remove('ring-2', 'ring-indigo-400'));
    list.addEventListener('drop', (e) => {
      e.preventDefault();
      const after = [...list.children].findIndex((li) => e.clientY < li.getBoundingClientRect().top + li.offsetHeight / 2);
      moveCard(dragging, col.id, after === -1 ? undefined : after);
    });
    return el;
  }
  function renderCard(card, col, all) {
    const li = cardTpl.content.firstElementChild.cloneNode(true);
    li.dataset.card = card.id;
    li.querySelector('[data-js="title"]').textContent = card.title;
    li.querySelector('[data-js="meta"]').textContent = card.owner;
    const move = li.querySelector('[data-js="move"]');
    for (const c of all) if (c.id !== col.id) move.add(new Option(c.title, c.id));
    move.addEventListener('change', () => { if (move.value) { moveCard(card.id, move.value); focusCard(card.id); } });
    li.addEventListener('dragstart', (e) => { dragging = card.id; e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', card.id); li.setAttribute('aria-grabbed', 'true'); });
    li.addEventListener('dragend', () => { dragging = null; li.removeAttribute('aria-grabbed'); });
    return li;
  }
  function focusCard(id) { requestAnimationFrame(() => host.querySelector(`[data-card="${id}"] select`)?.focus()); }

  const unsubscribe = store.subscribe((s) => { render(s); localStorage.setItem(KEY, JSON.stringify(s)); });
  return unsubscribe;
}

document.querySelectorAll('[data-widget="kanban"]').forEach(initKanban);
```

Why this shape: drag handlers only compute *where* and call `moveCard`; the render repaints every column, so the count badges, empty states and the move menus are always right. The `<select>` for moving is a native, focusable control that works on phones and with screen readers without any custom ARIA.

## Variations

- **Reorder within a column from the keyboard**: add "Move up / Move down" to the select (or Alt+Arrow keys on the card), calling `moveCard(id, sameColumn, index ± 1)`; see `web-interactive-sortable-list` for the full keyboard reorder pattern.
- **Touch drag**: HTML5 drag events do not fire on most mobile browsers. Either rely on the move menu (recommended) or implement `pointerdown` + `pointermove` with `setPointerCapture` and `touch-action: none` on the handle.
- **Card details**: clicking the title opens a `web-ui-modal-dialog` with description, due date and a delete button; store the extra fields on the card object.
- **WIP limits**: `{ id: 'doing', limit: 3 }`; in `drop` and the move handler, refuse and announce "Doing is full (3 of 3)" instead of moving.

## Pitfalls

- Without `e.preventDefault()` in `dragover`, `drop` never fires. This is the single most common "drag and drop does nothing" bug.
- Re-rendering on `dragover` destroys the element being dragged and ends the drag; only change classes during a drag and re-render on `drop`.
- `setData('text/plain', …)` is required for Firefox to start a drag at all; keep it even though you read the id from the closure.
- `aria-grabbed` is deprecated but still the only hook for the `aria-grabbed:` opacity utility; the real accessibility comes from the move menu and the live region, not from the attribute.
- Persist on every state change, not on `beforeunload` (unreliable on mobile), and version the key (`kanban:v1`) so a later shape change can migrate; see `web-js-storage`.
- `crypto.randomUUID()` needs a secure context (HTTPS or localhost); fall back to `Date.now().toString(36)` if the board must work from `file://`.

## Related skills

- `web-js-state-and-render`
- `web-js-storage`
- `web-interactive-sortable-list`
- `web-a11y-keyboard-and-focus`
- `web-a11y-aria-patterns`
- `web-ui-modal-dialog`
