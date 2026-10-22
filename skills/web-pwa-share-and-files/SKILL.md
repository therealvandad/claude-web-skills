---
name: web-pwa-share-and-files
description: Make a PWA share and open files natively - Web Share with copy-link fallback, a manifest share target, file handlers with launchQueue, and File System Access open/save with input and download fallbacks, all feature-detected. Use when a user says "share button", "share to my app", "open files with my PWA", "save file", "file picker" or "Web Share API".
---

# Sharing and files in a PWA

These four APIs make an installed web app feel native, but support is patchy and none of them works in every browser on every platform. Treat each as an enhancement over something that always works: a copy-link button, an upload field, a download. Detect the feature, never the browser, and keep the fallback path tested.

| API | Works in (2026) | Fallback |
| --- | --- | --- |
| `navigator.share` | Safari (iOS, macOS), Chrome and Firefox on Android, Chromium on Windows and ChromeOS | Copy link to clipboard |
| `share_target` (manifest) | Installed apps in Chromium on Android and ChromeOS | Paste or upload field in the app |
| `file_handlers` + `launchQueue` | Installed apps in desktop Chrome and Edge | "Open file" button |
| `showOpenFilePicker` / `showSaveFilePicker` | Desktop Chrome, Edge, Opera | `<input type="file">` and `<a download>` |

## Pattern

```js
// /js/share-files.js
export async function share({ title, text, url, files }) {
  const data = { title, text, url, ...(files?.length && { files }) };
  if (navigator.share && (navigator.canShare?.(data) ?? !files)) {
    try { await navigator.share(data); return "shared"; }          // must run inside a click handler
    catch (err) { if (err.name === "AbortError") return "cancelled"; } // user closed the sheet: not an error
  }
  if (url && navigator.clipboard) { await navigator.clipboard.writeText(url); return "copied"; }
  return "unsupported";
}

const types = [{ description: "Notes", accept: { "text/plain": [".txt"], "text/markdown": [".md"] } }];
let handle = null;                     // remembered so "Save" writes back to the same file where supported

export async function openFile() {
  if ("showOpenFilePicker" in window) {
    try { [handle] = await showOpenFilePicker({ types }); return await handle.getFile(); }
    catch (err) { if (err.name === "AbortError") return null; throw err; }
  }
  return new Promise((resolve) => {    // fallback: every browser
    const input = Object.assign(document.createElement("input"), { type: "file", accept: ".txt,.md,text/plain,text/markdown" });
    input.addEventListener("change", () => resolve(input.files[0] ?? null));
    input.addEventListener("cancel", () => resolve(null));
    input.click();
  });
}

export async function saveFile(text, suggestedName = "notes.md") {
  const blob = new Blob([text], { type: "text/markdown" });
  if ("showSaveFilePicker" in window) {
    try {
      handle ??= await showSaveFilePicker({ suggestedName, types });
      const w = await handle.createWritable(); await w.write(blob); await w.close(); return "saved";
    } catch (err) { if (err.name === "AbortError") return "cancelled"; throw err; }
  }
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: suggestedName });
  a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);  // fallback: a download
  return "downloaded";
}

if ("launchQueue" in window) {         // file handlers: the app was opened with files
  launchQueue.setConsumer(async ({ files }) => {
    for (const h of files) { handle = h; document.dispatchEvent(new CustomEvent("file-opened", { detail: await h.getFile() })); }
  });
}
```

```html
<div class="flex flex-wrap items-center gap-2">
  <button type="button" data-share class="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:border-slate-600 dark:hover:bg-slate-800">Share</button>
  <span data-share-status role="status" class="text-sm text-slate-600 dark:text-slate-300"></span>
</div>
<script type="module">
  import { share } from "/js/share-files.js";
  const status = document.querySelector("[data-share-status]");
  document.querySelector("[data-share]").addEventListener("click", async () => {
    const result = await share({ title: document.title, url: location.href });
    status.textContent = { copied: "Link copied.", unsupported: "Copy the address bar to share." }[result] ?? "";
  });
</script>
```

Manifest additions for receiving shares and opening files (installed app only):

```json
{
  "share_target": {
    "action": "/share-target", "method": "POST", "enctype": "multipart/form-data",
    "params": { "title": "title", "text": "text", "url": "url",
                "files": [{ "name": "media", "accept": ["image/*", "application/pdf"] }] }
  },
  "file_handlers": [{ "action": "/open", "accept": { "text/markdown": [".md"], "text/plain": [".txt"] } }]
}
```

The worker receives the shared POST. Put this handler before the `method !== "GET"` guard of `web-pwa-service-worker-offline`:

```js
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "POST" || url.pathname !== "/share-target") return;
  e.respondWith((async () => {
    const form = await e.request.formData();
    const cache = await caches.open("shared");
    const files = form.getAll("media");
    await Promise.all(files.map((f, i) => cache.put(`/shared/${i}`, new Response(f, { headers: { "Content-Type": f.type } }))));
    await cache.put("/shared/meta", Response.json({ title: form.get("title"), text: form.get("text"), url: form.get("url"), count: files.length }));
    return Response.redirect("/share-target?received=1", 303);   // the page reads /shared/* from the cache
  })());
});
```

## Variations

- **Text-only share target**: use `"method": "GET"` with `title`, `text`, `url` params; no worker code, the page reads `location.search`. Android apps often put the link in `text`, not `url`, so check both.
- **Share files out**: `share({ files: [new File([blob], "chart.png", { type: "image/png" })] })`. `canShare` rejects unsupported types; fall back to `saveFile`.
- **Drag and drop**: add `dragover`/`drop` on the editor and read `e.dataTransfer.files`; it works everywhere and covers desktop Firefox and Safari, where the pickers and file handlers do not exist.
- **Private app storage**: the Origin Private File System (`navigator.storage.getDirectory()`) works in all modern browsers including Safari and Firefox, but the user never sees those files; see `web-pwa-storage`.

## Pitfalls

- `navigator.share`, the pickers and `clipboard.writeText` need a user gesture and a secure context. Calling them after an `await fetch(...)` can lose the gesture in Safari; gather data first, then call.
- Share targets and file handlers only appear after install, and the OS share sheet caches the list; reinstall the app after changing the manifest.
- A file handle from `launchQueue` or a picker needs write permission again after a reload. Expect `createWritable` to prompt, and handle `NotAllowedError` by falling back to a download.
- Do not hide the Share button when `navigator.share` is missing; it still works as "Copy link". Hide only when both paths are unavailable.
- Files from a share target can be large. Check `navigator.storage.estimate()` before caching them and delete `/shared/*` once the page has consumed them.

## Related skills

- `web-pwa-manifest`
- `web-pwa-service-worker-offline`
- `web-pwa-storage`
- `web-form-file-upload`
- `web-ui-toast-notifications`
