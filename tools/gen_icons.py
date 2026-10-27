#!/usr/bin/env python3
"""MatOS icon theme: soft, filled, accent-coloured icons over Breeze (anything not drawn here comes from Breeze).

Colours are KDE colour-scheme classes (Highlight = the accent, Background = the window colour), so the icons
follow the accent picker and light/dark live, with no watcher. `--preview` bakes fixed colours for test renders.
Everything is drawn on a 64 grid; glyphs on a 24 grid with round caps, centred on the folder's front panel.

Usage: gen_icons.py [OUTDIR]      (default build/icons)
"""
import shutil, sys
from pathlib import Path

STYLE = '<style type="text/css">.ColorScheme-Text{color:#e6e0e9}.ColorScheme-Background{color:#201f25}.ColorScheme-Highlight{color:#b69cff}</style>'
PREVIEW = {"Text": "#e6e0e9", "Background": "#201f25", "Highlight": "#b69cff"}


class Ctx:
    def __init__(self, pv=None):
        self.pv = pv

    def col(self, cls, op=1, stroke=False):
        a = "stroke" if stroke else "fill"
        o = f' {a}-opacity="{op}"' if op != 1 else ""
        if self.pv:
            return f'{a}="{self.pv[cls]}"{o}'
        return f'class="ColorScheme-{cls}" {a}="currentColor"{o}'


TILE = "M6 22a12 12 0 0 1 12-12h28a12 12 0 0 1 12 12v21a11 11 0 0 1-11 11H17A11 11 0 0 1 6 43Z"
POCKET = "M6 38a11 11 0 0 1 11-11h8c3 0 4 4 7 4s4-4 7-4h8a11 11 0 0 1 11 11v5a11 11 0 0 1-11 11H17A11 11 0 0 1 6 43Z"


def sheen(x):
    return (f'<rect x="14" y="{x}" width="10" height="1.8" rx=".9" fill="#fff" fill-opacity=".32"/>'
            f'<rect x="40" y="{x}" width="10" height="1.8" rx=".9" fill="#fff" fill-opacity=".32"/>')


def glyph(x, body, cls="Background", op=.8):
    """body is a 24-grid fragment using the placeholders FILL / LINE for the two ink styles."""
    ink = x.col(cls, op)
    inks = x.col(cls, op, True)
    body = body.replace("FILL", ink).replace("LINE", f'fill="none" {inks} stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"')
    return f'<g transform="translate(20 30)">{body}</g>'


