#!/usr/bin/env python3
"""site_audit.py: audit a folder of HTML files or a live URL and write one HTML report page.

Usage:
  python site_audit.py dist/                          # every .html under a folder
  python site_audit.py https://example.com            # that page plus same-origin pages linked from it (max 20)
  python site_audit.py dist/ --out report.html        # where to write the report (default: site-audit.html in the cwd)
  python site_audit.py dist/ --max-pages 50 --json    # findings as JSON on stdout (summary goes to stderr)

Per page it checks:
  - the pack's vibe check (skills/web-craft-consistency-audit/scripts/vibe_check.py, located relative to this file)
  - broken internal links, missing anchor targets and missing local files (scripts, stylesheets, images, iframes)
  - images without alt, without width+height (or a CSS size class), or over 300 KB
  - WCAG contrast of inline style colours: color against the element's own or nearest ancestor's inline
    background (hex, rgb(), rgba(); Tailwind classes and stylesheets are not resolved)
  - title, meta description, viewport, canonical and <html lang>: present once, not duplicated
  - heading outline: exactly one h1, no skipped levels, no empty headings
  - form controls without a label
  - total page weight (HTML plus local or same-origin resources)
Findings are error / warning / info. Score per page = 100 - 10 per error - 3 per warning.
Exit code 1 when any page has an error-level finding, so it can gate a deploy.
Standard library only; Python 3.10+; Windows and Unix.
"""
from __future__ import annotations

import html as html_mod
import importlib.util
import json
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_EXT = (".pdf", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".mp4", ".webm", ".mp3",
            ".css", ".js", ".json", ".xml", ".txt", ".ico", ".woff", ".woff2")
IMG_LIMIT = 300 * 1024
PAGE_LIMIT = 1500 * 1024
UA = {"User-Agent": "Mozilla/5.0 (compatible; site-audit/1.0)"}


