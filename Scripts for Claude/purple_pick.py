"""Compare soft-purple default-accent candidates on the C2 + Vox dark logos.

Usage: python3 purple_pick.py OUT_DIR
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_c import icon, M_BARS, V_BARS
from logo_concepts import wordmark

CANDIDATES = [("Lavender", "#b69cff"), ("Periwinkle violet", "#9d8cff"),
              ("Orchid", "#c792ea"), ("Material baseline", "#6750a4")]

def main(out):
    CW, CH = 440, 230
    parts = []
    for i, (name, seed) in enumerate(CANDIDATES):
        x = i * CW
        for row, dark in enumerate((True, False)):
            y = 50 + row * (CH + 10)
            c, _ = icon(seed, dark, True, "accent", M_BARS, "x")
            g = lambda bars, s, gx, gy, k: (f'<g transform="translate({gx},{gy}) scale({s})">'
                                            f'{icon(seed, dark, True, "accent", bars, f"{i}{row}{k}")[1]}</g>')
            parts.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="{c["bg"]}"/>'
                         + g(M_BARS, 1.3, x + 20, y + 16, "m") + g(V_BARS, 1.3, x + 160, y + 16, "v")
                         + g(M_BARS, 0.32, x + 310, y + 30, "s") + g(V_BARS, 0.32, x + 350, y + 30, "t")
                         + g(M_BARS, 0.16, x + 318, y + 80, "u") + g(V_BARS, 0.16, x + 358, y + 80, "w")
                         + wordmark(x + 26, y + 200, 30, c)
                         + f'<rect x="{x + 300}" y="{y + 170}" width="110" height="34" rx="17" fill="{c["accent"]}"/>'
                         + f'<text x="{x + 355}" y="{y + 193}" text-anchor="middle" font-family="Roboto Flex" font-weight="600" font-size="14" fill="{c["bg"]}">Button</text>')
        parts.append(f'<text x="{x + 20}" y="34" font-family="Roboto Flex" font-size="17" fill="#ccc">{name}  {seed}</text>')
    tw, th = 4 * CW, 50 + 2 * (CH + 10)
    with open(os.path.join(out, "purple-sheet.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}"><rect width="100%" height="100%" fill="#1b1b1f"/>{"".join(parts)}</svg>')

if __name__ == "__main__":
    main(sys.argv[1])
