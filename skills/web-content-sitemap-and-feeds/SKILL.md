---
name: web-content-sitemap-and-feeds
description: Generate sitemap.xml, RSS 2.0, Atom and JSON Feed from a folder of built HTML pages with one Python 3.10 standard-library script and a --base-url argument. Use when a user says "generate a sitemap", "add an RSS feed", "Atom feed", "JSON Feed", "sitemap for a static site" or "let people subscribe".
---

# Sitemap and feeds from the pages folder

Search engines read `sitemap.xml`; feed readers read RSS, Atom or JSON Feed. All four files are lists of URLs with titles and dates, and your built pages already hold that data, so generate them in the last build step instead of editing XML by hand. The script reads each page's `<title>`, meta description and date, skips `noindex`, `404` and `_private` files, and writes the files beside the pages. A page enters the feeds only if it is dated; undated pages (home, about) go in the sitemap alone.

## Pattern

Date a post once, in its HTML (the markdown and blog generator skills can emit this line):

```html
<title>Roasting at home</title>
<meta name="description" content="What changed when we dropped the drum roaster.">
<meta property="article:published_time" content="2026-03-14T09:00:00Z">
```

```python
"""sitemap.xml, rss.xml, atom.xml and feed.json from a folder of built HTML pages.
Usage: python build_feeds.py dist --base-url https://example.com [--title "My site"] [--limit 20]
Pages with <meta property="article:published_time"> or a <time datetime> also go into the feeds."""
import argparse, json
from datetime import datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

ATOM = "http://www.w3.org/2005/Atom"
ET.register_namespace("atom", ATOM)

class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = self.desc = self.published = self.modified = self.robots = ""
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        key, val = a.get("name") or a.get("property") or "", a.get("content") or ""
        if tag == "title": self.in_title = True
        elif tag == "meta" and key == "description": self.desc = val
        elif tag == "meta" and key == "robots": self.robots = val.lower()
        elif tag == "meta" and key == "article:published_time": self.published = val
        elif tag == "meta" and key == "article:modified_time": self.modified = val
        elif tag == "time" and not self.published: self.published = a.get("datetime", "")
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data

def when(text, fallback):
    try: d = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError: d = fallback
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

def collect(pages, base):
    items = []
    for path in sorted(pages.rglob("*.html")):
        rel = path.relative_to(pages)
        if rel.name.startswith("404") or any(p.startswith(("_", ".")) for p in rel.parts): continue
        m = Meta(); m.feed(path.read_text(encoding="utf-8", errors="replace"))
        if "noindex" in m.robots: continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        url = base + "/" + rel.as_posix().removesuffix("index.html")       # /blog/ rather than /blog/index.html
        items.append({"url": url, "title": m.title.strip() or rel.stem, "summary": m.desc.strip(), "dated": bool(m.published),
                      "published": when(m.published, mtime), "modified": when(m.modified or m.published, mtime)})
    return items

def el(parent, tag, text=None, **attrs):
    e = ET.SubElement(parent, tag, attrs); e.text = text; return e

def save_xml(root, path):
    ET.indent(root); ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

def write_all(items, posts, site, out):
    base = site["base"]
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for i in items:
        u = el(root, "url"); el(u, "loc", i["url"]); el(u, "lastmod", i["modified"].date().isoformat())
    save_xml(root, out / "sitemap.xml")

    root = ET.Element("rss", version="2.0"); ch = el(root, "channel")
    for t in ("title", "description", "language"): el(ch, t, site[t])
    el(ch, "link", base + "/")
    el(ch, f"{{{ATOM}}}link", href=base + "/rss.xml", rel="self", type="application/rss+xml")
    for p in posts:
        i = el(ch, "item"); el(i, "title", p["title"]); el(i, "link", p["url"]); el(i, "guid", p["url"], isPermaLink="true")
        el(i, "pubDate", format_datetime(p["published"])); el(i, "description", p["summary"])
    save_xml(root, out / "rss.xml")

    root = ET.Element("feed", {"xmlns": ATOM, "xml:lang": site["language"]})
    el(root, "title", site["title"]); el(root, "id", base + "/"); el(root, "link", href=base + "/")
    el(root, "link", href=base + "/atom.xml", rel="self")
    el(root, "updated", max((p["modified"] for p in posts), default=datetime.now(timezone.utc)).isoformat())
    for p in posts:
        e = el(root, "entry"); el(e, "title", p["title"]); el(e, "id", p["url"]); el(e, "link", href=p["url"])
        el(e, "updated", p["modified"].isoformat()); el(e, "published", p["published"].isoformat()); el(e, "summary", p["summary"])
    save_xml(root, out / "atom.xml")

    feed = {"version": "https://jsonfeed.org/version/1.1", "title": site["title"], "language": site["language"],
            "home_page_url": base + "/", "feed_url": base + "/feed.json",
            "items": [{"id": p["url"], "url": p["url"], "title": p["title"], "summary": p["summary"],
                       "date_published": p["published"].isoformat(), "date_modified": p["modified"].isoformat()} for p in posts]}
    (out / "feed.json").write_text(json.dumps(feed, indent=2, ensure_ascii=False), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pages", type=Path)
    ap.add_argument("--base-url", required=True, help="https://example.com, trailing slash optional")
    ap.add_argument("--out", type=Path, help="output folder (default: the pages folder)")
    ap.add_argument("--title", default="Latest posts")
    ap.add_argument("--description", default="")
    ap.add_argument("--language", default="en")
    ap.add_argument("--limit", type=int, default=20, help="max feed entries")
    a = ap.parse_args()
    out = a.out or a.pages; out.mkdir(parents=True, exist_ok=True)
    site = {"base": a.base_url.rstrip("/"), "title": a.title, "description": a.description or a.title, "language": a.language}
    items = collect(a.pages, site["base"])
    posts = sorted((i for i in items if i["dated"]), key=lambda i: i["published"], reverse=True)[: a.limit]
    write_all(items, posts, site, out)
    print(f"sitemap.xml: {len(items)} urls; feeds: {len(posts)} entries -> {out}")

if __name__ == "__main__":
    main()
```