G = {
    "documents": '<path LINE d="M6 7h12M6 12h12M6 17h8"/>',
    "download": '<path LINE d="M12 5v10M7.5 11l4.5 4.5 4.5-4.5M6 19h12"/>',
    "pictures": '<rect LINE x="4" y="5" width="16" height="14" rx="3.5"/><circle FILL cx="9" cy="10" r="1.6"/><path LINE d="M4.5 17l4.5-4.5 4 4 3-3 3.5 3.5"/>',
    "music": '<path LINE d="M9.5 17V6l9-2v11"/><circle FILL cx="7" cy="17" r="2.6"/><circle FILL cx="16" cy="15" r="2.6"/>',
    "videos": '<rect LINE x="3.5" y="6" width="17" height="12" rx="3.5"/><path FILL d="M10 9.4v5.2l4.4-2.6z"/>',
    "templates": '<rect LINE x="5.5" y="4" width="13" height="16" rx="2.8"/><path LINE d="M9 9h6M9 13h6M9 16.5h3.5"/>',
    "share": '<circle FILL cx="6" cy="12" r="2.6"/><circle FILL cx="18" cy="6" r="2.6"/><circle FILL cx="18" cy="18" r="2.6"/><path LINE d="M8 11l8-4M8 13l8 4"/>',
    "recent": '<circle LINE cx="12" cy="12" r="8"/><path LINE d="M12 7.5V12l3 2"/>',
    "network": '<rect LINE x="4" y="5" width="16" height="5.5" rx="2.2"/><rect LINE x="4" y="13.5" width="16" height="5.5" rx="2.2"/><circle FILL cx="8" cy="7.8" r="1.1"/><circle FILL cx="8" cy="16.2" r="1.1"/>',
    "bookmark": '<path LINE d="M7 4.5h10v15l-5-3.6-5 3.6z"/>',
    "important": '<path LINE d="M12 4.5v9.5"/><circle FILL cx="12" cy="18.6" r="1.5"/>',
    "locked": '<rect LINE x="6" y="11" width="12" height="9" rx="2.8"/><path LINE d="M8.5 11V8a3.5 3.5 0 0 1 7 0v3"/>',
    "unlocked": '<rect LINE x="6" y="11" width="12" height="9" rx="2.8"/><path LINE d="M8.5 11V8a3.5 3.5 0 0 1 6.8-1.2"/>',
    "git": '<circle LINE cx="7" cy="6" r="2.3"/><circle LINE cx="7" cy="18" r="2.3"/><circle LINE cx="17" cy="10" r="2.3"/><path LINE d="M7 8.3v7.4M17 12.3c0 3.4-3 4-7.6 4.6"/>',
    "code": '<path LINE d="M9 7l-5 5 5 5M15 7l5 5-5 5"/>',
    "script": '<path LINE d="M5 7l5 5-5 5M12 17h7"/>',
    "cloud": '<path LINE d="M7 18a4 4 0 0 1-.6-7.9 5.6 5.6 0 0 1 10.7 1.3A3.3 3.3 0 0 1 17 18z"/>',
    "games": '<rect LINE x="3" y="7.5" width="18" height="9.5" rx="4.7"/><path LINE d="M8 10.3v4M6 12.3h4"/><circle FILL cx="15.3" cy="11.3" r="1.1"/><circle FILL cx="17.7" cy="13.3" r="1.1"/>',
    "root": '<path LINE d="M9 5v14M15 5v14M5 9h14M5 15h14"/>',
    "temp": '<path LINE d="M5 8h5M14 8h5M5 12h5M14 12h5M5 16h5M14 16h5"/>',
    "desktop": '<rect LINE x="3" y="5" width="18" height="11" rx="3"/><path LINE d="M9 20h6M12 16v4"/>',
    "table": '<rect LINE x="4" y="5" width="16" height="14" rx="3"/><path LINE d="M4 10h16M4 14.5h16M10 10v9"/>',
    "chart": '<rect FILL x="5" y="12" width="3.6" height="7" rx="1.4"/><rect FILL x="10.2" y="6" width="3.6" height="13" rx="1.4"/><rect FILL x="15.4" y="9.5" width="3.6" height="9.5" rx="1.4"/>',
    "database": '<ellipse LINE cx="12" cy="6.5" rx="7" ry="2.8"/><path LINE d="M5 6.5v11c0 1.6 3.1 2.8 7 2.8s7-1.2 7-2.8v-11M5 12c0 1.6 3.1 2.8 7 2.8s7-1.2 7-2.8"/>',
    "trash": '<path LINE d="M5.5 7h13M10 7V5h4v2M7.5 7l.8 12h7.4l.8-12"/>',
}


def folder_svg(kind="plain", state="closed", pv=None):
    """Pocket tile: a squircle card with a pocket across its lower half. Closed = hollow slot, open = cards in it."""
    x = Ctx(pv)
    parts = [f'<path d="{TILE}" {x.col("Highlight", .5)}/>']
    if state == "open":
        parts += [f'<rect x="11" y="6" width="23" height="26" rx="5.5" transform="rotate(-7 22 19)" {x.col("Text", .9)}/>',
                  f'<rect x="29" y="4" width="23" height="28" rx="5.5" transform="rotate(6 40 18)" {x.col("Text", .6)}/>']
    else:
        parts.append(f'<rect x="12" y="15" width="40" height="15" rx="6" {x.col("Background", .4)}/>')
    parts += [f'<path d="{POCKET}" {x.col("Highlight")}/>', sheen(28.2)]
    if kind != "plain":
        parts.append(f'<g transform="translate(0 0)">{glyph(x, G[kind])}</g>')
    return wrap(parts, pv)


def wrap(parts, pv):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            + ("" if pv else STYLE) + "".join(parts) + "</svg>\n")


def standalone_svg(kind, pv=None):
    x = Ctx(pv)
    H, Bg = x.col("Highlight"), x.col("Background", .8)
    if kind == "home":
        hs = x.col("Highlight", 1, True)
        parts = [f'<path d="M32 12 54 31H48V51H16V31H10Z" {H} {hs} stroke-width="6" stroke-linejoin="round"/>',
                 f'<rect x="27" y="36" width="10" height="15" rx="3.5" {Bg}/>',
                 '<path d="M20 29.5 32 19l12 10.5" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>']
    elif kind == "desktop":
        parts = [f'<rect x="6" y="10" width="52" height="35" rx="8" {H}/>', f'<rect x="10" y="14" width="44" height="27" rx="5" {Bg}/>',
                 f'<rect x="26" y="45" width="12" height="6" rx="2" {x.col("Highlight", .6)}/>', f'<rect x="17" y="50" width="30" height="5" rx="2.5" {H}/>',
                 sheen(11)]
    else:  # trash, trash-full
        hs = x.col("Highlight", 1, True)
        parts = []
        if kind == "trash-full":
            parts += [f'<rect x="18" y="3" width="17" height="14" rx="3" transform="rotate(-12 26 10)" {x.col("Text", .55)}/>',
                      f'<rect x="31" y="5" width="16" height="13" rx="3" transform="rotate(10 39 11)" {x.col("Text", .4)}/>']
        parts += [f'<rect x="24" y="8" width="16" height="9" rx="3.5" {x.col("Highlight", .6)}/>',
                  f'<rect x="9" y="14" width="46" height="7" rx="3.5" {H}/>',
                  f'<path d="M17 24h30l-2.6 28a5 5 0 0 1-5 4.5H24.6a5 5 0 0 1-5-4.5Z" {H} {hs} stroke-width="2" stroke-linejoin="round"/>',
                  f'<rect x="26" y="29" width="3.2" height="21" rx="1.6" {Bg}/><rect x="34.8" y="29" width="3.2" height="21" rx="1.6" {Bg}/>']
    return wrap(parts, pv)


