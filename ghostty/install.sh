#!/usr/bin/env bash
# Install the MatOS Ghostty theme + config. Backs up the current config once. Safe to run again.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
dest=~/.config/ghostty
python3 "$here/../tools/gen_ghostty.py" "$here/../build/ghostty" "$@"
mkdir -p "$dest/themes"
[ -e "$dest/config.ghostty.obscura" ] || cp "$dest/config.ghostty" "$dest/config.ghostty.obscura" 2>/dev/null || true
cp "$here/../build/ghostty/themes/"* "$dest/themes/"
cp "$here/../build/ghostty/config.ghostty" "$dest/config.ghostty"
echo "Installed. Open a new Ghostty window (or press Ctrl+Shift+, to reload). Old config: $dest/config.ghostty.obscura"
