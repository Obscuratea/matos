"""Offline preview of the MatOS Plasma style: exports 9-patch pieces with rsvg-convert and
assembles them the way KSvg/FrameSvg does, over a wallpaper. Not pixel-identical to Plasma
(no real blur, colours are the SVGs' built-in dark defaults), but shows geometry and shading.

Usage: python3 plasma_preview.py THEME_DIR OUT.png
"""
import io, os, subprocess, sys, functools
from PIL import Image, ImageDraw, ImageFilter, ImageFont

THEME, OUT = sys.argv[1], sys.argv[2]
S = 2  # render scale


@functools.lru_cache(None)
def piece(rel, eid):
    p = subprocess.run(["rsvg-convert", "-i", eid, "-z", str(S), os.path.join(THEME, rel + ".svg")], capture_output=True)
    if p.returncode or not p.stdout:
        return None
    return Image.open(io.BytesIO(p.stdout)).convert("RGBA")


def nine(canvas, rel, pre, x, y, w, h, shadow=False):
    """Shadow like Plasma: tiles drawn around the frame expanded by the shadow-hint-*-margin sizes."""
    x, y, w, h = x * S, y * S, w * S, h * S
    g = lambda n: piece(rel, f"{pre}{n}")
    if shadow and g("shadow-topleft"):
        hint = lambda side: piece(rel, f"{pre}shadow-hint-{side}-margin")
        t, b = hint("top").height, hint("bottom").height
        l, r = hint("left").width, hint("right").width
        sh = Image.new("RGBA", (w + l + r, h + t + b))
        nine_into(sh, lambda n: g("shadow-" + n), 0, 0, w + l + r, h + t + b, outside=True)
        canvas.alpha_composite(sh, (x - l, y - t))
    nine_into(canvas, g, x, y, w, h)


def nine_into(canvas, g, x, y, w, h, outside=False, s=0):
    tl, tr, bl, br = g("topleft"), g("topright"), g("bottomleft"), g("bottomright")
    if tl is None:
        return
    cw, ch = tl.size
    if outside:  # shadow: corners sit outside a (w-2s)x(h-2s) frame, centre empty
        pass
    top, bot, lef, rig, cen = g("top"), g("bottom"), g("left"), g("right"), g("center")
    canvas.alpha_composite(tl, (x, y)); canvas.alpha_composite(tr, (x + w - cw, y))
    canvas.alpha_composite(bl, (x, y + h - ch)); canvas.alpha_composite(br, (x + w - cw, y + h - ch))
    if w - 2 * cw > 0:
        canvas.alpha_composite(top.resize((w - 2 * cw, ch)), (x + cw, y))
        canvas.alpha_composite(bot.resize((w - 2 * cw, ch)), (x + cw, y + h - ch))
    if h - 2 * ch > 0:
        canvas.alpha_composite(lef.resize((cw, h - 2 * ch)), (x, y + ch))
        canvas.alpha_composite(rig.resize((cw, h - 2 * ch)), (x + w - cw, y + ch))
    if cen is not None and not outside and w - 2 * cw > 0 and h - 2 * ch > 0:
        canvas.alpha_composite(cen.resize((w - 2 * cw, h - 2 * ch)), (x + cw, y + ch))


def single(canvas, rel, eid, x, y, w=None, h=None):
    p = piece(rel, eid)
    if p is None:
        print("missing", rel, eid); return
    if w:
        p = p.resize((w * S, h * S))
    canvas.alpha_composite(p, (x * S, y * S))


def font(sz, bold=False):
    f = os.path.expanduser("~/.local/share/fonts/matos/RobotoFlex.ttf")
    ft = ImageFont.truetype(f, sz * S)
    try:
        ft.set_variation_by_axes([700 if bold else 420] + [0] * 0) if False else None
    except Exception:
        pass
    return ft


def txt(d, x, y, s, size=13, fill=(227, 225, 234), bold=False):
    d.text((x * S, y * S), s, font=font(size, bold), fill=fill)


W, H = 1000, 560
img = Image.new("RGBA", (W * S, H * S))
d = ImageDraw.Draw(img)
for i in range(H * S):  # wallpaper: purple -> dark -> orchid
    t = i / (H * S)
    c = tuple(int(a + (b - a) * t) for a, b in zip((82, 52, 142), (60, 30, 70)))
    d.line([(0, i), (W * S, i)], fill=c + (255,))
blob = Image.new("RGBA", img.size)
ImageDraw.Draw(blob).ellipse([700 * S, 300 * S, 1050 * S, 650 * S], fill=(210, 154, 247, 140))
ImageDraw.Draw(blob).ellipse([-100 * S, 60 * S, 260 * S, 400 * S], fill=(186, 162, 255, 110))
img.alpha_composite(blob.filter(ImageFilter.GaussianBlur(40 * S)))
bg_blur = img.filter(ImageFilter.GaussianBlur(18 * S))  # fake KWin blur


def glass(rel, pre, x, y, w, h, shadow=True):
    """Fake blur-behind: paste blurred wallpaper through the frame's mask, then the frame."""
    mask = Image.new("RGBA", img.size)
    nine_into(mask, lambda n: piece(rel, f"mask-{pre}{n}"), x * S, y * S, w * S, h * S)
    if shadow:
        nine(img, rel, pre, x, y, w, h, shadow=True)
    img.paste(bg_blur, (0, 0), mask.split()[3])
    nine_into(img, lambda n: piece(rel, f"{pre}{n}"), x * S, y * S, w * S, h * S)


