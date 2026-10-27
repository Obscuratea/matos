#!/usr/bin/env python3
"""Headless Firefox check of the MatOS skin: python ff_test.py SCRATCHDIR [dark|light]
Makes a scratch profile, installs the skin into it, drives states via Marionette, saves PNGs to SCRATCHDIR."""
import subprocess, sys, time, os, shutil, pathlib
from marionette_driver.marionette import Marionette
S = pathlib.Path(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else "dark"
prof = S / f"ffprofile-{mode}"
shutil.rmtree(prof, ignore_errors=True); prof.mkdir(parents=True)
(prof / "user.js").write_text(f'user_pref("ui.systemUsesDarkTheme", {1 if mode == "dark" else 0});\nuser_pref("browser.shell.checkDefaultBrowser", false);\n'
                              'user_pref("browser.aboutwelcome.enabled", false);\nuser_pref("datareporting.policy.dataSubmissionEnabled", false);\n')
subprocess.run([os.path.expanduser("~/Projects/matos/firefox/install.sh"), str(prof)], check=True, stdout=subprocess.DEVNULL)
env = dict(os.environ, MOZ_HEADLESS="1")
p = subprocess.Popen(["firefox", "--no-remote", "--new-instance", "--profile", str(prof), "--marionette", "--remote-allow-system-access"],
                     env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    c = None
    for _ in range(40):
        try:
            c = Marionette(host="127.0.0.1", port=2828); c.start_session(); break
        except Exception:
            time.sleep(0.5)
    c.set_window_rect(width=1400, height=900)
    c.set_context("content")
    c.navigate("data:text/html,<body style='font:16px sans-serif;background:%23f6f6f9'><h1>Example page</h1><p>Page content under the bar.</p>")
    c.set_context("chrome")
    for u in ("about:newtab", "about:blank"):
        c.execute_script("gBrowser.addTrustedTab(arguments[0]);", script_args=[u])
    c.execute_script("gBrowser.selectedTab = gBrowser.tabs[0];")
    time.sleep(1.5)
    def shot(name):
        (S / f"ff-{mode}-{name}.png").write_bytes(__import__("base64").b64decode(c.screenshot()))
    shot("tabs")
    c.execute_script("gURLBar.focus();"); time.sleep(0.8); shot("urlbar")
    c.execute_script("gURLBar.search('matos');"); time.sleep(1.5); shot("results")
    c.execute_script("gBrowser.selectedTab = gBrowser.tabs[1]; gURLBar.blur();"); time.sleep(1.2); shot("newtab")
    c.set_context("content")
    c.execute_script("")
    print("done")
finally:
    p.terminate()
