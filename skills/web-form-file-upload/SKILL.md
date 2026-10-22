---
name: web-form-file-upload
description: 'Build a drag-and-drop file upload zone with Tailwind and vanilla JS: a real file input underneath, image thumbnails, a file list with remove buttons, client-side size and type checks, and DataTransfer syncing so the form still submits natively. Use whenever a user asks for "file upload", "drag and drop files", "image picker", "attach a document", or "upload avatar".'
---

# File upload

The accessible core is always a native `<input type="file">` with a `<label>`: it opens the OS picker, works with the keyboard, and on phones opens camera and photo library. The drop zone is sugar layered on top: the label becomes the zone, `dragover`/`drop` events add files, and the chosen files are written back into the input through a `DataTransfer` object so a plain form submission (or `FormData`) still carries them. Validate size and MIME type in the browser for fast feedback, and again on the server because `accept` and `File.type` are advisory.

## Pattern

```html
<div class="space-y-2" data-upload data-max-size="5242880" data-max-files="5">
  <span id="files-label" class="block text-sm font-medium text-gray-800 dark:text-gray-200">Attachments</span>
  <label for="files" data-zone
    class="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 px-6 py-10 text-center
           transition-colors hover:border-blue-400 hover:bg-blue-50
           has-[:focus-visible]:border-blue-500 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-blue-500
           data-[dragging]:border-blue-500 data-[dragging]:bg-blue-50
           dark:border-gray-600 dark:bg-gray-900 dark:hover:bg-gray-800 dark:data-[dragging]:bg-gray-800">
    <svg class="size-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 16V4m0 0 4 4m-4-4-4 4M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>
    </svg>
    <span class="text-sm text-gray-700 dark:text-gray-300">
      <span class="font-semibold text-blue-600 dark:text-blue-400">Choose files</span> or drag them here
    </span>
    <span class="text-xs text-gray-500">PNG, JPG or PDF, up to 5 MB each, max 5 files</span>
    <input id="files" name="files" type="file" multiple accept="image/png,image/jpeg,application/pdf"
      aria-describedby="files-error" class="sr-only">
  </label>
  <p id="files-error" class="min-h-5 text-sm text-red-600" aria-live="polite"></p>
  <ul data-list class="divide-y divide-gray-200 rounded-md border border-gray-200 empty:hidden dark:divide-gray-700 dark:border-gray-700" aria-labelledby="files-label"></ul>
</div>
```

