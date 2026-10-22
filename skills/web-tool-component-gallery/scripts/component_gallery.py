#!/usr/bin/env python3
"""component_gallery.py: turn a folder of HTML pages into one living style-guide page.

Usage:
  python component_gallery.py src/                       # every .html under the folder
  python component_gallery.py src/ --out gallery.html    # default: component-gallery.html in the cwd

For every page it extracts the <header>, the <footer> and every top-level <section> (one that is not nested in
another section, article, header or footer). Each component is rendered live in an <iframe srcdoc> that carries
the source page's <head> (so the Tailwind CDN, @theme block, fonts and stylesheets load), the <html> and <body>
attributes, and the wrappers the component sat in (<main class="mx-auto max-w-6xl">...). Each card shows a label
(first heading or id), the source file and line, a 375 / 768 / 1280 / fit width toggle, a "copy HTML" button and
the source. Components whose HTML is identical across pages appear once, with the other files listed.
Standard library only; Python 3.10+; Windows and Unix. Open the output in a browser; no server needed.
"""
from __future__ import annotations

import html as html_mod
import os
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
COMPONENT_TAGS = {"header", "footer", "section"}
# a header/footer inside one of these is part of a component, not a page component
NESTING_TAGS = {"section", "article", "aside", "nav", "dialog", "figure", "li", "form", "header", "footer", "table", "blockquote"}


@dataclass
class Component:
    tag: str
    id: str
    start: int
    end: int = -1
    line: int = 0
    heading: str = ""
    aria_label: str = ""
    wrappers: list[tuple[str, str]] = field(default_factory=list)  # (tag, starttag text)
    html: str = ""
    source: str = ""
    also_in: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        # a footer's first heading is usually a link-column title ("Product"), so headers and footers keep their role
        if self.tag in ("header", "footer"):
            base = "Site header" if self.tag == "header" else "Site footer"
            return f"{base}: {self.aria_label[:60]}" if self.aria_label else base
        for text in (self.heading, self.aria_label):
            if text:
                return text[:70]
        return f"#{self.id}" if self.id else "Section"


class SliceParser(HTMLParser):
    """Finds byte ranges of components in the raw source so the output keeps the author's exact markup."""

    def __init__(self, src: str) -> None:
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", src)]
        self.stack: list[tuple[str, int, str]] = []  # (tag, start index, starttag text)
        self.components: list[Component] = []
        self.open: Component | None = None
        self.html_tag = "<html>"
        self.body_tag = "<body>"
        self.head: tuple[int, int] | None = None
        self._head_start = -1
        self._heading: list[str] | None = None
        self._heading_tag = ""

    def pos(self) -> int:
        line, off = self.getpos()
        return self.line_starts[line - 1] + off

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        p = self.pos()
        text = self.get_starttag_text() or f"<{tag}>"
        a = {k: (v if v is not None else "") for k, v in attrs}
        if tag == "html":
            self.html_tag = text
        elif tag == "head":
            self._head_start = p
        elif tag == "body":
            self.body_tag = text
        elif tag in COMPONENT_TAGS and self.open is None:
            open_tags = {t for t, _, _ in self.stack}
            qualifies = (tag == "section" and not open_tags & {"section", "article", "header", "footer"}) or \
                        (tag in ("header", "footer") and not open_tags & NESTING_TAGS)
            if qualifies:
                self.open = Component(tag=tag, id=a.get("id", ""), aria_label=html_mod.unescape(a.get("aria-label", "")).strip(),
                                      start=p, line=self.getpos()[0],
                                      wrappers=[(t, s) for t, _, s in self.stack if t not in ("html", "head", "body")])
                self.components.append(self.open)
        if self.open is not None and self._heading is None and not self.open.heading and re.fullmatch(r"h[1-6]", tag):
            self._heading, self._heading_tag = [], tag
        if tag not in VOID:
            self.stack.append((tag, p, text))

    def handle_endtag(self, tag: str) -> None:
        p = self.pos()
        gt = self.src.find(">", p)
        end = gt + 1 if gt != -1 else len(self.src)
        if tag == "head" and self._head_start >= 0:
            self.head = (self._head_start, end)
        if self._heading is not None and tag == self._heading_tag and self.open is not None:
            self.open.heading = re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", "".join(self._heading)))).strip()
            self._heading = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                if self.open is not None and self.stack[i][1] == self.open.start:
                    self.open.end = end
                    self.open.html = self.src[self.open.start:end]
                    self.open = None
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._heading is not None:
            self._heading.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._heading is not None:
            self._heading.append(f"&#{name};")


