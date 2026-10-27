"""Render a mock MatOS desktop (top bar + window + common widgets) from tools/palette.py.

Usage: python3 tools/preview_ui.py OUT.svg [--seed HEX]
Dark and light side by side, plus a strip of the colour roles. Glass is faked with alpha
(SVG has no backdrop blur), so the real Plasma result will look softer.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P

F = "font-family=\"Roboto Flex\""

def text(x, y, s, fill, size=13, weight=400, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" {F} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'

def logo(x, y, s, c):
    bars = [(22, 15, 47, c["on_surface"]), (42.5, 15, 29, c["accent"]), (63, 15, 47, c["on_surface"])]
    return f'<g transform="translate({x},{y}) scale({s}) translate(-22,-27)">' + "".join(
        f'<rect x="{bx}" y="27" width="{w}" height="{h}" rx="{w / 2}" fill="{f}"/>' for bx, w, h, f in bars) + "</g>"

def desktop(ox, c, sh, uid, dark):
    W, H = 900, 640
    o = [f'<clipPath id="dk{uid}"><rect width="{W}" height="{H}"/></clipPath>',
         f'<g transform="translate({ox},0)" clip-path="url(#dk{uid})">',
         f'<defs><linearGradient id="wp{uid}" x1="0" y1="0" x2="1" y2="1">'
         f'<stop stop-color="{c["primary_container"]}"/><stop offset=".55" stop-color="{c["surface_dim"]}"/>'
         f'<stop offset="1" stop-color="{c["tertiary_container"]}"/></linearGradient>'
         f'<linearGradient id="gr{uid}" x1="0" x2="1"><stop stop-color="{c["gradient_start"]}"/><stop offset="1" stop-color="{c["gradient_end"]}"/></linearGradient>'
         f'<filter id="sd{uid}" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dy="10" stdDeviation="16" flood-opacity="{.5 if dark else .18}"/></filter></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#wp{uid})"/>',
         # soft blobs on the wallpaper
         f'<circle cx="760" cy="520" r="170" fill="{c["gradient_end"]}" opacity=".35"/>',
         f'<circle cx="120" cy="140" r="120" fill="{c["accent"]}" opacity=".3"/>']
    # thin top bar (glass)
    o += [f'<rect width="{W}" height="28" fill="{c["surface_container"]}" opacity="{P.GLASS["panel_alpha"]}"/>',
          logo(14, 7, 0.3, c),
          text(46, 19, "Files", c["on_surface"], 13, 650)]
    o += [text(96 + i * 52, 19, m, c["on_surface"], 13) for i, m in enumerate(["Edit", "View", "Go", "Window"])]
    o += [f'<rect x="{W - 228}" y="5" width="56" height="18" rx="9" fill="{c["secondary_container"]}"/>',
          text(W - 200, 18, "EN", c["on_secondary_container"], 11, 600, "middle"),
          text(W - 14, 19, "Tue 27 Oct  14:32", c["on_surface"], 13, 500, "end")]
    # window
    wx, wy, ww, wh, r = 70, 64, 760, 520, sh["xl"]
    o += [f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="{r}" fill="{c["surface"]}" filter="url(#sd{uid})"/>',
          f'<clipPath id="cl{uid}"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="{r}"/></clipPath>',
          f'<g clip-path="url(#cl{uid})">',
          f'<rect x="{wx}" y="{wy}" width="210" height="{wh}" fill="{c["surface_container_low"]}"/>',
          "</g>",
          f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="{r}" fill="none" stroke="{c["outline_variant"]}" stroke-opacity=".6"/>']
    # window buttons (left, macOS placement, Material tones)
    for i, k in enumerate(["error", "tertiary", "primary"]):
        o.append(f'<circle cx="{wx + 26 + i * 22}" cy="{wy + 26}" r="7" fill="{c[k]}"/>')
    # sidebar nav (M3 drawer: selected = secondary container pill)
    items = ["Home", "Recent", "Documents", "Downloads", "Pictures", "Music", "Trash"]
    for i, name in enumerate(items):
        y = wy + 64 + i * 40
        if i == 2:
            o.append(f'<rect x="{wx + 12}" y="{y - 20}" width="186" height="34" rx="17" fill="{c["secondary_container"]}"/>')
        fg = c["on_secondary_container"] if i == 2 else c["on_surface_variant"]
        o.append(f'<rect x="{wx + 28}" y="{y - 10}" width="14" height="14" rx="4" fill="{c["accent"] if i == 2 else fg}" opacity="{1 if i == 2 else .7}"/>')
        o.append(text(wx + 54, y + 2, name, fg, 13, 600 if i == 2 else 450))
    # content
    cx = wx + 240
    o += [text(cx, wy + 50, "Documents", c["on_surface"], 26, 650),
          text(cx, wy + 74, "12 items · 3.4 GB free", c["on_surface_variant"], 13),
          # search field
          f'<rect x="{wx + ww - 230}" y="{wy + 30}" width="200" height="36" rx="18" fill="{c["surface_container_highest"]}"/>',
          text(wx + ww - 208, wy + 53, "Search", c["on_surface_variant"], 13)]
    # card
    ky = wy + 100
    o += [f'<rect x="{cx}" y="{ky}" width="490" height="172" rx="{sh["lg"]}" fill="{c["surface_container_high"]}"/>',
          text(cx + 20, ky + 32, "Sync to Programs drive", c["on_surface"], 16, 600),
          text(cx + 20, ky + 54, "Copies new files every hour over the 10 Gbps link.", c["on_surface_variant"], 13)]
    # switch (on)
    o += [f'<rect x="{cx + 418}" y="{ky + 18}" width="52" height="32" rx="16" fill="{c["primary"]}"/>',
          f'<circle cx="{cx + 454}" cy="{ky + 34}" r="12" fill="{c["on_primary"]}"/>']
    # gradient progress
    o += [f'<rect x="{cx + 20}" y="{ky + 76}" width="450" height="8" rx="4" fill="{c["surface_container_highest"]}"/>',
          f'<rect x="{cx + 20}" y="{ky + 76}" width="300" height="8" rx="4" fill="url(#gr{uid})"/>',
          text(cx + 20, ky + 108, "67%  ·  2 min left", c["on_surface_variant"], 12)]
    # buttons
    by = ky + 116
    o += [f'<rect x="{cx + 230}" y="{by}" width="110" height="36" rx="18" fill="none" stroke="{c["outline"]}"/>',
          text(cx + 285, by + 23, "Cancel", c["primary"], 14, 600, "middle"),
          f'<rect x="{cx + 350}" y="{by}" width="120" height="36" rx="18" fill="{c["primary"]}"/>',
          text(cx + 410, by + 23, "Sync now", c["on_primary"], 14, 600, "middle")]
    # chips
    cy = wy + 290
    for i, (name, sel) in enumerate([("All", True), ("Images", False), ("PDF", False), ("Code", False)]):
        x = cx + i * 92
        o.append(f'<rect x="{x}" y="{cy}" width="84" height="32" rx="{sh["sm"]}" fill="{c["secondary_container"] if sel else "none"}" stroke="{c["outline_variant"] if not sel else "none"}"/>')
        o.append(text(x + 42, cy + 21, ("✓ " if sel else "") + name, c["on_secondary_container"] if sel else c["on_surface_variant"], 13, 550, "middle"))
    # file tiles
    for i in range(4):
        x, y = cx + i * 124, wy + 338
        o += [f'<rect x="{x}" y="{y}" width="112" height="112" rx="{sh["lg"]}" fill="{c["surface_container"]}"/>',
              f'<rect x="{x + 34}" y="{y + 22}" width="44" height="52" rx="10" fill="{[c["primary_container"], c["tertiary_container"], c["secondary_container"], c["error_container"]][i]}"/>',
              text(x + 56, y + 96, ["report.pdf", "cover.png", "notes.md", "old.zip"][i], c["on_surface"], 12, 500, "middle")]
    # tonal button + FAB
    o += [f'<rect x="{cx}" y="{wy + 466}" width="140" height="36" rx="18" fill="{c["secondary_container"]}"/>',
          text(cx + 70, wy + 489, "New folder", c["on_secondary_container"], 14, 600, "middle"),
          f'<rect x="{wx + ww - 80}" y="{wy + wh - 80}" width="56" height="56" rx="{sh["lg"]}" fill="{c["primary_container"]}"/>',
          text(wx + ww - 52, wy + wh - 42, "+", c["on_primary_container"], 30, 400, "middle")]
    o.append("</g>")
    return "".join(o)

def swatches(y, tok):
    keys = ["primary", "primary_container", "secondary_container", "tertiary", "tertiary_container",
            "error", "surface", "surface_container", "surface_container_highest", "on_surface",
            "outline", "accent", "gradient_end"]
    o = []
    for row, mode in enumerate(("light", "dark")):
        for i, k in enumerate(keys):
            x, yy = 20 + i * 136, y + row * 70
            o.append(f'<rect x="{x}" y="{yy}" width="128" height="36" rx="10" fill="{tok[mode][k]}" stroke="#8884" />')
            o.append(text(x + 2, yy + 52, f"{k.replace('_container', ' ctr').replace('surface', 'surf')} {tok[mode][k]}", "#bbb", 10))
    return "".join(o)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed")
    a = ap.parse_args()
    tok = P.tokens(a.seed)
    body = (desktop(0, tok["dark"], tok["shape"], "d", True) + desktop(920, tok["light"], tok["shape"], "l", False)
            + swatches(670, tok) + text(20, 834, f"seed {tok['seed']}", "#888", 12))
    with open(a.out, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="1820" height="850"><rect width="100%" height="100%" fill="#1b1b1f"/>{body}</svg>')

if __name__ == "__main__":
    main()
