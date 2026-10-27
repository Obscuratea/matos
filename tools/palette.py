"""MatOS palette: one accent seed -> Material 3 colour roles + MatOS extras.

Every theme layer is generated from this module. Tones are exact CIELAB L* (what Material's
contrast guarantees rest on); hue and chroma come from OKLCH so hues stay perceptually even.

CLI:
  python3 tools/palette.py [--seed HEX] [--json | --css] [--check]
  With no --seed, reads the KDE accent ([General] AccentColor) and falls back to Lavender.
"""
import argparse, json, math, subprocess, sys

DEFAULT_SEED = "#b69cff"   # Lavender
GRADIENT_SHIFT = 16        # degrees of OKLCH hue: Lavender -> Orchid #c792ea

# ---------- colour maths ----------

def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _gam(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def rgb_hex(rgb):
    return "#" + "".join(f"{round(min(1, max(0, c)) * 255):02x}" for c in rgb)

def oklch_from_hex(h):
    r, g, b = (_lin(c) for c in hex_rgb(h))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360

def _oklch_linear(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def _in_gamut(rgb): return all(-1e-5 <= c <= 1 + 1e-5 for c in rgb)

def luminance(rgb_lin): return 0.2126 * rgb_lin[0] + 0.7152 * rgb_lin[1] + 0.0722 * rgb_lin[2]

def tone_to_y(t):
    fy = (t + 16) / 116
    return fy ** 3 if fy ** 3 > 216 / 24389 else (116 * fy - 16) / (24389 / 27)

def tone_of(h):
    y = luminance([_lin(c) for c in hex_rgb(h)])
    return 116 * (y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116) - 16

def solve(tone, chroma, hue):
    """sRGB hex with CIELAB L* == tone, OKLCH hue == hue, chroma as close to `chroma` as gamut allows."""
    if tone <= 0: return "#000000"
    if tone >= 100: return "#ffffff"
    target = tone_to_y(tone)
    C = chroma
    while True:
        lo, hi = 0.0, 1.0
        for _ in range(40):   # luminance rises monotonically with OKLab L at fixed a, b
            mid = (lo + hi) / 2
            if luminance(_oklch_linear(mid, C, hue)) < target: lo = mid
            else: hi = mid
        rgb = _oklch_linear((lo + hi) / 2, C, hue)
        if _in_gamut(rgb) or C <= 0:
            return rgb_hex([_gam(max(0, c)) for c in rgb])
        C = max(0, C - 0.002)

def contrast(a, b):
    ya, yb = (luminance([_lin(c) for c in hex_rgb(x)]) for x in (a, b))
    hi, lo = max(ya, yb), min(ya, yb)
    return (hi + 0.05) / (lo + 0.05)

# ---------- palettes ----------

class Tonal:
    def __init__(self, hue, chroma): self.hue, self.chroma = hue, chroma
    def __call__(self, t): return solve(t, self.chroma, self.hue)

def tonal_palettes(seed):
    _, C, H = oklch_from_hex(seed)
    C = max(min(C, 0.17), 0.09)   # keep a muted seed colourful, tame a neon one
    return dict(
        primary=Tonal(H, C),
        secondary=Tonal(H, C * 0.3),
        tertiary=Tonal((H + 60) % 360, C * 0.75),
        neutral=Tonal(H, 0.012),
        neutral_variant=Tonal(H, 0.024),
        error=Tonal(27, 0.17),
        gradient=Tonal((H + GRADIENT_SHIFT) % 360, C),
    )

# Material 3 roles: (palette, light tone, dark tone)
ROLES = {
    "primary": ("primary", 40, 80), "on_primary": ("primary", 100, 20),
    "primary_container": ("primary", 90, 30), "on_primary_container": ("primary", 10, 90),
    "secondary": ("secondary", 40, 80), "on_secondary": ("secondary", 100, 20),
    "secondary_container": ("secondary", 90, 30), "on_secondary_container": ("secondary", 10, 90),
    "tertiary": ("tertiary", 40, 80), "on_tertiary": ("tertiary", 100, 20),
    "tertiary_container": ("tertiary", 90, 30), "on_tertiary_container": ("tertiary", 10, 90),
    "error": ("error", 40, 80), "on_error": ("error", 100, 20),
    "error_container": ("error", 90, 30), "on_error_container": ("error", 10, 90),
    "surface": ("neutral", 98, 6), "surface_dim": ("neutral", 87, 6), "surface_bright": ("neutral", 98, 24),
    "surface_container_lowest": ("neutral", 100, 4), "surface_container_low": ("neutral", 96, 10),
    "surface_container": ("neutral", 94, 12), "surface_container_high": ("neutral", 92, 17),
    "surface_container_highest": ("neutral", 90, 22),
    "on_surface": ("neutral", 10, 90), "on_surface_variant": ("neutral_variant", 30, 80),
    "outline": ("neutral_variant", 50, 60), "outline_variant": ("neutral_variant", 80, 30),
    "inverse_surface": ("neutral", 20, 90), "inverse_on_surface": ("neutral", 95, 20),
    "inverse_primary": ("primary", 80, 40),
    "shadow": ("neutral", 0, 0), "scrim": ("neutral", 0, 0),
    # MatOS extras
    "accent": ("primary", 55, 72),          # brand accent as drawn in logos/selection
    "gradient_start": ("primary", 55, 72), "gradient_end": ("gradient", 55, 72),
}

# pairs that must stay readable (foreground, background, minimum ratio)
CONTRAST_PAIRS = [(f"on_{r}", r, 4.5) for r in ("primary", "secondary", "tertiary", "error",
                                                   "primary_container", "secondary_container",
                                                   "tertiary_container", "error_container")]
CONTRAST_PAIRS += [("on_surface", s, 4.5) for s in ("surface", "surface_dim", "surface_bright",
                                                      "surface_container_lowest", "surface_container_low",
                                                      "surface_container", "surface_container_high",
                                                      "surface_container_highest")]
CONTRAST_PAIRS += [("on_surface_variant", "surface_container_highest", 4.5),
                   ("inverse_on_surface", "inverse_surface", 4.5),
                   ("outline", "surface", 3.0), ("primary", "surface", 3.0)]

SHAPE = {"none": 0, "xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 28, "full": 9999}
GLASS = {"panel_alpha": 0.72, "menu_alpha": 0.82, "blur_px": 24, "highlight_alpha": 0.18}
TYPE = {"family": "Roboto Flex", "mono": "Roboto Mono", "base_pt": 10}
MOTION = {"spring_fast_ms": 200, "spring_default_ms": 350, "spring_slow_ms": 500,
          "easing": "cubic-bezier(0.2, 0, 0, 1)", "easing_emphasized": "cubic-bezier(0.05, 0.7, 0.1, 1)"}

def scheme(seed, dark):
    pals = tonal_palettes(seed)
    return {role: pals[p](dt if dark else lt) for role, (p, lt, dt) in ROLES.items()}

def tokens(seed=None):
    seed = (seed or system_accent() or DEFAULT_SEED).lower()
    return {"seed": seed, "light": scheme(seed, False), "dark": scheme(seed, True),
            "shape": SHAPE, "glass": GLASS, "type": TYPE, "motion": MOTION}

def check(tok):
    problems = []
    for mode in ("light", "dark"):
        s = tok[mode]
        for fg, bg, need in CONTRAST_PAIRS:
            r = contrast(s[fg], s[bg])
            if r < need:
                problems.append(f"{mode}: {fg} on {bg} = {r:.2f} (< {need})")
    return problems

def system_accent():
    """KDE accent as #rrggbb, or None when following the colour scheme's own."""
    try:
        v = subprocess.run(["kreadconfig6", "--group", "General", "--key", "AccentColor"],
                           capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    parts = v.split(",")
    if len(parts) >= 3 and all(p.strip().isdigit() for p in parts[:3]):
        return "#" + "".join(f"{int(p):02x}" for p in parts[:3])
    return v if v.startswith("#") and len(v) == 7 else None

def css(tok):
    out = []
    for mode, sel in (("light", ":root"), ("dark", '@media (prefers-color-scheme: dark) {\n  :root')):
        body = "".join(f"  --mat-{k.replace('_', '-')}: {v};\n" for k, v in tok[mode].items())
        out.append(f"{sel} {{\n{body}}}" + ("\n}" if mode == "dark" else ""))
    shared = "".join(f"  --mat-shape-{k}: {v}px;\n" for k, v in tok["shape"].items())
    shared += f"  --mat-font: '{tok['type']['family']}', sans-serif;\n  --mat-font-mono: '{tok['type']['mono']}', monospace;\n"
    shared += f"  --mat-easing: {tok['motion']['easing']};\n  --mat-easing-emphasized: {tok['motion']['easing_emphasized']};\n"
    return f"/* MatOS tokens, seed {tok['seed']} (generated by tools/palette.py) */\n:root {{\n{shared}}}\n" + "\n".join(out) + "\n"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--css", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = tokens(a.seed)
    if a.check:
        bad = check(t)
        print("\n".join(bad) if bad else f"all {len(CONTRAST_PAIRS) * 2} contrast pairs pass (seed {t['seed']})")
        sys.exit(1 if bad else 0)
    print(css(t) if a.css else json.dumps(t, indent=2))
