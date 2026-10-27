#!/usr/bin/env python3
"""MatOS for Firefox: userChrome.css, userContent.css and user.js, coloured from palette.py (light + dark).
Same layout as the Obscura skin (tabs on top, nav bar hidden under them until the address bar has focus);
the look is MatOS: pill tabs, a pill address bar, rounded panels, Roboto Flex, a soft gradient new tab.
Firefox can't read the Plasma accent, so the accent is baked in here; rerun after changing it.
Usage: gen_firefox.py [OUTDIR] [--seed HEX]"""
import argparse, pathlib, sys, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import palette as P

ROOT = pathlib.Path(__file__).resolve().parent.parent


def vars_block(s, mark=None):
    rgb = lambda h: ", ".join(str(round(c * 255)) for c in P.hex_rgb(h))
    return f"""  --m-bg: {s['surface_container']};
  --m-low: {s['surface_container_low']};
  --m-high: {s['surface_container_high']};
  --m-ink: {s['on_surface']};
  --m-ink-rgb: {rgb(s['on_surface'])};
  --m-ink-var: {s['on_surface_variant']};
  --m-accent: {s['accent']};
  --m-accent-end: {s['gradient_end']};
  --m-on-accent: {s['on_primary']};
  --m-pc: {s['primary_container']};
  --m-on-pc: {s['on_primary_container']};
  --m-line: {s['outline_variant']};
""" + (f"  --m-mark: {mark};\n" if mark else "")


def both(seed, body, marks=False):
    d, l = P.scheme(seed, True), P.scheme(seed, False)
    md, ml = (mark_uri(True), mark_uri(False)) if marks else (None, None)
    return (f":root {{\n{vars_block(d, md)}}}\n\n@media (prefers-color-scheme: light) {{\n  :root {{\n"
            + "".join("  " + ln + "\n" for ln in vars_block(l, ml).splitlines()) + "  }\n}\n\n" + body)


