#!/usr/bin/env python3
"""Generate the MatOS Kvantum theme (SVG + kvconfig) for dark/light and an accent.

Kvantum can't read the Qt palette for SVG fills, so colours are baked in from tools/palette.py;
the accent watcher re-runs this when the system accent changes.
Every frame is rounded: corner pieces hold a quarter-disc of fill plus a quarter-ring of border.
Usage: gen_kvantum.py <dark|light|both> <outdir> [--seed HEX]
"""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P

FLIP = {"topleft": "", "topright": "translate({r},0) scale(-1,1)",
        "bottomleft": "translate(0,{r}) scale(1,-1)", "bottomright": "translate({r},{r}) scale(-1,-1)"}
EDGE = {"top": ("h", ""), "bottom": ("h", "translate(0,{r}) scale(1,-1)"),
        "left": ("v", ""), "right": ("v", "translate({r},0) scale(-1,1)")}


def mix(a, b, t):
    """Blend hex a toward hex b by t (0..1)."""
    x, y = P.hex_rgb(a), P.hex_rgb(b)
    return P.rgb_hex([p + (q - p) * t for p, q in zip(x, y)])


def fill(c):
    """c is '#hex', ('#hex', alpha), 'url(#id)' or None."""
    if c is None:
        return 'fill="none"'
    if isinstance(c, tuple):
        return f'fill="{c[0]}" fill-opacity="{c[1]}"'
    return f'fill="{c}"'


def strk(c, w=1):
    col, op = (c if isinstance(c, tuple) else (c, 1))
    return f'fill="none" stroke="{col}" stroke-width="{w}"' + (f' stroke-opacity="{op}"' if op != 1 else "")


class Sheet:
    def __init__(self, width=1200):
        self.out, self.defs, self.x, self.y, self.row_h, self.width = [], [], 0, 0, 0, width

    def el(self, eid, w, h, body=""):
        if self.x + w > self.width:
            self.x, self.y, self.row_h = 0, self.y + self.row_h + 4, 0
        self.out.append(f'<g id="{eid}" transform="translate({self.x},{self.y})">'
                        f'<rect width="{w}" height="{h}" fill="#000" fill-opacity="0"/>{body}</g>')
        self.x += w + 4
        self.row_h = max(self.row_h, h)

    def svg(self):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.y + self.row_h}">\n'
                f'<defs>{"".join(self.defs)}</defs>\n' + "\n".join(self.out) + "\n</svg>\n")


def frame(sh, name, r, bg, border=None, bw=1):
    """Rounded Kvantum frame `name` (+ its 8 pieces), radius r. The kvconfig frame width must be r."""
    if r == 0:
        sh.el(name, 8, 8, f'<rect width="8" height="8" {fill(bg)}/>')
        for p in FLIP:
            sh.el(f"{name}-{p}", 1, 1)
        for p in EDGE:
            sh.el(f"{name}-{p}", 8 if p in ("top", "bottom") else 1, 1 if p in ("top", "bottom") else 8)
        return
    # Shapes must stay exactly inside the r x r tile: Kvantum/KSvg scale a piece by its bounding box,
    # so a stroke (whose bounds include its width) or any overshoot shrinks the piece and opens gaps.
    # The border is therefore a filled quarter-ring, not a stroked arc.
    q = f"M0,{r} A{r},{r} 0 0 1 {r},0 L{r},{r} Z"
    ri = r - bw
    ring = f"M0,{r} A{r},{r} 0 0 1 {r},0 V{bw} A{ri},{ri} 0 0 0 {bw},{r} Z"
    for p, t in FLIP.items():
        body = f'<path d="{q}" {fill(bg)}/>' + (f'<path d="{ring}" {fill(border)}/>' if border else "")
        sh.el(f"{name}-{p}", r, r, f'<g transform="{t.format(r=r)}">{body}</g>')
    for p, (o, t) in EDGE.items():
        w, hh = (8, r) if o == "h" else (r, 8)
        line = ""
        if border:
            line = f'<rect width="8" height="{bw}" {fill(border)}/>' if o == "h" else f'<rect width="{bw}" height="8" {fill(border)}/>'
        sh.el(f"{name}-{p}", w, hh, f'<g transform="{t.format(r=r)}"><rect width="{w}" height="{hh}" {fill(bg)}/>{line}</g>')
    sh.el(name, 8, 8, f'<rect width="8" height="8" {fill(bg)}/>')


