#!/usr/bin/env python3
"""screenshot_diff.py: screenshot two pages at phone, tablet and desktop widths and show what changed.

Usage:
  python screenshot_diff.py before.html after.html
  python screenshot_diff.py https://staging.example.com https://example.com --widths 375,1280 --out diff.html
  python screenshot_diff.py A B --threshold 12 --fail-above 5      # exit 1 when any width differs by more than 5%

A and B are URLs (http://, https://, file://) or paths to local files; files become file:// URLs.
For each width the script runs headless Chrome (or Edge) once per page:
  chrome --headless=new --disable-gpu --hide-scrollbars --window-size=W,2200 --screenshot=<png> <url>
so each screenshot is the top 2200 px of the page; anything below that is not compared.
Pillow compares the two PNGs: a pixel counts as changed when any colour channel differs by more than
--threshold (0-255, default 10). The browser is told to prefer a light colour scheme (--scheme dark or system to change). The report gives the changed-pixel percentage per width and shows
A, B and a diff image (A faded, changed pixels red) side by side. PNGs go in <out stem>-shots/ next to the report.
Browser lookup: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe, then
C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe, then chrome / msedge / chromium on PATH.
Needs Pillow (pip install pillow). Python 3.10+; Windows and Unix.
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

HEIGHT = 2200
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
PATH_NAMES = ["chrome", "google-chrome", "msedge", "microsoft-edge", "chromium", "chromium-browser"]


def find_browser() -> str | None:
    for candidate in BROWSERS:
        if Path(candidate).is_file():
            return candidate
    for name in PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


def to_url(target: str) -> str:
    if re.match(r"^(https?|file)://", target, re.I):
        return target
    path = Path(target)
    if not path.is_file():
        sys.exit(f"not a URL and not an existing file: {target}")
    return path.resolve().as_uri()


def screenshot(browser: str, url: str, width: int, png: Path, profile: Path, scheme: str = "light") -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    if png.exists():
        png.unlink()
    if scheme in ("light", "dark"):
        # headless Chrome follows the OS theme, so a page with dark: styles could come out dark in one run and light in
        # another; the throwaway profile pins the browser's colour scheme (browser.theme.color_scheme2: 1 light, 2 dark)
        (profile / "Default").mkdir(parents=True, exist_ok=True)
        (profile / "Default" / "Preferences").write_text(
            json.dumps({"browser": {"theme": {"color_scheme2": 1 if scheme == "light" else 2}}}), encoding="utf-8")
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           f"--window-size={width},{HEIGHT}", f"--screenshot={png}",
           # a throwaway profile so a Chrome that is already open does not swallow the command;
           # the virtual-time budget lets web fonts and the Tailwind CDN script finish before the shot
           f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check", "--virtual-time-budget=8000",
           url]
    try:
        subprocess.run(cmd, capture_output=True, timeout=120, check=False)
    except subprocess.TimeoutExpired:
        sys.exit(f"browser timed out on {url} at {width}px")
    if not png.is_file() or png.stat().st_size == 0:
        sys.exit(f"no screenshot produced for {url} at {width}px (browser: {browser})")


def compare(a_png: Path, b_png: Path, diff_png: Path, threshold: int) -> tuple[float, int, int]:
    """Returns (changed percentage, changed pixels, total pixels). Different sizes are padded with white."""
    a = Image.open(a_png).convert("RGB")
    b = Image.open(b_png).convert("RGB")
    w, h = max(a.width, b.width), max(a.height, b.height)
    if a.size != (w, h):
        canvas = Image.new("RGB", (w, h), "white")
        canvas.paste(a, (0, 0))
        a = canvas
    if b.size != (w, h):
        canvas = Image.new("RGB", (w, h), "white")
        canvas.paste(b, (0, 0))
        b = canvas
    channels = ImageChops.difference(a, b).split()
    peak = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])  # largest channel difference
    mask = peak.point(lambda v: 255 if v > threshold else 0)
    changed = sum(mask.histogram()[255:])
    total = w * h
    faded = Image.blend(a.convert("L").convert("RGB"), Image.new("RGB", (w, h), "white"), 0.65)
    shown = mask.filter(ImageFilter.MaxFilter(3))  # thicken one-pixel edges so they are visible when scaled down
    faded.paste(Image.new("RGB", (w, h), (230, 30, 60)), mask=shown)
    faded.save(diff_png)
    return 100 * changed / total, changed, total


CSS = """
:root{--bg:#fff;--fg:#1c1b19;--muted:#6b6660;--line:#e6e2da;--card:#faf8f4;--ok:#1d7a4a;--warn:#b54708;--bad:#b42318}
@media (prefers-color-scheme:dark){:root{--bg:#141311;--fg:#ece8e0;--muted:#a39d93;--line:#2c2a26;--card:#1c1a17;--ok:#5fcf8a;--warn:#f7a851;--bad:#f97066}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;padding:32px 24px 64px}
main{max-width:1500px;margin:0 auto}h1{font-size:28px;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 24px;overflow-wrap:anywhere}
h2{font-size:20px;margin:40px 0 4px;padding-top:24px;border-top:1px solid var(--line)}
a{color:inherit}table{border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:6px 14px 6px 0;border-bottom:1px solid var(--line)}th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.pct{font-weight:600;font-variant-numeric:tabular-nums}.same{color:var(--ok)}.some{color:var(--warn)}.lots{color:var(--bad)}
.row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:12px}
@media (max-width:900px){.row{grid-template-columns:minmax(0,1fr)}}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden}
figcaption{padding:6px 10px;font-size:12px;color:var(--muted);border-bottom:1px solid var(--line);overflow-wrap:anywhere}
figure img{display:block;width:100%;height:auto}
"""


def pct_class(p: float) -> str:
    return "same" if p < 0.05 else "some" if p < 5 else "lots"


def write_report(out: Path, shots_dir: Path, a: str, b: str, results: list[dict], threshold: int) -> None:
    e = html_mod.escape
    rows = "".join(f'<tr><td><a href="#w{r["width"]}">{r["width"]} px</a></td><td class="pct {pct_class(r["pct"])}">{r["pct"]:.2f}%</td>'
                   f'<td>{r["changed"]:,} of {r["total"]:,} pixels</td></tr>' for r in results)
    rel = shots_dir.name
    sections = []
    for r in results:
        sections.append(
            f'<h2 id="w{r["width"]}">{r["width"]} px <span class="pct {pct_class(r["pct"])}">{r["pct"]:.2f}% changed</span></h2>'
            f'<div class="row"><figure><figcaption>A (before): {e(a)}</figcaption><img src="{e(rel)}/{r["name"]}-a.png" alt="A at {r["width"]} px" loading="lazy"></figure>'
            f'<figure><figcaption>B (after): {e(b)}</figcaption><img src="{e(rel)}/{r["name"]}-b.png" alt="B at {r["width"]} px" loading="lazy"></figure>'
            f'<figure><figcaption>Diff: changed pixels in red, unchanged areas faded</figcaption><img src="{e(rel)}/{r["name"]}-diff.png" alt="Diff at {r["width"]} px" loading="lazy"></figure></div>')
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Screenshot diff</title><style>{CSS}</style></head><body><main>
<h1>Screenshot diff</h1>
<p class="sub">A: {e(a)}<br>B: {e(b)}<br>Top {HEIGHT} px of each page; a pixel counts as changed when a channel differs by more than {threshold} of 255.</p>
<table><thead><tr><th>Width</th><th>Changed</th><th>Pixels</th></tr></thead><tbody>{rows}</tbody></table>
{''.join(sections)}
</main></body></html>"""
    out.write_text(doc, encoding="utf-8")


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Screenshot two pages at several widths and diff them.")
    ap.add_argument("a", metavar="A", help="before: URL or file")
    ap.add_argument("b", metavar="B", help="after: URL or file")
    ap.add_argument("--widths", default="375,768,1280", help="comma-separated viewport widths (default 375,768,1280)")
    ap.add_argument("--out", default="diff.html", help="report file (default diff.html)")
    ap.add_argument("--scheme", choices=("light", "dark", "system"), default="light",
                    help="prefers-color-scheme to emulate (default light, so results do not depend on the OS theme)")
    ap.add_argument("--threshold", type=int, default=10, help="per-channel difference (0-255) that counts as changed (default 10)")
    ap.add_argument("--fail-above", type=float, default=None, metavar="PCT", help="exit 1 when any width changed by more than PCT percent")
    args = ap.parse_args(argv)
    try:
        widths = [int(w) for w in args.widths.split(",") if w.strip()]
    except ValueError:
        ap.error("--widths must be comma-separated integers, e.g. 375,768,1280")
    if not widths or any(w < 200 for w in widths):
        ap.error("--widths needs at least one width of 200 or more")
    browser = find_browser()
    if not browser:
        sys.exit("no Chrome or Edge found (looked in Program Files, then on PATH)")
    url_a, url_b = to_url(args.a), to_url(args.b)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shots = out.parent / f"{out.stem}-shots"
    shots.mkdir(parents=True, exist_ok=True)

    results = []
    with tempfile.TemporaryDirectory(prefix="shotdiff-") as tmp:
        for w in widths:
            name = f"w{w}"
            for side, url in (("a", url_a), ("b", url_b)):
                screenshot(browser, url, w, shots / f"{name}-{side}.png", Path(tmp) / f"profile-{side}-{w}", args.scheme)
            pct, changed, total = compare(shots / f"{name}-a.png", shots / f"{name}-b.png", shots / f"{name}-diff.png", args.threshold)
            results.append({"width": w, "name": name, "pct": pct, "changed": changed, "total": total})
    write_report(out, shots, args.a, args.b, results, args.threshold)

    print(f"screenshot diff: {args.a}  vs  {args.b}  (browser: {Path(browser).name})")
    for r in results:
        print(f"  {r['width']:>5} px  {r['pct']:6.2f}% changed  ({r['changed']:,} of {r['total']:,} pixels)")
    print(f"report: {out.resolve()}")
    if args.fail_above is not None and any(r["pct"] > args.fail_above for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
