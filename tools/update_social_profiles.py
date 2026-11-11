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
    const pers = document.getElementById("socialProfilesForm_pers");
    if (pers) {
        pers.value = "https://hsn96srhan.github.io/hsn/";
        pers.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const ldin = document.getElementById("socialProfilesForm_ldin");
    if (ldin) {
        ldin.value = "https://www.linkedin.com/in/srhan-jr/";
        ldin.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const git = document.getElementById("socialProfilesForm_gitb");
    if (git) {
        git.value = "https://github.com/hsn96srhan";
        git.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "Clicked submitCVForm for social";
    }
    return "Submit button not found";
})()
"""

print(run_js(script))