# ----------------------------------------------------------------------------- parsing
class PageParser(HTMLParser):
    """Collects everything the checks need in one pass."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.html_attrs: dict | None = None
        self.title_count = 0
        self.titles: list[str] = []
        self.metas: list[dict] = []
        self.link_tags: list[dict] = []
        self.headings: list[tuple[int, str, int]] = []
        self.imgs: list[tuple[dict, int]] = []
        self.anchors: list[tuple[str, int]] = []
        self.controls: list[dict] = []
        self.labels_for: set[str] = set()
        self.ids: set[str] = set()
        self.inline_styles: list[tuple[str, str, str | None, int]] = []  # (tag, style, inherited inline bg, line)
        self.bg_stack: list[str | None] = []  # inline background per open element, parallel to self.stack
        self.resources: list[tuple[str, str, int]] = []  # (kind, url, line)
        self._capture: list[tuple[str, list[str]]] = []
        self._in_label = 0

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a: dict = {}
        for k, v in attrs:
            a.setdefault(k, v if v is not None else "")
        line = self.getpos()[0]
        if "id" in a and a["id"]:
            self.ids.add(a["id"])
        if tag == "html":
            self.html_attrs = a
        elif tag == "title" and "svg" not in self.stack:
            self.title_count += 1
            self._capture.append(("title", []))
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.link_tags.append(a)
            rels = (a.get("rel") or "").lower().split()
            if "stylesheet" in rels and a.get("href"):
                self.resources.append(("stylesheet", a["href"], line))
            elif "icon" in rels and a.get("href"):
                self.resources.append(("icon", a["href"], line))
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._capture.append((tag, []))
        elif tag == "img":
            self.imgs.append((a, line))
            if a.get("src"):
                self.resources.append(("image", a["src"], line))
        elif tag == "a" and a.get("href") is not None:
            self.anchors.append((a["href"], line))
        elif tag == "script" and a.get("src"):
            self.resources.append(("script", a["src"], line))
        elif tag in ("source", "video", "audio") and a.get("src"):
            self.resources.append(("media", a["src"], line))
        elif tag == "iframe" and a.get("src"):
            self.resources.append(("iframe", a["src"], line))
        elif tag == "label":
            self._in_label += 1
            if a.get("for"):
                self.labels_for.add(a["for"])
        elif tag in ("input", "select", "textarea"):
            typ = (a.get("type") or "text").lower()
            if not (tag == "input" and typ in ("hidden", "submit", "button", "reset", "image")):
                self.controls.append({"tag": tag, "type": typ, "attrs": a, "line": line, "in_label": self._in_label > 0})
        if tag == "img" and self._capture and a.get("alt"):
            self._capture[-1][1].append(a["alt"])  # an image with alt inside a heading is the heading's text
        # background this element paints: an inline colour, UNKNOWN for a gradient/image or a Tailwind bg-* class
        # (classes are not resolved), or None when it paints nothing and the parent's background shows through
        own_bg = style_colours(a["style"])[1] if a.get("style") else None
        if own_bg is None and any(CLASS_BG_RE.match(c) for c in (a.get("class") or "").split()):
            own_bg = UNKNOWN
        if a.get("style"):
            effective = own_bg or next((b for b in reversed(self.bg_stack) if b), None)
            self.inline_styles.append((tag, a["style"], effective, line))
        if tag not in VOID:
            self.stack.append(tag)
            self.bg_stack.append(own_bg)

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self._in_label:
            self._in_label -= 1
        if self._capture and self._capture[-1][0] == tag:
            kind, buf = self._capture.pop()
            text = re.sub(r"\s+", " ", "".join(buf)).strip()
            if kind == "title":
                self.titles.append(text)
            else:
                self.headings.append((int(kind[1]), text, self.getpos()[0]))
        if tag in self.stack:
            idx = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[idx:]
            del self.bg_stack[idx:]

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._capture[-1][1].append(data)


# ----------------------------------------------------------------------------- helpers
def hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    h = value.strip().lstrip("#")
    if len(h) == 3 or len(h) == 4:
        h = "".join(c * 2 for c in h[:3])
    if len(h) == 8:
        h = h[:6]
    if len(h) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        return None
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def luminance(rgb: tuple[int, int, int]) -> float:
    def ch(c: int) -> float:
        v = c / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: tuple, bg: tuple) -> float:
    lf, lb = luminance(fg), luminance(bg)
    hi, lo = max(lf, lb), min(lf, lb)
    return (hi + 0.05) / (lo + 0.05)


COLOUR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)", re.I)
UNKNOWN = "?"  # a background that cannot be measured (gradient, image, utility class)
# an unprefixed Tailwind background-colour utility (bg-white, bg-brand-600, bg-[#111]), not bg-cover/bg-clip-text/...
CLASS_BG_RE = re.compile(r"bg-(?!(?:clip|cover|contain|center|fixed|local|scroll|repeat|no-repeat|origin|blend|none|"
                         r"transparent|auto|top|bottom|left|right|gradient|linear|radial|conic)\b)[\w\[#]")


def parse_colour(value: str) -> tuple[int, int, int] | None:
    """#rgb, #rrggbb, #rgba, #rrggbbaa, rgb(r g b), rgba(r, g, b, a). Translucent colours (alpha < 1) return None:
    their contrast depends on whatever is painted behind them."""
    value = value.strip()
    if value.startswith("#"):
        h = value[1:]
        if (len(h) == 4 and h[3].lower() != "f") or (len(h) == 8 and h[6:].lower() != "ff"):
            return None
        return hex_to_rgb(value)
    nums = re.findall(r"[\d.]+%?", value)
    if len(nums) < 3:
        return None
    if len(nums) >= 4:
        a = nums[3]
        if (float(a[:-1]) / 100 if a.endswith("%") else float(a)) < 1:
            return None
    rgb = [max(0, min(255, round(float(n[:-1]) * 2.55 if n.endswith("%") else float(n)))) for n in nums[:3]]
    return rgb[0], rgb[1], rgb[2]


def style_colours(style: str) -> tuple[str | None, str | None]:
    """(color, background colour) as written in an inline style attribute; None where absent."""
    fg = bg = None
    for decl in style.split(";"):
        if ":" not in decl:
            continue
        prop, _, val = decl.partition(":")
        prop = prop.strip().lower()
        if prop not in ("color", "background", "background-color"):
            continue
        if prop == "background" and re.search(r"gradient|url\(|var\(", val, re.I):
            bg = UNKNOWN  # a gradient or image has no single colour to measure against
            continue
        m = COLOUR_RE.search(val)
        if not m:
            continue
        if prop == "color":
            fg = m.group(0)
        else:
            bg = m.group(0)
    return fg, bg


def fmt_kb(n: int) -> str:
    if n < 10 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def is_external(href: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href)) or href.startswith("//")


def load_vibe_check():
    here = Path(__file__).resolve()
    candidate = here.parents[2] / "web-craft-consistency-audit" / "scripts" / "vibe_check.py"
    if not candidate.is_file():
        return None
    spec = importlib.util.spec_from_file_location("vibe_check", candidate)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------- page model
@dataclass
class Page:
    name: str            # display name (relative path or URL)
    html: str
    size: int
    path: Path | None    # local file, folder mode
    url: str | None      # absolute URL, URL mode
    parsed: PageParser = field(default_factory=PageParser)
    findings: list[dict] = field(default_factory=list)
    weight: int = 0
    vibe: str = "n/a"

    def add(self, severity: str, check: str, message: str, line: int | None = None) -> None:
        self.findings.append({"severity": severity, "check": check, "message": message, "line": line})

    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f["severity"] == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f["severity"] == "warning")

    @property
    def score(self) -> int:
        return max(0, 100 - 10 * self.errors - 3 * self.warnings)


class Fetcher:
    """Tiny caching HTTP client for URL mode."""

    def __init__(self) -> None:
        self.cache: dict[str, tuple[int | None, bytes, str]] = {}

    def get(self, url: str, timeout: int = 15) -> tuple[int | None, bytes, str]:
        if url in self.cache:
            return self.cache[url]
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                result = (r.status, r.read(), r.headers.get("Content-Type", ""))
        except urllib.error.HTTPError as e:
            result = (e.code, b"", "")
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            result = (None, b"", "")
        self.cache[url] = result
        return result

    def status(self, url: str) -> int | None:
        """HEAD, falling back to GET when the server refuses HEAD."""
        if url in self.cache:
            return self.cache[url][0]
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA, method="HEAD"), timeout=15) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if e.code not in (403, 405, 501):
                return e.code
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            return None
        return self.get(url)[0]


# ----------------------------------------------------------------------------- collection
def collect_folder(root: Path) -> list[Page]:
    pages = []
    for p in sorted(root.rglob("*.html")):
        html = p.read_text(encoding="utf-8", errors="replace")
        pages.append(Page(name=p.relative_to(root).as_posix(), html=html, size=p.stat().st_size, path=p, url=None))
    return pages


def collect_url(start: str, fetcher: Fetcher, max_pages: int) -> list[Page]:
    origin = urllib.parse.urlsplit(start)
    queue, seen, pages = [start], set(), []
    while queue and len(pages) < max_pages:
        url = queue.pop(0)
        clean = urllib.parse.urlsplit(url)._replace(fragment="", query="").geturl()
        if clean in seen:
            continue
        seen.add(clean)
        status, body, ctype = fetcher.get(clean)
        if status is None or status >= 400 or "html" not in ctype.lower():
            if url == start:
                sys.exit(f"could not fetch {start} (status {status}, content-type {ctype!r})")
            continue
        html = body.decode("utf-8", errors="replace")
        pages.append(Page(name=clean, html=html, size=len(body), path=None, url=clean))
        for href, _ in parse(html).anchors:
            if is_external(href) and not href.startswith(("http://", "https://")):
                continue
            absolute = urllib.parse.urljoin(clean, href)
            parts = urllib.parse.urlsplit(absolute)
            if (parts.scheme, parts.netloc) == (origin.scheme, origin.netloc) and not parts.path.lower().endswith(SKIP_EXT):
                queue.append(absolute)
    return pages


def parse(html: str) -> PageParser:
    p = PageParser()
    p.feed(html)
    p.close()
    return p


# ----------------------------------------------------------------------------- checks
def check_page(page: Page, pages: list[Page], root: Path | None, fetcher: Fetcher | None, vibe_mod) -> None:
    d = page.parsed  # main() parses every page first, so links can look up ids on other pages
    by_path = {p.path.resolve(): p for p in pages if p.path}
    by_url = {p.url: p for p in pages if p.url}

    # ---- document metadata
    lang = (d.html_attrs or {}).get("lang", "")
    if d.html_attrs is None or not lang.strip():
        page.add("error", "lang", "<html> has no lang attribute; screen readers pick the wrong voice and translation tools guess")
    if d.title_count == 0:
        page.add("error", "title", "no <title>; the tab, bookmarks and search results have nothing to show")
    elif d.title_count > 1:
        page.add("error", "title", f"{d.title_count} <title> elements; keep one")
    elif d.titles and not d.titles[0]:
        page.add("error", "title", "<title> is empty")
    elif d.titles and len(d.titles[0]) > 70:
        page.add("warning", "title", f"<title> is {len(d.titles[0])} characters; search results cut it around 60")

    def metas_named(name: str) -> list[dict]:
        return [m for m in d.metas if (m.get("name") or "").lower() == name]

    desc = metas_named("description")
    if not desc:
        page.add("warning", "description", 'no <meta name="description">; search engines will invent one')
    elif len(desc) > 1:
        page.add("warning", "description", f"{len(desc)} description metas; keep one")
    elif len(desc[0].get("content", "")) < 40:
        page.add("warning", "description", "meta description is shorter than 40 characters")
    viewport = metas_named("viewport")
    if not viewport:
        page.add("error", "viewport", 'no <meta name="viewport">; phones render the page at desktop width and zoom out')
    elif len(viewport) > 1:
        page.add("warning", "viewport", f"{len(viewport)} viewport metas; keep one")
    canon = [l for l in d.link_tags if "canonical" in (l.get("rel") or "").lower().split()]
    if not canon:
        page.add("info", "canonical", 'no <link rel="canonical">; add one before launch if the page is reachable under more than one URL')
    elif len(canon) > 1:
        page.add("error", "canonical", f"{len(canon)} canonical links; search engines ignore conflicting canonicals")

    # ---- heading outline
    h1s = [h for h in d.headings if h[0] == 1]
    if not h1s:
        page.add("error", "headings", "no <h1>; every page needs exactly one")
    elif len(h1s) > 1:
        page.add("warning", "headings", f"{len(h1s)} <h1> elements (lines {', '.join(str(h[2]) for h in h1s)}); keep one")
    prev = 0
    for level, text, line in d.headings:
        if not text:
            page.add("warning", "headings", f"empty <h{level}>", line)
        if prev and level > prev + 1:
            page.add("warning", "headings", f"heading level skipped: <h{prev}> followed by <h{level}> {text[:40]!r}", line)
        prev = level

    # ---- images
    for attrs, line in d.imgs:
        src = attrs.get("src", "")
        if "alt" not in attrs:
            page.add("error", "images", f"<img> without alt attribute: {src[:80]}", line)
        classes = (attrs.get("class") or "").split()
        sized_by_css = any(c.startswith(("aspect-", "size-")) for c in classes) or (
            any(c.startswith("h-") for c in classes) and any(c.startswith("w-") for c in classes))
        if not (attrs.get("width") and attrs.get("height")) and not sized_by_css:
            page.add("warning", "images", f"<img> without width and height (layout shift while it loads): {src[:80]}", line)

    # ---- links and local files
    def resolve_local(ref: str) -> Path | None:
        path = urllib.parse.unquote(ref.split("#", 1)[0].split("?", 1)[0])
        if not path:
            return page.path.resolve() if page.path else None
        assert page.path is not None and root is not None
        target = (root / path.lstrip("/")) if path.startswith("/") else (page.path.parent / path)
        if target.is_dir():
            target = target / "index.html"
        elif not target.exists() and not target.suffix and target.with_suffix(".html").is_file():
            target = target.with_suffix(".html")  # clean URLs: /about serves about.html on most static hosts
        return target.resolve()

    def same_site(url: str) -> bool:
        return bool(page.url) and urllib.parse.urlsplit(urllib.parse.urljoin(page.url, url)).netloc == urllib.parse.urlsplit(page.url).netloc

    checked_links: set[str] = set()
    for href, line in d.anchors:
        h = href.strip()
        if not h or h in checked_links:
            continue
        # external links are not fetched; in URL mode an absolute link to the same host is internal
        if is_external(h) and not (h.startswith(("http://", "https://", "//")) and same_site(h)):
            continue
        checked_links.add(h)
        if h.startswith("#"):
            frag = h[1:]
            if frag and frag not in d.ids:
                page.add("error", "links", f'anchor href="{h}" has no element with that id on this page', line)
            continue
        frag = h.split("#", 1)[1] if "#" in h else ""
        if page.path is not None:
            target = resolve_local(h)
            if target is None or not target.exists():
                r = root.resolve() if root else None
                shown = target.relative_to(r).as_posix() if target and r and r in target.parents else str(target)
                page.add("error", "links", f'broken link href="{h}": {shown} does not exist', line)
            elif frag and target in by_path and frag not in by_path[target].parsed.ids:
                page.add("error", "links", f'href="{h}": {target.name} has no id="{frag}"', line)
        elif fetcher is not None and page.url:
            absolute = urllib.parse.urljoin(page.url, h.split("#", 1)[0])
            if absolute in by_url:
                if frag and frag not in by_url[absolute].parsed.ids:
                    page.add("error", "links", f'href="{h}": that page has no id="{frag}"', line)
                continue
            status = fetcher.status(absolute)
            if status is None or status >= 400:
                page.add("error", "links", f'broken link href="{h}" -> {absolute} (status {status})', line)

    # ---- resources: missing files, image size, page weight
    weight = page.size
    external = measured = 0
    seen_res: set[str] = set()
    for kind, ref, line in d.resources:
        ref = ref.strip()
        if not ref or ref in seen_res or ref.startswith("data:"):
            continue
        seen_res.add(ref)
        if is_external(ref):
            if page.url and fetcher is not None:
                absolute = ref if not ref.startswith("//") else urllib.parse.urlsplit(page.url).scheme + ":" + ref
                if urllib.parse.urlsplit(absolute).netloc == urllib.parse.urlsplit(page.url).netloc:
                    status, body, _ = fetcher.get(absolute)
                    size = len(body)
                else:
                    external += 1
                    continue
            else:
                external += 1
                continue
        elif page.path is not None:
            target = resolve_local(ref)
            if target is None or not target.is_file():
                page.add("error", "files", f"{kind} file not found: {ref}", line)
                continue
            size = target.stat().st_size
        else:
            assert fetcher is not None and page.url
            absolute = urllib.parse.urljoin(page.url, ref)
            status, body, _ = fetcher.get(absolute)
            if status is None or status >= 400:
                page.add("error", "files", f"{kind} not found: {ref} (status {status})", line)
                continue
            size = len(body)
        weight += size
        measured += 1
        if kind == "image" and size > IMG_LIMIT:
            page.add("warning", "images", f"image is {fmt_kb(size)} (limit 300 KB): {ref[:80]}", line)
    page.weight = weight
    note = f" ({external} external resource{'s' if external != 1 else ''} not measured)" if external else ""
    page.add("warning" if weight > PAGE_LIMIT else "info", "weight",
             f"page weight {fmt_kb(weight)}: HTML {fmt_kb(page.size)} plus {measured} file(s){note}")

    # ---- inline contrast
    for tag, style, bg_s, line in d.inline_styles:
        fg_s, own_bg = style_colours(style)
        if not fg_s or not bg_s or bg_s == UNKNOWN:
            continue
        fg, bg = parse_colour(fg_s), parse_colour(bg_s)
        if not fg or not bg:
            continue
        ratio = contrast_ratio(fg, bg)
        where = "" if own_bg == bg_s else " (background set on a parent)"
        if ratio < 3:
            page.add("error", "contrast", f"<{tag}> {fg_s} on {bg_s}{where} is {ratio:.2f}:1 (needs 4.5:1, 3:1 for large text)", line)
        elif ratio < 4.5:
            page.add("warning", "contrast", f"<{tag}> {fg_s} on {bg_s}{where} is {ratio:.2f}:1; passes only for large text (24px, or 18.7px bold)", line)

    # ---- forms
    for c in d.controls:
        a = c["attrs"]
        labelled = c["in_label"] or (a.get("id") and a["id"] in d.labels_for) or a.get("aria-label") or a.get("aria-labelledby") or a.get("title")
        if not labelled:
            ident = a.get("name") or a.get("id") or c["type"]
            note = " (a placeholder is not a label)" if a.get("placeholder") else ""
            page.add("error", "forms", f"<{c['tag']}> {ident!r} has no label{note}", c["line"])

    # ---- vibe check
    if vibe_mod is None:
        page.add("info", "vibe", "vibe_check.py not found next to this pack; skipped")
    else:
        if page.path is not None:
            report = vibe_mod.analyze(page.path)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_file = Path(tmp) / "page.html"
                tmp_file.write_text(page.html, encoding="utf-8")
                report = vibe_mod.analyze(tmp_file)
        page.vibe = report["verdict"]
        for x in report["findings"]:
            sev = "warning" if x["tell"].startswith(("generic", "gradient", "purple", "lorem", "placeholder")) else "info"
            page.add(sev, "vibe", f"{x['tell']}: {x['count']}" + (f" [{x['detail']}]" if x.get("detail") else ""))
        if report["verdict"] == "generic":
            page.add("warning", "vibe", "vibe verdict GENERIC: run web-craft-consistency-audit and web-craft-anti-generic-design")


# ----------------------------------------------------------------------------- report
CSS = """
:root{--bg:#fff;--fg:#1c1b19;--muted:#6b6660;--line:#e6e2da;--err:#b42318;--warn:#b54708;--info:#1f6f78;--ok:#1d7a4a;--card:#faf8f4}
@media (prefers-color-scheme:dark){:root{--bg:#141311;--fg:#ece8e0;--muted:#a39d93;--line:#2c2a26;--err:#f97066;--warn:#f7a851;--info:#6cc5cf;--ok:#5fcf8a;--card:#1c1a17}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;padding:32px 24px 64px}
main{max-width:1100px;margin:0 auto}h1{font-size:28px;margin:0 0 4px}h2{font-size:20px;margin:40px 0 12px;padding-top:24px;border-top:1px solid var(--line)}
.sub{color:var(--muted);margin:0 0 24px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}td.num{text-align:right;font-variant-numeric:tabular-nums}
.score{display:inline-block;min-width:44px;text-align:center;padding:2px 8px;border-radius:999px;font-weight:600;color:#fff}
.s-good{background:var(--ok)}.s-mid{background:var(--warn)}.s-bad{background:var(--err)}
.sev{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}.error{color:var(--err)}.warning{color:var(--warn)}.info{color:var(--info)}
code{font:13px ui-monospace,monospace;background:var(--card);padding:1px 4px;border-radius:4px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--muted);margin:16px 0}
footer{margin-top:48px;color:var(--muted);font-size:13px}
"""


def score_class(score: int) -> str:
    return "s-good" if score >= 85 else "s-mid" if score >= 60 else "s-bad"


def write_report(pages: list[Page], target: str, out: Path, command: str) -> None:
    e = html_mod.escape
    total_err = sum(p.errors for p in pages)
    total_warn = sum(p.warnings for p in pages)
    rows = "".join(
        f'<tr><td><a href="#p{i}">{e(p.name)}</a></td><td class="num"><span class="score {score_class(p.score)}">{p.score}</span></td>'
        f'<td class="num">{p.errors}</td><td class="num">{p.warnings}</td><td class="num">{fmt_kb(p.weight)}</td><td>{e(p.vibe)}</td></tr>'
        for i, p in enumerate(pages))
    sections = []
    for i, p in enumerate(pages):
        order = {"error": 0, "warning": 1, "info": 2}
        items = sorted(p.findings, key=lambda f: (order[f["severity"]], f["check"], f["line"] or 0))
        body = "".join(
            f'<tr><td><span class="sev {f["severity"]}">{f["severity"]}</span></td><td>{e(f["check"])}</td>'
            f'<td>{e(f["message"])}</td><td class="num">{f["line"] or ""}</td></tr>' for f in items)
        sections.append(
            f'<h2 id="p{i}">{e(p.name)} <span class="score {score_class(p.score)}">{p.score}</span></h2>'
            f'<p class="sub">{p.errors} errors, {p.warnings} warnings, weight {fmt_kb(p.weight)}, vibe {e(p.vibe)}</p>'
            f'<table><thead><tr><th>Severity</th><th>Check</th><th>Finding</th><th>Line</th></tr></thead><tbody>{body}</tbody></table>')
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site audit: {e(target)}</title><style>{CSS}</style></head><body><main>
<h1>Site audit</h1><p class="sub">{e(target)} &middot; {len(pages)} page{'s' if len(pages) != 1 else ''} &middot; {total_err} errors, {total_warn} warnings</p>
<table><thead><tr><th>Page</th><th>Score</th><th>Errors</th><th>Warnings</th><th>Weight</th><th>Vibe</th></tr></thead><tbody>{rows}</tbody></table>
<div class="legend"><span><b class="error">error</b>: fix before shipping</span><span><b class="warning">warning</b>: fix when touching the page</span><span><b class="info">info</b>: context, no action needed</span></div>
{''.join(sections)}
<footer>Generated by <code>{e(command)}</code>. Score = 100 &minus; 10 per error &minus; 3 per warning.</footer>
</main></body></html>"""
    out.write_text(doc, encoding="utf-8")


# ----------------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
        except (AttributeError, ValueError):
            pass
    args = list(argv)
    out = Path("site-audit.html")
    max_pages = 20
    as_json = False
    positional: list[str] = []
    while args:
        a = args.pop(0)
        if a == "--out" and args:
            out = Path(args.pop(0))
        elif a == "--max-pages" and args:
            max_pages = int(args.pop(0))
        elif a == "--json":
            as_json = True
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            positional.append(a)
    if len(positional) != 1:
        print(__doc__)
        return 2
    target = positional[0]
    vibe_mod = load_vibe_check()
    fetcher: Fetcher | None = None
    root: Path | None = None
    if re.match(r"^https?://", target, re.I):
        fetcher = Fetcher()
        pages = collect_url(target, fetcher, max_pages)
    else:
        root = Path(target)
        if root.is_file():
            f = root
            root = root.parent
            pages = [Page(name=f.name, html=f.read_text(encoding="utf-8", errors="replace"), size=f.stat().st_size, path=f, url=None)]
        elif root.is_dir():
            pages = collect_folder(root)
        else:
            print(f"not a folder, file or http(s) URL: {target}")
            return 2
        if not pages:
            print(f"no .html files under {root}")
            return 2
    for p in pages:
        p.parsed = parse(p.html)
    for p in pages:
        check_page(p, pages, root, fetcher, vibe_mod)

    command = "python site_audit.py " + " ".join(argv)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_report(pages, target, out, command)

    log = sys.stderr if as_json else sys.stdout  # with --json, stdout carries only the JSON
    width = max(len(p.name) for p in pages)
    print(f"site audit: {len(pages)} page{'s' if len(pages) != 1 else ''} from {target}", file=log)
    for p in pages:
        print(f"  {p.name:<{width}}  score {p.score:>3}  {p.errors:>2} errors  {p.warnings:>2} warnings  {fmt_kb(p.weight):>7}  vibe: {p.vibe}", file=log)
    errors = [(p.name, f) for p in pages for f in p.findings if f["severity"] == "error"]
    if errors:
        print("errors:", file=log)
        for name, f in errors:
            where = f"{name}:{f['line']}" if f["line"] else name
            print(f"  {where}  [{f['check']}] {f['message']}", file=log)
    print(f"report: {out.resolve()}", file=log)
    if as_json:
        print(json.dumps([{"page": p.name, "score": p.score, "weight": p.weight, "vibe": p.vibe, "findings": p.findings}
                          for p in pages], indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