def extract(path: Path, root: Path) -> tuple[list[Component], str, str, str]:
    src = path.read_text(encoding="utf-8", errors="replace")
    parser = SliceParser(src)
    parser.feed(src)
    parser.close()
    head_html = src[parser.head[0]:parser.head[1]] if parser.head else "<head></head>"
    name = path.relative_to(root).as_posix()
    comps = [c for c in parser.components if c.end > 0]
    for c in comps:
        c.source = name
    return comps, head_html, parser.html_tag, parser.body_tag


def srcdoc_for(c: Component, head_html: str, html_tag: str, body_tag: str, base_href: str, token: str) -> str:
    """A complete document: the page's head (plus a <base> so relative images resolve), the component in its wrappers."""
    if "<base" not in head_html.lower():
        head_html = re.sub(r"(<head\b[^>]*>)", lambda m: m.group(1) + f'<base href="{html_mod.escape(base_href)}">', head_html, count=1, flags=re.I)
    opens = "".join(s for _, s in c.wrappers)
    closes = "".join(f"</{t}>" for t, _ in reversed(c.wrappers))
    # a full page's html/body are often h-full / min-h-screen: that would pin the iframe at its current height, so the
    # card could never shrink to fit; links are inert so a click cannot navigate the preview away (the <base> would resolve them)
    fix = "<style>html,body{height:auto!important;min-height:0!important}</style>"
    sizer = ("<script>document.addEventListener('click',function(e){if(e.target.closest('a'))e.preventDefault()});"
             "(function(){var send=function(){parent.postMessage({galleryToken:%r,"
             "height:Math.ceil(document.documentElement.getBoundingClientRect().height)},'*')};new ResizeObserver(send).observe(document.documentElement);"
             "addEventListener('load',function(){send();setTimeout(send,600);setTimeout(send,2000)});})();</script>") % token
    return f"<!doctype html>{html_tag}{head_html}{fix}{body_tag}{opens}{c.html}{closes}{sizer}</body></html>"


CSS = """
:root{--bg:#f4f2ee;--fg:#1c1b19;--muted:#6b6660;--line:#dcd7cd;--card:#fff;--accent:#1f6f78}
@media (prefers-color-scheme:dark){:root{--bg:#141311;--fg:#ece8e0;--muted:#a39d93;--line:#2c2a26;--card:#1c1a17;--accent:#6cc5cf}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
.top{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:12px 20px;background:var(--card);border-bottom:1px solid var(--line)}
.top h1{font-size:16px;margin:0 auto 0 0}.top .count{color:var(--muted)}
button{font:inherit;font-size:13px;padding:4px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);cursor:pointer}
button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
main{padding:20px;display:grid;gap:24px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.card[hidden]{display:none}
.card header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line)}
.card h2{font-size:15px;margin:0 auto 0 0}.meta{color:var(--muted);font-size:12px}.meta code{font:12px ui-monospace,monospace}
.tools{display:flex;gap:6px;flex-wrap:wrap}
.stage{overflow-x:auto;background:repeating-conic-gradient(var(--line) 0 25%,transparent 0 50%) 0 0/16px 16px;padding:16px}
iframe{display:block;width:100%;max-width:100%;height:200px;border:0;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.15);margin:0 auto;transition:width .2s}
details{border-top:1px solid var(--line)}summary{padding:8px 14px;cursor:pointer;color:var(--muted);font-size:12px}
pre{margin:0;padding:12px 14px;max-height:320px;overflow:auto;font:12px/1.45 ui-monospace,monospace;background:var(--bg)}
.toast{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:var(--fg);color:var(--bg);padding:8px 14px;border-radius:8px;opacity:0;transition:opacity .2s}
.toast.show{opacity:1}
"""

JS = """
const frames = new Map();
addEventListener('message', (e) => {
  const d = e.data; if (!d || !d.galleryToken) return;
  const f = frames.get(d.galleryToken); if (f && d.height) f.style.height = Math.min(Math.max(d.height, 80), 4000) + 'px';
});
for (const f of document.querySelectorAll('iframe[data-token]')) frames.set(f.dataset.token, f);
function setWidth(card, w) {
  const f = card.querySelector('iframe');
  f.style.width = w === 'fit' ? '100%' : w + 'px';
  f.style.maxWidth = w === 'fit' ? '100%' : 'none';  // a fixed width may be wider than the stage: scroll, don't squash
  for (const b of card.querySelectorAll('[data-width]')) b.setAttribute('aria-pressed', String(b.dataset.width === w));
}
document.addEventListener('click', async (e) => {
  const b = e.target.closest('button'); if (!b) return;
  const card = b.closest('.card');
  if (b.dataset.width && card) setWidth(card, b.dataset.width);
  if (b.dataset.allWidth) for (const c of document.querySelectorAll('.card')) setWidth(c, b.dataset.allWidth);
  if (b.dataset.copy && card) {
    const text = card.querySelector('textarea').value;
    try { await navigator.clipboard.writeText(text); toast('HTML copied'); }
    catch { const ta = card.querySelector('textarea'); ta.hidden = false; ta.select(); document.execCommand('copy'); ta.hidden = true; toast('HTML copied'); }
  }
  if (b.dataset.file !== undefined) {
    for (const o of document.querySelectorAll('[data-file]')) o.setAttribute('aria-pressed', String(o === b));
    for (const c of document.querySelectorAll('.card')) c.hidden = b.dataset.file !== '' && c.dataset.source !== b.dataset.file;
  }
});
let timer; function toast(msg) { const t = document.querySelector('.toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(timer); timer = setTimeout(() => t.classList.remove('show'), 1400); }
"""


