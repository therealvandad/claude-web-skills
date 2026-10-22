#!/usr/bin/env python3
"""vibe_check.py: scan HTML files for the tells of generic, AI-looking pages and for style drift.

Usage:
  python vibe_check.py index.html            # one file
  python vibe_check.py src/                  # every .html under a folder
  python vibe_check.py index.html --json     # machine-readable

It reports, per file and in total:
  - generic marketing words in visible text ("seamless", "unlock", "elevate"...)
  - gradient headline text and purple/indigo/pink gradient backgrounds
  - emoji used as icons in headings, buttons and list items
  - lorem ipsum and placeholder images
  - inline style= and onclick= attributes, console.log in scripts
  - how many distinct radius, shadow, padding, gap and heading-size utilities are in use (drift)
  - long class strings repeated 3+ times (copy-pasted components)
  - how many sections are centred
Exit code is 1 when the score is "generic", so it can gate a build.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

GENERIC_WORDS = [
    "seamless", "seamlessly", "unlock", "unleash", "elevate", "empower", "effortless", "effortlessly",
    "supercharge", "revolutionize", "revolutionary", "game-changing", "game changer", "cutting-edge",
    "next-level", "next level", "in today's fast-paced", "look no further", "take your .* to the next level",
    "all-in-one", "one-stop", "best-in-class", "world-class", "leverage", "synergy", "robust", "streamline",
    "transform the way", "reimagine", "the future of", "powered by ai", "ai-powered", "✨",
]
GRADIENT_TEXT_RE = re.compile(r"class=\"[^\"]*\bbg-clip-text\b[^\"]*\btext-transparent\b|class=\"[^\"]*\btext-transparent\b[^\"]*\bbg-clip-text\b")
PURPLE_GRADIENT_RE = re.compile(r"\bbg-gradient-to-\w+\b[^\"]*\b(?:from|via|to)-(?:purple|indigo|violet|fuchsia|pink)-\d+")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌\U0001F680-\U0001F6FF]")
HEADING_OR_BUTTON_RE = re.compile(r"<(h[1-6]|button|li|a)\b[^>]*>(.*?)</\1>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
CLASS_RE = re.compile(r"class=\"([^\"]+)\"")
SECTION_RE = re.compile(r"<section\b[^>]*>", re.I)

UTILITY_FAMILIES = {
    "radius": re.compile(r"(?<![\w-])rounded(?:-(?:none|sm|md|lg|xl|2xl|3xl|4xl|full|\[[^\]]+\]))?(?![\w-])"),
    "shadow": re.compile(r"(?<![\w-])shadow(?:-(?:none|xs|sm|md|lg|xl|2xl|\[[^\]]+\]))?(?![\w-])"),
    "padding": re.compile(r"(?<![\w-])p[xy]?-(?:\d+(?:\.\d+)?|px|\[[^\]]+\])(?![\w-])"),
    "gap": re.compile(r"(?<![\w-])gap(?:-[xy])?-(?:\d+(?:\.\d+)?|px|\[[^\]]+\])(?![\w-])"),
    "text-size": re.compile(r"(?<![\w-])text-(?:xs|sm|base|lg|xl|\dxl|\[[^\]]+\])(?![\w-])"),
}


def visible_text(html: str) -> str:
    html = SCRIPT_RE.sub(" ", html)
    html = STYLE_BLOCK_RE.sub(" ", html)
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", html)).lower()


def analyze(path: Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")
    text = visible_text(html)
    report: dict = {"file": str(path), "lines": html.count("\n") + 1, "findings": [], "drift": {}}
    f = report["findings"]

    words = Counter()
    for w in GENERIC_WORDS:
        n = len(re.findall(w, text))
        if n:
            words[w] += n
    if words:
        f.append({"tell": "generic marketing words", "count": sum(words.values()),
                  "detail": ", ".join(f"{k} x{v}" for k, v in words.most_common(8))})

    n = len(GRADIENT_TEXT_RE.findall(html))
    if n:
        f.append({"tell": "gradient headline text (bg-clip-text + text-transparent)", "count": n})
    n = len(PURPLE_GRADIENT_RE.findall(html))
    if n:
        f.append({"tell": "purple/indigo/pink gradient backgrounds", "count": n})

    emoji_hits = sum(1 for m in HEADING_OR_BUTTON_RE.finditer(html) if EMOJI_RE.search(m.group(2)))
    if emoji_hits:
        f.append({"tell": "emoji used as icons in headings/buttons/list items", "count": emoji_hits})

    if "lorem ipsum" in text:
        f.append({"tell": "lorem ipsum", "count": text.count("lorem ipsum")})
    # only image URLs: Tailwind's placeholder: variant and placeholder="" attributes are not tells
    n = len(re.findall(r"\b(?:src|srcset|href)=\"[^\"]*(?:placehold\.co|via\.placeholder|placeholder\.com|unsplash\.com/random|dummyimage|picsum\.photos)", html, re.I))
    if n:
        f.append({"tell": "placeholder images", "count": n})

    n = len(re.findall(r"\sstyle=\"", html))
    if n > 3:
        f.append({"tell": "inline style= attributes", "count": n})
    n = len(re.findall(r"\son\w+=\"", html))
    if n:
        f.append({"tell": "inline event handlers (onclick=...)", "count": n})
    scripts = "\n".join(m.group(1) for m in SCRIPT_RE.finditer(html))
    n = len(re.findall(r"console\.log\(", scripts))
    if n:
        f.append({"tell": "console.log left in scripts", "count": n})

    classes = CLASS_RE.findall(html)
    all_classes = " ".join(classes)
    for fam, rx in UTILITY_FAMILIES.items():
        vals = Counter(rx.findall(all_classes))
        report["drift"][fam] = {"distinct": len(vals), "values": dict(vals.most_common(12))}
    # three matching cards is a normal grid; four or more identical 100+ char strings is a component that wants a class
    long_dupes = [(c, k) for c, k in Counter(c for c in classes if len(c) > 100).items() if k >= 4]
    if long_dupes:
        f.append({"tell": "long class strings repeated 4+ times (copy-pasted components)", "count": len(long_dupes),
                  "detail": "; ".join(f"{k}x '{c[:60]}...'" for c, k in long_dupes[:3])})

    sections = len(SECTION_RE.findall(html))
    centred = len(re.findall(r"<section\b[^>]*>\s*(?:<div\b[^>]*>\s*){0,3}<[^>]*\btext-center\b", html, re.I))
    if sections and centred / sections > 0.7 and sections >= 3:
        f.append({"tell": "nearly every section is centred", "count": f"{centred}/{sections}"})
    if report["lines"] > 1500:
        f.append({"tell": "very long single file", "count": report["lines"]})

    # a full landing page legitimately uses ~5 radii, ~4 shadows, ~20 padding steps (p/px/py counted separately), ~10 gaps
    limits = {"radius": 5, "shadow": 4, "padding": 24, "gap": 10, "text-size": 9}
    drift_flags = [fam for fam, d in report["drift"].items() if d["distinct"] > limits[fam]]
    if drift_flags:
        f.append({"tell": "style drift: too many distinct values", "count": len(drift_flags), "detail": ", ".join(drift_flags)})

    score = sum(1 for x in f) + sum(1 for x in f if x["tell"].startswith(("generic", "gradient", "purple", "emoji", "lorem")))
    report["verdict"] = "generic" if score >= 5 else "mixed" if score >= 2 else "clean"
    return report


def main(argv: list[str]) -> int:
    # Windows consoles default to cp1252; the report may contain emoji found in the page.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    if not args:
        print(__doc__)
        return 2
    files: list[Path] = []
    for a in args:
        p = Path(a)
        files += sorted(p.rglob("*.html")) if p.is_dir() else [p]
    reports = [analyze(p) for p in files if p.is_file()]
    if as_json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        for r in reports:
            print(f"\n{r['file']}  ({r['lines']} lines)  verdict: {r['verdict'].upper()}")
            for x in r["findings"]:
                print(f"  - {x['tell']}: {x['count']}" + (f"  [{x['detail']}]" if x.get("detail") else ""))
            d = r["drift"]
            print("  drift: " + ", ".join(f"{k} {v['distinct']} distinct" for k, v in d.items()))
            if not r["findings"]:
                print("  no tells found")
    return 1 if any(r["verdict"] == "generic" for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
