#!/usr/bin/env python3
"""Ghostty theme files (MatOS Dark / MatOS Light) and the matching config, from the MatOS palette.
Usage: gen_ghostty.py OUTDIR [--seed HEX]"""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P

# OKLCH hues for the ANSI colours; tone/chroma keep them soft but readable on the surface
HUES = {"red": 25, "green": 148, "yellow": 95, "blue": 255, "magenta": 330, "cyan": 205}
ORDER = ["red", "green", "yellow", "blue", "magenta", "cyan"]


def theme(seed, dark):
    s = P.scheme(seed, dark)
    n, b = (72, 84) if dark else (42, 32)
    ch = 0.13 if dark else 0.15
    n_c = {k: P.solve(n, ch, h) for k, h in HUES.items()}
    b_c = {k: P.solve(b, ch, h) for k, h in HUES.items()}
    pal = [s["surface_container_highest"]] + [n_c[k] for k in ORDER] + [s["on_surface_variant"]]
    pal += [s["outline"]] + [b_c[k] for k in ORDER] + [s["on_surface"]]
    lines = [f"palette = {i}={c}" for i, c in enumerate(pal)]
    lines += [
        f"background = {s['surface']}",
        f"foreground = {s['on_surface']}",
        f"cursor-color = {s['accent']}",
        f"cursor-text = {s['surface']}",
        f"selection-background = {s['primary_container']}",
        f"selection-foreground = {s['on_primary_container']}",
    ]
    return "\n".join(lines) + "\n"


CONFIG = """# MatOS look: soft, rounded, Material You. Colours come from the MatOS palette (see the theme files).
# Regenerate with ~/Projects/matos/ghostty/install.sh

theme = dark:MatOS Dark,light:MatOS Light

font-family = Geist Mono
font-size = 12
font-thicken = true

# Cursor: soft bar that blinks, with a trail when it jumps
cursor-style = bar
cursor-style-blink = true
custom-shader = ~/.config/ghostty/shaders/cursor-trail.glsl
custom-shader-animation = true

# Window: generous padding, slight see-through glass
window-padding-x = 18
window-padding-y = 14
window-padding-balance = true
window-padding-color = background
background-opacity = 0.9
background-blur = true
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--seed")
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    out = pathlib.Path(a.out); (out / "themes").mkdir(parents=True, exist_ok=True)
    (out / "themes" / "MatOS Dark").write_text(theme(seed, True))
    (out / "themes" / "MatOS Light").write_text(theme(seed, False))
    (out / "config.ghostty").write_text(CONFIG)
