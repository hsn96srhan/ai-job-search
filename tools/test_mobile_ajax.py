#!/usr/bin/env python3
import subprocess
import base64
import time

def run_js(js_code):
    b64 = base64.b64encode(js_code.encode("utf-8")).decode("ascii")
    apple_script = f'''
    tell application "Google Chrome"
        tell tab 2 of window 1
            execute javascript "eval(decodeURIComponent(escape(atob('{b64}'))))"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    return res.stdout.strip()

script = """
(() => {
    window._mobileRes = "pending";
    const f = document.getElementById("contactMobileFormID");
    if (!f) {
        window._mobileRes = "form not found";
        return;
    }
    
    const fd = new FormData(f);
    fd.set("contactMobileForm[cellPhone]", "506267542");
    fd.set("contactMobileForm[mobPhoneAreaCode]", "966");
    fd.set("submit", "submit");
    
    fetch(f.action, {
        method: "POST",
        body: fd,
        headers: { "X-Requested-With": "XMLHttpRequest" }
    }).then(r => r.text()).then(data => {
        window._mobileRes = data;
    }).catch(e => {
        window._mobileRes = "Err: " + e.message;
    });
})()
"""

run_js(script)
time.sleep(2)
print("Response:", run_js("window._mobileRes"))