CHROME = r'''/* MatOS for Firefox. Tabs along the top; the nav bar is hidden under them and wipes down only when the address
   bar has focus (Ctrl+L, Ctrl+T), or while a menu from it is open. Hovering does nothing.
   Installed to <profile>/chrome/userChrome.css. Needs toolkit.legacyUserProfileCustomizations.stylesheets (user.js).
   Firefox's internal selectors can change between releases. */

:root {
  --m-font: "Roboto Flex", "Roboto", system-ui, sans-serif;
  --m-bar-h: 52px;
  --m-tab-h: 44px;          /* the tab row: 34px pills with 5px above and below */
  --m-nav-right: 132px;     /* gap right of Back/Forward: tab search + window buttons */
  --toolbar-bgcolor: var(--m-bg) !important;
  --toolbar-color: var(--m-ink) !important;
  --toolbarbutton-icon-fill: var(--m-ink) !important;
  --toolbarbutton-border-radius: 12px !important;
  --toolbarbutton-hover-background: rgba(var(--m-ink-rgb), 0.08) !important;
  --toolbarbutton-active-background: rgba(var(--m-ink-rgb), 0.14) !important;
  --lwt-accent-color: var(--m-bg) !important;
  --lwt-text-color: var(--m-ink) !important;
  --arrowpanel-background: var(--m-high) !important;
  --arrowpanel-color: var(--m-ink) !important;
  --arrowpanel-border-color: transparent !important;
  --arrowpanel-border-radius: 18px !important;
  --panel-background: var(--m-high) !important;
  --panel-color: var(--m-ink) !important;
  --panel-border-radius: 18px !important;
  --panel-border-color: transparent !important;
  --focus-outline-color: var(--m-accent) !important;
  --tab-min-height: 34px !important;
  --tab-block-margin: 5px !important;
  --tab-border-radius: 12px !important;
}

* { font-family: var(--m-font); }

#navigator-toolbox,
#titlebar,
#TabsToolbar,
#nav-bar,
#TabsToolbar-customization-target {
  background: var(--m-bg) !important;
  color: var(--m-ink) !important;
  box-shadow: none !important;
}

#navigator-toolbox {
  border: 0 !important;
  /* the nav bar hangs below the toolbox; keep it above the web content */
  position: relative !important;
  z-index: 1000 !important;
  /* Firefox sets overflow: clip on the toolbox, which would cut off the nav bar hanging below it */
  overflow: visible !important;
}

/* Strip everything that is not the address bar and its few buttons */
#PersonalToolbar,
#sidebar-button,
#fxa-toolbar-menu-button,
#home-button {
  display: none !important;
}

/* ── Tabs: pills; the selected one takes the container colour ─────────── */

#TabsToolbar {
  border: 0 !important;
  min-height: var(--m-tab-h) !important;
}

#tabbrowser-tabs {
  counter-reset: m-tab;
  min-height: var(--m-tab-h) !important;
}

.tabbrowser-tab { counter-increment: m-tab; }

.tab-background {
  margin-block: 0 !important;
  border: 0 !important;
  outline: 0 !important;
  border-radius: 12px !important;
  background: transparent !important;
  box-shadow: none !important;
  transition: background-color 140ms;
}

.tabbrowser-tab:hover:not([selected]) .tab-background {
  background: rgba(var(--m-ink-rgb), 0.08) !important;
}

.tabbrowser-tab[selected] .tab-background {
  background: var(--m-pc) !important;
}

/* 01, 02, 03 index in front of each tab, tonal on the selected one */
.tab-content::before {
  content: counter(m-tab, decimal-leading-zero);
  font: 500 10px var(--m-font);
  font-variant-numeric: tabular-nums;
  color: var(--m-ink-var);
  opacity: 0.8;
  margin-inline-end: 8px;
}

.tabbrowser-tab[selected] .tab-content::before {
  color: var(--m-on-pc);
  opacity: 1;
}

.tabbrowser-tab .tab-label {
  font: 450 12.5px var(--m-font) !important;
  color: var(--m-ink-var) !important;
}

.tabbrowser-tab[selected] .tab-label {
  color: var(--m-on-pc) !important;
  font-weight: 550 !important;
}

.tabbrowser-tab[selected] .tab-close-button { color: var(--m-on-pc) !important; }
.tab-close-button { border-radius: 9px !important; color: var(--m-ink-var) !important; fill: currentColor !important; }

/* ── Nav bar: under the tabs, keyboard only ───────────────────────────── */

/* Out of flow, hanging off the bottom edge of the toolbox so it overlays the page instead of pushing it.
   Hidden, its chrome is invisible and ignores the pointer; Ctrl+L / Ctrl+T / Alt+D focus the address bar and
   wipe it down from under the tabs. Back and Forward can't be moved to the tab row in Customize mode
   (Firefox marks them non-removable), so they stay in the nav bar and are lifted into the tab row with CSS. */
#nav-bar {
  position: absolute !important;
  inset: 100% 0 auto 0 !important;
  height: var(--m-bar-h) !important;
  min-height: var(--m-bar-h) !important;
  padding: 0 12px !important;
  z-index: 100;
  border: 0 !important;
  border-radius: 0 0 22px 22px !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28) !important;
  transition: background-color 140ms, box-shadow 140ms;
}

#nav-bar:not(:has(#urlbar[focused], :focus-visible, [open="true"], #urlbar[open])),
#main-window:not([customizing]) #nav-bar:not(:has(#urlbar[focused], :focus-visible, [open="true"], #urlbar[open])) {
  background: transparent !important;
  box-shadow: none !important;
  pointer-events: none;
}

#main-window:not([customizing]) #nav-bar > :not(#nav-bar-customization-target),
#main-window:not([customizing]) #nav-bar-customization-target > :not(#back-button, #forward-button) {
  clip-path: inset(0 0 100% 0);
  pointer-events: none;
  transition: clip-path 160ms cubic-bezier(0.2, 0, 0, 1);
}

#main-window:not([customizing]) #nav-bar:has(#urlbar[focused], :focus-visible, [open="true"], #urlbar[open]) > :not(#nav-bar-customization-target),
#main-window:not([customizing]) #nav-bar:has(#urlbar[focused], :focus-visible, [open="true"], #urlbar[open]) #nav-bar-customization-target > :not(#back-button, #forward-button) {
  clip-path: inset(0);
  pointer-events: auto;
}

/* Back / Forward ride in the tab row, left of tab search and the window buttons */
#main-window:not([customizing]) #back-button,
#main-window:not([customizing]) #forward-button {
  position: absolute !important;
  top: calc(-1 * var(--m-tab-h) + 5px);
  width: 34px;
  height: 34px;
  margin: 0 !important;
  padding: 0 !important;
  pointer-events: auto;
}

#main-window:not([customizing]) #forward-button { right: var(--m-nav-right); }
#main-window:not([customizing]) #back-button { right: calc(var(--m-nav-right) + 34px); }

#back-button,
#forward-button { --toolbarbutton-inner-padding: 9px; }

/* ── Address bar: a pill with a tonal fill; accent ring when focused ──── */

#urlbar {
  --urlbar-height: 38px;
  --urlbar-min-height: 38px;
  --urlbar-toolbar-height: var(--m-bar-h);
}

#urlbar-container {
  padding-block: 0 !important;
  margin-block: 0 !important;
}

.urlbar-background,
#searchbar {
  background: var(--m-high) !important;
  border: 0 !important;
  border-radius: 999px !important;
  box-shadow: none !important;
}

#urlbar[focused] .urlbar-background,
#searchbar:focus-within {
  box-shadow: none !important;
  outline: 2px solid var(--m-accent) !important;
  outline-offset: -2px !important;
}

#urlbar-input,
#searchbar .searchbar-textbox {
  font: 450 13.5px var(--m-font) !important;
}

#nav-bar,
#nav-bar-customization-target,
#urlbar-container { overflow: visible !important; }

.urlbarView {
  max-height: min(70vh, 560px) !important;
  background: var(--m-high) !important;
  border: 0 !important;
  border-radius: 22px !important;
  margin-top: 8px !important;
  padding: 6px !important;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.35) !important;
}

moz-urlbar,
.urlbarView {
  --urlbarView-highlight-background: var(--m-pc) !important;
  --urlbarView-highlight-color: var(--m-on-pc) !important;
  --urlbarView-hover-background: rgba(var(--m-ink-rgb), 0.08) !important;
  --urlbarView-separator-color: transparent !important;
}

.urlbarView-row { border-radius: 14px !important; }

.urlbarView-row[selected] {
  background: var(--m-pc) !important;
  color: var(--m-on-pc) !important;
}

/* The panel paints its own default background layer on top of ours */
.urlbarView-background { background: transparent !important; box-shadow: none !important; border: 0 !important; }

/* The engine chip in the address bar is a moz-button; it is themed through variables */
moz-button.searchmode-switcher {
  --button-background-color-muted: transparent !important;
  --button-background-color-muted-hover: rgba(var(--m-ink-rgb), 0.08) !important;
  --button-background-color-muted-active: rgba(var(--m-ink-rgb), 0.14) !important;
  --button-background-color-muted-selected: rgba(var(--m-ink-rgb), 0.14) !important;
  --button-border-color-muted: transparent !important;
  --button-border-color-muted-hover: transparent !important;
  --button-border-radius: 999px !important;
}

/* Empty content area (before a page paints) stays on-brand */
.browserContainer,
#tabbrowser-tabpanels { background: var(--m-low) !important; }

/* ── Menus and panels: rounded, tonal, no outline ─────────────────────── */

menupopup,
panel {
  --panel-border-radius: 18px;
  border-radius: 18px !important;
  border: 1px solid rgba(var(--m-ink-rgb), 0.08) !important;
}

menupopup menuitem,
menupopup menu { border-radius: 10px !important; margin-inline: 4px !important; }
'''

