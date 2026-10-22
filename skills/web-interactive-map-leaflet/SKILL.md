---
name: web-interactive-map-leaflet
description: Build an interactive map with Leaflet (pinned 1.9.4 from unpkg) showing markers loaded from JSON, popups, fit-to-bounds, and a list beside it that stays in sync with the map in both directions, keyboard accessible. Use whenever a user asks for a "map", "store locator", "show locations on a map", "Leaflet", "OpenStreetMap" or "pins with popups".
---

# Leaflet map with a synced list

A map alone is a poor interface: keyboard and screen reader users cannot scan it, and nobody can compare places on it. Pair every map with a list built from the same JSON, and make selection two-way: choosing a list item flies to its marker and opens the popup, opening a popup (by click or Enter on a marker) highlights the list item. Leaflet is the right size for this (about 40 KB gzipped), needs no API key, and OpenStreetMap tiles are free for modest traffic.

## Pattern

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<section data-widget="map" data-src="/data/roasters.json" class="mx-auto grid max-w-5xl gap-4 p-4 lg:grid-cols-[18rem_1fr]" aria-labelledby="map-title">
  <div>
    <h2 id="map-title" class="text-lg font-semibold">Coffee roasters in Lisbon</h2>
    <p data-js="count" aria-live="polite" class="mt-1 text-sm text-gray-600 dark:text-gray-400">Loading places…</p>
    <label class="mt-2 flex items-center gap-2 text-sm"><input data-js="inview" type="checkbox" class="size-4 accent-indigo-600"> Only list places in view</label>
    <button data-js="all" type="button" class="mt-2 rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus-visible:outline-2 focus-visible:outline-indigo-600 dark:border-gray-700">Show all on map</button>
    <ul data-js="list" class="mt-3 max-h-80 divide-y divide-gray-200 overflow-y-auto dark:divide-gray-800"></ul>
  </div>
  <div data-js="map" class="z-0 h-96 rounded-xl border border-gray-200 lg:h-[32rem] dark:border-gray-800"></div>
</section>
```

```json
[
  { "id": "alfama", "name": "Torrefação Alfama", "address": "Rua de São Miguel 41", "lat": 38.7129, "lng": -9.1301, "note": "Single-origin filter, open 08:00 to 18:00" },
  { "id": "baixa", "name": "Baixa Beans", "address": "Rua da Prata 112", "lat": 38.7110, "lng": -9.1390, "note": "Espresso bar, Saturday cuppings" },
  { "id": "principe", "name": "Príncipe Real Roasters", "address": "Rua Dom Pedro V 66", "lat": 38.7160, "lng": -9.1494, "note": "Roasts on site every Tuesday" },
  { "id": "lx", "name": "LX Roastery", "address": "Rua Rodrigues de Faria 103", "lat": 38.7033, "lng": -9.1786, "note": "Beans by the kilo, no seating" },
  { "id": "belem", "name": "Belém Café Lab", "address": "Rua de Belém 84", "lat": 38.6973, "lng": -9.2063, "note": "Pastry pairings, step-free entrance" }
]
```

```js
// /js/map.js  (a module runs after the classic Leaflet script above, so global L exists)
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

function popupNode(p) {                              // DOM nodes, never HTML strings built from data
  const box = document.createElement('div');
  const name = Object.assign(document.createElement('strong'), { textContent: p.name });
  const addr = Object.assign(document.createElement('p'), { textContent: `${p.address}. ${p.note}` });
  const link = Object.assign(document.createElement('a'), { textContent: 'Open in OpenStreetMap', target: '_blank', rel: 'noopener',
    href: `https://www.openstreetmap.org/?mlat=${p.lat}&mlon=${p.lng}#map=17/${p.lat}/${p.lng}` });
  box.append(name, addr, link);
  return box;
}

