#!/usr/bin/env python3
"""ff_probe.py SCRATCHDIR : start headless Firefox on the dark scratch profile, focus the urlbar, print computed backgrounds."""
import subprocess, sys, time, os, pathlib
from marionette_driver.marionette import Marionette
S = pathlib.Path(sys.argv[1]); prof = S / "ffprofile-dark"
p = subprocess.Popen(["firefox", "--no-remote", "--new-instance", "--profile", str(prof), "--marionette", "--remote-allow-system-access"],
                     env=dict(os.environ, MOZ_HEADLESS="1"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            c = Marionette(host="127.0.0.1", port=2828); c.start_session(); break
        except Exception: time.sleep(0.5)
    c.set_window_rect(width=1400, height=900)
    c.set_context("chrome")
    c.execute_script("gURLBar.focus()"); time.sleep(1)
    print(c.execute_script("""
      const out=[]; const els=[document.querySelector('#urlbar-container'), document.querySelector('#urlbar'), ...document.querySelectorAll('#urlbar *')];
      for (const e of els) for (const ps of [null,'::before','::after']) {
        const cs=getComputedStyle(e,ps); const o=cs.outlineStyle!=='none'&&cs.outlineWidth!=='0px'; const sh=cs.boxShadow!=='none'; const bd=cs.borderTopStyle!=='none'&&cs.borderTopWidth!=='0px';
        if (o||sh||bd) out.push((e.id||e.className||e.localName)+(ps||'')+' outline:'+(o?cs.outline:'-')+' shadow:'+(sh?cs.boxShadow.slice(0,60):'-')+' border:'+(bd?cs.border:'-'));
      }
      return out;"""))
    c.set_context("content")
    c.navigate("about:newtab"); time.sleep(1)
    print(c.execute_script("""const cs=getComputedStyle(document.body,'::before'); const r=getComputedStyle(document.documentElement);
      return [cs.content, cs.width, cs.backgroundImage.slice(0,60), r.getPropertyValue('--m-mark').slice(0,50), r.getPropertyValue('--m-accent')];"""))
finally:
    p.terminate()
