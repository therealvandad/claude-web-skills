---
name: web-content-partials-build
description: Assemble static pages from shared partials (header, footer) using <!-- include: header --> markers, with a short Python 3.10 build script, a --watch polling mode and automatic aria-current on the active link. Use when a user says "same header on every page", "include header and footer", "html includes", "partials without a framework" or "I copy the nav into every page".
---

# Partials build

Plain HTML has no include. Copying the nav into twelve pages means twelve edits for every new link, and one page always drifts. Keep each shared block in `src/partials/` and let a small script paste it into every page at build time; the output in `dist/` is ordinary HTML that any static host serves. A marker is an HTML comment on its own line, so an unbuilt page still opens in a browser and just lacks the header.

## Pattern

```text
src/partials/header.html   src/partials/footer.html
src/pages/index.html       src/pages/about/index.html   src/pages/css/site.css
                  -- python build_partials.py src dist -->
dist/index.html            dist/about/index.html        dist/css/site.css
```

```html
<!-- src/pages/about/index.html -->
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>About</title></head>
<body>
  <!-- include: header -->
  <main id="main"><h1>About</h1></main>
  <!-- include: footer -->
</body>
</html>
```

```python
"""Assemble pages from partials. Usage: python build_partials.py src dist [--watch]
src/partials/header.html  +  src/pages/**/*.html  ->  dist/**/*.html
A page pulls a partial in with a marker on its own: <!-- include: header -->"""
import re, shutil, sys, time
from pathlib import Path

MARKER = re.compile(r"[ \t]*<!--\s*include:\s*([\w./-]+?)\s*-->")
MAX_DEPTH = 5

def load_partial(partials, name, stack):
    if name in stack or len(stack) >= MAX_DEPTH:
        raise RuntimeError(f"include loop: {' -> '.join([*stack, name])}")
    path = partials / (name if name.endswith(".html") else f"{name}.html")
    if not path.is_file():
        raise FileNotFoundError(f"partial not found: {path}")
    text = path.read_text(encoding="utf-8").strip("\n")
    return expand(text, partials, [*stack, name])          # partials may include partials

def expand(text, partials, stack=()):
    return MARKER.sub(lambda m: load_partial(partials, m[1], list(stack)), text)

def mark_current(html, url):
    """Add aria-current="page" to links that point at this page (url like /about/)."""
    def fix(m):
        tag = m[0]
        return tag if "aria-current" in tag else tag[:-1] + ' aria-current="page">'
    return re.sub(rf'<a\b[^>]*\bhref="{re.escape(url)}"[^>]*>', fix, html)

def page_url(rel):
    p = "/" + rel.as_posix()
    return p[: -len("index.html")] if p.endswith("/index.html") or p == "/index.html" else p

def build(src, dist):
    pages, partials = src / "pages", src / "partials"
    count = 0
    for path in sorted(pages.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(pages)
        out = dist / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".html":
            html = expand(path.read_text(encoding="utf-8"), partials)
            out.write_text(mark_current(html, page_url(rel)), encoding="utf-8", newline="\n")
            count += 1
        elif not out.exists() or path.stat().st_mtime > out.stat().st_mtime:
            shutil.copy2(path, out)                       # css, images, fonts pass through
    print(f"built {count} pages -> {dist}")

def snapshot(src):
    return {str(p): p.stat().st_mtime_ns for p in src.rglob("*") if p.is_file()}

def watch(src, dist, interval=0.5):
    seen = None
    print(f"watching {src} (Ctrl+C to stop)")
    try:
        while True:
            now = snapshot(src)
            if now != seen:
                try:
                    build(src, dist)
                except (RuntimeError, OSError) as err:     # keep watching after a typo
                    print("error:", err)
                seen = now
            time.sleep(interval)
    except KeyboardInterrupt:
        print("stopped")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src, dist = Path(args[0] if args else "src"), Path(args[1] if len(args) > 1 else "dist")
    if "--watch" in sys.argv:
        watch(src, dist)
    else:
        try:
            build(src, dist)
        except (RuntimeError, OSError) as err:
            sys.exit(f"error: {err}")
```

```bash
python build_partials.py src dist            # one build; Windows: py build_partials.py src dist
python build_partials.py src dist --watch    # rebuild when any file in src changes
```

## Variations

- **Nested partials**: `header.html` may contain `<!-- include: nav -->`; loops are detected and reported with the chain of names.
- **Shared head tags**: keep `<title>` and the description in each page, and put the fonts, stylesheet link and favicon in `partials/head-common.html`, included inside `<head>` with `<!-- include: head-common -->`.
- **Subfolders of partials**: names may contain a slash, `<!-- include: blog/sidebar -->` reads `partials/blog/sidebar.html`.
- **Live reload**: run `--watch` in one terminal and any static server (`python -m http.server -d dist`) in another; refresh by hand.

## Pitfalls

- Use root-relative URLs (`/css/site.css`, `/about/`) inside partials. A relative `href="about/"` is correct on the home page and broken on `/blog/post/`.
- `aria-current` is added by matching `href` to the page URL exactly (`/about/` for `about/index.html`); links written without the trailing slash will not match.
- Polling checks file times twice a second, which is fine for a site of hundreds of files; it will not notice a partial that is replaced with an older timestamp.
- The marker regex only allows letters, digits, `.`, `/`, `_` and `-`; a typo prints `partial not found` with the path and the watcher keeps running.
- Delete `dist/` before a release build so renamed or removed pages do not linger on the host.
- Read and write UTF-8 explicitly; Windows defaults to cp1252 and corrupts non-ASCII text.

## Related skills

- `web-content-markdown-pipeline`
- `web-content-static-blog-generator`
- `web-craft-code-structure`
- `web-layout-page-shell`
- `web-ship-project-setup`
