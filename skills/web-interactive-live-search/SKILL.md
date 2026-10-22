---
name: web-interactive-live-search
description: Build a client-side search page over a static JSON index (docs, blog, products) with fuzzy matching, scored ranking, highlighted matches, debounced input, arrow-key navigation and a live result count, no library. Use whenever a user asks for "search my site", "search the docs", "filter as you type", "fuzzy search", or "search without a backend".
---

# Live search over a JSON index

A static site has no search server, but it can ship a small JSON index (title, excerpt, URL per page) and search it in the browser. Up to a few thousand entries, a hand-written scorer beats loading a search library: tokenise the query, score each entry by prefix and substring hits, rank, and render the top results with the matched text marked. The form still submits to `/search?q=` without JS, so the page degrades to whatever the host offers.

## Pattern

```html
<section data-widget="live-search" data-index="/search-index.json" class="mx-auto max-w-2xl p-4">
  <form role="search" action="/search" class="relative">
    <label for="q" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Search the handbook</label>
    <input id="q" name="q" type="search" autocomplete="off" spellcheck="false" placeholder="e.g. expense policy, parental leave"
      aria-controls="results" aria-describedby="result-count"
      class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 dark:border-gray-700 dark:bg-gray-900">
  </form>
  <p id="result-count" data-js="count" aria-live="polite" class="mt-2 text-sm text-gray-500">Type to search 212 pages.</p>
  <ol id="results" data-js="results" class="mt-3 divide-y divide-gray-200 dark:divide-gray-800"></ol>
</section>
```

```json
[
  { "title": "Expense policy", "url": "/handbook/expenses", "excerpt": "Claim meals up to €35 per day and hotels up to €160 per night." },
  { "title": "Parental leave", "url": "/handbook/parental-leave", "excerpt": "Twenty weeks fully paid for every parent, in blocks of at least two weeks." }
]
```

```js
// /js/live-search.js
import { debounce } from './events.js';   // see web-js-events-debounce-throttle

const normalise = (s) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
const tokens = (s) => normalise(s).split(/\s+/).filter(Boolean);

function score(entry, words) {               // higher is better, 0 means no match
  const title = normalise(entry.title), body = normalise(entry.excerpt);
  let total = 0;
  for (const w of words) {
    if (title.startsWith(w)) total += 10;
    else if (title.includes(w)) total += 6;
    else if (body.includes(w)) total += 2;
    else if (fuzzy(title, w)) total += 1;    // letters in order: "exp pol" finds "expense policy"
    else return 0;                           // every word must hit somewhere
  }
  return total;
}
function fuzzy(text, word) {
  let i = 0;
  for (const ch of text) if (ch === word[i] && ++i === word.length) return true;
  return false;
}
function mark(text, words) {                 // returns a DocumentFragment, never innerHTML with user text
  const frag = document.createDocumentFragment();
  const re = new RegExp(`(${words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'ig');
  for (const part of text.split(re)) {
    if (!part) continue;
    if (re.test(part)) { const m = document.createElement('mark'); m.className = 'rounded bg-yellow-200 dark:bg-yellow-700/60'; m.textContent = part; frag.append(m); }
    else frag.append(part);
    re.lastIndex = 0;
  }
  return frag;
}

