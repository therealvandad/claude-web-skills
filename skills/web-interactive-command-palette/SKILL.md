---
name: web-interactive-command-palette
description: Build a Ctrl+K / Cmd+K command palette in a native dialog, with a combobox input, fuzzy-ranked listbox of pages and actions, recent items, full keyboard control and screen reader announcements, no library. Use whenever a user asks for a "command palette", "Ctrl+K search", "quick switcher", "jump to page", "spotlight search" or "keyboard shortcuts menu".
---

# Command palette

A palette is a modal combobox: an input that filters a list of commands (pages to visit, actions to run) while focus never leaves the input. Use the native `<dialog>` with `showModal()` for the focus trap, Escape to close, top-layer stacking and focus restoration, then add the ARIA 1.2 combobox pattern (`role="combobox"` input, `role="listbox"` list, `aria-activedescendant`) so arrow keys move a highlight without moving focus. Commands are plain data, so adding one is one line.

## Pattern

```html
<div data-widget="palette">
  <button data-palette-open type="button" class="flex items-center gap-3 rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-600 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:border-gray-700 dark:text-gray-400">
    Search or jump to… <kbd data-js="hint" class="rounded border border-gray-300 px-1.5 text-xs dark:border-gray-600">Ctrl K</kbd>
  </button>

  <dialog data-js="dialog" aria-label="Command palette"
    class="mx-auto mt-[12vh] mb-auto w-[min(36rem,calc(100%-2rem))] overflow-hidden rounded-xl border border-gray-200 bg-white p-0 text-gray-900 shadow-2xl backdrop:bg-gray-950/50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100">
    <input data-js="input" type="text" role="combobox" aria-expanded="true" aria-controls="palette-list" aria-autocomplete="list"
      aria-label="Type a command or page name" placeholder="Type a command or page name" autocomplete="off" spellcheck="false"
      class="w-full border-b border-gray-200 bg-transparent px-4 py-3 outline-none placeholder:text-gray-500 dark:border-gray-800">
    <ul id="palette-list" data-js="list" role="listbox" aria-label="Commands" class="max-h-72 overflow-y-auto p-2"></ul>
    <p data-js="count" role="status" class="sr-only"></p>
    <p class="border-t border-gray-200 px-4 py-2 text-xs text-gray-500 dark:border-gray-800">Up and down to choose, Enter to run, Esc to close</p>
  </dialog>
  <p data-js="live" role="status" class="sr-only"></p>   <!-- outside the dialog so it still speaks after it closes -->
</div>
```