def build(root: Path, out: Path) -> tuple[int, int, int]:
    pages = sorted(root.rglob("*.html"))
    e = html_mod.escape
    cards: list[str] = []
    seen: dict[str, Component] = {}
    total = 0
    files_with_components: list[str] = []
    for page in pages:
        if page.resolve() == out.resolve():
            continue
        comps, head_html, html_tag, body_tag = extract(page, root)
        if comps:
            files_with_components.append(comps[0].source)
        try:
            base_href = Path(os.path.relpath(page.resolve(), out.resolve().parent)).as_posix()
        except ValueError:  # different drive on Windows
            base_href = page.resolve().as_uri()
        for c in comps:
            total += 1
            key = re.sub(r"\s+", " ", c.html).strip()
            if key in seen:
                seen[key].also_in.append(c.source)
                continue
            seen[key] = c
            token = f"c{len(seen)}"
            doc = srcdoc_for(c, head_html, html_tag, body_tag, base_href, token)
            cards.append((c, token, doc))  # type: ignore[arg-type]

    card_html = []
    for c, token, doc in cards:  # type: ignore[misc]
        also = f" &middot; also in {e(', '.join(sorted(set(c.also_in))))}" if c.also_in else ""
        ident = f' id="{c.id}"' if c.id else ""
        card_html.append(f"""
<article class="card" data-source="{e(c.source)}">
  <header>
    <h2>{e(c.label)}</h2>
    <span class="meta"><code>&lt;{c.tag}{e(ident)}&gt;</code> &middot; {e(c.source)}:{c.line}{also}</span>
    <div class="tools" role="group" aria-label="Preview width">
      <button data-width="375">375</button><button data-width="768">768</button><button data-width="1280">1280</button><button data-width="fit" aria-pressed="true">Fit</button>
      <button data-copy="1">Copy HTML</button>
    </div>
  </header>
  <div class="stage"><iframe data-token="{token}" title="{e(c.label)} from {e(c.source)}" loading="lazy" srcdoc="{e(doc, quote=True)}"></iframe></div>
  <details><summary>Source ({len(c.html.splitlines())} lines)</summary><pre>{e(c.html)}</pre></details>
  <textarea hidden aria-hidden="true">{e(c.html, quote=False)}</textarea>
</article>""")

    file_buttons = "".join(f'<button data-file="{e(f)}">{e(f)}</button>' for f in files_with_components)
    page_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Component gallery: {e(root.name)}</title><style>{CSS}</style></head><body>
<div class="top">
  <h1>Component gallery <span class="count">{len(cards)} components from {len(files_with_components)} pages</span></h1>
  <div class="tools" role="group" aria-label="All widths"><span class="meta">All:</span><button data-all-width="375">375</button><button data-all-width="768">768</button><button data-all-width="1280">1280</button><button data-all-width="fit">Fit</button></div>
  <div class="tools" role="group" aria-label="Filter by file"><button data-file="" aria-pressed="true">All files</button>{file_buttons}</div>
</div>
<main>{''.join(card_html) if card_html else '<p>No header, footer or top-level section elements found.</p>'}</main>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script></body></html>"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_html, encoding="utf-8")
    return len(pages), total, len(cards)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = list(argv)
    out = Path("component-gallery.html")
    positional: list[str] = []
    while args:
        a = args.pop(0)
        if a == "--out" and args:
            out = Path(args.pop(0))
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            positional.append(a)
    if len(positional) != 1 or not Path(positional[0]).is_dir():
        print(__doc__)
        return 2
    root = Path(positional[0])
    pages, found, unique = build(root, out)
    print(f"component gallery: {pages} page(s) scanned, {found} components found, {unique} unique after dedup")
    print(f"gallery: {out.resolve()}")
    return 0 if unique else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
