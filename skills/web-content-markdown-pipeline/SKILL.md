---
name: web-content-markdown-pipeline
description: Turn a folder of Markdown files with YAML-style front matter into HTML pages through one template, using a short Python 3.10 script with no required dependencies (optional `markdown` package), code-block classes for highlighting, lazy images and heading ids. Use when a user says "write pages in Markdown", "convert md to html", "front matter", "content folder", "docs from Markdown" or "no CMS".
---

# Markdown to HTML pipeline

Writing long content in HTML is slow and error-prone; Markdown keeps authors in prose while a build step owns the markup. The pipeline has three parts: front matter (title, description, date, draft) parsed into a dict, a Markdown renderer, and a template with `{{ placeholders }}`. The script below runs on a stock Python 3.10 on Windows, macOS and Linux. It uses the `markdown` package when installed (tables, footnotes, nested lists) and otherwise falls back to a built-in converter that covers headings, paragraphs, lists, quotes, code fences, links, images and emphasis.

## Pattern

```text
content/_template.html   content/hello.md   build_md.py   ->   dist/hello.html
```

```markdown
---
title: Shipping a static site in a weekend
description: Notes from moving our docs off a CMS.
date: 2026-03-14
---
# Shipping a static site

We moved **42 pages** in *two days*. ![Build output](/img/build.png)
```

`content/_template.html` is a normal page with three placeholders:

```html
<title>{{ title }}</title>
<meta name="description" content="{{ description }}">
...
<main class="mx-auto max-w-prose px-4 py-12">
  <article class="content">{{ content }}</article>
</main>
```

```python
"""Markdown + front matter -> HTML pages. Usage: python build_md.py content dist"""
import html, re, sys
from pathlib import Path

def front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    meta = dict(line.split(":", 1) for line in m[1].splitlines() if ":" in line)
    return {k.strip(): v.strip().strip('"') for k, v in meta.items()}, text[m.end():]

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)', r'<img src="\2" alt="\1" loading="lazy" decoding="async">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![*\w])\*(?!\s)(.+?)\*(?!\w)", r"<em>\1</em>", s)

def md_to_html(text):  # no-dependency subset: headings, lists, quotes, code fences, hr, paragraphs
    out, para, lst = [], [], None
    def flush():
        nonlocal lst
        if para: out.append(f"<p>{inline(' '.join(para))}</p>"); para.clear()
        if lst: out.append(f"</{lst}>"); lst = None
    lines = iter(text.splitlines())
    for line in lines:
        if line.startswith("```"):
            flush(); lang = line[3:].strip(); code = []
            for c in lines:
                if c.startswith("```"): break
                code.append(c)
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
        elif m := re.match(r"(#{1,6})\s+(.*)", line):
            flush(); n = len(m[1]); slug = re.sub(r"[^\w]+", "-", m[2].lower()).strip("-")
            out.append(f'<h{n} id="{slug}">{inline(m[2])}</h{n}>')
        elif m := re.match(r"\s*([-*]|\d+\.)\s+(.*)", line):
            tag = "ol" if m[1][0].isdigit() else "ul"
            if lst != tag: flush(); out.append(f"<{tag}>"); lst = tag
            out.append(f"<li>{inline(m[2])}</li>")
        elif line.startswith(">"):
            flush(); out.append(f"<blockquote><p>{inline(line.lstrip('> '))}</p></blockquote>")
        elif re.fullmatch(r"\s*(---|\*\*\*)\s*", line):
            flush(); out.append("<hr>")
        elif not line.strip():
            flush()
        else:
            if lst: flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)

try:  # richer output (tables, footnotes) when `pip install markdown` is available
    import markdown
    def render(text): return markdown.markdown(text, extensions=["fenced_code", "tables", "toc"])
except ImportError:
    render = md_to_html

def build(src, dist):
    template = (src / "_template.html").read_text(encoding="utf-8")
    for path in sorted(src.glob("*.md")):
        meta, body = front_matter(path.read_text(encoding="utf-8"))
        if meta.get("draft") == "true":
            continue
        page = template.replace("{{ title }}", html.escape(meta.get("title", path.stem)))
        page = page.replace("{{ description }}", html.escape(meta.get("description", "")))
        page = page.replace("{{ content }}", render(body))
        out = dist / f"{path.stem}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print("wrote", out)

if __name__ == "__main__":
    build(Path(sys.argv[1] if len(sys.argv) > 1 else "content"), Path(sys.argv[2] if len(sys.argv) > 2 else "dist"))
```

```bash
python build_md.py content dist        # Windows: py build_md.py content dist
```

Style the generated tags once, since Markdown output carries no classes (Tailwind v4, `src/input.css`):

```css
@layer components {
  .content > * + * { margin-top: 1.25em; }
  .content h2 { font-size: var(--text-2xl); font-weight: 700; margin-top: 2em; }
  .content a { text-decoration: underline; text-underline-offset: 3px; }
  .content ul { list-style: disc; padding-inline-start: 1.5em; }
  .content pre { overflow-x: auto; border-radius: var(--radius-lg); background: var(--color-gray-900); color: var(--color-gray-100); padding: 1rem; }
  .content img { border-radius: var(--radius-lg); max-width: 100%; height: auto; }
}
```

## Variations

- **Code highlighting**: the fallback writes `<pre><code class="language-python">`, which client highlighters understand. Load highlight.js pinned: `<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script><script>hljs.highlightAll()</script>` plus one theme CSS. For zero client JS, `pip install markdown pygments` and add `"codehilite"` to the extensions list.
- **Figures with captions**: post-process the output with `re.sub(r'<p>(<img [^>]*alt="([^"]*)"[^>]*>)</p>', r'<figure>\1<figcaption>\2</figcaption></figure>', html)`, or write `<figure>` HTML in the Markdown, which only the `markdown` package passes through.
- **Nested folders**: replace `src.glob("*.md")` with `src.rglob("*.md")` and write to `dist / path.relative_to(src).with_suffix(".html")` to keep `/docs/guide/install.html` URLs.
- **Image sizes**: run `web-content-images-pipeline` first and swap each `<img src>` for the generated `srcset` markup by file name.

## Pitfalls

- The fallback escapes all HTML, so raw `<div>` in Markdown appears as text. That is the safe default for content from other people; use the `markdown` package only for trusted authors, since it passes HTML through.
- Front matter here is flat `key: value` text, not full YAML: no lists or nesting. Write tags as `tags: css, layout` and split on commas, or `pip install pyyaml` when you need more.
- Always read and write with `encoding="utf-8"`; Windows defaults to cp1252 and breaks on the first em dash or Arabic word.
- The fallback converter is a subset: emphasis inside inline code and nested lists are not handled. If authors need them, install `markdown` rather than growing the regexes.
- Draft posts (`draft: true`) are skipped; delete the stale `dist/` before a full build so removed pages do not linger on the server.

## Related skills

- `web-content-static-blog-generator`
- `web-content-partials-build`
- `web-content-images-pipeline`
- `web-page-blog-post`
- `web-page-docs`
