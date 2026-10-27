"""MatOS final logo set (C2: glass squircle, neutral pills, accent centre pill).

Usage: python3 build_logo.py OUT_DIR [ACCENT_HEX]
Writes master SVGs (text converted to paths, no font needed) and preview-sheet.svg.
Default accent is Lavender #b69cff; gradients run accent -> accent hue +16 deg (Lavender -> Orchid).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_concepts import tone, squircle
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

DEFAULT_ACCENT = "#b69cff"
GRADIENT_SHIFT = 16  # Lavender #b69cff -> Orchid #c792ea
FONT = os.path.expanduser("~/.local/share/fonts/matos/RobotoFlex.ttf")

M_BARS = [(22, 15, 47), (42.5, 15, 29), (63, 15, 47)]
V_BARS = [(17, 10.5, 20), (31, 10.5, 33), (45, 10.5, 47), (59, 10.5, 33), (72.5, 10.5, 20)]

def bars3(a, b, c):
    """Three pills at the M's positions with the given heights; the middle one takes the accent."""
    return [(22, 15, a), (42.5, 15, b), (63, 15, c)]

# One mark per MatOS app: pills on the glass tile spelling its letter, accent in the middle.
# NEW APP -> add a line here, run this script, install the SVG (see APP_ICON_TARGETS in the memory note).
APP_BARS = {
    "ordo":    bars3(34, 47, 34),   # O: a dome
    "portae":  bars3(47, 38, 38),   # P: stem + bowl
    "firefox": bars3(47, 26, 14),   # F: stem + two arms
    "animus":  bars3(20, 47, 20),   # A: an apex
    "ghostty": bars3(47, 20, 34),   # G: top arc, notch, hooked base
}

def colours(seed, dark):
    n = lambda t: tone(seed, t, chroma=0.014)
    if dark:
        return dict(bg=n(10), ink=n(92), sub=n(70), bar=n(94), hi=n(34), lo=n(16),
                    accent=tone(seed, 72), accent2=tone(seed, 72, hue_shift=GRADIENT_SHIFT))
    return dict(bg=n(97), ink=n(12), sub=n(40), bar=n(22), hi=n(99), lo=n(86),
                accent=tone(seed, 55), accent2=tone(seed, 55, hue_shift=GRADIENT_SHIFT))

def mark(c, bars, uid, gradient):
    fill = f"url(#a{uid})" if gradient else c["accent"]
    mid = len(bars) // 2
    pills = "".join(f'<rect x="{x}" y="27" width="{w}" height="{h}" rx="{w / 2}" fill="{fill if i == mid else c["bar"]}"/>'
                    for i, (x, w, h) in enumerate(bars))
    return f"""<defs>
  <linearGradient id="g{uid}" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="{c['hi']}"/><stop offset="1" stop-color="{c['lo']}"/></linearGradient>
  <linearGradient id="h{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="a{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/></linearGradient>
  <filter id="s{uid}" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity=".28"/></filter>
</defs>
<path d="{squircle(50, 50, 46)}" fill="url(#g{uid})" filter="url(#s{uid})"/>
<path d="{squircle(50, 50, 45.2)}" fill="none" stroke="url(#h{uid})" stroke-width="1.6"/>
{pills}"""

def glyph(bars):
    """Flat, tile-less mark for panels: KDE recolours ColorScheme-Text / ColorScheme-Highlight."""
    mid = len(bars) // 2
    rects = "".join(f'<rect x="{x}" y="27" width="{w}" height="{h}" rx="{w / 2}" class="{"ColorScheme-Highlight" if i == mid else "ColorScheme-Text"}" fill="currentColor"/>'
                    for i, (x, w, h) in enumerate(bars))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="18 23 64 54" width="64" height="54">'
            '<style id="current-color-scheme">.ColorScheme-Text{color:#2a2a30}.ColorScheme-Highlight{color:#b69cff}</style>'
            f'{rects}</svg>')

# ---- wordmark as outlines ----

_fonts = {}
def _font(wght):
    if wght not in _fonts:
        _fonts[wght] = instantiateVariableFont(TTFont(FONT), {"wght": wght}, inplace=False)
    return _fonts[wght]

def text_path(runs, size, x0=0, y0=0):
    """runs: [(text, wght, fill)] -> (svg <path>s, width) with baseline at y0."""
    out, x = [], x0
    for text, wght, fill in runs:
        f = _font(wght); gs = f.getGlyphSet(); cmap = f.getBestCmap()
        scale = size / f["head"].unitsPerEm
        d = []
        for ch in text:
            name = cmap[ord(ch)]
            pen = SVGPathPen(gs)
            gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y0)))
            d.append(pen.getCommands())
            x += f["hmtx"][name][0] * scale
        out.append(f'<path fill="{fill}" d="{" ".join(d)}"/>')
    return "".join(out), x - x0

