#!/usr/bin/env bash
# Measure the window shadow on a flat white backdrop (also keeps personal windows out of the capture).
# Opens a white fullscreen-ish Qt window on the ultrawide, a test Dolphin on top, screenshots, prints
# mean luminance in bands at distances 0-2,2-6,6-12,12-24,24-40,40-64 px outside each edge (255 = no shadow).
S=${1:?scratch dir}
cat > "$S/white.py" <<'PY'
import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
app = QApplication(sys.argv)
w = QWidget(); w.setWindowTitle("shadowbackdrop"); w.setStyleSheet("background:#ffffff"); w.setWindowFlag(Qt.WindowType.FramelessWindowHint)
w.setGeometry(1440, 446, 3440, 1440); w.show(); app.exec()
PY
python3 "$S/white.py" >/dev/null 2>&1 & W=$!
sleep 2
dolphin --new-window "$HOME/Projects/matos/docs" >/dev/null 2>&1 & sleep 4
cat > "$S/place.js" <<'JS'
// only OUR test window (its folder is "docs"): never touch the user's own windows
// Wayland ignores a client's requested position, so place the white backdrop through KWin
for (const w of workspace.windowList()) if (w.caption == "shadowbackdrop") w.frameGeometry = {x: 1440, y: 446, width: 3440, height: 1440};
for (const w of workspace.windowList()) if (w.resourceClass == "org.kde.dolphin" && w.caption.indexOf("docs") == 0) { workspace.activeWindow = w; w.frameGeometry = {x: 2300, y: 700, width: 1000, height: 700}; }
JS
id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$S/place.js" place$$); qdbus6 org.kde.KWin /Scripting/Script$id org.kde.kwin.Script.run; sleep 2
spectacle -b -n -f -o "$S/full.png" 2>/dev/null
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript place$$ >/dev/null
cat > "$S/close.js" <<'JS'
for (const w of workspace.windowList()) if ((w.resourceClass == "org.kde.dolphin" && w.caption.indexOf("docs") == 0) || w.caption == "shadowbackdrop") w.closeWindow();
JS
id=$(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript "$S/close.js" close$$); qdbus6 org.kde.KWin /Scripting/Script$id org.kde.kwin.Script.run; sleep 1
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript close$$ >/dev/null
kill $W 2>/dev/null
python3 - "$S/full.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB"); x0, y0, w, h = 2300, 700, 1000, 700
print("top :", [im.getpixel((x0+400, y))[0] for y in range(y0-2, y0+5)])
print("side:", [im.getpixel((x, y0+300))[0] for x in range(x0-2, x0+5)])
print("bot :", [im.getpixel((x0+400, y))[0] for y in range(y0+h-4, y0+h+2)])
PY
