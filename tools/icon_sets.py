"""MatOS icon families beyond folders: settings + app tiles (accent squircle, rounded glyph) and file-type pages.
Glyphs are 24-grid fragments (FILL / LINE placeholders, see gen_icons.glyph) shared by all three families."""
from gen_icons import Ctx, G, glyph, wrap

L = "LINE"
N = {  # extra glyphs; the folder glyphs in gen_icons.G are reused too
    "sliders": f'<path {L} d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1"/><circle {L} cx="15" cy="7" r="2"/><circle {L} cx="9" cy="12" r="2"/><circle {L} cx="17" cy="17" r="2"/>',
    "mouse": f'<rect {L} x="6.5" y="3.5" width="11" height="17" rx="5.5"/><path {L} d="M12 3.5v6"/>',
    "touchpad": f'<rect {L} x="3.5" y="5.5" width="17" height="13" rx="3.5"/><path {L} d="M3.5 14h17"/>',
    "keyboard": f'<rect {L} x="2.5" y="6.5" width="19" height="11" rx="3"/><path {L} d="M6.5 10.5h.01M10 10.5h.01M14 10.5h.01M17.5 10.5h.01M7.5 14h9"/>',
    "sound": '<path FILL d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path LINE d="M15.5 9.5a4 4 0 0 1 0 5M18 7a7.5 7.5 0 0 1 0 10"/>',
    "display": G["desktop"],
    "accessibility": '<circle FILL cx="12" cy="5.5" r="1.9"/><path LINE d="M5 9.5l7 1.5 7-1.5M12 11v4M12 15l-3 5M12 15l3 5"/>',
    "bluetooth": '<path LINE d="M7 8l10 8-5 4V4l5 4-10 8"/>',
    "drive": '<rect LINE x="3" y="8" width="18" height="9" rx="3"/><path LINE d="M7 12.5h6"/><circle FILL cx="17" cy="12.5" r="1.1"/>',
    "usb": '<circle FILL cx="12" cy="19" r="2"/><path LINE d="M12 17V5M12 5l-2.5 3M12 5l2.5 3M12 12l-4-2.5v-2M12 14l4-2.5V10"/><circle FILL cx="8" cy="6" r="1.4"/><rect FILL x="14.8" y="7.6" width="2.6" height="2.6" rx=".7"/>',
    "wifi": '<path LINE d="M3.5 9.5a12 12 0 0 1 17 0M6.5 12.8a7.7 7.7 0 0 1 11 0M9.4 16a3.5 3.5 0 0 1 5.2 0"/><circle FILL cx="12" cy="19" r="1.4"/>',
    "user": '<circle LINE cx="12" cy="8" r="3.6"/><path LINE d="M5 20a7 7 0 0 1 14 0"/>',
    "users": '<circle LINE cx="9" cy="8.5" r="3.2"/><path LINE d="M3 19.5a6 6 0 0 1 12 0M15.5 5.5a3.2 3.2 0 0 1 0 6M17.5 14.5a6 6 0 0 1 3.5 5"/>',
    "palette": '<path LINE d="M12 3.5a8.5 8.5 0 1 0 0 17c1.5 0 2-1 1.5-2.2-.6-1.4.3-2.3 1.7-2.3H17a3.5 3.5 0 0 0 3.5-3.5C20.5 7 16.8 3.5 12 3.5z"/><circle FILL cx="7.5" cy="11" r="1.2"/><circle FILL cx="10" cy="7.5" r="1.2"/><circle FILL cx="14.5" cy="7.5" r="1.2"/>',
    "font": '<path LINE d="M5 19L12 5l7 14M7.8 14h8.4"/>',
    "sparkle": '<path FILL d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path FILL d="M18.5 15l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
    "check": '<circle LINE cx="12" cy="12" r="8.5"/><path LINE d="M8 12.3l2.8 2.8L16.2 9.5"/>',
    "bell": '<path LINE d="M6 17v-6a6 6 0 0 1 12 0v6l1.5 1.5h-15zM10 21h4"/>',
    "windows": '<rect LINE x="3.5" y="4.5" width="12" height="9" rx="2.5"/><rect LINE x="8.5" y="10.5" width="12" height="9" rx="2.5"/>',
    "grid": '<rect FILL x="4" y="4" width="6.5" height="6.5" rx="2"/><rect FILL x="13.5" y="4" width="6.5" height="6.5" rx="2"/><rect FILL x="4" y="13.5" width="6.5" height="6.5" rx="2"/><rect FILL x="13.5" y="13.5" width="6.5" height="6.5" rx="2"/>',
    "search": '<circle LINE cx="10.5" cy="10.5" r="6"/><path LINE d="M15 15l5 5"/>',
    "key": '<circle LINE cx="8" cy="12" r="3.5"/><path LINE d="M11.5 12H21M17 12v3.5M20 12v2.5"/>',
    "keycap": '<rect LINE x="4" y="4" width="16" height="16" rx="4.5"/><path LINE d="M9 14.5l3-3.5 3 3.5"/>',
    "battery": '<rect LINE x="3" y="7.5" width="16" height="9" rx="3"/><path LINE d="M21.5 11v2"/><rect FILL x="5.5" y="10" width="7" height="4" rx="1.2"/>',
    "power": '<path LINE d="M12 3.5v8M7 6.5a7.5 7.5 0 1 0 10 0"/>',
    "globe": '<circle LINE cx="12" cy="12" r="8.5"/><path LINE d="M3.5 12h17M12 3.5c3 3 3 14 0 17M12 3.5c-3 3-3 14 0 17"/>',
    "ethernet": '<rect LINE x="8" y="3.5" width="8" height="6" rx="1.8"/><rect LINE x="3" y="15.5" width="7" height="5" rx="1.6"/><rect LINE x="14" y="15.5" width="7" height="5" rx="1.6"/><path LINE d="M12 9.5v3M6.5 15.5v-3h11v3"/>',
    "proxy": '<circle LINE cx="5.5" cy="12" r="2.5"/><circle LINE cx="18.5" cy="12" r="2.5"/><rect LINE x="9.5" y="9" width="5" height="6" rx="1.6"/>',
    "shield": '<path LINE d="M12 3.5l7 2.8v5.4c0 4.2-2.8 7.2-7 8.8-4.2-1.6-7-4.6-7-8.8V6.3z"/>',
    "shield-check": '<path LINE d="M12 3.5l7 2.8v5.4c0 4.2-2.8 7.2-7 8.8-4.2-1.6-7-4.6-7-8.8V6.3z"/><path LINE d="M9 12l2.2 2.2L15.2 10"/>',
    "firewall": '<path LINE d="M12 3.5l7 2.8v5.4c0 4.2-2.8 7.2-7 8.8-4.2-1.6-7-4.6-7-8.8V6.3z"/><path LINE d="M8.5 10h7M8.5 13.5h7"/>',
    "moon": '<path LINE d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"/>',
    "gear": '<circle LINE cx="12" cy="12" r="5.5"/><circle FILL cx="12" cy="12" r="1.6"/><path LINE d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M18.4 5.6l-1.8 1.8M7.4 16.6l-1.8 1.8"/>',
    "sun": '<circle FILL cx="12" cy="12" r="4"/><path LINE d="M12 3.5v2M12 18.5v2M3.5 12h2M18.5 12h2M6 6l1.4 1.4M16.6 16.6L18 18M18 6l-1.4 1.4M7.4 16.6L6 18"/>',
    "login": '<path LINE d="M10 4.5H7a3 3 0 0 0-3 3v9a3 3 0 0 0 3 3h3M9 12h11M16.5 8.5L20 12l-3.5 3.5"/>',
    "rocket": '<path LINE d="M12 3c3 2 4.5 5 4.5 8.5L14 17h-4l-2.5-5.5C7.5 8 9 5 12 3z"/><circle FILL cx="12" cy="9.5" r="1.4"/><path LINE d="M7.5 14L5 17.5l3-.5M16.5 14l2.5 3.5-3-.5M10.5 20h3"/>',
    "layers": '<path LINE d="M12 4l8.5 4.5L12 13 3.5 8.5z"/><path LINE d="M3.5 12.5L12 17l8.5-4.5"/>',
    "pointer": '<path LINE d="M6 3.5l12 7-5.2 1.6 3.2 5.4-2.2 1.3-3.2-5.4L7.6 17z"/>',
    "shapes": '<circle LINE cx="8" cy="8" r="3.5"/><rect LINE x="13" y="13" width="7" height="7" rx="2"/><path LINE d="M7 20l3-6 3 6z"/>',
    "plasma": '<circle LINE cx="12" cy="12" r="8.5"/><circle FILL cx="12" cy="12" r="3"/>',
    "tablet": '<rect LINE x="4" y="3.5" width="16" height="17" rx="3.5"/><path LINE d="M10 17.5h4"/>',
    "phone": '<rect LINE x="7" y="3" width="10" height="18" rx="3"/><path LINE d="M10.5 18h3"/>',
    "touch": '<path LINE d="M9 11V6a1.8 1.8 0 0 1 3.6 0v4.5l3.2.8a2.4 2.4 0 0 1 1.7 2.7l-.5 3.3a3 3 0 0 1-3 2.7H11a3 3 0 0 1-2.4-1.2L5.5 14a1.7 1.7 0 0 1 2.7-1.8L9 13"/>',
    "bolt": '<path FILL d="M13 3L5.5 13.5h5L9.5 21l8-11h-5.2z"/>',
    "cube": '<path LINE d="M12 3.5l8 4.2v8.6l-8 4.2-8-4.2V7.7zM4 7.7l8 4.3 8-4.3M12 12v8.5"/>',
    "gamepad": G["games"],
    "play": '<circle LINE cx="12" cy="12" r="8.5"/><path FILL d="M10.2 8.6v6.8l5.6-3.4z"/>',
    "file": '<path LINE d="M7 3.5h6.5L19 9v9.5a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2zM13 3.5V9h6"/>',
    "plug": '<path LINE d="M9 3.5v5M15 3.5v5M6.5 8.5h11v3.5a5.5 5.5 0 0 1-11 0zM12 17.5v3"/>',
    "chat": '<path LINE d="M5 4.5h14a2.5 2.5 0 0 1 2.5 2.5v7a2.5 2.5 0 0 1-2.5 2.5h-6.5L8 20v-3.5H5A2.5 2.5 0 0 1 2.5 14V7A2.5 2.5 0 0 1 5 4.5z"/>',
    "dots": '<circle FILL cx="6" cy="6" r="1.7"/><circle FILL cx="12" cy="6" r="1.7"/><circle FILL cx="18" cy="6" r="1.7"/><circle FILL cx="6" cy="12" r="1.7"/><circle FILL cx="12" cy="12" r="1.7"/><circle FILL cx="18" cy="12" r="1.7"/><circle FILL cx="6" cy="18" r="1.7"/><circle FILL cx="12" cy="18" r="1.7"/><circle FILL cx="18" cy="18" r="1.7"/>',
    "info": '<circle LINE cx="12" cy="12" r="8.5"/><path LINE d="M12 11v5.5"/><circle FILL cx="12" cy="7.9" r="1.2"/>',
    "bulb": '<path LINE d="M9 17.5h6M10 20.5h4M12 3.5a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3.5z"/>',
    "terminal": '<rect LINE x="3" y="4.5" width="18" height="15" rx="3.5"/><path LINE d="M7.5 9.5l3 2.5-3 2.5M13 15h3.5"/>',
    "pen": '<path LINE d="M4 20l1-4.5L16.5 4a2 2 0 0 1 3 3L8 18.5zM14.5 6l3.5 3.5"/>',
    "camera": '<rect LINE x="3" y="6.5" width="18" height="13" rx="3.5"/><circle LINE cx="12" cy="13" r="3.5"/><path LINE d="M8.5 6.5L9.5 4h5l1 2.5"/>',
    "archive": '<rect LINE x="3.5" y="4.5" width="17" height="5" rx="2"/><path LINE d="M5 9.5v8a2.5 2.5 0 0 0 2.5 2.5h9a2.5 2.5 0 0 0 2.5-2.5v-8M10 13.5h4"/>',
    "bag": '<path LINE d="M5 8h14l-1 11a2 2 0 0 1-2 1.8H8A2 2 0 0 1 6 19zM9 8V7a3 3 0 0 1 6 0v1"/>',
    "calc": '<rect LINE x="5" y="3.5" width="14" height="17" rx="3.5"/><path LINE d="M8.5 8.5h7M9 13h.01M12 13h.01M15 13h.01M9 16.5h.01M12 16.5h.01M15 16.5h.01"/>',
    "pulse": '<path LINE d="M3 12h4l2.5-6 4 12 2.5-6H21"/>',
    "smile": '<circle LINE cx="12" cy="12" r="8.5"/><path LINE d="M8.5 14a4 4 0 0 0 7 0"/><circle FILL cx="9" cy="10" r="1.1"/><circle FILL cx="15" cy="10" r="1.1"/>',
    "x": '<path LINE d="M6 6l12 12M18 6L6 18"/>',
    "spell": '<path LINE d="M3.5 17L8 6l4.5 11M5 13.5h6M14.5 14.5l2.5 2.5 4-5"/>',
    "disc": '<circle LINE cx="12" cy="12" r="8.5"/><circle LINE cx="12" cy="12" r="2.2"/>',
    "mail": '<rect LINE x="3.5" y="5.5" width="17" height="13" rx="3.5"/><path LINE d="M4.5 8l7.5 5.5L19.5 8"/>',
    "filemanager": '<path LINE d="M4 8a2.5 2.5 0 0 1 2.5-2.5H10l2 2.5h5.5A2.5 2.5 0 0 1 20 10.5v6A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5z"/>',
    "question": '<path LINE d="M9.2 9a3 3 0 1 1 4.4 2.6c-1 .6-1.6 1.2-1.6 2.4M12 17.8h.01"/>',
    "clock": G["recent"], "image": G["pictures"], "docs": G["documents"], "music": G["music"], "video": G["videos"],
    "code": G["code"], "script": G["script"], "table": G["table"], "chart": G["chart"], "database": G["database"],
    "locked": G["locked"], "download": G["download"], "cloud": G["cloud"], "trash": G["trash"],
}
GL = {**G, **N}

