# MatOS: notes for Claude

Read this first when asked to install, update or debug MatOS on a machine. It is the install playbook, mainly for putting MatOS on Joshua's laptop. Project history lives in Joshua's memory file `project-matos.md`; this file is the portable part.

## What MatOS is
macOS 26 look rebuilt in Material You. One palette (`tools/palette.py`) generates every layer: colour schemes, Plasma style, Kvantum, Aurorae window decoration, KWin rounded-corners settings, icon theme (Breeze overlay), wallpaper, logos, Firefox skin, Ghostty themes. Default accent Lavender `#b69cff`; with no `--seed` it reads the KDE accent from kdeglobals. Window buttons stay on the right. No dock.

## Target
CachyOS/Arch, Plasma 6.x on Wayland. Not tested elsewhere (the effect plugin and `plasma-changeicons` path are Arch specific).

## Installing on a new machine (laptop)
1. Prereqs. Never run sudo yourself; print the command for Joshua (he runs it with `! `):
   `sudo pacman -S kvantum kwin-effect-rounded-corners librsvg python-pillow python-fonttools`
   Also needs `kwriteconfig6 kreadconfig6 plasma-apply-colorscheme plasma-apply-desktoptheme qdbus6` (come with Plasma). `install.sh` checks for all of these and prints what is missing. Roboto Flex ships in `fonts/` and is installed to `~/.local/share/fonts/matos` automatically.
2. Clone: `git clone https://github.com/Obscuratea/matos ~/Projects/matos` (gh is logged in as Obscuratea on Joshua's desktop; on the laptop he may need `gh auth login` only if the repo were private, it is public).
3. Build + install without switching: `cd ~/Projects/matos && ./install.sh`. This also builds the wallpaper (can take a while).
4. **Wallpaper size:** the default sizes target Joshua's ultrawide. On the laptop run first: `python3 tools/gen_wallpaper.py build/wallpapers/MatOS --sizes <W>x<H>,...` (ask `kscreen-doctor -o` / `xrandr` for the panel resolution; include portrait if rotated), then `./install.sh`. install.sh skips the wallpaper step when `build/wallpapers/MatOS/contents/images_dark` exists.
5. Switch: `./install.sh --apply` (dark) or `--apply light`. It first backs up kdeglobals, kwinrc, plasmarc, plasmashellrc, the applets rc, Kvantum config and kdedefaults to `~/.local/share/matos/backup/<time>`. `./restore.sh` reverts.
6. **Reload the rounded-corners effect.** KWin only re-reads its settings when the effect reloads: `qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect kwin4_effect_shapecorners; qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect kwin4_effect_shapecorners`. If windows are square or the glass line is missing, this is the cause. Also check System Settings > Desktop Effects that "Rounded Corners" is enabled (Plugins `kwin4_effect_shapecornersEnabled` is set by gen_kwin).
7. Apps: `./firefox/install.sh` (restart Firefox; accent is baked, rerun with `--seed`), `./ghostty/install.sh` (backs up old config to `config.ghostty.obscura`).
8. Log out/in (or restart plasmashell: `kquitapp6 plasmashell; kstart plasmashell`) so panel + icons settle.

## Laptop differences to expect
- **Panel:** `--apply` sets the kickoff launcher icon and wallpaper through plasmashell scripting for every panel. Joshua's desktop uses one thin floating top panel (kickoff, global menu, icon tasks, clock, systray). The laptop's panel layout is whatever he has; do not rebuild it unless asked.
- **Accent:** follows the KDE accent on that machine; pass `--seed '#b69cff'` to force Lavender so both machines match.
- **HiDPI / scaling:** Aurorae shadow pad (28px) and radii are in logical px; check once at the laptop's scale. Wallpaper sizes are physical px.
- **Touchpad/battery stuff is untouched.** MatOS only changes look: colours, Plasma style, Kvantum, window deco, KWin rounded-corner keys, icons, fonts (Roboto Flex everywhere except monospace), wallpaper.
- Other Joshua apps (Vox, Ordo, Portae, Animus, ...) are separate projects with their own MatOS styling; they auto-switch to the soft look when the colour scheme name starts with `MatOS` (Vox) or ship their own CSS. Not part of this repo.

## Regenerating / development
- `python3 tools/palette.py --check` verifies contrast pairs; `--css` emits `--mat-*` variables for web pages.
- Each `tools/gen_*.py` writes into `build/` (gitignored, safe to delete). Preview: `SCALE=2 tools/preview.sh dark|light [#seed]`.
- New app ported to MatOS = new pill-letter icon: add a line to `APP_BARS` in `Scripts for Claude/build_logo.py`, run `python3 "Scripts for Claude/build_logo.py" brand/logo`.
- Helper/test scripts live in `Scripts for Claude/` (Joshua's rule: keep them there, he doesn't delete that folder).

## Gotchas (learned the hard way)
- `fc-list | grep -q` under `set -o pipefail` reads as "missing" (SIGPIPE); use `>/dev/null`.
- The Rounded Corners effect only draws shadows inside room the decoration reserves; the shadow is painted by `gen_aurorae.py` and gen_kwin must keep `ShadowSize == SHADOW_PAD` and `UseNativeDecorationShadows=true`, `ShadowAlpha=0`.
- Radius: `gen_kwin.RADIUS` (18) must equal `WINDOW_RADIUS` in gen_aurorae.
- Rounded 9-patch tiles (Kvantum and Plasma SVGs) must stay exactly inside their tile; draw borders as filled quarter-rings, not stroked arcs.
- Firefox: logo as data: URI doesn't render in about:newtab; headless Marionette shows a double urlbar ring that is not a bug.
- Light variant has not been fully verified live; check it on first use.
- Never run `pkill -f` on PipeWire when testing Vox; use a private PipeWire.
