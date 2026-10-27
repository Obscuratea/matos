#!/usr/bin/env bash
# Removes the MatOS skin and restores the CSS files it backed up (e.g. the Obscura skin). Usage: ./uninstall.sh [profile-dir]
set -euo pipefail
here="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
source "$here/find-profile.sh"
profile="${1:-$(find_profile)}"
[ -d "$profile" ] || { echo "No Firefox profile found." >&2; exit 1; }
for f in userChrome.css userContent.css; do
  dest="$profile/chrome/$f"
  bak="$(ls -1t "$dest".bak-* 2>/dev/null | head -1 || true)"
  if [ -n "$bak" ]; then mv "$bak" "$dest"; echo "restored $f from $(basename "$bak")"
  else rm -f "$dest"; echo "removed $f"; fi
done
rm -f "$profile"/chrome/matos-mark-*.svg
python3 "$here/prefs.py" remove "$profile/user.js"
echo "Restart Firefox."
