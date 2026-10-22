#!/usr/bin/env python3
"""explain_site.py: turn a plain HTML + Tailwind site folder into one self-contained "how this site works" page.

Usage:
  python explain_site.py <folder> [--out explain.html] [--narrative notes.txt] [--title "My site"]

The report has five parts, all derived from the files (nothing is guessed from a framework):
  1. File map           every file with its role and size (node_modules, dist, .git and friends are skipped)
  2. Pages              per page: title, description, h1, sections (tag, id, heading, line), loaded assets, links
  3. Links between pages  who links to whom, orphan pages, broken links and broken #anchors
  4. Where to change what  a lookup table built from what was found (file:line for every row)
  5. Narrative          an empty slot, or the text of --narrative (blank line = new paragraph, "## " = subheading)

Run it, read the output, then write the plain-English story on top and pass it back with --narrative.
Never writes inside <folder>. Standard library only; Windows and Unix. Exit code 0 ok, 2 usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SKIP_DIRS = {"node_modules", "dist", ".git", "build", "_site", ".netlify", ".wrangler", "__pycache__", ".venv", ".next", "coverage", ".cache"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SECTION_TAGS = {"header", "nav", "main", "section", "article", "aside", "footer", "form", "dialog"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico", ".bmp"}
FONT_EXT = {".woff", ".woff2", ".ttf", ".otf"}
BINARY_EXT = IMG_EXT | FONT_EXT | {".mp4", ".webm", ".mp3", ".ogg", ".pdf", ".zip", ".gz", ".wasm", ".mov"}
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.I)


def human(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    for unit in ("KB", "MB", "GB"):
        n /= 1024
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}"
    return f"{n} B"


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def theme_tokens(css: str) -> list[str]:
    """Custom property names declared inside @theme { ... } blocks (brace-balanced)."""
    names: list[str] = []
    for m in re.finditer(r"@theme\b[^{]*\{", css):
        depth, i = 1, m.end()
        while i < len(css) and depth:
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        names += re.findall(r"(--[\w-]+)\s*:", css[m.end():i])
    return names


# ----------------------------------------------------------------------------- HTML parsing

class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = self.title = self.description = ""
        self.headings: list[dict] = []
        self.sections: list[dict] = []
        self.assets: list[dict] = []
        self.links: list[dict] = []
        self.ids: dict[str, int] = {}
        self.inline_styles: list[dict] = []
        self.inline_scripts: list[dict] = []
        self.svg_count = 0
        self.title_line = self.desc_line = 0
        self._stack: list[dict] = []        # open section-like elements
        self._comment = ""
        self._in_title = False
        self._heading: dict | None = None
        self._link: dict | None = None
        self._raw: dict | None = None       # open <style>/<script>

    def line(self) -> int:
        return self.getpos()[0]

    def handle_comment(self, data: str) -> None:
        text = " ".join(data.split())
        self._comment = text if 0 < len(text) <= 90 else ""

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = {k: (v or "") for k, v in attrs}
        ln = self.line()
        if tag in SECTION_TAGS:
            sec = dict(tag=tag, id=a.get("id", ""), label=a.get("aria-label", ""), labelledby=a.get("aria-labelledby", ""),
                       comment=self._comment, heading="", line=ln, depth=len(self._stack))
            self.sections.append(sec)
            self._stack.append(sec)
        self._comment = ""
        if a.get("id"):
            self.ids.setdefault(a["id"], ln)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._in_title, self.title_line = True, ln
        elif tag == "meta" and a.get("name", "").lower() == "description":
            self.description, self.desc_line = a.get("content", ""), ln
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading = dict(level=int(tag[1]), text="", line=ln, id=a.get("id", ""))
            self.headings.append(self._heading)
        elif tag == "a" and "href" in a:
            self._link = dict(href=a["href"].strip(), text="", label=a.get("aria-label", ""), line=ln, kind="link")
            self.links.append(self._link)
        elif tag == "iframe" and a.get("src"):
            self.links.append(dict(href=a["src"].strip(), text=a.get("title", "") or "(embedded frame)", label="", line=ln, kind="embed"))
            self.assets.append(dict(kind="iframe", ref=a["src"].strip(), line=ln))
        elif tag == "link" and a.get("href"):
            rel = a.get("rel", "").lower()
            if any(r in rel for r in ("stylesheet", "icon", "manifest", "modulepreload", "preload")):
                kind = "stylesheet" if "stylesheet" in rel else ("icon" if "icon" in rel else rel.split()[0])
                self.assets.append(dict(kind=kind, ref=a["href"].strip(), line=ln))
        elif tag == "script":
            if a.get("src"):
                self.assets.append(dict(kind="module script" if a.get("type") == "module" else "script", ref=a["src"].strip(), line=ln))
            else:
                self._raw = dict(tag="script", type=a.get("type", ""), line=ln, text="")
        elif tag == "style":
            self._raw = dict(tag="style", type=a.get("type", ""), line=ln, text="")
        elif tag in ("img", "source", "video", "audio", "track") and (a.get("src") or a.get("srcset")):
            ref = a.get("src") or a["srcset"].split(",")[0].split()[0]
            self.assets.append(dict(kind=tag, ref=ref.strip(), line=ln))
            if tag == "img" and self._link is not None and not self._link["text"].strip():
                self._link["text"] = a.get("alt", "")
        elif tag == "svg":
            self.svg_count += 1

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            h, self._heading = self._heading, None
            if h is not None:
                h["text"] = " ".join(h["text"].split())
                if self._stack and not self._stack[-1]["heading"]:
                    self._stack[-1]["heading"] = h["text"]
        elif tag == "a":
            self._link = None
        elif tag in ("script", "style") and self._raw and self._raw["tag"] == tag:
            raw, self._raw = self._raw, None
            (self.inline_scripts if tag == "script" else self.inline_styles).append(raw)
        elif tag in SECTION_TAGS:
            for i in range(len(self._stack) - 1, -1, -1):
                if self._stack[i]["tag"] == tag:
                    del self._stack[i:]
                    break

    def handle_data(self, data: str) -> None:
        if self._raw is not None:
            self._raw["text"] += data
            return
        if self._in_title:
            self.title += data
        if self._heading is not None:
            self._heading["text"] += data
        if self._link is not None:
            self._link["text"] += data

    def finish(self) -> None:
        self.title = " ".join(self.title.split())
        by_id = {h["id"]: h["text"] for h in self.headings if h["id"]}
        for s in self.sections:
            if not s["heading"] and s["labelledby"]:
                s["heading"] = by_id.get(s["labelledby"].split()[0], "")
            s["name"] = s["heading"] or s["label"] or s["comment"] or ""
        for lk in self.links:
            lk["text"] = " ".join(lk["text"].split()) or lk["label"] or "(icon or image link)"


# ----------------------------------------------------------------------------- site model

def file_role(rel: Path, path: Path, text: str | None, root_is_src: bool) -> tuple[str, str]:
    name, ext, parts = rel.name.lower(), rel.suffix.lower(), [p.lower() for p in rel.parts]
    first = ""
    if text:
        for ln in text.splitlines()[:12]:
            m = re.match(r"\s*(?:/\*+|//+|#!?|<!--)\s*(.{8,110}?)\s*(?:\*+/|-->)?\s*$", ln)
            if m and not ln.lstrip().startswith("#!/"):
                first = m.group(1)
                break
    if ext == ".html":
        if name == "404.html":
            return "Page: not-found (404)", "shown by the host for unknown URLs"
        return ("Page: home" if name == "index.html" and len(rel.parts) <= 2 else "Page"), ""
    if ext == ".css":
        if name in ("output.css", "styles.css", "tailwind.css") and text and "tailwindcss v" in text[:400].lower():
            return "Built CSS (generated)", "do not edit; rebuilt from input.css"
        if text and '@import "tailwindcss"' in text.replace("'", '"'):
            n = len(theme_tokens(text))
            return "Tailwind source CSS", f"{n} @theme tokens; edit this for colours, fonts, radii" if n else "imports Tailwind; custom CSS goes here"
        return "Stylesheet", first
    if ext in (".js", ".mjs", ".cjs", ".ts"):
        if "scripts" in parts[:-1]:
            return "Build or tooling script", first
        return "JavaScript (behaviour)", first
    if ext in IMG_EXT:
        return ("Icon" if "icon" in name or ext == ".ico" else "Image"), ""
    if ext in FONT_EXT:
        return "Font file (self-hosted)", ""
    table = {
        "package.json": ("Node manifest", "dependencies and the dev/build commands"),
        "package-lock.json": ("Dependency lockfile", "generated by npm; commit it, never hand-edit"),
        ".gitignore": ("Git ignore list", "files git will not commit"),
        ".editorconfig": ("Editor settings", "indent and line-ending rules"),
        "readme.md": ("Documentation", first),
        "license": ("Licence", ""), "robots.txt": ("Crawler rules", ""), "sitemap.xml": ("Sitemap for search engines", ""),
        "cname": ("Custom domain for GitHub Pages", ""), "_headers": ("Host response headers", "Cloudflare/Netlify"),
        "_redirects": ("Host redirect rules", "Cloudflare/Netlify"), "netlify.toml": ("Netlify config", ""),
        "wrangler.toml": ("Cloudflare config", ""), "wrangler.jsonc": ("Cloudflare config", ""),
        "manifest.webmanifest": ("Web app manifest", ""), "favicon.ico": ("Icon", ""),
    }
    if name in table:
        return table[name]
    if ".github" in parts and ext in (".yml", ".yaml"):
        return "GitHub Actions workflow", "runs on push; builds and deploys" if text and "deploy" in text.lower() else first
    if ext in (".md", ".txt"):
        return "Notes / documentation", first
    if ext == ".json":
        return "JSON data or config", first
    if ext in (".yml", ".yaml", ".toml"):
        return "Config", first
    return "Other", ""


class Site:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.files: list[dict] = []
        self.skipped: list[str] = []
        self.pages: dict[str, Page] = {}
        self.scan()
        src = folder / "src"
        has_src_html = src.is_dir() and any(f["rel"].parts[0] == "src" and f["ext"] == ".html" for f in self.files)
        self.root = src if has_src_html else folder
        self.root_name = "src/" if has_src_html else "./"
        self.parse_pages()
        self.pkg = {}
        if (folder / "package.json").is_file():
            try:
                self.pkg = json.loads(read_text(folder / "package.json"))
            except json.JSONDecodeError:
                pass

    def scan(self) -> None:
        def walk(d: Path) -> None:
            for p in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
                if p.is_dir():
                    if p.name in SKIP_DIRS:
                        self.skipped.append(p.relative_to(self.folder).as_posix() + "/")
                    else:
                        walk(p)
                elif p.is_file():
                    ext = p.suffix.lower()
                    text = None if ext in BINARY_EXT else read_text(p)
                    rel = p.relative_to(self.folder)
                    role, detail = file_role(rel, p, text, False)
                    self.files.append(dict(rel=rel, path=p, ext=ext, size=p.stat().st_size, text=text, role=role, detail=detail,
                                           lines=text.count("\n") + 1 if text else 0,
                                           digest=hashlib.sha1(p.read_bytes()).hexdigest()))
        walk(self.folder)
        seen: dict[str, str] = {}
        for f in self.files:
            if f["size"] and f["digest"] in seen:
                f["duplicate_of"] = seen[f["digest"]]
            else:
                seen[f["digest"]] = f["rel"].as_posix()

    def parse_pages(self) -> None:
        for f in self.files:
            if f["ext"] == ".html" and (self.root == self.folder or self.root in f["path"].parents):
                pg = Page()
                pg.feed(f["text"])
                pg.close()
                pg.finish()
                self.pages[f["path"].relative_to(self.root).as_posix()] = pg
        # file roles for pages carry the title
        for f in self.files:
            if f["ext"] == ".html":
                key = f["path"].relative_to(self.root).as_posix() if self.root in f["path"].parents else None
                if key in self.pages and self.pages[key].title:
                    f["detail"] = self.pages[key].title

    def resolve(self, page_key: str, ref: str) -> tuple[str, str] | None:
        """Return (kind, target) for a link: ('page', key) | ('file', rel) | ('anchor', id) | ('external', url) | ('missing', path)."""
        if ref.startswith("#"):
            return ("anchor", ref[1:])
        if EXTERNAL.match(ref):
            return ("external", ref)
        if ref.startswith("{") or not ref:
            return None
        path = ref.split("#")[0].split("?")[0]
        if not path:
            return ("anchor", "")
        page_path = self.root / page_key
        target = (self.root / path.lstrip("/")) if path.startswith("/") else (page_path.parent / path)
        if path.endswith("/"):
            target = target / "index.html"
        try:
            target = target.resolve()
            rel = target.relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return ("missing", path)
        if target.is_file():
            return ("page" if target.suffix.lower() == ".html" else "file", rel)
        if (target.with_suffix(".html")).is_file() and not target.suffix:
            return ("page", target.with_suffix(".html").relative_to(self.root.resolve()).as_posix())
        return ("missing", path)

    def builds_css(self) -> bool:
        return "build" in (self.pkg.get("scripts") or {})


# ----------------------------------------------------------------------------- report sections

def e(s: object) -> str:
    return html.escape(str(s), quote=True)


def code(s: object) -> str:
    return f"<code>{e(s)}</code>"


def table(head: list[str], rows: list[list[str]], cls: str = "") -> str:
    if not rows:
        return '<p class="muted">Nothing found.</p>'
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def file_map(site: Site) -> str:
    rows = []
    for f in site.files:
        note = e(f["detail"]) if f["detail"] else ""
        if f.get("duplicate_of"):
            note += (" " if note else "") + f'<span class="tag warn">byte-identical to {e(f["duplicate_of"])}</span>'
        size = human(f["size"]) + (f' <span class="muted">· {f["lines"]} lines</span>' if f["lines"] else "")
        rows.append([code(f["rel"].as_posix()), e(f["role"]), size, note])
    total = sum(f["size"] for f in site.files)
    out = f"<p>{len(site.files)} files, {human(total)} in total."
    if site.skipped:
        out += " Not listed (generated or vendored): " + ", ".join(code(s) for s in site.skipped) + "."
    return out + "</p>" + table(["File", "Role", "Size", "Notes"], rows)


def asset_row(site: Site, key: str, a: dict) -> list[str]:
    res = site.resolve(key, a["ref"])
    ref = a["ref"]
    if res is None:
        return [e(a["kind"]), code(ref), "template placeholder", str(a["line"])]
    kind, target = res
    if kind == "external":
        host = re.sub(r"^(?:https?:)?//", "", ref).split("/")[0]
        what = "CDN: Tailwind Play CDN (runs in the browser, no build step)" if "tailwindcss/browser" in ref else (
            "Google Fonts" if "fonts.g" in host else f"external: {host}")
        return [e(a["kind"]), code(ref if len(ref) < 90 else ref[:87] + "..."), e(what), str(a["line"])]
    if kind in ("page", "file"):
        size = next((f["size"] for f in site.files if f["path"].resolve() == (site.root / target).resolve()), 0)
        return [e(a["kind"]), code(ref), f"local, {human(size)}", str(a["line"])]
    if kind == "missing":
        built = site.builds_css() and Path(ref).name.lower() in ("output.css", "styles.css", "tailwind.css") or ref.startswith("./output")
        return [e(a["kind"]), code(ref), '<span class="tag ok">written by the build step</span>' if built else '<span class="tag bad">file not found</span>', str(a["line"])]
    return [e(a["kind"]), code(ref), "", str(a["line"])]


def pages_section(site: Site) -> str:
    out = []
    for key, pg in site.pages.items():
        h1s = [h for h in pg.headings if h["level"] == 1]
        bits = [f"<p>{e(pg.description)}</p>" if pg.description else '<p class="muted">No meta description.</p>']
        dl = [("Title", pg.title or "(none)"), ("h1", " / ".join(h["text"] for h in h1s) or "(none)"), ("Language", pg.lang or "(not set)"),
              ("Lines", str(next((f["lines"] for f in site.files if f["path"].resolve() == (site.root / key).resolve()), 0)))]
        bits.append("<dl>" + "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in dl) + "</dl>")
        # sections
        srows = []
        for s in pg.sections:
            indent = "&emsp;" * s["depth"]
            what = s["name"] or '<span class="muted">(no heading or label)</span>'
            srows.append([f"{indent}{code('<' + s['tag'] + '>')}", code("#" + s["id"]) if s["id"] else "", e(what) if s["name"] else what,
                          e(s["comment"]) if s["comment"] and s["comment"] != s["name"] else "", str(s["line"])])
        bits.append("<h4>Sections</h4>" + table(["Element", "id", "Heading or label", "Author's comment", "Line"], srows))
        # assets
        arows = [asset_row(site, key, a) for a in pg.assets]
        for st in pg.inline_styles:
            n = len(theme_tokens(st["text"]))
            arows.append(["inline style", code(f"<style{(' type=' + chr(34) + st['type'] + chr(34)) if st['type'] else ''}>"),
                          f"{st['text'].count(chr(10))} lines" + (f", {n} @theme tokens" if n else ""), str(st["line"])])
        for sc in pg.inline_scripts:
            if sc["type"] in ("application/ld+json", "importmap"):
                arows.append(["inline data", code(sc["type"]), "", str(sc["line"])])
            else:
                arows.append(["inline script", code("<script" + (f' type="{sc["type"]}"' if sc["type"] else "") + ">"),
                              f"{max(sc['text'].count(chr(10)) - 1, 0)} lines of JavaScript", str(sc["line"])])
        if pg.svg_count:
            arows.append(["inline svg", f"{pg.svg_count} icons or illustrations", "drawn in the HTML, no file", ""])
        bits.append("<h4>Loaded assets</h4>" + table(["Kind", "Reference", "Where it comes from", "Line"], arows))
        # links
        lrows, counts = [], {"page": 0, "anchor": 0, "external": 0, "other": 0}
        for lk in pg.links:
            res = site.resolve(key, lk["href"])
            if res is None:
                continue
            kind, target = res
            if kind == "anchor" and target and target not in pg.ids:
                status = '<span class="tag bad">no element with that id</span>'
            elif kind == "missing":
                status = '<span class="tag bad">target not found</span>'
            else:
                status = ""
            counts[kind if kind in counts else "other"] += 1
            dest = {"page": f"page {target}", "anchor": "this page, #" + target if target else "top of this page", "external": target,
                    "file": f"file {target}", "missing": lk["href"]}[kind]
            lrows.append([e(lk["text"][:60]) + (' <span class="tag">embed</span>' if lk["kind"] == "embed" else ""), code(lk["href"]), e(dest), status, str(lk["line"])])
        summary = f'{counts["page"]} to other pages, {counts["anchor"]} in-page anchors, {counts["external"]} external'
        bits.append(f"<h4>Links <span class='muted'>({summary})</span></h4>" +
                    (f"<details><summary>Show all {len(lrows)} links</summary>{table(['Text', 'href', 'Goes to', 'Status', 'Line'], lrows)}</details>" if lrows else '<p class="muted">No links.</p>'))
        out.append(f'<section class="card" id="page-{e(re.sub(r"[^a-z0-9]+", "-", key.lower()))}"><h3>{code(key)}</h3>{"".join(bits)}</section>')
    return "".join(out) or '<p class="muted">No .html pages found.</p>'


def links_section(site: Site) -> str:
    edges: dict[tuple[str, str], list[str]] = {}
    problems: list[list[str]] = []
    for key, pg in site.pages.items():
        for lk in pg.links:
            res = site.resolve(key, lk["href"])
            if not res:
                continue
            kind, target = res
            if kind == "page":
                edges.setdefault((key, target), []).append(lk["text"][:40])
            elif kind == "missing":
                problems.append([code(key), code(lk["href"]), "target file not found", str(lk["line"])])
            elif kind == "anchor" and target and target not in pg.ids:
                problems.append([code(key), code("#" + target), "no element with that id on this page", str(lk["line"])])
    keys = list(site.pages)
    out = []
    if len(keys) > 1:
        head = ["from \\ to"] + [e(k) for k in keys]
        rows = []
        for a in keys:
            row = [code(a)]
            for b in keys:
                n = len(edges.get((a, b), []))
                row.append("self" if a == b else (f'<b>{n}</b>' if n else '<span class="muted">·</span>'))
            rows.append(row)
        out.append("<h4>Matrix (number of links)</h4>" + table(head, rows, "matrix"))
    rows = [[code(a), code(b), str(len(t)), e(", ".join(dict.fromkeys(t))[:90])] for (a, b), t in sorted(edges.items())]
    out.append("<h4>Every link between pages</h4>" + table(["From", "To", "Count", "Link text"], rows))
    linked = {b for (_, b) in edges}
    orphans = [k for k in keys if k not in linked and k != "index.html"]
    entry = [k for k in keys if k == "index.html"]
    out.append("<h4>Pages nothing links to</h4>" + (
        "<ul>" + "".join(f"<li>{code(k)}: reachable only by typing the URL" + (" or via a hosting rule (a 404 page is normal)" if k == "404.html" else "") + ".</li>" for k in orphans) + "</ul>"
        if orphans else '<p class="muted">None: every page is linked from another page' + (f" (entry point: {code(entry[0])})." if entry else ".") + "</p>"))
    out.append("<h4>Broken links and anchors</h4>" + (table(["Page", "Link", "Problem", "Line"], problems) if problems else '<p><span class="tag ok">none</span> every internal link and #anchor resolves.</p>'))
    ext: dict[str, int] = {}
    for key, pg in site.pages.items():
        for lk in pg.links:
            if EXTERNAL.match(lk["href"]) and not lk["href"].startswith(("mailto:", "tel:")):
                host = re.sub(r"^(?:https?:)?//", "", lk["href"]).split("/")[0]
                ext[host] = ext.get(host, 0) + 1
    if ext:
        out.append("<h4>External sites linked</h4>" + table(["Host", "Links"], [[code(h), str(n)] for h, n in sorted(ext.items(), key=lambda x: -x[1])]))
    return "".join(out)


def where_to_change(site: Site) -> str:
    pages = site.pages
    rows: list[list[str]] = []

    def at(items: list[tuple[str, int]]) -> str:
        return ", ".join(code(f"{k}:{n}") for k, n in items)

    def pagelist(fn) -> list[tuple[str, int]]:
        return [(k, fn(p)) for k, p in pages.items() if fn(p)]

    rows.append(["Page title (browser tab, search results)", at(pagelist(lambda p: p.title_line)), "one <title> per page; keep each under ~60 characters"])
    rows.append(["Search-result description", at(pagelist(lambda p: p.desc_line)) or "no page has a meta description yet", "one <meta name=\"description\"> per page"])

    themes = []
    for f in site.files:
        if f["ext"] == ".css" and f["text"] and theme_tokens(f["text"]):
            m = re.search(r"@theme\b", f["text"])
            themes.append((f["rel"].as_posix(), f["text"][:m.start()].count("\n") + 1, len(theme_tokens(f["text"]))))
    for k, p in pages.items():
        for st in p.inline_styles:
            n = len(theme_tokens(st["text"]))
            if n:
                themes.append((k, st["line"] + st["text"][:re.search(r"@theme\b", st["text"]).start()].count("\n"), n))
    if themes:
        rows.append(["Colours, fonts, radii, type scale (design tokens)", ", ".join(f"{code(f'{a}:{b}')} ({n} tokens)" for a, b, n in themes),
                     "edit the values inside @theme { ... }; classes like bg-accent follow automatically"])
    else:
        rows.append(["Colours, fonts, radii", "no @theme block found", "colours are Tailwind's defaults, written as classes (bg-blue-600) on each element, so change them where they are used"])

    cdn = [k for k, p in pages.items() if any("tailwindcss/browser" in a["ref"] for a in p.assets)]
    if cdn:
        rows.append(["How Tailwind runs", f"Play CDN script in {len(cdn)} of {len(pages)} pages", "styles are computed in the browser; no build step. For production switch to @tailwindcss/cli (web-ship-tailwind-production)"])
    elif site.builds_css():
        rows.append(["How Tailwind runs", code("package.json") + " scripts", "the CLI reads the source CSS and writes output.css; run " + code("npm run build") + " after changes"])

    for tag, label in (("nav", "Navigation links"), ("header", "Site header / logo"), ("footer", "Footer links and legal line")):
        found = [(k, s["line"]) for k, p in pages.items() for s in p.sections if s["tag"] == tag and s["depth"] <= 1]
        if found:
            note = f"repeated in {len({k for k, _ in found})} files: edit every copy" if len({k for k, _ in found}) > 1 else "one copy"
            rows.append([label, at(found), note])

    for k, p in pages.items():
        named = [s for s in p.sections if s["tag"] in ("section", "article") and (s["name"] or s["id"])]
        if named:
            items = "; ".join(f"{e((s['name'] or '#' + s['id'])[:48])} " + code(f"line {s['line']}") for s in named[:10])
            more = f"; and {len(named) - 10} more (see the Sections table)" if len(named) > 10 else ""
            rows.append([f"Text, images and layout of a section in {k}", code(k) + ": " + items + more, e("each block is one <section>; ids such as ") + (code("#" + next(s["id"] for s in named if s["id"])) if any(s["id"] for s in named) else code("#id")) + e(" are the targets of nav links")])

    scripts = []
    for k, p in pages.items():
        scripts += [(k, sc["line"]) for sc in p.inline_scripts if sc["type"] not in ("application/ld+json", "importmap")]
    js_files = [f["rel"].as_posix() for f in site.files if f["ext"] in (".js", ".mjs") and "scripts" not in f["rel"].parts[:-1]]
    if scripts or js_files:
        rows.append(["Behaviour (menu toggle, tabs, forms)", ", ".join([code(j) for j in js_files] + ([at(scripts)] if scripts else [])), "inline scripts live inside the page; files in js/ are shared by every page that loads them"])
    imgs = sorted({a["ref"] for p in pages.values() for a in p.assets if a["kind"] == "img"})
    if imgs:
        rows.append(["Images", ", ".join(code(i) for i in imgs[:6]) + (" ..." if len(imgs) > 6 else ""), "swap the file, keep alt text accurate"])
    elif any(p.svg_count for p in pages.values()):
        rows.append(["Icons and illustrations", "inline svg elements in the HTML", "no image files: edit the path data or replace the <svg> block"])
    fonts = sorted({a["ref"] for p in pages.values() for a in p.assets if "fonts.googleapis.com/css" in a["ref"]})
    if fonts:
        rows.append(["Fonts", at(pagelist(lambda p: next((a["line"] for a in p.assets if "fonts.googleapis.com/css" in a["ref"]), 0))), "change the family in the Google Fonts URL, then the matching --font-* token"])
    hosts = [f["rel"].as_posix() for f in site.files if ".github" in f["rel"].parts and f["ext"] in (".yml", ".yaml")]
    if hosts:
        rows.append(["Deploy settings", ", ".join(code(h) for h in hosts), "what runs on every push to main"])
    if site.pkg:
        rows.append(["Build and dev commands, dependencies", code("package.json"), "scripts: " + (", ".join(site.pkg.get("scripts", {})) or "none")])
    rows.append(["Add a new page", "copy an existing page", "then add its link to the navigation and footer in every page that has them (see the link matrix)"])
    return table(["To change...", "Look at", "Notes"], [[e(r[0]), r[1], r[2] if "<code>" in r[2] else e(r[2])] for r in rows])


def narrative_html(path: str | None) -> str:
    if not path:
        return '<!-- NARRATIVE: write the plain-English tour here, or run again with --narrative notes.txt -->\n<p class="muted">No narrative yet. Run the script again with <code>--narrative notes.txt</code> to put the plain-English tour here.</p>'
    out = []
    for block in re.split(r"\n\s*\n", read_text(Path(path)).strip()):
        block = block.strip()
        if block.startswith("## "):
            head, _, rest = block[3:].partition("\n")
            out.append(f"<h3>{e(head.strip())}</h3>")
            block = rest.strip()
        if block:
            out.append(f"<p>{e(block)}</p>")
    return "".join(out)


CSS = """
:root{--bg:#faf8f4;--fg:#1d1b18;--mut:#6a655d;--line:#ddd7cc;--card:#fff;--accent:#8a4b2a;--ok:#1d6b47;--bad:#a3281e;--warn:#8a6100;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--bg:#161412;--fg:#ece7de;--mut:#9d968a;--line:#332f2a;--card:#1d1a17;--accent:#e0a37f;--ok:#6fcf9b;--bad:#ff8f84;--warn:#e6b84d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,sans-serif;padding:0 clamp(16px,4vw,48px)}
main{max-width:1100px;margin:0 auto;padding:32px 0 64px}h1{font:600 2rem/1.15 Georgia,serif;margin:0 0 4px}h2{font:600 1.35rem/1.2 Georgia,serif;margin:44px 0 12px;padding-top:16px;border-top:1px solid var(--line)}
h3{margin:0 0 8px;font-size:1.05rem}h4{margin:20px 0 6px;font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut)}
code{font:12.5px ui-monospace,Consolas,monospace;background:color-mix(in srgb,var(--line) 45%,transparent);padding:1px 5px;border-radius:3px;overflow-wrap:anywhere}
.muted{color:var(--mut)}.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{text-align:left;vertical-align:top;padding:7px 10px;border-bottom:1px solid var(--line)}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);white-space:nowrap}tr:last-child td{border-bottom:0}
.matrix td,.matrix th{text-align:center}.matrix td:first-child,.matrix th:first-child{text-align:left}
.card{border:1px solid var(--line);border-radius:8px;background:var(--card);padding:16px 18px;margin:0 0 16px}
dl{display:grid;grid-template-columns:max-content 1fr;gap:2px 16px;margin:8px 0;font-size:14px}dt{color:var(--mut)}dd{margin:0}
.tag{font-size:11px;padding:1px 7px;border-radius:99px;border:1px solid var(--line);white-space:nowrap}.tag.ok{color:var(--ok);border-color:currentColor}.tag.bad{color:var(--bad);border-color:currentColor}.tag.warn{color:var(--warn);border-color:currentColor}
.stats{display:flex;flex-wrap:wrap;gap:10px 28px;margin:16px 0}.stats b{display:block;font:600 1.5rem Georgia,serif}.stats span{font-size:12px;color:var(--mut)}
summary{cursor:pointer;color:var(--accent);margin:6px 0}nav.toc{display:flex;flex-wrap:wrap;gap:6px 18px;margin:12px 0}nav.toc a{color:var(--accent)}
.narr{max-width:68ch}.narr h3{margin-top:22px}
"""


def build_report(site: Site, title: str, narrative: str | None) -> str:
    n_links = sum(len(p.links) for p in site.pages.values())
    stats = [(str(len(site.files)), "files"), (str(len(site.pages)), "pages"), (human(sum(f["size"] for f in site.files)), "total size"),
             (str(n_links), "links"), (str(sum(len(p.sections) for p in site.pages.values())), "sections")]
    stat_html = '<div class="stats">' + "".join(f"<div><b>{e(a)}</b><span>{e(b)}</span></div>" for a, b in stats) + "</div>"
    toc = '<nav class="toc"><a href="#narrative">Tour</a><a href="#files">File map</a><a href="#pages">Pages</a><a href="#links">Links between pages</a><a href="#change">Where to change what</a></nav>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}: how it works</title>
<style>{CSS}</style>
</head>
<body>
<main>
<p class="muted">Site tour, generated by explain_site.py from <code>{e(site.folder.name)}/</code> (pages read from <code>{e(site.root_name)}</code>)</p>
<h1>{e(title)}: how it works</h1>
{stat_html}{toc}
<h2 id="narrative">Plain-English tour</h2>
<div class="narr">{narrative_html(narrative)}</div>
<h2 id="files">File map</h2>
{file_map(site)}
<h2 id="pages">Pages</h2>
{pages_section(site)}
<h2 id="links">Links between pages</h2>
{links_section(site)}
<h2 id="change">Where to change what</h2>
{where_to_change(site)}
</main>
</body>
</html>
"""


