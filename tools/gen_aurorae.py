#!/usr/bin/env python3
"""Generate the MatOS Aurorae window decoration (title bar + Material circle buttons).

Borderless: the Rounded Corners KWin effect (kwin-effect-rounded-corners) rounds the window,
draws the outline and the shadow (settings in tools/gen_kwin.py). The title bar uses the
Window colour so it melts into the app's toolbar, macOS style. Colours are baked in
(Aurorae SVG can't read the palette); the accent watcher regenerates on accent change.
Usage: gen_aurorae.py <dark|light|both> [outdir] [--seed HEX]
"""
import argparse, json, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P

TITLE_H = 38
BTN = 28        # button box; the circle inside is CIRCLE wide
CIRCLE = 22
SPACING = 6
WINDOW_RADIUS = 18  # keep equal to gen_kwin.RADIUS (the Rounded Corners effect)
SHADOW_PAD = 28  # transparent margin the Rounded Corners effect paints its shadow into


def rgbcsv(h, alpha=None):
    r, g, b = (round(c * 255) for c in P.hex_rgb(h))
    return f"{r},{g},{b}" + (f",{alpha}" if alpha is not None else "")


class Sheet:
    def __init__(self, width=400):
        self.out, self.x, self.y, self.row_h, self.width = [], 0, 0, 0, width

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
                + "\n".join(self.out) + "\n</svg>\n")


def glyph(kind, col, op=1):
    """Rounded-stroke glyphs (Material Symbols Rounded feel), centred in the BTN box."""
    c = BTN / 2
    st = f'fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    d = {
        "close": f"M{c - 3.5},{c - 3.5} L{c + 3.5},{c + 3.5} M{c + 3.5},{c - 3.5} L{c - 3.5},{c + 3.5}",
        "minimize": f"M{c - 4},{c} H{c + 4}",
        "keepabove": f"M{c - 4},{c + 2} L{c},{c - 2} L{c + 4},{c + 2}",
        "keepbelow": f"M{c - 4},{c - 2} L{c},{c + 2} L{c + 4},{c - 2}",
        "shade": f"M{c - 4},{c - 2} H{c + 4} M{c - 4},{c + 1} H{c + 4}",
    }
    if kind == "maximize":
        return f'<rect x="{c - 4}" y="{c - 4}" width="8" height="8" rx="2.2" {st}/>'
    if kind == "restore":
        return (f'<rect x="{c - 4.5}" y="{c - 2}" width="6.5" height="6.5" rx="1.8" {st}/>'
                f'<path d="M{c - 2},{c - 4.5} H{c + 2.7} Q{c + 4.5},{c - 4.5} {c + 4.5},{c - 2.7} V{c + 2}" {st}/>')
    if kind == "alldesktops":
        return f'<circle cx="{c}" cy="{c}" r="2.6" fill="{col}" fill-opacity="{op}"/>'
    return f'<path d="{d[kind]}" {st}/>'


def button_svg(kind, s):
    circle = lambda col, op=1: f'<circle cx="{BTN / 2}" cy="{BTN / 2}" r="{CIRCLE / 2}" fill="{col}" fill-opacity="{op}"/>'
    ink, ink2 = s["on_surface"], s["on_surface_variant"]
    rest = s["surface_container_highest"]
    if kind == "close":
        hov, hov_ink, prs = s["error"], s["on_error"], s["error_container"]
        prs_ink = s["on_error_container"]
    else:
        hov, hov_ink, prs = s["primary_container"], s["on_primary_container"], s["primary"]
        prs_ink = s["on_primary"]
    states = {
        "active": circle(rest) + glyph(kind, ink2),
        "hover": circle(hov) + glyph(kind, hov_ink),
        "pressed": circle(prs) + glyph(kind, prs_ink),
        "inactive": circle(rest, .6) + glyph(kind, ink2, .45),
        "deactivated": circle(rest, .5) + glyph(kind, ink2, .3),
    }
    sh = Sheet(width=BTN * 5 + 40)
    for st, body in states.items():
        sh.el(f"{st}-center", BTN, BTN, body)
    return sh.svg()


