"""MatOS logo concepts: renders a comparison sheet (concepts x accents, dark + light).

Usage: python3 logo_concepts.py OUT_DIR
Writes one SVG per concept/accent plus concepts-sheet.svg; render with rsvg-convert.
"""
import math, os, sys

# ---- colour: OKLCH tonal palette (approximation of Material tones) ----

def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _gam(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def hex_to_oklch(h):
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360

def _oklch_rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def tone(h, t, chroma=None, hue_shift=0):
    """Colour at Material-style tone t (0-100) with the seed's hue."""
    _, C, H = hex_to_oklch(h)
    C = min(C, 0.16) if chroma is None else chroma
    H = (H + hue_shift) % 360
    L = t / 100
    while True:  # reduce chroma until in sRGB gamut
        rgb = _oklch_rgb(L, C, H)
        if all(-1e-4 <= c <= 1 + 1e-4 for c in rgb) or C <= 0:
            break
        C -= 0.004
    return "#" + "".join(f"{round(_gam(min(1, max(0, c))) * 255):02x}" for c in rgb)

def palette(seed, dark):
    p = lambda t, **k: tone(seed, t, **k)
    q = lambda t: tone(seed, t, hue_shift=60)   # tertiary
    n = lambda t: tone(seed, t, chroma=0.012)   # neutral
    if dark:
        return dict(bg=n(10), ink=n(92), sub=n(70), primary=p(80), on_primary=p(20),
                    container=p(30), on_container=p(90), tertiary=q(80), glass_hi=p(92), glass_lo=p(38))
    return dict(bg=n(97), ink=n(12), sub=n(40), primary=p(45), on_primary=p(100),
                container=p(88), on_container=p(12), tertiary=q(55), glass_hi=p(96), glass_lo=p(80))

# ---- shapes ----

def squircle(cx, cy, r, n=5.0, steps=160):
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        c, s = math.cos(a), math.sin(a)
        pts.append((cx + r * math.copysign(abs(c) ** (2 / n), c),
                    cy + r * math.copysign(abs(s) ** (2 / n), s)))
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"

def cookie(cx, cy, r, lobes=8, depth=0.09, steps=240):
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        rr = r * (1 - depth + depth * math.cos(lobes * a))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"

def tile(c, uid):
    """macOS-style squircle tile with a tinted 'glass' gradient and top gloss (100x100 space)."""
    return f"""
  <defs>
    <linearGradient id="g{uid}" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="{c['glass_hi']}"/><stop offset="1" stop-color="{c['glass_lo']}"/>
    </linearGradient>
    <linearGradient id="h{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <filter id="s{uid}" x="-20%" y="-20%" width="140%" height="150%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity=".28"/>
    </filter>
  </defs>
  <path d="{squircle(50, 50, 46)}" fill="url(#g{uid})" filter="url(#s{uid})"/>
  <path d="{squircle(50, 50, 45.2)}" fill="none" stroke="url(#h{uid})" stroke-width="1.6"/>"""

def concept_arch(c, uid):
    """A: lowercase m from two thick round-capped arches."""
    m = "M31,70 V47 A9.5,9.5 0 0 1 50,47 V70 M50,47 A9.5,9.5 0 0 1 69,47 V70"
    return tile(c, uid) + f"""
  <path d="{m}" fill="none" stroke="{c['on_container']}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="69" cy="30" r="6" fill="{c['tertiary']}"/>"""

def concept_bloom(c, uid):
    """B: Material 3 Expressive 'cookie' shape blooming out of the squircle."""
    return tile(c, uid) + f"""
  <path d="{cookie(50, 50, 28, lobes=9, depth=0.08)}" fill="{c['primary']}"/>
  <path d="{cookie(50, 50, 13, lobes=6, depth=0.1)}" fill="{c['tertiary']}"/>"""

def concept_pills(c, uid):
    """C: an M made of three pills; the short middle one in tertiary."""
    return tile(c, uid) + f"""
  <rect x="22" y="27" width="15" height="47" rx="7.5" fill="{c['on_container']}"/>
  <rect x="42.5" y="27" width="15" height="29" rx="7.5" fill="{c['tertiary']}"/>
  <rect x="63" y="27" width="15" height="47" rx="7.5" fill="{c['on_container']}"/>"""

CONCEPTS = [("A  Arch m", concept_arch), ("B  Bloom", concept_bloom), ("C  Pills", concept_pills)]
ACCENTS = [("CachyOS green", "#00aa88"), ("Blue", "#3d7cff"), ("Rose", "#e0457b")]

def wordmark(x, y, size, c):
    return (f'<text x="{x}" y="{y}" font-family="Roboto Flex" font-size="{size}" fill="{c["ink"]}">'
            f'<tspan font-weight="700">Mat</tspan><tspan font-weight="300" fill="{c["sub"]}">OS</tspan></text>')

def cell(fn, seed, dark, ox, oy, uid):
    c = palette(seed, dark)
    g = lambda s, x, y, k: f'<g transform="translate({x},{y}) scale({s})">{fn(c, f"{uid}{k}")}</g>'
    return (f'<rect x="{ox}" y="{oy}" width="300" height="230" fill="{c["bg"]}"/>'
            + g(1.5, ox + 20, oy + 20, "a")
            + g(0.32, ox + 190, oy + 40, "b") + g(0.16, ox + 240, oy + 48, "c")
            + wordmark(ox + 185, oy + 120, 34, c)
            + f'<text x="{ox + 185}" y="{oy + 150}" font-family="Roboto Flex" font-size="12" fill="{c["sub"]}">{"dark" if dark else "light"}</text>'
            + f'<g transform="translate({ox + 20},{oy + 178})">'
            + "".join(f'<circle cx="{i * 24 + 9}" cy="9" r="9" fill="{c[k]}"/>'
                      for i, k in enumerate(["primary", "container", "tertiary", "glass_hi", "glass_lo"]))
            + "</g>")

def main(out):
    os.makedirs(out, exist_ok=True)
    W, H, HEAD, LAB = 600, 230, 60, 150
    rows = []
    for ci, (cname, fn) in enumerate(CONCEPTS):
        y = HEAD + ci * (H + 20)
        rows.append(f'<text x="16" y="{y + 120}" font-family="Roboto Flex" font-weight="700" font-size="22" fill="#ddd">{cname}</text>')
        for ai, (aname, seed) in enumerate(ACCENTS):
            x = LAB + ai * (W + 20)
            rows.append(cell(fn, seed, True, x, y, f"{ci}{ai}d"))
            rows.append(cell(fn, seed, False, x + 300, y, f"{ci}{ai}l"))
            # standalone master icon
            with open(os.path.join(out, f"logo-{'abc'[ci]}-{aname.split()[0].lower()}.svg"), "w") as f:
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="512" height="512">'
                        f'{fn(palette(seed, False), "m")}</svg>')
    heads = "".join(f'<text x="{LAB + ai * (W + 20) + 16}" y="38" font-family="Roboto Flex" font-size="18" fill="#aaa">{n}  {s}</text>'
                    for ai, (n, s) in enumerate(ACCENTS))
    tw, th = LAB + 3 * (W + 20), HEAD + 3 * (H + 20)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}" viewBox="0 0 {tw} {th}">'
           f'<rect width="100%" height="100%" fill="#1b1b1f"/>{heads}{"".join(rows)}</svg>')
    with open(os.path.join(out, "concepts-sheet.svg"), "w") as f:
        f.write(svg)

if __name__ == "__main__":
    main(sys.argv[1])
