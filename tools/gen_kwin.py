#!/usr/bin/env python3
"""KWin settings MatOS needs: the Rounded Corners effect (window shape, outline, shadow),
blur, and the MatOS decoration. Prints `kwriteconfig6` commands, or applies them with --apply.

Keys come from kwin-effect-rounded-corners 0.11 (src/kcm/options.kcfg, group [Round-Corners]).
Usage: gen_kwin.py <dark|light> [--seed HEX] [--apply]
"""
import argparse, pathlib, shlex, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P

RADIUS = 18  # squircle; panel/popups use 14-16 so windows read as the "biggest" surface


def settings(seed, dark):
    s = P.scheme(seed, dark)
    rc = {
        ("Plugins", "kwin4_effect_shapecornersEnabled"): "true",
        ("Plugins", "blurEnabled"): "true",
        ("Round-Corners", "Size"): RADIUS,
        ("Round-Corners", "InactiveCornerRadius"): RADIUS,
        ("Round-Corners", "UseSquircleShape"): "true",
        # hairline outline in the outline-variant tone
        ("Round-Corners", "OutlineThickness"): 1,
        ("Round-Corners", "InactiveOutlineThickness"): 1,
        ("Round-Corners", "OutlineColor"): s["outline_variant"],
        ("Round-Corners", "InactiveOutlineColor"): s["outline_variant"],
        ("Round-Corners", "ActiveOutlineAlpha"): 0 if dark else 200,
        ("Round-Corners", "InactiveOutlineAlpha"): 0 if dark else 150,
        # glass highlight: only reads on dark surfaces (the effect only re-reads these when it is reloaded)
        ("Round-Corners", "SecondOutlineThickness"): 1 if dark else 0,
        ("Round-Corners", "InactiveSecondOutlineThickness"): 1 if dark else 0,
        ("Round-Corners", "SecondOutlineColor"): s["primary"],  # soft purple glass line (the accent, lightened)
        ("Round-Corners", "InactiveSecondOutlineColor"): s["primary"],  # soft purple glass line (the accent, lightened)
        ("Round-Corners", "ActiveSecondOutlineAlpha"): 230,
        ("Round-Corners", "InactiveSecondOutlineAlpha"): 110,
        ("Round-Corners", "OuterOutlineThickness"): 0,
        ("Round-Corners", "InactiveOuterOutlineThickness"): 0,
        # soft custom shadows (the decoration draws none)
        ("Round-Corners", "UseNativeDecorationShadows"): "true",  # the shadow is painted by the Aurorae decoration (gen_aurorae.py)
        ("Round-Corners", "ActiveShadowUseCustom"): "true",
        ("Round-Corners", "InactiveShadowUseCustom"): "true",
        ("Round-Corners", "ShadowSize"): 28,  # = SHADOW_PAD in gen_aurorae.py (unused while the shadow alpha is 0)
        ("Round-Corners", "InactiveShadowSize"): 28,
        ("Round-Corners", "ShadowColor"): "#000000",
        ("Round-Corners", "InactiveShadowColor"): "#000000",
        ("Round-Corners", "ActiveShadowAlpha"): 0,  # 0 = the effect adds no shadow of its own; with it on, sides double up
        ("Round-Corners", "InactiveShadowAlpha"): 0,
        ("Round-Corners", "DisableRoundMaximize"): "true",
        ("Round-Corners", "DisableOutlineMaximize"): "true",
        ("org.kde.kdecoration2", "library"): "org.kde.kwin.aurorae",
        ("org.kde.kdecoration2", "theme"): f"__aurorae__svg__{'MatOSDark' if dark else 'MatOSLight'}",
        ("org.kde.kdecoration2", "BorderSize"): "None",
        ("org.kde.kdecoration2", "BorderSizeAuto"): "false",
    }
    return rc


def commands(rc):
    for (group, key), val in rc.items():
        v = str(val)
        if v.startswith("#"):  # kwriteconfig wants r,g,b for colours
            v = ",".join(str(round(c * 255)) for c in P.hex_rgb(v))
        yield ["kwriteconfig6", "--file", "kwinrc", "--group", group, "--key", key, v]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=["dark", "light"])
    ap.add_argument("--seed")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    for cmd in commands(settings(seed, a.variant == "dark")):
        if a.apply:
            subprocess.run(cmd, check=True)
        else:
            print(shlex.join(cmd))