# floating top bar (29 px, 4 px float margin)
glass("translucent/widgets/panel-background", "", 8, 6, W - 16, 29)
d = ImageDraw.Draw(img)
for i, (x, w, h, accent) in enumerate([(0, 3, 9, False), (4.3, 3, 5.5, True), (8.6, 3, 9, False)]):
    d.rounded_rectangle([(22 + x) * S, 15 * S, (22 + x + w) * S, (15 + h) * S], radius=1.5 * S,
                        fill=(186, 162, 255) if accent else (227, 225, 234))
txt(d, 44, 13, "Files", 13, bold=True)
for i, m in enumerate(["Edit", "View", "Go", "Window"]):
    txt(d, 86 + i * 46, 13, m)
nine_into(img, lambda n: piece("widgets/tasks", f"north-focus-{n}"), 330 * S, 10 * S, 120 * S, 21 * S)
txt(d, 345, 13, "Dolphin", 12, fill=(232, 222, 248))
txt(d, 470, 13, "Konsole", 12)
txt(d, 470 + 300, 13, "Tue 27 Oct  14:32", 13)

# popup (dialogs/background) like the launcher or a menu
px, py, pw, ph = 20, 48, 300, 360
glass("dialogs/background", "", px, py, pw, ph)
d = ImageDraw.Draw(img)
txt(d, px + 18, py + 16, "MatOS", 18, bold=True)
nine_into(img, lambda n: piece("widgets/lineedit", f"focus-{n}"), (px + 16) * S, (py + 48) * S, (pw - 32) * S, 32 * S)
txt(d, px + 30, py + 56, "Search…", 13, fill=(200, 196, 213))
for i, (name, st) in enumerate([("Files", "normal"), ("Konsole", "hover"), ("System Settings", "pressed"), ("Firefox", "normal"), ("Vox Obscurus", "normal")]):
    y = py + 96 + i * 40
    nine_into(img, lambda n: piece("widgets/listitem", f"{st}-{n}"), (px + 10) * S, y * S, (pw - 20) * S, 36 * S)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(px + 22) * S, (y + 8) * S, (px + 42) * S, (y + 28) * S], radius=6 * S, fill=(82, 52, 142))
    txt(d, px + 54, y + 9, name, 13, fill=(232, 222, 248) if st == "pressed" else (227, 225, 234))
y = py + ph - 52
for i, st in enumerate(["normal", "hover"]):
    nine_into(img, lambda n: piece("widgets/button", f"toolbutton-{st}-{n}" if st != "normal" else f"normal-{n}"), (px + 16 + i * 96) * S, y * S, 86 * S, 34 * S)
d = ImageDraw.Draw(img)
txt(d, px + 36, y + 8, "Sleep", 13); txt(d, px + 128, y + 8, "Restart", 13)

# controls on a widget background
cx, cy, cw, ch = 360, 60, 330, 300
glass("widgets/background", "", cx, cy, cw, ch)
d = ImageDraw.Draw(img)
txt(d, cx + 20, cy + 18, "Controls", 16, bold=True)
# buttons
for i, st in enumerate(["normal", "hover", "focus", "pressed"]):
    nine_into(img, lambda n: piece("widgets/button", f"{st}-{n}"), (cx + 20 + i * 74) * S, (cy + 52) * S, 68 * S, 32 * S)
    txt(ImageDraw.Draw(img), cx + 32 + i * 74, cy + 60, st, 11)
# switch on/off
for i, st in enumerate(["active", "inactive"]):
    x0, y0 = cx + 20 + i * 70, cy + 104
    single(img, "widgets/switch", f"{st}-left", x0, y0)
    single(img, "widgets/switch", f"{st}-center", x0 + 11, y0, 18, 22)
    single(img, "widgets/switch", f"{st}-right", x0 + 29, y0)
    single(img, "widgets/switch", "handle", x0 + (18 if st == "active" else 0), y0)
# checkbox / radio
single(img, "widgets/checkmarks", "checkbox", cx + 170, cy + 107)
single(img, "widgets/radiobutton", "normal", cx + 200, cy + 106)
single(img, "widgets/radiobutton", "checked", cx + 226, cy + 106)
# slider
nine_into(img, lambda n: piece("widgets/slider", f"groove-{n}"), (cx + 20) * S, (cy + 150) * S, 280 * S, 4 * S)
nine_into(img, lambda n: piece("widgets/slider", f"groove-highlight-{n}"), (cx + 20) * S, (cy + 150) * S, 170 * S, 4 * S)
single(img, "widgets/slider", "horizontal-slider-hover", cx + 181, cy + 143)
# tabs
nine_into(img, lambda n: piece("widgets/tabbar", f"north-active-tab-{n}"), (cx + 20) * S, (cy + 180) * S, 90 * S, 30 * S)
d = ImageDraw.Draw(img)
txt(d, cx + 40, cy + 187, "General", 12, fill=(232, 222, 248)); txt(d, cx + 130, cy + 187, "Advanced", 12)
# line edit
nine_into(img, lambda n: piece("widgets/lineedit", f"base-{n}"), (cx + 20) * S, (cy + 230) * S, 290 * S, 32 * S)
txt(ImageDraw.Draw(img), cx + 34, cy + 238, "Text field", 13, fill=(200, 196, 213))

# tooltip
glass("widgets/tooltip", "", 720, 60, 200, 64)
txt(ImageDraw.Draw(img), 736, 72, "Tooltip", 13, bold=True)
txt(ImageDraw.Draw(img), 736, 92, "Inverse surface in the real theme", 11, fill=(200, 196, 213))

img.convert("RGB").save(OUT)
print(OUT)
