#!/usr/bin/env python3
import subprocess
import base64

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
    const sec = document.getElementById("targetJob") || document.querySelector("[id*='targetJob']");
    if (!sec) return "Not found";
    const btns = Array.from(sec.querySelectorAll("a, button, i")).map(el => ({
        tag: el.tagName, id: el.id, cls: el.className, text: el.innerText.trim(), href: el.href || ''
    }));
    return JSON.stringify(btns);
})()
"""
print(run_js(script))

