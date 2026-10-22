---
name: web-pwa-app-icons-splash
description: Produce every icon a PWA needs (favicon, 192/512 any, 192/512 maskable with safe zone, 180 apple-touch-icon, monochrome badge) and iOS splash screens with matching `apple-touch-startup-image` tags, generated from one 1024 px PNG by a Pillow script. Use when a user says "app icon", "home screen icon looks cropped", "maskable icon", "splash screen", "iOS launch image" or "generate icon sizes".
---

# App icons and splash screens

Android masks icons into circles, squircles and rounded squares, so a flat icon with art at the edges gets cropped; a maskable icon keeps its art inside the central 80 percent and fills the rest with a solid colour. iOS ignores the manifest for its launch screen and needs one PNG per device size linked with media queries. Doing this by hand is twenty exports and a typo; one script from a single 1024 px source is repeatable and runs in CI.

## Pattern

```bash
python -m pip install "pillow==11.1.0"
python scripts/icons.py design/icon-1024.png "#0f766e" "#f8fafc"
#                        source (square, transparent bg)  maskable fill  splash background
```

```python
# scripts/icons.py
import sys, pathlib
from PIL import Image

src_path, mask_fill, splash_bg = sys.argv[1], sys.argv[2], sys.argv[3]
out = pathlib.Path("public/icons"); out.mkdir(parents=True, exist_ok=True)
splash_dir = pathlib.Path("public/splash"); splash_dir.mkdir(parents=True, exist_ok=True)
src = Image.open(src_path).convert("RGBA")

def square(size, pad=0.0, fill=None):
    """Resize src into a size x size canvas; pad is the fraction of width kept clear on each side."""
    canvas = Image.new("RGBA", (size, size), fill or (0, 0, 0, 0))
    inner = round(size * (1 - 2 * pad))
    art = src.resize((inner, inner), Image.LANCZOS)
    canvas.alpha_composite(art, ((size - inner) // 2, (size - inner) // 2))
    return canvas

for s in (192, 512):                                   # purpose "any"
    square(s).save(out / f"icon-{s}.png", optimize=True)
for s in (192, 512):                                   # purpose "maskable": art inside the central 80 %
    square(s, pad=0.1, fill=mask_fill).convert("RGB").save(out / f"maskable-{s}.png", optimize=True)
square(180, pad=0.06, fill=mask_fill).convert("RGB").save(out / "apple-touch-icon.png", optimize=True)
square(96, pad=0.1, fill=mask_fill).save(out / "shortcut-new.png", optimize=True)
# monochrome badge for Android notification bar: white art on transparent
badge = square(96, pad=0.1); white = Image.new("RGBA", badge.size, (255, 255, 255, 255)); white.putalpha(badge.getchannel("A"))
white.save(out / "badge-96.png", optimize=True)
square(32).save(out.parent / "favicon.ico", sizes=[(16, 16), (32, 32)])

# iOS splash: (css width, css height, device pixel ratio) for current devices; add rows as Apple ships new sizes
DEVICES = [(430, 932, 3), (393, 852, 3), (428, 926, 3), (390, 844, 3), (375, 812, 3), (414, 896, 3), (414, 896, 2),
           (375, 667, 2), (1024, 1366, 2), (834, 1194, 2), (820, 1180, 2), (834, 1112, 2), (810, 1080, 2), (768, 1024, 2)]
tags = []
for w, h, r in DEVICES:
    for orient, (pw, ph) in (("portrait", (w * r, h * r)), ("landscape", (h * r, w * r))):
        canvas = Image.new("RGB", (pw, ph), splash_bg)
        icon_size = round(min(pw, ph) * 0.25)              # icon at a quarter of the short edge
        art = src.resize((icon_size, icon_size), Image.LANCZOS)
        canvas.paste(art, ((pw - icon_size) // 2, (ph - icon_size) // 2), art)
        name = f"splash-{pw}x{ph}.png"
        canvas.save(splash_dir / name, optimize=True)
        tags.append(f'<link rel="apple-touch-startup-image" href="/splash/{name}" '
                    f'media="(device-width: {w}px) and (device-height: {h}px) and (-webkit-device-pixel-ratio: {r}) and (orientation: {orient})">')
pathlib.Path("src/partials/splash-links.html").write_text("\n".join(tags) + "\n", encoding="utf-8")
print(f"wrote {len(tags)} splash images and tags")
```

Include the generated tags in `<head>` (every page the app can start on), together with the manifest and icon links from `web-pwa-manifest`:

```html
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes"><!-- required or iOS ignores startup images -->
<!-- build step pastes src/partials/splash-links.html here -->
```

Android needs no splash files: Chrome composes one from `background_color`, `name` and the 512 px icon in the manifest.

## Variations

- **SVG source**: Pillow cannot rasterise SVG. Export a 1024 px PNG from your design tool, or rasterise once with `npx -y @resvg/resvg-js-cli` and feed the PNG to the script.
- **Dark splash on iOS**: generate a second set with the dark background and add `and (prefers-color-scheme: dark)` to those media queries; iOS 17+ honours it.
- **Windows and Linux desktop installs**: Chromium uses the 512 px `any` icon; add a 256 px entry if the 512 looks soft in the taskbar. No `.ico` beyond the favicon is needed.
- **Safari pinned tab / macOS Dock**: Safari uses `apple-touch-icon` for the Dock when installing from the File menu; an `svg` `rel="icon"` covers tabs (`web-design-icons` for the favicon itself).

## Pitfalls

- `"purpose": "any maskable"` on one file makes the plain icon look shrunken on desktop and in the install dialog. Ship separate files and separate manifest entries.
- The maskable safe zone is a circle of radius 40 percent of the width; 10 percent padding on each side is the minimum, and logos with thin edges need 15 to 20. Check with the Maskable section in DevTools > Application > Manifest, which previews each platform mask.
- An `apple-touch-icon` with transparency gets a black background on iOS; the script fills it for that reason.
- iOS matches startup images on exact `device-width`, `device-height`, pixel ratio and orientation; a mismatch means a white flash. Regenerate when a new iPhone size ships and keep the `DEVICES` table in version control.
- Startup images are only used when `apple-mobile-web-app-capable` is `yes` and the page was added to the Home Screen from Safari; a plain tab never shows them.
- Caching: give `/icons/*` and `/splash/*` a long `Cache-Control` and change the filename (not just the pixels) when you redesign, or installed apps keep the old icon until reinstall (`web-perf-caching-and-service-worker`).

## Related skills

- `web-pwa-manifest`
- `web-pwa-install-prompt`
- `web-design-icons`
- `web-design-dark-mode`
- `web-perf-images`
- `web-perf-caching-and-service-worker`
