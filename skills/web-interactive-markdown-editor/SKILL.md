---
name: web-interactive-markdown-editor
description: Build a split-pane Markdown editor with a live preview rendered by a 40-line safe parser (headings, emphasis, links, lists, code, quotes), debounced autosave to localStorage, word and reading-time count, Tab-to-indent and a mobile edit/preview toggle. Use whenever a user asks for a "markdown editor", "notes app", "live preview", "write and preview side by side", or "a textarea that renders markdown".
---

# Markdown editor with live preview

A notes or post editor needs three things that frameworks make look harder than they are: a `<textarea>` as the source of truth, a preview that is a pure function of its value, and autosave so nothing is lost. The parser below escapes HTML first and then applies a handful of regex rules, which covers what people actually type and cannot produce a script tag. Swap it for `marked` plus `DOMPurify` only when you need tables or nested lists.

## Pattern

```html
<section data-widget="md-editor" data-key="draft:release-notes" class="mx-auto flex h-dvh max-w-6xl flex-col p-4">
  <header class="flex flex-wrap items-center justify-between gap-2">
    <h1 class="text-lg font-semibold">Release notes 3.2</h1>
    <div class="flex items-center gap-3 text-sm text-gray-500">
      <span data-js="stats" aria-live="polite">0 words</span>
      <span data-js="saved" role="status"></span>
      <div class="flex rounded-lg border p-0.5 md:hidden" role="group" aria-label="View">
        <button type="button" data-view="write" aria-pressed="true" class="rounded-md px-3 py-1 aria-pressed:bg-gray-900 aria-pressed:text-white dark:aria-pressed:bg-gray-100 dark:aria-pressed:text-gray-900">Write</button>
        <button type="button" data-view="preview" aria-pressed="false" class="rounded-md px-3 py-1 aria-pressed:bg-gray-900 aria-pressed:text-white dark:aria-pressed:bg-gray-100 dark:aria-pressed:text-gray-900">Preview</button>
      </div>
    </div>
  </header>
  <div class="mt-3 grid min-h-0 flex-1 gap-4 md:grid-cols-2">
    <label class="sr-only" for="md-source">Markdown source</label>
    <textarea id="md-source" data-js="source" spellcheck="true" placeholder="# Heading&#10;&#10;Write **markdown** here."
      class="h-full w-full resize-none rounded-xl border border-gray-300 p-4 font-mono text-sm leading-relaxed focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-gray-700 dark:bg-gray-950"></textarea>
    <article data-js="preview" aria-label="Preview" aria-live="off" tabindex="0"
      class="prose prose-gray hidden max-w-none overflow-y-auto rounded-xl border border-gray-200 p-4 md:block dark:prose-invert dark:border-gray-800"></article>
  </div>
</section>
```

```js
// /js/markdown.js
const FENCE = '`'.repeat(3);                               // written this way so the snippet survives Markdown docs
const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const inline = (s) => s
  .replace(/`([^`]+)`/g, '<code>$1</code>')
  .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  .replace(/(^|\W)[*_](.+?)[*_](?=\W|$)/g, '$1<em>$2</em>')
  .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" rel="noopener noreferrer">$1</a>');   // http(s) only

export function renderMarkdown(src) {
  const blocks = escapeHtml(src.replace(/\r\n?/g, '\n')).split(/\n{2,}/);
  return blocks.map((block) => {
    if (block.startsWith(FENCE)) return `<pre><code>${block.split('\n').slice(1, block.endsWith(FENCE) ? -1 : undefined).join('\n')}</code></pre>`;
    const h = block.match(/^(#{1,6}) (.+)$/m);
    if (h && block.indexOf('\n') === -1) return `<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`;
    if (/^(?:[-*] .+\n?)+$/.test(block)) return `<ul>${block.split('\n').map((l) => `<li>${inline(l.slice(2))}</li>`).join('')}</ul>`;
    if (/^(?:\d+\. .+\n?)+$/.test(block)) return `<ol>${block.split('\n').map((l) => `<li>${inline(l.replace(/^\d+\. /, ''))}</li>`).join('')}</ol>`;
    if (/^&gt; /.test(block)) return `<blockquote><p>${inline(block.replace(/^&gt; ?/gm, ''))}</p></blockquote>`;
    if (/^(?:---|\*\*\*)$/.test(block)) return '<hr>';
    return `<p>${inline(block).replace(/\n/g, '<br>')}</p>`;
  }).join('\n');
}
```

