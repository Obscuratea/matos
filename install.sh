#!/usr/bin/env bash
# Build and install MatOS into your user profile. No root needed. Safe to run again.
#
#   ./install.sh                 build + install; switch themes yourself
#   ./install.sh --apply         also switch the desktop to MatOS Dark
#   ./install.sh --apply light   ...or MatOS Light
#   ./install.sh --seed '#hex'   build for a specific accent (default: your KDE accent, else Lavender)
#
# Every --apply first saves the settings MatOS changes to ~/.local/share/matos/backup/<time>;
# ./restore.sh puts the most recent one back.
# Needs (not installed by this script): kvantum, kwin-effect-rounded-corners, rsvg-convert, python-pillow, python-fonttools.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"

apply=0; variant=dark; seed=()
while [ $# -gt 0 ]; do
    case "$1" in
        --apply) apply=1; case "${2:-}" in dark|light) variant=$2; shift ;; esac ;;
        --seed) seed=(--seed "$2"); shift ;;
        -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown option: $1 (try --help)" >&2; exit 2 ;;
    esac
    shift
done

missing=()
for c in rsvg-convert kwriteconfig6 kreadconfig6 plasma-apply-colorscheme plasma-apply-desktoptheme qdbus6; do
    command -v "$c" >/dev/null || missing+=("$c")