export async function initMap(root) {
  const $ = (n) => root.querySelector(`[data-js="${n}"]`);
  const ac = new AbortController(), { signal } = ac;
  let places;
  try { places = await (await fetch(root.dataset.src)).json(); }
  catch { $('count').textContent = 'The map data could not be loaded.'; return () => {}; }

  const map = L.map($('map'), { scrollWheelZoom: false }).setView([38.7139, -9.1394], 13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);

  const markers = new Map(), items = new Map();
  const bounds = L.latLngBounds(places.map((p) => [p.lat, p.lng]));
  const fitAll = () => { map.closePopup(); map.fitBounds(bounds, { padding: [32, 32], animate: !reduce }); };

  for (const p of places) {
    const marker = L.marker([p.lat, p.lng], { title: p.name, alt: p.name, keyboard: true }).addTo(map).bindPopup(popupNode(p));
    marker.on('popupopen', () => mark(p.id));        // fires for click, Enter and list selection alike
    markers.set(p.id, marker);

    const li = document.createElement('li');
    const btn = Object.assign(document.createElement('button'), { type: 'button',
      className: 'block w-full px-2 py-2.5 text-left text-sm hover:bg-gray-50 focus-visible:outline-2 focus-visible:outline-indigo-600 aria-[current=true]:bg-indigo-50 aria-[current=true]:font-medium dark:hover:bg-gray-800 dark:aria-[current=true]:bg-indigo-950' });
    btn.append(Object.assign(document.createElement('span'), { textContent: p.name, className: 'block' }),
               Object.assign(document.createElement('span'), { textContent: p.address, className: 'block text-xs text-gray-500' }));
    btn.addEventListener('click', () => select(p.id), { signal });
    li.append(btn); items.set(p.id, li);
  }
  $('list').append(...items.values());

  function select(id) {                              // list -> map
    const m = markers.get(id), at = m.getLatLng(), zoom = Math.max(map.getZoom(), 15);
    if (map.getZoom() === zoom && map.getCenter().equals(at, 1e-6)) return m.openPopup();   // no move, so no moveend
    map.once('moveend', () => m.openPopup());        // opening mid-flight would be dragged off screen
    map.flyTo(at, zoom, { animate: !reduce });
  }
  function mark(id) {                                // map -> list
    items.forEach((li, key) => key === id ? li.firstElementChild.setAttribute('aria-current', 'true') : li.firstElementChild.removeAttribute('aria-current'));
    items.get(id).scrollIntoView({ block: 'nearest' });
  }
  function refreshList() {
    const only = $('inview').checked;
    let shown = 0;
    for (const [id, li] of items) {
      const visible = !only || map.getBounds().contains(markers.get(id).getLatLng());
      li.hidden = !visible; shown += visible;
    }
    $('count').textContent = `${shown} of ${places.length} places${only ? ' in view' : ''}`;
  }

  map.on('moveend', refreshList);
  $('inview').addEventListener('change', refreshList, { signal });
  $('all').addEventListener('click', fitAll, { signal });
  fitAll(); refreshList();
  return () => { ac.abort(); map.remove(); };
}

document.querySelectorAll('[data-widget="map"]').forEach(initMap);
```

## Variations

- **Inline data**: swap `fetch` for `JSON.parse(document.querySelector('#places').textContent)` when the markers ship with the page, so there is no loading state.
- **Clusters or hundreds of pins**: use `L.layerGroup` with `canvas: true` (`L.map(el, { preferCanvas: true })`) and `L.circleMarker`; add the Leaflet.markercluster plugin only beyond about 300 points, pinned to an exact version.
- **Numbered or coloured pins**: `L.divIcon({ html: '<span class="...">3</span>', className: '' })` styled with Tailwind, no image files.
- **Dark mode tiles**: swap the tile URL on a `prefers-color-scheme` change, or apply `dark:[&_.leaflet-tile-pane]:invert` plus `hue-rotate-180` as a cheap approximation.

## Pitfalls

- The map `div` needs an explicit height (`h-96`). A zero-height container renders nothing and logs no error.
- Keep Leaflet's `z-index` contained (`z-0` on the container, which creates a stacking context), or its panes (z-index up to 1000) paint over your sticky header and modals.
- If the map starts inside a hidden tab or dialog, call `map.invalidateSize()` when it becomes visible, otherwise tiles load as a grey strip.
- Always keep the attribution and, past light traffic, use a tile provider with a plan; the OpenStreetMap tile server forbids heavy use. Do not strip the attribution control.
- Leave `scrollWheelZoom` off so the page can still scroll past the map; enable it on first click if wanted. Every marker is a tab stop, so with many pins keep the list as the quick way around the map; Leaflet already closes popups on Escape.
- Remove the map with `map.remove()` on cleanup; re-initialising on the same element throws "Map container is already initialized".
- Pass `integrity` and `crossorigin` on both tags so a compromised CDN file does not run on your page.

## Related skills

- `web-interactive-live-search`
- `web-data-fetch-and-cache`
- `web-js-fetch-and-apis`
- `web-a11y-keyboard-and-focus`
- `web-a11y-aria-patterns`
- `web-css-sticky-and-fixed`