```js
// /js/md-editor.js
import { renderMarkdown } from './markdown.js';
import { debounce } from './events.js';          // see web-js-events-debounce-throttle

const WPM = 220;

export function initEditor(root) {
  const key = root.dataset.key;
  const source = root.querySelector('[data-js="source"]');
  const preview = root.querySelector('[data-js="preview"]');
  const stats = root.querySelector('[data-js="stats"]');
  const saved = root.querySelector('[data-js="saved"]');

  function render() {
    preview.innerHTML = renderMarkdown(source.value);       // safe: input was escaped before any tag was added
    const words = source.value.trim().split(/\s+/).filter(Boolean).length;
    stats.textContent = `${words} word${words === 1 ? '' : 's'} · ${Math.max(1, Math.round(words / WPM))} min read`;
  }
  const save = debounce(() => {
    localStorage.setItem(key, source.value);
    saved.textContent = `Saved ${new Intl.DateTimeFormat(undefined, { timeStyle: 'short' }).format(new Date())}`;
  }, 800);
  function onKey(e) {                                       // Tab inserts two spaces instead of leaving the field
    if (e.key !== 'Tab' || e.shiftKey) return;
    e.preventDefault();
    source.setRangeText('  ', source.selectionStart, source.selectionEnd, 'end');
    source.dispatchEvent(new Event('input'));
  }
  function setView(view) {                                  // mobile: one pane at a time
    source.classList.toggle('hidden', view === 'preview');
    preview.classList.toggle('hidden', view === 'write');
    root.querySelectorAll('[data-view]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  }

  source.addEventListener('input', () => { render(); saved.textContent = 'Unsaved changes'; save(); });
  source.addEventListener('keydown', onKey);
  root.addEventListener('click', (e) => { const b = e.target.closest('[data-view]'); if (b) setView(b.dataset.view); });
  const mq = matchMedia('(min-width: 768px)');
  const onMq = () => { if (mq.matches) { source.classList.remove('hidden'); preview.classList.remove('hidden'); } else setView('write'); };
  mq.addEventListener('change', onMq);

  source.value = localStorage.getItem(key) ?? source.value;
  render(); onMq();
  return () => { mq.removeEventListener('change', onMq); source.removeEventListener('keydown', onKey); };
}

document.querySelectorAll('[data-widget="md-editor"]').forEach(initEditor);
```

Why this shape: the preview is `innerHTML` from a renderer whose first step is `escapeHtml`, so the only tags that can appear are the ones the renderer wrote, and links are restricted to `http(s)`. The `prose` classes come from `@plugin "@tailwindcss/typography";` in your CSS; without the plugin, style `[data-js="preview"] h1, p, ul` yourself in `@layer components`.

## Variations

- **Toolbar**: buttons for bold, italic, link and heading that wrap the selection with `setRangeText('**' + selected + '**')`; give each an `aria-label` and a `title` with the shortcut (Ctrl+B).
- **Synced scrolling**: on `scroll` of the textarea set `preview.scrollTop = preview.scrollHeight * (source.scrollTop / source.scrollHeight)`; throttle to a frame with `requestAnimationFrame`.
- **Multiple documents**: key drafts as `draft:<slug>` and list them from `Object.keys(localStorage)`; add Export (`Blob` download as `.md`) and Import (`<input type="file" accept=".md,.txt">` + `file.text()`).
- **Full Markdown**: load `marked@15.0.12` and `dompurify@3.2.6` from a pinned CDN URL, then `preview.innerHTML = DOMPurify.sanitize(marked.parse(src))`. Never skip the sanitizer.

## Pitfalls

- Escaping after parsing (or not at all) turns `<img onerror=alert(1)>` in a note into a stored XSS the moment someone else previews it. Escape first, parse second, and allow only `http(s)` link targets.
- A `<textarea>` inside a `grid` with `h-full` needs `min-h-0` on the grid (as above) or the page grows instead of the textarea scrolling.
- Autosaving on every keystroke thrashes `localStorage` and blocks the main thread on long documents; debounce, and still write on `visibilitychange` to `hidden` so switching tabs on a phone does not lose the last second of typing.
- The preview must not be `aria-live="polite"`: it would read the whole document on every keystroke. Keep the stats line live instead and let users Tab into the preview.
- `prose` does not style inside `dark:` without `dark:prose-invert`, and the typography plugin is opt-in in v4 (`@plugin`), not bundled.
- Trailing `\r\n` from pasted Windows text breaks block splitting; normalise line endings first, as the renderer does.

## Related skills

- `web-js-storage`
- `web-js-events-debounce-throttle`
- `web-js-dom-utilities`
- `web-form-file-upload`
- `web-page-blog-post`
- `web-css-layers-and-organization`
