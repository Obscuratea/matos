"""MatOS logo C refinement: tertiary vs accent-centre variants, plus Vox in MatOS style.

Usage: python3 logo_c.py OUT_DIR
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_concepts import tone, squircle, wordmark, ACCENTS

def colours(seed, dark, neutral_tile):
    p = lambda t, **k: tone(seed, t, **k)
    n = lambda t: tone(seed, t, chroma=0.014)
    if dark:
        c = dict(bg=n(10), ink=n(92), sub=n(70), bar=p(90), tertiary=tone(seed, 80, hue_shift=60),
                 accent=p(72), hi=p(42), lo=p(22))
        if neutral_tile:
            c.update(hi=n(34), lo=n(16), bar=n(94))
    else:
        c = dict(bg=n(97), ink=n(12), sub=n(40), bar=p(28), tertiary=tone(seed, 52, hue_shift=60),
                 accent=p(55), hi=p(95), lo=p(80))
        if neutral_tile:
            c.update(hi=n(99), lo=n(86), bar=n(22))
    return c

def tile(c, uid):
    return f"""<defs>
  <linearGradient id="g{uid}" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="{c['hi']}"/><stop offset="1" stop-color="{c['lo']}"/></linearGradient>
  <linearGradient id="h{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="s{uid}" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity=".28"/></filter>
</defs>
<path d="{squircle(50, 50, 46)}" fill="url(#g{uid})" filter="url(#s{uid})"/>
<path d="{squircle(50, 50, 45.2)}" fill="none" stroke="url(#h{uid})" stroke-width="1.6"/>"""

def pills(bars, c, centre_key):
    """bars: list of (x, height) hanging from y=27, width 15; the middle one gets centre_key."""
    mid = len(bars) // 2
    return "".join(f'<rect x="{x}" y="27" width="{w}" height="{h}" rx="{w / 2}" fill="{c[centre_key] if i == mid else c["bar"]}"/>'
                   for i, (x, w, h) in enumerate(bars))

M_BARS = [(22, 15, 47), (42.5, 15, 29), (63, 15, 47)]
V_BARS = [(17, 10.5, 20), (31, 10.5, 33), (45, 10.5, 47), (59, 10.5, 33), (72.5, 10.5, 20)]

VARIANTS = [
    ("C1  tinted tile, tertiary centre", False, "tertiary", M_BARS),
    ("C2  glass tile, accent centre", True, "accent", M_BARS),
    ("Vox in MatOS style", True, "accent", V_BARS),
]

def icon(seed, dark, neutral, key, bars, uid):
    c = colours(seed, dark, neutral)
    return c, tile(c, uid) + pills(bars, c, key)

def main(out):
    os.makedirs(out, exist_ok=True)
    CW, CH, LAB, HEAD = 270, 200, 250, 50
    parts = []
    for vi, (name, neutral, key, bars) in enumerate(VARIANTS):
        y = HEAD + vi * (CH + 16)
        parts.append(f'<text x="16" y="{y + 105}" font-family="Roboto Flex" font-weight="600" font-size="17" fill="#ddd">{name}</text>')
        for ai, (aname, seed) in enumerate(ACCENTS):
            for di, dark in enumerate((True, False)):
                x = LAB + (ai * 2 + di) * CW
                c, body = icon(seed, dark, neutral, key, bars, f"{vi}{ai}{di}")
                g = lambda s, gx, gy, k: f'<g transform="translate({gx},{gy}) scale({s})">{icon(seed, dark, neutral, key, bars, f"{vi}{ai}{di}{k}")[1]}</g>'
                parts.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="{c["bg"]}"/>'
                             + g(1.3, x + 14, y + 14, "a") + g(0.48, x + 160, y + 20, "b")
                             + g(0.32, x + 160, y + 80, "c") + g(0.16, x + 205, y + 88, "d"))
                if bars is M_BARS:
                    parts.append(wordmark(x + 160, y + 160, 30, c))
                else:
                    parts.append(f'<text x="{x + 160}" y="{y + 160}" font-family="Roboto Flex" font-size="30" fill="{c["ink"]}"><tspan font-weight="700">Vox</tspan></text>')
        # master SVGs (light, default accent) for this variant
        for dark in (False, True):
            _, body = icon(ACCENTS[0][1], dark, neutral, key, bars, "m")
            fname = f"{['c1', 'c2', 'vox'][vi]}-{'dark' if dark else 'light'}.svg"
            with open(os.path.join(out, fname), "w") as f:
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="512" height="512">{body}</svg>')
    heads = "".join(f'<text x="{LAB + ai * 2 * CW + 12}" y="32" font-family="Roboto Flex" font-size="17" fill="#aaa">{n}  {s}</text>'
                    for ai, (n, s) in enumerate(ACCENTS))
    tw, th = LAB + 6 * CW, HEAD + 3 * (CH + 16)
    with open(os.path.join(out, "c-refine-sheet.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}"><rect width="100%" height="100%" fill="#1b1b1f"/>{heads}{"".join(parts)}</svg>')

if __name__ == "__main__":
    main(sys.argv[1])