def wordmark(c, size, x=0, y=0):
    return text_path([("Mat", 700, c["ink"]), ("OS", 300, c["sub"])], size, x, y)

def svg(w, h, body, vb=None):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb or f"0 0 {w} {h}"}" width="{w}" height="{h}">{body}</svg>'

def main(out, seed=DEFAULT_ACCENT):
    os.makedirs(out, exist_ok=True)
    w = lambda name, s: open(os.path.join(out, name), "w").write(s)
    for dark in (False, True):
        c, mode = colours(seed, dark), ("dark" if dark else "light")
        # logo pill is always solid accent; the gradient is reserved for UI surfaces
        w(f"matos-mark-{mode}.svg", svg(512, 512, mark(c, M_BARS, "m", False), "0 0 100 100"))
        w(f"vox-mark-{mode}.svg", svg(512, 512, mark(c, V_BARS, "v", False), "0 0 100 100"))
        for app, bars in APP_BARS.items():
            w(f"{app}-mark-{mode}.svg", svg(512, 512, mark(c, bars, app[:2], False), "0 0 100 100"))
        paths, tw = wordmark(c, 100, 0, 76)
        w(f"matos-wordmark-{mode}.svg", svg(round(tw), 100, paths))
        paths, tw = wordmark(c, 64, 112, 72)
        lw = round(112 + tw + 20)  # 6-unit margin all round so the tile's shadow isn't clipped
        w(f"matos-lockup-{mode}.svg", svg(lw, 112, mark(c, M_BARS, "l", False) + paths, f"-6 -6 {lw} 112"))
    w("matos-glyph.svg", glyph(M_BARS))
    w("vox-glyph.svg", glyph(V_BARS))
    preview(out, seed)

def preview(out, seed):
    parts, W = [], 1500
    for row, dark in enumerate((True, False)):
        c, y = colours(seed, dark), row * 330
        g = lambda bars, grad, s, x, yy, k: f'<g transform="translate({x},{yy}) scale({s})">{mark(c, bars, f"p{row}{k}", grad)}</g>'
        parts.append(f'<rect y="{y}" width="{W}" height="330" fill="{c["bg"]}"/>')
        for i, (bars, grad, k) in enumerate([(M_BARS, False, "a"), (M_BARS, True, "b"), (V_BARS, False, "c"), (V_BARS, True, "d")]):
            parts.append(g(bars, grad, 1.6, 30 + i * 175, y + 24, k))
            label = ("solid" if not grad else "gradient")
            parts.append(f'<text x="{110 + i * 175}" y="{y + 200}" text-anchor="middle" font-family="Roboto Flex" font-size="14" fill="{c["sub"]}">{label}</text>')
        for j, s in enumerate((0.48, 0.32, 0.16)):
            parts.append(g(M_BARS, False, s, 740 + j * 60, y + 40, f"s{j}"))
        wm, _ = wordmark(c, 80, 740, y + 175)
        parts.append(wm)
        # fake thin top bar with the flat glyph
        bar_y = y + 240
        parts.append(f'<rect x="30" y="{bar_y}" width="{W - 60}" height="30" rx="15" fill="{c["hi"]}" opacity=".85"/>')
        glyph_g = "".join(f'<rect x="{x}" y="27" width="{wd}" height="{h}" rx="{wd / 2}" fill="{c["accent"] if i == 1 else c["ink"]}"/>'
                          for i, (x, wd, h) in enumerate(M_BARS))
        parts.append(f'<g transform="translate({44 - 22 * 0.33},{bar_y + 6 - 27 * 0.33}) scale(0.33)">{glyph_g}</g>')
        for k, item in enumerate(["Files", "Edit", "View", "Window"]):
            parts.append(f'<text x="{90 + k * 70}" y="{bar_y + 20}" font-family="Roboto Flex" font-weight="{600 if k == 0 else 400}" font-size="14" fill="{c["ink"]}">{item}</text>')
        parts.append(f'<text x="{W - 50}" y="{bar_y + 20}" text-anchor="end" font-family="Roboto Flex" font-size="14" fill="{c["ink"]}">Tue 27 Oct  14:32</text>')
        parts.append(f'<rect x="{1200}" y="{y + 60}" width="230" height="56" rx="28" fill="url(#bt{row})"/>'
                     f'<defs><linearGradient id="bt{row}" x1="0" x2="1"><stop stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent2"]}"/></linearGradient></defs>'
                     f'<text x="1315" y="{y + 95}" text-anchor="middle" font-family="Roboto Flex" font-weight="600" font-size="18" fill="{c["bg"]}">Gradient button</text>')
    open(os.path.join(out, "preview-sheet.svg"), "w").write(svg(W, 660, "".join(parts)))

if __name__ == "__main__":
    main(sys.argv[1], *(sys.argv[2:3]))