```js
// /js/palette.js
const COMMANDS = [
  { id: 'home', title: 'Home', group: 'Go to', href: '/', keywords: 'start landing' },
  { id: 'pricing', title: 'Pricing', group: 'Go to', href: '/pricing', keywords: 'plans cost billing upgrade' },
  { id: 'docs', title: 'Documentation', group: 'Go to', href: '/docs', keywords: 'guide reference api help' },
  { id: 'changelog', title: 'Changelog', group: 'Go to', href: '/changelog', keywords: 'releases updates news' },
  { id: 'status', title: 'System status', group: 'Go to', href: '/status', keywords: 'uptime incident outage' },
  { id: 'theme', title: 'Toggle dark mode', group: 'Actions', run: 'theme', keywords: 'light appearance colour' },
  { id: 'copy', title: 'Copy link to this page', group: 'Actions', run: 'copy', keywords: 'share url clipboard' },
  { id: 'top', title: 'Scroll to top', group: 'Actions', run: 'top', keywords: 'beginning up' },
];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const ACTIONS = {
  theme: () => { document.documentElement.classList.toggle('dark'); return 'Dark mode toggled.'; },
  copy: async () => { await navigator.clipboard.writeText(location.href); return 'Page link copied.'; },
  top: () => { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); return 'Scrolled to top.'; },
};

function score(text, q) {                            // subsequence match; bonus for runs and word starts; 0 = no match
  text = text.toLowerCase();
  let at = -1, run = 0, total = 0;
  for (const ch of q) {
    const next = text.indexOf(ch, at + 1);
    if (next === -1) return 0;
    run = next === at + 1 ? run + 1 : 0;
    total += 1 + run * 2 + (next === 0 || text[next - 1] === ' ' ? 3 : 0);
    at = next;
  }
  return total;
}

export function initPalette(root) {
  const $ = (n) => root.querySelector(`[data-js="${n}"]`);
  const dialog = $('dialog'), input = $('input'), list = $('list');
  const ac = new AbortController(), { signal } = ac;
  const KEY = 'palette:recent:v1';
  let results = [], active = 0;
  const recent = () => { try { return JSON.parse(localStorage.getItem(KEY)) ?? []; } catch { return []; } };
  const remember = (id) => { try { localStorage.setItem(KEY, JSON.stringify([id, ...recent().filter((r) => r !== id)].slice(0, 5))); } catch { /* private mode */ } };

  function search(query) {
    const q = query.trim().toLowerCase();
    if (!q) {                                        // empty query: recent commands first, then everything else
      const ids = recent(), seen = COMMANDS.filter((c) => ids.includes(c.id)).sort((a, b) => ids.indexOf(a.id) - ids.indexOf(b.id));
      return [...seen.map((c) => ({ ...c, group: 'Recent' })), ...COMMANDS.filter((c) => !ids.includes(c.id))];
    }
    return COMMANDS.map((c) => ({ c, s: Math.max(score(c.title, q) * 2, score(`${c.title} ${c.keywords}`, q)) }))
      .filter((r) => r.s > 0).sort((a, b) => b.s - a.s).map((r) => r.c);
  }
  function render() {
    results = search(input.value); active = 0;
    list.replaceChildren(...results.map((c, i) => {
      const li = document.createElement('li');
      li.id = `palette-opt-${i}`; li.setAttribute('role', 'option');
      li.className = 'flex cursor-pointer items-center justify-between rounded-md px-3 py-2 text-sm aria-selected:bg-indigo-600 aria-selected:text-white';
      li.append(Object.assign(document.createElement('span'), { textContent: c.title }),
                Object.assign(document.createElement('span'), { textContent: c.group, className: 'text-xs opacity-60' }));
      li.addEventListener('mousemove', () => highlight(i));
      li.addEventListener('click', () => run(c));
      return li;
    }));
    highlight(0);
    $('count').textContent = results.length ? `${results.length} result${results.length === 1 ? '' : 's'}` : 'No matching commands';
  }
  function highlight(i) {
    if (!results.length) { input.removeAttribute('aria-activedescendant'); return; }
    list.children[active]?.setAttribute('aria-selected', 'false');
    active = (i + results.length) % results.length;
    const el = list.children[active];
    el.setAttribute('aria-selected', 'true'); el.scrollIntoView({ block: 'nearest' });
    input.setAttribute('aria-activedescendant', el.id);
  }
  async function run(cmd) {
    remember(cmd.id); dialog.close();                // closing first restores focus to the trigger
    if (cmd.href) { location.href = cmd.href; return; }
    $('live').textContent = await ACTIONS[cmd.run]();
  }
  function open() { if (dialog.open) return; input.value = ''; dialog.showModal(); render(); }

  input.addEventListener('input', render, { signal });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); highlight(active + 1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(active - 1); }
    else if (e.key === 'Enter' && results[active]) { e.preventDefault(); run(results[active]); }
  }, { signal });
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); }, { signal });   // backdrop click
  document.addEventListener('keydown', (e) => {
    const typing = e.target.closest?.('input, textarea, select, [contenteditable]');
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); dialog.open ? dialog.close() : open(); }
    else if (e.key === '/' && !typing && !dialog.open) { e.preventDefault(); open(); }
  }, { signal });
  root.querySelector('[data-palette-open]').addEventListener('click', open, { signal });
  if (/Mac|iPhone|iPad/.test(navigator.userAgent)) $('hint').textContent = '⌘ K';
  return () => ac.abort();
}

document.querySelectorAll('[data-widget="palette"]').forEach(initPalette);
```

## Variations

- **Commands from the site**: generate `COMMANDS` from your search index or navigation at build time and `fetch` it on first open; see `web-interactive-live-search`.
- **Nested commands**: when a command has `children`, replace the list with them, show a "Back" row and push a breadcrumb into the input placeholder. Backspace on an empty input goes up one level.
- **Shortcut hints**: add `shortcut: 'g d'` to commands and listen for two-key sequences outside inputs, with a 1 second reset timer.
- **Results from the page**: add a "Headings on this page" group built from `document.querySelectorAll('main h2, main h3')`, each with `run: 'scrollTo'`.

## Pitfalls

- Tailwind's Preflight zeroes every margin, which removes the dialog's native `margin: auto` centring; the `mx-auto mt-[12vh] mb-auto` classes put it back. Without them the palette sits in the top-left corner.
- Keep DOM focus on the input and move only `aria-activedescendant`. If you focus the options instead, typing stops filtering and screen readers lose the combobox context.
- Intercept Ctrl+K with `preventDefault()`, but do not hijack `/` while the user types in a field; the `typing` check above prevents that. Browsers use Ctrl+K for their own search bar, so do not rely on it as the only entry: always keep the visible button.
- Announce results in a `role="status"` region inside the dialog, and action outcomes in one outside it. A live region inside a closed dialog is not rendered, so "Page link copied." would never be spoken.
- Reset the query on every open; reopening with stale text and a stale highlight confuses people.
- Build rows with `textContent`, never `innerHTML`, once commands come from content you do not fully control.

## Related skills

- `web-interactive-live-search`
- `web-ui-modal-dialog`
- `web-form-select-and-combobox`
- `web-a11y-keyboard-and-focus`
- `web-a11y-aria-patterns`
- `web-js-storage`