# icon name -> glyph. Symbolic (monochrome panel) icons are left to Breeze.
SETTINGS = {}
for g, names in {
    "sliders": "preferences-desktop-settings preferences-system systemsettings preferences-desktop org.kde.systemsettings preferences-desktop-default-applications",
    "mouse": "preferences-desktop-mouse input-mouse", "touchpad": "preferences-desktop-touchpad",
    "keyboard": "preferences-desktop-keyboard input-keyboard input-keyboard-virtual",
    "sound": "preferences-desktop-sound audio-volume-high preferences-desktop-multimedia-sound multimedia-volume-control",
    "display": "preferences-desktop-display preferences-desktop-display-randr",
    "accessibility": "preferences-desktop-accessibility", "bluetooth": "preferences-bluetooth preferences-system-bluetooth",
    "drive": "drive-harddisk preferences-system-disks", "usb": "drive-removable-media preferences-system-removable-media",
    "wifi": "network-wireless network-wireless-hotspot", "ethernet": "preferences-system-network network-wired",
    "globe": "preferences-system-network-connection internet-web-browser web-browser preferences-desktop-locale preferences-desktop-language preferences-web-browser-shortcuts",
    "proxy": "preferences-system-network-proxy", "user": "preferences-desktop-user preferences-system-user",
    "users": "preferences-system-users", "key": "preferences-desktop-user-password",
    "image": "preferences-desktop-wallpaper", "palette": "preferences-desktop-color preferences-desktop-theme preferences-desktop-plasma-theme",
    "font": "preferences-desktop-font preferences-desktop-font-installer", "sparkle": "preferences-desktop-effects preferences-desktop-animations",
    "bell": "preferences-desktop-notification preferences-desktop-notification-bell",
    "windows": "preferences-system-windows preferences-desktop-theme-windowdecorations preferences-system-windows-behavior preferences-system-windows-actions",
    "grid": "applications-all preferences-desktop-theme-applications org.kde.kmenuedit preferences-system-tabbox",
    "search": "preferences-system-search preferences-desktop-search plasma-search krunner preferences-desktop-baloo",
    "locked": "preferences-security preferences-system-login-lock", "shield-check": "preferences-security-privacy",
    "firewall": "preferences-security-firewall", "keycap": "preferences-desktop-keyboard-shortcut",
    "battery": "battery", "power": "preferences-system-power-management system-shutdown",
    "clock": "preferences-system-time preferences-desktop-clock", "moon": "preferences-system-night-light preferences-desktop-screensaver",
    "sun": "redshift-status-on", "gear": "preferences-system-services preferences-system-session-services",
    "login": "preferences-system-login system-log-out", "rocket": "preferences-desktop-splash preferences-system-splash preferences-system-splash-display",
    "layers": "preferences-desktop-theme-global preferences-desktop-virtual preferences-desktop-activities",
    "pointer": "preferences-desktop-cursors", "shapes": "preferences-desktop-icons", "plasma": "preferences-desktop-plasma",
    "tablet": "preferences-desktop-tablet", "phone": "smartphone", "touch": "preferences-desktop-touchscreen",
    "bolt": "preferences-desktop-thunderbolt", "cube": "preferences-desktop-virtual-machine", "gamepad": "preferences-desktop-gaming input-gaming",
    "play": "preferences-desktop-multimedia", "file": "preferences-desktop-filetype-association", "plug": "preferences-desktop-peripherals",
    "chat": "preferences-desktop-feedback", "cloud": "preferences-online-accounts", "dots": "preferences-other",
    "info": "help-about help-contents", "bulb": "ktip", "terminal": "system-run", "filemanager": "system-file-manager",
    "spell": "tools-check-spelling", "x": "xorg", "image-light": "lighttable",
    "pen": "preferences-desktop-text-to-speech",
}.items():
    for n in names.split():
        SETTINGS[n] = "image" if g == "image-light" else g

