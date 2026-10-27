#!/usr/bin/env bash
# Put back the settings saved by the most recent `./install.sh --apply` (or the backup you name).
#   ./restore.sh                 newest backup
#   ./restore.sh 20261027-031500 a specific one (see ~/.local/share/matos/backup)
set -euo pipefail
root=~/.local/share/matos/backup
bk=$root/${1:-$(ls -1 "$root" | sort | tail -1)}
[ -f "$bk/names" ] || { echo "no backup at $bk" >&2; exit 1; }
echo "Restoring from $bk"
. "$bk/names"

for f in kdeglobals kwinrc plasmarc; do [ -e "$bk/$f" ] && cp "$bk/$f" ~/.config/$f; done
[ -e "$bk/kvantum.kvconfig" ] && cp "$bk/kvantum.kvconfig" ~/.config/Kvantum/kvantum.kvconfig
[ -d "$bk/kdedefaults" ] && { rm -rf ~/.config/kdedefaults; cp -r "$bk/kdedefaults" ~/.config/kdedefaults; }

# re-apply by name so running apps get the change signal (copying files alone doesn't notify them)
[ -n "${colorscheme:-}" ] && plasma-apply-colorscheme "$colorscheme" >/dev/null || true
[ -n "${desktoptheme:-}" ] && plasma-apply-desktoptheme "$desktoptheme" >/dev/null || true
[ -n "${icons:-}" ] && /usr/lib/plasma-changeicons "$icons" >/dev/null 2>&1 || true
qdbus6 org.kde.KWin /KWin reconfigure >/dev/null

# panel + wallpaper live in plasmashell's own config: swap it while plasmashell is stopped
if [ -e "$bk/plasma-org.kde.plasma.desktop-appletsrc" ]; then
    kquitapp6 plasmashell >/dev/null 2>&1 || true
    sleep 2
    cp "$bk/plasma-org.kde.plasma.desktop-appletsrc" ~/.config/
    [ -e "$bk/plasmashellrc" ] && cp "$bk/plasmashellrc" ~/.config/
    (setsid kstart plasmashell >/dev/null 2>&1 &)
fi
echo "Done. Restart open apps to drop the MatOS widget style."
