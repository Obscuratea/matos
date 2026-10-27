#!/usr/bin/env bash
# Installs the MatOS skin (userChrome.css, userContent.css, prefs) into a Firefox profile
# (default: the install's default profile). Usage: ./install.sh [profile-dir] [--seed HEX]
# Backs up CSS files that are not ours (e.g. the Obscura skin) as <file>.bak-<time>, never overrides your own
# prefs, never uses sudo. Restart Firefox afterwards.
set -euo pipefail
here="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
source "$here/find-profile.sh"
profile=""; seed=()
while [ $# -gt 0 ]; do
  case "$1" in
    --seed) seed=(--seed "$2"); shift ;;
    *) profile="$1" ;;
  esac
  shift
done
profile="${profile:-$(find_profile)}"
[ -d "$profile" ] || { echo "No Firefox profile found. Pass one: ./install.sh <profile-dir>" >&2; exit 1; }
fc-list : family | grep -i 'Roboto Flex' >/dev/null || echo "note: Roboto Flex isn't installed; Firefox will fall back to Roboto/system-ui."

python3 "$here/../tools/gen_firefox.py" "$here/../build/firefox" "${seed[@]}" >/dev/null
build="$here/../build/firefox"
mkdir -p "$profile/chrome"
stamp="$(date +%Y%m%d-%H%M%S)"

put() {  # put <source> <dest>: install, backing up an existing file that is not ours
  if [ -f "$2" ] && ! cmp -s "$2" "$1" && ! grep -q "MatOS for Firefox" "$2"; then cp "$2" "$2.bak-$stamp"; echo "backed up $(basename "$2") -> $(basename "$2").bak-$stamp"; fi
  install -m644 "$1" "$2"
}
put "$build/userChrome.css" "$profile/chrome/userChrome.css"
put "$build/userContent.css" "$profile/chrome/userContent.css"
install -m644 "$build"/matos-mark-*.svg "$profile/chrome/"
# prefs live in a managed block of user.js (replaces an Obscura block too)
python3 "$here/prefs.py" install "$profile/user.js" "$build/user.js"

# launcher icon: a user-level copy of firefox.desktop with the MatOS icon (found before /usr/share/applications)
data="${XDG_DATA_HOME:-$HOME/.local/share}"
install -Dm644 "$here/../brand/logo/firefox-mark-dark.svg" "$data/icons/hicolor/scalable/apps/matos-firefox.svg"
if [ -f /usr/share/applications/firefox.desktop ]; then
  mkdir -p "$data/applications"
  sed 's|^Icon=.*|Icon=matos-firefox|' /usr/share/applications/firefox.desktop > "$data/applications/firefox.desktop"
fi
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q -t "$data/icons/hicolor" 2>/dev/null || true
command -v update-desktop-database >/dev/null && update-desktop-database -q "$data/applications" 2>/dev/null || true

echo "Installed into $profile"
echo "Restart Firefox to apply. Ctrl+L or Ctrl+T brings up the address bar under the tabs (hover does nothing)."