```js
function initUpload(root) {
  const input = root.querySelector('input[type=file]');
  const zone = root.querySelector('[data-zone]');
  const list = root.querySelector('[data-list]');
  const error = root.querySelector('[id$=-error]');
  const maxSize = Number(root.dataset.maxSize);
  const maxFiles = Number(root.dataset.maxFiles) || Infinity;
  const accept = (input.accept || '').split(',').map((t) => t.trim()).filter(Boolean);
  let files = [];

  const fmt = (bytes) => bytes < 1048576 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / 1048576).toFixed(1)} MB`;
  const allowed = (f) => accept.length === 0 || accept.some((t) => t.endsWith('/*') ? f.type.startsWith(t.slice(0, -1)) : f.type === t);

  function addFiles(incoming) {
    const problems = [];
    for (const f of incoming) {
      if (files.length >= maxFiles) { problems.push(`Only ${maxFiles} files allowed.`); break; }
      if (!allowed(f)) { problems.push(`${f.name}: type not allowed.`); continue; }
      if (f.size > maxSize) { problems.push(`${f.name}: larger than ${fmt(maxSize)}.`); continue; }
      if (files.some((x) => x.name === f.name && x.size === f.size)) continue;   // skip duplicates
      files.push(f);
    }
    error.textContent = problems.join(' ');
    sync();
  }

  function sync() {
    const dt = new DataTransfer();                       // write our list back into the native input
    files.forEach((f) => dt.items.add(f));
    input.files = dt.files;
    list.replaceChildren(...files.map(renderItem));
  }

  function renderItem(f, i) {
    const li = document.createElement('li');
    li.className = 'flex items-center gap-3 p-3 text-sm';
    const thumb = f.type.startsWith('image/')
      ? Object.assign(document.createElement('img'), { src: URL.createObjectURL(f), alt: '', className: 'size-10 rounded object-cover' })
      : Object.assign(document.createElement('span'), { textContent: 'PDF', className: 'grid size-10 place-items-center rounded bg-gray-100 text-xs font-semibold text-gray-600' });
    thumb.addEventListener('load', () => URL.revokeObjectURL(thumb.src));
    const name = Object.assign(document.createElement('span'), { textContent: f.name, className: 'min-w-0 flex-1 truncate text-gray-900 dark:text-gray-100' });
    const size = Object.assign(document.createElement('span'), { textContent: fmt(f.size), className: 'text-gray-500' });
    const remove = Object.assign(document.createElement('button'), { type: 'button', textContent: 'Remove',
      className: 'rounded px-2 py-1 text-red-600 hover:bg-red-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500' });
    remove.setAttribute('aria-label', `Remove ${f.name}`);
    remove.addEventListener('click', () => { files.splice(i, 1); sync(); input.focus(); });
    li.append(thumb, name, size, remove);
    return li;
  }

  input.addEventListener('change', () => addFiles(input.files));
  ['dragenter', 'dragover'].forEach((t) => zone.addEventListener(t, (e) => { e.preventDefault(); zone.dataset.dragging = ''; }));
  ['dragleave', 'drop'].forEach((t) => zone.addEventListener(t, (e) => { e.preventDefault(); delete zone.dataset.dragging; }));
  zone.addEventListener('drop', (e) => addFiles(e.dataTransfer.files));
}

document.querySelectorAll('[data-upload]').forEach(initUpload);
```

Why these choices: the input is `sr-only` (not `hidden` or `display:none`), so it remains focusable and the label gets a visible ring through `has-[:focus-visible]:`. `preventDefault` on `dragover` is mandatory or the browser navigates to the dropped file. Writing files back with `DataTransfer` means removal actually removes from the submission; without it the input still holds the original selection. Object URLs are revoked on load to avoid leaking memory with many previews. Errors go to the reserved `aria-live` slot so screen readers hear why a file was rejected.

## Variations

- **Single avatar**: drop `multiple`, set `data-max-files="1"`, render the preview as a `size-24 rounded-full` image inside the zone itself, and replace rather than append on each change.
- **Camera on mobile**: add `capture="environment"` (rear) or `capture="user"` (front) alongside `accept="image/*"`; the picker opens the camera directly.
- **Upload progress**: send with `XMLHttpRequest` (the only API with upload progress events) and render a `<progress max="100">` per file; see `web-form-submit-with-fetch` for the surrounding flow.
- **Paste support**: listen for `paste` on the zone and pass `e.clipboardData.files` to `addFiles` so screenshots can be pasted.

## Pitfalls

- `accept` filters the picker but does not block a dragged file or a renamed `.exe`; check `File.type` client-side and the real bytes server-side.
- `File.type` is empty for some files (unknown extensions, some Windows drops); treat empty as "unknown", not "forbidden", or allow by extension too.
- Dragging a file over child elements fires `dragleave` on the zone repeatedly; the `data-[dragging]` toggle handles it because `dragover` re-adds it every frame. Add `pointer-events-none` to children if you see flicker.
- Setting `input.files` throws in very old browsers; wrap `sync()` in a feature check (`'DataTransfer' in window`) and fall back to submitting via `FormData` built from your `files` array.
- The whole zone as a `<label>` means a click anywhere opens the picker; keep the "Remove" buttons outside the label or the click bubbles and reopens it.
- Large image previews from a 20 MB photo freeze the main thread; for photo-heavy flows use `createImageBitmap(file, { resizeWidth: 200 })` and draw to a canvas.

## Related skills

- `web-form-layout`
- `web-form-validation`
- `web-form-submit-with-fetch`
- `web-motion-loading-and-progress`
- `web-perf-images`
- `web-a11y-keyboard-and-focus`