CONTENT = r'''/* MatOS for Firefox: new tab page, error pages, scrollbars. Installed to <profile>/chrome/userContent.css.
   The new tab is Firefox's emptied about:newtab (user.js turns its own page off), drawn from CSS. */

@-moz-document url("about:blank"), url("about:newtab"), url("about:home"), url-prefix("about:neterror"), url-prefix("about:certerror") {
  html {
    height: 100%;
    font-family: "Roboto Flex", "Roboto", system-ui, sans-serif;
    background-color: var(--m-bg);
    background-image:
      radial-gradient(60vmax 50vmax at 80% 8%, rgba(var(--m-ink-rgb), 0) 0, transparent 0),
      radial-gradient(55vmax 45vmax at 18% 92%, color-mix(in srgb, var(--m-accent-end) 26%, transparent), transparent 70%),
      radial-gradient(60vmax 50vmax at 85% 10%, color-mix(in srgb, var(--m-accent) 30%, transparent), transparent 70%);
  }

  body { margin: 0; height: 100%; background: transparent; }

  /* the mark, centred, with a soft pill hint underneath */
  body::before {
    content: "";
    position: fixed;
    left: 50%; top: 42%;
    width: min(22vmin, 180px); height: min(22vmin, 180px);
    transform: translate(-50%, -50%);
    background: var(--m-mark) center / contain no-repeat;
    pointer-events: none;
  }
}

@-moz-document url("about:blank"), url("about:newtab"), url("about:home") {
  body::after {
    content: "Ctrl+L to search";
    position: fixed;
    left: 50%; top: calc(42% + min(14vmin, 120px));
    transform: translateX(-50%);
    padding: 10px 20px;
    border-radius: 999px;
    background: var(--m-high);
    color: var(--m-ink-var);
    font: 450 13px "Roboto Flex", "Roboto", system-ui, sans-serif;
    letter-spacing: .02em;
    white-space: nowrap;
    user-select: none;
    pointer-events: none;
  }
}

/* error pages: the card is a shadow-DOM component, so it is themed through inherited properties and the
   design-system variables it reads (the fox is switched off in user.js) */
@-moz-document url-prefix("about:neterror"), url-prefix("about:certerror") {
  body { display: grid; place-items: center; min-height: 100%; }
  body::before { top: 14%; width: 80px; height: 80px; }
  net-error-card {
    color: rgb(var(--m-ink-rgb));
    font-family: "Roboto Flex", "Roboto", system-ui, sans-serif;
    --button-background-color-primary: var(--m-accent);
    --button-background-color-primary-hover: var(--m-accent);
    --button-background-color-primary-active: var(--m-accent);
    --button-text-color-primary: var(--m-on-accent);
    --button-text-color-primary-hover: var(--m-on-accent);
    --button-text-color-primary-active: var(--m-on-accent);
    --button-border-color-primary: var(--m-accent);
    --button-border-radius: 999px;
    --border-radius-small: 12px;
    --border-radius-medium: 18px;
    --focus-outline-color: var(--m-accent);
    --focus-outline: 2px solid var(--m-accent);
    --color-accent-primary: var(--m-accent);
    --color-accent-primary-hover: var(--m-accent);
    --color-accent-primary-active: var(--m-accent);
    --link-color: var(--m-accent);
    --link-color-hover: var(--m-accent);
  }
}

/* thin accent scrollbars everywhere; pages that style their own keep theirs */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--m-accent) transparent;
}
'''

USERJS = '''// MatOS: load userChrome.css / userContent.css from the profile's chrome/ folder.
// Read at Firefox startup, so restart Firefox after installing.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
// New tab and home are about:newtab (emptied by the pref above), drawn by userContent.css.
user_pref("browser.newtabpage.enabled", false);
user_pref("browser.startup.homepage", "about:newtab");
// Error pages: drop the fox illustration so userContent.css can theme the rest.
user_pref("browser.netError.illustration.enabled", false);
'''


def mark_uri(dark):
    # a file next to the stylesheet (chrome/): Firefox refused the same SVG as a data: URI in about:newtab
    return f'url("matos-mark-{"dark" if dark else "light"}.svg")'


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=str(ROOT / "build/firefox"))
    ap.add_argument("--seed")
    a = ap.parse_args()
    seed = P.tokens(a.seed)["seed"]
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "userChrome.css").write_text(both(seed, CHROME))
    content = both(seed, CONTENT, marks=True)
    (out / "userContent.css").write_text(content)
    (out / "user.js").write_text(USERJS)
    for v in ("dark", "light"):
        (out / f"matos-mark-{v}.svg").write_text((ROOT / "brand/logo" / f"matos-mark-{v}.svg").read_text())
    print(f"wrote {out}")