def decoration_svg(s):
    """Borderless title bar inside a SHADOW_PAD margin. KWin builds the window shadow from what the border
    pieces paint in that margin, so the shadow is drawn here: peak at the window edge, fading to nothing
    at the margin's outer edge; inactive windows get a lighter one.

    Corner pieces are P = pad + R square (R = the window's corner radius), i.e. they reach R px into the
    window. That lets the shadow follow the window's real rounded corner: strength depends on the distance
    from the arc of radius R centred (pad+R, pad+R), so it meets the straight edges exactly at the
    piece boundary and never peaks at the square corner the rounded window has curved away from.
    Inside the window the pieces paint the bar colour / nothing (the client covers it)."""
    bar = s["surface_container"]
    pad, th, R = SHADOW_PAD, TITLE_H, WINDOW_RADIUS
    P = pad + R
    k = R / P
    sh = Sheet(width=700)
    for tag, peak in (("", .45), ("inactive-", .24)):
        p = lambda n: f"decoration-{tag}{n}"
        fade = lambda a, b: "".join(f'<stop offset="{o}" stop-color="#000" stop-opacity="{v:.3f}"/>' for o, v in (
            (a, peak), (a + (b - a) * .45, peak * .22), (b, 0)))
        defs = (f'<defs>'
                f'<radialGradient id="r{tag}" gradientUnits="userSpaceOnUse" cx="{P}" cy="{P}" r="{P}">'
                f'<stop offset="0" stop-color="#000" stop-opacity="{peak}"/>{fade(k, 1)}</radialGradient>'
                f'<linearGradient id="h{tag}" x1="0" x2="1" y1="0" y2="0">'
                f'<stop offset="0" stop-color="#000" stop-opacity="0"/>'
                f'<stop offset=".55" stop-color="#000" stop-opacity="{peak * .22:.3f}"/>'
                f'<stop offset="1" stop-color="#000" stop-opacity="{peak}"/></linearGradient>'
                f'<linearGradient id="v{tag}" x1="0" x2="0" y1="0" y2="1">'
                f'<stop offset="0" stop-color="#000" stop-opacity="0"/>'
                f'<stop offset=".55" stop-color="#000" stop-opacity="{peak * .22:.3f}"/>'
                f'<stop offset="1" stop-color="#000" stop-opacity="{peak}"/></linearGradient>'
                f'</defs>')
        flipx, flipy = f"translate({P},0) scale(-1,1)", f"translate(0,{P}) scale(1,-1)"
        both = f"translate({P},{P}) scale(-1,-1)"
        # shadow of a corner pad x pad outside + the arc zone; flat bar colour over the window's own part
        corner = lambda t: f'<g transform="{t}"><rect width="{P}" height="{P}" fill="url(#r{tag})"/></g>'
        sh.el(p("top"), 8, pad + th, defs + f'<rect width="8" height="{pad}" fill="url(#v{tag})"/>'
                                           f'<rect y="{pad}" width="8" height="{th}" fill="{bar}"/>')
        for name, t in (("topleft", ""), ("topright", flipx)):
            body = (corner(t)
                    + f'<g transform="{t}"><rect x="{pad}" y="{pad}" width="{R}" height="{th}" fill="{bar}"/>'
                      f'<rect y="{P}" width="{pad}" height="{pad + th - P}" fill="url(#h{tag})"/></g>')
            sh.el(p(name), P, pad + th, defs + body)
        sh.el(p("left"), P, 8, defs + f'<rect width="{pad}" height="8" fill="url(#h{tag})"/>')
        sh.el(p("right"), P, 8, defs + f'<g transform="{flipx}"><rect width="{pad}" height="8" fill="url(#h{tag})"/></g>')
        sh.el(p("bottom"), 8, P, defs + f'<g transform="translate(0,{P}) scale(1,-1)"><rect width="8" height="{pad}" fill="url(#v{tag})"/></g>')
        sh.el(p("bottomleft"), P, P, defs + corner(flipy))
        sh.el(p("bottomright"), P, P, defs + corner(both))
        sh.el(p("center"), 8, 8, f'<rect width="8" height="8" fill="{bar}"/>')
    for side, (w, h) in {"top": (4, pad + th), "bottom": (4, pad), "left": (pad, 4), "right": (pad, 4)}.items():
        sh.el(f"hint-{side}-margin", w, h)
    return sh.svg()


RC = """[General]
ActiveTextColor={act}
InactiveTextColor={inact}
TitleAlignment=Center
TitleVerticalAlignment=Center
UseTextShadow=false
LeftButtons=M
RightButtons=IAX
Shadow=true
Animation=150

[Layout]
BorderLeft=0
BorderRight=0
BorderBottom=0
TitleEdgeTop=0
TitleEdgeBottom=0
TitleEdgeLeft=10
TitleEdgeRight=10
TitleBorderLeft=12
TitleBorderRight=12
TitleHeight={th}
ButtonWidth={bw}
ButtonHeight={bw}
ButtonSpacing={sp}
ButtonMarginTop={mt}
ExplicitButtonSpacer=8
PaddingTop={pad}
PaddingBottom={pad}
PaddingRight={pad}
PaddingLeft={pad}
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=10
TitleEdgeRightMaximized=10
"""


def write(variant, outdir, seed):
    dark = variant == "dark"
    name = "MatOSDark" if dark else "MatOSLight"
    s = P.scheme(seed, dark)
    d = pathlib.Path(outdir) / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "decoration.svg").write_text(decoration_svg(s))
    for kind in ("close", "maximize", "restore", "minimize", "alldesktops", "keepabove", "keepbelow", "shade"):
        (d / f"{kind}.svg").write_text(button_svg(kind, s))
    (d / f"{name}rc").write_text(RC.format(act=rgbcsv(s["on_surface"]), inact=rgbcsv(s["on_surface"], 120),
                                          th=TITLE_H, bw=BTN, sp=SPACING, mt=(TITLE_H - BTN) // 2, pad=SHADOW_PAD))
    label = f"MatOS {'Dark' if dark else 'Light'}"
    meta = {"KPackageStructure": "KWin/Aurorae",
            "KPlugin": {"Authors": [{"Name": "MatOS"}], "Category": "Plasma 6 Window Decorations",
                        "ServiceTypes": ["KWin/Aurorae"], "EnabledByDefault": True, "Name": label,
                        "Description": "Borderless title bar with Material circle buttons", "Id": name,
                        "Version": "0.1", "License": "MIT"}}
    (d / "metadata.json").write_text(json.dumps(meta, indent=4) + "\n")
    (d / "metadata.desktop").write_text(f"[Desktop Entry]\nName={label}\nComment=Borderless title bar with Material circle buttons\n"
                                        f"X-KDE-PluginInfo-Name={name}\nX-KDE-PluginInfo-Version=0.1\n"
                                        f"X-KDE-PluginInfo-License=MIT\nX-KDE-ServiceTypes=KWin/Decoration\n")
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=["dark", "light", "both"])
    ap.add_argument("outdir", nargs="?", default="build/aurorae")
    ap.add_argument("--seed")
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    for v in (["dark", "light"] if a.variant == "both" else [a.variant]):
        print("wrote", write(v, a.outdir, seed))
