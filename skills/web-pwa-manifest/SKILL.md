---
name: web-pwa-manifest
description: Write a complete `manifest.webmanifest` (name, id, start_url, scope, display, theme and background colour, any + maskable icons, screenshots, shortcuts) with the head tags iOS still needs and a checklist of the install criteria. Use when a user says "make it installable", "add to home screen", "PWA", "app icon on the phone", "standalone app" or "manifest".
---

# Web app manifest

The manifest is the contract that turns a site into an installable app: it tells the browser what to call it, which icon to put on the home screen, which URL to open and whether to hide the browser chrome. Chromium reads nearly every field; Safari reads a handful and still leans on `<meta>`/`<link>` tags, so ship both. Get the manifest right first, because every other PWA feature (install prompt, splash screen, share target, file handling) hangs off it.

## Pattern

```json
// /manifest.webmanifest  (serve as application/manifest+json; most hosts do by extension)
{
  "id": "/",
  "name": "Fieldbook - Site Inspection Notes",
  "short_name": "Fieldbook",
  "description": "Write inspection notes and photos on site, even without signal.",
  "lang": "en",
  "dir": "ltr",
  "start_url": "/?source=pwa",
  "scope": "/",
  "display": "standalone",
  "display_override": ["window-controls-overlay", "standalone"],
  "orientation": "any",
  "theme_color": "#0f766e",
  "background_color": "#f8fafc",
  "categories": ["productivity", "business"],
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
    { "src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "screenshots": [
    { "src": "/screenshots/phone-notes.png", "sizes": "1080x1920", "type": "image/png", "form_factor": "narrow", "label": "Notes list" },
    { "src": "/screenshots/desktop-notes.png", "sizes": "1920x1080", "type": "image/png", "form_factor": "wide", "label": "Notes on desktop" }
  ],
  "shortcuts": [
    { "name": "New note", "url": "/new?source=shortcut", "icons": [{ "src": "/icons/shortcut-new.png", "sizes": "96x96" }] }
  ]
}
```

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Fieldbook</title>
  <link rel="manifest" href="/manifest.webmanifest">
  <!-- theme-color colours the Android status bar and the desktop title bar; one per scheme -->
  <meta name="theme-color" content="#0f766e" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#134e4a" media="(prefers-color-scheme: dark)">
  <!-- Safari: still the most reliable way to get the right home-screen icon and status bar -->
  <link rel="apple-touch-icon" href="/icons/apple-touch-icon.png"><!-- 180x180, no transparency -->
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Fieldbook">
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/icons/icon.svg" type="image/svg+xml">
</head>
```

Install criteria (Chromium; Safari has no prompt, it installs anything via the Share sheet):

1. Served over HTTPS (`localhost` counts as secure for development).
2. Manifest linked from the page, with `name` or `short_name`, `start_url`, `display` of `standalone`, `fullscreen` or `minimal-ui`, and icons at 192 and 512 px.
3. `start_url` is inside `scope` and responds 200 (not a redirect to a login page).
4. A service worker is no longer required for the prompt in current Chromium, but install one anyway so the app opens offline (`web-pwa-service-worker-offline`).

Verify in Chrome DevTools: Application > Manifest lists every field it parsed and an "Installability" section with the exact reason when the prompt will not show.

## Variations

- **Separate maskable files, not `"purpose": "any maskable"`**: a maskable icon has 20 percent padding that looks tiny as a plain icon. Generate both from one source with `web-pwa-app-icons-splash`.
- **Desktop app feel**: `"display_override": ["window-controls-overlay"]` lets the title bar become part of your page; pad the header with `env(titlebar-area-height)` and keep it optional, Safari ignores it.
- **Multi-page site with one app section**: set `"scope": "/app/"` and `"start_url": "/app/"`; links outside the scope open in a browser tab with a URL bar, which is what you want for the marketing pages.
- **Localised names**: serve a different manifest per language (`/fr/manifest.webmanifest`) rather than switching the `<link>` at runtime; the browser reads the manifest once at install time.

## Pitfalls

- `start_url` with a query string (`?source=pwa`) is useful for analytics but must be stable: Chromium uses `id` (falling back to `start_url`) to decide whether an install is "the same app". Set `id` explicitly so you can change `start_url` later without creating a duplicate app.
- `theme_color` in the manifest is only read at install; the `<meta name="theme-color">` tag is what updates live and per colour scheme. Keep them consistent.
- `background_color` must match your page background or users see a flash between the splash screen and the first paint (`web-design-dark-mode` for the dark variant).
- Icons with transparency on iOS get a black background. Give `apple-touch-icon.png` a solid fill.
- A manifest served with `Content-Type: text/plain` or with a JSON comment in it silently fails. Validate it in DevTools, and strip the `//` comment from the sample above.
- `screenshots` without `form_factor` are shown on neither platform; one `narrow` and one `wide` unlocks the richer install dialog on Android and desktop Chrome.
- Changing icons after launch: Android refreshes the icon only when the manifest changes and the app is next launched, and some launchers cache it until reinstall. Get the icon right before launch.

## Related skills

- `web-pwa-app-icons-splash`
- `web-pwa-install-prompt`
- `web-pwa-service-worker-offline`
- `web-perf-caching-and-service-worker`
- `web-seo-meta-tags`
- `web-ship-static-hosting`