FOLDERS = {
    "folder": ("plain", "closed"), "inode-directory": ("plain", "closed"), "folder-open": ("plain", "open"),
    "folder-documents": ("documents", "closed"), "folder-text": ("documents", "closed"), "folder-txt": ("documents", "closed"),
    "folder-notes": ("documents", "closed"),
    "folder-download": ("download", "closed"), "folder-downloads": ("download", "closed"),
    "folder-pictures": ("pictures", "closed"), "folder-picture": ("pictures", "closed"),
    "folder-images": ("pictures", "closed"), "folder-image": ("pictures", "closed"),
    "folder-music": ("music", "closed"), "folder-sound": ("music", "closed"),
    "folder-video": ("videos", "closed"), "folder-videos": ("videos", "closed"),
    "folder-templates": ("templates", "closed"),
    "folder-public": ("share", "closed"), "folder-publicshare": ("share", "closed"),
    "folder-recent": ("recent", "closed"),
    "folder-network": ("network", "closed"), "folder-remote": ("network", "closed"),
    "folder-bookmark": ("bookmark", "closed"), "folder-favorites": ("bookmark", "closed"),
    "folder-important": ("important", "closed"),
    "folder-locked": ("locked", "closed"), "folder-encrypted": ("locked", "closed"),
    "folder-unlocked": ("unlocked", "closed"), "folder-decrypted": ("unlocked", "closed"),
    "folder-git": ("git", "closed"), "folder-development": ("code", "closed"), "folder-script": ("script", "closed"),
    "folder-cloud": ("cloud", "closed"), "folder-games": ("games", "closed"),
    "folder-root": ("root", "closed"), "folder-temp": ("temp", "closed"),
    "folder-desktop": ("desktop", "closed"), "folder-table": ("table", "closed"),
    "folder-chart": ("chart", "closed"), "folder-database": ("database", "closed"),
    "folder-trash": ("trash", "closed"),
}
STANDALONE = {"user-home": "home", "user-desktop": "desktop", "desktop": "desktop",
              "user-trash": "trash", "user-trash-full": "trash-full"}

INDEX = """[Icon Theme]
Name=MatOS Icons
Comment=Soft, accent-coloured icons for MatOS. Anything not drawn here comes from Breeze.
Inherits=breeze-dark,breeze,hicolor
Directories=places,mimetypes,apps
DesktopSizes=16,22,32,48,64,128,256
PanelSizes=16,22,32,48,64,128,256

[places]
Size=64
MinSize=8
MaxSize=512
Type=Scalable
Context=Places

[apps]
Size=64
MinSize=8
MaxSize=512
Type=Scalable
Context=Applications

[mimetypes]
Size=64
MinSize=8
MaxSize=512
Type=Scalable
Context=MimeTypes
"""


def build(out, pv=None):
    for d in ("places", "mimetypes", "apps"):
        (out / d).mkdir(parents=True, exist_ok=True)
    (out / "index.theme").write_text(INDEX)
    for icon, (kind, state) in FOLDERS.items():
        (out / ("mimetypes" if icon == "inode-directory" else "places") / f"{icon}.svg").write_text(folder_svg(kind, state, pv))
    for icon, kind in STANDALONE.items():
        (out / "places" / f"{icon}.svg").write_text(standalone_svg(kind, pv))
    import icon_sets
    return len(FOLDERS) + len(STANDALONE) + icon_sets.build(out, pv)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = Path(args[0] if args else Path(__file__).resolve().parent.parent / "build" / "icons" / "MatOS-Icons")
    if out.exists():
        shutil.rmtree(out)
    print(f"wrote {build(out, PREVIEW if '--preview' in sys.argv else None)} icons to {out}")
