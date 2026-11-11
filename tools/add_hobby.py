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
    const f = document.getElementById("hobbiesID");
    if (!f) return "hobbiesID not found";
    
    const inp = document.getElementById("hobbiesForm_hobby");
    if (inp) {
        inp.value = "صناعة المحتوى الرقمي والتصوير الإبداعي";
        inp.dispatchEvent(new Event("input", {bubbles: true}));
    }
    
    const btn = document.getElementById("submitCVForm");
    if (btn) {
        btn.click();
        return "Clicked submitCVForm for hobby";
    }
    return "Submit button not found";
})()
"""

print(run_js(script))