done
python3 -c "import PIL, fontTools" 2>/dev/null || missing+=("python-pillow / python-fonttools")
[ -d /usr/share/Kvantum ] || missing+=("kvantum")
[ -e /usr/lib/qt6/plugins/kwin/effects/plugins/kwin4_effect_shapecorners.so ] || missing+=("kwin-effect-rounded-corners")
if [ ${#missing[@]} -gt 0 ]; then
    echo "Missing: ${missing[*]}"
    echo "On CachyOS/Arch: sudo pacman -S kvantum kwin-effect-rounded-corners librsvg python-pillow python-fonttools"
    exit 1
fi
# (no grep -q after a pipe: under pipefail an early exit SIGPIPEs fc-list and reads as "missing")
if ! fc-list : family | grep -i 'Roboto Flex' >/dev/null; then
    mkdir -p ~/.local/share/fonts/matos && cp fonts/RobotoFlex.ttf fonts/OFL.txt ~/.local/share/fonts/matos/ && fc-cache -f >/dev/null
    echo "Installed Roboto Flex (OFL) to ~/.local/share/fonts/matos"
fi

state=~/.local/share/matos
V=$([ "$variant" = dark ] && echo MatOSDark || echo MatOSLight)

echo "Building"
python3 tools/palette.py "${seed[@]}" --check
python3 tools/gen_colors.py build/color-schemes "${seed[@]}" >/dev/null
python3 tools/gen_plasma.py build/desktoptheme/MatOS >/dev/null
python3 tools/gen_kvantum.py both build/Kvantum "${seed[@]}" >/dev/null
python3 tools/gen_aurorae.py both build/aurorae "${seed[@]}" >/dev/null
python3 tools/gen_icons.py build/icons/MatOS-Icons >/dev/null
[ -d build/wallpapers/MatOS/contents/images_dark ] || python3 tools/gen_wallpaper.py build/wallpapers/MatOS "${seed[@]}" >/dev/null
python3 "Scripts for Claude/build_logo.py" brand/logo "${seed[@]}" >/dev/null

echo "Installing"
mkdir -p ~/.local/share/{color-schemes,plasma/desktoptheme,aurorae/themes,wallpapers} ~/.config/Kvantum \
         ~/.local/share/icons/hicolor/scalable/apps
cp build/color-schemes/MatOS*.colors ~/.local/share/color-schemes/
rm -rf ~/.local/share/plasma/desktoptheme/MatOS && cp -r build/desktoptheme/MatOS ~/.local/share/plasma/desktoptheme/
for v in MatOSDark MatOSLight; do
    rm -rf ~/.config/Kvantum/$v ~/.local/share/aurorae/themes/$v
    cp -r build/Kvantum/$v ~/.config/Kvantum/
    cp -r build/aurorae/$v ~/.local/share/aurorae/themes/
done
rm -rf ~/.local/share/icons/MatOS-Icons && cp -r build/icons/MatOS-Icons ~/.local/share/icons/
rm -rf ~/.local/share/wallpapers/MatOS && cp -r build/wallpapers/MatOS ~/.local/share/wallpapers/
# launcher icon: the flat glyph; its fallback colours match the variant in case the panel doesn't recolour it
python3 - "$variant" "${seed[@]}" <<'EOF'
import sys, pathlib
sys.path.insert(0, "tools")
import palette as P
dark = sys.argv[1] == "dark"
seed = P.tokens(sys.argv[3] if len(sys.argv) > 3 else None)["seed"]
s = P.scheme(seed, dark)
svg = pathlib.Path("brand/logo/matos-glyph.svg").read_text()
svg = svg.replace("color:#2a2a30", f"color:{s['on_surface']}").replace("color:#b69cff", f"color:{s['accent']}")
# the panel recolours ColorScheme-Highlight to the text colour too, so bake the accent into the middle pill
svg = svg.replace('class="ColorScheme-Highlight" fill="currentColor"', f'fill="{s["accent"]}"')
pathlib.Path.home().joinpath(".local/share/icons/hicolor/scalable/apps/matos.svg").write_text(svg)
EOF

if [ "$apply" = 0 ]; then
    echo; echo "Installed. Run ./install.sh --apply to switch to MatOS (your current setup is backed up first)."
    exit 0
fi

# ---- backup: everything --apply touches ----
bk=$state/backup/$(date +%Y%m%d-%H%M%S)
echo "Backing up your current settings to $bk"
mkdir -p "$bk"
for f in kdeglobals kwinrc plasmarc plasmashellrc plasma-org.kde.plasma.desktop-appletsrc Kvantum/kvantum.kvconfig; do
    [ -e ~/.config/$f ] && cp ~/.config/$f "$bk/$(basename $f)"
done
[ -d ~/.config/kdedefaults ] && cp -r ~/.config/kdedefaults "$bk/kdedefaults"
{   # names to switch back to (Global Themes keep these in kdedefaults, so read through kreadconfig6)
    echo "colorscheme=$(kreadconfig6 --group General --key ColorScheme)"
    echo "desktoptheme=$(kreadconfig6 --file plasmarc --group Theme --key name)"
    echo "icons=$(kreadconfig6 --group Icons --key Theme)"
    echo "kvantum=$(kreadconfig6 --file ~/.config/Kvantum/kvantum.kvconfig --group General --key theme)"
} > "$bk/names"

echo "Applying MatOS ${variant^}"
plasma-apply-colorscheme "$V" >/dev/null
plasma-apply-desktoptheme MatOS >/dev/null
kwriteconfig6 --file ~/.config/Kvantum/kvantum.kvconfig --group General --key theme "$V"
kwriteconfig6 --group KDE --key widgetStyle kvantum
/usr/lib/plasma-changeicons MatOS-Icons >/dev/null 2>&1 || kwriteconfig6 --group Icons --key Theme MatOS-Icons
python3 tools/gen_kwin.py "$variant" "${seed[@]}" --apply
# fonts: Roboto Flex everywhere except monospace
if fc-list : family | grep -i 'Roboto Flex' >/dev/null; then
    f() { echo "Roboto Flex,$1,-1,5,$2,0,0,0,0,0,0,0,0,0,0,1"; }
    kwriteconfig6 --group General --key font "$(f 11 400)"
    kwriteconfig6 --group General --key menuFont "$(f 11 400)"
    kwriteconfig6 --group General --key toolBarFont "$(f 10 400)"
    kwriteconfig6 --group General --key smallestReadableFont "$(f 9 400)"
    kwriteconfig6 --group WM --key activeFont "$(f 11 600)"
fi
qdbus6 org.kde.KWin /KWin reconfigure >/dev/null
# panel launcher icon + wallpaper (through plasmashell so it doesn't overwrite our edits)
qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript '
for (const p of panels()) for (const w of p.widgets())
    if (w.type == "org.kde.plasma.kickoff") { w.currentConfigGroup = ["General"]; w.writeConfig("icon", "matos"); }
for (const d of desktops()) {
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file://'"$HOME"'/.local/share/wallpapers/MatOS/");
}' >/dev/null

echo
echo "MatOS ${variant^} is on. Apps that were already open pick up the new style when restarted."
echo "To go back: ./restore.sh"