APPS = {}
for g, names in {
    "filemanager": "org.kde.dolphin dolphin", "terminal": "org.kde.konsole konsole utilities-terminal",
    "pen": "org.kde.kate kate org.kde.kwrite kwrite accessories-text-editor", "camera": "org.kde.spectacle spectacle accessories-screenshot",
    "archive": "org.kde.ark ark utilities-file-archiver", "docs": "org.kde.okular okular", "image": "org.kde.gwenview gwenview",
    "bag": "org.kde.discover plasmadiscover system-software-install", "calc": "org.kde.kcalc kcalc accessories-calculator",
    "pulse": "org.kde.plasma-systemmonitor ksysguard utilities-system-monitor", "info": "org.kde.kinfocenter kinfocenter",
    "smile": "org.kde.plasma.emojier accessories-character-map", "drive": "org.kde.partitionmanager partitionmanager",
    "phone": "org.kde.kdeconnect kdeconnect", "clock": "org.kde.kclock", "music": "org.kde.elisa elisa", "play": "org.kde.haruna",
    "disc": "org.kde.filelight filelight", "mail": "internet-mail",
}.items():
    for n in names.split():
        APPS[n] = g

MIME = {}
for g, names in {
    "docs": "text-plain text-x-generic text-x-readme text-x-log text-markdown text-x-markdown text-rtf application-rtf application-pdf application-msword "
            "application-vnd.oasis.opendocument.text application-vnd.openxmlformats-officedocument.wordprocessingml.document application-epub+zip",
    "table": "text-csv application-vnd.ms-excel application-vnd.oasis.opendocument.spreadsheet application-vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "chart": "application-vnd.ms-powerpoint application-vnd.oasis.opendocument.presentation application-vnd.openxmlformats-officedocument.presentationml.presentation",
    "image": "image-x-generic image-png image-jpeg image-gif image-webp image-svg+xml image-bmp image-tiff image-x-xcf image-vnd.adobe.photoshop image-avif image-heif image-x-icon",
    "music": "audio-x-generic audio-mpeg audio-flac audio-ogg audio-x-wav audio-x-flac audio-mp4 audio-x-vorbis+ogg audio-x-mp3 audio-aac",
    "video": "video-x-generic video-mp4 video-x-matroska video-webm video-quicktime video-x-msvideo video-mpeg video-ogg",
    "archive": "application-zip application-x-tar application-gzip application-x-7z-compressed application-vnd.rar application-x-rar application-x-compressed-tar "
               "application-x-xz application-zstd application-x-archive application-x-bzip application-x-bzip2 application-x-cpio application-x-lzma",
    "code": "text-x-python text-x-csrc text-x-chdr text-x-c++src text-x-c++hdr text-x-java text-javascript application-javascript text-x-javascript text-x-rust text-x-go "
            "text-css text-html application-xml text-xml application-json text-x-makefile application-x-php text-x-cmake application-x-yaml text-x-typescript text-x-qml",
    "script": "application-x-shellscript text-x-shellscript text-x-script text-x-perl text-x-lua",
    "bolt": "application-x-executable application-x-sharedlib application-vnd.appimage application-x-appimage application-x-ms-dos-executable application-x-msi application-x-pie-executable",
    "disc": "application-x-cd-image application-x-iso9660-image application-x-raw-disk-image application-x-cdimage",
    "font": "font-x-generic font-ttf font-otf font-woff font-woff2 application-x-font-ttf application-x-font-otf",
    "database": "application-vnd.sqlite3 application-x-sqlite3",
    "key": "application-pkix-cert application-x-x509-ca-cert application-pgp-keys application-pgp-signature",
    "question": "unknown application-octet-stream application-x-generic",
    "grid": "application-x-desktop", "download": "application-x-bittorrent", "cube": "model-stl model-gltf+json",
}.items():
    for n in names.split():
        MIME[n] = g

