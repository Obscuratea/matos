# Sourced by install.sh and uninstall.sh: prints the default profile of the Firefox install.
find_profile() {
  python3 - <<'PY'
import configparser, os
for base in ("~/.config/mozilla/firefox", "~/.mozilla/firefox"):
    base = os.path.expanduser(base)
    ini = os.path.join(base, "profiles.ini")
    if not os.path.exists(ini):
        continue
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(ini)
    for section in cp.sections():
        if section.startswith("Install") and cp.has_option(section, "Default"):
            print(os.path.join(base, cp.get(section, "Default")))
            raise SystemExit
PY
}
