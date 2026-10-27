#!/usr/bin/env bash
# Render the Qt widget gallery with MatOS colours + Kvantum against a scratch config.
# Never touches ~/.config. Usage: preview.sh <dark|light> [#seed]
set -euo pipefail
here=$(cd "$(dirname "$0")/.." && pwd)
variant=${1:-dark}; seed=${2:-#b69cff}
V=$([ "$variant" = dark ] && echo MatOSDark || echo MatOSLight)
S=${PREVIEW_DIR:-$here/build/preview}; rm -rf "$S/cfg" "$S/data"; mkdir -p "$S/cfg/Kvantum" "$S/data/color-schemes"
python3 "$here/tools/gen_colors.py" "$S/data/color-schemes" --seed "$seed" >/dev/null
cp ~/.config/kdeglobals "$S/cfg/kdeglobals"
XDG_DATA_HOME=$S/data XDG_CONFIG_HOME=$S/cfg plasma-apply-colorscheme "$V" >/dev/null 2>&1 || true
python3 "$here/tools/gen_kvantum.py" "$variant" "$S/cfg/Kvantum" --seed "$seed" >/dev/null
printf '[General]\ntheme=%s\n' "$V" > "$S/cfg/Kvantum/kvantum.kvconfig"
out="$S/$variant-${seed#\#}.png"
XDG_DATA_HOME=$S/data XDG_CONFIG_HOME=$S/cfg QT_STYLE_OVERRIDE=kvantum QT_QPA_PLATFORMTHEME=kde \
  QT_FONT_DPI=96 QT_SCALE_FACTOR=${SCALE:-1} python3 "$here/tools/preview_app.py" "$out"
echo "$out"
