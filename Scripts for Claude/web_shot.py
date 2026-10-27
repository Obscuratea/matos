#!/usr/bin/env python3
"""web_shot.py SCRATCH URL OUT_PREFIX [click-selector] : headless Firefox screenshots (dark+light) after the page has loaded data."""
import subprocess, sys, time, os, pathlib, base64
from marionette_driver.marionette import Marionette
S = pathlib.Path(sys.argv[1]); url = sys.argv[2]; out = sys.argv[3]; click = sys.argv[4] if len(sys.argv) > 4 else None
for mode in ("dark", "light"):
    prof = S / f"ffp-web-{mode}"
    import shutil; shutil.rmtree(prof, ignore_errors=True); prof.mkdir(parents=True)
    (prof / "user.js").write_text(f'user_pref("ui.systemUsesDarkTheme", {1 if mode == "dark" else 0});\nuser_pref("browser.shell.checkDefaultBrowser", false);\n')
    p = subprocess.Popen(["firefox", "--no-remote", "--new-instance", "--profile", str(prof), "--marionette"], env=dict(os.environ, MOZ_HEADLESS="1"),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                c = Marionette(host="127.0.0.1", port=2828); c.start_session(); break
            except Exception: time.sleep(0.5)
        c.set_window_rect(width=1600, height=1000)
        c.navigate(url); time.sleep(2.5)
        if click:
            c.execute_script(f"document.querySelector({click!r}).click()"); time.sleep(1)
        open(f"{S}/{out}-{mode}.png", "wb").write(base64.b64decode(c.screenshot()))
    finally:
        p.terminate(); time.sleep(1)
print("ok")
