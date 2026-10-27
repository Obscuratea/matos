#!/usr/bin/env python3
"""MatOS wallpaper: blurred tonal colour fields + crisp glass M3 Expressive shapes + fine grain.

Writes a Plasma wallpaper package (contents/images = light, contents/images_dark = dark).
Shapes are laid out relative to the shorter screen side so ultrawide and portrait both work.
Usage: gen_wallpaper.py [outdir] [--seed HEX] [--sizes 3440x1440,1440x2560,...]
"""
import argparse, io, json, math, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P
from PIL import Image

SIZES = ["3840x2160", "3440x1440", "2560x1440", "1920x1080", "1440x2560"]


def cookie(cx, cy, r, lobes, depth, rot=0, steps=360):
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        rr = r * (1 - depth + depth * math.cos(lobes * (a + rot)))
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + "Z"


def svg(w, h, seed, dark):
    s = P.scheme(seed, dark)
    pal = P.tonal_palettes(seed)
    u = min(w, h) * (0.8 if h > w else 1)  # layout unit; smaller on portrait so the pill stays on screen
    cx, cy = w * 0.62, h * 0.5        # cluster sits right of centre (windows usually open left/centre)
    if h > w:                          # portrait: cluster lower-centre
        cx, cy = w * 0.5, h * 0.62
    base_top, base_bot = (pal["neutral"](8), pal["primary"](12)) if dark else (pal["neutral"](97), pal["primary"](90))
    t = (lambda x: x) if dark else (lambda x: x)
    blob = lambda col, x, y, r, op: f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{col}" fill-opacity="{op}"/>'
    lav, orch, pink = (pal["primary"](55 if dark else 75), pal["gradient"](50 if dark else 78), pal["tertiary"](45 if dark else 82))
    blobs = "".join([
        blob(lav, cx - 0.55 * u, cy - 0.35 * u, 0.60 * u, .55 if dark else .65),
        blob(orch, cx + 0.45 * u, cy + 0.30 * u, 0.55 * u, .50 if dark else .55),
        blob(pink, cx - 0.10 * u, cy + 0.55 * u, 0.40 * u, .35 if dark else .45),
        blob(lav, cx + 0.70 * u, cy - 0.55 * u, 0.35 * u, .30),
    ])
    g0, g1 = (s["gradient_start"], s["gradient_end"])
    hi = "#ffffff"
    glass_op = .22 if dark else .38
    shapes = [
        # (path, fill gradient opacity)
        cookie(cx + 0.10 * u, cy - 0.04 * u, 0.24 * u, 9, 0.07, rot=0.2),
        f"M{cx - 0.42 * u:.0f},{cy + 0.06 * u:.0f} h{0.34 * u:.0f} a{0.07 * u:.0f},{0.07 * u:.0f} 0 0 1 0,{0.14 * u:.0f} "
        f"h{-0.34 * u:.0f} a{0.07 * u:.0f},{0.07 * u:.0f} 0 0 1 0,{-0.14 * u:.0f} Z",
    ]
    circ = (cx + 0.36 * u, cy + 0.22 * u, 0.09 * u)
    glass = "".join(
        f'<path d="{d}" fill="url(#gl)" fill-opacity="{glass_op}"/>'
        f'<path d="{d}" fill="none" stroke="url(#edge)" stroke-width="{max(1.5, u / 600):.1f}"/>' for d in shapes)
    glass += (f'<circle cx="{circ[0]:.0f}" cy="{circ[1]:.0f}" r="{circ[2]:.0f}" fill="url(#gl)" fill-opacity="{glass_op + .1}"/>'
              f'<circle cx="{circ[0]:.0f}" cy="{circ[1]:.0f}" r="{circ[2]:.0f}" fill="none" stroke="url(#edge)" stroke-width="{max(1.5, u / 600):.1f}"/>')
    # the MatOS mark, small and quiet, as three pills inside the cookie
    m = 0.05 * u
    mx, my = cx + 0.10 * u - 1.4 * m, cy - 0.04 * u - 1.25 * m
    pill = lambda x, hgt, col, op: (f'<rect x="{mx + x * m:.1f}" y="{my:.1f}" width="{0.75 * m:.1f}" height="{hgt * m:.1f}" '
                                    f'rx="{0.375 * m:.1f}" fill="{col}" fill-opacity="{op}"/>')
    ink = hi if dark else s["on_surface"]
    mark = pill(0, 2.35, ink, .55) + pill(1.025, 1.45, s["accent"], .9) + pill(2.05, 2.35, ink, .55)
    blur = 0.18 * u
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1"><stop stop-color="{base_top}"/><stop offset="1" stop-color="{base_bot}"/></linearGradient>
  <linearGradient id="gl" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{g0}"/><stop offset="1" stop-color="{g1}"/></linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="0.6" y2="1"><stop stop-color="{hi}" stop-opacity=".7"/><stop offset=".5" stop-color="{hi}" stop-opacity=".08"/><stop offset="1" stop-color="{hi}" stop-opacity=".25"/></linearGradient>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{blur:.0f}"/></filter>
</defs>
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<g filter="url(#soft)">{blobs}</g>
{glass}
{mark}
</svg>'''


def render(w, h, seed, dark):
    # blur is the slow part: render at half size, upscale (it's soft anyway), then the crisp layer full size
    p = subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-"], input=svg(w, h, seed, dark).encode(),
                       capture_output=True, check=True)
    img = Image.open(io.BytesIO(p.stdout)).convert("RGB")
    noise = Image.effect_noise((w, h), 18).convert("RGB")      # fine grain keeps big gradients from banding
    return Image.blend(img, noise, 0.025 if dark else 0.02)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir", nargs="?", default="build/wallpapers/MatOS")
    ap.add_argument("--seed")
    ap.add_argument("--sizes", default=",".join(SIZES))
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    root = pathlib.Path(a.outdir)
    for sub, dark in (("images", False), ("images_dark", True)):
        d = root / "contents" / sub
        d.mkdir(parents=True, exist_ok=True)
        for size in a.sizes.split(","):
            w, h = map(int, size.split("x"))
            render(w, h, seed, dark).save(d / f"{w}x{h}.png", optimize=True)
            print("wrote", d / f"{w}x{h}.png")
    shot = render(640, 360, seed, True)
    shot.save(root / "contents" / "screenshot.png")
    meta = {"KPlugin": {"Authors": [{"Name": "MatOS"}], "Id": "MatOS", "License": "MIT", "Name": "MatOS"}}
    (root / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")


if __name__ == "__main__":
    main()
