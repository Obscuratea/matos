#!/usr/bin/env python3
"""Generate the MatOS Plasma style (desktoptheme): rounded glass frames, Material controls.

Colours are ColorScheme-* classes, so Plasma recolours them from the active MatOS colour
scheme (accent and dark/light follow with no regeneration). Every frame also gets mask-*
pieces (blur follows the rounded shape) and soft shadow-* tiles. Anything not generated
here falls back to Plasma's default theme.
Usage: gen_plasma.py [outdir]
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P

_D = P.scheme(P.DEFAULT_SEED, True)
STYLE = '<style type="text/css" id="current-color-scheme">' + "".join(
    f".ColorScheme-{n}{{color:{c};}}" for n, c in {
        "Text": _D["on_surface"], "Background": _D["surface_container"], "Highlight": _D["primary_container"],
        "HighlightedText": _D["on_primary_container"], "ViewText": _D["on_surface"], "ViewBackground": _D["surface"],
        "ViewHover": _D["primary"], "ViewFocus": _D["primary"], "ButtonText": _D["on_surface"],
        "ButtonBackground": _D["surface_container_high"], "ButtonHover": _D["primary"], "ButtonFocus": _D["primary"],
        "NegativeText": _D["error"], "NeutralText": "#fdba54", "PositiveText": "#80da95",
    }.items()) + "</style>"

TEXT, BG, BTN, VIEW = "ColorScheme-Text", "ColorScheme-Background", "ColorScheme-ButtonBackground", "ColorScheme-ViewBackground"
HL, HL_TEXT, FOCUS, NEU = "ColorScheme-Highlight", "ColorScheme-HighlightedText", "ColorScheme-ButtonFocus", "ColorScheme-NeutralText"
LINE = (TEXT, .10)       # hairline edge on glass
LINE_HI = (TEXT, .28)    # outlined controls

def shadow_defs(r, s):
    """Gradients for a rounded-rect shadow: full strength under the frame's corner radius r,
    fading to nothing s px outside it. Tiles are T = r + s so they tuck under the frame."""
    k = r / (r + s)
    stops = (f'<stop offset="0" stop-opacity="0"/><stop offset="{k:.3f}" stop-opacity=".28"/>'
             f'<stop offset="{k + (1 - k) * .4:.3f}" stop-opacity=".10"/><stop offset="1" stop-opacity="0"/>')
    return (f'<radialGradient id="sc" cx="1" cy="1" r="1">{stops}</radialGradient>'
            f'<linearGradient id="se" x1="0" y1="1" x2="0" y2="0">{stops}</linearGradient>'
            f'<linearGradient id="sv" x1="1" y1="0" x2="0" y2="0">{stops}</linearGradient>')


def paint(p):
    if p is None:
        return 'fill="none"'
    cls, op = p
    return f'class="{cls}" fill="currentColor"' + (f' fill-opacity="{op}"' if op != 1 else "")


def stroke(p, w=1):
    cls, op = p
    return f'class="{cls}" fill="none" stroke="currentColor" stroke-width="{w}"' + (f' stroke-opacity="{op}"' if op != 1 else "")


class Sheet:
    """Elements laid out in rows. Each is <g id> with an invisible bbox rect, body drawn in local coords."""
    def __init__(self, defs="", width=1000):
        self.out, self.x, self.y, self.row_h, self.width, self.defs = [], 0, 0, 0, width, defs

    def el(self, eid, w, h, body=""):
        if self.x + w > self.width:
            self.x, self.y, self.row_h = 0, self.y + self.row_h + 4, 0
        self.out.append(f'<g id="{eid}" transform="translate({self.x},{self.y})">'
                        f'<rect width="{w}" height="{h}" fill="#000" fill-opacity="0"/>{body}</g>')
        self.x += w + 4
        self.row_h = max(self.row_h, h)

    def svg(self):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.y + self.row_h}">\n'
                f'<defs>{STYLE}{self.defs}</defs>\n' + "\n".join(self.out) + "\n</svg>\n")


def write(sh, root, rel):
    d = pathlib.Path(root) / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(sh.svg())


def margins(sh, pre, t, b, l, r, kind="margin"):
    z = lambda v: max(v, 0.001)
    sh.el(f"{pre}hint-top-{kind}", 4, z(t))
    sh.el(f"{pre}hint-bottom-{kind}", 4, z(b))
    sh.el(f"{pre}hint-left-{kind}", z(l), 4)
    sh.el(f"{pre}hint-right-{kind}", z(r), 4)


# transforms that turn a top-left corner drawn in [0,r]^2 into the other corners
FLIP = {"topleft": "", "topright": "translate({r},0) scale(-1,1)",
        "bottomleft": "translate(0,{r}) scale(1,-1)", "bottomright": "translate({r},{r}) scale(-1,-1)"}
EDGE = {"top": ("h", ""), "bottom": ("h", "translate(0,{r}) scale(1,-1)"),
        "left": ("v", ""), "right": ("v", "translate({r},0) scale(-1,1)")}


def rounded(sh, pre, r, fill, border=None, m=None, mask=False):
    """9-patch with radius r. fill/border are (class, opacity) or None."""
    # shapes stay exactly inside the tile (KSvg scales a piece by its bounds): border = filled quarter-ring
    q = f"M0,{r} A{r},{r} 0 0 1 {r},0 L{r},{r} Z"
    ring = f"M0,{r} A{r},{r} 0 0 1 {r},0 V1 A{r - 1},{r - 1} 0 0 0 1,{r} Z"
    for name, t in FLIP.items():
        body = f'<path d="{q}" {paint(fill)}/>' + (f'<path d="{ring}" {paint(border)}/>' if border else "")
        sh.el(f"{pre}{name}", r, r, f'<g transform="{t.format(r=r)}">{body}</g>')
        if mask:
            sh.el(f"mask-{pre}{name}", r, r, f'<g transform="{t.format(r=r)}"><path d="{q}" fill="#000"/></g>')
    for name, (o, t) in EDGE.items():
        w, hh = (8, r) if o == "h" else (r, 8)
        line = (f'<rect width="8" height="1" {paint(border)}/>' if o == "h" else f'<rect width="1" height="8" {paint(border)}/>') if border else ""
        body = f'<rect width="{w}" height="{hh}" {paint(fill)}/>' if o == "h" else f'<rect width="{w}" height="{hh}" {paint(fill)}/>'
        sh.el(f"{pre}{name}", w, hh, f'<g transform="{t.format(r=r)}">{body}{line}</g>')
        if mask:
            sh.el(f"mask-{pre}{name}", w, hh, f'<rect width="{w}" height="{hh}" fill="#000"/>')
    sh.el(f"{pre}center", 8, 8, f'<rect width="8" height="8" {paint(fill)}/>')
    if mask:
        sh.el(f"mask-{pre}center", 8, 8, '<rect width="8" height="8" fill="#000"/>')
    if m is not None:
        t, b, l, rr = m if isinstance(m, tuple) else (m,) * 4
        margins(sh, pre, t, b, l, rr)


def shadow(sh, r, s, offset=3):
    """Soft drop shadow reaching s px past the frame (r = frame radius), shifted down by `offset`.
    Hints are the outward reach; the r px beyond that sit under the frame."""
    t = r + s
    for name, tr in FLIP.items():
        sh.el(f"shadow-{name}", t, t, f'<g transform="{tr.format(r=t)}"><rect width="{t}" height="{t}" fill="url(#sc)"/></g>')
    for name, (o, tr) in EDGE.items():
        if o == "h":
            sh.el(f"shadow-{name}", 8, t, f'<g transform="{tr.format(r=t)}"><rect width="8" height="{t}" fill="url(#se)"/></g>')
        else:  # own horizontal gradient: a rotated strip leaves a float-error transparent row that stretches into a seam
            sh.el(f"shadow-{name}", t, 8, f'<g transform="{tr.format(r=t)}"><rect width="{t}" height="8" fill="url(#sv)"/></g>')
    sh.el("shadow-center", 8, 8)
    margins(sh, "shadow-", s - offset, s + offset, s, s)


# ---------------------------------------------------------------- frames
FRAMES = {  # rel: (radius, content margin, shadow size, thick)
    "dialogs/background": (16, 8, 22, False),
    "widgets/background": (20, 10, 16, False),
    "widgets/panel-background": (14, 3, 12, True),
    "widgets/tooltip": (12, 6, 14, False),
}


def frames(root, folder, alpha):
    pre = f"{folder}/" if folder else ""
    for rel, (r, m, s, thick) in FRAMES.items():
        if folder == "opaque" and rel == "widgets/background":
            continue
        sh = Sheet(shadow_defs(r, s))
        rounded(sh, "", r, (BG, alpha), LINE, (m, m, m + 2, m + 2), mask=True)
        if folder != "opaque":
            shadow(sh, r, s)
        if thick:
            sh.el("thick-center", 32, 32, f'<rect width="32" height="32" {paint((BG, alpha))}/>')
            margins(sh, "thick-", 4, 4, 8, 8)
        write(sh, root, f"{pre}{rel}.svg")


# ---------------------------------------------------------------- controls
def button(root):
    sh = Sheet()
    for pre, fill, bd in (("normal-", (BTN, 1), None), ("hover-", (BTN, 1), (FOCUS, .6)),
                          ("focus-", (BTN, 1), (FOCUS, 1)), ("pressed-", (HL, 1), None),
                          ("toolbutton-hover-", (TEXT, .08), None), ("toolbutton-focus-", None, (FOCUS, 1)),
                          ("toolbutton-pressed-", (HL, 1), None)):
        rounded(sh, pre, 12 if not pre.startswith("tool") else 8, fill, bd, (5, 5, 10, 10) if not pre.startswith("tool") else 5)
    write(sh, root, "widgets/button.svg")


def lineedit(root):
    sh = Sheet()
    sh.el("hint-focus-over-base", 2, 2)
    for pre, fill, bd in (("base-", (VIEW, 1), (TEXT, .18)), ("hover-", (VIEW, 1), (TEXT, .40)), ("focus-", (VIEW, 1), (FOCUS, 1))):
        rounded(sh, pre, 10, fill, bd, (5, 5, 10, 10))
    rounded(sh, "focusframe-", 10, None, None, 0)
    write(sh, root, "widgets/lineedit.svg")


def frame(root):
    sh = Sheet()
    rounded(sh, "plain-", 12, None, LINE, 4)
    rounded(sh, "sunken-", 12, (VIEW, 1), LINE, 4)
    rounded(sh, "raised-", 12, (BTN, 1), None, 4)
    write(sh, root, "widgets/frame.svg")


def tabbar(root):
    sh = Sheet()
    for orient in ("north", "south", "west", "east"):
        rounded(sh, f"{orient}-active-tab-", 10, (HL, 1), None, (6, 6, 10, 10))
    write(sh, root, "widgets/tabbar.svg")


def scrollbar(root):
    sh = Sheet()
    sh.el("hint-scrollbar-size", 10, 10)
    for pre in ("background-vertical-", "background-horizontal-"):
        rounded(sh, pre, 4, None)
        margins(sh, pre, 2, 2, 2, 2, "inset")
    for pre, fill in (("slider-", (TEXT, .32)), ("mouseover-slider-", (TEXT, .55))):
        rounded(sh, pre, 3, fill)
        margins(sh, pre, 2, 2, 2, 2, "inset")
    write(sh, root, "widgets/scrollbar.svg")


def circle(d, fill, border=None, inset=0):
    r = d / 2 - inset
    b = f'<circle cx="{d / 2}" cy="{d / 2}" r="{r - .5}" {stroke(border)}/>' if border else ""
    return f'<circle cx="{d / 2}" cy="{d / 2}" r="{r}" {paint(fill)}/>{b}'


def slider(root):
    sh = Sheet()
    sh.el("hint-tile-center", 2, 2)
    sh.el("hint-handle-size", 18, 18)
    for o in ("horizontal", "vertical"):
        for st, fill in (("handle", (FOCUS, 1)), ("hover", (FOCUS, 1)), ("focus", (FOCUS, 1))):
            halo = f'<circle cx="9" cy="9" r="9" {paint((FOCUS, .22))}/>' if st != "handle" else ""
            sh.el(f"{o}-slider-{st}", 18, 18, halo + f'<circle cx="9" cy="9" r="6" {paint(fill)}/>')
        sh.el(f"{o}-slider-shadow", 18, 18)
    for pre, fill in (("groove-", (TEXT, .16)), ("groove-highlight-", (FOCUS, 1))):
        rounded(sh, pre, 2, fill)
    write(sh, root, "widgets/slider.svg")


def switch(root):
    """M3 switch: pill track, filled when on, outlined when off; handle grows when on."""
    sh = Sheet()
    sh.el("hint-stretch-borders", 4, 4)
    sh.el("hint-bar-size", 40, 22)
    for st, fill, bd in (("active", (FOCUS, 1), None), ("inactive", (TEXT, .10), (TEXT, .45))):
        sh.el(f"{st}-center", 8, 22, f'<rect width="8" height="22" {paint(fill)}/>'
              + (f'<rect width="8" height="1" {paint(bd)}/><rect y="21" width="8" height="1" {paint(bd)}/>' if bd else ""))
        half = f'<path d="M11,0 A11,11 0 0 0 11,22 Z" {paint(fill)}/>' + (f'<path d="M11,0 A11,11 0 0 0 11,22 V21 A10,10 0 0 1 11,1 Z" {paint(bd)}/>' if bd else "")
        sh.el(f"{st}-left", 11, 22, half)
        sh.el(f"{st}-right", 11, 22, f'<g transform="translate(11,0) scale(-1,1)">{half}</g>')
    for st, fill, inset in (("handle", (BTN, 1), 3), ("handle-hover", (BTN, 1), 2),
                            ("handle-focus", (BTN, 1), 2), ("handle-pressed", (HL, 1), 1)):
        sh.el(st, 22, 22, circle(22, fill, inset=inset))
    write(sh, root, "widgets/switch.svg")


def checks(root):
    sh = Sheet()
    tick = f'<path d="M4,8.5 L7,11.5 L12.5,5" fill="none" class="{HL_TEXT}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    sh.el("checkbox", 16, 16, f'<rect width="16" height="16" rx="4" {paint((FOCUS, 1))}/>'.replace(HL_TEXT, HL_TEXT) + tick.replace(HL_TEXT, "ColorScheme-ViewBackground"))
    sh.el("radiobutton", 16, 16, f'<circle cx="8" cy="8" r="5" {paint((FOCUS, 1))}/>')
    write(sh, root, "widgets/checkmarks.svg")
    sh = Sheet()
    sh.el("hint-size", 18, 18)
    for st, bd in (("normal", (TEXT, .55)), ("hover", (TEXT, .8)), ("focus", (FOCUS, 1))):
        sh.el(st, 18, 18, f'<circle cx="9" cy="9" r="8" {stroke(bd, 2)}/>')
    sh.el("checked", 18, 18, f'<circle cx="9" cy="9" r="8" {stroke((FOCUS, 1), 2)}/><circle cx="9" cy="9" r="4.5" {paint((FOCUS, 1))}/>')
    write(sh, root, "widgets/radiobutton.svg")


def items(root):
    sh = Sheet()
    rounded(sh, "normal-", 8, None, None, 5)
    rounded(sh, "hover-", 8, (TEXT, .08), None, 5)
    rounded(sh, "pressed-", 8, (HL, 1), None, 5)
    write(sh, root, "widgets/menubaritem.svg")

    sh = Sheet()
    sh.el("hint-tile-center", 8, 8)
    rounded(sh, "normal-", 10, None)
    rounded(sh, "hover-", 10, (TEXT, .08))
    rounded(sh, "selected-", 10, (HL, 1))
    rounded(sh, "selected+hover-", 10, (HL, 1), (FOCUS, .5))
    write(sh, root, "widgets/viewitem.svg")

    sh = Sheet()
    sh.el("hint-tile-center", 8, 8)
    sh.el("separator", 8, 1, f'<rect width="8" height="1" {paint((TEXT, .12))}/>')
    rounded(sh, "normal-", 10, None, None, 6)
    rounded(sh, "hover-", 10, (TEXT, .08))
    rounded(sh, "pressed-", 10, (HL, 1), None, 6)
    rounded(sh, "section-", 10, None, None, 6)
    write(sh, root, "widgets/listitem.svg")


def bars(root):
    sh = Sheet()
    sh.el("hint-tile-center", 2, 2)
    rounded(sh, "", 2, None, None, 4)
    write(sh, root, "widgets/toolbar.svg")

    sh = Sheet()
    sh.el("hint-stretch-borders", 4, 4)
    rounded(sh, "header-", 2, None)
    rounded(sh, "footer-", 2, None)
    margins(sh, "", 6, 6, 8, 8)
    write(sh, root, "widgets/plasmoidheading.svg")


def tasks(root):
    """Task buttons: soft rounded wash; the active one gets a small accent pill on the screen-facing edge."""
    sh = Sheet()
    for orient in ("", "north-", "west-", "east-"):
        for st, fill in (("normal", None), ("hover", (TEXT, .08)), ("minimized", None),
                         ("focus", (HL, 1)), ("attention", (NEU, .25)), ("progress", (FOCUS, .30))):
            rounded(sh, f"{orient}{st}-", 8, fill, None, 4 if st == "normal" else None)
    write(sh, root, "widgets/tasks.svg")


def actionbutton(root):
    sh = Sheet()
    for size in ("", "16-16-", "22-22-", "24-24-"):
        n = int(size.split("-")[0]) if size else 22
        for st, fill in (("normal", (BTN, .7)), ("hover", (BTN, 1)), ("focus", (HL, 1)), ("pressed", (HL, 1))):
            sh.el(f"{size}{st}", n, n, circle(n, fill))
    write(sh, root, "widgets/actionbutton.svg")


def plasmarc(root):
    g = P.GLASS
    (pathlib.Path(root) / "plasmarc").write_text(
        "[AdaptiveTransparency]\nenabled=true\n\n"
        "[BlurBehindEffect]\nenabled=true\n\n"
        f"[ContrastEffect]\nenabled=true\ncontrast=0.9\nintensity=1.1\nsaturation=1.6\n")


def metadata(root):
    meta = {"KPackageStructure": "Plasma/Theme",
            "KPlugin": {"Authors": [{"Name": "MatOS"}], "Category": "",
                        "Description": "Rounded glass Plasma style in Material colours. Follows the system accent.",
                        "Id": "MatOS", "License": "MIT", "Name": "MatOS", "Version": "0.1"}}
    (pathlib.Path(root) / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")


def build(root):
    root = pathlib.Path(root)
    root.mkdir(parents=True, exist_ok=True)
    a = P.GLASS
    frames(root, "", a["menu_alpha"])
    frames(root, "translucent", a["panel_alpha"])
    frames(root, "solid", 1)
    frames(root, "opaque", 1)
    for fn in (button, lineedit, frame, tabbar, scrollbar, slider, switch, checks, items, bars, tasks, actionbutton):
        fn(root)
    plasmarc(root)
    metadata(root)


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/desktoptheme/MatOS")
    build(out)
    print(f"wrote {sum(1 for _ in out.rglob('*.svg'))} svg files to {out}")