PAGE = "M22 5h16l13 13v32a9 9 0 0 1-9 9H22a9 9 0 0 1-9-9V14a9 9 0 0 1 9-9z"
FOLD = "M38 5v9a4 4 0 0 0 4 4h9z"


def tile_svg(kind, pv=None):
    """Settings / app icon: accent squircle with the glyph cut out in the window colour."""
    x = Ctx(pv)
    return wrap([f'<rect x="5" y="5" width="54" height="54" rx="17" {x.col("Highlight")}/>',
                 '<rect x="16" y="6.6" width="32" height="2" rx="1" fill="#fff" fill-opacity=".3"/>',
                 f'<g transform="translate(14 14) scale(1.5)">{glyph(x, GL[kind]).replace("translate(20 30)", "translate(0 0)")}</g>'], pv)


def page_svg(kind, pv=None):
    """File-type icon: a soft page with a folded corner and the glyph in the accent."""
    x = Ctx(pv)
    return wrap([f'<path d="{PAGE}" {x.col("Highlight", .38)}/>', f'<path d="{FOLD}" {x.col("Highlight", .85)}/>',
                 glyph(x, GL[kind], "Highlight", 1).replace("translate(20 30)", "translate(20 27)")], pv)


def build(out, pv=None):
    n = 0
    for table, folder, fn in ((SETTINGS, "apps", tile_svg), (APPS, "apps", tile_svg), (MIME, "mimetypes", page_svg)):
        for name, kind in table.items():
            (out / folder / f"{name}.svg").write_text(fn(kind, pv))
            n += 1
    return n