```bash
python build_feeds.py dist --base-url https://example.com --title "Example Roasters"   # Windows: py build_feeds.py ...
```

Advertise the feeds in every page `<head>` (a partial is the place) and add `Sitemap: https://example.com/sitemap.xml` to `robots.txt`:

```html
<link rel="alternate" type="application/rss+xml" title="Example Roasters" href="/rss.xml">
```

## Variations

- **Big sites**: a sitemap holds 50,000 URLs at most; beyond that split it and add a `<sitemapindex>`.
- **Only the blog in the feeds**: filter in `main()` with `posts = [i for i in posts if "/blog/" in i["url"]]`.
- **Full content in feeds**: add `<content:encoded>` (RSS) or `content_html` (JSON Feed) from the page's `<article>`; keep the summary for readers that want a short list.

## Pitfalls

- `--base-url` must match the production origin exactly (scheme, `www` or not); a sitemap with the wrong host is ignored by search engines.
- Dates without a time zone are read as UTC; write `2026-03-14T09:00:00+01:00` or `Z` so feed readers order posts correctly.
- Never change a post's URL after publishing: the URL is the RSS `guid`, and readers show it again as a new item.
- The mtime fallback for `<lastmod>` changes on every deploy; add `article:modified_time` for honest values, since crawlers learn to ignore a lastmod that always says today.
- Keep redirects and 404 URLs out of the sitemap; ElementTree escapes `&` in titles, so never build the XML by string concatenation.

## Related skills

- `web-seo-sitemap-robots-urls`
- `web-content-static-blog-generator`
- `web-content-markdown-pipeline`
- `web-content-partials-build`
- `web-page-blog-index`