# frame radius per kvconfig section (frame widths must match these)
RAD = {"button": 12, "tbutton": 10, "lineedit": 10, "common": 12, "group": 14, "menu": 12, "tooltip": 8,
       "dock": 12, "itemview": 8, "menuitem": 8, "menubaritem": 8, "tab": 10, "tabframe": 14,
       "scrollbarslider": 4, "slider": 2, "progress": 3, "progress-pattern": 3, "header": 0, "toolbar": 0}


def build(s, dark):
    ink, ink2 = s["on_surface"], s["on_surface_variant"]
    win, view = s["surface_container"], s["surface_container_low"]
    hover = (ink, .08)
    sel, on_sel = s["primary_container"], s["on_primary_container"]
    pri, on_pri = s["primary"], s["on_primary"]
    outline, outline_v = s["outline"], s["outline_variant"]
    sh = Sheet()
    sh.defs.append(f'<linearGradient id="grad" x1="0" x2="1"><stop stop-color="{s["gradient_start"]}"/>'
                   f'<stop offset="1" stop-color="{s["gradient_end"]}"/></linearGradient>')

    # ---- buttons: tonal pills (M3 "filled tonal"), pressed/toggled go primary container ----
    frame(sh, "button-normal", RAD["button"], s["surface_container_highest"])
    frame(sh, "button-focused", RAD["button"], mix(s["surface_container_highest"], ink, .08))
    frame(sh, "button-pressed", RAD["button"], sel)
    frame(sh, "button-toggled", RAD["button"], sel)
    frame(sh, "button-disabled", RAD["button"], (ink, .06))
    sh.el("button-default-indicator", 8, 8)  # empty: stops Kvantum's fallback corner triangle
    frame(sh, "tbutton-normal", RAD["tbutton"], None)
    frame(sh, "tbutton-focused", RAD["tbutton"], hover)
    frame(sh, "tbutton-pressed", RAD["tbutton"], sel)
    frame(sh, "tbutton-toggled", RAD["tbutton"], sel)
    # ---- text fields: filled, no border until focused ----
    frame(sh, "lineedit-normal", RAD["lineedit"], s["surface_container_highest"])
    frame(sh, "lineedit-focused", RAD["lineedit"], s["surface_container_highest"], pri, 2)
    frame(sh, "lineedit-disabled", RAD["lineedit"], (ink, .04))
    # views: no outline. The frame is a rounded card in the view colour; the (square) viewport inside it has
    # the same colour, so the view reads as rounded and the subtler background is the only separator.
    frame(sh, "common-normal", RAD["common"], view)
    frame(sh, "common-focused", RAD["common"], view)
    frame(sh, "group-normal", RAD["group"], s["surface_container_low"] if not dark else s["surface_container_high"])
    frame(sh, "menu-normal", RAD["menu"], (s["surface_container_high"], P.GLASS["menu_alpha"]), (ink, .12))
    frame(sh, "tooltip-normal", RAD["tooltip"], s["inverse_surface"])
    frame(sh, "dock-normal", RAD["dock"], win)

    # ---- item views / menu items: rounded pills ----
    frame(sh, "itemview-focused", RAD["itemview"], hover)
    frame(sh, "itemview-pressed", RAD["itemview"], sel)
    frame(sh, "itemview-toggled", RAD["itemview"], sel)
    for st in ("focused", "pressed", "toggled"):
        frame(sh, f"menuitem-{st}", RAD["menuitem"], sel)
    frame(sh, "menubaritem-focused", RAD["menubaritem"], hover)
    frame(sh, "menubaritem-pressed", RAD["menubaritem"], sel)
    frame(sh, "menubaritem-toggled", RAD["menubaritem"], sel)

    # ---- tabs: selected tab is a primary-container pill, no attached frame ----
    for pre in ("tab", "floating-tab"):
        frame(sh, f"{pre}-normal", RAD["tab"], None)
        frame(sh, f"{pre}-focused", RAD["tab"], hover)
        frame(sh, f"{pre}-toggled", RAD["tab"], sel)
    frame(sh, "tabframe-normal", RAD["tabframe"], None, outline_v)
    sh.el("tab-tear", 8, 8)
    sh.el("header-separator", 2, 8, f'<rect width="1" height="8" {fill(outline_v)}/>')
    for st, bg in (("normal", win), ("focused", mix(win, ink, .06)), ("pressed", mix(win, ink, .10)), ("toggled", win)):
        sh.el(f"header-{st}", 8, 8, f'<rect width="8" height="8" {fill(bg)}/>')
        # 1px line as a real frame piece: drawn inside the stretched interior it scales up
        sh.el(f"header-{st}-bottom", 8, 1, f'<rect width="8" height="1" {fill(outline_v)}/>')
        for p in list(FLIP) + ["top", "left", "right"]:
            sh.el(f"header-{st}-{p}", 1, 1)
    sh.el("toolbar-normal", 8, 8)
    for p in list(FLIP) + list(EDGE):
        sh.el(f"toolbar-normal-{p}", 1, 1)
    sh.el("toolbar-handle", 4, 12, "".join(f'<circle cx="2" cy="{y}" r="1" {fill(outline)}/>' for y in (3, 6, 9)))
    for st in ("normal", "focused"):
        sh.el(f"titlebar-{st}", 8, 8, f'<rect width="8" height="8" {fill(win if st == "focused" else s["surface_container_low"])}/>')

    # ---- scrollbars: thin rounded thumb, no groove ----
    frame(sh, "scrollbarslider-normal", RAD["scrollbarslider"], (ink, .30))
    frame(sh, "scrollbarslider-focused", RAD["scrollbarslider"], (ink, .50))
    frame(sh, "scrollbarslider-pressed", RAD["scrollbarslider"], pri)
    sh.el("scrollbargroove-normal", 8, 8)
    for p in list(FLIP) + list(EDGE):
        sh.el(f"scrollbargroove-normal-{p}", 1, 1)

    # ---- slider (M3 Expressive: thick track, vertical pill handle) / progress (gradient) ----
    frame(sh, "slider-normal", RAD["slider"], s["secondary_container"])
    frame(sh, "slider-toggled", RAD["slider"], pri)
    for st, col in (("normal", pri), ("focused", pri), ("pressed", mix(pri, ink, .25)), ("disabled", (ink, .38))):
        sh.el(f"slidercursor-{st}", 6, 20, f'<rect x="1" y="0" width="4" height="20" rx="2" {fill(col)}/>')
    frame(sh, "progress-normal", RAD["progress"], s["secondary_container"])
    frame(sh, "progress-pattern-normal", RAD["progress-pattern"], "url(#grad)")
    frame(sh, "progress-pattern-disabled", RAD["progress-pattern"], (ink, .3))

    # ---- splitter / size grip ----
    for st, col in (("normal", None), ("focused", (pri, .5)), ("pressed", pri)):
        sh.el(f"splitter-{st}", 4, 4, f'<rect width="4" height="4" {fill(col)}/>')
    for st, col in (("normal", outline), ("focused", pri), ("pressed", pri)):
        sh.el(f"splitter-grip-{st}", 16, 4, f'<rect x="2" y="1" width="12" height="2" rx="1" {fill(col)}/>')
    for st, col in (("normal", outline), ("focused", pri)):
        sh.el(f"resize-grip-{st}", 13, 13, "".join(f'<circle cx="{x}" cy="{y}" r="1.2" {fill(col)}/>'
                                                   for x, y in ((11, 5), (8, 8), (11, 8), (5, 11), (8, 11), (11, 11))))

    # ---- check boxes and radios ----
    tick = f'<path d="M4.5,9.5 L7.5,12.5 L13.5,6" fill="none" stroke="{on_pri}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    dash = f'<rect x="5" y="8" width="8" height="2" rx="1" {fill(on_pri)}/>'
    for st, bd in (("normal", ink2), ("focused", pri), ("pressed", pri), ("disabled", (ink, .38))):
        sh.el(f"checkbox-{st}", 18, 18, f'<rect x="1" y="1" width="16" height="16" rx="4" {strk(bd, 2)}/>')
        on = pri if st != "disabled" else (ink, .38)
        sh.el(f"checkbox-checked-{st}", 18, 18, f'<rect width="18" height="18" rx="5" {fill(on)}/>{tick}')
        sh.el(f"checkbox-tristate-{st}", 18, 18, f'<rect width="18" height="18" rx="5" {fill(on)}/>{dash}')
        sh.el(f"radio-{st}", 18, 18, f'<circle cx="9" cy="9" r="8" {strk(bd, 2)}/>')
        sh.el(f"radio-checked-{st}", 18, 18, f'<circle cx="9" cy="9" r="8" {strk(on, 2)}/><circle cx="9" cy="9" r="4.5" {fill(on)}/>')

    # ---- arrows: rounded chevrons; spin +/- ----
    chev = {"up": "M3,8 L6,5 L9,8", "down": "M3,4.5 L6,7.5 L9,4.5", "left": "M7.5,3 L4.5,6 L7.5,9", "right": "M4.5,3 L7.5,6 L4.5,9"}
    for d, path in chev.items():
        for st, col in (("normal", ink2), ("focused", ink), ("pressed", pri), ("disabled", (ink, .38))):
            sh.el(f"arrow-{d}-{st}", 12, 12, f'<path d="{path}" {strk(col, 1.6)} stroke-linecap="round" stroke-linejoin="round"/>')
    for st, col in (("normal", ink2), ("pressed", pri)):
        sh.el(f"arrow-plus-{st}", 12, 12, f'<path d="M2.5,6 H9.5 M6,2.5 V9.5" {strk(col, 1.6)} stroke-linecap="round"/>')
        sh.el(f"arrow-minus-{st}", 12, 12, f'<path d="M2.5,6 H9.5" {strk(col, 1.6)} stroke-linecap="round"/>')

    # ---- dial ----
    sh.el("dial", 20, 20, f'<circle cx="10" cy="10" r="9.5" {fill(s["surface_container_highest"])}/>')
    sh.el("dial-handle", 6, 6, f'<circle cx="3" cy="3" r="3" {fill(pri)}/>')
    sh.el("dial-notches", 20, 20)
    return sh.svg(), kvconfig(s, dark)


