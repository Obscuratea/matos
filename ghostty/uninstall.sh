#!/usr/bin/env bash
set -euo pipefail
d=~/.config/ghostty
[ -e "$d/config.ghostty.obscura" ] && mv "$d/config.ghostty.obscura" "$d/config.ghostty"
rm -f "$d/themes/MatOS Dark" "$d/themes/MatOS Light"
echo "Restored the previous Ghostty config."
