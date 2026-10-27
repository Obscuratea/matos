"""Offline preview of the MatOS window decoration: real Aurorae button SVGs (all states) on mock
windows that imitate the Rounded Corners effect (squircle-ish radius, hairline outline, glass
highlight, soft shadow). Usage: python3 deco_preview.py AURORAE_DIR OUT.png"""
import io, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.expanduser("~/Projects/matos/tools"))
import palette as P
import gen_kwin

DIR, OUT = sys.argv[1], sys.argv[2]
S = 2
FONT = os.path.expanduser("~/.local/share/fonts/matos/RobotoFlex.ttf")


def rgb(h, a=255):
    return tuple(round(c * 255) for c in P.hex_rgb(h)) + (a,)


def btn(variant, kind, state):
    p = subprocess.run(["rsvg-convert", "-i", f"{state}-center", "-z", str(S), f"{DIR}/{variant}/{kind}.svg"], capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGBA")


def font(sz, w=500):
    f = ImageFont.truetype(FONT, sz * S)
    try:
        f.set_variation_by_axes([w if a["name"] == b"Weight" else a["default"] for a in f.get_variation_axes()])
    except Exception:
        pass
    return f


def window(canvas, x, y, w, h, variant, active, states):
    dark = variant.endswith("Dark")
    s = P.scheme(P.DEFAULT_SEED, dark)
    k = dict(gen_kwin.settings(P.DEFAULT_SEED, dark))
    r = gen_kwin.RADIUS * S
    X, Y, W, H = x * S, y * S, w * S, h * S
    # shadow
    sz = k[("Round-Corners", "ShadowSize" if active else "InactiveShadowSize")] * S
    alpha = k[("Round-Corners", "ActiveShadowAlpha" if active else "InactiveShadowAlpha")]
    sh = Image.new("RGBA", canvas.size)
    ImageDraw.Draw(sh).rounded_rectangle([X, Y + sz // 6, X + W, Y + H + sz // 6], r, fill=(0, 0, 0, alpha))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(sz / 3)))
    # body
    win = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(win)
    th = 38 * S
    d.rectangle([0, 0, W, H], fill=rgb(s["surface"]))
    d.rectangle([0, 0, W, th + 44 * S], fill=rgb(s["surface_container"]))   # title bar + toolbar, one surface
    d.rectangle([0, th + 44 * S, 190 * S, H], fill=rgb(s["surface_container_low"]))  # sidebar
    ink = rgb(s["on_surface"], 255 if active else 120)
    title = "Documents — Dolphin"
    f = font(13, 600)
    tw = d.textlength(title, font=f)
    d.text(((W - tw) / 2, (th - 13 * S * 1.2) / 2), title, font=f, fill=ink)
    bx = W - 10 * S
    for kind in ("close", "maximize", "minimize"):
        im = btn(variant, kind, states.get(kind, "active" if active else "inactive"))
        bx -= im.width
        win.alpha_composite(im, (bx, (th - im.height) // 2))
        bx -= 6 * S
    # toolbar pills + sidebar + content rows
    for i, lab in enumerate(["Back", "Forward", "Search"]):
        d.rounded_rectangle([(12 + i * 92) * S, th + 6 * S, (12 + i * 92 + 84) * S, th + 36 * S], 15 * S, fill=rgb(s["surface_container_highest"]))
        d.text(((26 + i * 92) * S, th + 12 * S), lab, font=font(12), fill=rgb(s["on_surface_variant"]))
    for i, lab in enumerate(["Home", "Documents", "Downloads", "Pictures"]):
        yy = th + (56 + i * 34) * S
        if i == 1:
            d.rounded_rectangle([8 * S, yy - 6 * S, 182 * S, yy + 22 * S], 10 * S, fill=rgb(s["primary_container"]))
        d.text((24 * S, yy), lab, font=font(12, 600 if i == 1 else 450),
               fill=rgb(s["on_primary_container"] if i == 1 else s["on_surface"]))
    for i in range(5):
        yy = th + (58 + i * 30) * S
        d.text((210 * S, yy), f"report-{i + 1}.pdf", font=font(12), fill=rgb(s["on_surface"]))
    # squircle-ish mask (rounded rect) + outlines
    mask = Image.new("L", (W, H))
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], r, fill=255)
    canvas.paste(win, (X, Y), mask)
    o = ImageDraw.Draw(canvas)
    oa = k[("Round-Corners", "ActiveOutlineAlpha" if active else "InactiveOutlineAlpha")]
    o.rounded_rectangle([X, Y, X + W - 1, Y + H - 1], r, outline=rgb(s["outline_variant"], oa), width=S)
    if k[("Round-Corners", "SecondOutlineThickness")]:
        ia = k[("Round-Corners", "ActiveSecondOutlineAlpha" if active else "InactiveSecondOutlineAlpha")]
        hl = Image.new("RGBA", canvas.size)
        ImageDraw.Draw(hl).rounded_rectangle([X + S, Y + S, X + W - 1 - S, Y + H - 1 - S], r - S, outline=(255, 255, 255, ia), width=S)
        canvas.alpha_composite(hl)


Wd, Hd = 1180, 860
img = Image.new("RGBA", (Wd * S, Hd * S))
g = ImageDraw.Draw(img)
for i in range(Hd * S):
    t = i / (Hd * S)
    g.line([(0, i), (Wd * S, i)], fill=(int(120 - 60 * t), int(96 - 60 * t), int(190 - 90 * t), 255))
for row, variant in enumerate(("MatOSDark", "MatOSLight")):
    y = 30 + row * 420
    window(img, 30, y + 10, 540, 360, variant, False, {})
    window(img, 610, y, 540, 360, variant, True, {"close": "hover", "maximize": "active", "minimize": "pressed"})
img.convert("RGB").save(OUT)
print(OUT)