def kvconfig(s, dark):
    ink, on_sel = s["on_surface"], s["on_primary_container"]

    def sec(name, **kw):
        def key(k):
            for pre in ("frame_", "text_", "interior_", "indicator_", "min_"):
                if k.startswith(pre):
                    return k.replace("_", ".", 1) if pre != "min_" else k.replace("_", ".")
            return k
        return f"[{name}]\n" + "\n".join(f"{key(k)}={v}" for k, v in kw.items()) + "\n"

    def fr(n, r=None):
        r = RAD[n] if r is None else r
        return dict(frame="true", frame_element=n, frame_top=r, frame_bottom=r, frame_left=r, frame_right=r)

    g = f"""[%General]
author=MatOS
comment=MatOS: rounded Material glass. Generated by tools/gen_kvantum.py.
x11drag=menubar_and_primary_toolbar
alt_mnemonic=true
left_tabs=false
center_doc_tabs=false
center_normal_tabs=true
attach_active_tab=false
joined_inactive_tabs=false
mirror_doc_tabs=false
group_toolbar_buttons=false
toolbar_item_spacing=2
toolbar_interior_spacing=4
spread_progressbar=true
composite=true
menu_shadow_depth=0
tooltip_shadow_depth=0
splitter_width=4
scroll_width=8
scroll_arrows=false
scroll_min_extent=40
slider_width=4
slider_handle_width=20
slider_handle_length=6
tickless_slider_handle_size=20
check_size=18
textless_progressbar=true
progressbar_thickness=6
menubar_mouse_tracking=true
toolbutton_style=0
click_behavior=0
translucent_windows=false
blurring=false
popup_blurring=true
vertical_spin_indicators=false
spin_button_width=24
fill_rubberband=true
small_icon_size=16
large_icon_size=32
button_icon_size=16
toolbar_icon_size=22
combo_as_lineedit=true
animate_states=true
combo_menu=true
hide_combo_checkboxes=true
combo_focus_rect=false
groupbox_top_label=true
inline_spin_indicators=true
layout_spacing=8
layout_margin=10
scrollbar_in_view=true
transient_scrollbar=true
transient_groove=true
submenu_overlap=0
tooltip_delay=-1
tree_branch_line=false
no_window_pattern=true
reduce_window_opacity=0
respect_DE=true
menu_separator_height=9
"""
    gc = f"""[GeneralColors]
window.color={s['surface_container']}
base.color={s['surface_container_low']}
alt.base.color={s['surface_container']}
button.color={s['surface_container_highest']}
light.color={mix(s['surface_container'], ink, .12)}
mid.light.color={mix(s['surface_container'], ink, .08)}
dark.color={mix(s['surface_container'], '#000000', .5)}
mid.color={s['outline_variant']}
highlight.color={s['primary_container']}
inactive.highlight.color={mix(s['primary_container'], s['surface_container'], .4)}
text.color={ink}
window.text.color={ink}
button.text.color={ink}
disabled.text.color={mix(s['surface_container'], ink, .38)}
tooltip.text.color={s['inverse_on_surface']}
highlight.text.color={on_sel}
link.color={s['primary']}
link.visited.color={s['tertiary']}
progress.indicator.text.color={ink}
"""
    sep = f"[MenuSeparator]\n"  # nothing; separator colour comes from mid.color
    tips = s["inverse_on_surface"]
    parts = [g, gc, "[Hacks]\ntransparent_ktitle_label=true\nkcapacitybar_as_progressbar=true\nrespect_darkness=true\n"]
    parts.append(sec("PanelButtonCommand", **fr("button"), interior="true", interior_element="button", indicator_element="arrow", indicator_size=10,
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on_sel, text_toggle_color=on_sel,
                     text_iconspacing=6, text_margin_top=0, text_margin_bottom=0, text_margin_left=4, text_margin_right=4, min_height="+6", min_width="+12"))
    parts.append(sec("PanelButtonTool", **fr("tbutton"), interior="true", interior_element="tbutton", indicator_element="arrow", indicator_size=10,
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on_sel, text_toggle_color=on_sel,
                     text_margin_top=0, text_margin_bottom=0, text_margin_left=0, text_margin_right=0))
    parts.append(sec("ToolbarButton", **fr("tbutton"), interior="true", interior_element="tbutton", indicator_element="arrow", indicator_size=10,
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on_sel, text_toggle_color=on_sel))
    parts.append(sec("Dock", **fr("dock"), interior="true", interior_element="dock"))
    parts.append(sec("DockTitle", frame="false", interior="false", text_focus_color=ink, text_bold="true"))
    parts.append(sec("IndicatorSpinBox", indicator_element="arrow", indicator_size=12, frame="false"))
    parts.append(sec("RadioButton", interior_element="radio", frame="false", interior="true", text_normal_color=ink, text_focus_color=ink))
    parts.append(sec("CheckBox", interior_element="checkbox", frame="false", interior="true", text_normal_color=ink, text_focus_color=ink))
    parts.append(sec("GenericFrame", **fr("common"), interior="false"))
    parts.append(sec("LineEdit", **fr("lineedit"), interior="true", interior_element="lineedit",
                     text_margin_left=0, text_margin_right=0, text_margin_top=0, text_margin_bottom=0))
    parts.append(sec("DropDownButton", indicator_element="arrow-down", frame="false"))
    parts.append(sec("IndicatorArrow", indicator_element="arrow", indicator_size=12, frame="false"))
    parts.append(sec("ToolboxTab", frame="false", text_normal_color=ink, text_focus_color=ink))
    parts.append(sec("Tab", **fr("tab"), interior="true", interior_element="tab", indicator_element="tab",
                     text_normal_color=s["on_surface_variant"], text_focus_color=ink, text_toggle_color=on_sel, text_press_color=on_sel,
                     text_margin_left=4, text_margin_right=4, text_margin_top=0, text_margin_bottom=0, min_width="+12", min_height="+4"))
    parts.append(sec("TabFrame", **fr("tabframe"), interior="false"))
    parts.append(sec("TreeExpander", indicator_size=12, indicator_element="arrow"))
    parts.append(sec("HeaderSection", frame="true", frame_element="header", frame_top=0, frame_bottom=1, frame_left=0, frame_right=0,
                     interior="true", interior_element="header",
                     text_normal_color=s["on_surface_variant"], text_focus_color=ink,
                     text_margin_left=8, text_margin_right=8, text_margin_top=4, text_margin_bottom=4))
    parts.append(sec("SizeGrip", indicator_element="resize-grip", indicator_size=13))
    parts.append(sec("Toolbar", frame="true", frame_element="toolbar", frame_top=0, frame_bottom=0, frame_left=0, frame_right=0,
                     interior="true", interior_element="toolbar", indicator_element="toolbar", indicator_size=5,
                     text_normal_color=ink, text_focus_color=ink))
    parts.append(sec("Slider", **fr("slider"), interior="true", interior_element="slider"))
    parts.append(sec("SliderCursor", interior="true", interior_element="slidercursor", frame="false"))
    parts.append(sec("Progressbar", **fr("progress"), interior="true", interior_element="progress",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=ink, text_toggle_color=ink))
    parts.append(sec("ProgressbarContents", **fr("progress-pattern"), interior="true", interior_element="progress-pattern"))
    parts.append(sec("ItemView", **fr("itemview"), interior="true", interior_element="itemview",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on_sel, text_toggle_color=on_sel,
                     text_margin_left=2, text_margin_right=2, text_margin_top=1, text_margin_bottom=1, min_height="+6"))
    parts.append(sec("Splitter", frame="false", interior="true", interior_element="splitter", indicator_element="splitter-grip", indicator_size=16))
    parts.append(sec("Scrollbar", indicator_size=10, indicator_element="arrow"))
    parts.append(sec("ScrollbarSlider", **fr("scrollbarslider"), interior="true", interior_element="scrollbarslider"))
    parts.append(sec("ScrollbarGroove", frame="false", interior="true", interior_element="scrollbargroove"))
    parts.append(sec("MenuItem", **fr("menuitem"), interior="true", interior_element="menuitem", indicator_element="arrow", indicator_size=10,
                     text_normal_color=ink, text_focus_color=on_sel, text_press_color=on_sel, text_toggle_color=on_sel,
                     text_margin_left=4, text_margin_right=4, text_margin_top=1, text_margin_bottom=1, min_height="+8"))
    parts.append(sec("MenuBarItem", **fr("menubaritem"), interior="true", interior_element="menubaritem",
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on_sel, text_toggle_color=on_sel,
                     text_margin_left=4, text_margin_right=4, text_margin_top=0, text_margin_bottom=0))
    parts.append(sec("MenuBar", frame="false", interior="false"))
    parts.append(sec("TitleBar", frame="false", interior="true", interior_element="titlebar", indicator_size=12,
                     text_normal_color=s["on_surface_variant"], text_focus_color=ink))
    parts.append(sec("ComboBox", **fr("button"), interior="true", interior_element="button", indicator_element="arrow", indicator_size=12,
                     text_normal_color=ink, text_focus_color=ink, text_press_color=on_sel, text_toggle_color=on_sel,
                     text_margin_left=2, text_margin_right=2, text_margin_top=0, text_margin_bottom=0, min_height="+6"))
    parts.append(sec("Menu", **fr("menu"), interior="true", interior_element="menu", text_normal_color=ink, frame_expansion=0))
    parts.append(sec("GroupBox", **fr("group"), interior="false", text_normal_color=ink, text_bold="true",
                     text_margin_top=2, text_margin_left=8, text_margin_right=8, text_margin_bottom=2))
    parts.append(sec("ToolTip", **fr("tooltip"), interior="true", interior_element="tooltip",
                     text_normal_color=tips, text_margin_left=2, text_margin_right=2, text_margin_top=2, text_margin_bottom=2))
    parts.append(sec("StatusBar", frame="false", interior="false"))
    parts.append(sec("Window", interior="false", frame="false"))
    return "\n".join(parts)


def write(variant, outdir, seed):
    dark = variant == "dark"
    name = "MatOSDark" if dark else "MatOSLight"
    d = pathlib.Path(outdir) / name
    d.mkdir(parents=True, exist_ok=True)
    svg, kv = build(P.scheme(seed, dark), dark)
    (d / f"{name}.svg").write_text(svg)
    (d / f"{name}.kvconfig").write_text(kv)
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=["dark", "light", "both"])
    ap.add_argument("outdir", nargs="?", default="build/Kvantum")
    ap.add_argument("--seed")
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    for v in (["dark", "light"] if a.variant == "both" else [a.variant]):
        print("wrote", write(v, a.outdir, seed))
