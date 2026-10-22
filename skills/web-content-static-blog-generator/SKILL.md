---
name: web-content-static-blog-generator
description: 'A 64-line Python 3.10 static blog generator: posts/*.md with front matter become an index, post pages, tag pages and an RSS feed through one template.html. Use when a user says "make a blog without WordPress", "static blog", "blog from Markdown files", "tag pages" or "RSS for my blog".'
---

# Static blog generator

A blog is four kinds of output (post pages, a newest-first index, tag archives, a feed) computed from one list of posts. A static site generator such as Hugo or Eleventy does that plus a hundred things a small site never uses; this script does exactly the four in about 60 lines of standard-library Python, so you can read all of it, change the HTML it writes, and host the result on any static host. It uses the `markdown` package when installed and otherwise a built-in fallback for headings, paragraphs and code blocks.

## Pattern

```text
blog.py   template.html   posts/container-queries.md   posts/no-cms.md
  -> dist/index.html  dist/posts/<slug>.html  dist/tags/<tag>.html  dist/feed.xml
```

A post: the file name is the slug, front matter is flat `key: value`.

```markdown
---
title: Container queries in a sidebar
date: 2026-03-14
tags: css, layout
summary: Why the card broke and how @container fixed it.
---
The card looked fine on the home page.

## The fix
```

`template.html` is any full page with `{{ title }}` and `{{ content }}`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <link rel="stylesheet" href="/css/output.css">
  <link rel="alternate" type="application/rss+xml" title="Field Notes" href="/feed.xml">
</head>
<body class="bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
  <header class="mx-auto max-w-prose px-4 pt-8"><a href="/" class="font-semibold">Field Notes</a></header>
  <main class="content mx-auto max-w-prose px-4 py-10">{{ content }}</main>
</body>
</html>
```

```python
"""posts/*.md -> dist/ index, posts, tags, feed.xml. Usage: python blog.py"""
import html, re, shutil
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

SITE = {"title": "Field Notes", "url": "https://example.com", "description": "Notes on building small websites."}
ROOT, DIST = Path(__file__).parent, Path(__file__).parent / "dist"
BASE = (ROOT / "template.html").read_text(encoding="utf-8")

try:
    from markdown import markdown as render
except ImportError:  # no-dependency fallback: headings, code fences, paragraphs
    def render(text):
        blocks = re.split(r"\n\s*\n", text.strip())
        out = []
        for b in blocks:
            if b.startswith("```"):
                out.append(f"<pre><code>{html.escape(b.strip('`').split(chr(10), 1)[-1])}</code></pre>")
            elif m := re.match(r"(#{2,4}) (.+)", b):
                out.append(f"<h{len(m[1])}>{html.escape(m[2])}</h{len(m[1])}>")
            else:
                out.append(f"<p>{html.escape(b)}</p>")
        return "\n".join(out)

def load(path):
    head, body = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(encoding="utf-8"), re.S).groups()
    meta = {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in head.splitlines() if ":" in l)}
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    date = datetime.fromisoformat(meta["date"]).replace(tzinfo=timezone.utc)
    return {"slug": path.stem, "title": meta["title"], "date": date, "tags": tags, "html": render(body),
            "summary": meta.get("summary", "")}

def page(path, title, content):
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    text = BASE.replace("{{ title }}", html.escape(f"{title} · {SITE['title']}")).replace("{{ content }}", content)
    out.write_text(text, encoding="utf-8")

def listing(posts):
    items = "".join(f'<li><a href="/posts/{p["slug"]}.html">{html.escape(p["title"])}</a> '
                    f'<time datetime="{p["date"]:%Y-%m-%d}">{p["date"]:%d %b %Y}</time></li>' for p in posts)
    return f'<ul class="post-list">{items}</ul>'

def build():
    shutil.rmtree(DIST, ignore_errors=True)
    posts = sorted((load(p) for p in (ROOT / "posts").glob("*.md")), key=lambda p: p["date"], reverse=True)
    for p in posts:
        tags = " ".join(f'<a href="/tags/{t}.html">#{html.escape(t)}</a>' for t in p["tags"])
        page(f"posts/{p['slug']}.html", p["title"], f'<article><h1>{html.escape(p["title"])}</h1>'
             f'<p><time datetime="{p["date"]:%Y-%m-%d}">{p["date"]:%d %b %Y}</time> {tags}</p>{p["html"]}</article>')
    page("index.html", "Home", f"<h1>{SITE['title']}</h1>{listing(posts)}")
    for tag in sorted({t for p in posts for t in p["tags"]}):
        page(f"tags/{tag}.html", f"#{tag}", f"<h1>Tagged #{html.escape(tag)}</h1>{listing([p for p in posts if tag in p['tags']])}")
    items = "".join(f"<item><title>{html.escape(p['title'])}</title><link>{SITE['url']}/posts/{p['slug']}.html</link>"
                    f"<guid>{SITE['url']}/posts/{p['slug']}.html</guid><pubDate>{format_datetime(p['date'])}</pubDate>"
                    f"<description>{html.escape(p['summary'] or p['html'])}</description></item>" for p in posts[:20])
    (DIST / "feed.xml").write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel>'
        f"<title>{SITE['title']}</title><link>{SITE['url']}/</link><description>{SITE['description']}</description>"
        f"{items}</channel></rss>\n", encoding="utf-8")
    print(f"built {len(posts)} posts into {DIST}")

if __name__ == "__main__":
    build()
```

```bash
python blog.py                                 # Windows: py blog.py
python -m http.server 8000 --directory dist    # preview at http://localhost:8000
```

## Variations

- **Full Markdown**: `pip install markdown` and the `try` import picks it up (lists, links, emphasis, tables via `markdown(text, extensions=["tables"])`). Or paste `md_to_html` from `web-content-markdown-pipeline` over the fallback for lists, links and images without a dependency.
- **Styled listing**: the generated tags carry plain classes (`post-list`, `content`); style them in `@layer components` or put Tailwind classes straight into the f-strings, and add `dist/**/*.html` (or the script itself via `@source "../blog.py"`) to Tailwind's sources so the classes are generated.
- **Drafts and future posts**: skip posts with `meta.get("draft") == "true"` or `date > datetime.now(timezone.utc)` inside `build()` before rendering.
- **Pagination**: slice `posts` into chunks of 10 and write `page/2.html`, `page/3.html` with the same `listing()`; link them with `web-nav-pagination`.

## Pitfalls

- The fallback splits on blank lines, so a code block that contains an empty line breaks in two. Install `markdown` for posts with real code samples.
- Tags become file names: keep them lowercase ASCII with hyphens (`web-design`, not `Web Design`), or slugify with `re.sub(r"[^a-z0-9]+", "-", tag.lower())`.
- The feed needs absolute URLs and RFC 822 dates; `SITE["url"]` and `email.utils.format_datetime` handle both. Change `SITE["url"]` before deploying or every feed reader links to example.com.
- `build()` deletes `dist/` first so renamed or removed posts disappear; keep CSS and images in a `static/` folder and copy it in with `shutil.copytree("static", DIST, dirs_exist_ok=True)`.
- Dates without a time are treated as midnight UTC; add a time (`2026-03-14T09:00`) if the order of two same-day posts matters.

## Related skills

- `web-content-markdown-pipeline`
- `web-content-sitemap-and-feeds`
- `web-content-partials-build`
- `web-page-blog-index`
- `web-page-blog-post`
- `web-ship-static-hosting`
