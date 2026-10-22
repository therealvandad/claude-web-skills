---
name: web-content-images-pipeline
description: Resize original photos to 480, 960 and 1600 px, save WebP (and AVIF when Pillow supports it) and print a ready picture snippet with srcset, sizes, width and height, using a Python 3.10 script with Pillow. Use when a user says "optimize my images", "convert to webp", "avif", "responsive images", "srcset", "resize photos" or "images are too heavy".
---

# Images pipeline

A 4 MB phone photo shown in a 400 px card is the most common reason a static site is slow. Fix it at build time: from each original, make a few widths in modern formats, and serve the right one with `srcset`. The script never upscales, applies the camera's EXIF rotation, keeps originals untouched in their own folder, and skips outputs that are newer than their source, so a second run takes a second. It needs one install: `pip install Pillow`.

## Pattern

```text
originals/roast.jpg  -- python build_images.py originals dist/img -->  dist/img/roast-480.webp, roast-960.avif ...
```

```python
"""Resize originals to 480/960/1600 px, save WebP (+ AVIF if Pillow can), print <picture> snippets.
Usage: python build_images.py originals out_dir [--url-prefix /img] [--sizes 480,960,1600]
Needs: pip install Pillow"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps, features

SOURCES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}

def avif_ok():
    try:
        return bool(features.check("avif"))
    except Exception:                                   # older Pillow without the feature name
        return False

def save(img, path, fmt):
    opts = {"WEBP": {"quality": 80, "method": 6}, "AVIF": {"quality": 55, "speed": 6}}[fmt]
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "transparency" in img.info or img.mode in ("LA", "PA") else "RGB")
    img.save(path, fmt, **opts)

def process(src, out, widths, formats, force):
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)                # honour phone rotation before measuring
        w0, h0 = im.size
        targets = sorted({w for w in widths if w < w0} | ({w0} if w0 <= max(widths) else set()))
        made = {}
        for w in targets:
            h = round(h0 * w / w0)
            small = im if w == w0 else im.resize((w, h), Image.Resampling.LANCZOS)
            for fmt in formats:
                dest = out / f"{src.stem}-{w}.{fmt.lower()}"
                if force or not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
                    save(small, dest, fmt)
            made[w] = h
        return made

def snippet(stem, made, formats, prefix, sizes):
    pick = 960 if 960 in made else max(made)           # the <img> fallback: mid size keeps it light
    srcset = lambda ext: ", ".join(f"{prefix}/{stem}-{w}.{ext} {w}w" for w in made)
    lines = ["<picture>"]
    for fmt in formats[::-1]:                          # AVIF first, then WebP
        lines.append(f'  <source type="image/{fmt.lower()}" srcset="{srcset(fmt.lower())}" sizes="{sizes}">')
    lines.append(f'  <img src="{prefix}/{stem}-{pick}.webp" width="{pick}" height="{made[pick]}" alt="" '
                 f'loading="lazy" decoding="async" class="h-auto w-full">')
    lines.append("</picture>")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("originals", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--url-prefix", default="/img", help="URL folder used in the snippet")
    ap.add_argument("--sizes", default="480,960,1600", help="comma separated widths")
    ap.add_argument("--attr-sizes", default="(min-width: 64rem) 50vw, 100vw", help="value of the sizes attribute")
    ap.add_argument("--force", action="store_true", help="rebuild even if outputs are newer")
    a = ap.parse_args()
    widths = [int(x) for x in a.sizes.split(",")]
    formats = ["WEBP"] + (["AVIF"] if avif_ok() else [])
    if len(formats) == 1:
        print("note: this Pillow build has no AVIF support, writing WebP only")
    a.out.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in a.originals.iterdir() if p.suffix.lower() in SOURCES)
    if not files:
        raise SystemExit(f"no images found in {a.originals}")
    for src in files:
        try:
            made = process(src, a.out, widths, formats, a.force)
        except OSError as err:                          # one broken file should not stop the run
            print(f"skip {src.name}: {err}")
            continue
        print(f"\n<!-- {src.name}: {', '.join(f'{w}px' for w in made)} -->")
        print(snippet(src.stem, made, formats, a.url_prefix.rstrip("/"), a.attr_sizes))

if __name__ == "__main__":
    main()
```

```bash
pip install Pillow
python build_images.py originals dist/img --url-prefix /img     # Windows: py build_images.py ...
```

The script prints markup like this; paste it in and write a real `alt` (empty only when the image is decorative):

```html
<picture>
  <source type="image/avif" srcset="/img/roast-480.avif 480w, /img/roast-960.avif 960w, /img/roast-1600.avif 1600w" sizes="(min-width: 64rem) 50vw, 100vw">
  <source type="image/webp" srcset="/img/roast-480.webp 480w, /img/roast-960.webp 960w, /img/roast-1600.webp 1600w" sizes="(min-width: 64rem) 50vw, 100vw">
  <img src="/img/roast-960.webp" width="960" height="640" alt="" loading="lazy" decoding="async" class="h-auto w-full">
</picture>
```

## Variations

- **Different sizes**: `--sizes 320,640,1280` for thumbnails; `--attr-sizes "(min-width: 48rem) 33vw, 100vw"` when the image fills a third of a grid row.
- **Above the fold**: for the hero image remove `loading="lazy"`, add `fetchpriority="high"`, and keep the `width` and `height` so the layout does not jump.
- **Fixed crop**: for uniform thumbnails use `ImageOps.fit(im, (w, w * 3 // 4))` instead of `resize`, or leave the files and crop in CSS with `aspect-ratio` and `object-cover`.
- **Quality**: lower WebP `quality` to 70 for photos with lots of noise; raise to 90 for product shots with fine text.

## Pitfalls

- `width` and `height` must be the intrinsic size of the `<img src>` file, not the display size; they only reserve the aspect ratio, and Tailwind's `w-full h-auto` does the sizing.
- `sizes` describes how wide the image is displayed, not the file width. A wrong `sizes` makes the browser pick a file that is too big or too soft; the default assumes half the viewport on large screens.
- AVIF encoding is slow at high effort and needs a Pillow built with AVIF (Pillow 11.3 or newer on most platforms). The script falls back to WebP only and says so.
- Do not run the pipeline on its own output, and do not commit giant originals to the repo without Git LFS or a separate assets folder.
- PNG screenshots with flat colours may be smaller as lossless WebP (`lossless=True`) than as lossy; check one before converting a whole folder.
- Transparency survives only if the mode is RGBA, which the script preserves; JPEG is never used as output.

## Related skills

- `web-perf-images`
- `web-design-images`
- `web-a11y-images-and-media`
- `web-content-markdown-pipeline`
- `web-css-aspect-ratio-media`
