#!/usr/bin/env python3
"""Manage the MatOS prefs block in a profile's user.js.

  prefs.py install <profile/user.js> <our user.js>   add or refresh the managed block
  prefs.py remove  <profile/user.js>                 remove the managed block

The block is replaced on every install. A pref the user set themselves (outside the block) is never
overridden. Lines written by earlier versions of this installer (no block) are migrated.
"""
import re
import sys
from pathlib import Path

BEGIN = "// >>> MatOS (managed by install.sh; rerunning it replaces this block)"
END = "// <<< MatOS"
# written verbatim by earlier versions of install.sh, outside any block
LEGACY = {
    'user_pref("browser.startup.homepage", "about:blank");',
    'user_pref("browser.newtabpage.enabled", false);',
    'user_pref("browser.netError.illustration.enabled", false);',
}


def key_of(line):
    m = re.match(r'\s*user_pref\("([^"]+)"', line)
    return m.group(1) if m else None


OLD_BEGIN = "// >>> Obscura (managed by install.sh; rerunning it replaces this block)"
OLD_END = "// <<< Obscura"


def strip_block(lines):
    out, inside = [], False
    for line in lines:
        if line.strip() in (BEGIN, OLD_BEGIN):
            inside = True
        elif line.strip() in (END, OLD_END):
            inside = False
        elif not inside:
            out.append(line)
    return out


def main():
    cmd, target = sys.argv[1], Path(sys.argv[2])
    lines = target.read_text().splitlines() if target.exists() else []
    lines = [l for l in strip_block(lines) if l.strip() not in LEGACY]
    if cmd == "install":
        ours = [l for l in Path(sys.argv[3]).read_text().splitlines() if l.startswith("user_pref(")]
        taken = {key_of(l) for l in lines if key_of(l)}
        block = []
        for l in ours:
            if key_of(l) in taken:
                if l not in lines:
                    print(f"Note: your user.js already sets {key_of(l)} differently; left as is.", file=sys.stderr)
            else:
                block.append(l)
        if block:
            lines += ["", BEGIN, *block, END]
    target.write_text("\n".join(lines).rstrip() + "\n")


main()