export async function initLiveSearch(root) {
  const input = root.querySelector('input[type="search"]');
  const list = root.querySelector('[data-js="results"]');
  const count = root.querySelector('[data-js="count"]');
  const index = await fetch(root.dataset.index).then((r) => r.json());
  let active = -1;

  function search(query) {
    const words = tokens(query);
    if (words.length === 0) { list.replaceChildren(); count.textContent = `Type to search ${index.length} pages.`; return; }
    const hits = index.map((e) => ({ e, s: score(e, words) })).filter((h) => h.s > 0)
      .sort((a, b) => b.s - a.s).slice(0, 20);
    list.replaceChildren(...hits.map(({ e }, i) => renderHit(e, words, i)));
    active = -1;
    count.textContent = hits.length ? `${hits.length} result${hits.length === 1 ? '' : 's'} for “${query}”` : `No results for “${query}”`;
  }
  function renderHit(entry, words, i) {
    const li = document.createElement('li');
    li.innerHTML = `<a id="hit-${i}" class="block rounded-md px-3 py-3 hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 aria-[selected=true]:bg-indigo-50 dark:hover:bg-gray-800 dark:aria-[selected=true]:bg-indigo-950">
      <span class="block font-medium"></span><span class="mt-0.5 block text-sm text-gray-600 dark:text-gray-400"></span></a>`;
    const a = li.firstElementChild; a.href = entry.url;
    a.children[0].append(mark(entry.title, words));
    a.children[1].append(mark(entry.excerpt, words));
    return li;
  }
  function move(delta) {                      // arrow keys walk the list while focus stays in the input
    const links = [...list.querySelectorAll('a')];
    if (links.length === 0) return;
    links[active]?.removeAttribute('aria-selected');
    active = (active + delta + links.length) % links.length;
    links[active].setAttribute('aria-selected', 'true');
    links[active].scrollIntoView({ block: 'nearest' });
    input.setAttribute('aria-activedescendant', links[active].id);
  }

  const onInput = debounce(() => search(input.value), 120);
  const onKey = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
    else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); list.querySelectorAll('a')[active].click(); }
    else if (e.key === 'Escape') { input.value = ''; search(''); }
  };
  input.addEventListener('input', onInput);
  input.addEventListener('keydown', onKey);
  const params = new URLSearchParams(location.search);
  if (params.get('q')) { input.value = params.get('q'); search(input.value); }
  return () => { input.removeEventListener('input', onInput); input.removeEventListener('keydown', onKey); };
}

document.querySelectorAll('[data-widget="live-search"]').forEach(initLiveSearch);
```

Why this shape: the whole index is fetched once, so every keystroke is a pure in-memory scan; a 2,000-entry index scores in well under a millisecond. `aria-activedescendant` lets arrow keys highlight results without moving focus out of the input, and the `aria-live` count tells screen reader users what happened after each debounce.

## Variations

- **Build the index** in your static build step: walk `dist/**/*.html`, pull `<title>`, the first `<p>`, and the URL into `search-index.json`. Keep excerpts under 200 characters; the index for 500 pages is about 60 KB, gzip to 15 KB.
- **Field weights and tags**: add `tags: ["hr", "money"]` to each entry and give tag hits `+8`; expose a chip row above the results that pre-fills the query with the tag.
- **Sync the URL**: call `history.replaceState(null, '', '?q=' + encodeURIComponent(query))` inside `search()` so results are shareable and survive reload; see `web-js-router-and-urls`.
- **Larger indexes** (10k+ entries): precompute `normalise(title)` once at load, and run the scan in `requestIdleCallback` chunks, or move it to a Web Worker and post results back.

## Pitfalls

- Highlighting with `innerHTML = text.replace(re, '<mark>$1</mark>')` is an XSS hole as soon as an excerpt contains `<`. Build the marks with `textContent` as above.
- Escape regex metacharacters in the query; a user typing `c++` or `(` must not throw a `SyntaxError` and kill the handler.
- Normalise accents on both sides (`NFD` + strip combining marks) or "resume" never finds "résumé".
- A fuzzy pass alone ranks "prl" over an exact "parental" prefix; order the checks prefix, substring, body, fuzzy, and require every word to match so results stay predictable.
- Do not re-announce on every keystroke; the debounce plus a single `aria-live="polite"` element keeps screen readers from reading twenty partial counts.
- Keep `type="search"` and a real `<form action>`: Enter with nothing selected submits normally, and users get the native clear button.

## Related skills

- `web-form-search-suggestions`
- `web-js-events-debounce-throttle`
- `web-js-router-and-urls`
- `web-data-fetch-and-cache`
- `web-a11y-keyboard-and-focus`
- `web-interactive-command-palette`