def guess_title(site: Site) -> str:
    name = site.pkg.get("name") if site.pkg else ""
    home = site.pages.get("index.html")
    if home and home.title:
        t = re.split(r"\s[:–—|-]\s|:\s", home.title)[0].strip()
        if t:
            return t
    return (name or site.folder.name).replace("-", " ").title()


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Explain a plain HTML + Tailwind site folder as one HTML page.")
    ap.add_argument("folder")
    ap.add_argument("--out", default="explain.html", help="report file to write (default ./explain.html; never inside the site if you can avoid it)")
    ap.add_argument("--narrative", help="text file with the plain-English tour: blank line = new paragraph, '## ' = subheading")
    ap.add_argument("--title", help="site name for the heading (default: taken from the home page title)")
    a = ap.parse_args(argv)
    folder = Path(a.folder).resolve()
    if not folder.is_dir():
        print(f"error: {folder} is not a folder", file=sys.stderr)
        return 2
    if a.narrative and not Path(a.narrative).is_file():
        print(f"error: {a.narrative} not found", file=sys.stderr)
        return 2
    site = Site(folder)
    report = build_report(site, a.title or guess_title(site), a.narrative)
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    broken = sum(1 for k, p in site.pages.items() for lk in p.links
                 if (r := site.resolve(k, lk["href"])) and (r[0] == "missing" or (r[0] == "anchor" and r[1] and r[1] not in p.ids)))
    print(f"{folder.name}: {len(site.files)} files, {len(site.pages)} pages, {sum(len(p.links) for p in site.pages.values())} links, {broken} broken")
    for k, p in site.pages.items():
        print(f"  {k:<24} {p.title[:60] or '(no title)'}  [{len(p.sections)} sections, {len(p.assets)} assets, {len(p.links)} links]")
    dups = [f for f in site.files if f.get("duplicate_of")]
    for f in dups:
        print(f"  note: {f['rel'].as_posix()} is byte-identical to {f['duplicate_of']}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
