#!/usr/bin/env python3
"""Widget gallery that grabs itself (and an open menu) to PNGs, for checking a Qt style
without a screenshot tool. Run through tools/preview.sh so it uses a scratch config.
Usage: preview_app.py out.png
"""
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

app = QApplication(sys.argv)
w = QWidget(); w.setWindowTitle("MatOS preview")
root = QVBoxLayout(w)

tb = QToolBar(); tb.addAction("File"); tb.addAction("Edit"); tb.addSeparator()
a = tb.addAction("Toggled"); a.setCheckable(True); a.setChecked(True)
root.addWidget(tb)

row = QHBoxLayout(); root.addLayout(row)
col1, col2 = QVBoxLayout(), QVBoxLayout(); row.addLayout(col1, 1); row.addLayout(col2, 1)

col1.addWidget(QPushButton("Button"))
d = QPushButton("Default"); d.setDefault(True); col1.addWidget(d)
t = QPushButton("Checked"); t.setCheckable(True); t.setChecked(True); col1.addWidget(t)
x = QPushButton("Disabled"); x.setEnabled(False); col1.addWidget(x)
col1.addWidget(QLineEdit("Line edit"))
le = QLineEdit("Focused edit"); col1.addWidget(le); le.setFocus()
cb = QComboBox(); cb.addItems(["Combo box", "Two", "Three"]); col1.addWidget(cb)
sp = QSpinBox(); sp.setValue(42); col1.addWidget(sp)
for text, st in (("Checkbox", Qt.CheckState.Unchecked), ("Checked", Qt.CheckState.Checked), ("Partial", Qt.CheckState.PartiallyChecked)):
    c = QCheckBox(text); c.setTristate(True); c.setCheckState(st); col1.addWidget(c)
r1, r2 = QRadioButton("Radio"), QRadioButton("Radio checked"); r2.setChecked(True); col1.addWidget(r1); col1.addWidget(r2)
col1.addStretch()

s = QSlider(Qt.Orientation.Horizontal); s.setValue(40); col2.addWidget(s)
p = QProgressBar(); p.setValue(60); col2.addWidget(p)
tabs = QTabWidget(); tabs.addTab(QLabel("Tab one"), "Overview"); tabs.addTab(QLabel("two"), "Settings"); tabs.addTab(QLabel("three"), "Logs")
col2.addWidget(tabs)
gb = QGroupBox("Group box"); gl = QVBoxLayout(gb); gl.addWidget(QLabel("Inside the group")); col2.addWidget(gb)
lst = QListWidget(); lst.addItems([f"Item {i:02d}" for i in range(1, 7)]); lst.setCurrentRow(2); col2.addWidget(lst)
tree = QTreeWidget(); tree.setHeaderLabels(["Name", "Size"])
par = QTreeWidgetItem(["Folder", "—"]); QTreeWidgetItem(par, ["child.txt", "4 KB"]); tree.addTopLevelItem(par); par.setExpanded(True)
col2.addWidget(tree)
tb2 = QToolButton(); tb2.setText("Tool"); col2.addWidget(tb2)
menu = QMenu(); menu.addAction("Open")
mb = QPushButton("Menu button"); mb.setMenu(menu); col2.addWidget(mb)

w.resize(640, 720); w.show()
out = sys.argv[1]


def shot():
    w.grab().save(out)
    m = QMenu(); m.addAction("Open"); c2 = m.addAction("Checked item"); c2.setCheckable(True); c2.setChecked(True)
    m.addAction("Hovered item"); m.addSeparator(); sub = m.addMenu("Submenu"); sub.addAction("x"); m.addAction("Quit")
    m.popup(w.mapToGlobal(w.rect().center()))
    QTimer.singleShot(300, lambda: QTest.mouseMove(m, m.actionGeometry(m.actions()[2]).center()))
    QTimer.singleShot(1500, lambda: (m.grab().save(out.replace(".png", "-menu.png")), app.quit()))


QTimer.singleShot(600, shot)
app.exec()
