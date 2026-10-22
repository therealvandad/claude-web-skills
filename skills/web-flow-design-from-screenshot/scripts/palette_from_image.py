#!/usr/bin/env python3
"""palette_from_image.py: pull a restrained Tailwind v4 palette out of a screenshot.

Usage:
  python palette_from_image.py shot.png                       # print palette + @theme, write palette-preview.html
  python palette_from_image.py shot.png --count 8 --out theme.css   # also write theme.css and theme.html

Quantizes the image with Pillow, sorts colours by how much of the screen they cover, converts
sRGB to OKLCH in plain Python, then picks four roles:
  paper   the colour covering the most area (the page background)
  ink     the palette colour with the most lightness contrast against paper (synthesized if none reaches 7:1)
  accent  the most saturated colour that still covers a visible share of the screen
  line    a palette colour just off paper, or paper nudged 12% toward ink
plus derived paper-2, ink-2, accent-deep (accent darkened or lightened until it passes 4.5:1 on paper)
and accent-tint. Token names match web-flow-new-site, so the block drops into src/input.css.
Needs Pillow; everything else is the standard library.
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("palette_from_image.py needs Pillow: python -m pip install pillow")


# ----------------------------------------------------------------------------- colour maths

def _lin(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c: float) -> float:
    c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return c * 255


def rgb_to_oklch(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (_lin(v) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    C = math.hypot(A, B)
    H = math.degrees(math.atan2(B, A)) % 360
    return L, C, H


def _oklch_to_linear(L: float, C: float, H: float) -> tuple[float, float, float]:
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def oklch_to_rgb(L: float, C: float, H: float) -> tuple[int, int, int]:
    """Convert back to sRGB, lowering chroma until the colour is inside the gamut."""
    lo, hi = 0.0, C
    rgb = _oklch_to_linear(L, C, H)
    if any(v < -1e-4 or v > 1 + 1e-4 for v in rgb):
        for _ in range(24):
            mid = (lo + hi) / 2
            if any(v < -1e-4 or v > 1 + 1e-4 for v in _oklch_to_linear(L, mid, H)):
                hi = mid
            else:
                lo = mid
        rgb = _oklch_to_linear(L, lo, H)
    return tuple(max(0, min(255, round(_gam(max(0.0, min(1.0, v)))))) for v in rgb)


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hexs(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def css(L: float, C: float, H: float) -> str:
    return f"oklch({L * 100:.1f}% {C:.3f} {H if C >= 0.002 else 0:.1f})"


class Swatch:
    def __init__(self, rgb: tuple[int, int, int], share: float, source: str = "image") -> None:
        self.rgb, self.share, self.source = rgb, share, source
        self.L, self.C, self.H = rgb_to_oklch(rgb)

    @classmethod
    def lch(cls, L: float, C: float, H: float, source: str) -> "Swatch":
        L = max(0.0, min(1.0, L))
        s = cls(oklch_to_rgb(L, C, H), 0.0, source)
        s.L, s.C, s.H = L, s.C, H if s.C >= 0.002 else 0.0  # keep exact L and hue, gamut-clipped chroma
        return s

    @property
    def oklch(self) -> str:
        return css(self.L, self.C, self.H)


def dist(a: Swatch, b: Swatch) -> float:
    ah, bh = math.radians(a.H), math.radians(b.H)
    return math.dist((a.L, a.C * math.cos(ah), a.C * math.sin(ah)), (b.L, b.C * math.cos(bh), b.C * math.sin(bh)))


# ----------------------------------------------------------------------------- extraction

def load(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    return im.convert("RGB")


def extract(im: Image.Image, count: int) -> list[Swatch]:
    small = im.copy()
    small.thumbnail((320, 320))
    q = small.quantize(colors=max(count * 3, 16), method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    total = small.width * small.height
    raw = sorted(q.getcolors(), reverse=True)  # [(pixels, index)], most frequent first
    swatches: list[Swatch] = []
    for n, idx in raw:
        s = Swatch(tuple(pal[idx * 3: idx * 3 + 3]), n / total)
        twin = next((t for t in swatches if dist(t, s) < 0.035), None)  # merge near-duplicates (anti-aliasing, jpeg noise)
        if twin:
            twin.share += s.share
        else:
            swatches.append(s)
    swatches.sort(key=lambda s: s.share, reverse=True)
    return swatches[:count]


def pick_roles(pal: list[Swatch]) -> dict[str, Swatch]:
    paper = pal[0]
    dark = paper.L < 0.5
    sign = 1 if dark else -1  # direction from paper toward ink

    candidates = [s for s in pal[1:] if contrast(s.rgb, paper.rgb) >= 7 and s.C < 0.08]
    ink = max(candidates, key=lambda s: s.share) if candidates else \
        Swatch.lch(0.93 if dark else 0.22, min(paper.C, 0.02), paper.H, "derived: no 7:1 text colour in the image")

    # accent: chroma matters most, but a colour covering 0.1% of the screen is noise
    chromatic = [s for s in pal if s is not paper and s is not ink and s.C >= 0.06 and s.share >= 0.004]
    if chromatic:
        accent = max(chromatic, key=lambda s: s.C * (0.6 + min(s.share, 0.15) * 4))
    else:
        accent = Swatch.lch(0.72 if dark else 0.55, 0.14, paper.H if paper.C > 0.01 else 45, "derived: image is near-neutral")

    near = [s for s in pal if s not in (paper, ink, accent) and 0.03 <= abs(s.L - paper.L) <= 0.16 and s.C < 0.06]
    line = near[0] if near else Swatch.lch(paper.L + sign * 0.12, paper.C, paper.H, "derived: paper toward ink")

    deep = Swatch.lch(accent.L, accent.C, accent.H, "derived: accent passing 4.5:1 on paper")
    for _ in range(60):
        if contrast(deep.rgb, paper.rgb) >= 4.5:
            break
        deep = Swatch.lch(deep.L + sign * 0.01, accent.C, accent.H, deep.source)
    return {
        "paper": paper,
        "paper-2": Swatch.lch(paper.L + sign * 0.03, paper.C + 0.004, paper.H, "derived: paper, one step in"),
        "ink": ink,
        "ink-2": Swatch.lch(ink.L - sign * 0.25, ink.C, ink.H, "derived: ink toward paper, for secondary text"),
        "line": line,
        "accent": accent,
        "accent-deep": deep,
        "accent-tint": Swatch.lch(paper.L + sign * 0.04, min(0.05, accent.C), accent.H, "derived: paper tinted with accent"),
    }


# ----------------------------------------------------------------------------- output

def theme_block(roles: dict[str, Swatch], image: str) -> str:
    lines = [f"/* Palette borrowed from {image}: mood only. Re-check every pair with web-a11y-color-contrast. */",
             "@theme {"]
    for name, s in roles.items():
        note = f"{hexs(s.rgb)}, {s.share * 100:.1f}% of the screenshot" if s.source == "image" else f"{hexs(s.rgb)}, {s.source}"
        lines.append(f"  --color-{name + ':':<13} {s.oklch + ';':<28} /* {note} */")
    lines.append("}")
    return "\n".join(lines) + "\n"


def thumb_uri(im: Image.Image) -> str:
    t = im.copy()
    t.thumbnail((640, 640))
    buf = io.BytesIO()
    t.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def preview_html(im: Image.Image, image: str, pal: list[Swatch], roles: dict[str, Swatch], theme: str) -> str:
    r = {k: hexs(v.rgb) for k, v in roles.items()}
    role_of = {id(v): k for k, v in roles.items()}
    chips = "\n".join(
        f'<li><span class="chip" style="background:{hexs(s.rgb)}"></span><b>{hexs(s.rgb)}</b> {s.oklch}'
        f'<br><small>{s.share * 100:.1f}% of screen{" &middot; " + role_of[id(s)] if id(s) in role_of else ""}</small></li>' for s in pal)
    role_rows = "\n".join(
        f'<tr><td><span class="chip" style="background:{hexs(s.rgb)}"></span></td><td><code>--color-{k}</code></td>'
        f'<td>{s.oklch}</td><td>{contrast(s.rgb, roles["paper"].rgb):.2f}:1</td><td>{html.escape(s.source)}</td></tr>' for k, s in roles.items())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Palette from {html.escape(image)}</title>
<style>
  body {{ margin: 0; font: 15px/1.5 system-ui, sans-serif; background: #f6f6f4; color: #1d1d1b; }}
  main {{ max-width: 72rem; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  h1 {{ font-size: 1.5rem; margin: 0 0 .25rem; }} h2 {{ font-size: 1rem; margin: 2.5rem 0 .75rem; }}
  .cols {{ display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr)); align-items: start; }}
  img {{ max-width: 100%; border: 1px solid #ddd; }}
  ul {{ list-style: none; padding: 0; margin: 0; display: grid; gap: .75rem; grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr)); }}
  .chip {{ display: inline-block; width: 1.75rem; height: 1.75rem; border-radius: 4px; vertical-align: middle; margin-right: .5rem; box-shadow: inset 0 0 0 1px #0002; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; }} td {{ padding: .35rem .5rem; border-top: 1px solid #ddd; }}
  .scroll {{ overflow-x: auto; }}
  .demo {{ background: {r['paper']}; color: {r['ink']}; padding: 2rem; border: 1px solid {r['line']}; }}
  .demo .band {{ background: {r['paper-2']}; border-top: 1px solid {r['line']}; padding: 1.25rem; margin-top: 1.5rem; }}
  .demo h3 {{ font-size: 1.75rem; line-height: 1.15; margin: .25rem 0 .5rem; }}
  .demo p {{ color: {r['ink-2']}; max-width: 36rem; }}
  .demo .eyebrow {{ color: {r['accent-deep']}; font: 12px ui-monospace, monospace; letter-spacing: .15em; text-transform: uppercase; }}
  .demo a {{ color: {r['accent-deep']}; }}
  .demo button {{ background: {r['accent']}; color: {r['paper'] if contrast(roles['accent'].rgb, roles['paper'].rgb) >= contrast(roles['accent'].rgb, roles['ink'].rgb) else r['ink']}; border: 0; padding: .65rem 1.1rem; border-radius: 6px; font: inherit; }}
  .demo .ghost {{ background: {r['accent-tint']}; color: {r['ink']}; box-shadow: inset 0 0 0 1px {r['line']}; }}
  pre {{ background: #fff; border: 1px solid #ddd; padding: 1rem; overflow-x: auto; font-size: 12.5px; }}
</style>
</head>
<body>
<main>
  <h1>Palette from {html.escape(image)}</h1>
  <p>Borrow the mood, never the content, layout or logo. Every role below is a starting point: check it against your own content.</p>
  <div class="cols">
    <div><h2>Source</h2><img src="{thumb_uri(im)}" alt="The screenshot the palette was taken from"></div>
    <div><h2>Roles applied to a sample block</h2>
      <div class="demo">
        <div class="eyebrow">01 &middot; Sample</div>
        <h3>A heading set in ink on paper.</h3>
        <p>Secondary text uses ink-2. Links and small labels use <a href="#">accent-deep</a>, which is adjusted to pass 4.5:1 on paper.</p>
        <button type="button">Primary action</button> <button type="button" class="ghost">Secondary</button>
        <div class="band">A paper-2 band with a line border on top.</div>
      </div>
    </div>
  </div>
  <h2>Roles</h2>
  <div class="scroll"><table><tr><td></td><td><b>token</b></td><td><b>value</b></td><td><b>vs paper</b></td><td><b>from</b></td></tr>
{role_rows}
  </table></div>
  <h2>Every colour found, by share of the screen</h2>
  <ul>
{chips}
  </ul>
  <h2>@theme block</h2>
  <pre>{html.escape(theme)}</pre>
</main>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--count", type=int, default=6, help="colours to keep after merging near-duplicates (default 6)")
    ap.add_argument("--out", help="write the @theme block to this .css file (preview goes next to it as .html)")
    ap.add_argument("--preview", help="path for the HTML swatch preview (default: palette-preview.html, or <out>.html)")
    a = ap.parse_args(argv)
    src = Path(a.image)
    if not src.is_file():
        print(f"error: {src} not found", file=sys.stderr)
        return 2
    im = load(src)
    pal = extract(im, max(3, min(a.count, 16)))
    roles = pick_roles(pal)
    theme = theme_block(roles, src.name)

    print(f"{src.name}: {im.width}x{im.height}, {len(pal)} colours after merging near-duplicates\n")
    for s in pal:
        print(f"  {hexs(s.rgb)}  {s.oklch:<26} {s.share * 100:5.1f}%")
    print()
    for k in ("ink", "ink-2", "accent", "accent-deep"):
        print(f"  {k:<12} on paper: {contrast(roles[k].rgb, roles['paper'].rgb):5.2f}:1")
    print("\n" + theme)

    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(theme, encoding="utf-8", newline="\n")
        print(f"wrote {out}")
    prev = Path(a.preview) if a.preview else (Path(a.out).with_suffix(".html") if a.out else Path("palette-preview.html"))
    prev.parent.mkdir(parents=True, exist_ok=True)
    prev.write_text(preview_html(im, src.name, pal, roles, theme), encoding="utf-8", newline="\n")
    print(f"wrote {prev}  (open it in a browser to see the roles applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
