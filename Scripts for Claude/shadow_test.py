"""Render one frame's shadow alone on white (assembled like Plasma's FrameSvg), contrast-boosted
so seams between tiles show. Usage: python3 shadow_test.py SVG OUT.png"""
import io, subprocess, sys
from PIL import Image, ImageOps

SVG, OUT, Z = sys.argv[1], sys.argv[2], 4

def piece(eid):
    p = subprocess.run(["rsvg-convert", "-i", eid, "-z", str(Z), SVG], capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGBA")

g = {n: piece(f"shadow-{n}") for n in ("topleft", "topright", "bottomleft", "bottomright", "top", "bottom", "left", "right")}
hint = {s: piece(f"shadow-hint-{s}-margin") for s in ("top", "bottom", "left", "right")}
w, h = 160 * Z, 100 * Z
t, b, l, r = hint["top"].height, hint["bottom"].height, hint["left"].width, hint["right"].width
W, H = w + l + r, h + t + b
c = g["topleft"].width
img = Image.new("RGBA", (W, H), "white")
img.alpha_composite(g["topleft"], (0, 0)); img.alpha_composite(g["topright"], (W - c, 0))
img.alpha_composite(g["bottomleft"], (0, H - c)); img.alpha_composite(g["bottomright"], (W - c, H - c))
img.alpha_composite(g["top"].resize((W - 2 * c, c)), (c, 0)); img.alpha_composite(g["bottom"].resize((W - 2 * c, c)), (c, H - c))
img.alpha_composite(g["left"].resize((c, H - 2 * c)), (0, c)); img.alpha_composite(g["right"].resize((c, H - 2 * c)), (W - c, c))
out = ImageOps.autocontrast(img.convert("L"), cutoff=0)
out.save(OUT)
print(OUT, "tile", c, "hints", t, b, l, r)
