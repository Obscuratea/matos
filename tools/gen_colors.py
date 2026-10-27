"""MatOS KDE colour schemes (MatOSLight / MatOSDark) from tools/palette.py.

Usage: python3 tools/gen_colors.py OUT_DIR [--seed HEX]
Material roles map onto KDE sets: Window = chrome (sidebars, toolbars), View = content,
Selection = primary container (richer than M3's
secondary-container default: MatOS is "fun and classy", not corporate), Tooltip = inverse surface.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P

def rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))

def extras(seed, dark):
    """Status colours Material doesn't define: green for positive, amber for neutral/warning."""
    t = 80 if dark else 40
    return {"positive": P.solve(t, 0.13, 150), "neutral": P.solve(t, 0.14, 75)}

def colour_set(s, x, bg, alt, fg, fg_inactive, focus):
    return {
        "BackgroundNormal": bg, "BackgroundAlternate": alt,
        "ForegroundNormal": fg, "ForegroundInactive": fg_inactive,
        "ForegroundActive": s["primary"], "ForegroundLink": s["primary"], "ForegroundVisited": s["tertiary"],
        "ForegroundNegative": s["error"], "ForegroundNeutral": x["neutral"], "ForegroundPositive": x["positive"],
        "DecorationFocus": focus, "DecorationHover": focus,
    }

def scheme(seed, dark):
    s = P.scheme(seed, dark)
    x = extras(seed, dark)
    std = dict(fg=s["on_surface"], fg_inactive=s["on_surface_variant"], focus=s["primary"])
    sets = {
        "Window": colour_set(s, x, s["surface_container"], s["surface_container_high"], **std),
        "View": colour_set(s, x, s["surface_container_low"], s["surface_container"], **std),
        "Button": colour_set(s, x, s["surface_container_high"], s["surface_container_highest"], **std),
        "Header": colour_set(s, x, s["surface_container"], s["surface_container_high"], **std),
        "Header][Inactive": colour_set(s, x, s["surface_container_low"], s["surface_container"], **std),
        "Selection": colour_set(s, x, s["primary_container"], s["secondary_container"],
                                s["on_primary_container"], s["on_primary_container"], s["primary"]),
        "Tooltip": colour_set(s, x, s["inverse_surface"], s["inverse_surface"],
                              s["inverse_on_surface"], s["inverse_on_surface"], s["inverse_primary"]),
    }
    # Complementary is Plasma's "always dark" set (OSDs, lock screen): use the dark scheme either way
    d = P.scheme(seed, True)
    sets["Complementary"] = colour_set(d, extras(seed, True), d["surface_container"], d["surface_container_high"],
                                       d["on_surface"], d["on_surface_variant"], d["primary"])
    name = "MatOSDark" if dark else "MatOSLight"
    lines = [f"[General]\nColorScheme={name}\nName=MatOS {'Dark' if dark else 'Light'}\nshadeSortColumn=true\n",
             "[KDE]\ncontrast=4\n",
             "[ColorEffects:Disabled]\nColor=" + rgb(s["on_surface"]) + "\nColorAmount=0\nColorEffect=0\n"
             "ContrastAmount=0.5\nContrastEffect=1\nIntensityAmount=0\nIntensityEffect=0\n",
             "[ColorEffects:Inactive]\nChangeSelectionColor=false\nEnable=false\n"]
    for set_name, vals in sets.items():
        lines.append(f"[Colors:{set_name}]\n" + "".join(f"{k}={rgb(v)}\n" for k, v in sorted(vals.items())))
    lines.append("[WM]\n" + "".join(f"{k}={rgb(v)}\n" for k, v in {
        "activeBackground": s["surface_container"], "activeBlend": s["surface_container"],
        "activeForeground": s["on_surface"], "inactiveBackground": s["surface_container_low"],
        "inactiveBlend": s["surface_container_low"], "inactiveForeground": s["on_surface_variant"],
    }.items()))
    return name, "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed")
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    os.makedirs(a.out, exist_ok=True)
    for dark in (False, True):
        name, text = scheme(seed, dark)
        with open(os.path.join(a.out, f"{name}.colors"), "w") as f:
            f.write(text)
        print(os.path.join(a.out, f"{name}.colors"))

if __name__ == "__main__":
    main()
